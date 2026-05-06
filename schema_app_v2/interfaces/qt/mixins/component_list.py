"""Component list mixin: flat list view, add/remove bricks, schema references, context menu."""
from PyQt6.QtWidgets import (
    QListWidgetItem, QMenu, QMessageBox, QInputDialog, QDialog
)
from PyQt6.QtCore import Qt


class ComponentListMixin:
    """Handles the flat component list and related add/remove operations."""

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def refresh_component_list(self):
        """Rebuild the flat component list widget"""
        self.ui.componentBricksListWidget.blockSignals(True)
        self.ui.componentBricksListWidget.clear()
        if self.current_schema:
            for brick_id in self.current_schema.get_components_by_sequence():
                brick = self.brick_integration.get_brick_by_id(brick_id)
                if brick:
                    item = QListWidgetItem(brick.name)
                    item.setData(Qt.ItemDataRole.UserRole, ('brick', brick_id))
                    self.ui.componentBricksListWidget.addItem(item)
            for ref in self.current_schema.schema_refs:
                label = ref.get('label') or ref['schema_id']
                prop  = ref.get('property_path', '')
                item = QListWidgetItem(f"⬡ {label}  [{prop}]")
                item.setData(Qt.ItemDataRole.UserRole, ('schema_ref', ref['schema_id'],
                                                        ref.get('attach_to_brick_id', '')))
                from PyQt6.QtGui import QColor
                item.setForeground(QColor(80, 120, 200))
                self.ui.componentBricksListWidget.addItem(item)
        self.ui.componentBricksListWidget.blockSignals(False)

    def _refresh_component_views(self):
        """Refresh both list and tree views"""
        self.refresh_component_list()
        self.refresh_component_tree()

    # ------------------------------------------------------------------
    # Add / Remove
    # ------------------------------------------------------------------

    def add_component_brick(self):
        """Add component brick via dialog"""
        if not self.current_schema:
            QMessageBox.warning(self, "No Schema", "Please create or select a schema first")
            return

        from schema_app_v2.interfaces.qt.add_component_dialog import AddComponentDialog
        dialog = AddComponentDialog(self.brick_integration, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_brick_id = dialog.get_selected_brick()
            if selected_brick_id:
                try:
                    if selected_brick_id not in self.current_schema.component_brick_ids:
                        self.current_schema.component_brick_ids.append(selected_brick_id)
                        self.current_schema.update_timestamp()
                        self.qt_session._emit_event('component_added', {"brick_id": selected_brick_id})
                    self._refresh_component_views()
                    self.update_preview()
                    QMessageBox.information(self, "Success",
                        f"Component '{selected_brick_id}' added to schema successfully!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to add component: {e}")

    def add_brick_as_component(self, item):
        """Add brick as component from double-click on brick list"""
        if not self.current_schema:
            return
        brick_name = item.text()
        all_bricks = self.brick_integration.get_available_bricks()
        bricks = [b for b in all_bricks if b.name == brick_name]
        if bricks:
            brick_id = bricks[0].brick_id
            if brick_id not in self.current_schema.component_brick_ids:
                self.current_schema.component_brick_ids.append(brick_id)
                self.current_schema.update_timestamp()
                self.qt_session._emit_event('component_added', {"brick_id": brick_id})
                self._refresh_component_views()
                self.ui.statusbar.showMessage(f"Added component: {brick_name}")

    def remove_component_brick(self):
        """Remove selected component or schema ref via Remove button"""
        items = self.ui.componentBricksListWidget.selectedItems()
        if not items:
            QMessageBox.warning(self, "No Selection", "Please select a component to remove")
            return
        if not self.current_schema:
            return

        data = items[0].data(Qt.ItemDataRole.UserRole)
        if not data:
            return

        kind = data[0]
        if kind == 'brick':
            brick_id = data[1]
            if brick_id in self.current_schema.component_brick_ids:
                self.current_schema.component_brick_ids.remove(brick_id)
                self.current_schema.update_timestamp()
                self.qt_session._emit_event('component_removed', {"brick_id": brick_id})
                self.state_manager.mark_schema_modified()
                self._refresh_component_views()
                self.update_preview()
                brick = self.brick_integration.get_brick_by_id(brick_id)
                self.ui.statusbar.showMessage(f"Removed component: {brick.name if brick else brick_id}")
        elif kind == 'schema_ref':
            schema_id, attach_brick_id = data[1], data[2]
            self.current_schema.remove_schema_ref(schema_id, attach_brick_id)
            self.schema_core.save_schema(self.current_schema)
            self.state_manager.mark_schema_modified()
            self._refresh_component_views()
            self.update_preview()
            self.ui.statusbar.showMessage("Removed schema reference")

    def add_schema_reference(self):
        """Embed a saved schema into the current schema via sh:node reference"""
        if not self.current_schema:
            QMessageBox.warning(self, "No Schema", "Please create or select a schema first")
            return

        all_schemas = []
        for lib_name in self.schema_core.get_libraries():
            for s in self.schema_core.get_all_schemas(lib_name):
                if s.schema_id != self.current_schema.schema_id:
                    all_schemas.append((lib_name, s))

        if not all_schemas:
            QMessageBox.information(self, "No Schemas", "No other saved schemas available to reference.")
            return

        schema_labels = [f"{s.name}  ({lib})" for lib, s in all_schemas]
        chosen_label, ok = QInputDialog.getItem(
            self, "Add Schema Reference", "Select schema to embed:", schema_labels, 0, False)
        if not ok:
            return
        ref_lib, ref_schema = all_schemas[schema_labels.index(chosen_label)]

        attach_options = []
        if self.current_schema.root_brick_id:
            rb = self.brick_integration.get_brick_by_id(self.current_schema.root_brick_id)
            if rb:
                attach_options.append((rb.name, self.current_schema.root_brick_id))
        for bid in self.current_schema.component_brick_ids:
            b = self.brick_integration.get_brick_by_id(bid)
            if b:
                attach_options.append((b.name, bid))

        if not attach_options:
            QMessageBox.warning(self, "No Attach Target",
                "Please set a root brick or add components before adding a schema reference.")
            return

        if len(attach_options) > 1:
            chosen_attach, ok2 = QInputDialog.getItem(
                self, "Attach To", "Attach schema reference to which brick?",
                [n for n, _ in attach_options], 0, False)
            if not ok2:
                return
            attach_brick_id = dict(attach_options)[chosen_attach]
        else:
            attach_brick_id = attach_options[0][1]

        property_path, ok3 = QInputDialog.getText(
            self, "Property Path",
            "Property path for sh:node attachment (e.g. ex:address):",
            text=f"ex:{ref_schema.name.lower().replace(' ', '')}"
        )
        if not ok3 or not property_path.strip():
            return

        self.current_schema.add_schema_ref(
            schema_id=ref_schema.schema_id,
            attach_to_brick_id=attach_brick_id,
            property_path=property_path.strip(),
            label=ref_schema.name,
        )
        self.schema_core.save_schema(self.current_schema)
        self.state_manager.mark_schema_modified()
        self._refresh_component_views()
        self.update_preview()
        self.ui.statusbar.showMessage(f"Added schema reference: {ref_schema.name}")

    # ------------------------------------------------------------------
    # Context menu
    # ------------------------------------------------------------------

    def on_list_context_menu(self, pos):
        """Right-click context menu for the flat component list"""
        if not self.current_schema:
            return
        item = self.ui.componentBricksListWidget.itemAt(pos)
        if not item:
            return
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return

        kind = data[0]
        menu = QMenu(self)

        if kind == 'schema_ref':
            schema_id, attach_brick_id = data[1], data[2]
            remove_action = menu.addAction("Remove Schema Reference")
            action = menu.exec(self.ui.componentBricksListWidget.viewport().mapToGlobal(pos))
            if action == remove_action:
                self.current_schema.remove_schema_ref(schema_id, attach_brick_id)
                self.schema_core.save_schema(self.current_schema)
                self.state_manager.mark_schema_modified()
                self._refresh_component_views()
                self.update_preview()
                self.ui.statusbar.showMessage("Removed schema reference")
            return

        # kind == 'brick'
        brick_id = data[1]
        ordered = self.current_schema.get_components_by_sequence()
        idx = ordered.index(brick_id) if brick_id in ordered else -1
        max_idx = len(ordered) - 1

        up_action = menu.addAction("Move Up")
        up_action.setEnabled(idx > 0)
        down_action = menu.addAction("Move Down")
        down_action.setEnabled(0 <= idx < max_idx)
        menu.addSeparator()
        meta_action = menu.addAction("Edit UI Metadata…")
        menu.addSeparator()
        remove_action = menu.addAction("Remove from Schema")

        action = menu.exec(self.ui.componentBricksListWidget.viewport().mapToGlobal(pos))
        if action == up_action:
            self._swap_component_positions(ordered, idx, idx - 1)
        elif action == down_action:
            self._swap_component_positions(ordered, idx, idx + 1)
        elif action == meta_action:
            self._open_ui_metadata_dialog(brick_id)
        elif action == remove_action:
            self._tree_remove_component(brick_id)

    # ------------------------------------------------------------------
    # Selection / double-click
    # ------------------------------------------------------------------

    def on_component_selection_changed(self):
        """Handle component list selection change"""
        pass

    def open_ui_metadata_editor(self, item):
        """Open UI metadata editor for double-clicked list item"""
        if not self.current_schema:
            QMessageBox.warning(self, "No Schema", "Please create or select a schema first")
            return
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return
        if data[0] == 'schema_ref':
            return  # schema refs have no UI metadata
        brick_id = data[1]
        self._open_ui_metadata_dialog(brick_id)

    def _open_ui_metadata_dialog(self, brick_id: str):
        """Open UI metadata dialog for a component"""
        if brick_id not in self.current_schema.component_brick_ids:
            QMessageBox.warning(self, "Invalid Component",
                f"Component '{brick_id}' not found in schema")
            return
        from schema_app_v2.interfaces.qt.ui_metadata_panel_dialog import UIMetadataPanelDialog
        dialog = UIMetadataPanelDialog(self.current_schema, brick_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.schema_core.save_schema(self.current_schema)
            self.qt_session._emit_event('schema_updated', self.current_schema.to_dict())
            self.refresh_component_list()
            self.refresh_component_tree()
