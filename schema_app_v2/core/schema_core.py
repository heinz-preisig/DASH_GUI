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
    inheritance_chain: List[str] = field(default_factory=list)  # Parent schema IDs
    relationships: Dict[str, List[str]] = field(default_factory=dict)  # Brick relationships
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
    
    def add_child_component(self, parent_brick_id: str, child_brick_id: str):
        """Add a child component to a parent"""
        if parent_brick_id not in self.relationships:
            self.relationships[parent_brick_id] = []
        if child_brick_id not in self.relationships[parent_brick_id]:
            self.relationships[parent_brick_id].append(child_brick_id)
    
    def remove_child_component(self, parent_brick_id: str, child_brick_id: str):
        """Remove a child component from a parent"""
        if parent_brick_id in self.relationships:
            if child_brick_id in self.relationships[parent_brick_id]:
                self.relationships[parent_brick_id].remove(child_brick_id)
    
    def get_children(self, parent_brick_id: str) -> List[str]:
        """Get all children of a parent brick"""
        return self.relationships.get(parent_brick_id, [])
    
    def get_parent(self, child_brick_id: str) -> Optional[str]:
        """Get the parent of a child brick"""
        for parent_id, children in self.relationships.items():
            if child_brick_id in children:
                return parent_id
        return None
    
    def get_root_components(self) -> List[str]:
        """Get components with no parent (top-level)"""
        all_children = set()
        for children in self.relationships.values():
            all_children.update(children)
        root_components = []
        for brick_id in self.component_brick_ids:
            if brick_id not in all_children:
                root_components.append(brick_id)
        return root_components


@dataclass
class DaisyChain:
    """Daisy-chain configuration for multi-step interfaces"""
    chain_id: str
    name: str
    description: str
    schema_ids: List[str]  # Schema IDs in chain order
    navigation_rules: Dict[str, Any] = field(default_factory=dict)
    shared_data: Dict[str, Any] = field(default_factory=dict)  # Data shared between steps
    conditional_logic: Dict[str, Any] = field(default_factory=dict)
    ui_theme: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DaisyChain':
        """Create from dictionary"""
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
        self.daisy_chains: Dict[str, DaisyChain] = {}  # Store daisy chains
        
        # Ensure default library exists
        self._ensure_library_exists("default")
    
    def _ensure_library_exists(self, library_name: str):
        """Ensure a library directory exists"""
        library_path = os.path.join(self.repository_path, library_name)
        os.makedirs(library_path, exist_ok=True)
    
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
        schemas_dir = os.path.join(self.repository_path, lib_name)
        
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
    
    def extend_schema(self, parent_schema_id: str, name: str, description: str,
                     additional_brick_ids: List[str], brick_integration=None) -> Optional[Schema]:
        """Create a schema that extends an existing one"""
        # Load parent schema
        parent_schema = self.load_schema(parent_schema_id)
        if not parent_schema:
            return None
        
        # Combine parent and new bricks
        all_brick_ids = [parent_schema.root_brick_id] + parent_schema.component_brick_ids + additional_brick_ids
        
        # Create extended schema
        schema = Schema(
            schema_id=str(uuid.uuid4()),
            name=name,
            description=description,
            root_brick_id=parent_schema.root_brick_id,
            component_brick_ids=parent_schema.component_brick_ids + additional_brick_ids,
            inheritance_chain=[parent_schema_id] + parent_schema.inheritance_chain,
            flow_config=parent_schema.flow_config
        )
        
        # Analyze brick relationships if brick_integration is provided
        if brick_integration:
            schema.relationships = self._analyze_brick_relationships(
                schema.root_brick_id,
                schema.component_brick_ids,
                brick_integration
            )
        
        self.current_schema = schema
        return schema
    
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
    
    def create_daisy_chain(self, name: str, description: str, schema_ids: List[str],
                         navigation_rules: Dict[str, Any] = None) -> Optional[DaisyChain]:
        """Create a daisy-chain of schemas for multi-step interfaces"""
        # Validate schemas exist
        for schema_id in schema_ids:
            schema = self.load_schema(schema_id)
            if not schema:
                return None
        
        chain_id = str(uuid.uuid4())
        
        daisy_chain = DaisyChain(
            chain_id=chain_id,
            name=name,
            description=description,
            schema_ids=schema_ids,
            navigation_rules=navigation_rules or {}
        )
        
        self.daisy_chains[chain_id] = daisy_chain
        return daisy_chain
    
    def get_daisy_chain(self, chain_id: str) -> Optional[DaisyChain]:
        """Get daisy chain by ID"""
        return self.daisy_chains.get(chain_id)
    
    def get_all_daisy_chains(self) -> List[DaisyChain]:
        """Get all daisy chains"""
        return list(self.daisy_chains.values())
    
    def delete_daisy_chain(self, chain_id: str) -> bool:
        """Delete a daisy chain"""
        if chain_id in self.daisy_chains:
            del self.daisy_chains[chain_id]
            return True
        return False
    
    def _analyze_brick_relationships(self, root_brick_id: str, component_brick_ids: List[str],
                                    brick_integration) -> Dict[str, List[str]]:
        """Analyze relationships between bricks"""
        relationships = {}
        
        # Get root brick details
        root_brick = brick_integration.get_brick_by_id(root_brick_id)
        if not root_brick:
            return relationships
        
        # Analyze component bricks
        for brick_id in component_brick_ids:
            comp_brick = brick_integration.get_brick_by_id(brick_id)
            if comp_brick:
                # Determine relationship type based on object_type
                if hasattr(comp_brick, 'object_type'):
                    if comp_brick.object_type == "PropertyShape":
                        relationships[brick_id] = ["property_of", root_brick_id]
                    else:
                        relationships[brick_id] = ["related_to", root_brick_id]
                else:
                    relationships[brick_id] = ["related_to", root_brick_id]
        
        return relationships
