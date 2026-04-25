#!/usr/bin/env python3
"""
Clean Schema GUI Module
Following v2 brick app pattern with proper controller separation
"""

import sys
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, 
    QFileDialog, QInputDialog, QDialog
)
from PyQt6.QtCore import Qt

# Import core components
from schema_app_v2.core.schema_core import SchemaCore, Schema
from schema_app_v2.core.flow_engine import FlowEngine, FlowConfig
from schema_app_v2.core.brick_integration import BrickIntegration

# Import controller
from .schema_controller import SchemaController

# Import UI components
from .ui_components import UiLoader, ComponentManager
from .help_dialog import HelpDialog
from .ui_state_manager import UIStateManager, SchemaState


class CleanSchemaGUI(QMainWindow):
    """Clean schema construction GUI with proper controller pattern"""
    
    def __init__(self, schema_repository_path: str = None,
                 brick_repository_path: str = None, use_shared_libraries: bool = True):
        super().__init__()
        
        # Initialize controller
        self.controller = SchemaController(
            SchemaCore(schema_repository_path),
            BrickIntegration(brick_repository_path),
            FlowEngine()
        )
        
        # Load UI from .ui file using existing UiLoader
        from .ui_components import UiLoader
        self.ui_loader = UiLoader()
        self.ui = self.ui_loader.load_main_window()
        self.setCentralWidget(self.ui)
        
        # Initialize state manager
        self.state_manager = UIStateManager()
        
        # Component manager for UI interactions
        self.components = ComponentManager()
        
        # Setup UI
        self.setup_ui()
        self.register_ui_widgets()
        self.connect_signals()
        self.connect_state_signals()
        self.load_initial_data()
        
        # Window setup
        self.setWindowTitle("Schema App v2 - Clean Interface")
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
        
        # Library menu
        self.ui.manageLibrariesAction.triggered.connect(self.manage_libraries)
        
        # Help menu
        self.ui.aboutAction.triggered.connect(self.show_about)
    
    def connect_signals(self):
        """Connect UI signals to handlers using controller"""
        # Schema management
        self.ui.schemaListWidget.itemSelectionChanged.connect(self.on_schema_selection_changed)
        self.ui.newSchemaButton.clicked.connect(self.new_schema)
        self.ui.deleteSchemaButton.clicked.connect(self.delete_schema)
        
        # Brick management
        self.ui.brickSearchLineEdit.textChanged.connect(self.on_brick_search_changed)
        self.ui.brickListWidget.itemDoubleClicked.connect(self.add_brick_as_component)
        
        # Component management
        self.ui.removeComponentButton.clicked.connect(self.remove_component_brick)
        self.ui.componentBricksListWidget.itemSelectionChanged.connect(self.on_component_selection_changed)
        # Note: addComponentButton and popup removed - double-click adds components directly
        
        # Schema details
        self.ui.rootBrickComboBox.currentTextChanged.connect(self.on_root_brick_changed)
        
        # Flow management
        self.ui.flowTypeComboBox.currentTextChanged.connect(self.on_flow_type_changed)
        self.ui.editFlowButton.clicked.connect(self.edit_flow)
        
        # Action buttons
        self.ui.saveButton.clicked.connect(self.save_schema)
        self.ui.exportShaclButton.clicked.connect(self.export_schema)
    
    def load_initial_data(self):
        """Load initial data into UI"""
        self.refresh_library_list()
        self.refresh_brick_library_list()
        self.refresh_schema_list()
        self.refresh_brick_list()
        self.refresh_root_bricks()
        # Set initial state to INITIAL
        self.state_manager.set_state(SchemaState.INITIAL)
    
    def refresh_library_list(self):
        """Refresh library list"""
        self.ui.libraryComboBox.clear()
        libraries = self.controller.get_libraries()
        if libraries:
            self.ui.libraryComboBox.addItems(libraries)
            # Set current library if available
            current_library = getattr(self.controller.schema_core, 'active_library', 'default')
            if current_library in libraries:
                index = self.ui.libraryComboBox.findText(current_library)
                if index >= 0:
                    self.ui.libraryComboBox.setCurrentIndex(index)
    
    def refresh_brick_library_list(self):
        """Refresh brick library list"""
        self.ui.brickLibraryComboBox.clear()
        brick_libraries = self.controller.get_brick_libraries()
        if brick_libraries:
            self.ui.brickLibraryComboBox.addItems(brick_libraries)
            # Set current brick library if available
            current_brick_library = getattr(self.controller.brick_integration.brick_core, 'active_library', 'default')
            if current_brick_library in brick_libraries:
                index = self.ui.brickLibraryComboBox.findText(current_brick_library)
                if index >= 0:
                    self.ui.brickLibraryComboBox.setCurrentIndex(index)
    
    # Schema Management Methods
    def new_schema(self):
        """Create new schema"""
        name, ok = QInputDialog.getText(self, "New Schema", "Enter schema name:")
        if ok and name.strip():
            schema = self.controller.create_new_schema(name.strip())
            if schema:
                self.refresh_schema_list()
                # Load schema into UI and enable details for editing
                self.load_schema_into_ui(schema)
                self.connect_schema_detail_signals()
                # Set state to SCHEMA_SELECTED to enable schema details
                self.state_manager.set_current_schema(schema, False)
                self.ui.statusbar.showMessage(f"Created new schema: {name} - Ready for editing")
    
    def open_schema(self):
        """Open existing schema"""
        schemas = self.controller.get_all_schemas()
        if not schemas:
            QMessageBox.information(self, "No Schemas", "No schemas found in current library.")
            return
        
        schema_names = [s.name for s in schemas]
        name, ok = QInputDialog.getItem(self, "Open Schema", "Select schema:", schema_names, 0, False)
        if ok and name:
            if self.controller.select_schema(name):
                self.refresh_schema_list()
                self.load_schema_into_ui(self.controller.current_schema)
                self.connect_schema_detail_signals()
                # Use state manager for UI state
                self.state_manager.set_current_schema(self.controller.current_schema, False)
                self.ui.statusbar.showMessage(f"Opened schema: {name}")
    
    def save_schema(self):
        """Save current schema"""
        if self.controller.current_schema:
            # Use state manager for save process
            self.state_manager.start_saving()
            try:
                if self.controller.save_current_schema():
                    self.state_manager.mark_schema_saved()
                else:
                    # Revert to modified state on failure
                    self.state_manager.set_state(SchemaState.SCHEMA_MODIFIED)
                    QMessageBox.warning(self, "Error", "Failed to save schema")
            except Exception as e:
                # Revert to modified state on error
                self.state_manager.set_state(SchemaState.SCHEMA_MODIFIED)
                QMessageBox.critical(self, "Error", f"Save failed: {str(e)}")
    
    def delete_schema(self):
        """Delete current schema"""
        if self.controller.current_schema:
            reply = QMessageBox.question(
                self, "Delete Schema", 
                f"Are you sure you want to delete schema '{self.controller.current_schema.name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.controller.delete_current_schema():
                    self.refresh_schema_list()
                    # Use state manager for UI state
                    self.state_manager.set_current_schema(None, False)
                    self.state_manager.clear_form_fields()
                    self.refresh_component_list()
                    self.ui.statusbar.showMessage("Schema deleted successfully!")
    
    # Component Management Methods
    def add_component_brick(self):
        """Add component brick to current schema"""
        # Use state manager for component addition process
        self.state_manager.start_component_adding()
        
        # Show component selection dialog
        from .add_component_dialog import AddComponentDialog
        dialog = AddComponentDialog(self.controller, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_brick_id = dialog.get_selected_brick()
            if selected_brick_id:
                if self.controller.add_component_to_schema(selected_brick_id):
                    self.refresh_component_list()
                    # Mark schema as modified
                    self.state_manager.mark_schema_modified()
                    QMessageBox.information(self, "Success", 
                        f"Component '{selected_brick_id}' added to schema successfully!")
        
        # Always finish component adding process
        self.state_manager.finish_component_adding(was_modified=True)
    
    def remove_component_brick(self):
        """Remove component brick from current schema"""
        current_item = self.ui.componentBricksListWidget.currentItem()
        if current_item:
            brick_id = current_item.data(Qt.ItemDataRole.UserRole)
            if brick_id:
                if self.controller.remove_component_from_schema(brick_id):
                    self.refresh_component_list()
                    # Mark schema as modified
                    self.state_manager.mark_schema_modified()
                    QMessageBox.information(self, "Success", 
                        f"Component '{brick_id}' removed from schema successfully!")
    
    def add_brick_as_component(self, item):
        """Add brick as component from double-click"""
        brick_name = item.text()
        all_bricks = self.controller.get_available_bricks()
        for brick in all_bricks:
            if brick.name == brick_name:
                if self.controller.add_component_to_schema(brick.brick_id):
                    self.refresh_component_list()
                    # Mark schema as modified
                    self.state_manager.mark_schema_modified()
                    QMessageBox.information(self, "Success", 
                        f"Component '{brick_name}' added to schema successfully!")
                break
    
    # UI Helper Methods
    def on_schema_selection_changed(self):
        """Handle schema selection change"""
        items = self.ui.schemaListWidget.selectedItems()
        print(f"DEBUG: Schema selection changed, items: {len(items)}")
        if items:
            schema_name = items[0].text()
            print(f"DEBUG: Selected schema: {schema_name}")
            if self.controller.select_schema(schema_name):
                print(f"DEBUG: Schema selected successfully")
                self.load_schema_into_ui(self.controller.current_schema)
                self.connect_schema_detail_signals()
                # Use state manager for UI state
                self.state_manager.set_current_schema(self.controller.current_schema, False)
            else:
                print(f"DEBUG: Failed to select schema")
        else:
            print(f"DEBUG: No schema selected")
            # No selection, use state manager
            self.state_manager.set_current_schema(None, False)
    
    def on_brick_search_changed(self, text):
        """Handle brick search"""
        self.refresh_brick_list(search_term=text)
    
    def on_root_brick_changed(self, brick_name):
        """Handle root brick change"""
        if self.controller.current_schema and brick_name:
            all_bricks = self.controller.get_available_bricks()
            for brick in all_bricks:
                if brick.name == brick_name:
                    self.controller.update_schema_details(root_brick_id=brick.brick_id)
                    # Mark schema as modified
                    self.state_manager.mark_schema_modified()
                    break
    
    def on_flow_type_changed(self, flow_type):
        """Handle flow type change"""
        if self.controller.current_schema and flow_type:
            # Update flow configuration
            pass  # Would integrate with flow engine
    
    def edit_flow(self):
        """Edit flow configuration"""
        # Use state manager for flow editing process
        self.state_manager.start_flow_editing()
        
        # Show flow editor dialog (placeholder)
        QMessageBox.information(self, "Edit Flow", "Flow editor coming soon")
        
        # Finish flow editing process
        self.state_manager.finish_flow_editing(was_modified=False)
    
    def preview_schema(self):
        """Preview schema"""
        QMessageBox.information(self, "Preview", "Schema preview coming soon")
    
    def export_schema(self):
        """Export schema"""
        QMessageBox.information(self, "Export", "Schema export coming soon")
    
    def on_component_selection_changed(self):
        """Handle component selection change"""
        current_item = self.ui.componentBricksListWidget.currentItem()
        has_selection = current_item is not None
        # Update remove button state based on selection
        self.state_manager.update_remove_button_state(has_selection)
    
    # UI State Management
    def connect_schema_detail_signals(self):
        """Connect schema detail signals when schema is selected"""
        self.ui.nameLineEdit.textChanged.connect(self.on_schema_details_changed)
        self.ui.descriptionLineEdit.textChanged.connect(self.on_schema_details_changed)
    
    def on_schema_details_changed(self):
        """Handle schema details change"""
        if self.controller.current_schema:
            name = self.ui.nameLineEdit.text().strip()
            description = self.ui.descriptionLineEdit.text().strip()
            self.controller.update_schema_details(name=name, description=description)
            # Mark schema as modified
            self.state_manager.mark_schema_modified()
    
    def load_schema_into_ui(self, schema):
        """Load schema data into UI"""
        self.ui.nameLineEdit.setText(schema.name)
        self.ui.descriptionLineEdit.setText(schema.description or "")
        
        # Load root brick
        if schema.root_brick_id:
            brick = self.controller.get_brick_by_id(schema.root_brick_id)
            if brick:
                index = self.ui.rootBrickComboBox.findText(brick.name)
                if index >= 0:
                    self.ui.rootBrickComboBox.setCurrentIndex(index)
        
        # Load component bricks
        self.refresh_component_list()
    
    def refresh_schema_list(self):
        """Refresh schema list"""
        self.ui.schemaListWidget.clear()
        schemas = self.controller.get_all_schemas()
        for schema in schemas:
            self.ui.schemaListWidget.addItem(schema.name)
    
    def refresh_brick_list(self, search_term=""):
        """Refresh brick list"""
        self.ui.brickListWidget.clear()
        bricks = self.controller.get_available_bricks()
        
        if search_term:
            search_lower = search_term.lower()
            bricks = [b for b in bricks if search_lower in b.name.lower()]
        
        for brick in bricks:
            self.ui.brickListWidget.addItem(brick.name)
    
    def refresh_component_list(self):
        """Refresh component list"""
        self.ui.componentBricksListWidget.clear()
        if self.controller.current_schema:
            for brick_id in self.controller.current_schema.component_brick_ids:
                brick = self.controller.get_brick_by_id(brick_id)
                if brick:
                    from PyQt6.QtWidgets import QListWidgetItem
                    item = QListWidgetItem(brick.name)
                    item.setData(Qt.ItemDataRole.UserRole, brick_id)
                    self.ui.componentBricksListWidget.addItem(item)
        # Reset remove button state (no selection initially)
        self.state_manager.update_remove_button_state(False)
    
    def refresh_root_bricks(self):
        """Refresh root brick options"""
        self.ui.rootBrickComboBox.clear()
        self.ui.rootBrickComboBox.addItem("Select root brick...")
        
        root_bricks = self.controller.get_node_shape_bricks()
        for brick in root_bricks:
            self.ui.rootBrickComboBox.addItem(brick.name, brick.brick_id)
    
    def register_ui_widgets(self):
        """Register UI widgets with state manager"""
        # Register all widgets that need state management
        widgets_to_register = [
            "nameLineEdit", "descriptionLineEdit", "rootBrickComboBox",
            "addComponentButton", "removeComponentButton", "componentBricksListWidget",
            "flowTypeComboBox", "editFlowButton", "saveButton", "exportShaclButton",
            "schemaListWidget", "newSchemaButton", "deleteSchemaButton",
            "brickListWidget", "brickSearchLineEdit", "libraryComboBox", "brickLibraryComboBox",
            # Group containers
            "bricksGroupBox", "schemaDetailsGroupBox"
        ]
        
        for widget_name in widgets_to_register:
            widget = getattr(self.ui, widget_name, None)
            if widget:
                self.state_manager.register_widget(widget_name, widget)
    
    def connect_state_signals(self):
        """Connect state manager signals"""
        self.state_manager.state_changed.connect(self.on_state_changed)
        self.state_manager.schema_modified.connect(self.on_schema_modified)
        self.state_manager.schema_saved.connect(self.on_schema_saved)
        self.state_manager.schema_selected.connect(self.on_schema_selected)
        self.state_manager.schema_deselected.connect(self.on_schema_deselected)
    
    def on_state_changed(self, old_state: SchemaState, new_state: SchemaState):
        """Handle state changes with visual feedback"""
        # Update status bar with current state
        state_messages = {
            SchemaState.INITIAL: "Ready - No schema selected",
            SchemaState.SCHEMA_SELECTED: "Schema loaded - Ready for editing",
            SchemaState.SCHEMA_MODIFIED: "Schema modified - Unsaved changes",
            SchemaState.SCHEMA_SAVING: "Saving schema...",
            SchemaState.COMPONENT_ADDING: "Adding component...",
            SchemaState.FLOW_EDITING: "Editing flow configuration..."
        }
        message = state_messages.get(new_state, "Unknown state")
        self.ui.statusbar.showMessage(message)
        
        # Add visual indicators for modified state
        if new_state == SchemaState.SCHEMA_MODIFIED:
            self.ui.saveButton.setStyleSheet("QPushButton { background-color: #ffeb3b; font-weight: bold; }")
        else:
            self.ui.saveButton.setStyleSheet("")
    
    def on_schema_modified(self):
        """Handle schema modification"""
        self.ui.statusbar.showMessage("Schema modified - Click save to preserve changes")
    
    def on_schema_saved(self):
        """Handle successful save"""
        self.ui.statusbar.showMessage("Schema saved successfully!")
    
    def on_schema_selected(self, schema):
        """Handle schema selection via state manager"""
        pass  # Additional logic when schema is selected
    
    def on_schema_deselected(self):
        """Handle schema deselection via state manager"""
        pass  # Additional logic when schema is deselected
    
    def set_ui_state(self, has_schema: bool):
        """Enable/disable UI based on schema state (deprecated - use state manager)"""
        # Use enhanced state manager instead
        if has_schema:
            self.state_manager.set_current_schema(self.controller.current_schema, False)
        else:
            self.state_manager.set_current_schema(None, False)
    
    # Menu Actions
    def manage_libraries(self):
        """Manage libraries dialog"""
        QMessageBox.information(self, "Library Management", "Library management feature coming soon.")
    
    def show_help(self):
        """Show help dialog"""
        help_dialog = HelpDialog(self)
        help_dialog.exec()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Schema App v2", 
                         "Clean, modular schema construction system\n"
                         "Following v2 brick app architecture")


def main():
    """Main entry point for clean GUI"""
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = CleanSchemaGUI()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    main()
