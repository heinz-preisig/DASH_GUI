#!/usr/bin/env python3
"""
Step 1: SHACL Brick Generator - Backend Component
Comprehensive SHACL brick generation with full SHACL object knowledge
Designed for clean frontend/backend separation
"""

import json
import os
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum
from datetime import datetime
from rdflib import Graph, Namespace, Literal, URIRef, RDF
from rdflib.namespace import SH, XSD, RDFS, OWL

# Namespaces
BRICK = Namespace("http://example.org/brick#")
EX = Namespace("http://example.org/")

class SHACLObjectType(Enum):
    """Enumeration of all SHACL object types"""
    # Shape types
    NODE_SHAPE = "NodeShape"
    PROPERTY_SHAPE = "PropertyShape"
    
    # Constraint components
    MIN_COUNT = "MinCountConstraintComponent"
    MAX_COUNT = "MaxCountConstraintComponent"
    MIN_LENGTH = "MinLengthConstraintComponent"
    MAX_LENGTH = "MaxLengthConstraintComponent"
    PATTERN = "PatternConstraintComponent"
    DATATYPE = "DatatypeConstraintComponent"
    CLASS = "ClassConstraintComponent"
    NODE_KIND = "NodeKindConstraintComponent"
    UNIQUE_LANG = "UniqueLangConstraintComponent"
    EQUALS = "EqualsConstraintComponent"
    DISJOINT = "DisjointConstraintComponent"
    LESS_THAN = "LessThanConstraintComponent"
    LESS_THAN_OR_EQUALS = "LessThanOrEqualsConstraintComponent"
    
    # Node kinds
    BLANK_NODE = "BlankNode"
    BLANK_NODE_OR_IRI = "BlankNodeOrIRI"
    BLANK_NODE_OR_LITERAL = "BlankNodeOrLiteral"
    IRI = "IRI"
    IRI_OR_LITERAL = "IRIOrLiteral"
    LITERAL = "Literal"
    
    # Target types
    TARGET_CLASS = "TargetClass"
    TARGET_NODE = "TargetNode"
    TARGET_OBJECTS_OF = "TargetObjectsOf"
    TARGET_SUBJECTS_OF = "TargetSubjectsOf"

@dataclass
class SHACLConstraint:
    """Represents a SHACL constraint"""
    constraint_type: str
    value: Union[str, int, float, bool, List[str]]
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SHACLTarget:
    """Represents a SHACL target declaration"""
    target_type: str
    value: Union[str, List[str]]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SHACLBrick:
    """Represents a reusable SHACL brick with modification tracking"""
    brick_id: str
    name: str
    description: str
    object_type: str
    targets: List[SHACLTarget] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    constraints: List[SHACLConstraint] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Post-initialization to ensure timestamps are set"""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()
    
    def _mark_modified(self):
        """Mark the brick as modified by updating the updated_at timestamp"""
        self.updated_at = datetime.now().isoformat()
    
    def update_name(self, name: str):
        """Update brick name and mark as modified"""
        self.name = name
        self._mark_modified()
    
    def update_description(self, description: str):
        """Update brick description and mark as modified"""
        self.description = description
        self._mark_modified()
    
    def update_target_class(self, target_class: str):
        """Update target class and mark as modified"""
        # For NodeShape, target_class should be in the first target
        if self.object_type == "NodeShape":
            if self.targets:
                self.targets[0].value = target_class
            else:
                self.targets.append(SHACLTarget("targetClass", target_class))
        self._mark_modified()
    
    def get_target_class(self) -> str:
        """Get the target class for this brick"""
        if self.object_type == "NodeShape" and self.targets:
            return self.targets[0].value
        return ""
    
    def add_property(self, prop_name: str, prop_data: Dict[str, Any]):
        """Add a property and mark as modified"""
        self.properties[prop_name] = prop_data
        self._mark_modified()
    
    def remove_property(self, prop_name: str):
        """Remove a property and mark as modified"""
        if prop_name in self.properties:
            del self.properties[prop_name]
            self._mark_modified()
    
    def add_constraint(self, constraint: SHACLConstraint):
        """Add a constraint and mark as modified"""
        self.constraints.append(constraint)
        self._mark_modified()
    
    def remove_constraint(self, index: int):
        """Remove constraint by index and mark as modified"""
        if 0 <= index < len(self.constraints):
            del self.constraints[index]
            self._mark_modified()
    
    def is_modified_since(self, timestamp: str) -> bool:
        """Check if brick has been modified since given timestamp"""
        return self.updated_at > timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert brick to dictionary for serialization"""
        data = asdict(self)
        data['targets'] = [target.to_dict() for target in self.targets]
        data['constraints'] = [constraint.to_dict() for constraint in self.constraints]
        
        # Add flat target_class field for compatibility with validation logic
        data['target_class'] = self.get_target_class()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SHACLBrick':
        """Create brick from dictionary"""
        # Handle targets
        targets = [SHACLTarget(**t) for t in data.get('targets', [])]
        
        # Handle constraints
        constraints = [SHACLConstraint(**c) for c in data.get('constraints', [])]
        
        return cls(
            brick_id=data['brick_id'],
            name=data['name'],
            description=data['description'],
            object_type=data['object_type'],
            targets=targets,
            properties=data.get('properties', {}),
            constraints=constraints,
            tags=data.get('tags', []),
            metadata=data.get('metadata', {}),
            created_at=data.get('created_at', datetime.now().isoformat()),
            updated_at=data.get('updated_at', datetime.now().isoformat())
        )

