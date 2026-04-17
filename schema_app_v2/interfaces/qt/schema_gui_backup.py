"""
Schema GUI Module - Final Fixed Version
Main PyQt interface for schema construction using .ui files
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
    
    def refresh_schema_libraries(self):
        """Refresh schema library combo box"""
        libraries = self.schema_core.get_libraries()
        self.components.populate_combo_box(self.ui.libraryComboBox, libraries)
        
        if libraries and not self.schema_core.active_library:
            self.schema_core.set_active_library(libraries[0])
        
        if self.schema_core.active_library:
            self.components.set_combo_box_current_text(
                self.ui.libraryComboBox, self.schema_core.active_library
            )
    
    def refresh_brick_libraries(self):
        """Refresh brick library combo box"""
        try:
            libraries = self.brick_integration.get_brick_libraries()
            self.components.populate_combo_box(self.ui.brickLibraryComboBox, libraries)
        except Exception as e:
            print(f"Error loading brick libraries: {e}")
            self.components.populate_combo_box(self.ui.brickLibraryComboBox, [])
    
    def refresh_brick_list(self):
        """Refresh brick list widget"""
        try:
            library_name = self.components.get_combo_box_current_text(self.ui.brickLibraryComboBox)
            search_text = self.components.get_line_edit_text(self.ui.brickSearchLineEdit)
            
            if search_text:
                bricks = self.brick_integration.search_bricks(search_text, library_name)
            else:
                bricks = self.brick_integration.get_available_bricks(library_name)
            
            self.components.set_list_widget_data(self.ui.brickListWidget, bricks, 'brick_id')
            
        except Exception as e:
            print(f"Error loading bricks: {e}")
            self.components.clear_list_widget(self.ui.brickListWidget)
    
    def refresh_root_bricks(self):
        """Refresh root brick combo box"""
        try:
            library_name = self.components.get_combo_box_current_text(self.ui.brickLibraryComboBox)
            node_bricks = self.brick_integration.get_node_shape_bricks(library_name)
            
            self.ui.rootBrickComboBox.clear()
            self.ui.rootBrickComboBox.addItem("Select root brick...")
            for brick in node_bricks:
                self.ui.rootBrickComboBox.addItem(brick.name, brick.brick_id)
                
        except Exception as e:
            print(f"Error loading root bricks: {e}")
            self.ui.rootBrickComboBox.clear()
            self.ui.rootBrickComboBox.addItem("No bricks available")
    
    def refresh_schema_list(self):
        """Refresh schema list widget"""
        schemas = self.schema_core.get_all_schemas()
        self.components.set_list_widget_data(self.ui.schemaListWidget, schemas, 'schema_id')
    
    def set_ui_state(self, schema_loaded: bool):
        """Set UI state based on whether a schema is loaded"""
        # Enable/disable components
        self.components.set_enabled(self.ui.nameLineEdit, schema_loaded)
        self.components.set_enabled(self.ui.descriptionLineEdit, schema_loaded)
        self.components.set_enabled(self.ui.rootBrickComboBox, schema_loaded)
        self.components.set_enabled(self.ui.addComponentButton, schema_loaded)
        self.components.set_enabled(self.ui.removeComponentButton, schema_loaded)
        self.components.set_enabled(self.ui.componentBricksListWidget, schema_loaded)
        self.components.set_enabled(self.ui.flowTypeComboBox, schema_loaded)
        self.components.set_enabled(self.ui.editFlowButton, schema_loaded)
        self.components.set_enabled(self.ui.saveButton, schema_loaded)
        self.components.set_enabled(self.ui.exportShaclButton, schema_loaded)
        
        # Enable/disable actions
        self.ui.saveSchemaAction.setEnabled(schema_loaded)
        self.ui.exportShaclAction.setEnabled(schema_loaded)
        self.ui.validateSchemaAction.setEnabled(schema_loaded)
        
        if not schema_loaded:
            # Clear fields
            self.components.set_line_edit_text(self.ui.nameLineEdit, "")
            self.components.set_line_edit_text(self.ui.descriptionLineEdit, "")
            self.components.clear_list_widget(self.ui.componentBricksListWidget)
            self.components.clear_list_widget(self.ui.flowStepsListWidget)
            self.components.set_text_edit_text(self.ui.previewTextEdit, "")
    
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

    # Event handlers
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
        # Get selected schema
        schema_id = self.components.get_selected_list_data(self.ui.schemaListWidget)
        if not schema_id:
            self.components.show_warning_message(self, "No Selection", "Please select a schema to open.")
            return
        
        # Load schema
        schema = self.schema_core.load_schema(schema_id)
        if schema:
            self.current_schema = schema
            self.load_schema_into_ui(schema)
            self.set_ui_state(True)
            self.ui.statusbar.showMessage(f"Loaded schema: {schema.name}")
        else:
            self.components.show_error_message(self, "Error", "Failed to load schema.")
    
    def load_schema_into_ui(self, schema):
        """Load schema data into UI"""
        # Basic details
        self.components.set_line_edit_text(self.ui.nameLineEdit, schema.name)
        self.components.set_line_edit_text(self.ui.descriptionLineEdit, schema.description)
        
        # Root brick
        if schema.root_brick_id:
            # Find and select root brick
            for i in range(self.ui.rootBrickComboBox.count()):
                if self.ui.rootBrickComboBox.itemData(i) == schema.root_brick_id:
                    self.ui.rootBrickComboBox.setCurrentIndex(i)
                    break
        
        # Component bricks
        self.refresh_component_bricks()
        
        # Flow configuration
        if schema.flow_config:
            self.current_flow = schema.flow_config
            self.components.set_combo_box_current_text(
                self.ui.flowTypeComboBox, 
                schema.flow_config.flow_type.value
            )
            self.refresh_flow_steps()
        else:
            self.components.set_combo_box_current_text(self.ui.flowTypeComboBox, "Sequential")
            self.components.clear_list_widget(self.ui.flowStepsListWidget)
        
        # Update preview
        self.update_preview()
    
    def refresh_component_bricks(self):
        """Refresh component bricks list"""
        if not self.current_schema:
            self.components.clear_list_widget(self.ui.componentBricksListWidget)
            return
        
        try:
            library_name = self.components.get_combo_box_current_text(self.ui.brickLibraryComboBox)
            component_bricks = []
            
            for brick_id in self.current_schema.component_brick_ids:
                brick = self.brick_integration.get_brick_by_id(brick_id, library_name)
                if brick:
                    component_bricks.append(brick)
            
            self.components.set_list_widget_data(
                self.ui.componentBricksListWidget, 
                component_bricks, 
                'brick_id'
            )
            
        except Exception as e:
            print(f"Error loading component bricks: {e}")
            self.components.clear_list_widget(self.ui.componentBricksListWidget)
    
    def refresh_flow_steps(self):
        """Refresh flow steps list"""
        if not self.current_flow:
            return
        
        self.components.clear_list_widget(self.ui.flowStepsListWidget)
        
        for step in self.current_flow.steps:
            step_text = f"{step.name} ({len(step.brick_ids)} bricks)"
            self.ui.flowStepsListWidget.addItem(step_text)
    
    def update_preview(self):
        """Update schema preview"""
        if not self.current_schema:
            self.components.set_text_edit_text(self.ui.previewTextEdit, "")
            return
        
        preview_text = f"Schema: {self.current_schema.name}\n"
        preview_text += f"Description: {self.current_schema.description}\n"
        preview_text += f"Root Brick: {self.current_schema.root_brick_id}\n"
        preview_text += f"Component Bricks: {len(self.current_schema.component_brick_ids)}\n"
        
        if self.current_flow:
            preview_text += f"Flow Type: {self.current_flow.flow_type.value}\n"
            preview_text += f"Flow Steps: {len(self.current_flow.steps)}\n"
        
        self.components.set_text_edit_text(self.ui.previewTextEdit, preview_text)
    
    def save_schema(self):
        """Save current schema"""
        if not self.current_schema:
            return
        
        # Update schema from UI
        self.current_schema.name = self.components.get_line_edit_text(self.ui.nameLineEdit)
        self.current_schema.description = self.components.get_line_edit_text(self.ui.descriptionLineEdit)
        
        # Get root brick ID
        root_brick_id = self.ui.rootBrickComboBox.currentData()
        if root_brick_id and root_brick_id != "Select root brick...":
            self.current_schema.root_brick_id = root_brick_id
        
        # Update flow configuration
        if self.current_flow:
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
        
        # Save schema
        if self.schema_core.save_schema():
            self.refresh_schema_list()
            self.ui.statusbar.showMessage(f"Saved schema: {self.current_schema.name}")
        else:
            self.components.show_error_message(self, "Error", "Failed to save schema.")
    
    def delete_schema(self):
        """Delete selected schema"""
        schema_id = self.components.get_selected_list_data(self.ui.schemaListWidget)
        if not schema_id:
            return
        
        # Confirm deletion
        schema_name = self.components.get_selected_list_text(self.ui.schemaListWidget)
        if not self.components.ask_confirmation(
            self, "Confirm Delete", 
            f"Are you sure you want to delete schema '{schema_name}'?"
        ):
            return
        
        # Delete schema
        if self.schema_core.delete_schema(schema_id):
            self.refresh_schema_list()
            if self.current_schema and self.current_schema.schema_id == schema_id:
                self.current_schema = None
                self.set_ui_state(False)
            self.ui.statusbar.showMessage(f"Deleted schema: {schema_name}")
        else:
            self.components.show_error_message(self, "Error", "Failed to delete schema.")
    
    def add_brick_as_component(self):
        """Add double-clicked brick as component"""
        brick_id = self.components.get_selected_list_data(self.ui.brickListWidget)
        if not brick_id or not self.current_schema:
            return
        
        if self.schema_core.add_component_brick(brick_id):
            self.refresh_component_bricks()
            self.update_preview()
            self.ui.statusbar.showMessage("Added component brick")
    
    def add_component_brick(self):
        """Add selected brick as component"""
        brick_id = self.components.get_selected_list_data(self.ui.brickListWidget)
        if not brick_id or not self.current_schema:
            self.components.show_warning_message(self, "No Selection", "Please select a brick to add.")
            return
        
        if self.schema_core.add_component_brick(brick_id):
            self.refresh_component_bricks()
            self.update_preview()
            self.ui.statusbar.showMessage("Added component brick")
    
    def remove_component_brick(self):
        """Remove selected component brick"""
        brick_id = self.components.get_selected_list_data(self.ui.componentBricksListWidget)
        if not brick_id or not self.current_schema:
            return
        
        if self.schema_core.remove_component_brick(brick_id):
            self.refresh_component_bricks()
            self.update_preview()
            self.ui.statusbar.showMessage("Removed component brick")
    
    def edit_flow(self):
        """Edit flow configuration"""
        if not self.current_schema:
            self.components.show_warning_message(self, "No Schema", "No schema loaded to edit flow for.")
            return
        
        # Import here to avoid circular imports
        from .flow_editor_dialog import FlowEditorDialog
        
        dialog = FlowEditorDialog(
            self.flow_engine, 
            self.brick_integration,
            self.current_flow,
            self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.current_flow = dialog.get_flow_config()
            self.refresh_flow_steps()
            self.update_preview()
            self.ui.statusbar.showMessage("Flow configuration updated")
    
    def export_shacl(self):
        """Export schema as SHACL"""
        if not self.current_schema:
            return
        
        # Get save file name
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export SHACL", f"{self.current_schema.name}.ttl", 
            "Turtle Files (*.ttl);;All Files (*)"
        )
        
        if not file_name:
            return
        
        try:
            # Generate SHACL content
            shacl_lines = []
            
            # Prefixes
            shacl_lines.append("@prefix sh: <http://www.w3.org/ns/shacl#> .")
            shacl_lines.append("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .")
            shacl_lines.append("")
            
            library_name = self.components.get_combo_box_current_text(self.ui.brickLibraryComboBox)
            
            # Add root brick SHACL
            root_brick = self.brick_integration.get_brick_by_id(
                self.current_schema.root_brick_id, library_name
            )
            if root_brick:
                root_shacl = self.brick_integration.export_brick_as_shacl(
                    self.current_schema.root_brick_id, library_name
                )
                if root_shacl:
                    shacl_lines.append("# Root Brick")
                    shacl_lines.append(root_shacl)
                    shacl_lines.append("")
            
            # Add component bricks SHACL
            for brick_id in self.current_schema.component_brick_ids:
                component_shacl = self.brick_integration.export_brick_as_shacl(brick_id, library_name)
                if component_shacl:
                    shacl_lines.append(f"# Component Brick: {brick_id}")
                    shacl_lines.append(component_shacl)
                    shacl_lines.append("")
            
            shacl_content = "\n".join(shacl_lines)
            
            with open(file_name, 'w') as f:
                f.write(shacl_content)
            
            self.ui.statusbar.showMessage(f"Exported SHACL to: {file_name}")
            
        except Exception as e:
            self.components.show_error_message(self, "Export Error", f"Failed to export SHACL: {e}")
    
    def validate_schema(self):
        """Validate current schema and show results"""
        if not self.current_schema:
            self.components.show_warning_message(self, "No Schema", "No schema loaded to validate.")
            return
        
        # Basic validation
        issues = []
        
        if not self.current_schema.name.strip():
            issues.append("Schema name is required")
        
        if not self.current_schema.root_brick_id:
            issues.append("Root brick is required")
        
        # Check root brick exists
        if self.current_schema.root_brick_id:
            root_brick = self.brick_integration.get_brick_by_id(self.current_schema.root_brick_id)
            if not root_brick:
                issues.append("Root brick not found")
            elif root_brick.object_type != "NodeShape":
                issues.append("Root brick must be a NodeShape")
        
        # Check component bricks
        library_name = self.components.get_combo_box_current_text(self.ui.brickLibraryComboBox)
        for brick_id in self.current_schema.component_brick_ids:
            brick = self.brick_integration.get_brick_by_id(brick_id, library_name)
            if not brick:
                issues.append(f"Component brick not found: {brick_id}")
        
        # Check flow configuration
        if self.current_flow:
            flow_issues = self.flow_engine.validate_flow(self.current_flow.flow_id)
            issues.extend([f"Flow: {issue}" for issue in flow_issues])
        
        # Show validation result
        if issues:
            self.components.show_warning_message(
                self, "Validation Issues", 
                "Schema has validation issues:\n\n" + "\n".join(issues)
            )
        else:
            self.components.show_info_message(self, "Validation", "Schema is valid!")
    
    def manage_libraries(self):
        """Manage schema libraries"""
        library_name, ok = QInputDialog.getText(
            self, "Create Library", "Enter new library name:"
        )
        
        if ok and library_name.strip():
            if self.schema_core.create_library(library_name.strip()):
                self.refresh_schema_libraries()
                self.ui.statusbar.showMessage(f"Created library: {library_name}")
            else:
                self.components.show_error_message(self, "Error", "Failed to create library.")
    
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
