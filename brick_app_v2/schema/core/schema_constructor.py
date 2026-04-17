#!/usr/bin/env python3
"""
Step 2: Schema Constructor
Combines bricks into complex shapes with daisy-chaining capabilities
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from datetime import datetime

from ...core.brick_generator import SHACLBrick, SHACLObjectType, SHACLConstraint, SHACLTarget

class InterfaceFlowType(Enum):
    """Types of interface flow for daisy-chaining"""
    SEQUENTIAL = "sequential"  # Step 1 -> Step 2 -> Step 3
    CONDITIONAL = "conditional"  # If/else branching
    PARALLEL = "parallel"  # Multiple simultaneous steps
    LOOPING = "looping"  # Repeatable steps
    DYNAMIC = "dynamic"  # User-driven navigation

@dataclass
class InterfaceStep:
    """Single step in interface flow"""
    step_id: str
    name: str
    description: str
    brick_ids: List[str]  # Bricks used in this step
    next_steps: List[str]  # Possible next steps
    conditions: Dict[str, Any] = field(default_factory=dict)  # Conditions for navigation
    ui_template: Optional[str] = None  # UI template to use
    validation_rules: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SchemaComposition:
    """Complex schema composed of multiple bricks"""
    schema_id: str
    name: str
    description: str
    root_brick_id: str  # Main entity brick
    component_brick_ids: List[str]  # Property and component bricks
    inheritance_chain: List[str] = field(default_factory=list)  # Parent schemas
    interface_flow: Optional[InterfaceFlowType] = InterfaceFlowType.SEQUENTIAL
    interface_steps: List[InterfaceStep] = field(default_factory=list)
    relationships: Dict[str, List[str]] = field(default_factory=dict)  # Brick relationships
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class DaisyChain:
    """Daisy-chain configuration for multi-step interfaces"""
    chain_id: str
    name: str
    description: str
    schemas: List[str]  # Schema IDs in chain order
    navigation_rules: Dict[str, Any] = field(default_factory=dict)
    shared_data: Dict[str, Any] = field(default_factory=dict)  # Data shared between steps
    conditional_logic: Dict[str, Any] = field(default_factory=dict)
    ui_theme: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class SchemaConstructor:
    """Main schema construction system"""
    
    def __init__(self, brick_backend):
        self.brick_backend = brick_backend
        self.schemas: Dict[str, SchemaComposition] = {}
        self.daisy_chains: Dict[str, DaisyChain] = {}
        self.templates: Dict[str, Dict[str, Any]] = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize common schema templates"""
        self.templates = {
            "person_profile": {
                "name": "Person Profile",
                "description": "Complete person information schema",
                "root_type": "NodeShape",
                "components": ["name", "email", "phone", "address"],
                "interface_steps": [
                    {"name": "Basic Info", "bricks": ["name", "email"]},
                    {"name": "Contact Details", "bricks": ["phone"]},
                    {"name": "Address", "bricks": ["address"]}
                ]
            },
            "product_catalog": {
                "name": "Product Catalog",
                "description": "Product information and categorization",
                "root_type": "NodeShape",
                "components": ["product_name", "description", "price", "category"],
                "interface_steps": [
                    {"name": "Basic Product", "bricks": ["product_name", "description"]},
                    {"name": "Pricing", "bricks": ["price"]},
                    {"name": "Category", "bricks": ["category"]}
                ]
            },
            "organization": {
                "name": "Organization",
                "description": "Organization structure and details",
                "root_type": "NodeShape",
                "components": ["org_name", "org_type", "address", "contact"],
                "interface_steps": [
                    {"name": "Organization Info", "bricks": ["org_name", "org_type"]},
                    {"name": "Location", "bricks": ["address"]},
                    {"name": "Contact", "bricks": ["contact"]}
                ]
            }
        }
    
    def create_schema(self, name: str, description: str, root_brick_id: str,
                     component_brick_ids: List[str] = None,
                     interface_flow: InterfaceFlowType = InterfaceFlowType.SEQUENTIAL) -> SchemaComposition:
        """Create a new schema composition"""
        schema_id = name.lower().replace(" ", "_") + "_" + str(uuid.uuid4())[:8]
        
        # Validate bricks exist
        if not self._validate_bricks_exist([root_brick_id] + (component_brick_ids or [])):
            raise ValueError("One or more specified bricks do not exist")
        
        # Create interface steps automatically if not provided
        interface_steps = self._create_default_interface_steps(root_brick_id, component_brick_ids or [])
        
        schema = SchemaComposition(
            schema_id=schema_id,
            name=name,
            description=description,
            root_brick_id=root_brick_id,
            component_brick_ids=component_brick_ids or [],
            interface_flow=interface_flow,
            interface_steps=interface_steps,
            relationships=self._analyze_brick_relationships(root_brick_id, component_brick_ids or [])
        )
        
        self.schemas[schema_id] = schema
        return schema
    
    def create_schema_from_template(self, template_name: str, custom_name: str = None,
                                   brick_mappings: Dict[str, str] = None) -> SchemaComposition:
        """Create schema from predefined template"""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name]
        name = custom_name or template["name"]
        description = template["description"]
        
        # Map template bricks to actual bricks
        brick_mappings = brick_mappings or {}
        root_brick_id = brick_mappings.get("root", template.get("root_brick", ""))
        component_brick_ids = []
        
        for component in template["components"]:
            mapped_brick = brick_mappings.get(component, component)
            if mapped_brick:
                component_brick_ids.append(mapped_brick)
        
        # Create interface steps
        interface_steps = []
        for i, step_template in enumerate(template["interface_steps"]):
            step_brick_ids = []
            for brick in step_template["bricks"]:
                mapped_brick = brick_mappings.get(brick, brick)
                if mapped_brick:
                    step_brick_ids.append(mapped_brick)
            
            interface_step = InterfaceStep(
                step_id=f"step_{i+1}",
                name=step_template["name"],
                description=f"Step {i+1}: {step_template['name']}",
                brick_ids=step_brick_ids,
                next_steps=[f"step_{i+2}"] if i < len(template["interface_steps"]) - 1 else []
            )
            interface_steps.append(interface_step)
        
        schema = SchemaComposition(
            schema_id=name.lower().replace(" ", "_") + "_" + str(uuid.uuid4())[:8],
            name=name,
            description=description,
            root_brick_id=root_brick_id,
            component_brick_ids=component_brick_ids,
            interface_steps=interface_steps,
            relationships=self._analyze_brick_relationships(root_brick_id, component_brick_ids)
        )
        
        self.schemas[schema.schema_id] = schema
        return schema
    
    def extend_schema(self, parent_schema_id: str, name: str, description: str,
                     additional_brick_ids: List[str]) -> SchemaComposition:
        """Create a schema that extends an existing one"""
        if parent_schema_id not in self.schemas:
            raise ValueError(f"Parent schema '{parent_schema_id}' not found")
        
        parent_schema = self.schemas[parent_schema_id]
        
        # Combine parent and new bricks
        all_brick_ids = [parent_schema.root_brick_id] + parent_schema.component_brick_ids + additional_brick_ids
        
        # Create extended schema
        schema = SchemaComposition(
            schema_id=name.lower().replace(" ", "_") + "_" + str(uuid.uuid4())[:8],
            name=name,
            description=description,
            root_brick_id=parent_schema.root_brick_id,
            component_brick_ids=parent_schema.component_brick_ids + additional_brick_ids,
            inheritance_chain=[parent_schema_id] + parent_schema.inheritance_chain,
            interface_flow=parent_schema.interface_flow,
            interface_steps=self._extend_interface_steps(parent_schema.interface_steps, additional_brick_ids),
            relationships=self._analyze_brick_relationships(parent_schema.root_brick_id, parent_schema.component_brick_ids + additional_brick_ids)
        )
        
        self.schemas[schema.schema_id] = schema
        return schema
    
    def create_daisy_chain(self, name: str, description: str, schema_ids: List[str],
                         navigation_rules: Dict[str, Any] = None) -> DaisyChain:
        """Create a daisy-chain of schemas for multi-step interfaces"""
        # Validate schemas exist
        for schema_id in schema_ids:
            if schema_id not in self.schemas:
                raise ValueError(f"Schema '{schema_id}' not found")
        
        chain_id = name.lower().replace(" ", "_") + "_" + str(uuid.uuid4())[:8]
        
        daisy_chain = DaisyChain(
            chain_id=chain_id,
            name=name,
            description=description,
            schemas=schema_ids,
            navigation_rules=navigation_rules or {},
            conditional_logic=self._generate_conditional_logic(schema_ids)
        )
        
        self.daisy_chains[chain_id] = daisy_chain
        return daisy_chain
    
    def get_schema(self, schema_id: str) -> Optional[SchemaComposition]:
        """Get schema by ID"""
        return self.schemas.get(schema_id)
    
    def get_all_schemas(self) -> List[SchemaComposition]:
        """Get all schemas"""
        return list(self.schemas.values())
    
    def get_daisy_chain(self, chain_id: str) -> Optional[DaisyChain]:
        """Get daisy chain by ID"""
        return self.daisy_chains.get(chain_id)
    
    def get_all_daisy_chains(self) -> List[DaisyChain]:
        """Get all daisy chains"""
        return list(self.daisy_chains.values())
    
    def add_component_to_schema(self, schema_id: str, brick_id: str) -> SchemaComposition:
        """Add a component brick to an existing schema"""
        if schema_id not in self.schemas:
            raise ValueError(f"Schema '{schema_id}' not found")
        
        # Validate brick exists
        if not self._validate_bricks_exist([brick_id]):
            raise ValueError(f"Brick '{brick_id}' does not exist")
        
        schema = self.schemas[schema_id]
        
        # Check if brick is already a component
        if brick_id in schema.component_brick_ids:
            raise ValueError(f"Brick '{brick_id}' is already a component of schema '{schema_id}'")
        
        # Add brick to components
        schema.component_brick_ids.append(brick_id)
        
        # Update relationships
        schema.relationships = self._analyze_brick_relationships(schema.root_brick_id, schema.component_brick_ids)
        
        # Update interface steps
        new_step = InterfaceStep(
            step_id=f"step_{len(schema.interface_steps) + 1}",
            name=f"Component {len(schema.interface_steps) + 1}",
            description=f"Added component: {brick_id}",
            brick_ids=[brick_id],
            next_steps=[]
        )
        schema.interface_steps.append(new_step)
        
        # Update modified timestamp
        schema.modified_at = datetime.now().isoformat()
        
        return schema
    
    def export_schema_shacl(self, schema_id: str) -> Dict[str, Any]:
        """Export schema as SHACL"""
        if schema_id not in self.schemas:
            raise ValueError(f"Schema '{schema_id}' not found")
        
        schema = self.schemas[schema_id]
        
        # Get all bricks in schema
        all_brick_ids = [schema.root_brick_id] + schema.component_brick_ids
        bricks_data = []
        
        for brick_id in all_brick_ids:
            result = self.brick_backend.get_brick_details(brick_id)
            if result["status"] == "success":
                bricks_data.append(result["data"])
        
        return {
            "schema_id": schema.schema_id,
            "name": schema.name,
            "description": schema.description,
            "bricks": bricks_data,
            "relationships": schema.relationships,
            "interface_flow": schema.interface_flow.value,
            "interface_steps": [
                {
                    "step_id": step.step_id,
                    "name": step.name,
                    "description": step.description,
                    "brick_ids": step.brick_ids,
                    "next_steps": step.next_steps,
                    "conditions": step.conditions
                }
                for step in schema.interface_steps
            ],
            "metadata": schema.metadata
        }
    
    def export_daisy_chain_config(self, chain_id: str) -> Dict[str, Any]:
        """Export daisy chain configuration for HTML GUI generation"""
        if chain_id not in self.daisy_chains:
            raise ValueError(f"Daisy chain '{chain_id}' not found")
        
        chain = self.daisy_chains[chain_id]
        
        # Get schema data for each step
        schemas_data = []
        for schema_id in chain.schemas:
            schema_data = self.export_schema_shacl(schema_id)
            schemas_data.append(schema_data)
        
        return {
            "chain_id": chain.chain_id,
            "name": chain.name,
            "description": chain.description,
            "schemas": schemas_data,
            "navigation_rules": chain.navigation_rules,
            "conditional_logic": chain.conditional_logic,
            "shared_data": chain.shared_data,
            "ui_theme": chain.ui_theme,
            "metadata": chain.metadata
        }
    
    def generate_interface_config(self, chain_id: str) -> Dict[str, Any]:
        """Generate interface configuration for HTML GUI"""
        if chain_id not in self.daisy_chains:
            raise ValueError(f"Daisy chain '{chain_id}' not found")
        
        chain_config = self.export_daisy_chain_config(chain_id)
        
        # Generate interface-specific configuration
        interface_config = {
            "interface_id": f"interface_{chain_id}",
            "title": chain_config["name"],
            "description": chain_config["description"],
            "steps": [],
            "navigation": {
                "type": "step_wizard",
                "show_progress": True,
                "allow_skip": False,
                "conditional_navigation": bool(chain_config["conditional_logic"])
            },
            "data_flow": {
                "shared_fields": chain_config["shared_data"],
                "field_mapping": self._generate_field_mapping(chain_config["schemas"]),
                "validation_rules": self._collect_validation_rules(chain_config["schemas"])
            },
            "ui_config": {
                "theme": chain_config["ui_theme"] or "default",
                "layout": "vertical",
                "responsive": True,
                "auto_save": True
            }
        }
        
        # Generate step configurations
        for i, schema in enumerate(chain_config["schemas"]):
            step_config = {
                "step_id": f"step_{i+1}",
                "title": schema["name"],
                "description": schema["description"],
                "bricks": schema["bricks"],
                "fields": self._extract_form_fields(schema["bricks"]),
                "validation": self._extract_validation_rules(schema["bricks"]),
                "next_step": f"step_{i+2}" if i < len(chain_config["schemas"]) - 1 else "complete",
                "previous_step": f"step_{i}" if i > 0 else None
            }
            interface_config["steps"].append(step_config)
        
        return interface_config
    
    # Private helper methods
    def _validate_bricks_exist(self, brick_ids: List[str]) -> bool:
        """Validate that all specified bricks exist"""
        for brick_id in brick_ids:
            result = self.brick_backend.get_brick_details(brick_id)
            if result["status"] != "success":
                return False
        return True
    
    def _create_default_interface_steps(self, root_brick_id: str, component_brick_ids: List[str]) -> List[InterfaceStep]:
        """Create default interface steps from bricks"""
        steps = []
        
        # Group bricks by logical categories
        property_bricks = []
        other_bricks = []
        
        for brick_id in component_brick_ids:
            result = self.brick_backend.get_brick_details(brick_id)
            if result["status"] == "success":
                brick_data = result["data"]
                if brick_data["object_type"] == "PropertyShape":
                    property_bricks.append(brick_data)
                else:
                    other_bricks.append(brick_data)
        
        # Create steps
        if property_bricks:
            # Group properties into logical steps (max 5 properties per step)
            for i in range(0, len(property_bricks), 5):
                step_bricks = property_bricks[i:i+5]
                step = InterfaceStep(
                    step_id=f"step_{len(steps)+1}",
                    name=f"Properties {len(steps)+1}",
                    description=f"Enter property information",
                    brick_ids=[brick["brick_id"] for brick in step_bricks],
                    next_steps=[f"step_{len(steps)+2}"]
                )
                steps.append(step)
        
        if other_bricks:
            step = InterfaceStep(
                step_id=f"step_{len(steps)+1}",
                name="Additional Information",
                description="Enter additional details",
                brick_ids=[brick["brick_id"] for brick in other_bricks],
                next_steps=[]
            )
            steps.append(step)
        
        # Fix next steps for the last step
        if steps:
            steps[-1].next_steps = []
        
        return steps
    
    def _analyze_brick_relationships(self, root_brick_id: str, component_brick_ids: List[str]) -> Dict[str, List[str]]:
        """Analyze relationships between bricks"""
        relationships = {}
        
        # Get root brick details
        root_result = self.brick_backend.get_brick_details(root_brick_id)
        if root_result["status"] == "success":
            root_brick = root_result["data"]
            
            # Analyze component bricks
            for brick_id in component_brick_ids:
                comp_result = self.brick_backend.get_brick_details(brick_id)
                if comp_result["status"] == "success":
                    comp_brick = comp_result["data"]
                    
                    # Determine relationship type
                    if comp_brick["object_type"] == "PropertyShape":
                        relationships[brick_id] = ["property_of", root_brick_id]
                    else:
                        relationships[brick_id] = ["related_to", root_brick_id]
        
        return relationships
    
    def _extend_interface_steps(self, parent_steps: List[InterfaceStep], new_brick_ids: List[str]) -> List[InterfaceStep]:
        """Extend interface steps with new bricks"""
        extended_steps = parent_steps.copy()
        
        if new_brick_ids:
            # Add new step for additional bricks
            new_step = InterfaceStep(
                step_id=f"step_{len(extended_steps)+1}",
                name="Extended Information",
                description="Additional information",
                brick_ids=new_brick_ids,
                next_steps=[]
            )
            
            # Update previous step's next steps
            if extended_steps:
                extended_steps[-1].next_steps = [new_step.step_id]
            
            extended_steps.append(new_step)
        
        return extended_steps
    
    def _generate_conditional_logic(self, schema_ids: List[str]) -> Dict[str, Any]:
        """Generate conditional logic for daisy chain"""
        # Basic conditional logic - can be extended
        return {
            "conditions": {},
            "rules": {},
            "defaults": {}
        }
    
    def _generate_field_mapping(self, schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate field mapping between schemas"""
        mapping = {}
        
        for i, schema in enumerate(schemas):
            schema_prefix = f"step_{i+1}"
            for brick in schema["bricks"]:
                brick_id = brick["brick_id"]
                mapping[brick_id] = {
                    "step": schema_prefix,
                    "field_name": brick["name"],
                    "data_type": brick.get("properties", {}).get("datatype", "string")
                }
        
        return mapping
    
    def _collect_validation_rules(self, schemas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Collect all validation rules from schemas"""
        rules = []
        
        for schema in schemas:
            for brick in schema["bricks"]:
                for constraint in brick["constraints"]:
                    rules.append({
                        "brick_id": brick["brick_id"],
                        "constraint_type": constraint["constraint_type"],
                        "value": constraint["value"]
                    })
        
        return rules
    
    def _extract_form_fields(self, bricks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract form fields from bricks for HTML generation"""
        fields = []
        
        for brick in bricks:
            field_config = {
                "field_id": brick["brick_id"],
                "field_name": brick["name"],
                "field_label": brick["name"],
                "field_type": self._map_shacl_to_html_type(brick),
                "required": self._is_required_field(brick),
                "placeholder": f"Enter {brick['name']}",
                "help_text": brick.get("description", ""),
                "validation": self._extract_field_validation(brick)
            }
            fields.append(field_config)
        
        return fields
    
    def _extract_validation_rules(self, bricks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract validation rules for bricks"""
        rules = {}
        
        for brick in bricks:
            brick_rules = []
            for constraint in brick["constraints"]:
                rule = self._map_constraint_to_validation(constraint)
                if rule:
                    brick_rules.append(rule)
            
            rules[brick["brick_id"]] = brick_rules
        
        return rules
    
    def _map_shacl_to_html_type(self, brick: Dict[str, Any]) -> str:
        """Map SHACL datatype to HTML input type"""
        datatype = brick.get("properties", {}).get("datatype", "")
        
        type_mapping = {
            "xsd:string": "text",
            "xsd:integer": "number",
            "xsd:decimal": "number",
            "xsd:boolean": "checkbox",
            "xsd:date": "date",
            "xsd:anyURI": "url",
            "xsd:email": "email"
        }
        
        return type_mapping.get(datatype, "text")
    
    def _is_required_field(self, brick: Dict[str, Any]) -> bool:
        """Check if brick field is required"""
        for constraint in brick["constraints"]:
            if constraint["constraint_type"] == "MinCountConstraintComponent" and constraint["value"] >= 1:
                return True
        return False
    
    def _extract_field_validation(self, brick: Dict[str, Any]) -> Dict[str, Any]:
        """Extract validation configuration for field"""
        validation = {}
        
        for constraint in brick["constraints"]:
            constraint_type = constraint["constraint_type"]
            value = constraint["value"]
            
            if constraint_type == "MinLengthConstraintComponent":
                validation["minlength"] = value
            elif constraint_type == "MaxLengthConstraintComponent":
                validation["maxlength"] = value
            elif constraint_type == "PatternConstraintComponent":
                validation["pattern"] = value
            elif constraint_type == "MinInclusiveConstraintComponent":
                validation["min"] = value
            elif constraint_type == "MaxInclusiveConstraintComponent":
                validation["max"] = value
        
        return validation
    
    def _map_constraint_to_validation(self, constraint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Map SHACL constraint to validation rule"""
        constraint_type = constraint["constraint_type"]
        value = constraint["value"]
        
        validation_mapping = {
            "MinLengthConstraintComponent": {"type": "minlength", "value": value},
            "MaxLengthConstraintComponent": {"type": "maxlength", "value": value},
            "PatternConstraintComponent": {"type": "pattern", "value": value},
            "MinInclusiveConstraintComponent": {"type": "min", "value": value},
            "MaxInclusiveConstraintComponent": {"type": "max", "value": value},
            "MinCountConstraintComponent": {"type": "required", "value": value >= 1}
        }
        
        return validation_mapping.get(constraint_type)