class BrickRepository:
    """Manages a collection of brick libraries"""
    
    def __init__(self, repository_path: str = "brick_repositories"):
        self.repository_path = Path(repository_path)
        self.repository_path.mkdir(exist_ok=True)
        self.libraries: Dict[str, 'BrickLibrary'] = {}
        self.active_library: Optional[str] = None
        self._load_available_libraries()
    
    def _load_available_libraries(self):
        """Load all available libraries from repository"""
        for lib_dir in self.repository_path.iterdir():
            if lib_dir.is_dir() and (lib_dir / "metadata.json").exists():
                try:
                    library = BrickLibrary.from_directory(lib_dir)
                    self.libraries[library.name] = library
                except Exception as e:
                    print(f"Warning: Failed to load library {lib_dir.name}: {e}")
    
    def create_library(self, name: str, description: str, author: str = "Unknown") -> 'BrickLibrary':
        """Create a new brick library"""
        library = BrickLibrary(name, description, author)
        library_path = self.repository_path / name
        library.save_to_directory(library_path)
        self.libraries[name] = library
        return library
    
    def get_library(self, name: str) -> Optional['BrickLibrary']:
        """Get a library by name"""
        return self.libraries.get(name)
    
    def list_libraries(self) -> List[Dict[str, Any]]:
        """List all libraries"""
        return [
            {
                "name": lib.name,
                "description": lib.description,
                "brick_count": len(lib.bricks),
                "author": lib.author,
                "created": lib.metadata.get("created")
            }
            for lib in self.libraries.values()
        ]
    
    def set_active_library(self, name: str):
        """Set the active library"""
        if name in self.libraries:
            self.active_library = name
        else:
            raise ValueError(f"Library {name} not found")
    
    def get_active_library(self) -> Optional['BrickLibrary']:
        """Get the active library"""
        if self.active_library:
            return self.libraries.get(self.active_library)
        return None
    
    def delete_library(self, name: str):
        """Delete a library"""
        if name in self.libraries:
            lib_path = self.repository_path / name
            if lib_path.exists():
                import shutil
                shutil.rmtree(lib_path)
            del self.libraries[name]
            if self.active_library == name:
                self.active_library = None

