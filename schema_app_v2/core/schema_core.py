"""
Schema Core Module
Simple schema composition and management following brick_app_v2 architecture
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict


@dataclass
class Schema:
    """Simple schema representation"""
    schema_id: str
    name: str
    description: str
    root_brick_id: str
    component_brick_ids: List[str]
    flow_config: Optional['FlowConfig'] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Handle flow_config serialization
        if self.flow_config:
            data['flow_config'] = self.flow_config.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schema':
        """Create from dictionary"""
        # Handle flow_config deserialization
        if data.get('flow_config'):
            from .flow_engine import FlowConfig
            data['flow_config'] = FlowConfig.from_dict(data['flow_config'])
        return cls(**data)
    
    def update_timestamp(self):
        """Update the modification timestamp"""
        self.updated_at = datetime.now().isoformat()


class SchemaCore:
    """Core schema management functionality - Simple Version"""
    
    def __init__(self, repository_path: str = None, use_shared_libraries: bool = True):
        # Use shared libraries by default
        if use_shared_libraries:
            # Import shared library manager
            import sys
            shared_libs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'shared_libraries')
            if shared_libs_path not in sys.path:
                sys.path.insert(0, shared_libs_path)
            
            from library_manager import shared_library_manager
            self.repository_path = os.path.abspath(shared_library_manager.get_schema_library_path())
            self.shared_library_manager = shared_library_manager
        else:
            # Legacy behavior
            self.repository_path = os.path.abspath(repository_path or "schema_repositories")
            self.shared_library_manager = None
        
        os.makedirs(self.repository_path, exist_ok=True)
        self.current_schema: Optional[Schema] = None
        self.active_library: str = "default"
        
        # Ensure default library exists
        self._ensure_library_exists("default")
    
    def _ensure_library_exists(self, library_name: str):
        """Ensure a library directory exists"""
        library_path = os.path.join(self.repository_path, library_name)
        schemas_path = os.path.join(library_path, "schemas")
        
        os.makedirs(library_path, exist_ok=True)
        os.makedirs(schemas_path, exist_ok=True)
    
    def create_schema(self, name: str, description: str = "", root_brick_id: str = "") -> Schema:
        """Create a new schema"""
        schema = Schema(
            schema_id=str(uuid.uuid4()),
            name=name,
            description=description,
            root_brick_id=root_brick_id,
            component_brick_ids=[]
        )
        self.current_schema = schema
        return schema
    
    def load_schema(self, schema_id: str, library_name: Optional[str] = None) -> Optional[Schema]:
        """Load a schema from storage"""
        lib_name = library_name or self.active_library
        schema_file = os.path.join(self.repository_path, lib_name, "schemas", f"{schema_id}.json")
        
        if not os.path.exists(schema_file):
            return None
        
        try:
            with open(schema_file, 'r') as f:
                data = json.load(f)
            schema = Schema.from_dict(data)
            self.current_schema = schema
            return schema
        except Exception:
            return None
    
    def save_schema(self, schema: Optional[Schema] = None) -> bool:
        """Save current schema to storage"""
        schema_to_save = schema or self.current_schema
        if not schema_to_save:
            return False
        
        # Validate schema
        if not schema_to_save.name.strip():
            return False
        
        if not schema_to_save.root_brick_id.strip():
            return False
        
        # Update timestamp
        schema_to_save.update_timestamp()
        
        # Save to file
        lib_name = self.active_library
        schemas_path = os.path.join(self.repository_path, lib_name, "schemas")
        schema_file = os.path.join(schemas_path, f"{schema_to_save.schema_id}.json")
        
        # Ensure directory exists
        os.makedirs(schemas_path, exist_ok=True)
        
        try:
            with open(schema_file, 'w') as f:
                json.dump(schema_to_save.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"DEBUG: Save failed with error: {e}")
            return False
    
    def get_all_schemas(self, library_name: Optional[str] = None) -> List[Schema]:
        """Get all schemas from a library"""
        lib_name = library_name or self.active_library
        schemas_dir = os.path.join(self.repository_path, lib_name, "schemas")
        
        if not os.path.exists(schemas_dir):
            return []
        
        schemas = []
        try:
            schema_files = [f for f in os.listdir(schemas_dir) if f.endswith('.json')]
                
            for schema_file in schema_files:
                schema_path = os.path.join(schemas_dir, schema_file)
                try:
                    with open(schema_path, 'r') as f:
                        data = json.load(f)
                    schema = Schema.from_dict(data)
                    schemas.append(schema)
                except Exception as e:
                    print(f"DEBUG: Failed to load schema {schema_file}: {e}")
                    continue
        except Exception as e:
            print(f"DEBUG: Failed to list schemas: {e}")
        
        return sorted(schemas, key=lambda s: s.updated_at, reverse=True)
    
    def delete_schema(self, schema_id: str, library_name: Optional[str] = None) -> bool:
        """Delete a schema"""
        lib_name = library_name or self.active_library
        schema_file = os.path.join(self.repository_path, lib_name, "schemas", f"{schema_id}.json")
        
        try:
            if os.path.exists(schema_file):
                os.remove(schema_file)
                return True
        except Exception as e:
            print(f"DEBUG: Delete failed with error: {e}")
        
        return False
    
    def add_component_brick(self, brick_id: str) -> bool:
        """Add a component brick to current schema"""
        if not self.current_schema:
            return False
        
        if brick_id not in self.current_schema.component_brick_ids:
            self.current_schema.component_brick_ids.append(brick_id)
            self.current_schema.update_timestamp()
        
        return True
    
    def remove_component_brick(self, brick_id: str) -> bool:
        """Remove a component brick from current schema"""
        if not self.current_schema:
            return False
        
        if brick_id in self.current_schema.component_brick_ids:
            self.current_schema.component_brick_ids.remove(brick_id)
            self.current_schema.update_timestamp()
        
        return True
    
    def get_libraries(self) -> List[str]:
        """Get all available libraries"""
        try:
            libraries = [d for d in os.listdir(self.repository_path) 
                        if os.path.isdir(os.path.join(self.repository_path, d))]
            return sorted(libraries)
        except Exception:
            return []
    
    def create_library(self, library_name: str) -> bool:
        """Create a new library"""
        if not library_name.strip():
            return False
        
        self._ensure_library_exists(library_name)
        return True
    
    def set_active_library(self, library_name: str) -> bool:
        """Set the active library"""
        libraries = self.get_libraries()
        if library_name in libraries:
            self.active_library = library_name
            return True
        return False
