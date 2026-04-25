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

# Add core modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from core.schema_core import SchemaCore, Schema
from core.flow_engine import FlowEngine, FlowType, FlowStep, FlowConfig
from core.brick_integration import BrickIntegration
from core.schema_helper import SchemaHelper

from .ui_components import UiLoader, ComponentManager
from .help_dialog import HelpDialog


class SchemaGUI(QMainWindow):
    """Main schema construction GUI"""
    
    def __init__(self, schema_repository_path: str = "schema_repositories",
                 brick_repository_path: str = "brick_repositories_v2"):
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
        
        # Schema details
        self.ui.nameLineEdit.textChanged.connect(self.on_schema_details_changed)
        self.ui.descriptionLineEdit.textChanged.connect(self.on_schema_details_changed)
        self.ui.rootBrickComboBox.currentTextChanged.connect(self.on_root_brick_changed)
        
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
    
    def show_help(self):
        """Show help dialog"""
        help_dialog = HelpDialog(self)
        
        # Handle template selection if any
        if help_dialog.exec() == QDialog.DialogCode.Accepted:
            template = help_dialog.get_selected_template()
            if template:
                self.create_schema_from_template(template)

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


def main():
    """Main entry point for Qt interface"""
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = SchemaGUI()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
