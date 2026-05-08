"""Component tree mixin: tree rendering, context menu, move/group/parent operations."""
import uuid
from PyQt6.QtWidgets import QTreeWidgetItem, QMenu, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt


class ComponentTreeMixin:
    """Handles the hierarchical tree view of schema components."""

    def on_component_view_changed(self, tree_selected: bool):
        """Handle view toggle between list and tree"""
        if tree_selected:
            self.ui.componentViewStack.setCurrentIndex(1)
            self.refresh_component_tree()
        else:
            self.ui.componentViewStack.setCurrentIndex(0)

    def refresh_component_tree(self):
        """Rebuild the component tree widget from scratch"""
        self.ui.componentTreeWidget.clear()
        if not self.current_schema:
            return

        # Root NodeShape header
        if self.current_schema.root_brick_id:
            root_brick = self.brick_integration.get_brick_by_id(self.current_schema.root_brick_id)
            if root_brick:
                root_item = QTreeWidgetItem(self.ui.componentTreeWidget)
                root_item.setText(0, f"◆ {root_brick.name}  [NodeShape / root]")
                root_item.setData(0, Qt.ItemDataRole.UserRole, ('root', self.current_schema.root_brick_id))
                font = root_item.font(0)
                font.setBold(True)
                root_item.setFont(0, font)
                root_item.setExpanded(True)

                for ref in self.current_schema.get_schema_refs_for_brick(self.current_schema.root_brick_id):
                    self._add_schema_ref_item(root_item, ref, self.current_schema.root_brick_id)

        # Groups as top-level branches
        for group in self.current_schema.get_groups_by_sequence():
            self._add_group_to_tree(None, group)

        # Ungrouped top-level components
        for brick_id in self.current_schema.get_ui_root_components():
            ui_meta = self.current_schema.get_component_ui_metadata(brick_id)
            if ui_meta and ui_meta.group_id:
                continue
            self._add_brick_tree_item(None, brick_id)

    def _add_group_to_tree(self, parent_item, group: dict):
        """Add a group node and all its members to the tree"""
        if parent_item is None:
            group_item = QTreeWidgetItem(self.ui.componentTreeWidget)
        else:
            group_item = QTreeWidgetItem(parent_item)

        group_item.setText(0, f"▼ {group['label']}  [group]")
        group_item.setData(0, Qt.ItemDataRole.UserRole, ('group', group['id']))
        font = group_item.font(0)
        font.setBold(True)
        group_item.setFont(0, font)
        group_item.setExpanded(True)

        for brick_id in self.current_schema.get_ui_root_components():
            ui_meta = self.current_schema.get_component_ui_metadata(brick_id)
            if ui_meta and ui_meta.group_id == group['id']:
                self._add_brick_tree_item(group_item, brick_id)

    def _add_brick_tree_item(self, parent_item, brick_id: str):
        """Recursively add a brick and its UI-metadata children to the tree"""
        brick = self.brick_integration.get_brick_by_id(brick_id)
        if not brick:
            return

        ui_meta = self.current_schema.get_component_ui_metadata(brick_id)
        label = (ui_meta.label if ui_meta and ui_meta.label else brick.name)
        type_tag = brick.object_type

        if parent_item is None:
            item = QTreeWidgetItem(self.ui.componentTreeWidget)
        else:
            item = QTreeWidgetItem(parent_item)

        item.setText(0, f"{label}  [{type_tag}]")
        item.setData(0, Qt.ItemDataRole.UserRole, ('brick', brick_id))
        item.setExpanded(True)

        for child_id in self.current_schema.get_ui_children(brick_id):
            self._add_brick_tree_item(item, child_id)

        for ref in self.current_schema.get_schema_refs_for_brick(brick_id):
            self._add_schema_ref_item(item, ref, brick_id)

    def _add_schema_ref_item(self, parent_item, ref: dict, attach_brick_id: str,
                             _visited: set = None):
        """Add a schema-reference node and recursively expand its contents."""
        if _visited is None:
            _visited = set()
        ref_schema_id = ref["schema_id"]

        ref_item = QTreeWidgetItem(parent_item)
        ref_label = ref.get("label") or ref_schema_id
        ref_path = ref.get("property_path", "")
        ref_item.setText(0, f"⬡ {ref_label}  [schema ref · {ref_path}]")
        ref_item.setData(0, Qt.ItemDataRole.UserRole, ('schema_ref', ref_schema_id, attach_brick_id))
        font = ref_item.font(0)
        font.setBold(True)
        font.setItalic(True)
        ref_item.setFont(0, font)
        ref_item.setExpanded(True)

        # Guard against circular references
        if ref_schema_id in _visited:
            warn = QTreeWidgetItem(ref_item)
            warn.setText(0, "⚠ circular reference")
            return
        _visited = _visited | {ref_schema_id}

        # Load the referenced schema and expand its components
        ref_schema = None
        for lib in self.schema_core.get_libraries():
            for s in self.schema_core.get_all_schemas(lib):
                if s.schema_id == ref_schema_id:
                    ref_schema = s
                    break
            if ref_schema:
                break

        if ref_schema is None:
            missing = QTreeWidgetItem(ref_item)
            missing.setText(0, "⚠ schema not found")
            self._style_readonly(missing)
            return

        # Root brick of the referenced schema
        if ref_schema.root_brick_id:
            rb = self.brick_integration.get_brick_by_id(ref_schema.root_brick_id)
            if rb:
                rb_item = QTreeWidgetItem(ref_item)
                rb_item.setText(0, f"◆ {rb.name}  [NodeShape / root]")
                rb_item.setData(0, Qt.ItemDataRole.UserRole, ('readonly_brick', rb.brick_id))
                self._style_readonly(rb_item)
                rb_item.setExpanded(True)
                for nested_ref in ref_schema.get_schema_refs_for_brick(ref_schema.root_brick_id):
                    self._add_schema_ref_item(rb_item, nested_ref, ref_schema.root_brick_id, _visited)

        # Component bricks of the referenced schema
        for brick_id in ref_schema.get_components_by_sequence():
            brick = self.brick_integration.get_brick_by_id(brick_id)
            if not brick:
                continue
            b_item = QTreeWidgetItem(ref_item)
            b_item.setText(0, f"{brick.name}  [{brick.object_type}]")
            b_item.setData(0, Qt.ItemDataRole.UserRole, ('readonly_brick', brick_id))
            self._style_readonly(b_item)
            b_item.setExpanded(True)
            for nested_ref in ref_schema.get_schema_refs_for_brick(brick_id):
                self._add_schema_ref_item(b_item, nested_ref, brick_id, _visited)

    def _style_readonly(self, item: QTreeWidgetItem):
        """Apply greyed-out italic style to mark a node as read-only."""
        from PyQt6.QtGui import QColor
        font = item.font(0)
        font.setItalic(True)
        item.setFont(0, font)
        item.setForeground(0, QColor(130, 130, 130))

    # ------------------------------------------------------------------
    # Context menu
    # ------------------------------------------------------------------

    def on_tree_context_menu(self, pos):
        """Show right-click context menu on tree widget"""
        if not self.current_schema:
            return

        item = self.ui.componentTreeWidget.itemAt(pos)
        menu = QMenu(self)

        add_group_action = menu.addAction("Add Group")
        add_group_action.triggered.connect(self._tree_add_group)

        if item:
            node_data = item.data(0, Qt.ItemDataRole.UserRole)
            if node_data:
                kind = node_data[0]

                if kind == 'readonly_brick':
                    menu.exec(self.ui.componentTreeWidget.viewport().mapToGlobal(pos))
                    return

                if kind == 'brick':
                    node_id = node_data[1]
                    menu.addSeparator()
                    menu.addAction("Set Parent…").triggered.connect(
                        lambda: self._tree_set_parent(node_id))
                    menu.addAction("Move to Group…").triggered.connect(
                        lambda: self._tree_move_to_group(node_id))

                    ui_meta = self.current_schema.get_component_ui_metadata(node_id)
                    if ui_meta and (ui_meta.parent_id or ui_meta.group_id):
                        menu.addAction("Remove from Parent / Group").triggered.connect(
                            lambda: self._tree_remove_parent(node_id))

                    menu.addSeparator()
                    menu.addAction("Move Up").triggered.connect(
                        lambda: self._tree_move_up(node_id))
                    menu.addAction("Move Down").triggered.connect(
                        lambda: self._tree_move_down(node_id))
                    menu.addSeparator()
                    menu.addAction("Remove from Schema").triggered.connect(
                        lambda: self._tree_remove_component(node_id))

                elif kind == 'group':
                    node_id = node_data[1]
                    menu.addSeparator()
                    menu.addAction("Rename Group…").triggered.connect(
                        lambda: self._tree_rename_group(node_id))
                    menu.addAction("Delete Group").triggered.connect(
                        lambda: self._tree_delete_group(node_id))

        menu.exec(self.ui.componentTreeWidget.viewport().mapToGlobal(pos))

    # ------------------------------------------------------------------
    # Tree actions
    # ------------------------------------------------------------------

    def _tree_add_group(self):
        label, ok = QInputDialog.getText(self, "Add Group", "Group label:")
        if not ok or not label.strip():
            return
        group_id = f"group_{uuid.uuid4().hex[:8]}"
        self.current_schema.create_group(group_id, label.strip(), sequence=len(self.current_schema.groups))
        self.schema_core.save_schema(self.current_schema)
        self.refresh_component_tree()
        self.ui.statusbar.showMessage(f"Group '{label}' added")

    def _tree_rename_group(self, group_id: str):
        current_label = self.current_schema.groups.get(group_id, {}).get('label', '')
        label, ok = QInputDialog.getText(self, "Rename Group", "New label:", text=current_label)
        if not ok or not label.strip():
            return
        self.current_schema.groups[group_id]['label'] = label.strip()
        self.current_schema.update_timestamp()
        self.schema_core.save_schema(self.current_schema)
        self.refresh_component_tree()

    def _tree_delete_group(self, group_id: str):
        label = self.current_schema.groups.get(group_id, {}).get('label', group_id)
        reply = QMessageBox.question(
            self, "Delete Group",
            f"Delete group '{label}'? Members will become ungrouped.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.current_schema.delete_group(group_id)
        self.schema_core.save_schema(self.current_schema)
        self.refresh_component_tree()

    def _tree_set_parent(self, brick_id: str):
        candidates = [b for b in self.current_schema.component_brick_ids if b != brick_id]
        if not candidates:
            QMessageBox.information(self, "No candidates", "No other components to use as parent.")
            return
        id_map = {}
        names = []
        for bid in candidates:
            brick = self.brick_integration.get_brick_by_id(bid)
            name = brick.name if brick else bid
            names.append(name)
            id_map[name] = bid
        chosen, ok = QInputDialog.getItem(self, "Set Parent", "Select parent component:", names, 0, False)
        if not ok or not chosen:
            return
        self.current_schema.set_component_parent(brick_id, id_map[chosen])
        self.schema_core.save_schema(self.current_schema)
        self.refresh_component_tree()

    def _tree_remove_parent(self, brick_id: str):
        self.current_schema.remove_component_parent(brick_id)
        self.current_schema.remove_component_from_group(brick_id)
        self.schema_core.save_schema(self.current_schema)
        self.refresh_component_tree()

    def _tree_move_to_group(self, brick_id: str):
        groups = self.current_schema.get_groups_by_sequence()
        if not groups:
            QMessageBox.information(self, "No Groups", "No groups defined yet. Add a group first.")
            return
        group_id_map = {g['label']: g['id'] for g in groups}
        chosen, ok = QInputDialog.getItem(
            self, "Move to Group", "Select group:", list(group_id_map.keys()), 0, False)
        if not ok or not chosen:
            return
        self.current_schema.add_component_to_group(brick_id, group_id_map[chosen])
        self.schema_core.save_schema(self.current_schema)
        self.refresh_component_tree()

    def _swap_component_positions(self, ordered: list, idx_a: int, idx_b: int):
        """Swap two adjacent components and reassign contiguous sequences"""
        ordered = list(ordered)
        ordered[idx_a], ordered[idx_b] = ordered[idx_b], ordered[idx_a]
        for i, bid in enumerate(ordered):
            self.current_schema.set_component_sequence(bid, i)
        self.schema_core.save_schema(self.current_schema)
        self._refresh_component_views()

    def _tree_move_up(self, brick_id: str):
        ordered = self.current_schema.get_components_by_sequence()
        idx = ordered.index(brick_id) if brick_id in ordered else -1
        if idx > 0:
            self._swap_component_positions(ordered, idx, idx - 1)

    def _tree_move_down(self, brick_id: str):
        ordered = self.current_schema.get_components_by_sequence()
        idx = ordered.index(brick_id) if brick_id in ordered else -1
        if 0 <= idx < len(ordered) - 1:
            self._swap_component_positions(ordered, idx, idx + 1)

    def _tree_remove_component(self, brick_id: str):
        brick = self.brick_integration.get_brick_by_id(brick_id)
        name = brick.name if brick else brick_id
        reply = QMessageBox.question(
            self, "Remove Component", f"Remove '{name}' from the schema?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if brick_id in self.current_schema.component_brick_ids:
            self.current_schema.component_brick_ids.remove(brick_id)
            self.current_schema.remove_component_parent(brick_id)
            self.current_schema.remove_component_from_group(brick_id)
            self.current_schema.update_timestamp()
            self.schema_core.save_schema(self.current_schema)
            self._refresh_component_views()
            self.update_preview()
            self.ui.statusbar.showMessage(f"Removed component: {name}")

    # ------------------------------------------------------------------
    # UI metadata editor (tree double-click)
    # ------------------------------------------------------------------

    def open_ui_metadata_editor_tree(self, item, column):
        """Open UI metadata editor for double-clicked tree item"""
        if not self.current_schema:
            return
        node_data = item.data(0, Qt.ItemDataRole.UserRole)
        if not node_data:
            return
        kind = node_data[0]
        if kind == 'brick':
            self._open_ui_metadata_dialog(node_data[1])
