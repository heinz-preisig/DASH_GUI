"""
Schema GUI Module - Local State Architecture
Main window with consolidated logic - no mixins, no global state manager.
"""

import os
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QMainWindow, QButtonGroup, QMessageBox, QInputDialog, QFileDialog,
    QListWidgetItem, QTreeWidgetItem
)
from PyQt6.QtCore import Qt

from schema_app_v2.core.schema_core import Schema
from schema_app_v2.core.multi_tenant_backend import MultiTenantBackend
from schema_app_v2.core.schema_helper import SchemaHelper
from schema_app_v2.core.shacl_export import SHACLExporter

from .ui_components import UiLoader, ComponentManager


class SchemaGUI(QMainWindow):
    """Main schema construction GUI - local state management."""

    # UI States
    BROWSE = "browse"
    EDIT = "edit"
    CREATE = "create"

    def __init__(self, schema_repository_path: str = None,
                 brick_repository_path: str = None):
        super().__init__()

        # Backend
        self.backend = MultiTenantBackend(schema_repository_path, brick_repository_path)
        self.qt_session = self.backend.get_qt_session()
        self.schema_core = self.qt_session.schema_core
        self.brick_integration = self.qt_session.brick_integration
        self.helper = SchemaHelper()

        # UI Setup
        self.ui_loader = UiLoader()
        self.ui = self.ui_loader.load_main_window()
        self.setCentralWidget(self.ui)
        self.components = ComponentManager()

        # Local State (instead of state_manager)
        self.ui_state = self.BROWSE
        self.current_schema: Optional[Schema] = None
        self.current_library: str = ""
        self.modified: bool = False

        # Setup
        self.setup_ui()
        self.connect_signals()
        self.load_initial_data()

        self.setWindowTitle("Schema App v2 - Schema Constructor")
        self.setGeometry(50, 50, 1400, 900)

    def setup_ui(self):
        """Setup UI components"""
        # File menu
        self.ui.newSchemaAction.triggered.connect(self.new_schema)
        self.ui.openSchemaAction.triggered.connect(self.open_schema)
        self.ui.saveSchemaAction.triggered.connect(self.save_schema)
        self.ui.exportShaclAction.triggered.connect(self.export_shacl)
        self.ui.exitAction.triggered.connect(self.close)

        # Tools menu
        self.ui.validateSchemaAction.triggered.connect(self.validate_schema)

        # Schema menu
        daisy_chain_action = self.ui.toolsMenu.addAction("Create Daisy Chain")
        daisy_chain_action.triggered.connect(self.create_daisy_chain)
        extend_schema_action = self.ui.toolsMenu.addAction("Extend Schema")
        extend_schema_action.triggered.connect(self.extend_schema)

        # Help menu
        self.ui.helpMenu.addSeparator()
        help_guide_action = self.ui.helpMenu.addAction("Schema Guide")
        help_guide_action.triggered.connect(self.show_schema_guide)
        self.ui.aboutAction.triggered.connect(self.show_about)

    def connect_signals(self):
        """Connect UI signals to handlers"""
        # Library management
        self.ui.libraryComboBox.currentTextChanged.connect(self.on_schema_library_changed)
        self.ui.newLibraryButton.clicked.connect(self.new_library)
        self.ui.brickLibraryComboBox.currentTextChanged.connect(self.on_brick_library_changed)

        # Schema management
        self.ui.schemaListWidget.itemSelectionChanged.connect(self.on_schema_selection_changed)
        self.ui.schemaListWidget.itemDoubleClicked.connect(self.on_schema_double_clicked)
        self.ui.newSchemaButton.clicked.connect(self.new_schema)
        self.ui.deleteSchemaButton.clicked.connect(self.delete_schema)

        # Brick management
        self.ui.brickSearchLineEdit.textChanged.connect(self.on_brick_search_changed)
        self.ui.brickListWidget.itemDoubleClicked.connect(self.add_brick_as_component)
        self.ui.brickListWidget.itemSelectionChanged.connect(self.on_brick_selection_changed)

        # Component management
        self.ui.addComponentButton.clicked.connect(self.add_component_brick)
        self.ui.addSchemaRefButton.clicked.connect(self.add_schema_reference)
        self.ui.removeComponentButton.clicked.connect(self.remove_component_brick)
        self.ui.componentBricksListWidget.itemSelectionChanged.connect(self.on_component_selection_changed)
        self.ui.componentBricksListWidget.itemDoubleClicked.connect(self.open_ui_metadata_editor)

        # Tree view
        if hasattr(self.ui, 'componentTreeWidget'):
            self.ui.componentTreeWidget.itemDoubleClicked.connect(self.open_ui_metadata_editor_tree)

        # View toggle
        self._view_toggle_group = QButtonGroup(self)
        self._view_toggle_group.addButton(self.ui.listViewRadio)
        self._view_toggle_group.addButton(self.ui.treeViewRadio)
        self.ui.treeViewRadio.toggled.connect(self.on_component_view_changed)

        # Action buttons
        self.ui.saveButton.clicked.connect(self.save_schema)
        self.ui.exportShaclButton.clicked.connect(self.save_schema)
        self.ui.generateWebFormButton.clicked.connect(self.generate_web_form)

    # -------------------------------------------------------------------------
    # Local State Management (replaces state_manager)
    # -------------------------------------------------------------------------

    def set_ui_state(self, state: str):
        """Set UI state and update visibility"""
        self.ui_state = state
        self._update_ui_visibility()

    def _update_ui_visibility(self):
        """Update UI based on current state"""
        has_schema = self.current_schema is not None

        # Enable/disable buttons based on state
        self.ui.saveButton.setEnabled(has_schema)
        self.ui.exportShaclButton.setEnabled(has_schema)
        self.ui.addComponentButton.setEnabled(has_schema)
        self.ui.removeComponentButton.setEnabled(has_schema)
        self.ui.deleteSchemaButton.setEnabled(has_schema)

        # Show/hide schema details
        self.ui.schemaDetailsGroupBox.setVisible(has_schema)

    def mark_modified(self):
        """Mark schema as modified"""
        self.modified = True
        if self.current_schema:
            title = f"*{self.current_schema.name} - Schema App v2"
            self.setWindowTitle(title)

    # -------------------------------------------------------------------------
    # Schema Operations
    # -------------------------------------------------------------------------

    def new_schema(self):
        """Create a new schema"""
        name, ok = QInputDialog.getText(self, "New Schema", "Enter schema name:")
        if not ok or not name.strip():
            return

        self.current_schema = self.schema_core.create_schema(name.strip())
        self.schema_core.save_schema(self.current_schema)

        self.refresh_schema_list()
        self.load_schema_into_ui(self.current_schema)
        self.set_ui_state(self.EDIT)
        self.ui.statusbar.showMessage(f"Created new schema: {name}")

    def open_schema(self):
        """Open an existing schema"""
        schemas = sorted(self.schema_core.get_all_schemas(), key=lambda s: s.name.lower())
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
                self.load_schema_into_ui(schema)
                self.set_ui_state(self.EDIT)
                self.ui.statusbar.showMessage(f"Opened schema: {name}")
                break

    def save_schema(self):
        """Save current schema"""
        if not self.current_schema:
            return

        try:
            self.schema_core.save_schema(self.current_schema)
            self._export_all()
            self.modified = False
            self.setWindowTitle(f"{self.current_schema.name} - Schema App v2")
            self.ui.statusbar.showMessage(
                f"Saved schema: {self.current_schema.name} (JSON + SHACL + form)"
            )
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save schema: {e}")

    def delete_schema(self):
        """Delete current schema"""
        if not self.current_schema:
            return

        reply = QMessageBox.question(
            self, "Delete Schema",
            f"Are you sure you want to delete '{self.current_schema.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.schema_core.delete_schema(self.current_schema.schema_id)
            self.current_schema = None
            self.set_ui_state(self.BROWSE)
            self.refresh_schema_list()
            self.ui.statusbar.showMessage("Schema deleted")

    def _export_all(self):
        """Write .ttl and _form.html alongside the schema .json"""
        if not self.current_schema:
            return
        lib_name = self.schema_core.active_library
        output_dir = os.path.join(self.schema_core.repository_path, lib_name)
        try:
            SHACLExporter(self.brick_integration).export_all(self.current_schema, output_dir)
        except Exception as e:
            print(f"Auto-export failed: {e}")

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
            exporter = SHACLExporter(self.brick_integration)
            turtle_str = exporter.export_schema(self.current_schema)
            with open(file_path, 'w') as f:
                f.write(turtle_str)
            self.ui.statusbar.showMessage(f"Exported SHACL to: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export: {e}")

    # -------------------------------------------------------------------------
    # Component Operations
    # -------------------------------------------------------------------------

    def add_brick_as_component(self):
        """Add brick as component (called from double-click on brick list)"""
        self.add_component_brick()

    def add_component_brick(self):
        """Add selected brick as component to current schema"""
        if not self.current_schema:
            QMessageBox.warning(self, "No Schema", "Please create or open a schema first.")
            return

        # Get selected brick from brick list
        brick_item = self.ui.brickListWidget.currentItem()
        if not brick_item:
            QMessageBox.information(self, "Select Brick", "Please select a brick from the list first.")
            return

        brick_data = brick_item.data(Qt.ItemDataRole.UserRole)
        if not brick_data:
            return

        try:
            # Add brick as component (direct list append)
            brick_id = brick_data.get('brick_id', '')
            if brick_id and brick_id not in self.current_schema.component_brick_ids:
                self.current_schema.component_brick_ids.append(brick_id)
                self.current_schema.update_timestamp()
            self.mark_modified()
            self.refresh_component_list()
            self.ui.statusbar.showMessage(f"Added brick: {brick_data.get('name', '')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add component: {e}")

    def add_schema_reference(self):
        """Add reference to another schema"""
        QMessageBox.information(self, "Not Implemented", "Schema references not yet implemented.")

    def remove_component_brick(self):
        """Remove selected component from schema"""
        if not self.current_schema:
            return

        component_item = self.ui.componentBricksListWidget.currentItem()
        if not component_item:
            return

        component_id = component_item.data(Qt.ItemDataRole.UserRole)
        if not component_id:
            return

        try:
            # Remove from component list directly
            if component_id in self.current_schema.component_brick_ids:
                self.current_schema.component_brick_ids.remove(component_id)
                self.current_schema.update_timestamp()
            self.mark_modified()
            self.refresh_component_list()
            self.ui.statusbar.showMessage("Component removed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove component: {e}")

    # -------------------------------------------------------------------------
    # UI Update Methods
    # -------------------------------------------------------------------------

    def load_schema_into_ui(self, schema: Schema):
        """Load schema data into UI fields"""
        self.ui.nameLineEdit.setText(schema.name)
        self.ui.descriptionLineEdit.setText(schema.description or "")
        self.refresh_component_list()
        self._update_ui_visibility()

    def refresh_component_list(self):
        """Refresh the component list/tree views"""
        self.ui.componentBricksListWidget.clear()

        if not self.current_schema:
            return

        # component_brick_ids is a list of brick IDs
        for brick_id in self.current_schema.component_brick_ids:
            # Look up brick name from integration
            brick = self.brick_integration.get_brick_by_id(brick_id)
            brick_name = brick.name if hasattr(brick, 'name') else brick_id[:8]
            item = QListWidgetItem(brick_name)
            item.setData(Qt.ItemDataRole.UserRole, brick_id)
            self.ui.componentBricksListWidget.addItem(item)

        # Also refresh tree if it exists
        if hasattr(self.ui, 'componentTreeWidget'):
            self._refresh_component_tree()

    def _refresh_component_tree(self):
        """Refresh the component tree view"""
        self.ui.componentTreeWidget.clear()
        if not self.current_schema:
            return

        root = QTreeWidgetItem(self.ui.componentTreeWidget, [self.current_schema.name])
        for brick_id in self.current_schema.component_brick_ids:
            brick = self.brick_integration.get_brick_by_id(brick_id)
            brick_name = brick.name if hasattr(brick, 'name') else brick_id[:8]
            QTreeWidgetItem(root, [brick_name])
        root.setExpanded(True)

    # -------------------------------------------------------------------------
    # Library & Data Loading
    # -------------------------------------------------------------------------

    def load_initial_data(self):
        """Load initial data into UI"""
        self.refresh_schema_libraries()
        self.refresh_brick_libraries()
        self.refresh_brick_list()
        self.refresh_schema_list()
        self.ui.statusbar.showMessage("Ready")

    def refresh_schema_libraries(self):
        """Load schema libraries into combo"""
        libraries = self.schema_core.get_libraries()
        self.ui.libraryComboBox.clear()
        self.ui.libraryComboBox.addItems(libraries)
        if libraries:
            self.current_library = libraries[0]

    def refresh_brick_libraries(self):
        """Load brick libraries into combo"""
        libraries = self.brick_integration.get_brick_libraries()
        self.ui.brickLibraryComboBox.clear()
        self.ui.brickLibraryComboBox.addItems(libraries)

    def refresh_schema_list(self):
        """Load schemas into list widget"""
        self.ui.schemaListWidget.clear()
        schemas = self.schema_core.get_all_schemas()
        for schema in schemas:
            item = QListWidgetItem(schema.name)
            item.setData(Qt.ItemDataRole.UserRole, schema.schema_id)
            self.ui.schemaListWidget.addItem(item)

    def refresh_brick_list(self):
        """Load bricks into list widget"""
        self.ui.brickListWidget.clear()
        bricks = self.brick_integration.get_available_bricks()
        for brick in bricks:
            brick_dict = brick.to_dict() if hasattr(brick, 'to_dict') else brick
            item = QListWidgetItem(brick_dict.get('name', 'Unnamed'))
            item.setData(Qt.ItemDataRole.UserRole, brick_dict)
            self.ui.brickListWidget.addItem(item)

    # -------------------------------------------------------------------------
    # Signal Handlers
    # -------------------------------------------------------------------------

    def on_schema_library_changed(self, library_name: str):
        """Handle schema library change"""
        if library_name:
            self.schema_core.set_active_library(library_name)
            self.current_library = library_name
            self.refresh_schema_list()

    def on_brick_library_changed(self, library_name: str):
        """Handle brick library change"""
        if library_name:
            self.refresh_brick_list()

    def on_schema_selection_changed(self):
        """Handle schema selection"""
        item = self.ui.schemaListWidget.currentItem()
        if item:
            schema_id = item.data(Qt.ItemDataRole.UserRole)
            # Just enable delete button, don't auto-open
            self.ui.deleteSchemaButton.setEnabled(True)

    def on_schema_double_clicked(self, item):
        """Handle schema double-click - open the schema"""
        if not item:
            return
        schema_id = item.data(Qt.ItemDataRole.UserRole)
        # Find and open the schema
        for schema in self.schema_core.get_all_schemas():
            if schema.schema_id == schema_id:
                self.current_schema = schema
                self.load_schema_into_ui(schema)
                self.set_ui_state(self.EDIT)
                self.ui.statusbar.showMessage(f"Opened schema: {schema.name}")
                break

    def on_brick_selection_changed(self):
        """Handle brick selection"""
        has_selection = self.ui.brickListWidget.currentItem() is not None
        self.ui.addComponentButton.setEnabled(has_selection and self.current_schema is not None)

    def on_component_selection_changed(self):
        """Handle component selection"""
        has_selection = self.ui.componentBricksListWidget.currentItem() is not None
        self.ui.removeComponentButton.setEnabled(has_selection)

    def on_component_view_changed(self, use_tree: bool):
        """Handle view toggle between list and tree"""
        if hasattr(self.ui, 'componentStack'):
            self.ui.componentStack.setCurrentIndex(1 if use_tree else 0)

    def on_brick_search_changed(self, text: str):
        """Handle brick search filter"""
        for i in range(self.ui.brickListWidget.count()):
            item = self.ui.brickListWidget.item(i)
            brick_data = item.data(Qt.ItemDataRole.UserRole) or {}
            brick_name = brick_data.get('name', '').lower()
            item.setHidden(text.lower() not in brick_name)

    # -------------------------------------------------------------------------
    # Dialog Handlers
    # -------------------------------------------------------------------------

    def open_ui_metadata_editor(self):
        """Open metadata editor for selected component"""
        QMessageBox.information(self, "Not Implemented", "UI metadata editor not yet implemented.")

    def open_ui_metadata_editor_tree(self):
        """Open metadata editor for tree-selected component"""
        self.open_ui_metadata_editor()

    def validate_schema(self):
        """Validate current schema"""
        if not self.current_schema:
            QMessageBox.warning(self, "No Schema", "Please create or open a schema first.")
            return
        QMessageBox.information(self, "Validation", "Schema validation not yet implemented.")

    def create_daisy_chain(self):
        """Create daisy chain from current schema"""
        QMessageBox.information(self, "Not Implemented", "Daisy chain creation not yet implemented.")

    def extend_schema(self):
        """Extend current schema"""
        QMessageBox.information(self, "Not Implemented", "Schema extension not yet implemented.")

    def generate_web_form(self):
        """Generate web form for current schema"""
        if not self.current_schema:
            QMessageBox.warning(self, "No Schema", "Please create or open a schema first.")
            return
        try:
            lib_name = self.schema_core.active_library
            output_dir = os.path.join(self.schema_core.repository_path, lib_name)
            SHACLExporter(self.brick_integration).export_all(self.current_schema, output_dir)
            self.ui.statusbar.showMessage(f"Generated web form in: {output_dir}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate form: {e}")

    def show_schema_guide(self):
        """Show schema guide help"""
        QMessageBox.information(self, "Schema Guide", "Schema construction guide:\n\n1. Create or open a schema\n2. Add bricks as components\n3. Configure flow steps\n4. Save and export")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About", "Schema App v2\n\nA tool for constructing SHACL-based data entry schemas.")

    def new_library(self):
        """Create new schema library"""
        name, ok = QInputDialog.getText(self, "New Library", "Enter library name:")
        if ok and name.strip():
            try:
                lib_path = os.path.join(self.schema_core.repository_path, name.strip())
                os.makedirs(lib_path, exist_ok=True)
                self.refresh_schema_libraries()
                self.ui.libraryComboBox.setCurrentText(name.strip())
                self.ui.statusbar.showMessage(f"Created library: {name.strip()}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create library: {e}")

    def closeEvent(self, event):
        """Handle application close"""
        if self.current_schema and self.modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Do you want to save before exiting?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.save_schema()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        event.accept()
