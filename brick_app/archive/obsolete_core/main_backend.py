#!/usr/bin/env python3
"""
Main Backend Controller - Centralized event processing with signal/slot architecture
"""

from typing import Dict, List, Any, Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal
from .brick_backend import BrickBackendAPI
from .editor_backend import BrickEditorBackend


class MainBackend(QObject):
    """Main backend controller with centralized event processing"""
    
    # Signals for UI communication
    brick_created = pyqtSignal(dict)
    brick_updated = pyqtSignal(dict)
    property_added = pyqtSignal(str, dict)
    property_removed = pyqtSignal(str)
    constraint_added = pyqtSignal(str, dict)
    constraint_removed = pyqtSignal(str)
    target_class_selected = pyqtSignal(str)
    status_message = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    # Dialog signals
    show_property_dialog = pyqtSignal()
    show_class_browser = pyqtSignal()
    show_ontology_browser = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.brick_api = BrickBackendAPI()
        self.editor_backend = BrickEditorBackend(self.brick_api)
        self.current_brick = {}
        
        # Event handlers registry
        self._event_handlers = {}
        
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler for centralized processing"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    def emit_event(self, event_type: str, *args, **kwargs):
        """Emit event to all registered handlers"""
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    self.error_occurred.emit(f"Event handler error: {e}")
    
    # Brick operations
    def create_new_brick(self, brick_type: str = "NodeShape"):
        """Create new brick and emit signal"""
        try:
            self.current_brick = self.editor_backend.create_new_brick(brick_type)
            self.brick_created.emit(self.current_brick)
            self.status_message.emit("New brick created")
            return self.current_brick
        except Exception as e:
            self.error_occurred.emit(f"Failed to create brick: {e}")
            return None
    
    def save_brick(self, brick_data: Dict[str, Any]):
        """Save brick and emit signal"""
        try:
            success, message = self.editor_backend.save_brick(brick_data)
            if success:
                self.current_brick = brick_data
                self.brick_updated.emit(self.current_brick)
                self.status_message.emit("Brick saved successfully")
            else:
                self.error_occurred.emit(f"Failed to save brick: {message}")
            return success, message
        except Exception as e:
            self.error_occurred.emit(f"Save error: {e}")
            return False, str(e)
    
    def load_brick(self, brick_id: str):
        """Load brick and emit signal"""
        try:
            brick = self.editor_backend.load_brick(brick_id)
            if brick:
                self.current_brick = brick
                self.brick_updated.emit(self.current_brick)
                self.status_message.emit("Brick loaded successfully")
            return brick
        except Exception as e:
            self.error_occurred.emit(f"Load error: {e}")
            return None
    
    # Property operations
    def add_property(self, property_data: Dict[str, Any]):
        """Add property and emit signal"""
        try:
            if not self.current_brick:
                self.error_occurred.emit("No brick selected")
                return False
            
            prop_name = property_data["name"]
            self.current_brick["properties"][prop_name] = property_data
            self.property_added.emit(prop_name, property_data)
            self.status_message.emit(f"Property '{prop_name}' added")
            return True
        except Exception as e:
            self.error_occurred.emit(f"Add property error: {e}")
            return False
    
    def remove_property(self, prop_name: str):
        """Remove property and emit signal"""
        try:
            if prop_name in self.current_brick.get("properties", {}):
                del self.current_brick["properties"][prop_name]
                self.property_removed.emit(prop_name)
                self.status_message.emit(f"Property '{prop_name}' removed")
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Remove property error: {e}")
            return False
    
    # Constraint operations
    def add_constraint(self, prop_name: str, constraint_data: Dict[str, Any]):
        """Add constraint and emit signal"""
        try:
            if prop_name in self.current_brick.get("properties", {}):
                if "constraints" not in self.current_brick["properties"][prop_name]:
                    self.current_brick["properties"][prop_name]["constraints"] = []
                self.current_brick["properties"][prop_name]["constraints"].append(constraint_data)
                self.constraint_added.emit(prop_name, constraint_data)
                self.status_message.emit("Constraint added")
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Add constraint error: {e}")
            return False
    
    def remove_constraint(self, prop_name: str, constraint_index: int):
        """Remove constraint and emit signal"""
        try:
            if prop_name in self.current_brick.get("properties", {}):
                constraints = self.current_brick["properties"][prop_name].get("constraints", [])
                if 0 <= constraint_index < len(constraints):
                    del constraints[constraint_index]
                    self.constraint_removed.emit(prop_name)
                    self.status_message.emit("Constraint removed")
                    return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Remove constraint error: {e}")
            return False
    
    # Target class operations
    def set_target_class(self, class_uri: str):
        """Set target class and emit signal"""
        try:
            if self.current_brick:
                self.current_brick["target_class"] = class_uri
                self.target_class_selected.emit(class_uri)
                self.status_message.emit(f"Target class set: {class_uri}")
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Set target class error: {e}")
            return False
    
    # Dialog operations
    def request_property_dialog(self):
        """Request property dialog via signal"""
        self.show_property_dialog.emit()
    
    def request_class_browser(self):
        """Request class browser via signal"""
        self.show_class_browser.emit()
    
    def request_ontology_browser(self):
        """Request ontology browser via signal"""
        self.show_ontology_browser.emit()
    
    # Ontology operations
    def get_available_ontologies(self) -> Dict[str, Any]:
        """Get available ontologies from manager"""
        return self.editor_backend.ontology_manager.ontologies
    
    def get_ontology_classes(self, ontology_name: str) -> List[Dict[str, str]]:
        """Get classes from specific ontology"""
        ontologies = self.get_available_ontologies()
        if ontology_name in ontologies:
            return ontologies[ontology_name].get('classes', [])
        return []
    
    def get_ontology_properties(self, ontology_name: str) -> List[Dict[str, str]]:
        """Get properties from specific ontology"""
        ontologies = self.get_available_ontologies()
        if ontology_name in ontologies:
            return ontologies[ontology_name].get('properties', [])
        return []
