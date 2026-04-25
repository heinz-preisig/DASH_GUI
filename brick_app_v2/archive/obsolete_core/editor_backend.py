#!/usr/bin/env python3
"""
Editor Backend - Business logic for brick editing
Separates frontend concerns from business logic
"""

from typing import Dict, List, Any, Optional, Tuple, Callable
import uuid
import os
import json
from datetime import datetime
from .brick_backend import BrickBackendAPI
from .brick_generator import SHACLBrick, SHACLConstraint
from .ontology_manager import OntologyManager
from rdflib import Graph, Namespace, URIRef, RDF, RDFS, OWL

class BrickEditorBackend:
    """Backend logic for brick editing operations"""
    
    def __init__(self, brick_api: BrickBackendAPI):
        self.brick_api = brick_api
        self.current_brick = None  # Will be set when create_new_brick is called
        self.last_saved_timestamp = None  # Track when brick was last saved
        self.ontology_manager = OntologyManager()
        self.frontend_window = None  # Reference to frontend for dialog control
        
        # Ensure we have an active library
        self._ensure_active_library()
        
        # Dialog instance management
        self.dialogs = {
            'property_dialog': None,
            'class_browser': None,
            'constraint_dialog': None,
            'load_brick_dialog': None,
            'ontology_browser': None
        }
        
        # Event handler system (automata)
        self.event_handlers = {
            'brick_created': [],
            'brick_updated': [],
            'brick_loaded': [],
            'property_added': [],
            'property_removed': [],
            'constraint_added': [],
            'constraint_removed': [],
            'target_class_set': [],
            'brick_saved': [],
            'dialog_requested': [],
            'error_occurred': []
        }
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler for backend events"""
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
    
    def emit_event(self, event_type: str, *args, **kwargs):
        """Emit event to all registered handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    self.emit_event('error_occurred', f"Event handler error: {e}")
    
    def create_new_brick(self, brick_type: str = "NodeShape") -> SHACLBrick:
        """Create a new brick and set as current"""
        self.current_brick = SHACLBrick(
            brick_id=str(uuid.uuid4()),
            name="",
            description="",
            object_type=brick_type
        )
        self.last_saved_timestamp = None  # New brick hasn't been saved yet
        self.emit_event('brick_created', self.current_brick.to_dict())
        return self.current_brick
    
    def get_current_brick(self) -> Dict[str, Any]:
        """Get current brick data"""
        if self.current_brick is None:
            return {}
        return self.current_brick.to_dict()
    
    def set_current_brick(self, brick_data: Dict[str, Any]):
        """Set current brick and emit update event"""
        self.current_brick = SHACLBrick.from_dict(brick_data)
        self.emit_event('brick_updated', self.current_brick.to_dict())
    
    def update_brick_field(self, field_name: str, value: Any):
        """Update a specific field in current brick"""
        if not self.current_brick:
            self.emit_event('error_occurred', "No current brick")
            return
        
        if field_name == "name":
            self.current_brick.update_name(value)
        elif field_name == "description":
            self.current_brick.update_description(value)
        elif field_name == "target_class":
            self.current_brick.update_target_class(value)
        else:
            # For other fields, use direct assignment
            setattr(self.current_brick, field_name, value)
            self.current_brick._mark_modified()
        
        self.emit_event('brick_updated', self.current_brick.to_dict())
    
    def set_target_class(self, class_uri: str):
        """Set target class for current brick"""
        if not self.current_brick:
            self.emit_event('error_occurred', "No current brick")
            return
        
        self.current_brick.update_target_class(class_uri)
        self.emit_event('target_class_set', class_uri)
        self.emit_event('brick_updated', self.current_brick.to_dict())
    
    def add_property_to_current_brick(self, property_data: Dict[str, Any]) -> bool:
        """Add property to current brick"""
        if not self.current_brick:
            self.emit_event('error_occurred', "No current brick")
            return False
        
        prop_name = property_data["name"]
        self.current_brick.add_property(prop_name, property_data)
        self.emit_event('property_added', prop_name, property_data)
        self.emit_event('brick_updated', self.current_brick.to_dict())
        return True
    
    def remove_property_from_current_brick(self, prop_name: str) -> bool:
        """Remove property from current brick"""
        if not self.current_brick:
            self.emit_event('error_occurred', "No current brick")
            return False
        
        if prop_name in self.current_brick.properties:
            self.current_brick.remove_property(prop_name)
            self.emit_event('property_removed', prop_name)
            self.emit_event('brick_updated', self.current_brick.to_dict())
            return True
        return False
    
    def add_constraint_to_property(self, prop_name: str, constraint_data: Dict[str, Any]) -> bool:
        """Add constraint to property in current brick"""
        if not self.current_brick:
            self.emit_event('error_occurred', "No current brick")
            return False
        
        if prop_name not in self.current_brick.properties:
            self.emit_event('error_occurred', f"Property '{prop_name}' not found")
            return False
        
        # Create SHACLConstraint object
        constraint = SHACLConstraint(
            constraint_type=constraint_data["constraint_type"],
            value=constraint_data["value"],
            parameters=constraint_data.get("parameters", {})
        )
        
        self.current_brick.add_constraint(constraint)
        self.emit_event('constraint_added', prop_name, constraint_data)
        self.emit_event('brick_updated', self.current_brick.to_dict())
        return True
    
    def remove_constraint_from_property(self, prop_name: str, constraint_index: int) -> bool:
        """Remove constraint from property in current brick"""
        if not self.current_brick:
            self.emit_event('error_occurred', "No current brick")
            return False
        
        if prop_name not in self.current_brick.properties:
            self.emit_event('error_occurred', f"Property '{prop_name}' not found")
            return False
        
        if 0 <= constraint_index < len(self.current_brick.constraints):
            self.current_brick.remove_constraint(constraint_index)
            self.emit_event('constraint_removed', prop_name)
            self.emit_event('brick_updated', self.current_brick.to_dict())
        else:
            self.emit_event('error_occurred', f"Constraint index {constraint_index} out of range")
            return False
    
    def load_brick(self, brick_id: str) -> Optional[SHACLBrick]:
        """Load existing brick from backend for editing"""
        result = self.brick_api.get_brick_details(brick_id)
        if result["status"] == "success":
            # Create SHACLBrick object from dictionary data
            self.current_brick = SHACLBrick.from_dict(result["data"])
            # Track the last saved timestamp from the loaded brick
            self.last_saved_timestamp = self.current_brick.updated_at
            self.emit_event('brick_loaded', self.current_brick.to_dict())
            return self.current_brick
        return None
    
    def is_brick_modified(self) -> bool:
        """Check if current brick has been modified since last save"""
        if self.last_saved_timestamp is None:
            return True  # New brick or never saved
        
        if not self.current_brick:
            return False  # No current brick
        
        return self.current_brick.is_modified_since(self.last_saved_timestamp)
    
    def save_current_brick(self) -> Tuple[bool, str]:
        """Save current brick to backend"""
        if not self.current_brick:
            return False, "No current brick to save"
        
        try:
            # Debug: Check brick_id
            print(f"DEBUG: Saving brick - brick_id: {getattr(self.current_brick, 'brick_id', 'MISSING')}")
            print(f"DEBUG: Brick type: {type(self.current_brick)}")
            print(f"DEBUG: Brick dict keys: {list(self.current_brick.to_dict().keys())}")
            
            # Validate brick data directly
            if not self.current_brick.name.strip():
                return False, "Brick name is required"
            
            if self.current_brick.object_type == "NodeShape":
                target_class = self.current_brick.get_target_class().strip()
                if not target_class:
                    return False, "Target class is required for NodeShape"
            
            # Update or create brick
            if self.current_brick.brick_id:
                print(f"DEBUG: Checking if brick exists: {self.current_brick.brick_id}")
                # Check if brick actually exists in database
                existing_brick = self.brick_api.get_brick_details(self.current_brick.brick_id)
                print(f"DEBUG: Existing brick result: {existing_brick['status']}")
                if existing_brick["status"] == "success":
                    # Brick exists, update it
                    print(f"DEBUG: Updating brick with data keys: {list(self.current_brick.to_dict().keys())}")
                    result = self.brick_api.update_brick(self.current_brick.brick_id, self.current_brick.to_dict())
                    print(f"DEBUG: Update result: {result['status']}")
                else:
                    # Brick doesn't exist in database, create it
                    print(f"DEBUG: Creating new brick with brick_id: {self.current_brick.brick_id}")
                    result = self.brick_api.create_nodeshape_brick(
                        self.current_brick.brick_id,
                        self.current_brick.name,
                        self.current_brick.description,
                        self.current_brick.get_target_class(),
                        self.current_brick.properties,
                        [c.to_dict() for c in self.current_brick.constraints],
                        self.current_brick.tags
                    )
                    print(f"DEBUG: Create result: {result['status']}")
            else:
                # Create new brick
                print(f"DEBUG: No brick_id, creating new brick")
                self.current_brick.brick_id = str(uuid.uuid4())
                print(f"DEBUG: Assigned new brick_id: {self.current_brick.brick_id}")
                result = self.brick_api.create_nodeshape_brick(
                    self.current_brick.brick_id,
                    self.current_brick.name,
                    self.current_brick.description,
                    self.current_brick.get_target_class(),
                    self.current_brick.properties,
                    [c.to_dict() for c in self.current_brick.constraints],
                    self.current_brick.tags
                )
                print(f"DEBUG: Create result: {result['status']}")
            
            if result["status"] == "success":
                # Update current brick with saved data
                print(f"DEBUG: Save result data keys: {list(result['data'].keys())}")
                print(f"DEBUG: brick_id in result data: {'brick_id' in result['data']}")
                
                # The brick data is nested under 'brick' key
                brick_data = result["data"].get("brick", result["data"])
                print(f"DEBUG: Final brick data keys: {list(brick_data.keys())}")
                print(f"DEBUG: brick_id in final brick data: {'brick_id' in brick_data}")
                
                self.current_brick = SHACLBrick.from_dict(brick_data)
                # Update last saved timestamp to match the saved brick's updated_at
                self.last_saved_timestamp = self.current_brick.updated_at
                self.emit_event('brick_saved', self.current_brick.to_dict())
                self.emit_event('brick_updated', self.current_brick.to_dict())
                return True, "Brick saved successfully"
            else:
                return False, result.get("message", "Failed to save brick")
                
        except Exception as e:
            self.emit_event('error_occurred', f"Error saving brick: {str(e)}")
            return False, f"Error saving brick: {str(e)}"
    
    def validate_brick(self, brick_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate brick data"""
        if not brick_data.get("name", "").strip():
            return False, "Brick name is required"
        
        object_type = brick_data.get("object_type", "")
        
        if object_type == "NodeShape":
            # NodeShape requires target class
            target_class = brick_data.get("target_class", "").strip()
            if not target_class:
                return False, "Target class is required for NodeShape"
                
        elif object_type == "PropertyShape":
            # PropertyShape requires path
            properties = brick_data.get("properties", {})
            if not properties.get("path", "").strip():
                return False, "Path is required for PropertyShape"
        
        return True, ""
    
    def get_available_target_classes(self) -> List[Dict[str, str]]:
        """Get available target classes from ontologies"""
        return self.ontology_manager.get_available_classes()
    
    def get_available_properties(self) -> List[Dict[str, str]]:
        """Get available properties from ontologies"""
        return self.ontology_manager.get_available_properties()
    
    def get_property_datatype(self, prop_name: str) -> str:
        """Get the data type of a property from ontology information"""
        # Look up the property in the ontology manager
        properties = self.ontology_manager.get_available_properties()
        for prop in properties:
            if prop.get('name') == prop_name or prop.get('uri') == prop_name:
                # For now, return a generic type - could be enhanced with actual ontology data
                return "string"
        
        # Default fallback
        return "string"
    
    def get_property_constraints(self, prop_name: str) -> List[str]:
        """Get compatible constraint types for a property"""
        # Standard SHACL constraint types
        common_constraints = [
            "minLength",
            "maxLength", 
            "pattern",
            "minInclusive",
            "maxInclusive",
            "minExclusive",
            "maxExclusive",
            "in",
            "datatype",
            "nodeKind",
            "class"
        ]
        
        # Could be enhanced to return property-specific constraints based on ontology
        return common_constraints
    
    def set_frontend_window(self, window):
        """Set reference to frontend window for dialog control"""
        self.frontend_window = window
    
    # Backend-controlled GUI methods
    def request_property_dialog(self):
        """Request property dialog - backend controls GUI"""
        if not self.frontend_window:
            self.emit_event('error_occurred', 'No frontend window available')
            return
        
        self.emit_event('dialog_requested', 'property')
        self.frontend_window._show_add_property_dialog()
    
    def request_class_browser(self):
        """Request class browser - backend controls GUI"""
        if not self.frontend_window:
            self.emit_event('error_occurred', 'No frontend window available')
            return
        
        self.emit_event('dialog_requested', 'class')
        self.frontend_window._show_class_browser_dialog()
    
    def request_property_browser(self):
        """Request property browser - backend controls GUI"""
        if not self.frontend_window:
            self.emit_event('error_occurred', 'No frontend window available')
            return
        
        self.emit_event('dialog_requested', 'property')
        self.frontend_window._show_property_browser_dialog()
    
    def request_constraint_dialog(self, prop_name):
        """Request constraint dialog - backend controls GUI"""
        if not self.frontend_window:
            self.emit_event('error_occurred', 'No frontend window available')
            return
        
        self.emit_event('dialog_requested', 'constraint')
        self.frontend_window._show_constraint_dialog(prop_name)
    
    def request_load_brick_dialog(self):
        """Request load brick dialog - backend controls GUI"""
        if not self.frontend_window:
            self.emit_event('error_occurred', 'No frontend window available')
            return
        
        self.emit_event('dialog_requested', 'load_brick')
        self.frontend_window._show_load_brick_dialog()
    
    def request_ontology_browser(self, context='all', title='Browse Ontologies'):
        """Request ontology browser - backend controls GUI"""
        if not self.frontend_window:
            self.emit_event('error_occurred', 'No frontend window available')
            return
        
        self.emit_event('dialog_requested', 'ontology')
        return self.frontend_window._show_unified_ontology_browser(title, context)
    
    def _ensure_active_library(self):
        """Ensure we have an active library"""
        result = self.brick_api.get_repository_info()
        if result["status"] == "success" and not result["data"]["active_library"]:
            # Try to set default library
            libraries = result["data"]["libraries"]
            if libraries:
                default_lib = libraries[0]["name"]
                set_result = self.brick_api.set_active_library(default_lib)
                if set_result["status"] != "success":
                    print(f"Warning: Could not set active library {default_lib}: {set_result['message']}")
            else:
                print("Warning: No libraries available")
    
    def request_save_brick(self):
        """Request save operation - backend controls GUI"""
        if not self.current_brick:
            self.emit_event('error_occurred', 'No current brick to save')
            return
        
        # Sync UI to backend before saving
        if self.frontend_window:
            self.frontend_window._sync_ui_to_backend()
        
        success, message = self.save_current_brick()
        if success:
            self.emit_event('brick_saved', self.current_brick)
        else:
            self.emit_event('error_occurred', message)