class BrickLibrary:
    """Manages a collection of SHACL bricks"""
    
    def __init__(self, name: str, description: str, author: str = "Unknown"):
        self.name = name
        self.description = description
        self.author = author
        self.bricks: Dict[str, SHACLBrick] = {}
        now = datetime.now().isoformat()
        self.created_at = now
        self.updated_at = now
        self.metadata = {
            "name": name,
            "description": description,
            "author": author,
            "created": "2026-04-13",
            "version": "1.0",
            "created_at": now,
            "updated_at": now
        }
        self._load_default_bricks()
    
    def _mark_modified(self):
        """Mark library as modified by updating updated_at timestamp"""
        self.updated_at = datetime.now().isoformat()
        self.metadata["updated_at"] = self.updated_at
    
    def _load_default_bricks(self):
        """Load default commonly used bricks"""
        # Person NodeShape brick
        person_brick = SHACLBrick(
            brick_id="person_nodeshape",
            name="Person NodeShape",
            description="Basic person shape with common properties",
            object_type=SHACLObjectType.NODE_SHAPE.value,
            targets=[SHACLTarget(SHACLObjectType.TARGET_CLASS.value, "foaf:Person")],
            properties={"nodeKind": SHACLObjectType.IRI.value},
            tags=["person", "foaf", "basic", "common"]
        )
        
        # Email PropertyShape brick
        email_brick = SHACLBrick(
            brick_id="email_property",
            name="Email Property",
            description="Email property with validation",
            object_type=SHACLObjectType.PROPERTY_SHAPE.value,
            properties={"path": "foaf:mbox", "datatype": "xsd:string"},
            constraints=[
                SHACLConstraint(SHACLObjectType.MIN_LENGTH.value, 5),
                SHACLConstraint(SHACLObjectType.PATTERN.value, "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")
            ],
            tags=["email", "contact", "validation", "common"]
        )
        
        # Name PropertyShape brick
        name_brick = SHACLBrick(
            brick_id="name_property",
            name="Name Property",
            description="Name property with constraints",
            object_type=SHACLObjectType.PROPERTY_SHAPE.value,
            properties={"path": "foaf:name", "datatype": "xsd:string"},
            constraints=[
                SHACLConstraint(SHACLObjectType.MIN_LENGTH.value, 1),
                SHACLConstraint(SHACLObjectType.MAX_LENGTH.value, 100)
            ],
            tags=["name", "basic", "text", "common"]
        )
        
        # Organization NodeShape brick
        org_brick = SHACLBrick(
            brick_id="organization_nodeshape",
            name="Organization NodeShape",
            description="Basic organization shape",
            object_type=SHACLObjectType.NODE_SHAPE.value,
            targets=[SHACLTarget(SHACLObjectType.TARGET_CLASS.value, "foaf:Organization")],
            properties={"nodeKind": SHACLObjectType.IRI.value},
            tags=["organization", "foaf", "basic"]
        )
        
        # Date PropertyShape brick
        date_brick = SHACLBrick(
            brick_id="date_property",
            name="Date Property",
            description="Date property for various date fields",
            object_type=SHACLObjectType.PROPERTY_SHAPE.value,
            properties={"path": "schema:date", "datatype": "xsd:date"},
            tags=["date", "temporal", "common"]
        )
        
        self.add_brick(person_brick)
        self.add_brick(email_brick)
        self.add_brick(name_brick)
        self.add_brick(org_brick)
        self.add_brick(date_brick)
    
    def add_brick(self, brick: SHACLBrick):
        """Add a brick to the library"""
        self.bricks[brick.brick_id] = brick
        self._mark_modified()
    
    def get_brick(self, brick_id: str) -> Optional[SHACLBrick]:
        """Get a brick by ID"""
        return self.bricks.get(brick_id)
    
    def remove_brick(self, brick_id: str) -> bool:
        """Remove a brick from the library"""
        if brick_id in self.bricks:
            del self.bricks[brick_id]
            self._mark_modified()
            return True
        return False
    
    def list_bricks(self, object_type: Optional[str] = None, tags: Optional[List[str]] = None) -> List[SHACLBrick]:
        """List bricks with optional filtering"""
        bricks = list(self.bricks.values())
        
        if object_type:
            bricks = [b for b in bricks if b.object_type == object_type]
        
        if tags:
            bricks = [b for b in bricks if any(tag in b.tags for tag in tags)]
        
        return bricks
    
    def search_bricks(self, query: str) -> List[SHACLBrick]:
        """Search bricks by name, description, or tags"""
        query = query.lower()
        return [
            brick for brick in self.bricks.values()
            if (query in brick.name.lower() or 
                query in brick.description.lower() or
                any(query in tag.lower() for tag in brick.tags))
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get library statistics"""
        object_type_counts = {}
        tag_counts = {}
        
        for brick in self.bricks.values():
            # Count object types
            object_type_counts[brick.object_type] = object_type_counts.get(brick.object_type, 0) + 1
            
            # Count tags
            for tag in brick.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return {
            "total_bricks": len(self.bricks),
            "object_types": object_type_counts,
            "tags": tag_counts,
            "name": self.name,
            "description": self.description
        }
    
    def export_to_json(self, file_path: str):
        """Export library to JSON file"""
        data = {
            "metadata": self.metadata,
            "bricks": {brick_id: brick.to_dict() for brick_id, brick in self.bricks.items()}
        }
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_from_json(self, file_path: str):
        """Import library from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        self.metadata = data.get("metadata", {})
        self.name = self.metadata.get("name", "Imported Library")
        self.description = self.metadata.get("description", "Imported from file")
        
        self.bricks.clear()
        for brick_id, brick_data in data.get("bricks", {}).items():
            brick = SHACLBrick.from_dict(brick_data)
            self.bricks[brick_id] = brick
    
    def save_to_directory(self, directory_path: Union[str, Path]):
        """Save library to directory"""
        dir_path = Path(directory_path)
        dir_path.mkdir(exist_ok=True)
        
        # Save metadata
        with open(dir_path / "metadata.json", 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        # Save bricks
        bricks_dir = dir_path / "bricks"
        bricks_dir.mkdir(exist_ok=True)
        
        for brick_id, brick in self.bricks.items():
            brick_file = bricks_dir / f"{brick_id}.json"
            with open(brick_file, 'w') as f:
                json.dump(brick.to_dict(), f, indent=2)
    
    @classmethod
    def from_directory(cls, directory_path: Union[str, Path]) -> 'BrickLibrary':
        """Load library from directory"""
        dir_path = Path(directory_path)
        
        # Load metadata
        with open(dir_path / "metadata.json", 'r') as f:
            metadata = json.load(f)
        
        library = cls(
            metadata["name"],
            metadata["description"],
            metadata.get("author", "Unknown")
        )
        library.metadata = metadata
        # Restore timestamps from metadata if available
        library.created_at = metadata.get("created_at", library.created_at)
        library.updated_at = metadata.get("updated_at", library.updated_at)
        
        # Load bricks
        bricks_dir = dir_path / "bricks"
        if bricks_dir.exists():
            for brick_file in bricks_dir.glob("*.json"):
                with open(brick_file, 'r') as f:
                    brick_data = json.load(f)
                brick = SHACLBrick.from_dict(brick_data)
                library.bricks[brick.brick_id] = brick
        
        return library

class SHACLBrickGenerator:
    """Generates SHACL bricks with comprehensive SHACL knowledge"""
    
    def __init__(self, library: BrickLibrary):
        self.library = library
        self.known_constraints = self._initialize_constraint_templates()
        self.known_properties = self._initialize_property_templates()
    
    def _initialize_constraint_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize constraint templates for all SHACL constraint types"""
        return {
            SHACLObjectType.MIN_COUNT.value: {
                "description": "Minimum number of values",
                "value_type": "integer",
                "min_value": 0
            },
            SHACLObjectType.MAX_COUNT.value: {
                "description": "Maximum number of values", 
                "value_type": "integer",
                "min_value": 0
            },
            SHACLObjectType.MIN_LENGTH.value: {
                "description": "Minimum string length",
                "value_type": "integer",
                "min_value": 0
            },
            SHACLObjectType.MAX_LENGTH.value: {
                "description": "Maximum string length",
                "value_type": "integer", 
                "min_value": 0
            },
            SHACLObjectType.PATTERN.value: {
                "description": "Regular expression pattern",
                "value_type": "string",
                "examples": ["^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"]
            },
            SHACLObjectType.DATATYPE.value: {
                "description": "Datatype constraint",
                "value_type": "uri",
                "common_values": ["xsd:string", "xsd:integer", "xsd:decimal", "xsd:boolean", "xsd:date", "xsd:anyURI"]
            },
            SHACLObjectType.CLASS.value: {
                "description": "Class constraint",
                "value_type": "uri"
            },
            SHACLObjectType.NODE_KIND.value: {
                "description": "Node kind constraint",
                "value_type": "enumeration",
                "values": [kind.value for kind in [
                    SHACLObjectType.BLANK_NODE,
                    SHACLObjectType.BLANK_NODE_OR_IRI,
                    SHACLObjectType.BLANK_NODE_OR_LITERAL,
                    SHACLObjectType.IRI,
                    SHACLObjectType.IRI_OR_LITERAL,
                    SHACLObjectType.LITERAL
                ]]
            }
        }
    
    def _initialize_property_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize property templates for common SHACL properties"""
        return {
            "path": {
                "description": "Property path",
                "value_type": "uri",
                "required": True
            },
            "datatype": {
                "description": "Expected datatype",
                "value_type": "uri",
                "common_values": ["xsd:string", "xsd:integer", "xsd:decimal", "xsd:boolean", "xsd:date"]
            },
            "nodeKind": {
                "description": "Allowed node kind",
                "value_type": "enumeration",
                "values": [kind.value for kind in [
                    SHACLObjectType.BLANK_NODE,
                    SHACLObjectType.BLANK_NODE_OR_IRI,
                    SHACLObjectType.BLANK_NODE_OR_LITERAL,
                    SHACLObjectType.IRI,
                    SHACLObjectType.IRI_OR_LITERAL,
                    SHACLObjectType.LITERAL
                ]]
            },
            "minCount": {
                "description": "Minimum count",
                "value_type": "integer",
                "min_value": 0
            },
            "maxCount": {
                "description": "Maximum count",
                "value_type": "integer",
                "min_value": 0
            },
            "name": {
                "description": "Human-readable name",
                "value_type": "string"
            },
            "description": {
                "description": "Human-readable description",
                "value_type": "string"
            },
            "deactivated": {
                "description": "Whether the shape is deactivated",
                "value_type": "boolean"
            },
            "severity": {
                "description": "Validation severity",
                "value_type": "uri",
                "common_values": ["sh:Violation", "sh:Warning", "sh:Info"]
            }
        }
    
    def get_constraint_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get all constraint templates"""
        return self.known_constraints
    
    def get_property_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get all property templates"""
        return self.known_properties
    
    def create_nodeshape_brick(self, brick_id: str, name: str, description: str,
                             target_class: Optional[str] = None,
                             properties: Optional[Dict[str, Any]] = None,
                             constraints: Optional[List[SHACLConstraint]] = None,
                             tags: Optional[List[str]] = None) -> SHACLBrick:
        """Create a NodeShape brick"""
        targets = []
        if target_class:
            targets.append(SHACLTarget(SHACLObjectType.TARGET_CLASS.value, target_class))
        
        brick = SHACLBrick(
            brick_id=brick_id,
            name=name,
            description=description,
            object_type=SHACLObjectType.NODE_SHAPE.value,
            targets=targets,
            properties=properties or {},
            constraints=constraints or [],
            tags=tags or []
        )
        
        self.library.add_brick(brick)
        return brick
    
    def create_propertyshape_brick(self, brick_id: str, name: str, description: str,
                                 path: str,
                                 properties: Optional[Dict[str, Any]] = None,
                                 constraints: Optional[List[SHACLConstraint]] = None,
                                 tags: Optional[List[str]] = None) -> SHACLBrick:
        """Create a PropertyShape brick"""
        brick_properties = properties or {}
        brick_properties["path"] = path
        
        brick = SHACLBrick(
            brick_id=brick_id,
            name=name,
            description=description,
            object_type=SHACLObjectType.PROPERTY_SHAPE.value,
            properties=brick_properties,
            constraints=constraints or [],
            tags=tags or []
        )
        
        self.library.add_brick(brick)
        return brick
    
    def create_brick_from_template(self, template_type: str, name: str, 
                                 parameters: Dict[str, Any]) -> SHACLBrick:
        """Create a brick from a predefined template"""
        brick_id = f"{name.lower().replace(' ', '_')}_brick"
        
        if template_type == "person":
            return self.create_nodeshape_brick(
                brick_id, name, "Person shape with common properties",
                target_class="foaf:Person",
                properties={"nodeKind": SHACLObjectType.IRI.value},
                tags=["person", "template"]
            )
        elif template_type == "organization":
            return self.create_nodeshape_brick(
                brick_id, name, "Organization shape",
                target_class="foaf:Organization", 
                properties={"nodeKind": SHACLObjectType.IRI.value},
                tags=["organization", "template"]
            )
        elif template_type == "email_property":
            return self.create_propertyshape_brick(
                brick_id, name, "Email property with validation",
                "foaf:mbox",
                properties={"datatype": "xsd:string"},
                constraints=[
                    SHACLConstraint(SHACLObjectType.MIN_LENGTH.value, 5),
                    SHACLConstraint(SHACLObjectType.PATTERN.value, "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")
                ],
                tags=["email", "template", "validated"]
            )
        else:
            raise ValueError(f"Unknown template type: {template_type}")
    
    def brick_to_shacl(self, brick: SHACLBrick, base_uri: str = EX) -> Graph:
        """Convert a brick to SHACL RDF graph"""
        g = Graph()
        g.bind("sh", SH)
        g.bind("brick", BRICK)
        
        brick_uri = URIRef(f"{base_uri}{brick.brick_id}")
        
        # Add type
        if brick.object_type == SHACLObjectType.NODE_SHAPE.value:
            g.add((brick_uri, RDF.type, SH.NodeShape))
        elif brick.object_type == SHACLObjectType.PROPERTY_SHAPE.value:
            g.add((brick_uri, RDF.type, SH.PropertyShape))
        
        # Add targets
        for target in brick.targets:
            if target.target_type == SHACLObjectType.TARGET_CLASS.value:
                g.add((brick_uri, SH.targetClass, URIRef(target.value)))
            elif target.target_type == SHACLObjectType.TARGET_NODE.value:
                g.add((brick_uri, SH.targetNode, URIRef(target.value)))
        
        # Add properties
        for prop_name, prop_value in brick.properties.items():
            if hasattr(SH, prop_name):
                prop = getattr(SH, prop_name)
                if isinstance(prop_value, str) and (prop_value.startswith("http://") or prop_value.startswith("https://") or ":" in prop_value and "/" in prop_value):
                    g.add((brick_uri, prop, URIRef(prop_value)))
                elif isinstance(prop_value, bool):
                    g.add((brick_uri, prop, Literal(prop_value)))
                elif isinstance(prop_value, (int, float)):
                    g.add((brick_uri, prop, Literal(prop_value)))
                else:
                    g.add((brick_uri, prop, Literal(prop_value)))
        
        # Add constraints
        for constraint in brick.constraints:
            # Map constraint types to SHACL properties
            constraint_mapping = {
                "MinCountConstraintComponent": "minCount",
                "MaxCountConstraintComponent": "maxCount", 
                "MinLengthConstraintComponent": "minLength",
                "MaxLengthConstraintComponent": "maxLength",
                "PatternConstraintComponent": "pattern",
                "DatatypeConstraintComponent": "datatype",
                "ClassConstraintComponent": "class",
                "NodeKindConstraintComponent": "nodeKind"
            }
            
            constraint_name = constraint_mapping.get(constraint.constraint_type)
            if constraint_name and hasattr(SH, constraint_name):
                constraint_prop = getattr(SH, constraint_name)
                if isinstance(constraint.value, (int, float)):
                    g.add((brick_uri, constraint_prop, Literal(constraint.value)))
                elif isinstance(constraint.value, bool):
                    g.add((brick_uri, constraint_prop, Literal(constraint.value)))
                elif isinstance(constraint.value, list):
                    for val in constraint.value:
                        g.add((brick_uri, constraint_prop, Literal(val)))
                else:
                    g.add((brick_uri, constraint_prop, Literal(constraint.value)))
        
        # Add annotations
        if brick.description:
            g.add((brick_uri, RDFS.comment, Literal(brick.description)))
        
        g.add((brick_uri, RDFS.label, Literal(brick.name)))
        
        return g

def main():
    """Test the brick generator"""
    # Create repository
    repo = BrickRepository()
    
    # Create a new library
    library = repo.create_library("test_library", "Test library for demonstration")
    repo.set_active_library("test_library")
    
    # Create generator
    generator = SHACLBrickGenerator(library)
    
    # Create some bricks
    person_brick = generator.create_nodeshape_brick(
        "custom_person",
        "Custom Person",
        "A custom person shape",
        target_class="foaf:Person",
        properties={"nodeKind": SHACLObjectType.IRI.value},
        tags=["person", "custom"]
    )
    
    email_brick = generator.create_propertyshape_brick(
        "work_email",
        "Work Email",
        "Work email property",
        "foaf:mbox",
        properties={"datatype": "xsd:string"},
        constraints=[
            SHACLConstraint(SHACLObjectType.MIN_LENGTH.value, 5),
            SHACLConstraint(SHACLObjectType.PATTERN.value, "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")
        ],
        tags=["email", "work", "validated"]
    )
    
    print(f"Created {len(library.bricks)} bricks")
    
    # List bricks
    print("\nAvailable bricks:")
    for brick in library.list_bricks():
        print(f"  - {brick.brick_id}: {brick.name} ({brick.object_type})")
    
    # Search bricks
    print("\nSearch results for 'person':")
    for brick in library.search_bricks("person"):
        print(f"  - {brick.brick_id}: {brick.name}")
    
    # Get statistics
    stats = library.get_statistics()
    print(f"\nLibrary statistics: {stats}")
    
    # Convert to SHACL
    g = generator.brick_to_shacl(person_brick)
    print("\nSHACL Turtle for person brick:")
    print(g.serialize(format='turtle'))

if __name__ == "__main__":
    main()
