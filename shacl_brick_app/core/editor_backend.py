#!/usr/bin/env python3
"""
Editor Backend - Business logic for brick editing
Separates frontend concerns from business logic
"""

from typing import Dict, List, Any, Optional, Tuple, Callable
import uuid
import os
import json
from .brick_backend import BrickBackendAPI
from rdflib import Graph, Namespace, URIRef, RDF, RDFS, OWL

class BrickEditorBackend:
    """Backend logic for brick editing operations"""
    
    def __init__(self, brick_api: BrickBackendAPI):
        self.brick_api = brick_api
        self.current_brick = None  # Will be set when create_new_brick is called
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
    
    def create_new_brick(self, brick_type: str = "NodeShape") -> Dict[str, Any]:
        """Create a new brick and set as current"""
        self.current_brick = {
            "brick_id": str(uuid.uuid4()),
            "name": "",
            "object_type": brick_type,
            "target_class": "",
            "description": "",
            "properties": {},
            "constraints": [],
            "metadata": {}
        }
        self.emit_event('brick_created', self.current_brick)
        return self.current_brick
    
    def get_current_brick(self) -> Dict[str, Any]:
        """Get current brick data"""
        if self.current_brick is None:
            return {}
        return self.current_brick.copy()
    
    def set_current_brick(self, brick_data: Dict[str, Any]):
        """Set current brick and emit update event"""
        self.current_brick = brick_data
        self.emit_event('brick_updated', self.current_brick)
    
    def update_brick_field(self, field_name: str, value: Any):
        """Update a specific field in current brick"""
        if field_name in self.current_brick:
            self.current_brick[field_name] = value
            self.emit_event('brick_updated', self.current_brick)
        else:
            self.emit_event('error_occurred', f"Unknown field: {field_name}")
    
    def set_target_class(self, class_uri: str):
        """Set target class for current brick"""
        self.current_brick["target_class"] = class_uri
        self.emit_event('target_class_set', class_uri)
        self.emit_event('brick_updated', self.current_brick)
    
    def add_property_to_current_brick(self, property_data: Dict[str, Any]) -> bool:
        """Add property to current brick"""
        if not self.current_brick:
            self.emit_event('error_occurred', "No current brick")
            return False
        
        # Ensure properties dictionary exists
        if "properties" not in self.current_brick:
            self.current_brick["properties"] = {}
        
        prop_name = property_data["name"]
        self.current_brick["properties"][prop_name] = property_data
        self.emit_event('property_added', prop_name, property_data)
        self.emit_event('brick_updated', self.current_brick)
        return True
    
    def remove_property_from_current_brick(self, prop_name: str) -> bool:
        """Remove property from current brick"""
        if not self.current_brick:
            self.emit_event('error_occurred', "No current brick")
            return False
        
        # Ensure properties dictionary exists
        if "properties" not in self.current_brick:
            self.emit_event('error_occurred', "No properties to remove from")
            return False
        
        if prop_name in self.current_brick["properties"]:
            del self.current_brick["properties"][prop_name]
            self.emit_event('property_removed', prop_name)
            self.emit_event('brick_updated', self.current_brick)
            return True
        return False
    
    def add_constraint_to_property(self, prop_name: str, constraint_data: Dict[str, Any]) -> bool:
        """Add constraint to property in current brick"""
        if not self.current_brick:
            self.emit_event('error_occurred', "No current brick")
            return False
        
        if prop_name not in self.current_brick["properties"]:
            self.emit_event('error_occurred', f"Property '{prop_name}' not found")
            return False
        
        prop_data = self.current_brick["properties"][prop_name]
        
        # Handle both dictionary and string property data
        if isinstance(prop_data, str):
            # Convert string property to dictionary to support constraints
            self.current_brick["properties"][prop_name] = {
                "value": prop_data,
                "constraints": []
            }
        elif isinstance(prop_data, dict):
            if "constraints" not in prop_data:
                prop_data["constraints"] = []
        else:
            self.emit_event('error_occurred', f"Property '{prop_name}' has invalid data type")
            return False
        
        self.current_brick["properties"][prop_name]["constraints"].append(constraint_data)
        self.emit_event('constraint_added', prop_name, constraint_data)
        self.emit_event('brick_updated', self.current_brick)
        return True
    
    def remove_constraint_from_property(self, prop_name: str, constraint_index: int) -> bool:
        """Remove constraint from property in current brick"""
        if not self.current_brick:
            self.emit_event('error_occurred', "No current brick")
            return False
        
        if prop_name not in self.current_brick["properties"]:
            self.emit_event('error_occurred', f"Property '{prop_name}' not found")
            return False
        
        prop_data = self.current_brick["properties"][prop_name]
        
        # Handle both dictionary and string property data
        if isinstance(prop_data, dict):
            constraints = prop_data.get("constraints", [])
            if 0 <= constraint_index < len(constraints):
                del constraints[constraint_index]
                self.emit_event('constraint_removed', prop_name)
                self.emit_event('brick_updated', self.current_brick)
        else:
            self.emit_event('error_occurred', f"Property '{prop_name}' has no constraints to remove")
            return False
    
    def load_brick(self, brick_id: str) -> Optional[Dict[str, Any]]:
        """Load existing brick from backend"""
        result = self.brick_api.get_brick_details(brick_id)
        if result["status"] == "success":
            self.current_brick = result["data"]
            return self.current_brick
        return None
    
    def save_current_brick(self) -> Tuple[bool, str]:
        """Save current brick to backend"""
        if not self.current_brick:
            return False, "No current brick to save"
        
        try:
            # Validate brick data
            validation_result = self.validate_brick(self.current_brick)
            if not validation_result[0]:
                return False, validation_result[1]
            
            # Update or create brick
            if "brick_id" in self.current_brick and self.current_brick["brick_id"]:
                result = self.brick_api.update_brick(self.current_brick["brick_id"], self.current_brick)
            else:
                # Create new brick
                self.current_brick["brick_id"] = str(uuid.uuid4())
                result = self.brick_api.create_nodeshape_brick(
                    self.current_brick["brick_id"],
                    self.current_brick["name"],
                    self.current_brick["description"],
                    self.current_brick.get("target_class"),
                    self.current_brick.get("properties", {}),
                    self.current_brick.get("constraints", []),
                    self.current_brick.get("tags", [])
                )
            
            if result["status"] == "success":
                self.current_brick = result["data"]
                self.emit_event('brick_saved', self.current_brick)
                self.emit_event('brick_updated', self.current_brick)
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
            # NodeShape requires targets with TargetClass
            targets = brick_data.get("targets", [])
            if not targets:
                return False, "Targets are required for NodeShape"
            
            # Check if any target has TargetClass type
            has_target_class = any(
                target.get("target_type") == "TargetClass" and target.get("value", "").strip()
                for target in targets
            )
            if not has_target_class:
                return False, "TargetClass is required for NodeShape"
                
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

