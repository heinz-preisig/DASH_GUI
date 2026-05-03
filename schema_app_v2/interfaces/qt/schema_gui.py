"""
Schema GUI Module - Minimal Working Version
Minimal PyQt interface that bypasses complex import issues
"""

import sys
import os
from typing import Optional, Dict, List, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QMessageBox, 
    QFileDialog, QInputDialog, QDialog, QListWidgetItem, QTreeWidgetItem
)
from PyQt6.QtCore import Qt

# Use absolute imports from schema_app_v2 package
from schema_app_v2.core.schema_core import SchemaCore, Schema
from schema_app_v2.core.flow_engine import FlowEngine, FlowType, FlowStep, FlowConfig
from schema_app_v2.core.brick_integration import BrickIntegration
from schema_app_v2.core.schema_helper import SchemaHelper
from schema_app_v2.core.multi_tenant_backend import MultiTenantBackend
from schema_app_v2.core.abstract_events import EventType

from .ui_components import UiLoader, ComponentManager
from .add_component_dialog import AddComponentDialog
from .daisy_chain_editor_dialog import DaisyChainEditorDialog
from .ui_state_manager import UIStateManager, SchemaState


class SchemaGUI(QMainWindow):
    """Main schema construction GUI with multi-tenant backend support"""
    
    def __init__(self, schema_repository_path: str = None,
                 brick_repository_path: str = None):
        super().__init__()
        
        # Initialize multi-tenant backend
        self.backend = MultiTenantBackend(schema_repository_path, brick_repository_path)
        self.qt_session = self.backend.get_qt_session()
        
        # Get core components from session
        self.schema_core = self.qt_session.schema_core
        self.flow_engine = self.qt_session.flow_engine
        self.brick_integration = self.qt_session.brick_integration
        
        # Initialize helper for user-friendly features
        self.helper = SchemaHelper()
        
        # Load UI from .ui file
        self.ui_loader = UiLoader()
        self.ui = self.ui_loader.load_main_window()
        self.setCentralWidget(self.ui)
        
        # Component manager for UI interactions
        self.components = ComponentManager()
        
        # Initialize state manager
        self.state_manager = UIStateManager()
        
        # Current state
        self.current_schema: Optional[Schema] = self.qt_session.current_schema
        self.current_flow: Optional[FlowConfig] = None
        
        # Setup UI
        self.setup_ui()
        self.connect_signals()
        self.register_widgets_with_state_manager()
        self.connect_state_signals()
        self.load_initial_data()
        
        # Set initial state
        self.state_manager.set_state(SchemaState.INITIAL)
        
        # Register Qt signals for event handling
        self._setup_event_handlers()
        
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
        self.ui.validateSchemaAction.triggered.connect(self.validate_schema)
        
        # Schema menu - add advanced features
        daisy_chain_action = self.ui.toolsMenu.addAction("Create Daisy Chain")
        daisy_chain_action.triggered.connect(self.create_daisy_chain)
        
        extend_schema_action = self.ui.toolsMenu.addAction("Extend Schema")
        extend_schema_action.triggered.connect(self.extend_schema)
        
        # Help menu
        self.ui.helpMenu.addSeparator()
        help_guide_action = self.ui.helpMenu.addAction("Schema Guide")
        help_guide_action.triggered.connect(self.show_schema_guide)
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
        self.ui.brickListWidget.itemSelectionChanged.connect(self.on_brick_selection_changed)
        
        # Schema details (only connect when schema exists)
        # Note: These will be connected when schema is created/selected
        
        # Component management
        self.ui.addComponentButton.clicked.connect(self.add_component_brick)
        self.ui.removeComponentButton.clicked.connect(self.remove_component_brick)
        self.ui.componentBricksListWidget.itemSelectionChanged.connect(self.on_component_selection_changed)
        self.ui.componentBricksListWidget.itemDoubleClicked.connect(self.open_ui_metadata_editor)
        
        # Tree widget double-click
        if hasattr(self.ui, 'componentTreeWidget'):
            self.ui.componentTreeWidget.itemDoubleClicked.connect(self.open_ui_metadata_editor_tree)
        
        # View toggle
        self.ui.listViewRadio.toggled.connect(self.on_component_view_changed)
        self.ui.treeViewRadio.toggled.connect(self.on_component_view_changed)
        
        # Flow management
        self.ui.flowTypeComboBox.currentTextChanged.connect(self.on_flow_type_changed)
        self.ui.editFlowButton.clicked.connect(self.edit_flow)
        self.ui.flowStepsListWidget.itemSelectionChanged.connect(self.on_flow_step_selection_changed)
        
        # Action buttons
        self.ui.saveButton.clicked.connect(self.save_schema)
        self.ui.exportShaclButton.clicked.connect(self.export_shacl)
    
    def register_widgets_with_state_manager(self):
        """Register UI widgets with state manager"""
        # Register all widgets that need state management
        self.state_manager.register_widget("libraryComboBox", self.ui.libraryComboBox)
        self.state_manager.register_widget("brickLibraryComboBox", self.ui.brickLibraryComboBox)
        self.state_manager.register_widget("schemaListWidget", self.ui.schemaListWidget)
        self.state_manager.register_widget("newSchemaButton", self.ui.newSchemaButton)
        self.state_manager.register_widget("deleteSchemaButton", self.ui.deleteSchemaButton)
        self.state_manager.register_widget("nameLineEdit", self.ui.nameLineEdit)
        self.state_manager.register_widget("descriptionLineEdit", self.ui.descriptionLineEdit)
        self.state_manager.register_widget("rootBrickComboBox", self.ui.rootBrickComboBox)
        self.state_manager.register_widget("addComponentButton", self.ui.addComponentButton)
        self.state_manager.register_widget("removeComponentButton", self.ui.removeComponentButton)
        self.state_manager.register_widget("componentBricksListWidget", self.ui.componentBricksListWidget)
        self.state_manager.register_widget("flowTypeComboBox", self.ui.flowTypeComboBox)
        self.state_manager.register_widget("editFlowButton", self.ui.editFlowButton)
        self.state_manager.register_widget("saveButton", self.ui.saveButton)
        self.state_manager.register_widget("exportShaclButton", self.ui.exportShaclButton)
        self.state_manager.register_widget("brickListWidget", self.ui.brickListWidget)
        self.state_manager.register_widget("brickSearchLineEdit", self.ui.brickSearchLineEdit)
        self.state_manager.register_widget("bricksGroupBox", self.ui.bricksGroupBox)
        self.state_manager.register_widget("schemaDetailsGroupBox", self.ui.schemaDetailsGroupBox)
        self.state_manager.register_widget("flowStepsListWidget", self.ui.flowStepsListWidget)
        self.state_manager.register_widget("previewTextEdit", self.ui.previewTextEdit)
    
    def connect_state_signals(self):
        """Connect state manager signals to handlers"""
        self.state_manager.state_changed.connect(self.on_state_changed)
        self.state_manager.schema_modified.connect(self.on_schema_modified)
        self.state_manager.schema_saved.connect(self.on_schema_saved)
        self.state_manager.schema_selected.connect(self.on_schema_selected)
        self.state_manager.schema_deselected.connect(self.on_schema_deselected)
    
    def on_state_changed(self, old_state: SchemaState, new_state: SchemaState):
        """Handle state changes"""
        # Could add additional logic here if needed
        pass
    
    def on_schema_modified(self):
        """Handle schema modification"""
        pass  # Can add specific logic if needed
    
    def on_schema_saved(self):
        """Handle schema saved"""
        pass  # Can add specific logic if needed
    
    def on_schema_selected(self, schema):
        """Handle schema selected"""
        pass  # Can add specific logic if needed
    
    def on_schema_deselected(self):
        """Handle schema deselected"""
        # Clear preview when deselected
        self.ui.previewTextEdit.clear()
    
    def _setup_event_handlers(self):
        """Setup Qt signal handlers for backend events"""
        # Register Qt signals with backend event manager
        # This allows the backend to emit events that trigger UI updates
        pass  # Can be expanded later for real-time updates
    
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
        
        # Create new schema using backend
        schema = self.schema_core.create_schema(name.strip())
        self.current_schema = schema
        self.qt_session.current_schema = schema  # Sync with backend session
        
        # Save to disk so it appears in the list
        self.schema_core.save_schema(schema)
        
        # Emit event
        self.qt_session._emit_event('schema_created', schema.to_dict())
        
        # Update UI
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
        
        # Find and load the schema
        for schema in schemas:
            if schema.name == name:
                self.current_schema = schema
                self.qt_session.current_schema = schema  # Sync with backend session
                self.qt_session._emit_event('schema_loaded', schema.to_dict())
                self.load_schema_into_ui(schema)
                self.state_manager.set_current_schema(schema, has_unsaved_changes=False)
                self.ui.statusbar.showMessage(f"Opened schema: {name}")
                break
    
    def save_schema(self):
        """Save current schema"""
        if not self.current_schema:
            return
        
        try:
            self.state_manager.start_saving()
            self.schema_core.save_schema(self.current_schema)
            self.qt_session._emit_event('schema_saved', self.current_schema.to_dict())
            self.state_manager.mark_schema_saved()
            self.ui.statusbar.showMessage(f"Saved schema: {self.current_schema.name}")
        except Exception as e:
            self.qt_session._emit_event('error_occurred', {"message": f"Failed to save schema: {e}"})
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
            exporter = SHACLExporter(self.brick_integration)
            exporter.export_schema(self.current_schema, file_path)
            self.ui.statusbar.showMessage(f"Exported SHACL to: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export SHACL: {e}")
    
        """Manage libraries dialog"""
        QMessageBox.information(self, "Library Management", "Library management feature coming soon.")
    
    def create_daisy_chain(self):
        """Create daisy chain of schemas"""
        # Get all available schemas
        schemas = self.schema_core.get_all_schemas()
        
        if len(schemas) < 2:
            QMessageBox.warning(self, "Insufficient Schemas", 
                "You need at least 2 schemas to create a daisy chain.")
            return
        
        # Open daisy chain editor dialog
        dialog = DaisyChainEditorDialog(
            self.schema_core,
            schemas,
            self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            chain_data = dialog.get_chain_data()
            
            # Create daisy chain using backend
            daisy_chain = self.schema_core.create_daisy_chain(
                chain_data['name'],
                chain_data['description'],
                chain_data['schema_ids'],
                chain_data['navigation_rules']
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
            QMessageBox.warning(self, "No Schema", 
                "Please create or select a schema to extend first.")
            return
        
        # Get all schemas except current one
        all_schemas = self.schema_core.get_all_schemas()
        parent_schemas = [s for s in all_schemas if s.schema_id != self.current_schema.schema_id]
        
        if not parent_schemas:
            QMessageBox.warning(self, "No Parent Schemas", 
                "No other schemas available to extend from.")
            return
        
        # Let user select parent schema
        schema_names = [s.name for s in parent_schemas]
        parent_name, ok = QInputDialog.getItem(
            self, "Select Parent Schema",
            "Select the schema to extend:",
            schema_names, 0, False
        )
        
        if not ok or not parent_name:
            return
        
        # Find parent schema
        parent_schema = next((s for s in parent_schemas if s.name == parent_name), None)
        if not parent_schema:
            return
        
        # Get additional bricks
        additional_bricks, ok = QInputDialog.getText(
            self, "Additional Bricks",
            "Enter additional brick IDs (comma-separated):"
        )
        
        if not ok:
            return
        
        brick_ids = [b.strip() for b in additional_bricks.split(',') if b.strip()] if additional_bricks else []
        
        # Get new schema name
        new_name, ok = QInputDialog.getText(
            self, "Extended Schema Name",
            "Enter name for the extended schema:",
            text=f"{self.current_schema.name}_extended"
        )
        
        if not ok or not new_name.strip():
            return
        
        # Extend schema using backend
        extended_schema = self.schema_core.extend_schema(
            parent_schema.schema_id,
            new_name.strip(),
            f"Extended from {parent_schema.name}",
            brick_ids,
            self.brick_integration
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
                schema_id = self.current_schema.schema_id
                schema_name = self.current_schema.name
                self.current_schema = None
                self.state_manager.set_current_schema(None, has_unsaved_changes=False)
                
                # Clear UI first
                self.ui.schemaListWidget.clear()
                self.ui.nameLineEdit.clear()
                self.ui.descriptionLineEdit.clear()
                self.ui.componentBricksListWidget.clear()
                self.ui.previewTextEdit.clear()
                
                # Delete from backend
                if self.schema_core.delete_schema(schema_id):
                    # Refresh list after deletion
                    self.refresh_schema_list()
                    self.ui.statusbar.showMessage(f"Deleted schema: {schema_name}")
                else:
                    QMessageBox.warning(self, "Delete Warning", "Schema file may not have been deleted")
            except Exception as e:
                QMessageBox.critical(self, "Delete Error", f"Failed to delete schema: {e}")
    
    def show_schema_guide(self):
        """Show schema construction guide"""
        guide_text = """
<h3>Schema Construction Guide</h3>

<p><b>Step 1: Create a Schema</b></p>
<ol>
<li>Click "New Schema" button or File → New Schema</li>
<li>Enter a name for your schema (required)</li>
<li>Add a description (optional)</li>
<li>Click OK to create the schema</li>
</ol>

<p><b>Step 2: Select Root Brick</b></p>
<ol>
<li>Choose a NodeShape brick from the "Root Brick" dropdown</li>
<li>The root brick defines the main entity of your schema (e.g., Person, Organization)</li>
<li>This is the foundation that all other components relate to</li>
</ol>

<p><b>Step 3: Add Component Bricks</b></p>
<ol>
<li>Browse PropertyShape bricks in the brick list (center panel)</li>
<li>Double-click a brick to add it as a component</li>
<li>Components appear in the "Components" list</li>
<li>Add all relevant properties for your schema</li>
</ol>

<p><b>Step 4: Configure Flow (Optional)</b></p>
<ol>
<li>Select a flow type from the dropdown:
  <ul>
  <li><b>Sequential:</b> Steps in order (1 → 2 → 3)</li>
  <li><b>Conditional:</b> Next step depends on conditions</li>
  <li><b>Parallel:</b> Multiple steps at once</li>
  <li><b>Dynamic:</b> Steps added/removed at runtime</li>
  </ul>
</li>
<li>Click "Edit Flow" to configure steps</li>
<li>Add steps and assign bricks to each step</li>
<li>Configure navigation between steps</li>
</ol>

<p><b>Step 5: Save and Export</b></p>
<ol>
<li>Click "Save" to save your schema</li>
<li>Click "Export SHACL" to generate a SHACL file</li>
<li>The SHACL file can be used for validation</li>
</ol>

<p><b>Tips:</b></p>
<ul>
<li>Use the preview panel to review your schema</li>
<li>Components shown in preview are by brick name, not ID</li>
<li>Save frequently to avoid losing work</li>
<li>Use the Help button in the flow editor for detailed flow configuration help</li>
</ul>
"""
        QMessageBox.information(self, "Schema Construction Guide", guide_text)
    
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
                    self.qt_session.current_schema = schema  # Sync with backend session
                    self.qt_session._emit_event('schema_loaded', schema.to_dict())
                    self.load_schema_into_ui(schema)
                    self.state_manager.set_current_schema(schema, has_unsaved_changes=False)
                    
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
            brick_id = bricks[0].brick_id
            if brick_id not in self.current_schema.component_brick_ids:
                self.current_schema.component_brick_ids.append(brick_id)
                self.current_schema.update_timestamp()
                self.qt_session._emit_event('component_added', {"brick_id": brick_id})
                self.refresh_component_list()
                self.ui.statusbar.showMessage(f"Added component: {brick_name}")
    
    def on_brick_selection_changed(self):
        """Handle brick selection change - show brick details"""
        current_item = self.ui.brickListWidget.currentItem()
        if not current_item:
            self.ui.brickDetailsTextEdit.clear()
            return
        
        brick_name = current_item.text()
        # Find brick by name since get_brick_by_name doesn't exist
        all_bricks = self.brick_integration.get_available_bricks()
        brick = next((b for b in all_bricks if b.name == brick_name), None)
        
        if brick:
            details = f"<b>Name:</b> {brick.name}<br>"
            details += f"<b>Type:</b> {brick.object_type}<br>"
            details += f"<b>ID:</b> {brick.brick_id}<br>"
            
            if hasattr(brick, 'description') and brick.description:
                details += f"<b>Description:</b> {brick.description}<br>"
            
            if hasattr(brick, 'target_class') and brick.target_class:
                details += f"<b>Target Class:</b> {brick.target_class}<br>"
            
            if hasattr(brick, 'properties') and brick.properties:
                details += f"<b>Properties ({len(brick.properties)}):</b><br>"
                for prop_name, prop_value in brick.properties.items():
                    details += f"  • {prop_name}: {prop_value}<br>"
            
            if hasattr(brick, 'constraints') and brick.constraints:
                details += f"<b>Constraints ({len(brick.constraints)}):</b><br>"
                for constraint in brick.constraints:
                    details += f"  • {constraint}<br>"
            
            self.ui.brickDetailsTextEdit.setText(details)
        else:
            self.ui.brickDetailsTextEdit.setText("Brick details not available")
    
    def on_schema_details_changed(self):
        """Handle schema detail changes"""
        if self.current_schema:
            self.current_schema.name = self.ui.nameLineEdit.text()
            self.current_schema.description = self.ui.descriptionLineEdit.text()
            self.current_schema.update_timestamp()
            self.qt_session._emit_event('schema_updated', self.current_schema.to_dict())
            self.update_preview()
    
    def on_root_brick_changed(self, brick_name):
        """Handle root brick change"""
        if self.current_schema and brick_name:
            all_bricks = self.brick_integration.get_available_bricks()
            bricks = [brick for brick in all_bricks if brick.name == brick_name]
            if bricks:
                self.current_schema.root_brick_id = bricks[0].brick_id
                self.current_schema.update_timestamp()
                self.qt_session._emit_event('root_brick_set', {"brick_id": bricks[0].brick_id})
                self.state_manager.mark_schema_modified()
                self.update_preview()
    
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
                    if selected_brick_id not in self.current_schema.component_brick_ids:
                        self.current_schema.component_brick_ids.append(selected_brick_id)
                        self.current_schema.update_timestamp()
                        self.qt_session._emit_event('component_added', {"brick_id": selected_brick_id})
                    
                    # Update UI
                    self.refresh_component_list()
                    self.update_preview()
                    QMessageBox.information(self, "Success", 
                        f"Component '{selected_brick_id}' added to schema successfully!")
                except Exception as e:
                    self.qt_session._emit_event('error_occurred', {"message": f"Failed to add component: {str(e)}"})
                    QMessageBox.critical(self, "Error", f"Failed to add component: {str(e)}")
    
    def remove_component_brick(self):
        """Remove component brick button handler"""
        items = self.ui.componentBricksListWidget.selectedItems()
        if not items:
            QMessageBox.warning(self, "No Selection", "Please select a component to remove")
            return
        
        if not self.current_schema:
            return
        
        component_name = items[0].text()
        all_bricks = self.brick_integration.get_available_bricks()
        bricks = [brick for brick in all_bricks if brick.name == component_name]
        
        if bricks:
            brick_id = bricks[0].brick_id
            if brick_id in self.current_schema.component_brick_ids:
                self.current_schema.component_brick_ids.remove(brick_id)
                self.current_schema.update_timestamp()
                self.qt_session._emit_event('component_removed', {"brick_id": brick_id})
                self.state_manager.mark_schema_modified()
                self.refresh_component_list()
                self.update_preview()
                self.ui.statusbar.showMessage(f"Removed component: {component_name}")
    
    def on_component_view_changed(self):
        """Handle component view toggle between list and tree"""
        if self.ui.listViewRadio.isChecked():
            self.ui.componentViewStack.setCurrentIndex(0)
        else:
            self.ui.componentViewStack.setCurrentIndex(1)
            self.refresh_component_tree()
    
    def refresh_component_tree(self):
        """Refresh the component tree view with parent-child relationships"""
        self.ui.componentTreeWidget.clear()
        
        if not self.current_schema:
            return
        
        # Get root components (components with no parent)
        root_brick_ids = self.current_schema.get_root_components()
        
        # Add root brick as the tree root
        if self.current_schema.root_brick_id:
            root_brick = self.brick_integration.get_brick_by_id(self.current_schema.root_brick_id)
            if root_brick:
                root_item = QTreeWidgetItem(self.ui.componentTreeWidget)
                root_item.setText(0, f"Root: {root_brick.name}")
                root_item.setData(0, Qt.ItemDataRole.UserRole, self.current_schema.root_brick_id)
                
                # Add children recursively
                self._add_tree_children(root_item, self.current_schema.root_brick_id)
        
        # Add top-level components (components with no parent)
        for brick_id in root_brick_ids:
            brick = self.brick_integration.get_brick_by_id(brick_id)
            if brick:
                item = QTreeWidgetItem(self.ui.componentTreeWidget)
                item.setText(0, brick.name)
                item.setData(0, Qt.ItemDataRole.UserRole, brick_id)
                
                # Add children recursively
                self._add_tree_children(item, brick_id)
    
    def _add_tree_children(self, parent_item: QTreeWidgetItem, parent_brick_id: str):
        """Recursively add children to a tree item"""
        if not self.current_schema:
            return
        
        children = self.current_schema.get_children(parent_brick_id)
        for child_id in children:
            child_brick = self.brick_integration.get_brick_by_id(child_id)
            if child_brick:
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, child_brick.name)
                child_item.setData(0, Qt.ItemDataRole.UserRole, child_id)
                
                # Recursively add grandchildren
                self._add_tree_children(child_item, child_id)
    
    def on_component_selection_changed(self):
        """Handle component selection change"""
        pass
    
    def open_ui_metadata_editor(self, item):
        """Open UI metadata editor for double-clicked component in list view"""
        if not self.current_schema:
            QMessageBox.warning(self, "No Schema", "Please create or select a schema first")
            return
        
        brick_id = item.text()
        self._open_ui_metadata_dialog(brick_id)
    
    def open_ui_metadata_editor_tree(self, item, column):
        """Open UI metadata editor for double-clicked component in tree view"""
        if not self.current_schema:
            QMessageBox.warning(self, "No Schema", "Please create or select a schema first")
            return
        
        brick_id = item.text(0)
        self._open_ui_metadata_dialog(brick_id)
    
    def _open_ui_metadata_dialog(self, brick_id: str):
        """Open UI metadata dialog for a component"""
        if brick_id not in self.current_schema.component_brick_ids:
            QMessageBox.warning(self, "Invalid Component", f"Component '{brick_id}' not found in schema")
            return
        
        dialog = UIMetadataPanelDialog(self.current_schema, brick_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Save schema after metadata update
            self.qt_session.schema_core.save_schema(self.current_schema)
            self.qt_session._emit_event('schema_updated', self.current_schema.to_dict())
            self.refresh_component_list()
    
    def on_flow_type_changed(self, flow_type):
        """Handle flow type change"""
        if self.current_schema and flow_type:
            try:
                flow_enum = FlowType(flow_type)
                self.current_schema.flow_config = self.flow_engine.create_flow(
                    f"Flow for {self.current_schema.name}", flow_enum
                )
                self.current_schema.update_timestamp()
                self.qt_session._emit_event('flow_updated', self.current_schema.flow_config.to_dict())
                self.state_manager.mark_schema_modified()
                self.refresh_flow_steps()
            except ValueError:
                pass
    
    def edit_flow(self):
        """Edit flow button handler"""
        if not self.current_schema:
            QMessageBox.warning(self, "No Schema", "Please create or select a schema first")
            return
        
        # Import flow editor dialog
        from .flow_editor_dialog import FlowEditorDialog
        
        dialog = FlowEditorDialog(
            self.flow_engine, 
            self.brick_integration, 
            self.current_schema.flow_config,
            self,
            self.current_schema
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.current_schema.flow_config = dialog.current_flow
            self.current_schema.update_timestamp()
            self.qt_session._emit_event('flow_updated', self.current_schema.flow_config.to_dict())
            self.refresh_flow_steps()
            self.update_preview()
            self.ui.statusbar.showMessage("Flow updated successfully")
    
    def refresh_schema_libraries(self):
        """Refresh schema library list"""
        try:
            libraries = self.schema_core.get_libraries()
            self.ui.libraryComboBox.clear()
            self.ui.libraryComboBox.addItems(libraries)
            if libraries:
                self.ui.libraryComboBox.setCurrentIndex(0)
        except Exception as e:
            print(f"Error loading schema libraries: {e}")
    
    def refresh_brick_libraries(self):
        """Refresh brick library list"""
        try:
            libraries = self.brick_integration.get_brick_libraries()
            self.ui.brickLibraryComboBox.clear()
            self.ui.brickLibraryComboBox.addItems(libraries)
            if libraries:
                self.ui.brickLibraryComboBox.setCurrentIndex(0)
        except Exception as e:
            print(f"Error loading brick libraries: {e}")
    
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
        
        # Load flow steps
        self.refresh_flow_steps()
        
        # Update preview
        self.update_preview()
    
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
        self.state_manager.set_current_schema(schema, has_unsaved_changes=False)
        
        self.ui.statusbar.showMessage(f"Created schema from template: {template.name}")

    def on_flow_step_selection_changed(self):
        """Handle flow step selection change"""
        # Could show step details here
        pass
    
    def refresh_flow_steps(self):
        """Refresh flow steps list widget"""
        self.ui.flowStepsListWidget.clear()
        
        if self.current_schema and self.current_schema.flow_config:
            flow = self.current_schema.flow_config
            for step in flow.steps:
                step_text = f"{step.name} ({len(step.brick_ids)} bricks)"
                self.ui.flowStepsListWidget.addItem(step_text)
    
    def update_preview(self):
        """Update schema preview"""
        if not self.current_schema:
            self.ui.previewTextEdit.clear()
            return
        
        # Get root brick name
        root_brick_name = "Not set"
        if self.current_schema.root_brick_id:
            root_brick = self.brick_integration.get_brick_by_id(self.current_schema.root_brick_id)
            if root_brick:
                root_brick_name = root_brick.name
        
        preview_text = f"""Schema Preview
{'=' * 50}

Name: {self.current_schema.name}
Description: {self.current_schema.description or 'No description'}
Root Brick: {root_brick_name}

Components ({len(self.current_schema.component_brick_ids)}):
"""
        for brick_id in self.current_schema.component_brick_ids:
            brick = self.brick_integration.get_brick_by_id(brick_id)
            brick_name = brick.name if brick else brick_id
            preview_text += f"  - {brick_name}\n"
        
        # Add inheritance chain if present
        if self.current_schema.inheritance_chain:
            preview_text += f"\nInherits from: {len(self.current_schema.inheritance_chain)} schemas\n"
            for parent_id in self.current_schema.inheritance_chain:
                preview_text += f"  - {parent_id}\n"
        
        # Add relationships if present
        if self.current_schema.relationships:
            preview_text += f"\nBrick Relationships:\n"
            for brick_id, relations in self.current_schema.relationships.items():
                preview_text += f"  - {brick_id}: {relations}\n"
        
        # Add flow info if present
        if self.current_schema.flow_config:
            flow = self.current_schema.flow_config
            preview_text += f"""
Flow Configuration:
  Type: {flow.flow_type.value}
  Steps: {len(flow.steps)}
"""
            for i, step in enumerate(flow.steps, 1):
                preview_text += f"  {i}. {step.name} ({len(step.brick_ids)} bricks)\n"
        
        self.ui.previewTextEdit.setPlainText(preview_text)

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
