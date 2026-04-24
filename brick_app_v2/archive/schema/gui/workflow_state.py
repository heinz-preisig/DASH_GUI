#!/usr/bin/env python3
"""
Workflow State Machine for Brick Creation
Controls interface elements based on current state and prerequisites
Based on OntoBuild_v1 BricksAutomaton pattern
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget

class WorkflowState(Enum):
    """States in the brick creation workflow"""
    INITIALIZED = "start"                         # Application started
    LIBRARIES_LOADED = "libraries_loaded"        # Libraries checked and loaded
    ACTIVE_LIBRARY_SET = "active_library_set"    # At least one active library exists
    BRICK_EDITING = "brick_editing"              # Brick editor is open
    BRICK_VALID = "brick_valid"                  # Brick data is valid
    READY_TO_SAVE = "ready_to_save"              # Ready to save brick
    BRICK_SAVED = "brick_saved"                  # Brick successfully saved

# OntoBuild_v1 style UI state definition
UI_STATE = {
    "start": {
        "show": [
            "exit",
            "library_manager_create",
            "library_manager_load",
        ],
        "except": [
            "library_manager_set_active",
            "library_manager_delete",
        ],
        "action": ["InitializeApplication"],
    },
    "libraries_loaded": {
        "show": [
            "exit",
            "library_manager_create",
            "library_manager_list",
            "library_manager_set_active",
        ],
        "except": [
            "library_manager_delete",
        ],
        "action": ["LibrariesLoaded", "UpdateLibraryUI"],
    },
    "active_library_set": {
        "show": [
            "exit",
            "library_manager_create",
            "library_manager_list",
            "library_manager_delete",
            "brick_create",
            "brick_create_person",
            "brick_create_address",
            "schema_create",
        ],
        "except": [],
        "action": ["ActiveLibrarySet", "EnableBrickCreation"],
    },
    "brick_editing": {
        "show": [
            "exit",
            "brick_editor_save",
            "brick_editor_cancel",
            "brick_editor_add_property",
            "brick_editor_remove_property",
            "brick_editor_help",
        ],
        "except": [
            "brick_create",
            "brick_create_person", 
            "brick_create_address",
            "library_manager_delete",
        ],
        "action": ["BrickEditingStarted", "DisableOtherOperations"],
    },
    "brick_valid": {
        "show": [
            "exit",
            "brick_editor_save",
            "brick_editor_cancel",
            "brick_editor_add_property",
            "brick_editor_remove_property",
            "brick_editor_help",
            "brick_editor_select_library",
        ],
        "except": [
            "brick_create",
            "brick_create_person",
            "brick_create_address",
        ],
        "action": ["BrickValidated", "EnableSaveButton"],
    },
    "ready_to_save": {
        "show": [
            "exit",
            "brick_editor_save",
            "brick_editor_cancel",
            "brick_editor_select_library",
        ],
        "except": [
            "brick_create",
            "brick_create_person",
            "brick_create_address",
            "brick_editor_add_property",
        ],
        "action": ["ReadyToSave", "PrepareSaveDialog"],
    },
    "brick_saved": {
        "show": [
            "exit",
            "library_manager_create",
            "library_manager_list",
            "brick_create",
            "brick_create_person",
            "brick_create_address",
            "schema_create",
        ],
        "except": [],
        "action": ["BrickSaved", "RefreshLibraryList", "ResetForNewBrick"],
    },
}

class WorkflowController(QObject):
    """State machine that controls interface based on workflow state"""
    
    state_changed = pyqtSignal(str, str)  # old_state, new_state
    interface_update_requested = pyqtSignal()  # Request UI update
    action_triggered = pyqtSignal(str)  # Action name
    
    def __init__(self):
        super().__init__()
        self.current_state = WorkflowState.INITIALIZED
        self.state_history = []
        self.registered_widgets = {}  # widget_id -> widget
        self.widget_visibility = {}   # widget_id -> visibility state
        
    def get_state_config(self, state: WorkflowState) -> Dict:
        """Get state configuration from UI_STATE"""
        state_name = state.value
        return UI_STATE.get(state_name, {"show": [], "except": [], "action": []})
    
    def get_visible_widgets(self, state: WorkflowState) -> List[str]:
        """Get list of widgets that should be visible in given state"""
        config = self.get_state_config(state)
        return config["show"]
    
    def get_hidden_widgets(self, state: WorkflowState) -> List[str]:
        """Get list of widgets that should be hidden in given state"""
        config = self.get_state_config(state)
        return config["except"]
    
    def get_state_actions(self, state: WorkflowState) -> List[str]:
        """Get list of actions to trigger for given state"""
        config = self.get_state_config(state)
        return config["action"]
    
    def can_transition_to(self, target_state: WorkflowState) -> bool:
        """Check if transition to target state is allowed"""
        if target_state == self.current_state:
            return True
        
        # Define valid transitions based on workflow logic
        valid_transitions = {
            WorkflowState.INITIALIZED: [WorkflowState.LIBRARIES_LOADED],
            WorkflowState.LIBRARIES_LOADED: [WorkflowState.ACTIVE_LIBRARY_SET, WorkflowState.INITIALIZED],
            WorkflowState.ACTIVE_LIBRARY_SET: [WorkflowState.BRICK_EDITING, WorkflowState.LIBRARIES_LOADED],
            WorkflowState.BRICK_EDITING: [WorkflowState.BRICK_VALID, WorkflowState.ACTIVE_LIBRARY_SET],
            WorkflowState.BRICK_VALID: [WorkflowState.READY_TO_SAVE, WorkflowState.BRICK_EDITING],
            WorkflowState.READY_TO_SAVE: [WorkflowState.BRICK_SAVED, WorkflowState.BRICK_VALID],
            WorkflowState.BRICK_SAVED: [WorkflowState.ACTIVE_LIBRARY_SET]
        }
        
        allowed_states = valid_transitions.get(self.current_state, [])
        
        # Special case: can always go back to earlier states
        if self._is_earlier_state(target_state):
            return True
        
        return target_state in allowed_states
    
    def _is_earlier_state(self, state: WorkflowState) -> bool:
        """Check if a state is earlier in the workflow"""
        state_order = [
            WorkflowState.INITIALIZED,
            WorkflowState.LIBRARIES_LOADED,
            WorkflowState.ACTIVE_LIBRARY_SET,
            WorkflowState.BRICK_EDITING,
            WorkflowState.BRICK_VALID,
            WorkflowState.READY_TO_SAVE,
            WorkflowState.BRICK_SAVED
        ]
        
        try:
            current_index = state_order.index(self.current_state)
            target_index = state_order.index(state)
            return target_index < current_index
        except ValueError:
            return False
    
    def transition_to(self, target_state: WorkflowState, force: bool = False) -> bool:
        """Transition to target state if allowed"""
        if not force and not self.can_transition_to(target_state):
            return False
        
        old_state = self.current_state
        self.current_state = target_state
        self.state_history.append(target_state)
        
        # Emit state change signal
        self.state_changed.emit(old_state.value, target_state.value)
        
        # Trigger state actions
        self._execute_state_actions(target_state)
        
        # Request interface update
        self.interface_update_requested.emit()
        
        return True
    
    def _execute_state_actions(self, state: WorkflowState):
        """Execute actions associated with state change"""
        actions = self.get_state_actions(state)
        for action in actions:
            self.action_triggered.emit(action)
    
    def get_current_state(self) -> WorkflowState:
        """Get current workflow state"""
        return self.current_state
    
    def get_state_history(self) -> List[WorkflowState]:
        """Get state transition history"""
        return self.state_history.copy()
    
    def reset_to_state(self, state: WorkflowState):
        """Reset workflow to specific state"""
        self.current_state = state
        self.state_history = [state]
        self.interface_update_requested.emit()

class InterfaceStateManager:
    """Manages widget states based on workflow controller using OntoBuild_v1 pattern"""
    
    def __init__(self, workflow_controller: WorkflowController):
        self.workflow = workflow_controller
        self.registered_widgets = {}  # widget_id -> widget
        self.widget_mapping = self._create_widget_mapping()  # UI element names to widget IDs
        
        # Connect to workflow signals
        self.workflow.interface_update_requested.connect(self.update_interface)
    
    def _create_widget_mapping(self) -> Dict[str, str]:
        """Map UI_STATE element names to actual widget IDs"""
        return {
            # Menu items
            "brick_create": "menu_create_brick",
            "brick_create_person": "menu_create_person_brick", 
            "brick_create_address": "menu_create_address_brick",
            "library_manager_create": "menu_library_manager",
            "library_manager_list": "menu_library_manager",
            "library_manager_set_active": "menu_library_manager",
            "library_manager_delete": "menu_library_manager",
            "library_manager_load": "menu_library_manager",
            "schema_create": "menu_create_schema",
            
            # Toolbar items
            "exit": "toolbar_exit",
            
            # Brick editor items
            "brick_editor_save": "brick_editor_ok_button",
            "brick_editor_cancel": "brick_editor_cancel_button",
            "brick_editor_add_property": "brick_editor_add_property",
            "brick_editor_remove_property": "brick_editor_remove_property",
            "brick_editor_help": "brick_editor_help_button",
            "brick_editor_select_library": "brick_editor_select_library",
        }
    
    def register_widget(self, widget_id: str, widget: QWidget):
        """Register a widget for state management"""
        self.registered_widgets[widget_id] = widget
    
    def update_interface(self):
        """Update all registered widgets based on current state using show/hide logic"""
        current_state = self.workflow.get_current_state()
        
        # Get widgets that should be visible and hidden in current state
        visible_widgets = self.workflow.get_visible_widgets(current_state)
        hidden_widgets = self.workflow.get_hidden_widgets(current_state)
        
        # Update all registered widgets
        for widget_id, widget in self.registered_widgets.items():
            # Find which UI state element this widget corresponds to
            ui_element_name = self._find_ui_element_for_widget(widget_id)
            
            if ui_element_name:
                # Check if this widget should be visible
                should_be_visible = (ui_element_name in visible_widgets and 
                                  ui_element_name not in hidden_widgets)
                
                # Apply visibility and enable state
                if hasattr(widget, 'setVisible'):
                    widget.setVisible(should_be_visible)
                elif hasattr(widget, 'setShown'):
                    widget.setShown(should_be_visible)
                
                # Also disable hidden widgets for safety
                if hasattr(widget, 'setEnabled'):
                    widget.setEnabled(should_be_visible)
                
                # Apply visual styling
                if hasattr(widget, 'setStyleSheet'):
                    if not should_be_visible:
                        widget.setStyleSheet("opacity: 0.3;")
                    else:
                        widget.setStyleSheet("")
            else:
                # If widget is not in UI_STATE, keep it visible but check if it should be disabled
                if hasattr(widget, 'setEnabled'):
                    widget.setEnabled(True)
                if hasattr(widget, 'setVisible'):
                    widget.setVisible(True)
    
    def _find_ui_element_for_widget(self, widget_id: str) -> Optional[str]:
        """Find which UI_STATE element this widget corresponds to"""
        for ui_element, mapped_widget_id in self.widget_mapping.items():
            if mapped_widget_id == widget_id:
                return ui_element
        return None
    
    def is_widget_visible(self, widget_id: str) -> bool:
        """Check if a widget should be visible in current state"""
        current_state = self.workflow.get_current_state()
        visible_widgets = self.workflow.get_visible_widgets(current_state)
        hidden_widgets = self.workflow.get_hidden_widgets(current_state)
        
        ui_element_name = self._find_ui_element_for_widget(widget_id)
        if ui_element_name:
            return (ui_element_name in visible_widgets and 
                   ui_element_name not in hidden_widgets)
        return True  # Default to visible if not in UI_STATE
    
    def can_perform_action(self, action_id: str) -> bool:
        """Check if an action can be performed in current state"""
        current_state = self.workflow.get_current_state()
        visible_widgets = self.workflow.get_visible_widgets(current_state)
        hidden_widgets = self.workflow.get_hidden_widgets(current_state)
        
        return (action_id in visible_widgets and 
                action_id not in hidden_widgets)
    
    def get_widget_state(self, widget_id: str) -> bool:
        """Get current enabled state for a widget"""
        return self.is_widget_visible(widget_id)

class BrickCreationWorkflow:
    """High-level workflow controller for brick creation process with OntoBuild_v1 action handling"""
    
    def __init__(self):
        self.workflow = WorkflowController()
        self.interface_manager = InterfaceStateManager(self.workflow)
        self.processor = None  # Will be set by main application
        
        # Connect action signals
        self.workflow.action_triggered.connect(self.handle_action)
        
    def set_processor(self, processor):
        """Set the event processor for backend communication"""
        self.processor = processor
    
    def handle_action(self, action_name: str):
        """Handle actions triggered by state transitions"""
        action_handlers = {
            "InitializeApplication": self._handle_initialize_application,
            "LibrariesLoaded": self._handle_libraries_loaded,
            "UpdateLibraryUI": self._handle_update_library_ui,
            "ActiveLibrarySet": self._handle_active_library_set,
            "EnableBrickCreation": self._handle_enable_brick_creation,
            "BrickEditingStarted": self._handle_brick_editing_started,
            "DisableOtherOperations": self._handle_disable_other_operations,
            "BrickValidated": self._handle_brick_validated,
            "EnableSaveButton": self._handle_enable_save_button,
            "ReadyToSave": self._handle_ready_to_save,
            "PrepareSaveDialog": self._handle_prepare_save_dialog,
            "BrickSaved": self._handle_brick_saved,
            "RefreshLibraryList": self._handle_refresh_library_list,
            "ResetForNewBrick": self._handle_reset_for_new_brick,
        }
        
        handler = action_handlers.get(action_name)
        if handler:
            handler()
    
    def _handle_initialize_application(self):
        """Handle application initialization"""
        # Check libraries and transition to appropriate state
        self.initialize_workflow()
    
    def _handle_libraries_loaded(self):
        """Handle libraries loaded state"""
        # Update UI to show library manager options
        pass
    
    def _handle_update_library_ui(self):
        """Handle library UI update"""
        # Refresh library display
        pass
    
    def _handle_active_library_set(self):
        """Handle active library being set"""
        # Enable brick creation options
        pass
    
    def _handle_enable_brick_creation(self):
        """Handle enabling brick creation"""
        # Show brick creation menu items
        pass
    
    def _handle_brick_editing_started(self):
        """Handle brick editing started"""
        # Hide other operations, show editor
        pass
    
    def _handle_disable_other_operations(self):
        """Handle disabling other operations during editing"""
        # Disable menu items that shouldn't be available during editing
        pass
    
    def _handle_brick_validated(self):
        """Handle brick validation"""
        # Enable save button
        pass
    
    def _handle_enable_save_button(self):
        """Handle enabling save button"""
        # Show save options
        pass
    
    def _handle_ready_to_save(self):
        """Handle ready to save state"""
        # Show library selection dialog
        pass
    
    def _handle_prepare_save_dialog(self):
        """Handle preparing save dialog"""
        # Get ready for save operation
        pass
    
    def _handle_brick_saved(self):
        """Handle brick saved successfully"""
        # Show success message
        pass
    
    def _handle_refresh_library_list(self):
        """Handle refreshing library list"""
        # Reload library data
        pass
    
    def _handle_reset_for_new_brick(self):
        """Handle resetting for new brick creation"""
        # Return to ready state
        pass
    
    def initialize_workflow(self):
        """Initialize the workflow by checking libraries"""
        if self.processor:
            # Check if libraries exist
            result = self.processor.process_event({"event": "get_libraries"})
            if result["status"] == "success":
                libraries = result["data"]["libraries"]
                if libraries:
                    # Transition to libraries_loaded state
                    self.workflow.transition_to(WorkflowState.LIBRARIES_LOADED)
                    
                    # Check if there's an active library
                    active_library = result["data"].get("active_library")
                    if active_library:
                        # Transition to active_library_set state
                        self.workflow.transition_to(WorkflowState.ACTIVE_LIBRARY_SET)
                    else:
                        # Don't automatically set active library - let user choose
                        # Stay in libraries_loaded state until user sets active library
                        pass
                else:
                    # No libraries exist - transition to libraries_loaded but no active library
                    self.workflow.transition_to(WorkflowState.LIBRARIES_LOADED)
        
        # Always update interface after initialization
        self.interface_manager.update_interface()
    
    def start_brick_creation(self):
        """Start the brick creation process"""
        if self.workflow.can_transition_to(WorkflowState.BRICK_EDITING):
            self.workflow.transition_to(WorkflowState.BRICK_EDITING)
            return True
        return False
    
    def validate_brick_data(self, brick_data: dict) -> bool:
        """Validate brick data and transition to appropriate state"""
        if self.workflow.get_current_state() == WorkflowState.BRICK_EDITING:
            # Basic validation
            if brick_data.get("name") and brick_data.get("properties"):
                self.workflow.transition_to(WorkflowState.BRICK_VALID)
                return True
        return False
    
    def prepare_to_save(self):
        """Prepare to save brick"""
        if self.workflow.get_current_state() == WorkflowState.BRICK_VALID:
            # Double-check library availability
            if self.processor:
                result = self.processor.process_event({"event": "get_libraries"})
                if result["status"] == "success" and result["data"]["libraries"]:
                    self.workflow.transition_to(WorkflowState.READY_TO_SAVE)
                    return True
        return False
    
    def complete_brick_save(self):
        """Complete the brick save process"""
        if self.workflow.get_current_state() == WorkflowState.READY_TO_SAVE:
            self.workflow.transition_to(WorkflowState.BRICK_SAVED)
            # Reset to ready state for next brick
            self.workflow.transition_to(WorkflowState.ACTIVE_LIBRARY_SET)
            return True
        return False
    
    def cancel_brick_creation(self):
        """Cancel brick creation and reset state"""
        if self.workflow.get_current_state() in [WorkflowState.BRICK_EDITING, WorkflowState.BRICK_VALID]:
            self.workflow.transition_to(WorkflowState.ACTIVE_LIBRARY_SET)
            return True
        return False
    
    def can_perform_action(self, action_id: str) -> bool:
        """Check if an action can be performed in current state"""
        return self.interface_manager.can_perform_action(action_id)
    
    def get_workflow_status(self) -> dict:
        """Get current workflow status for display"""
        return {
            "current_state": self.workflow.get_current_state().value,
            "can_create_brick": self.interface_manager.can_perform_action("brick_create"),
            "has_active_library": self.workflow.get_current_state() in [
                WorkflowState.ACTIVE_LIBRARY_SET, 
                WorkflowState.BRICK_EDITING,
                WorkflowState.BRICK_VALID,
                WorkflowState.READY_TO_SAVE,
                WorkflowState.BRICK_SAVED
            ],
            "ready_for_brick_creation": self.workflow.get_current_state() == WorkflowState.ACTIVE_LIBRARY_SET
        }
