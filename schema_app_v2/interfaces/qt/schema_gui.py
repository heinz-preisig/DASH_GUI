"""
Schema GUI Module - Minimal Working Version
Minimal PyQt interface that bypasses complex import issues
"""

import sys
import os
from typing import Optional, Dict, List, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QMessageBox, 
    QFileDialog, QInputDialog, QDialog
)
from PyQt6.QtCore import Qt

# Use absolute imports from schema_app_v2 package
from schema_app_v2.core.schema_core import SchemaCore, Schema
from schema_app_v2.core.flow_engine import FlowEngine, FlowType, FlowStep, FlowConfig
from schema_app_v2.core.brick_integration import BrickIntegration
from schema_app_v2.core.schema_helper import SchemaHelper

from .ui_components import UiLoader, ComponentManager
from .help_dialog import HelpDialog


class SchemaGUI(QMainWindow):
    """Main schema construction GUI"""
    
    def __init__(self, schema_repository_path: str = "schema_repositories",
                 brick_repository_path: str = "brick_repositories"):
        super().__init__()
        
        # Initialize core components
        self.schema_core = SchemaCore(schema_repository_path)
        self.flow_engine = FlowEngine()
        self.brick_integration = BrickIntegration(brick_repository_path)
        
        # Initialize helper for user-friendly features
        self.helper = SchemaHelper()
        
        # Load UI from .ui file
        self.ui_loader = UiLoader()
        self.ui = self.ui_loader.load_main_window()
        self.setCentralWidget(self.ui)
        
        # Component manager for UI interactions
        self.components = ComponentManager()
        
        # Current state
        self.current_schema: Optional[Schema] = None
        self.current_flow: Optional[FlowConfig] = None
        
        # Setup UI
        self.setup_ui()
        self.connect_signals()
        self.load_initial_data()
        
        # Window setup
        self.setWindowTitle("Schema App v2 - Schema Constructor")
        self.setGeometry(50, 50, 1400, 900)
    
    def setup_ui(self):
        """Setup UI components"""
        # Setup menu bar actions
        self.setup_menu_actions()
        
    def setup_menu_actions(self):
        """Setup menu bar actions"""
        # File menu
        self.ui.newSchemaAction.triggered.connect(self.new_schema)
        self.ui.openSchemaAction.triggered.connect(self.open_schema)
        self.ui.saveSchemaAction.triggered.connect(self.save_schema)
        self.ui.exportShaclAction.triggered.connect(self.export_shacl)
        self.ui.exitAction.triggered.connect(self.close)
        
        # Tools menu
        self.ui.manageLibrariesAction.triggered.connect(self.manage_libraries)
        self.ui.validateSchemaAction.triggered.connect(self.validate_schema)
        
        # Help menu
        help_action = self.ui.helpMenu.addAction("Help & Guide")
        help_action.triggered.connect(self.show_help)
        self.ui.helpMenu.addSeparator()
        self.ui.aboutAction.triggered.connect(self.show_about)
    
    def connect_signals(self):
        """Connect UI signals to handlers"""
        # Library management
        self.ui.libraryComboBox.currentTextChanged.connect(self.on_schema_library_changed)
        self.ui.brickLibraryComboBox.currentTextChanged.connect(self.on_brick_library_changed)
        
        # Schema management
        self.ui.schemaListWidget.itemSelectionChanged.connect(self.on_schema_selection_changed)
        self.ui.newSchemaButton.clicked.connect(self.new_schema)
        self.ui.deleteSchemaButton.clicked.connect(self.delete_schema)
        
        # Brick management
        self.ui.brickSearchLineEdit.textChanged.connect(self.on_brick_search_changed)
        self.ui.brickListWidget.itemDoubleClicked.connect(self.add_brick_as_component)
        
        # Schema details (only connect when schema exists)
        # Note: These will be connected when schema is created/selected
        
        # Component management
        self.ui.addComponentButton.clicked.connect(self.add_component_brick)
        self.ui.removeComponentButton.clicked.connect(self.remove_component_brick)
        self.ui.componentBricksListWidget.itemSelectionChanged.connect(self.on_component_selection_changed)
        
        # Flow management
        self.ui.flowTypeComboBox.currentTextChanged.connect(self.on_flow_type_changed)
        self.ui.editFlowButton.clicked.connect(self.edit_flow)
        
        # Action buttons
        self.ui.saveButton.clicked.connect(self.save_schema)
        self.ui.exportShaclButton.clicked.connect(self.export_shacl)
    
    def load_initial_data(self):
        """Load initial data into UI"""
        # Load available libraries
        self.refresh_schema_libraries()
        self.refresh_brick_libraries()
        
        # Load available bricks
        self.refresh_brick_list()
        
        # Load available schemas
        self.refresh_schema_list()
        
        # Load root brick options
        self.refresh_root_bricks()
        
        self.ui.statusbar.showMessage("Ready")
    
    def new_schema(self):
        """Create a new schema"""
        name, ok = QInputDialog.getText(self, "New Schema", "Enter schema name:")
        if not ok or not name.strip():
            return
        
        # Create new schema
        schema = self.schema_core.create_schema(name.strip())
        self.current_schema = schema
        
        # Update UI
        self.refresh_schema_list()
        self.load_schema_into_ui(schema)
        self.set_ui_state(True)
        
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
        
        # Find and load the schema
        for schema in schemas:
            if schema.name == name:
                self.current_schema = schema
                self.load_schema_into_ui(schema)
                self.set_ui_state(True)
                self.ui.statusbar.showMessage(f"Opened schema: {name}")
                break
    
    def save_schema(self):
        """Save current schema"""
        if not self.current_schema:
            return
        
        try:
            self.schema_core.save_schema(self.current_schema)
            self.ui.statusbar.showMessage(f"Saved schema: {self.current_schema.name}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save schema: {e}")
    
    def export_shacl(self):
        """Export schema as SHACL"""
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
            exporter = SHACLExporter()
            exporter.export_schema(self.current_schema, file_path)
            self.ui.statusbar.showMessage(f"Exported SHACL to: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export SHACL: {e}")
    
    def show_help(self):
        """Show help dialog"""
        help_dialog = HelpDialog(self)
        
        # Handle template selection if any
        if help_dialog.exec() == QDialog.DialogCode.Accepted:
            template = help_dialog.get_selected_template()
            if template:
                self.create_schema_from_template(template)

    def manage_libraries(self):
        """Manage libraries dialog"""
        QMessageBox.information(self, "Library Management", "Library management feature coming soon.")
    
    def validate_schema(self):
        """Validate current schema"""
        if not self.current_schema:
            QMessageBox.warning(self, "No Schema", "Please create or open a schema first.")
            return
        
        try:
            # Basic validation
            if not self.current_schema.name:
                raise ValueError("Schema name is required")
            if not self.current_schema.root_brick_id:
                raise ValueError("Root brick is required")
            
            QMessageBox.information(self, "Validation", "Schema validation passed!")
            self.ui.statusbar.showMessage("Schema validation passed")
        except Exception as e:
            QMessageBox.critical(self, "Validation Error", f"Schema validation failed: {e}")
    
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
            try:
                self.schema_core.delete_schema(self.current_schema.schema_id)
                self.current_schema = None
                self.refresh_schema_list()
                self.set_ui_state(False)
                self.ui.statusbar.showMessage("Schema deleted")
            except Exception as e:
                QMessageBox.critical(self, "Delete Error", f"Failed to delete schema: {e}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Schema App v2", 
                         "Schema App v2\nClean, modular schema construction system\n\n"
                         "Version: 2.0.0\n"
                         "Features: Brick-based schema construction, Flow management, SHACL export")
    
    def on_schema_library_changed(self, library_name):
        """Handle schema library change"""
        self.refresh_schema_list()
        self.ui.statusbar.showMessage(f"Changed to library: {library_name}")
    
    def on_brick_library_changed(self, library_name):
        """Handle brick library change"""
        self.refresh_brick_list()
        self.ui.statusbar.showMessage(f"Changed brick library: {library_name}")
    
    def on_schema_selection_changed(self):
        """Handle schema selection change"""
        items = self.ui.schemaListWidget.selectedItems()
        if items:
            schema_name = items[0].text()
            schemas = self.schema_core.get_all_schemas()
            for schema in schemas:
                if schema.name == schema_name:
                    self.current_schema = schema
                    self.load_schema_into_ui(schema)
                    self.set_ui_state(True)
                    
                    # Connect schema detail signals now that we have a schema
                    self.ui.nameLineEdit.textChanged.connect(self.on_schema_details_changed)
                    self.ui.descriptionLineEdit.textChanged.connect(self.on_schema_details_changed)
                    self.ui.rootBrickComboBox.currentTextChanged.connect(self.on_root_brick_changed)
                    break
    
    def on_brick_search_changed(self, text):
        """Handle brick search"""
        self.refresh_brick_list(search_term=text)
    
    def add_brick_as_component(self, item):
        """Add brick as component from double-click"""
        brick_name = item.text()
        all_bricks = self.brick_integration.get_available_bricks()
        bricks = [brick for brick in all_bricks if brick.name == brick_name]
        if bricks and self.current_schema:
            self.current_schema.component_brick_ids.append(bricks[0].brick_id)
            self.refresh_component_list()
            self.ui.statusbar.showMessage(f"Added component: {brick_name}")
    
    def on_schema_details_changed(self):
        """Handle schema detail changes"""
        if self.current_schema:
            self.current_schema.name = self.ui.nameLineEdit.text()
            self.current_schema.description = self.ui.descriptionLineEdit.text()
    
    def on_root_brick_changed(self, brick_name):
        """Handle root brick change"""
        if self.current_schema and brick_name:
            all_bricks = self.brick_integration.get_available_bricks()
            bricks = [brick for brick in all_bricks if brick.name == brick_name]
            if bricks:
                self.current_schema.root_brick_id = bricks[0].brick_id
    
    def add_component_brick(self):
        """Add component brick button handler"""
        if not self.current_schema:
            QMessageBox.warning(self, "No Schema", "Please create or select a schema first")
            return
        
        # Show component selection dialog
        dialog = AddComponentDialog(self.brick_integration, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_brick_id = dialog.get_selected_brick()
            if selected_brick_id:
                try:
                    # Add component to schema
                    self.brick_integration.add_component_to_schema(
                        self.current_schema.schema_id, selected_brick_id
                    )
                    
                    # Update UI
                    self.refresh_component_list()
                    QMessageBox.information(self, "Success", 
                        f"Component '{selected_brick_id}' added to schema successfully!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to add component: {str(e)}")
    
    def remove_component_brick(self):
        """Remove component brick button handler"""
        QMessageBox.information(self, "Remove Component", "Feature coming soon")
    
    def on_component_selection_changed(self):
        """Handle component selection change"""
        pass
    
    def on_flow_type_changed(self, flow_type):
        """Handle flow type change"""
        if self.current_schema and flow_type:
            try:
                flow_enum = FlowType(flow_type)
                self.current_schema.flow_config = self.flow_engine.create_flow(
                    f"Flow for {self.current_schema.name}", flow_enum
                )
            except ValueError:
                pass
    
    def edit_flow(self):
        """Edit flow button handler"""
        QMessageBox.information(self, "Edit Flow", "Flow editor coming soon")
    
    def refresh_schema_libraries(self):
        """Refresh schema library list"""
        # Placeholder for library loading
        pass
    
    def refresh_brick_libraries(self):
        """Refresh brick library list"""
        # Placeholder for library loading
        pass
    
    def refresh_brick_list(self, search_term=""):
        """Refresh brick list"""
        self.ui.brickListWidget.clear()
        if search_term:
            # Simple search implementation - filter available bricks by name
            all_bricks = self.brick_integration.get_available_bricks()
            bricks = [brick for brick in all_bricks if search_term.lower() in brick.name.lower()]
        else:
            bricks = self.brick_integration.get_available_bricks()
        for brick in bricks:
            self.ui.brickListWidget.addItem(brick.name)
    
    def refresh_schema_list(self):
        """Refresh schema list"""
        self.ui.schemaListWidget.clear()
        schemas = self.schema_core.get_all_schemas()
        for schema in schemas:
            self.ui.schemaListWidget.addItem(schema.name)
    
    def refresh_root_bricks(self):
        """Refresh root brick options"""
        self.ui.rootBrickComboBox.clear()
        root_bricks = self.brick_integration.get_node_shape_bricks()
        for brick in root_bricks:
            self.ui.rootBrickComboBox.addItem(brick.name)
    
    def refresh_component_list(self):
        """Refresh component list"""
        self.ui.componentBricksListWidget.clear()
        if self.current_schema:
            for brick_id in self.current_schema.component_brick_ids:
                brick = self.brick_integration.get_brick_by_id(brick_id)
                if brick:
                    self.ui.componentBricksListWidget.addItem(brick.name)
    
    def load_schema_into_ui(self, schema):
        """Load schema data into UI"""
        self.ui.nameLineEdit.setText(schema.name)
        self.ui.descriptionLineEdit.setText(schema.description or "")
        
        # Load root brick
        if schema.root_brick_id:
            brick = self.brick_integration.get_brick_by_id(schema.root_brick_id)
            if brick:
                index = self.ui.rootBrickComboBox.findText(brick.name)
                if index >= 0:
                    self.ui.rootBrickComboBox.setCurrentIndex(index)
        
        # Load components
        self.refresh_component_list()
    
    def set_ui_state(self, has_schema):
        """Set UI state based on whether a schema is loaded"""
        self.ui.nameLineEdit.setEnabled(has_schema)
        self.ui.descriptionLineEdit.setEnabled(has_schema)
        self.ui.rootBrickComboBox.setEnabled(has_schema)
        self.ui.saveButton.setEnabled(has_schema)
        self.ui.exportShaclButton.setEnabled(has_schema)
    
    def create_schema_from_template(self, template):
        """Create schema from selected template"""
        # Create new schema with template name
        schema = self.schema_core.create_schema(template.name, template.description)
        
        # Try to find and set root brick
        root_bricks = self.brick_integration.get_node_shape_bricks()
        for brick in root_bricks:
            if template.root_brick_type.lower() in brick.name.lower():
                schema.root_brick_id = brick.brick_id
                break
        
        # Add suggested components if available
        for component_name in template.suggested_components:
            component_bricks = self.brick_integration.search_bricks(component_name)
            if component_bricks:
                schema.component_brick_ids.append(component_bricks[0].brick_id)
        
        # Set flow type
        if template.flow_type:
            flow_type = FlowType(template.flow_type)
            schema.flow_config = self.flow_engine.create_flow(
                f"Flow for {template.name}",
                flow_type,
                f"Auto-generated flow for {template.name}"
            )
        
        # Load into UI
        self.current_schema = schema
        self.load_schema_into_ui(schema)
        self.set_ui_state(True)
        
        self.ui.statusbar.showMessage(f"Created schema from template: {template.name}")

    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h3>Schema App v2</h3>
        <p>Schema Constructor for SHACL Bricks</p>
        <p>Version: 2.0</p>
        <p>Architecture: Simple, modular design following brick_app_v2</p>
        <p><strong>Features:</strong></p>
        <ul>
        <li>📋 Schema composition from bricks</li>
        <li>🔄 Flow configuration (sequential, conditional, parallel, dynamic)</li>
        <li>📤 SHACL export</li>
        <li>🎨 PyQt interface with .ui files</li>
        <li>💡 User-friendly help system</li>
        <li>📚 Templates for common use cases</li>
        </ul>
        <p><strong>Perfect for:</strong> Users who want to create data schemas without learning SHACL technical details</p>
        """
        
        QMessageBox.about(self, "About Schema App v2", about_text)

    def on_schema_library_changed(self):
        """Handle schema library change"""
        library_name = self.components.get_combo_box_current_text(self.ui.libraryComboBox)
        if library_name:
            self.schema_core.set_active_library(library_name)
            self.refresh_schema_list()
    
    def on_brick_library_changed(self):
        """Handle brick library change"""
        self.refresh_brick_list()
        self.refresh_root_bricks()
    
    def on_brick_search_changed(self):
        """Handle brick search text change"""
        self.refresh_brick_list()
    
    def on_schema_selection_changed(self):
        """Handle schema selection change"""
        pass  # Selection is handled by open_schema()
    
    def on_component_selection_changed(self):
        """Handle component brick selection change"""
        pass  # Could show component details here
    
    def on_schema_details_changed(self):
        """Handle schema details change"""
        if self.current_schema:
            self.update_preview()
    
    def update_preview(self):
        """Update schema preview"""
        # Placeholder for preview functionality
        pass
    
    def on_root_brick_changed(self):
        """Handle root brick change"""
        if self.current_schema:
            root_brick_id = self.ui.rootBrickComboBox.currentData()
            if root_brick_id and root_brick_id != "Select root brick...":
                self.current_schema.root_brick_id = root_brick_id
                self.update_preview()
    
    def on_flow_type_changed(self):
        """Handle flow type change"""
        if self.current_schema:
            flow_type_str = self.components.get_combo_box_current_text(self.ui.flowTypeComboBox)
            flow_type = FlowType(flow_type_str.lower())
            
            if not self.current_flow:
                # Create basic flow
                self.current_flow = self.flow_engine.create_flow(
                    f"Flow for {self.current_schema.name}",
                    flow_type,
                    f"Auto-generated flow for {self.current_schema.name}"
                )
                self.current_schema.flow_config = self.current_flow
            else:
                # Update flow type
                self.current_flow.flow_type = flow_type
            
            self.update_preview()
    
    def closeEvent(self, event):
        """Handle application close"""
        # Check for unsaved changes
        if self.current_schema:
            reply = self.components.ask_confirmation(
                self, "Unsaved Changes", 
                "You have unsaved changes. Do you want to save before exiting?"
            )
            
            if reply:
                self.save_schema()
        
        event.accept()


class AddComponentDialog(QDialog):
    """Dialog for adding components to a schema"""
    
    def __init__(self, brick_integration, parent=None):
        super().__init__(parent)
        self.brick_integration = brick_integration
        self.selected_brick_id = None
        self.setWindowTitle("Add Component")
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QListWidget, QDialogButtonBox
        
        layout = QVBoxLayout(self)
        
        # Instructions
        info_label = QLabel("Select a brick to add as a component:")
        layout.addWidget(info_label)
        
        # Brick list
        self.brick_list = QListWidget()
        self.brick_list.itemDoubleClicked.connect(self.on_brick_selected)
        layout.addWidget(self.brick_list)
        
        # Search/filter
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.filter_bricks)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # Filter by type
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "NodeShape", "PropertyShape"])
        self.type_filter.currentTextChanged.connect(self.filter_bricks)
        filter_layout.addWidget(self.type_filter)
        layout.addLayout(filter_layout)
        
        # Load bricks
        self.load_bricks()
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def load_bricks(self):
        """Load available bricks from backend"""
        self.brick_list.clear()
        
        # Get all bricks from brick integration
        bricks = self.brick_integration.get_available_bricks()
        for brick in bricks:
            display_text = f"{brick.name} ({brick.object_type})"
            if hasattr(brick, 'description') and brick.description:
                display_text += f" - {brick.description[:50]}..."
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, brick.brick_id)
            item.setData(Qt.ItemDataRole.UserRole + 1, brick)  # Store full brick data
            self.brick_list.addItem(item)
    
    def filter_bricks(self):
        """Filter bricks based on search and type"""
        search_text = self.search_edit.text().lower()
        filter_type = self.type_filter.currentText()
        
        for i in range(self.brick_list.count()):
            item = self.brick_list.item(i)
            brick_data = item.data(Qt.ItemDataRole.UserRole + 1)
            
            # Check search filter
            matches_search = True
            if search_text:
                matches_search = (
                    search_text in brick_data.name.lower() or
                    (hasattr(brick_data, 'description') and search_text in brick_data.description.lower())
                )
            
            # Check type filter
            matches_type = filter_type == "All" or brick_data.object_type == filter_type
            
            # Show/hide item
            item.setHidden(not (matches_search and matches_type))
    
    def on_brick_selected(self, item):
        """Handle brick selection"""
        self.selected_brick_id = item.data(Qt.ItemDataRole.UserRole)
        self.accept()
    
    def on_accept(self):
        """Handle OK button click"""
        current_item = self.brick_list.currentItem()
        if current_item:
            self.selected_brick_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.accept()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a brick to add")
    
    def get_selected_brick(self):
        """Get the selected brick ID"""
        return self.selected_brick_id


def main():
    """Main entry point for Qt interface"""
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = SchemaGUI()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
