#!/usr/bin/env python3
"""
Simplified Brick Service - No Global State Dependencies
Returns data/results, doesn't manage UI state
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# Add paths
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))
sys.path.insert(0, str(app_dir / 'core'))

from core.brick_core_simple import BrickCore, SHACLBrick
from core.ontology_manager import OntologyManager


@dataclass
class OperationResult:
    """Result from service operations"""
    success: bool
    message: str = ""
    data: Any = None


class BrickService:
    """Service layer - pure business logic, no UI state management"""
    
    def __init__(self):
        self.brick_core = BrickCore()
        self.ontology_manager = OntologyManager()
    
    # Library Operations
    def get_libraries(self) -> List[str]:
        return self.brick_core.get_libraries()
    
    def set_active_library(self, library_name: str) -> bool:
        try:
            self.brick_core.set_active_library(library_name)
            return True
        except Exception as e:
            print(f"Error setting library: {e}")
            return False
    
    def create_library(self, name: str, description: str = "") -> OperationResult:
        try:
            self.brick_core.shared_library_manager.create_library(
                lib_type="bricks", name=name, description=description
            )
            return OperationResult(success=True, message=f"Library '{name}' created")
        except Exception as e:
            return OperationResult(success=False, message=str(e))
    
    def delete_library(self, name: str) -> OperationResult:
        """Delete library by archiving to ZIP"""
        try:
            success = self.brick_core.delete_library(name)
            if success:
                return OperationResult(success=True, message=f"Library '{name}' archived as ZIP")
            return OperationResult(success=False, message="Failed to delete library")
        except Exception as e:
            return OperationResult(success=False, message=str(e))
    
    def list_archived_libraries(self) -> List[Dict[str, Any]]:
        """List all archived libraries"""
        return self.brick_core.list_archived_libraries()
    
    def restore_library(self, archive_name: str) -> OperationResult:
        """Restore an archived library with auto-versioning"""
        try:
            success, message, restored_name = self.brick_core.restore_library(archive_name)
            return OperationResult(success=success, message=message, data=restored_name)
        except Exception as e:
            return OperationResult(success=False, message=str(e))

    def copy_library(self, source_name: str, target_name: str) -> OperationResult:
        """Copy a library with a new name"""
        try:
            success, message = self.brick_core.copy_library(source_name, target_name)
            return OperationResult(success=success, message=message, data=target_name if success else None)
        except Exception as e:
            return OperationResult(success=False, message=str(e))
    
    # Brick Operations
    def get_bricks(self) -> List[Dict[str, Any]]:
        """Get all bricks as dictionaries"""
        try:
            bricks = self.brick_core.get_all_bricks()
            return [brick.to_dict() for brick in bricks]
        except Exception as e:
            print(f"Error getting bricks: {e}")
            return []
    
    def load_brick(self, brick_id: str) -> Optional[Dict[str, Any]]:
        """Load a brick by ID, return as dictionary or None"""
        try:
            brick = self.brick_core.load_brick(brick_id)
            if brick:
                return brick.to_dict()
            return None
        except Exception as e:
            print(f"Error loading brick {brick_id}: {e}")
            return None
    
    def create_brick(self, brick_type: str = "NodeShape") -> Dict[str, Any]:
        """Create a new brick, return initial data"""
        try:
            self.brick_core.create_brick(brick_type)
            if self.brick_core.current_brick:
                return self.brick_core.current_brick.to_dict()
            return {"object_type": brick_type, "name": f"New {brick_type}"}
        except Exception as e:
            print(f"Error creating brick: {e}")
            return {"object_type": brick_type, "name": f"New {brick_type}"}
    
    def save_brick(self, brick_data: Dict[str, Any]) -> OperationResult:
        """Save brick data"""
        try:
            # Validate
            if not brick_data.get("name", "").strip():
                return OperationResult(success=False, message="Brick name is required")
            
            object_type = brick_data.get("object_type", "")
            if object_type == "PropertyShape" and not brick_data.get("property_path", "").strip():
                return OperationResult(success=False, message="Property path is required for PropertyShape")
            
            # Update core with current data
            self.brick_core.update_current_brick(
                name=brick_data.get("name", ""),
                description=brick_data.get("description", ""),
                object_type=object_type,
                target_class=brick_data.get("target_class", ""),
                property_path=brick_data.get("property_path", ""),
                properties=brick_data.get("properties", {})
            )
            
            # Save
            if self.brick_core.save_brick():
                return OperationResult(success=True, message="Brick saved successfully")
            return OperationResult(success=False, message="Failed to save brick")
            
        except Exception as e:
            return OperationResult(success=False, message=f"Error: {str(e)}")
    
    def delete_brick(self, brick_id: str) -> OperationResult:
        """Delete a brick by ID"""
        try:
            success = self.brick_core.delete_brick(brick_id)
            if success:
                return OperationResult(success=True, message="Brick deleted successfully")
            return OperationResult(success=False, message="Failed to delete brick")
        except Exception as e:
            return OperationResult(success=False, message=f"Error: {str(e)}")
    
    # Property Operations
    def add_property(self, brick_id: str, property_data: Dict[str, Any]) -> OperationResult:
        """Add property to a brick"""
        try:
            # Load brick if needed
            if not self.brick_core.current_brick or self.brick_core.current_brick.brick_id != brick_id:
                self.brick_core.load_brick(brick_id)
            
            prop_name = property_data.get("name", "")
            if not prop_name:
                return OperationResult(success=False, message="Property name is required")
            
            self.brick_core.add_property(prop_name, property_data)
            return OperationResult(success=True, message=f"Property '{prop_name}' added")
        except Exception as e:
            return OperationResult(success=False, message=str(e))
    
    def remove_property(self, brick_id: str, prop_name: str) -> OperationResult:
        """Remove property from a brick"""
        try:
            if not self.brick_core.current_brick or self.brick_core.current_brick.brick_id != brick_id:
                self.brick_core.load_brick(brick_id)
            
            self.brick_core.remove_property(prop_name)
            return OperationResult(success=True, message=f"Property '{prop_name}' removed")
        except Exception as e:
            return OperationResult(success=False, message=str(e))
    
    # Ontology Operations
    def get_ontology_classes(self) -> List[Dict[str, Any]]:
        return self.ontology_manager.get_available_classes()
    
    def get_ontology_properties(self) -> List[Dict[str, Any]]:
        return self.ontology_manager.get_available_properties()


# Global instance for convenience
brick_service = BrickService()
