"""Schema management mixin: new/open/save/delete/export/validate/extend/daisy-chain."""
import os
from PyQt6.QtWidgets import QMessageBox, QInputDialog, QFileDialog, QDialog
from PyQt6.QtCore import Qt


class SchemaManagementMixin:
    """Handles all schema-level CRUD and export operations."""

    # ------------------------------------------------------------------
    # Create / Open / Save / Delete
    # ------------------------------------------------------------------

    def new_schema(self):
        """Create a new schema"""
        name, ok = QInputDialog.getText(self, "New Schema", "Enter schema name:")
        if not ok or not name.strip():
            return

        schema = self.schema_core.create_schema(name.strip())
        self.current_schema = schema
        self.qt_session.current_schema = schema

        self.schema_core.save_schema(schema)
        self.qt_session._emit_event('schema_created', schema.to_dict())

        self.refresh_schema_list()
        self.load_schema_into_ui(schema)
        self.state_manager.set_current_schema(schema, has_unsaved_changes=False)
        self.ui.statusbar.showMessage(f"Created new schema: {name}")

    def open_schema(self):
        """Open an existing schema"""
        schemas = self.schema_core.get_all_schemas()
        if not schemas:
            QMessageBox.information(self, "No Schemas", "No schemas found in current library.")
            return

        schema_names = [s.name for s in schemas]
        name, ok = QInputDialog.getItem(self, "Open Schema", "Select schema:", schema_names, 0, False)
        if not ok or not name:
            return

        for schema in schemas:
            if schema.name == name:
                self.current_schema = schema
                self.qt_session.current_schema = schema
                self.qt_session._emit_event('schema_loaded', schema.to_dict())
                self.load_schema_into_ui(schema)
                self.state_manager.set_current_schema(schema, has_unsaved_changes=False)
                self.ui.statusbar.showMessage(f"Opened schema: {name}")
                break

    def save_schema(self):
        """Save current schema (JSON + SHACL .ttl)"""
        if not self.current_schema:
            return

        try:
            self.state_manager.start_saving()
            self.schema_core.save_schema(self.current_schema)
            self._write_shacl_to_library()
            self.qt_session._emit_event('schema_saved', self.current_schema.to_dict())
            self.state_manager.mark_schema_saved()
            self.ui.statusbar.showMessage(
                f"Saved schema: {self.current_schema.name} (JSON + SHACL)"
            )
        except Exception as e:
            self.qt_session._emit_event('error_occurred', {"message": f"Failed to save schema: {e}"})
            QMessageBox.critical(self, "Save Error", f"Failed to save schema: {e}")

    def _write_shacl_to_library(self):
        """Write SHACL .ttl alongside the JSON in the shared library"""
        if not self.current_schema:
            return
        from schema_app_v2.core.shacl_export import SHACLExporter
        lib_name = self.schema_core.active_library
        schemas_path = os.path.join(self.schema_core.repository_path, lib_name)
        os.makedirs(schemas_path, exist_ok=True)
        ttl_path = os.path.join(schemas_path, f"{self.current_schema.schema_id}.ttl")
        try:
            exporter = SHACLExporter(self.brick_integration)
            turtle_str = exporter.export_schema(self.current_schema)
            with open(ttl_path, 'w') as f:
                f.write(turtle_str)
        except Exception as e:
            print(f"SHACL auto-export failed: {e}")

    def export_shacl(self):
        """Export schema as SHACL to a user-chosen file"""
        if not self.current_schema:
            QMessageBox.warning(self, "No Schema", "Please create or open a schema first.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export SHACL", f"{self.current_schema.name}.ttl",
            "Turtle Files (*.ttl);;All Files (*)"
        )
        if not file_path:
            return

        try:
            from schema_app_v2.core.shacl_export import SHACLExporter
            exporter = SHACLExporter(self.brick_integration)
            turtle_str = exporter.export_schema(self.current_schema)
            with open(file_path, 'w') as f:
                f.write(turtle_str)
            self.ui.statusbar.showMessage(f"Exported SHACL to: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export SHACL: {e}")

    def delete_schema(self):
        """Delete current schema"""
        if not self.current_schema:
            return

        reply = QMessageBox.question(
            self, "Delete Schema",
            f"Are you sure you want to delete '{self.current_schema.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            schema_id = self.current_schema.schema_id
            schema_name = self.current_schema.name
            self.current_schema = None
            self.state_manager.set_current_schema(None, has_unsaved_changes=False)

            self.ui.schemaListWidget.clear()
            self.ui.nameLineEdit.clear()
            self.ui.descriptionLineEdit.clear()
            self.ui.componentBricksListWidget.clear()
            self.ui.previewTextEdit.clear()

            if self.schema_core.delete_schema(schema_id):
                self.refresh_schema_list()
                self.ui.statusbar.showMessage(f"Deleted schema: {schema_name}")
            else:
                QMessageBox.warning(self, "Delete Warning", "Schema file may not have been deleted")
        except Exception as e:
            QMessageBox.critical(self, "Delete Error", f"Failed to delete schema: {e}")

    # ------------------------------------------------------------------
    # Validate / Extend / Daisy-chain
    # ------------------------------------------------------------------

    def validate_schema(self):
        """Validate current schema"""
        if not self.current_schema:
            QMessageBox.warning(self, "No Schema", "Please create or open a schema first.")
            return
        try:
            if not self.current_schema.name:
                raise ValueError("Schema name is required")
            if not self.current_schema.root_brick_id:
                raise ValueError("Root brick is required")
            QMessageBox.information(self, "Validation", "Schema validation passed!")
            self.ui.statusbar.showMessage("Schema validation passed")
        except Exception as e:
            QMessageBox.critical(self, "Validation Error", f"Schema validation failed: {e}")

    def create_daisy_chain(self):
        """Create daisy chain of schemas"""
        from schema_app_v2.interfaces.qt.daisy_chain_editor_dialog import DaisyChainEditorDialog
        schemas = self.schema_core.get_all_schemas()
        if len(schemas) < 2:
            QMessageBox.warning(self, "Insufficient Schemas",
                "You need at least 2 schemas to create a daisy chain.")
            return

        dialog = DaisyChainEditorDialog(self.schema_core, schemas, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            chain_data = dialog.get_chain_data()
            daisy_chain = self.schema_core.create_daisy_chain(
                chain_data['name'], chain_data['description'],
                chain_data['schema_ids'], chain_data['navigation_rules']
            )
            if daisy_chain:
                self.qt_session._emit_event('daisy_chain_created', daisy_chain.to_dict())
                QMessageBox.information(self, "Success",
                    f"Daisy chain '{daisy_chain.name}' created with {len(daisy_chain.schema_ids)} schemas.")
                self.ui.statusbar.showMessage(f"Created daisy chain: {daisy_chain.name}")
            else:
                QMessageBox.critical(self, "Error", "Failed to create daisy chain.")

    def extend_schema(self):
        """Extend an existing schema"""
        if not self.current_schema:
            QMessageBox.warning(self, "No Schema", "Please create or select a schema to extend first.")
            return

        all_schemas = self.schema_core.get_all_schemas()
        parent_schemas = [s for s in all_schemas if s.schema_id != self.current_schema.schema_id]
        if not parent_schemas:
            QMessageBox.warning(self, "No Parent Schemas", "No other schemas available to extend from.")
            return

        parent_name, ok = QInputDialog.getItem(
            self, "Select Parent Schema", "Select the schema to extend:",
            [s.name for s in parent_schemas], 0, False
        )
        if not ok or not parent_name:
            return
        parent_schema = next((s for s in parent_schemas if s.name == parent_name), None)
        if not parent_schema:
            return

        additional_bricks, ok = QInputDialog.getText(
            self, "Additional Bricks", "Enter additional brick IDs (comma-separated):"
        )
        if not ok:
            return
        brick_ids = [b.strip() for b in additional_bricks.split(',') if b.strip()] if additional_bricks else []

        new_name, ok = QInputDialog.getText(
            self, "Extended Schema Name", "Enter name for the extended schema:",
            text=f"{self.current_schema.name}_extended"
        )
        if not ok or not new_name.strip():
            return

        extended_schema = self.schema_core.extend_schema(
            parent_schema.schema_id, new_name.strip(),
            f"Extended from {parent_schema.name}", brick_ids, self.brick_integration
        )
        if extended_schema:
            self.current_schema = extended_schema
            self.qt_session.current_schema = extended_schema
            self.qt_session._emit_event('schema_extended', extended_schema.to_dict())
            self.load_schema_into_ui(extended_schema)
            self.state_manager.set_current_schema(extended_schema, has_unsaved_changes=False)
            QMessageBox.information(self, "Success",
                f"Schema '{extended_schema.name}' created extending '{parent_schema.name}'.")
            self.ui.statusbar.showMessage(f"Extended schema: {extended_schema.name}")
        else:
            QMessageBox.critical(self, "Error", "Failed to extend schema.")

    def create_schema_from_template(self, template):
        """Create schema from selected template"""
        from schema_app_v2.core.flow_engine import FlowType
        schema = self.schema_core.create_schema(template.name, template.description)
        for brick in self.brick_integration.get_node_shape_bricks():
            if template.root_brick_type.lower() in brick.name.lower():
                schema.root_brick_id = brick.brick_id
                break
        for component_name in template.suggested_components:
            bricks = self.brick_integration.search_bricks(component_name)
            if bricks:
                schema.component_brick_ids.append(bricks[0].brick_id)
        if template.flow_type:
            schema.flow_config = self.flow_engine.create_flow(
                f"Flow for {template.name}", FlowType(template.flow_type),
                f"Auto-generated flow for {template.name}"
            )
        self.current_schema = schema
        self.load_schema_into_ui(schema)
        self.state_manager.set_current_schema(schema, has_unsaved_changes=False)
        self.ui.statusbar.showMessage(f"Created schema from template: {template.name}")

    # ------------------------------------------------------------------
    # Library management
    # ------------------------------------------------------------------

    def on_schema_library_changed(self, library_name):
        """Handle schema library change"""
        if not library_name:
            return
        self.schema_core.active_library = library_name
        self.current_schema = None
        self.state_manager.set_current_schema(None, has_unsaved_changes=False)
        self.refresh_schema_list()
        self.ui.statusbar.showMessage(f"Library: {library_name}")

    def new_library(self):
        """Create a new schema library in the shared library"""
        name, ok = QInputDialog.getText(self, "New Library", "Library name:")
        if not ok or not name.strip():
            return
        name = name.strip()
        try:
            if self.schema_core.shared_library_manager:
                self.schema_core.shared_library_manager.create_library(
                    lib_type="schemas", name=name, description=f"Schema library '{name}'"
                )
            else:
                self.schema_core.create_library(name)
            self.refresh_schema_libraries()
            idx = self.ui.libraryComboBox.findText(name)
            if idx >= 0:
                self.ui.libraryComboBox.setCurrentIndex(idx)
            self.ui.statusbar.showMessage(f"Created library: {name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create library: {e}")

    # ------------------------------------------------------------------
    # Schema selection
    # ------------------------------------------------------------------

    def on_schema_selection_changed(self):
        """Handle schema list selection change"""
        items = self.ui.schemaListWidget.selectedItems()
        if not items:
            return
        schema_name = items[0].text()
        for schema in self.schema_core.get_all_schemas():
            if schema.name == schema_name:
                self.current_schema = schema
                self.qt_session.current_schema = schema
                self.qt_session._emit_event('schema_loaded', schema.to_dict())
                self.load_schema_into_ui(schema)
                self.state_manager.set_current_schema(schema, has_unsaved_changes=False)

                try:
                    self.ui.nameLineEdit.textChanged.disconnect(self.on_schema_details_changed)
                    self.ui.descriptionLineEdit.textChanged.disconnect(self.on_schema_details_changed)
                    self.ui.rootBrickComboBox.currentTextChanged.disconnect(self.on_root_brick_changed)
                except (RuntimeError, TypeError):
                    pass
                self.ui.nameLineEdit.textChanged.connect(self.on_schema_details_changed)
                self.ui.descriptionLineEdit.textChanged.connect(self.on_schema_details_changed)
                self.ui.rootBrickComboBox.currentTextChanged.connect(self.on_root_brick_changed)
                break

    def on_schema_details_changed(self):
        """Handle name/description edits"""
        if self.current_schema:
            self.current_schema.name = self.ui.nameLineEdit.text()
            self.current_schema.description = self.ui.descriptionLineEdit.text()
            self.current_schema.update_timestamp()
            self.qt_session._emit_event('schema_updated', self.current_schema.to_dict())
            self.update_preview()

    def on_root_brick_changed(self, brick_name):
        """Handle root brick selection change"""
        if self.current_schema and brick_name:
            all_bricks = self.brick_integration.get_available_bricks()
            bricks = [b for b in all_bricks if b.name == brick_name]
            if bricks:
                self.current_schema.root_brick_id = bricks[0].brick_id
                self.current_schema.update_timestamp()
                self.qt_session._emit_event('root_brick_set', {"brick_id": bricks[0].brick_id})
                self.state_manager.mark_schema_modified()
                self.update_preview()

    # ------------------------------------------------------------------
    # Refresh helpers
    # ------------------------------------------------------------------

    def refresh_schema_libraries(self):
        """Refresh schema library combo"""
        try:
            libraries = self.schema_core.get_libraries()
            self.ui.libraryComboBox.clear()
            self.ui.libraryComboBox.addItems(libraries)
            if libraries:
                self.ui.libraryComboBox.setCurrentIndex(0)
        except Exception as e:
            print(f"Error loading schema libraries: {e}")

    def refresh_schema_list(self):
        """Refresh schema list widget"""
        self.ui.schemaListWidget.clear()
        for schema in self.schema_core.get_all_schemas():
            self.ui.schemaListWidget.addItem(schema.name)

    def refresh_root_bricks(self):
        """Refresh root brick combo"""
        self.ui.rootBrickComboBox.clear()
        for brick in self.brick_integration.get_node_shape_bricks():
            self.ui.rootBrickComboBox.addItem(brick.name)

    def load_schema_into_ui(self, schema):
        """Populate all editor fields from a schema object"""
        for w in (self.ui.nameLineEdit, self.ui.descriptionLineEdit, self.ui.rootBrickComboBox):
            w.blockSignals(True)

        self.ui.nameLineEdit.setText(schema.name)
        self.ui.descriptionLineEdit.setText(schema.description or "")

        if schema.root_brick_id:
            brick = self.brick_integration.get_brick_by_id(schema.root_brick_id)
            if brick:
                idx = self.ui.rootBrickComboBox.findText(brick.name)
                if idx >= 0:
                    self.ui.rootBrickComboBox.setCurrentIndex(idx)

        for w in (self.ui.nameLineEdit, self.ui.descriptionLineEdit, self.ui.rootBrickComboBox):
            w.blockSignals(False)

        self.refresh_component_list()
        self.refresh_flow_steps()
        self.update_preview()

    def update_preview(self):
        """Update the preview text panel"""
        if not self.current_schema:
            self.ui.previewTextEdit.clear()
            return

        root_brick_name = "Not set"
        if self.current_schema.root_brick_id:
            rb = self.brick_integration.get_brick_by_id(self.current_schema.root_brick_id)
            if rb:
                root_brick_name = rb.name

        text = (
            f"Schema Preview\n{'=' * 50}\n\n"
            f"Name: {self.current_schema.name}\n"
            f"Description: {self.current_schema.description or 'No description'}\n"
            f"Root Brick: {root_brick_name}\n\n"
            f"Components ({len(self.current_schema.component_brick_ids)}):\n"
        )
        for brick_id in self.current_schema.component_brick_ids:
            brick = self.brick_integration.get_brick_by_id(brick_id)
            text += f"  - {brick.name if brick else brick_id}\n"

        if self.current_schema.schema_refs:
            text += f"\nSchema References ({len(self.current_schema.schema_refs)}):\n"
            for ref in self.current_schema.schema_refs:
                text += f"  - {ref.get('label', ref['schema_id'])} via {ref.get('property_path', '')}\n"

        if self.current_schema.inheritance_chain:
            text += f"\nInherits from: {len(self.current_schema.inheritance_chain)} schemas\n"
            for pid in self.current_schema.inheritance_chain:
                text += f"  - {pid}\n"

        if self.current_schema.relationships:
            text += "\nBrick Relationships:\n"
            for bid, rels in self.current_schema.relationships.items():
                text += f"  - {bid}: {rels}\n"

        if self.current_schema.flow_config:
            flow = self.current_schema.flow_config
            text += (
                f"\nFlow Configuration:\n"
                f"  Type: {flow.flow_type.value}\n"
                f"  Steps: {len(flow.steps)}\n"
            )
            for i, step in enumerate(flow.steps, 1):
                text += f"  {i}. {step.name} ({len(step.brick_ids)} bricks)\n"

        self.ui.previewTextEdit.setPlainText(text)

    # ------------------------------------------------------------------
    # Help / About
    # ------------------------------------------------------------------

    def show_schema_guide(self):
        """Show schema construction guide"""
        QMessageBox.information(self, "Schema Construction Guide",
            "<h3>Schema Construction Guide</h3>"
            "<p>1. Create a Schema → 2. Select Root Brick → "
            "3. Add Component Bricks → 4. Configure Flow → 5. Save &amp; Export</p>"
        )

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Schema App v2",
            "Schema App v2\nClean, modular schema construction system\n\nVersion: 2.0.0")
