"""
Brick Editor Backend - Stub file for compatibility.
The main editor functionality has been refactored into brick_core_simple.py.
This file exists for backward compatibility with session_manager.py.
"""

from typing import Dict, Any, List, Optional, Tuple
from .brick_core_simple import BrickCore


class BrickEditorBackend:
    """
    Editor backend that wraps BrickCore for compatibility with session_manager.py.
    Provides property-level constraint management.
    """
    
    def __init__(self, brick_api_or_path=None):
        # Handle different initialization patterns
        if brick_api_or_path is None:
            repository_path = "brick_repositories"
        elif isinstance(brick_api_or_path, str):
            repository_path = brick_api_or_path
        else:
            # It's a BrickBackendAPI instance - extract the core
            repository_path = getattr(brick_api_or_path, 'repository_path', 'brick_repositories')
        
        self.core = BrickCore(repository_path)
        self.repository_path = repository_path
    
    def __getattr__(self, name):
        """Delegate unknown attributes to core"""
        return getattr(self.core, name)
    
    def register_event_handler(self, event_type: str, handler):
        """Register an event handler - stub for compatibility with session_manager.py"""
        # Event handling is managed by the multi-tenant backend
        # This method exists for API compatibility
        pass
    
    def add_constraint_to_property(self, prop_name: str, constraint_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Add constraint to a specific property"""
        return self.core.add_constraint_to_property(prop_name, constraint_data)
    
    def update_constraint_on_property(self, prop_name: str, index: int, constraint_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Update constraint at specific index on a property"""
        return self.core.update_constraint_on_property(prop_name, index, constraint_data)
    
    def remove_constraint_from_property(self, prop_name: str, index: int) -> Tuple[bool, str]:
        """Remove constraint at specific index from a property"""
        return self.core.remove_constraint_from_property(prop_name, index)
    
    def add_property(self, prop_name: str, prop_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Add a property to the current brick"""
        try:
            self.core.add_property(prop_name, prop_data)
            return True, "Property added successfully"
        except Exception as e:
            return False, str(e)
    
    def remove_property(self, prop_name: str) -> Tuple[bool, str]:
        """Remove a property from the current brick"""
        try:
            self.core.remove_property(prop_name)
            return True, "Property removed successfully"
        except Exception as e:
            return False, str(e)
    
    def set_brick_target_class(self, target_class: str) -> Tuple[bool, str]:
        """Set the target class for the current brick"""
        try:
            self.core.set_target_class(target_class)
            return True, "Target class set successfully"
        except Exception as e:
            return False, str(e)
    
    def save_current_brick(self) -> Tuple[bool, str]:
        """Save the current brick"""
        return self.core.save_current_brick()
    
    def get_current_brick(self) -> Optional[Dict[str, Any]]:
        """Get the current brick as a dictionary"""
        brick = self.core.get_current_brick()
        if brick:
            return brick.to_dict()
        return None
