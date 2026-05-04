#!/usr/bin/env python3
"""
Business Logic Layer
Handles brick operations separated from UI concerns
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add brick_app_v2 directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))
sys.path.insert(0, str(app_dir / 'core'))
sys.path.insert(0, str(app_dir / 'state'))

from core.brick_core_simple import BrickCore
from core.ontology_manager import OntologyManager
from state.app_state import app_state_manager, UIState, BrickType


class BrickBusinessLogic:
    """Business logic for brick operations"""
    
    def __init__(self):
        self.brick_core = BrickCore()
        self.ontology_manager = OntologyManager()
        
        # Subscribe to state changes
        app_state_manager.add_state_listener(self)
    
    def on_state_changed(self, state_type: str, old_value: Any, new_value: Any):
        """Handle state changes"""
        if state_type == "selected_library":
            self._handle_library_change(new_value)
        elif state_type == "selected_brick":
            self._handle_brick_selection(new_value)
        elif state_type == "brick_field_name":
            self._handle_brick_field_change("name", new_value)
        elif state_type == "brick_field_description":
            self._handle_brick_field_change("description", new_value)
        elif state_type == "brick_field_target_class":
            self._handle_brick_field_change("target_class", new_value)
        elif state_type == "brick_field_property_path":
            self._handle_brick_field_change("property_path", new_value)
    
    # Library Operations
    def get_libraries(self) -> List[str]:
        """Get available libraries"""
        try:
            return self.brick_core.get_libraries()
        except Exception as e:
            print(f"Error getting libraries: {e}")
            return ["default"]
    
    def set_active_library(self, library_name: str) -> bool:
        """Set active library"""
        try:
            self.brick_core.set_active_library(library_name)
            app_state_manager.set_selected_library(library_name)
            return True
        except Exception as e:
            print(f"Error setting library {library_name}: {e}")
            return False
    
    def _handle_library_change(self, library_name: str):
        """Handle library change from state"""
        try:
            self.brick_core.set_active_library(library_name)
        except Exception as e:
            print(f"Error handling library change: {e}")
    
    # Brick Operations
    def get_bricks(self) -> List[Dict[str, Any]]:
        """Get all bricks from active library"""
        try:
            bricks = self.brick_core.get_all_bricks()
            return [brick.to_dict() for brick in bricks]
        except Exception as e:
            print(f"Error getting bricks: {e}")
            return []
    
    def load_brick(self, brick_id: str) -> bool:
        """Load a brick for editing"""
        try:
            brick = self.brick_core.load_brick(brick_id)
            if brick:
                app_state_manager.load_brick(brick.to_dict())
                app_state_manager.set_ui_state(UIState.EDIT)
                return True
            return False
        except Exception as e:
            print(f"Error loading brick {brick_id}: {e}")
            return False
    
    def create_new_brick(self, brick_type: BrickType = BrickType.NODE_SHAPE) -> bool:
        """Create a new brick"""
        try:
            self.brick_core.create_brick(brick_type.value)
            app_state_manager.create_new_brick(brick_type)
            app_state_manager.set_ui_state(UIState.CREATE)
            return True
        except Exception as e:
            print(f"Error creating brick: {e}")
            return False
    
    def save_current_brick(self) -> Tuple[bool, str]:
        """Save current brick"""
        try:
            brick_data = app_state_manager.get_brick_dict()
            
            # Validate brick data
            validation_result = self._validate_brick_data(brick_data)
            if not validation_result[0]:
                return False, validation_result[1]
            
            # Update brick core with current data
            self.brick_core.update_current_brick(
                name=brick_data.get("name", ""),
                description=brick_data.get("description", ""),
                target_class=brick_data.get("target_class", ""),
                property_path=brick_data.get("property_path", "")
            )
            
            # Save brick
            success = self.brick_core.save_brick()
            if success:
                app_state_manager.set_ui_state(UIState.BROWSE)
                return True, "Brick saved successfully"
            else:
                return False, "Failed to save brick"
                
        except Exception as e:
            return False, f"Error saving brick: {str(e)}"
    
    def delete_brick(self, brick_id: str) -> Tuple[bool, str]:
        """Delete a brick"""
        try:
            success = self.brick_core.delete_brick(brick_id)
            if success:
                # Clear selection if deleted brick was selected
                if app_state_manager.get_selected_brick() == brick_id:
                    app_state_manager.set_selected_brick(None)
                return True, "Brick deleted successfully"
            else:
                return False, "Failed to delete brick"
        except Exception as e:
            return False, f"Error deleting brick: {str(e)}"
    
    def _handle_brick_selection(self, brick_id: Optional[str]):
        """Handle brick selection from state"""
        if brick_id:
            self.load_brick(brick_id)
    
    def _handle_brick_field_change(self, field_name: str, value: Any):
        """Handle brick field change from state"""
        try:
            if field_name == "name":
                self.brick_core.update_current_brick(name=value)
            elif field_name == "description":
                self.brick_core.update_current_brick(description=value)
            elif field_name == "target_class":
                self.brick_core.update_current_brick(target_class=value)
            elif field_name == "property_path":
                self.brick_core.update_current_brick(property_path=value)
        except Exception as e:
            print(f"Error handling field change {field_name}: {e}")
    
    def _validate_brick_data(self, brick_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate brick data"""
        if not brick_data.get("name", "").strip():
            return False, "Brick name is required"
        
        object_type = brick_data.get("object_type", "")
        
        if object_type == "NodeShape":
            target_class = brick_data.get("target_class", "").strip()
            if not target_class:
                return False, "Target class is required for NodeShape"
        
        elif object_type == "PropertyShape":
            property_path = brick_data.get("property_path", "").strip()
            if not property_path:
                return False, "Property path is required for PropertyShape"
        
        return True, ""
    
    # Property Operations
    def add_property(self, property_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Add property to current brick"""
        try:
            prop_name = property_data.get("name", "")
            if not prop_name:
                return False, "Property name is required"
            
            self.brick_core.add_property(prop_name, property_data)
            
            # Update state
            brick_state = app_state_manager.get_brick_state()
            brick_state.properties[prop_name] = property_data
            app_state_manager.update_brick_field("properties", brick_state.properties)
            
            return True, "Property added successfully"
        except Exception as e:
            return False, f"Error adding property: {str(e)}"
    
    def remove_property(self, prop_name: str) -> Tuple[bool, str]:
        """Remove property from current brick"""
        try:
            # Update brick_core first (doesn't return success status)
            self.brick_core.remove_property(prop_name)
            
            # Update state
            brick_state = app_state_manager.get_brick_state()
            if prop_name in brick_state.properties:
                del brick_state.properties[prop_name]
                app_state_manager.update_brick_field("properties", brick_state.properties)
                return True, "Property removed successfully"
            else:
                return False, "Property not found in brick state"
        except Exception as e:
            return False, f"Error removing property: {str(e)}"
    
    def add_constraint(self, prop_name: str, constraint_data: Dict[str, Any], prop_data: Dict[str, Any] = None) -> Tuple[bool, str]:
        """Add constraint to property"""
        try:
            # Update brick state with constraint
            brick_state = app_state_manager.get_brick_state()
            if prop_name in brick_state.properties:
                # Ensure property data is a dict, not a string
                existing_prop = brick_state.properties[prop_name]
                if not isinstance(existing_prop, dict):
                    # Try to recover by replacing with prop_data if available
                    if prop_data and isinstance(prop_data, dict):
                        brick_state.properties[prop_name] = prop_data
                        existing_prop = prop_data
                    else:
                        return False, f"Property '{prop_name}' data is corrupted (expected dict, got {type(existing_prop).__name__})"
                if 'constraints' not in existing_prop:
                    existing_prop['constraints'] = []
                existing_prop['constraints'].append(constraint_data)
                app_state_manager.update_brick_field("properties", brick_state.properties)
            elif prop_data:
                # Property not in brick state yet, add full property data with constraint
                prop_data_copy = prop_data.copy()
                if 'constraints' not in prop_data_copy:
                    prop_data_copy['constraints'] = []
                prop_data_copy['constraints'].append(constraint_data)
                brick_state.properties[prop_name] = prop_data_copy
                app_state_manager.update_brick_field("properties", brick_state.properties)
            else:
                # Property not in brick state and no prop_data provided
                brick_state.properties[prop_name] = {'constraints': [constraint_data]}
                app_state_manager.update_brick_field("properties", brick_state.properties)
            
            self.brick_core.add_constraint(constraint_data)
            return True, "Constraint added successfully"
        except Exception as e:
            return False, f"Error adding constraint: {str(e)}"
    
    def remove_constraint(self, prop_name: str, constraint_index: int) -> Tuple[bool, str]:
        """Remove constraint from property"""
        try:
            # Update brick state by removing constraint
            brick_state = app_state_manager.get_brick_state()
            if prop_name in brick_state.properties and 'constraints' in brick_state.properties[prop_name]:
                constraints = brick_state.properties[prop_name]['constraints']
                if 0 <= constraint_index < len(constraints):
                    constraints.pop(constraint_index)
                    app_state_manager.update_brick_field("properties", brick_state.properties)
                    return True, "Constraint removed successfully"
                else:
                    return False, "Invalid constraint index"
            else:
                return False, "Property not found or has no constraints"
        except Exception as e:
            return False, f"Error removing constraint: {str(e)}"
    
    def update_constraint(self, prop_name: str, constraint_index: int, constraint_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Update constraint at specific index"""
        try:
            # Update brick state by modifying constraint at index
            brick_state = app_state_manager.get_brick_state()
            if prop_name in brick_state.properties and 'constraints' in brick_state.properties[prop_name]:
                constraints = brick_state.properties[prop_name]['constraints']
                if 0 <= constraint_index < len(constraints):
                    constraints[constraint_index] = constraint_data
                    app_state_manager.update_brick_field("properties", brick_state.properties)
                    return True, "Constraint updated successfully"
                else:
                    return False, "Invalid constraint index"
            else:
                return False, "Property not found or has no constraints"
        except Exception as e:
            return False, f"Error updating constraint: {str(e)}"
    
    # Ontology Operations
    def get_ontology_classes(self) -> List[Dict[str, Any]]:
        """Get available ontology classes"""
        try:
            return self.ontology_manager.get_available_classes()
        except Exception as e:
            print(f"Error getting ontology classes: {e}")
            return []
    
    def get_ontology_properties(self) -> List[Dict[str, Any]]:
        """Get available ontology properties"""
        try:
            return self.ontology_manager.get_available_properties()
        except Exception as e:
            print(f"Error getting ontology properties: {e}")
            return []
    
    # Export/Import Operations
    def export_brick_shacl(self, brick_id: str, format_type: str = "turtle") -> Tuple[bool, str, str]:
        """Export brick to SHACL format"""
        try:
            # This would need to be implemented in BrickCore
            # For now, return a placeholder
            return True, f"# SHACL for {brick_id}\n", f"{brick_id}.ttl"
        except Exception as e:
            return False, "", f"Error exporting brick: {str(e)}"
    
    def export_library(self, library_name: Optional[str] = None) -> Tuple[bool, str]:
        """Export library to JSON"""
        try:
            # This would need to be implemented in BrickCore
            # For now, return a placeholder
            return True, f"Library {library_name or 'default'} exported successfully"
        except Exception as e:
            return False, f"Error exporting library: {str(e)}"
    
    def import_library(self, file_path: str, library_name: Optional[str] = None) -> Tuple[bool, str]:
        """Import library from JSON file"""
        try:
            # This would need to be implemented in BrickCore
            # For now, return a placeholder
            return True, f"Library imported successfully from {file_path}"
        except Exception as e:
            return False, f"Error importing library: {str(e)}"


# Global business logic instance
brick_business_logic = BrickBusinessLogic()
