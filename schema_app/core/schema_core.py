"""
Schema Core Module
Simple schema composition and management following brick_app architecture
"""

import json
import os
import sys
import uuid
from pathlib import Path as _Path
_dash_gui_root = str(_Path(__file__).parent.parent.parent)
if _dash_gui_root not in sys.path:
    sys.path.insert(0, _dash_gui_root)
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict


@dataclass
class UIMetadata:
    """UI-specific metadata for schema components"""
    sequence: int = 0  # Order in UI
    group_id: Optional[str] = None  # Group membership
    parent_id: Optional[str] = None  # Parent component for nesting
    label: str = ""  # UI label (can differ from name)
    help_text: str = ""  # Help text for UI
    is_collapsible: bool = True  # Can be collapsed in tree view
    is_visible: bool = True  # Visibility in UI

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UIMetadata':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class SchemaEdge:
    """Explicit directed edge in the schema tree: parent brick -> child brick.
    Carries the SHACL path used in sh:property [sh:path ...; sh:node ...] blocks,
    plus UI metadata (label, sequence, cardinality, etc.).
    """
    child_brick_id: str
    path_iri: str  # sh:path IRI for this edge
    label: str = ""  # rdfs:label on the sh:property block
    parent_brick_id: Optional[str] = None  # None = root-level edge
    min_count: int = 1
    max_count: Optional[int] = 1
    collapsible: bool = True
    description: str = ""
    sequence: int = 0  # sh:order

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SchemaEdge':
        """Create from dictionary"""
        return cls(**data)


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
    relationships: Dict[str, List[str]] = field(default_factory=dict)  # Legacy brick relationships (parent -> children)
    edges: List[SchemaEdge] = field(default_factory=list)  # Rich edge relationships with path, cardinality, metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    component_ui_metadata: Dict[str, UIMetadata] = field(default_factory=dict)  # UI metadata per component
    groups: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # UI groups (id -> {label, description, sequence})
    schema_refs: List[Dict[str, Any]] = field(default_factory=list)  # Referenced schemas [{schema_id, attach_to_brick_id, property_path, label}]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Handle flow_config serialization
        if self.flow_config:
            data['flow_config'] = self.flow_config.to_dict()
        # Handle UIMetadata serialization
        data['component_ui_metadata'] = {
            k: v.to_dict() for k, v in self.component_ui_metadata.items()
        }
        # Handle SchemaEdge serialization
        data['edges'] = [edge.to_dict() for edge in self.edges]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schema':
        """Create from dictionary"""
        data = dict(data)  # don't mutate caller's dict
        # Handle flow_config deserialization
        if data.get('flow_config'):
            from .flow_engine import FlowConfig
            data['flow_config'] = FlowConfig.from_dict(data['flow_config'])
        # Handle UIMetadata deserialization
        if data.get('component_ui_metadata'):
            data['component_ui_metadata'] = {
                k: UIMetadata.from_dict(v) for k, v in data['component_ui_metadata'].items()
            }
        # Handle SchemaEdge deserialization
        if data.get('edges'):
            data['edges'] = [SchemaEdge.from_dict(e) for e in data['edges']]
        # Supply defaults for fields added after initial release
        data.setdefault('schema_refs', [])
        data.setdefault('groups', {})
        data.setdefault('inheritance_chain', [])
        data.setdefault('relationships', {})
        data.setdefault('edges', [])
        data.setdefault('metadata', {})
        data.setdefault('component_ui_metadata', {})
        # Drop any keys not in the dataclass to stay forward-compatible
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        data = {k: v for k, v in data.items() if k in valid_fields}
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

    # SchemaEdge Methods (rich edge relationships)

    def add_edge(self, edge: SchemaEdge):
        """Add an edge to the schema"""
        self.edges.append(edge)
        self.update_timestamp()

    def remove_edge(self, parent_brick_id: str, child_brick_id: str) -> bool:
        """Remove an edge by parent and child brick IDs"""
        for i, edge in enumerate(self.edges):
            if edge.parent_brick_id == parent_brick_id and edge.child_brick_id == child_brick_id:
                self.edges.pop(i)
                self.update_timestamp()
                return True
        return False

    def get_edges_from(self, parent_brick_id: str) -> List[SchemaEdge]:
        """Get all outgoing edges from a parent brick"""
        return [e for e in self.edges if e.parent_brick_id == parent_brick_id]

    def get_edge_to(self, child_brick_id: str) -> Optional[SchemaEdge]:
        """Get the edge that points to a child brick (returns first match)"""
        for edge in self.edges:
            if edge.child_brick_id == child_brick_id:
                return edge
        return None

    def get_children_from_edges(self, parent_brick_id: str) -> List[str]:
        """Get child brick IDs via edges (ordered by sequence)"""
        edges = self.get_edges_from(parent_brick_id)
        edges.sort(key=lambda e: e.sequence)
        return [e.child_brick_id for e in edges]

    def get_parent_from_edges(self, child_brick_id: str) -> Optional[str]:
        """Get parent brick ID via edges"""
        edge = self.get_edge_to(child_brick_id)
        return edge.parent_brick_id if edge else None

    def get_root_components_from_edges(self) -> List[str]:
        """Get root components (those with no parent edge)"""
        all_children = {e.child_brick_id for e in self.edges}
        return [bid for bid in self.component_brick_ids if bid not in all_children]

    # Schema Reference Methods

    def add_schema_ref(self, schema_id: str, attach_to_brick_id: str,
                       property_path: str, label: str = "") -> Dict[str, Any]:
        """Attach a referenced schema via sh:node on a property of attach_to_brick_id"""
        ref = {
            "schema_id": schema_id,
            "attach_to_brick_id": attach_to_brick_id,
            "property_path": property_path,
            "label": label,
        }
        self.schema_refs.append(ref)
        self.update_timestamp()
        return ref

    def remove_schema_ref(self, schema_id: str, attach_to_brick_id: str):
        """Remove a schema reference"""
        self.schema_refs = [
            r for r in self.schema_refs
            if not (r["schema_id"] == schema_id and r["attach_to_brick_id"] == attach_to_brick_id)
        ]
        self.update_timestamp()

    def get_schema_refs_for_brick(self, brick_id: str) -> List[Dict[str, Any]]:
        """Get all schema refs attached to a given brick"""
        return [r for r in self.schema_refs if r["attach_to_brick_id"] == brick_id]

    # UI Metadata Methods
    
    def set_component_ui_metadata(self, brick_id: str, ui_metadata: UIMetadata):
        """Set UI metadata for a component"""
        self.component_ui_metadata[brick_id] = ui_metadata
        self.update_timestamp()
    
    def get_component_ui_metadata(self, brick_id: str) -> Optional[UIMetadata]:
        """Get UI metadata for a component"""
        return self.component_ui_metadata.get(brick_id)
    
    def initialize_component_ui_metadata(self, brick_id: str):
        """Initialize UI metadata for a component if not exists"""
        if brick_id not in self.component_ui_metadata:
            # Auto-assign sequence based on current count
            sequence = len(self.component_ui_metadata)
            self.component_ui_metadata[brick_id] = UIMetadata(sequence=sequence)
            self.update_timestamp()
    
    # Sequence Management Methods
    
    def set_component_sequence(self, brick_id: str, sequence: int):
        """Set sequence number for a component"""
        self.initialize_component_ui_metadata(brick_id)
        self.component_ui_metadata[brick_id].sequence = sequence
        self.update_timestamp()
    
    def get_component_sequence(self, brick_id: str) -> int:
        """Get sequence number for a component"""
        ui_metadata = self.get_component_ui_metadata(brick_id)
        return ui_metadata.sequence if ui_metadata else 0
    
    def get_components_by_sequence(self) -> List[str]:
        """Get component brick IDs sorted by sequence"""
        components_with_sequence = []
        for brick_id in self.component_brick_ids:
            seq = self.get_component_sequence(brick_id)
            components_with_sequence.append((seq, brick_id))
        components_with_sequence.sort(key=lambda x: x[0])
        return [brick_id for _, brick_id in components_with_sequence]
    
    def reorder_component(self, brick_id: str, new_sequence: int):
        """Move component to new sequence, shifting others"""
        old_sequence = self.get_component_sequence(brick_id)
        if old_sequence == new_sequence:
            return
        
        # Get all components with their sequences
        component_sequences = {}
        for comp_id in self.component_brick_ids:
            component_sequences[comp_id] = self.get_component_sequence(comp_id)
        
        # Remove the moved component
        del component_sequences[brick_id]
        
        # Shift components
        for comp_id in component_sequences:
            if old_sequence < new_sequence:
                # Moving down: shift components between old and new down
                if old_sequence < component_sequences[comp_id] <= new_sequence:
                    component_sequences[comp_id] -= 1
            else:
                # Moving up: shift components between new and old up
                if new_sequence <= component_sequences[comp_id] < old_sequence:
                    component_sequences[comp_id] += 1
        
        # Set new sequence for moved component
        component_sequences[brick_id] = new_sequence
        
        # Apply changes
        for comp_id, seq in component_sequences.items():
            self.set_component_sequence(comp_id, seq)
    
    # Grouping Methods
    
    def create_group(self, group_id: str, label: str, description: str = "", sequence: int = 0) -> bool:
        """Create a UI group"""
        if group_id in self.groups:
            return False
        self.groups[group_id] = {
            'label': label,
            'description': description,
            'sequence': sequence
        }
        self.update_timestamp()
        return True
    
    def delete_group(self, group_id: str) -> bool:
        """Delete a UI group and remove components from it"""
        if group_id not in self.groups:
            return False
        del self.groups[group_id]
        # Remove components from this group
        for brick_id, ui_metadata in self.component_ui_metadata.items():
            if ui_metadata.group_id == group_id:
                ui_metadata.group_id = None
        self.update_timestamp()
        return True
    
    def add_component_to_group(self, brick_id: str, group_id: str) -> bool:
        """Add a component to a group"""
        if group_id not in self.groups:
            return False
        self.initialize_component_ui_metadata(brick_id)
        self.component_ui_metadata[brick_id].group_id = group_id
        self.update_timestamp()
        return True
    
    def remove_component_from_group(self, brick_id: str) -> bool:
        """Remove a component from its group"""
        if brick_id not in self.component_ui_metadata:
            return False
        self.component_ui_metadata[brick_id].group_id = None
        self.update_timestamp()
        return True
    
    def get_group_members(self, group_id: str) -> List[str]:
        """Get all components in a group, sorted by sequence"""
        members = []
        for brick_id in self.component_brick_ids:
            ui_metadata = self.get_component_ui_metadata(brick_id)
            if ui_metadata and ui_metadata.group_id == group_id:
                members.append((ui_metadata.sequence, brick_id))
        members.sort(key=lambda x: x[0])
        return [brick_id for _, brick_id in members]
    
    def get_groups_by_sequence(self) -> List[Dict[str, Any]]:
        """Get groups sorted by sequence"""
        groups_list = [{'id': gid, **gdata} for gid, gdata in self.groups.items()]
        groups_list.sort(key=lambda x: x.get('sequence', 0))
        return groups_list
    
    def get_components_without_group(self) -> List[str]:
        """Get components not assigned to any group"""
        ungrouped = []
        for brick_id in self.component_brick_ids:
            ui_metadata = self.get_component_ui_metadata(brick_id)
            if not ui_metadata or not ui_metadata.group_id:
                ungrouped.append(brick_id)
        return ungrouped
    
    # Enhanced Parent-Child Methods for UI Metadata
    
    def set_component_parent(self, child_brick_id: str, parent_brick_id: str, 
                              path_iri: str = "", label: str = "") -> bool:
        """Set parent component for UI nesting - uses SchemaEdge if available, else UIMetadata"""
        if child_brick_id not in self.component_brick_ids:
            return False
        if parent_brick_id not in self.component_brick_ids:
            return False
        
        # If edges are being used, create/update an edge
        if self.edges:
            # Remove existing edge to this child if any
            self.remove_edge(None, child_brick_id)
            # Create new edge
            edge = SchemaEdge(
                child_brick_id=child_brick_id,
                parent_brick_id=parent_brick_id,
                path_iri=path_iri or f"ex:has{child_brick_id.replace('_', '').capitalize()}",
                label=label or child_brick_id.replace('_', ' ').title()
            )
            self.add_edge(edge)
        else:
            # Legacy approach: use UIMetadata
            self.initialize_component_ui_metadata(child_brick_id)
            self.component_ui_metadata[child_brick_id].parent_id = parent_brick_id
        
        self.update_timestamp()
        return True
    
    def remove_component_parent(self, child_brick_id: str) -> bool:
        """Remove parent from component (make it top-level in UI)"""
        removed = False
        
        # If edges are being used, remove the edge
        if self.edges:
            edge = self.get_edge_to(child_brick_id)
            if edge:
                self.remove_edge(edge.parent_brick_id, child_brick_id)
                removed = True
        
        # Also clear legacy UIMetadata
        if child_brick_id in self.component_ui_metadata:
            self.component_ui_metadata[child_brick_id].parent_id = None
            removed = True
        
        if removed:
            self.update_timestamp()
        return removed
    
    def get_ui_children(self, parent_brick_id: str) -> List[str]:
        """Get UI children of a component (sorted by sequence) using SchemaEdge"""
        # Use new edge-based approach if edges exist
        if self.edges:
            edges = self.get_edges_from(parent_brick_id)
            edges.sort(key=lambda e: e.sequence)
            return [e.child_brick_id for e in edges]
        # Fallback to legacy UIMetadata approach
        children = []
        for brick_id in self.component_brick_ids:
            ui_metadata = self.get_component_ui_metadata(brick_id)
            if ui_metadata and ui_metadata.parent_id == parent_brick_id:
                children.append((ui_metadata.sequence, brick_id))
        children.sort(key=lambda x: x[0])
        return [brick_id for _, brick_id in children]
    
    def get_ui_parent(self, child_brick_id: str) -> Optional[str]:
        """Get UI parent of a component using SchemaEdge"""
        # Use new edge-based approach if edges exist
        if self.edges:
            edge = self.get_edge_to(child_brick_id)
            return edge.parent_brick_id if edge else None
        # Fallback to legacy UIMetadata approach
        ui_metadata = self.get_component_ui_metadata(child_brick_id)
        return ui_metadata.parent_id if ui_metadata else None
    
    def get_ui_root_components(self) -> List[str]:
        """Get components with no UI parent (top-level in UI), sorted by sequence"""
        # Use new edge-based approach if edges exist
        if self.edges:
            return self.get_root_components_from_edges()
        # Fallback to legacy UIMetadata approach
        roots = []
        for brick_id in self.component_brick_ids:
            ui_metadata = self.get_component_ui_metadata(brick_id)
            if not ui_metadata or not ui_metadata.parent_id:
                seq = ui_metadata.sequence if ui_metadata else 0
                roots.append((seq, brick_id))
        roots.sort(key=lambda x: x[0])
        return [brick_id for _, brick_id in roots]
    
    def get_ui_tree(self) -> Dict[str, List[str]]:
        """Get complete UI tree structure (parent -> children)"""
        tree = {}
        for brick_id in self.component_brick_ids:
            children = self.get_ui_children(brick_id)
            if children:
                tree[brick_id] = children
        return tree
    
    def set_component_label(self, brick_id: str, label: str):
        """Set UI label for a component"""
        self.initialize_component_ui_metadata(brick_id)
        self.component_ui_metadata[brick_id].label = label
        self.update_timestamp()
    
    def set_component_help_text(self, brick_id: str, help_text: str):
        """Set help text for a component"""
        self.initialize_component_ui_metadata(brick_id)
        self.component_ui_metadata[brick_id].help_text = help_text
        self.update_timestamp()
    
    def set_component_collapsible(self, brick_id: str, is_collapsible: bool):
        """Set whether component can be collapsed in tree view"""
        self.initialize_component_ui_metadata(brick_id)
        self.component_ui_metadata[brick_id].is_collapsible = is_collapsible
        self.update_timestamp()
    
    def set_component_visibility(self, brick_id: str, is_visible: bool):
        """Set component visibility in UI"""
        self.initialize_component_ui_metadata(brick_id)
        self.component_ui_metadata[brick_id].is_visible = is_visible
        self.update_timestamp()
    
    # Enhanced Tree Structure Methods for Hierarchical Schemas
    
    def get_hierarchical_tree(self, brick_integration=None) -> Dict[str, Any]:
        """Get complete hierarchical tree structure with brick details"""
        if not brick_integration:
            return self.get_ui_tree()
        
        tree = {}
        for brick_id in self.component_brick_ids:
            children = self.get_ui_children(brick_id)
            if children:
                # Get brick details
                brick = brick_integration.get_brick_by_id(brick_id)
                brick_info = {
                    'brick_id': brick_id,
                    'brick_type': brick.object_type if brick else 'unknown',
                    'children': children,
                    'ui_metadata': self.get_component_ui_metadata(brick_id)
                }
                tree[brick_id] = brick_info
        return tree
    
    def get_tree_depth(self, brick_id: str) -> int:
        """Get depth of a component in the tree (root = 0)"""
        if brick_id not in self.component_brick_ids:
            return -1
        
        depth = 0
        current = brick_id
        while True:
            parent = self.get_ui_parent(current)
            if not parent:
                break
            depth += 1
            current = parent
        return depth
    
    def get_tree_level(self, depth: int) -> List[str]:
        """Get all components at a specific tree depth"""
        components_at_level = []
        for brick_id in self.component_brick_ids:
            if self.get_tree_depth(brick_id) == depth:
                components_at_level.append(brick_id)
        return components_at_level
    
    def validate_tree_structure(self) -> Dict[str, Any]:
        """Validate tree structure for cycles and orphaned nodes"""
        issues = []
        warnings = []
        
        # Check for cycles
        visited = set()
        recursion_stack = set()
        
        def has_cycle(node):
            if node in recursion_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            recursion_stack.add(node)
            
            children = self.get_ui_children(node)
            for child in children:
                if has_cycle(child):
                    return True
            
            recursion_stack.remove(node)
            return False
        
        # Check each component for cycles
        for brick_id in self.component_brick_ids:
            if has_cycle(brick_id):
                issues.append(f"Circular reference detected involving component: {brick_id}")
                break
        
        # Check for orphaned nodes (parent not in component list)
        for brick_id in self.component_brick_ids:
            parent = self.get_ui_parent(brick_id)
            if parent and parent not in self.component_brick_ids:
                warnings.append(f"Component {brick_id} has parent {parent} which is not in the schema")
        
        # Check for deep nesting
        for brick_id in self.component_brick_ids:
            depth = self.get_tree_depth(brick_id)
            if depth > 5:
                warnings.append(f"Component {brick_id} is deeply nested (depth {depth})")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'tree_stats': {
                'total_components': len(self.component_brick_ids),
                'root_components': len(self.get_ui_root_components()),
                'max_depth': max([self.get_tree_depth(bid) for bid in self.component_brick_ids]) if self.component_brick_ids else 0
            }
        }
    
    def get_nested_components(self, parent_brick_id: str) -> List[str]:
        """Get all nested components (recursively) under a parent"""
        nested = []
        children = self.get_ui_children(parent_brick_id)
        
        for child in children:
            nested.append(child)
            nested.extend(self.get_nested_components(child))
        
        return nested
    
    def get_component_path(self, brick_id: str) -> List[str]:
        """Get the path from root to a component"""
        if brick_id not in self.component_brick_ids:
            return []
        
        path = []
        current = brick_id
        while current:
            path.insert(0, current)
            parent = self.get_ui_parent(current)
            if not parent:
                break
            current = parent
        
        return path
    
    def is_ancestor(self, ancestor_id: str, descendant_id: str) -> bool:
        """Check if ancestor_id is an ancestor of descendant_id"""
        current = descendant_id
        while current:
            parent = self.get_ui_parent(current)
            if parent == ancestor_id:
                return True
            current = parent
        return False
    
    def get_leaf_components(self) -> List[str]:
        """Get all leaf components (components with no children)"""
        leaves = []
        for brick_id in self.component_brick_ids:
            children = self.get_ui_children(brick_id)
            if not children:
                leaves.append(brick_id)
        return leaves


