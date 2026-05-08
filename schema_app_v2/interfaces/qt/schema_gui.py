"""
Schema GUI Module
Main window — wiring only. All logic lives in the mixins package.
"""

import os
from typing import Optional
from PyQt6.QtWidgets import QMainWindow, QButtonGroup
from PyQt6.QtCore import Qt

from schema_app_v2.core.schema_core import Schema
from schema_app_v2.core.flow_engine import FlowEngine, FlowConfig
from schema_app_v2.core.multi_tenant_backend import MultiTenantBackend
from schema_app_v2.core.schema_helper import SchemaHelper

from .ui_components import UiLoader, ComponentManager
from .ui_state_manager import UIStateManager, SchemaState
from .mixins import (
    SchemaManagementMixin,
    ComponentTreeMixin,
    ComponentListMixin,
    BrickPanelMixin,
    FlowManagementMixin,
)


class SchemaGUI(
    QMainWindow,
    SchemaManagementMixin,
    ComponentTreeMixin,
    ComponentListMixin,
    BrickPanelMixin,
    FlowManagementMixin,
):
    """Main schema construction GUI — logic delegated to mixins."""

    def __init__(self, schema_repository_path: str = None,
                 brick_repository_path: str = None):
        super().__init__()

        self.backend = MultiTenantBackend(schema_repository_path, brick_repository_path)
        self.qt_session = self.backend.get_qt_session()

        self.schema_core = self.qt_session.schema_core
        self.flow_engine = self.qt_session.flow_engine
        self.brick_integration = self.qt_session.brick_integration

        self.helper = SchemaHelper()

        self.ui_loader = UiLoader()
        self.ui = self.ui_loader.load_main_window()
        self.setCentralWidget(self.ui)

        self.components = ComponentManager()
        self.state_manager = UIStateManager()

        self.current_schema: Optional[Schema] = self.qt_session.current_schema
        self.current_flow: Optional[FlowConfig] = None

        self.setup_ui()
        self.connect_signals()
        self.register_widgets_with_state_manager()
        self.connect_state_signals()
        self.load_initial_data()

        self.state_manager.set_state(SchemaState.INITIAL)
        self._setup_event_handlers()

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
        self.ui.newLibraryButton.clicked.connect(self.new_library)
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
        self.ui.addSchemaRefButton.clicked.connect(self.add_schema_reference)
        self.ui.removeComponentButton.clicked.connect(self.remove_component_brick)
        self.ui.componentBricksListWidget.itemSelectionChanged.connect(self.on_component_selection_changed)
        self.ui.componentBricksListWidget.itemDoubleClicked.connect(self.open_ui_metadata_editor)
        self.ui.componentBricksListWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.componentBricksListWidget.customContextMenuRequested.connect(self.on_list_context_menu)
        
        # Tree widget double-click and context menu
        if hasattr(self.ui, 'componentTreeWidget'):
            self.ui.componentTreeWidget.itemDoubleClicked.connect(self.open_ui_metadata_editor_tree)
            self.ui.componentTreeWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.ui.componentTreeWidget.customContextMenuRequested.connect(self.on_tree_context_menu)
        
        # View toggle — group radios so they are mutually exclusive, then
        # drive the stack from treeViewRadio alone (toggled carries the bool)
        self._view_toggle_group = QButtonGroup(self)
        self._view_toggle_group.addButton(self.ui.listViewRadio)
        self._view_toggle_group.addButton(self.ui.treeViewRadio)
        self.ui.treeViewRadio.toggled.connect(self.on_component_view_changed)
        
        # Flow management
        self.ui.flowTypeComboBox.currentTextChanged.connect(self.on_flow_type_changed)
        self.ui.editFlowButton.clicked.connect(self.edit_flow)
        self.ui.flowStepsListWidget.itemSelectionChanged.connect(self.on_flow_step_selection_changed)
        
        # Action buttons
        self.ui.saveButton.clicked.connect(self.save_schema)
        self.ui.exportShaclButton.clicked.connect(self.save_schema)
        self.ui.generateWebFormButton.clicked.connect(self.generate_web_form)
    
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
        self.state_manager.register_widget("addSchemaRefButton", self.ui.addSchemaRefButton)
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
    
    def closeEvent(self, event):
        """Handle application close"""
        if (self.current_schema and
                self.state_manager.get_current_state() == SchemaState.SCHEMA_MODIFIED):
            reply = self.components.ask_confirmation(
                self, "Unsaved Changes",
                "You have unsaved changes. Do you want to save before exiting?"
            )
            if reply:
                self.save_schema()
        event.accept()

