#!/usr/bin/env python3
"""
UI State Manager
Centralized state management to prevent cascading effects and improve organization
"""

from typing import Dict, Any, Optional
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget


class SchemaState(Enum):
    """Schema application states"""
    INITIAL = "initial"              # No schema selected, fresh start
    SCHEMA_SELECTED = "selected"     # Schema loaded, editing enabled
    SCHEMA_MODIFIED = "modified"      # Unsaved changes present
    SCHEMA_SAVING = "saving"         # Save operation in progress
    COMPONENT_ADDING = "adding"      # Component selection dialog active
    FLOW_EDITING = "flow_editing"    # Flow configuration dialog active


class UIStateManager(QObject):
    """Enhanced UI state management with granular state control"""
    
    # Signals for state changes
    state_changed = pyqtSignal(SchemaState, SchemaState)  # old_state, new_state
    schema_modified = pyqtSignal()                        # changes detected
    schema_saved = pyqtSignal()                           # save completed
    schema_selected = pyqtSignal(object)                  # schema object
    schema_deselected = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._widgets: Dict[str, QWidget] = {}
        self._current_schema = None
        self._current_state = SchemaState.INITIAL
        self._has_unsaved_changes = False
        
        # Complete list of all GUI components
        self._all_components = [
            "libraryComboBox", "brickLibraryComboBox", "schemaListWidget", "newSchemaButton", 
            "deleteSchemaButton", "nameLineEdit", "descriptionLineEdit", "rootBrickComboBox",
            "addComponentButton", "removeComponentButton", "componentBricksListWidget",
            "flowTypeComboBox", "editFlowButton", "saveButton", "exportShaclButton",
            "brickListWidget", "brickSearchLineEdit", "bricksGroupBox", "schemaDetailsGroupBox"
        ]
        
        # State visibility dictionary - key=state, value=list of visible components
        self._state_visibility: Dict[SchemaState, list] = {
            SchemaState.INITIAL: [
                "libraryComboBox", "brickLibraryComboBox", "schemaListWidget", "newSchemaButton"
            ],
            SchemaState.SCHEMA_SELECTED: [
                "libraryComboBox", "brickLibraryComboBox", "schemaListWidget", "newSchemaButton",
                "deleteSchemaButton", "nameLineEdit", "descriptionLineEdit", "rootBrickComboBox",
                "addComponentButton", "removeComponentButton", "componentBricksListWidget",
                "flowTypeComboBox", "editFlowButton", "exportShaclButton",
                "brickListWidget", "brickSearchLineEdit", "bricksGroupBox", "schemaDetailsGroupBox"
            ],
            SchemaState.SCHEMA_MODIFIED: [
                "libraryComboBox", "brickLibraryComboBox", "schemaListWidget", "newSchemaButton",
                "deleteSchemaButton", "nameLineEdit", "descriptionLineEdit", "rootBrickComboBox",
                "addComponentButton", "removeComponentButton", "componentBricksListWidget",
                "flowTypeComboBox", "editFlowButton", "saveButton", "exportShaclButton",
                "brickListWidget", "brickSearchLineEdit", "bricksGroupBox", "schemaDetailsGroupBox"
            ],
            SchemaState.SCHEMA_SAVING: [
                # Only library selection and schema list during saving
                "libraryComboBox", "brickLibraryComboBox", "schemaListWidget"
            ],
            SchemaState.COMPONENT_ADDING: [
                # Show schema details and component management, but hide available bricks
                "libraryComboBox", "brickLibraryComboBox", "schemaListWidget", "newSchemaButton",
                "deleteSchemaButton", "nameLineEdit", "descriptionLineEdit", "rootBrickComboBox",
                "addComponentButton", "removeComponentButton", "componentBricksListWidget",
                "flowTypeComboBox", "editFlowButton", "exportShaclButton",
                "schemaDetailsGroupBox"  # Show schema details for component editing
                # Note: brickListWidget, brickSearchLineEdit, bricksGroupBox intentionally hidden
            ],
            SchemaState.FLOW_EDITING: [
                # Same as SCHEMA_SELECTED but with save disabled
                "libraryComboBox", "brickLibraryComboBox", "schemaListWidget", "newSchemaButton",
                "deleteSchemaButton", "nameLineEdit", "descriptionLineEdit", "rootBrickComboBox",
                "addComponentButton", "removeComponentButton", "componentBricksListWidget",
                "flowTypeComboBox", "editFlowButton", "exportShaclButton",
                "brickListWidget", "brickSearchLineEdit", "bricksGroupBox", "schemaDetailsGroupBox"
            ]
        }
    
    def register_widget(self, name: str, widget: QWidget):
        """Register a widget for state management"""
        self._widgets[name] = widget
    
    def get_current_state(self) -> SchemaState:
        """Get the current application state"""
        return self._current_state
    
    def set_state(self, new_state: SchemaState) -> bool:
        """Set new application state with validation"""
        print(f"DEBUG: State transition requested: {self._current_state} -> {new_state}")
        
        # Allow same state during initialization
        if self._current_state != new_state and not self._is_valid_transition(self._current_state, new_state):
            print(f"DEBUG: Invalid state transition: {self._current_state} -> {new_state}")
            return False
        
        old_state = self._current_state
        self._current_state = new_state
        print(f"DEBUG: Setting state to {new_state}")
        
        # Apply state-specific widget configuration
        self._apply_state_configuration(new_state)
        
        # Emit state change signal
        self.state_changed.emit(old_state, new_state)
        print(f"DEBUG: State transition completed: {old_state} -> {new_state}")
        
        return True
    
    def _is_valid_transition(self, from_state: SchemaState, to_state: SchemaState) -> bool:
        """Validate state transition"""
        # Define valid transitions
        valid_transitions = {
            SchemaState.INITIAL: [SchemaState.SCHEMA_SELECTED],
            SchemaState.SCHEMA_SELECTED: [
                SchemaState.INITIAL, SchemaState.SCHEMA_MODIFIED, 
                SchemaState.COMPONENT_ADDING, SchemaState.FLOW_EDITING
            ],
            SchemaState.SCHEMA_MODIFIED: [
                SchemaState.INITIAL, SchemaState.SCHEMA_SELECTED, 
                SchemaState.SCHEMA_SAVING, SchemaState.COMPONENT_ADDING, 
                SchemaState.FLOW_EDITING
            ],
            SchemaState.SCHEMA_SAVING: [SchemaState.SCHEMA_SELECTED, SchemaState.SCHEMA_MODIFIED],
            SchemaState.COMPONENT_ADDING: [SchemaState.SCHEMA_SELECTED, SchemaState.SCHEMA_MODIFIED],
            SchemaState.FLOW_EDITING: [SchemaState.SCHEMA_SELECTED, SchemaState.SCHEMA_MODIFIED]
        }
        return to_state in valid_transitions.get(from_state, [])
    
    def _apply_state_configuration(self, state: SchemaState):
        """Apply widget visibility configuration for specific state"""
        print(f"DEBUG: Applying state configuration: {state.name}")
        print(f"DEBUG: Visible components: {self._state_visibility.get(state, [])}")
        
        # Step 1: Hide ALL components first
        self._hide_all_components()
        print("DEBUG: Hidden all components")
        
        # Step 2: Show only components that should be visible for this state
        visible_components = self._state_visibility.get(state, [])
        self._show_components(visible_components)
        print(f"DEBUG: Showing {len(visible_components)} components: {visible_components}")
        
        # Step 3: Handle special case for save button (enabled/disabled but visible)
        if state in [SchemaState.SCHEMA_SELECTED, SchemaState.COMPONENT_ADDING, SchemaState.FLOW_EDITING]:
            save_button = self._widgets.get("saveButton")
            if save_button:
                save_button.setEnabled(False)
                print("DEBUG: Save button disabled")
        elif state == SchemaState.SCHEMA_MODIFIED:
            save_button = self._widgets.get("saveButton")
            if save_button:
                save_button.setEnabled(True)
                print("DEBUG: Save button enabled")
    
    def _hide_all_components(self):
        """Hide all GUI components"""
        print("DEBUG: Hiding all components")
        for component_name in self._all_components:
            widget = self._widgets.get(component_name)
            if widget:
                widget.setVisible(False)
                widget.setEnabled(False)
                print(f"DEBUG: Hidden {component_name}")
    
    def _show_components(self, component_names: list):
        """Show specific components"""
        print(f"DEBUG: Showing {len(component_names)} components: {component_names}")
        for component_name in component_names:
            widget = self._widgets.get(component_name)
            if widget:
                widget.setVisible(True)
                widget.setEnabled(True)
                print(f"DEBUG: Shown {component_name}")
            else:
                print(f"DEBUG: Widget {component_name} not found in registry!")
    
    def _configure_widgets(self, config: Dict[str, Any]):
        """Configure widgets based on state configuration"""
        for group_name, enabled in config.items():
            if group_name in self._widgets:
                # Individual widget configuration
                widget = self._widgets[group_name]
                if widget:
                    widget.setEnabled(enabled)
            else:
                # Group configuration
                widget_names = self._state_groups.get(group_name, [])
                for widget_name in widget_names:
                    widget = self._widgets.get(widget_name)
                    if widget:
                        # For group containers, use visibility, for others use enabled state
                        if "group" in group_name:
                            widget.setVisible(enabled)
                        else:
                            widget.setEnabled(enabled)
    
    def set_schema_state(self, has_schema: bool):
        """Set UI state based on whether a schema is selected"""
        for group_name, widget_names in self._state_groups.items():
            for widget_name in widget_names:
                widget = self._widgets.get(widget_name)
                if widget:
                    widget.setEnabled(has_schema)
                    self.state_changed.emit(widget_name, has_schema)
        
        if has_schema:
            self.schema_selected.emit(self._current_schema)
        else:
            self.schema_deselected.emit()
    
    def set_current_schema(self, schema, has_unsaved_changes: bool = False):
        """Set the current schema and update state accordingly"""
        self._current_schema = schema
        self._has_unsaved_changes = has_unsaved_changes
        
        if schema:
            if has_unsaved_changes:
                self.set_state(SchemaState.SCHEMA_MODIFIED)
            else:
                self.set_state(SchemaState.SCHEMA_SELECTED)
            self.schema_selected.emit(schema)
        else:
            self.set_state(SchemaState.INITIAL)
            self.schema_deselected.emit()
    
    def mark_schema_modified(self):
        """Mark current schema as having unsaved changes"""
        if self._current_state in [SchemaState.SCHEMA_SELECTED, SchemaState.SCHEMA_MODIFIED]:
            self._has_unsaved_changes = True
            self.set_state(SchemaState.SCHEMA_MODIFIED)
            self.schema_modified.emit()
    
    def mark_schema_saved(self):
        """Mark current schema as saved"""
        if self._current_state == SchemaState.SCHEMA_SAVING:
            self._has_unsaved_changes = False
            self.set_state(SchemaState.SCHEMA_SELECTED)
            self.schema_saved.emit()
    
    def start_saving(self):
        """Start save operation"""
        if self._current_state == SchemaState.SCHEMA_MODIFIED:
            self.set_state(SchemaState.SCHEMA_SAVING)
    
    def start_component_adding(self):
        """Start component addition process"""
        if self._current_state in [SchemaState.SCHEMA_SELECTED, SchemaState.SCHEMA_MODIFIED]:
            self.set_state(SchemaState.COMPONENT_ADDING)
    
    def finish_component_adding(self, was_modified: bool = False):
        """Finish component addition process"""
        if self._current_state == SchemaState.COMPONENT_ADDING:
            if was_modified or self._has_unsaved_changes:
                self.set_state(SchemaState.SCHEMA_MODIFIED)
            else:
                self.set_state(SchemaState.SCHEMA_SELECTED)
    
    def start_flow_editing(self):
        """Start flow editing process"""
        if self._current_state in [SchemaState.SCHEMA_SELECTED, SchemaState.SCHEMA_MODIFIED]:
            self.set_state(SchemaState.FLOW_EDITING)
    
    def finish_flow_editing(self, was_modified: bool = False):
        """Finish flow editing process"""
        if self._current_state == SchemaState.FLOW_EDITING:
            if was_modified or self._has_unsaved_changes:
                self.set_state(SchemaState.SCHEMA_MODIFIED)
            else:
                self.set_state(SchemaState.SCHEMA_SELECTED)
    
    def get_widget(self, name: str) -> Optional[QWidget]:
        """Get a registered widget by name"""
        return self._widgets.get(name)
    
    def enable_group(self, group_name: str, enabled: bool):
        """Enable/disable a specific group of widgets"""
        widget_names = self._state_groups.get(group_name, [])
        for widget_name in widget_names:
            widget = self._widgets.get(widget_name)
            if widget:
                widget.setEnabled(enabled)
                # Emit individual widget state change for compatibility
                self.state_changed.emit(self._current_state, self._current_state)
    
    def has_unsaved_changes(self) -> bool:
        """Check if current schema has unsaved changes"""
        return self._has_unsaved_changes
    
    def update_remove_button_state(self, has_selection: bool):
        """Update remove button state based on component selection"""
        remove_button = self._widgets.get("removeComponentButton")
        if remove_button:
            # Only enable remove button if we have a schema and component is selected
            should_enable = (self._current_state in [SchemaState.SCHEMA_SELECTED, SchemaState.SCHEMA_MODIFIED] and has_selection)
            remove_button.setEnabled(should_enable)
    
    def clear_form_fields(self):
        """Clear all form fields"""
        field_widgets = ["nameLineEdit", "descriptionLineEdit"]
        for widget_name in field_widgets:
            widget = self._widgets.get(widget_name)
            if widget and hasattr(widget, 'clear'):
                widget.clear()
        
        # Reset comboboxes
        combobox_widgets = ["rootBrickComboBox", "flowTypeComboBox"]
        for widget_name in combobox_widgets:
            widget = self._widgets.get(widget_name)
            if widget and hasattr(widget, 'setCurrentIndex'):
                widget.setCurrentIndex(0)
        
        # Clear lists
        list_widgets = ["componentBricksListWidget"]
        for widget_name in list_widgets:
            widget = self._widgets.get(widget_name)
            if widget and hasattr(widget, 'clear'):
                widget.clear()
