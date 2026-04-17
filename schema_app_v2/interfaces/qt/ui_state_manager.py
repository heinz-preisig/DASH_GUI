#!/usr/bin/env python3
"""
UI State Manager
Centralized state management to prevent cascading effects and improve organization
"""

from typing import Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget


class UIStateManager(QObject):
    """Centralized UI state management"""
    
    # Signals for state changes
    state_changed = pyqtSignal(str, bool)  # widget_name, enabled_state
    schema_selected = pyqtSignal(object)   # schema object
    schema_deselected = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._widgets: Dict[str, QWidget] = {}
        self._state_groups: Dict[str, list] = {
            "schema_details": ["nameLineEdit", "descriptionLineEdit", "rootBrickComboBox"],
            "component_management": ["addComponentButton", "removeComponentButton", "componentBricksListWidget"],
            "flow_management": ["flowTypeComboBox", "editFlowButton"],
            "actions": ["saveButton", "exportShaclButton"]
        }
        self._current_schema = None
    
    def register_widget(self, name: str, widget: QWidget):
        """Register a widget for state management"""
        self._widgets[name] = widget
    
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
    
    def set_current_schema(self, schema):
        """Set the current schema and update UI accordingly"""
        self._current_schema = schema
        self.set_schema_state(schema is not None)
    
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
                self.state_changed.emit(widget_name, enabled)
    
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