# Real OntologyManager class that loads cached ontologies
class OntologyManager:
    def __init__(self):
        self.ontologies = {}
        self.cache_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'ontologies', 'cache')
        self.load_cached_ontologies()
    
    def load_cached_ontologies(self):
        """Load cached ontologies from the cache directory"""
        if not os.path.exists(self.cache_dir):
            print(f"Cache directory not found: {self.cache_dir}")
            return
        
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(('.ttl', '.rdf')):
                    filepath = os.path.join(self.cache_dir, filename)
                    ontology_name = filename.replace('.ttl', '').replace('.rdf', '')
                    
                    # Parse RDF/TTL file
                    graph = Graph()
                    graph.parse(filepath, format='turtle' if filename.endswith('.ttl') else 'xml')
                    
                    # Extract classes and properties
                    classes = []
                    properties = []
                    
                    # Get classes
                    for class_uri in graph.subjects(RDF.type, OWL.Class):
                        if isinstance(class_uri, URIRef):
                            class_name = str(class_uri).split('/')[-1].split('#')[-1]
                            classes.append({
                                'name': class_name,
                                'uri': str(class_uri)
                            })
                    
                    # Get properties
                    for prop_uri in graph.subjects(RDF.type, OWL.ObjectProperty):
                        if isinstance(prop_uri, URIRef):
                            prop_name = str(prop_uri).split('/')[-1].split('#')[-1]
                            properties.append({
                                'name': prop_name,
                                'uri': str(prop_uri)
                            })
                    
                    for prop_uri in graph.subjects(RDF.type, OWL.DatatypeProperty):
                        if isinstance(prop_uri, URIRef):
                            prop_name = str(prop_uri).split('/')[-1].split('#')[-1]
                            properties.append({
                                'name': prop_name,
                                'uri': str(prop_uri)
                            })
                    
                    self.ontologies[ontology_name] = {
                        'classes': classes,
                        'properties': properties,
                        'name': ontology_name,
                        'uri': filepath
                    }
                    
                    print(f"Loaded ontology: {ontology_name} ({len(classes)} classes, {len(properties)} properties)")
                    
        except Exception as e:
            print(f"Error loading cached ontologies: {e}")
            import traceback
            traceback.print_exc()
    
    def get_available_classes(self):
        """Get all available classes from all ontologies"""
        classes = []
        for ontology_data in self.ontologies.values():
            classes.extend(ontology_data.get('classes', []))
        return classes
    
    def get_available_properties(self):
        """Get all available properties from all ontologies"""
        properties = []
        for ontology_data in self.ontologies.values():
            properties.extend(ontology_data.get('properties', []))
        return properties
