"""
Simple SHACL Brick Management Module - Truly Simple Version

This module contains the essential logic for creating, editing, and managing SHACL bricks.
It's designed to be interface-agnostic and can be used by GUI, web, or CLI interfaces.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict


@dataclass
class SHACLBrick:
    """Simple SHACL brick representation"""
    brick_id: str
    name: str
    description: str
    object_type: str  # "NodeShape" or "PropertyShape"
    target_class: str = ""  # For NodeShape
    property_path: str = ""  # For PropertyShape
    properties: Dict[str, Any] = field(default_factory=dict)
    constraints: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SHACLBrick':
        """Create from dictionary"""
        # Extract only the fields that SHACLBrick expects
        valid_fields = {
            'brick_id', 'name', 'description', 'object_type', 
            'target_class', 'property_path', 'properties', 
            'constraints', 'tags', 'created_at', 'updated_at'
        }
        
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def update_timestamp(self):
        """Update the modification timestamp"""
        self.updated_at = datetime.now().isoformat()


class BrickCore:
    """Core brick management functionality - Simple Version"""
    
    def __init__(self, repository_path: str = None, use_shared_libraries: bool = True):
        # Use shared libraries by default
        if use_shared_libraries:
            # Import shared library manager
            import sys
            shared_libs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'shared_libraries')
            if shared_libs_path not in sys.path:
                sys.path.insert(0, shared_libs_path)
            
            from library_manager import shared_library_manager
            self.repository_path = os.path.abspath(shared_library_manager.get_brick_library_path())
            self.shared_library_manager = shared_library_manager
        else:
            # Legacy behavior
            self.repository_path = os.path.abspath(repository_path or "brick_repositories_v2")
            self.shared_library_manager = None
        
        os.makedirs(self.repository_path, exist_ok=True)
        self.current_brick: Optional[SHACLBrick] = None
        self.active_library: str = "default"
        
        # Ensure default library exists
        self._ensure_library_exists("default")
    
    def _ensure_library_exists(self, library_name: str):
        """Ensure a library directory exists"""
        library_path = os.path.join(self.repository_path, library_name)
        bricks_path = os.path.join(library_path, "bricks")
        
        os.makedirs(library_path, exist_ok=True)
        os.makedirs(bricks_path, exist_ok=True)
    
    def create_brick(self, brick_type: str = "NodeShape", name: str = "") -> SHACLBrick:
        """Create a new brick"""
        brick = SHACLBrick(
            brick_id=str(uuid.uuid4()),
            name=name or f"New {brick_type}",
            description="",
            object_type=brick_type
        )
        self.current_brick = brick
        return brick
    
    def load_brick(self, brick_id: str, library_name: Optional[str] = None) -> Optional[SHACLBrick]:
        """Load a brick from storage"""
        lib_name = library_name or self.active_library
        brick_file = os.path.join(self.repository_path, lib_name, "bricks", f"{brick_id}.json")
        
        if not os.path.exists(brick_file):
            return None
        
        try:
            with open(brick_file, 'r') as f:
                data = json.load(f)
            brick = SHACLBrick.from_dict(data)
            self.current_brick = brick
            return brick
        except Exception:
            return None
    
    def save_brick(self, brick: Optional[SHACLBrick] = None) -> bool:
        """Save current brick to storage"""
        brick_to_save = brick or self.current_brick
        if not brick_to_save:
            return False
        
        # Validate brick
        if not brick_to_save.name.strip():
            return False
        
        if brick_to_save.object_type == "NodeShape" and not brick_to_save.target_class.strip():
            return False
        
        if brick_to_save.object_type == "PropertyShape" and not brick_to_save.property_path.strip():
            return False
        
        # Update timestamp
        brick_to_save.update_timestamp()
        
        # Save to file
        lib_name = self.active_library
        library_path = os.path.join(self.repository_path, lib_name, "bricks")
        brick_file = os.path.join(library_path, f"{brick_to_save.brick_id}.json")
        
        # Ensure directory exists
        os.makedirs(library_path, exist_ok=True)
        
        try:
            with open(brick_file, 'w') as f:
                json.dump(brick_to_save.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"DEBUG: Save failed with error: {e}")
            return False
    
    def get_all_bricks(self, library_name: Optional[str] = None) -> List[SHACLBrick]:
        """Get all bricks from a library"""
        lib_name = library_name or self.active_library
        bricks_dir = os.path.join(self.repository_path, lib_name, "bricks")
        
        if not os.path.exists(bricks_dir):
            return []
        
        bricks = []
        try:
            brick_files = [f for f in os.listdir(bricks_dir) if f.endswith('.json')]
                
            for brick_file in brick_files:
                brick_path = os.path.join(bricks_dir, brick_file)
                try:
                    with open(brick_path, 'r') as f:
                        data = json.load(f)
                    brick = SHACLBrick.from_dict(data)
                    bricks.append(brick)
                except Exception:
                    continue
        except Exception:
            # Return empty list on any error
            pass
        
        return bricks
    
    def delete_brick(self, brick_id: str, library_name: Optional[str] = None) -> bool:
        """Delete a brick"""
        lib_name = library_name or self.active_library
        brick_file = os.path.join(self.repository_path, lib_name, "bricks", f"{brick_id}.json")
        
        try:
            os.remove(brick_file)
            if self.current_brick and self.current_brick.brick_id == brick_id:
                self.current_brick = None
            return True
        except Exception:
            return False
    
    def update_current_brick(self, **kwargs):
        """Update current brick with new values"""
        if not self.current_brick:
            return
        
        for key, value in kwargs.items():
            if hasattr(self.current_brick, key):
                setattr(self.current_brick, key, value)
        
        self.current_brick.update_timestamp()
    
    def add_property(self, prop_name: str, prop_data: Dict[str, Any]):
        """Add a property to current brick"""
        if not self.current_brick:
            return
        
        self.current_brick.properties[prop_name] = prop_data
        self.current_brick.update_timestamp()
    
    def remove_property(self, prop_name: str):
        """Remove a property from current brick"""
        if not self.current_brick or prop_name not in self.current_brick.properties:
            return
        
        del self.current_brick.properties[prop_name]
        self.current_brick.update_timestamp()
    
    def add_constraint(self, constraint_data: Dict[str, Any]):
        """Add a constraint to current brick"""
        if not self.current_brick:
            return
        
        self.current_brick.constraints.append(constraint_data)
        self.current_brick.update_timestamp()
    
    def remove_constraint(self, index: int):
        """Remove a constraint by index"""
        if not self.current_brick or 0 <= index >= len(self.current_brick.constraints):
            return
        
        del self.current_brick.constraints[index]
        self.current_brick.update_timestamp()
    
    def get_libraries(self) -> List[str]:
        """Get list of all libraries"""
        libraries = []
        
        try:
            # Use repository path directly to avoid recursion
            if not os.path.exists(self.repository_path):
                return ["default"]
            
            for item_name in os.listdir(self.repository_path):
                item_path = os.path.join(self.repository_path, item_name)
                if os.path.isdir(item_path):
                    bricks_path = os.path.join(item_path, "bricks")
                    if os.path.exists(bricks_path):
                        libraries.append(item_name)
        except Exception as e:
            print(f"Error getting libraries: {e}")
            return ["default"]
        
        if not libraries:
            return ["default"]
        
        return sorted(libraries)
    
    def set_active_library(self, library_name: str):
        """Set the active library"""
        lib_path = os.path.join(self.repository_path, library_name, "bricks")
        if os.path.exists(lib_path):
            self.active_library = library_name
            return True
        return False
