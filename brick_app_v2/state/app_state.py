#!/usr/bin/env python3
"""
Application State Management
Clean state management pattern for UI and business logic separation
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


class UIState(Enum):
    """UI application states"""
    BROWSE = "browse"
    EDIT = "edit"
    CREATE = "create"


class BrickType(Enum):
    """Brick types"""
    NODE_SHAPE = "NodeShape"
    PROPERTY_SHAPE = "PropertyShape"


@dataclass
class BrickState:
    """Current brick editing state"""
    brick_id: Optional[str] = None
    name: str = ""
    description: str = ""
    object_type: str = BrickType.NODE_SHAPE.value
    target_class: str = ""
    property_path: str = ""
    properties: Dict[str, Any] = None
    constraints: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
        if self.constraints is None:
            self.constraints = []


@dataclass
class UIViewState:
    """UI visibility and interaction state"""
    current_state: UIState = UIState.BROWSE
    current_brick_type: BrickType = BrickType.NODE_SHAPE
    selected_library: str = "default"
    selected_brick_id: Optional[str] = None
    selected_property_name: Optional[str] = None
    
    # UI visibility flags
    show_library_panel: bool = True
    show_brick_list: bool = True
    show_property_list: bool = False
    show_brick_details: bool = True
    show_brick_editor: bool = False
    
    # Field visibility based on brick type
    show_target_class_fields: bool = True
    show_property_path_fields: bool = False


class AppStateManager:
    """Centralized application state manager"""
    
    def __init__(self):
        self._ui_state = UIViewState()
        self._brick_state = BrickState()
        self._state_listeners = []
    
    def add_state_listener(self, listener):
        """Add listener for state changes"""
        self._state_listeners.append(listener)
    
    def remove_state_listener(self, listener):
        """Remove state listener"""
        if listener in self._state_listeners:
            self._state_listeners.remove(listener)
    
    def _notify_state_change(self, state_type: str, old_value: Any, new_value: Any):
        """Notify all listeners of state change"""
        for listener in self._state_listeners:
            try:
                listener.on_state_changed(state_type, old_value, new_value)
            except Exception as e:
                print(f"Error notifying listener: {e}")
    
    # UI State Management
    def set_ui_state(self, new_state: UIState):
        """Set current UI state"""
        old_state = self._ui_state.current_state
        self._ui_state.current_state = new_state
        self._update_ui_visibility()
        self._notify_state_change("ui_state", old_state, new_state)
    
    def get_ui_state(self) -> UIState:
        """Get current UI state"""
        return self._ui_state.current_state
    
    def set_brick_type(self, brick_type: BrickType):
        """Set current brick type"""
        old_type = self._ui_state.current_brick_type
        self._ui_state.current_brick_type = brick_type
        self._update_field_visibility()
        self._notify_state_change("brick_type", old_type, brick_type)
    
    def get_brick_type(self) -> BrickType:
        """Get current brick type"""
        return self._ui_state.current_brick_type
    
    def set_selected_library(self, library_name: str):
        """Set selected library"""
        old_library = self._ui_state.selected_library
        self._ui_state.selected_library = library_name
        self._notify_state_change("selected_library", old_library, library_name)
    
    def get_selected_library(self) -> str:
        """Get selected library"""
        return self._ui_state.selected_library
    
    def set_selected_brick(self, brick_id: Optional[str]):
        """Set selected brick"""
        old_brick = self._ui_state.selected_brick_id
        self._ui_state.selected_brick_id = brick_id
        self._notify_state_change("selected_brick", old_brick, brick_id)
    
    def get_selected_brick(self) -> Optional[str]:
        """Get selected brick"""
        return self._ui_state.selected_brick_id
    
    # Brick State Management
    def load_brick(self, brick_data: Dict[str, Any]):
        """Load brick data into state"""
        old_brick = self._brick_state
        
        self._brick_state = BrickState(
            brick_id=brick_data.get("brick_id"),
            name=brick_data.get("name", ""),
            description=brick_data.get("description", ""),
            object_type=brick_data.get("object_type", "NodeShape"),
            target_class=brick_data.get("target_class", ""),
            property_path=brick_data.get("property_path", ""),
            properties=brick_data.get("properties", {}),
            constraints=brick_data.get("constraints", [])
        )
        
        # Update brick type if different
        if self._brick_state.object_type != self._ui_state.current_brick_type.value:
            new_type = BrickType.NODE_SHAPE if self._brick_state.object_type == "NodeShape" else BrickType.PROPERTY_SHAPE
            self.set_brick_type(new_type)
        
        self._notify_state_change("brick_loaded", old_brick, self._brick_state)
    
    def create_new_brick(self, brick_type: BrickType = BrickType.NODE_SHAPE):
        """Create new brick in state"""
        old_brick = self._brick_state
        
        self._brick_state = BrickState(
            brick_id=None,
            name="",
            description="",
            object_type=brick_type.value,
            target_class="",
            property_path="",
            properties={},
            constraints=[]
        )
        
        self.set_brick_type(brick_type)
        self._notify_state_change("brick_created", old_brick, self._brick_state)
    
    def update_brick_field(self, field_name: str, value: Any):
        """Update a specific brick field"""
        old_value = getattr(self._brick_state, field_name, None)
        setattr(self._brick_state, field_name, value)
        self._notify_state_change(f"brick_field_{field_name}", old_value, value)
    
    def get_brick_state(self) -> BrickState:
        """Get current brick state"""
        return self._brick_state
    
    def get_brick_dict(self) -> Dict[str, Any]:
        """Get brick state as dictionary"""
        return {
            "brick_id": self._brick_state.brick_id,
            "name": self._brick_state.name,
            "description": self._brick_state.description,
            "object_type": self._brick_state.object_type,
            "target_class": self._brick_state.target_class,
            "property_path": self._brick_state.property_path,
            "properties": self._brick_state.properties,
            "constraints": self._brick_state.constraints
        }
    
    # UI Visibility Management
    def _update_ui_visibility(self):
        """Update UI visibility based on current state"""
        state = self._ui_state.current_state
        
        if state == UIState.BROWSE:
            self._ui_state.show_brick_list = True
            self._ui_state.show_property_list = True  # Show both lists in browse mode
            self._ui_state.show_brick_details = True
            self._ui_state.show_brick_editor = False
            
        elif state == UIState.EDIT:
            self._ui_state.show_brick_list = False
            self._ui_state.show_property_list = True
            self._ui_state.show_brick_details = True
            self._ui_state.show_brick_editor = True
            
        elif state == UIState.CREATE:
            self._ui_state.show_brick_list = False
            self._ui_state.show_property_list = False
            self._ui_state.show_brick_details = False
            self._ui_state.show_brick_editor = True
    
    def _update_field_visibility(self):
        """Update field visibility based on brick type"""
        brick_type = self._ui_state.current_brick_type
        
        if brick_type == BrickType.NODE_SHAPE:
            self._ui_state.show_target_class_fields = True
            self._ui_state.show_property_path_fields = False
        else:  # PROPERTY_SHAPE
            self._ui_state.show_target_class_fields = False
            self._ui_state.show_property_path_fields = True
    
    def get_ui_visibility(self) -> UIViewState:
        """Get current UI visibility state"""
        return self._ui_state


# Global state manager instance
app_state_manager = AppStateManager()