class SchemaCore:
    """Core schema management functionality - Simple Version"""

    def __init__(self, repository_path: str = None, use_shared_libraries: bool = True):
        # Use shared libraries by default
        if use_shared_libraries:
            from common import shared_library_manager
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
        schema_file = os.path.join(self.repository_path, lib_name, f"{schema_id}.json")  # flat — no schemas/ subdir
        
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
    
    def save_schema(self, schema: Optional[Schema] = None, library_name: Optional[str] = None) -> bool:
        """Save current schema to storage"""
        schema_to_save = schema or self.current_schema
        if not schema_to_save:
            return False
        
        # Validate schema
        if not schema_to_save.name.strip():
            return False
        
        # Update timestamp
        schema_to_save.update_timestamp()
        
        # Save to file
        lib_name = library_name or self.active_library
        schemas_path = os.path.join(self.repository_path, lib_name)
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
        lib_path = os.path.join(self.repository_path, lib_name)
        
        if not os.path.exists(lib_path):
            return []
        
        schemas = []
        try:
            schema_files = [f for f in os.listdir(lib_path)
                            if f.endswith('.json') and f != 'metadata.json']
                
            for schema_file in schema_files:
                schema_path = os.path.join(lib_path, schema_file)
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
        schema_file = os.path.join(self.repository_path, lib_name, f"{schema_id}.json")
        
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
