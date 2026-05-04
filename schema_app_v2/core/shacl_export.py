"""
SHACL Export Module
Export schemas and bricks to SHACL Turtle format
"""

import json
from typing import Dict, List, Any, Optional
from .schema_core import Schema
from .brick_integration import BrickIntegration


class SHACLExporter:
    """Export schemas and bricks to SHACL format"""
    
    def __init__(self, brick_integration: BrickIntegration):
        self.brick_integration = brick_integration
    
    def export_schema(self, schema: Schema, library_name: Optional[str] = None) -> str:
        """Export a complete schema to SHACL Turtle format"""
        lines = []
        
        # Add prefixes
        lines.extend(self._generate_prefixes(schema, library_name))
        lines.append("")
        
        # Export root brick
        if schema.root_brick_id:
            root_shacl = self.brick_integration.export_brick_as_shacl(
                schema.root_brick_id, library_name
            )
            if root_shacl:
                lines.append("# Root Brick")
                lines.append(root_shacl)
                lines.append("")
        
        # Export component bricks hierarchically
        exported_bricks = set()
        root_components = schema.get_ui_root_components()
        
        # Export root-level components first
        for brick_id in root_components:
            self._export_component_hierarchy(
                schema, brick_id, library_name, lines, exported_bricks, 0
            )
        
        # Export any remaining components (orphaned or not in tree)
        for brick_id in schema.component_brick_ids:
            if brick_id not in exported_bricks:
                self._export_component_hierarchy(
                    schema, brick_id, library_name, lines, exported_bricks, 0
                )
        
        # Add schema metadata
        lines.extend(self._generate_schema_metadata(schema))
        
        return "\n".join(lines)
    
    def export_schema_with_flow(self, schema: Schema, library_name: Optional[str] = None) -> str:
        """Export schema with flow configuration to SHACL"""
        lines = []
        
        # Basic schema export
        lines.append(self.export_schema(schema, library_name))
        
        # Add flow configuration as comments
        if schema.flow_config:
            lines.append("")
            lines.append("# Flow Configuration")
            lines.append(f"# Flow Type: {schema.flow_config.flow_type.value}")
            lines.append(f"# Flow Name: {schema.flow_config.name}")
            lines.append(f"# Flow Description: {schema.flow_config.description}")
            lines.append("")
            
            for i, step in enumerate(schema.flow_config.steps):
                lines.append(f"# Step {i+1}: {step.name}")
                lines.append(f"# Description: {step.description}")
                lines.append(f"# Bricks: {', '.join(step.brick_ids)}")
                if step.next_steps:
                    lines.append(f"# Next Steps: {', '.join(step.next_steps)}")
                if step.conditions:
                    lines.append(f"# Conditions: {json.dumps(step.conditions, indent=2)}")
                lines.append("")
        
        return "\n".join(lines)
    
    def export_schema_as_json_ld(self, schema: Schema, library_name: Optional[str] = None) -> Dict[str, Any]:
        """Export schema as JSON-LD format"""
        json_ld = {
            "@context": {
                "sh": "http://www.w3.org/ns/shacl#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "schema": "http://schema.org/"
            },
            "@graph": []
        }
        
        # Export root brick
        if schema.root_brick_id:
            root_brick = self.brick_integration.get_brick_by_id(schema.root_brick_id, library_name)
            if root_brick:
                root_shape = self._brick_to_json_ld(root_brick)
                json_ld["@graph"].append(root_shape)
        
        # Export component bricks
        for brick_id in schema.component_brick_ids:
            brick = self.brick_integration.get_brick_by_id(brick_id, library_name)
            if brick:
                brick_shape = self._brick_to_json_ld(brick)
                json_ld["@graph"].append(brick_shape)
        
        return json_ld
    
    def _generate_prefixes(self, schema: Schema, library_name: Optional[str] = None) -> List[str]:
        """Generate prefix declarations"""
        prefixes = [
            "@prefix sh: <http://www.w3.org/ns/shacl#> .",
            "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
            "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> ."
        ]
        
        # Add prefixes for brick classes
        if schema.root_brick_id:
            root_brick = self.brick_integration.get_brick_by_id(schema.root_brick_id, library_name)
            if root_brick and root_brick.target_class and ":" in root_brick.target_class:
                prefix = root_brick.target_class.split(":")[0]
                prefixes.append(f"@prefix {prefix}: <http://example.org/{prefix}/#> .")
        
        return prefixes
    
    def _generate_schema_metadata(self, schema: Schema) -> List[str]:
        """Generate schema metadata as comments"""
        metadata = [
            "# Schema Metadata",
            f"# Schema ID: {schema.schema_id}",
            f"# Schema Name: {schema.name}",
            f"# Description: {schema.description}",
            f"# Created: {schema.created_at}",
            f"# Updated: {schema.updated_at}",
            f"# Root Brick: {schema.root_brick_id}",
            f"# Component Bricks: {len(schema.component_brick_ids)}",
            f"# Components: {', '.join(schema.component_brick_ids)}",
            ""
        ]
        
        if schema.metadata:
            metadata.append("# Additional Metadata:")
            for key, value in schema.metadata.items():
                metadata.append(f"# {key}: {value}")
            metadata.append("")
        
        return metadata
    
    def _brick_to_json_ld(self, brick) -> Dict[str, Any]:
        """Convert brick to JSON-LD format"""
        shape = {
            "@id": f"#{brick.name}",
            "@type": [
                "sh:NodeShape" if brick.object_type == "NodeShape" else "sh:PropertyShape"
            ]
        }
        
        # Add target class for NodeShape
        if brick.object_type == "NodeShape" and brick.target_class:
            shape["sh:targetClass"] = {
                "@id": brick.target_class
            }
        
        # Add path for PropertyShape
        if brick.object_type == "PropertyShape" and brick.property_path:
            shape["sh:path"] = {
                "@id": brick.property_path
            }
        
        # Add properties
        for prop_name, prop_value in brick.properties.items():
            if prop_name == "datatype":
                shape[f"sh:{prop_name}"] = {
                    "@id": prop_value
                }
            elif prop_name in ["minCount", "maxCount", "minLength", "maxLength"]:
                shape[f"sh:{prop_name}"] = prop_value
            else:
                shape[f"sh:{prop_name}"] = prop_value
        
        # Add constraints
        for constraint in brick.constraints:
            for constraint_type, constraint_value in constraint.items():
                if constraint_type == "pattern":
                    shape["sh:pattern"] = constraint_value
                elif constraint_type in ["minInclusive", "maxInclusive"]:
                    shape[f"sh:{constraint_type}"] = constraint_value
        
        return shape
    
    def validate_shacl_syntax(self, shacl_content: str) -> List[str]:
        """Validate SHACL syntax (basic validation)"""
        issues = []
        lines = shacl_content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Check for basic SHACL syntax
            if 'a sh:' in line and not line.endswith('.'):
                issues.append(f"Line {i}: Missing period at end of statement")
            
            if 'sh:targetClass' in line and not any(prefix in line for prefix in ['@prefix', '<', '>']):
                issues.append(f"Line {i}: Invalid target class format")
            
            if 'sh:path' in line and not any(prefix in line for prefix in ['@prefix', '<', '>']):
                issues.append(f"Line {i}: Invalid property path format")
        
        return issues
    
    def generate_schema_documentation(self, schema: Schema, library_name: Optional[str] = None) -> str:
        """Generate human-readable documentation for schema"""
        doc_lines = []
        
        # Title
        doc_lines.append(f"# Schema Documentation: {schema.name}")
        doc_lines.append("=" * len(f"# Schema Documentation: {schema.name}"))
        doc_lines.append("")
        
        # Basic information
        doc_lines.append("## Basic Information")
        doc_lines.append(f"- **Name**: {schema.name}")
        doc_lines.append(f"- **Description**: {schema.description}")
        doc_lines.append(f"- **ID**: {schema.schema_id}")
        doc_lines.append(f"- **Created**: {schema.created_at}")
        doc_lines.append(f"- **Updated**: {schema.updated_at}")
        doc_lines.append("")
        
        # Root brick
        if schema.root_brick_id:
            doc_lines.append("## Root Brick")
            root_brick = self.brick_integration.get_brick_by_id(schema.root_brick_id, library_name)
            if root_brick:
                doc_lines.append(f"- **Name**: {root_brick.name}")
                doc_lines.append(f"- **Type**: {root_brick.object_type}")
                doc_lines.append(f"- **Target Class**: {root_brick.target_class}")
                doc_lines.append(f"- **Description**: {root_brick.description}")
            doc_lines.append("")
        
        # Component bricks
        if schema.component_brick_ids:
            doc_lines.append("## Component Bricks")
            for i, brick_id in enumerate(schema.component_brick_ids, 1):
                doc_lines.append(f"### {i}. {brick_id}")
                brick = self.brick_integration.get_brick_by_id(brick_id, library_name)
                if brick:
                    doc_lines.append(f"- **Name**: {brick.name}")
                    doc_lines.append(f"- **Type**: {brick.object_type}")
                    if brick.object_type == "PropertyShape":
                        doc_lines.append(f"- **Property Path**: {brick.property_path}")
                    doc_lines.append(f"- **Description**: {brick.description}")
                    
                    if brick.properties:
                        doc_lines.append("- **Properties**:")
                        for prop_name, prop_value in brick.properties.items():
                            doc_lines.append(f"  - {prop_name}: {prop_value}")
                    
                    if brick.constraints:
                        doc_lines.append("- **Constraints**:")
                        for constraint in brick.constraints:
                            for constraint_type, constraint_value in constraint.items():
                                doc_lines.append(f"  - {constraint_type}: {constraint_value}")
                doc_lines.append("")
        
        # Flow configuration
        if schema.flow_config:
            doc_lines.append("## Flow Configuration")
            doc_lines.append(f"- **Flow Type**: {schema.flow_config.flow_type.value}")
            doc_lines.append(f"- **Flow Name**: {schema.flow_config.name}")
            doc_lines.append(f"- **Flow Description**: {schema.flow_config.description}")
            doc_lines.append("")
            
            if schema.flow_config.steps:
                doc_lines.append("### Flow Steps")
                for i, step in enumerate(schema.flow_config.steps, 1):
                    doc_lines.append(f"#### Step {i}: {step.name}")
                    doc_lines.append(f"- **Description**: {step.description}")
                    doc_lines.append(f"- **Bricks**: {', '.join(step.brick_ids)}")
                    if step.next_steps:
                        doc_lines.append(f"- **Next Steps**: {', '.join(step.next_steps)}")
                    if step.conditions:
                        doc_lines.append(f"- **Conditions**: {json.dumps(step.conditions, indent=2)}")
                    doc_lines.append("")
        
        return "\n".join(doc_lines)
    
    def _export_component_hierarchy(self, schema: Schema, brick_id: str, library_name: Optional[str],
                                   lines: List[str], exported_bricks: set, depth: int):
        """Export a component and its children hierarchically"""
        if brick_id in exported_bricks:
            return
        
        # Get brick details
        brick = self.brick_integration.get_brick_by_id(brick_id, library_name)
        if not brick:
            return
        
        # Get UI metadata
        ui_metadata = schema.get_component_ui_metadata(brick_id)
        sequence = ui_metadata.sequence if ui_metadata else None
        
        # Generate hierarchical SHACL
        hierarchical_shacl = self._generate_hierarchical_shacl(
            brick, schema, library_name, sequence, depth
        )
        
        if hierarchical_shacl:
            lines.append(f"# Component: {brick_id} (depth {depth})")
            lines.append(hierarchical_shacl)
            lines.append("")
        
        exported_bricks.add(brick_id)
        
        # Export children recursively
        children = schema.get_ui_children(brick_id)
        for child_id in children:
            self._export_component_hierarchy(
                schema, child_id, library_name, lines, exported_bricks, depth + 1
            )
    
    def _generate_hierarchical_shacl(self, brick, schema: Schema, library_name: Optional[str],
                                   sequence: Optional[int], depth: int) -> str:
        """Generate hierarchical SHACL for a brick"""
        shacl_lines = []
        
        # Prefix declarations (only for root level or first brick)
        if depth == 0:
            shacl_lines.append("@prefix sh: <http://www.w3.org/ns/shacl#> .")
            shacl_lines.append("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .")
            
            if brick.target_class and ":" in brick.target_class:
                prefix = brick.target_class.split(":")[0]
                shacl_lines.append(f"@prefix {prefix}: <http://example.org/{prefix}/#> .")
            
            shacl_lines.append("")
        
        # Shape definition
        if brick.object_type == "NodeShape":
            shacl_lines.append(f"{brick.name} a sh:NodeShape ;")
            if brick.target_class:
                shacl_lines.append(f"    sh:targetClass {brick.target_class} ;")
            
            # Add hierarchical properties for children
            children = schema.get_ui_children(brick.brick_id)
            if children:
                shacl_lines.append("    sh:property [")
                for i, child_id in enumerate(children):
                    child_brick = self.brick_integration.get_brick_by_id(child_id, library_name)
                    if child_brick:
                        if i > 0:
                            shacl_lines.append("    ] ;")
                            shacl_lines.append("    sh:property [")
                        
                        if child_brick.object_type == "PropertyShape":
                            shacl_lines.append(f"        sh:path {child_brick.property_path or child_id} ;")
                            shacl_lines.append(f"        sh:node {child_brick.name} ;")
                        elif child_brick.object_type == "NodeShape":
                            # For nested NodeShapes, create a property shape
                            property_name = f"has{child_brick.name.capitalize()}"
                            shacl_lines.append(f"        sh:path {property_name} ;")
                            shacl_lines.append(f"        sh:node {child_brick.name} ;")
                        
                        # Add UI metadata as SHACL properties
                        child_ui_metadata = schema.get_component_ui_metadata(child_id)
                        if child_ui_metadata:
                            if child_ui_metadata.sequence is not None:
                                shacl_lines.append(f"        sh:order {child_ui_metadata.sequence} ;")
                            if child_ui_metadata.label:
                                shacl_lines.append(f"        sh:name \"{child_ui_metadata.label}\"@en ;")
                            if child_ui_metadata.help_text:
                                shacl_lines.append(f"        sh:description \"{child_ui_metadata.help_text}\"@en ;")
                
                shacl_lines.append("    ] ;")
                
        else:  # PropertyShape
            shacl_lines.append(f"{brick.name} a sh:PropertyShape ;")
            if brick.property_path:
                shacl_lines.append(f"    sh:path {brick.property_path} ;")
            
            # Add properties
            for prop_name, prop_value in brick.properties.items():
                if prop_name == "datatype":
                    shacl_lines.append(f"    sh:datatype {prop_value} ;")
                elif prop_name in ["minCount", "maxCount", "minLength", "maxLength"]:
                    shacl_lines.append(f"    sh:{prop_name} {prop_value} ;")
        
        # Add brick properties and constraints
        for prop_name, prop_value in brick.properties.items():
            if prop_name not in ["datatype", "minCount", "maxCount", "minLength", "maxLength"]:
                shacl_lines.append(f"    sh:{prop_name} {prop_value} ;")
        
        # Add constraints
        for constraint in brick.constraints:
            for constraint_type, constraint_value in constraint.items():
                if constraint_type == "pattern":
                    shacl_lines.append(f"    sh:pattern \"{constraint_value}\" ;")
                elif constraint_type in ["minInclusive", "maxInclusive"]:
                    shacl_lines.append(f"    sh:{constraint_type} {constraint_value} ;")
        
        # Add sh:order if sequence is provided
        if sequence is not None:
            shacl_lines.append(f"    sh:order {sequence} ;")
        
        # Remove trailing semicolon from last line
        if shacl_lines and shacl_lines[-1].endswith(" ;"):
            shacl_lines[-1] = shacl_lines[-1][:-2] + " ."
        
        return "\n".join(shacl_lines)
    
    def export_schema_hierarchical(self, schema: Schema, library_name: Optional[str] = None) -> str:
        """Export schema with explicit hierarchical structure"""
        lines = []
        
        # Add prefixes
        lines.extend(self._generate_prefixes(schema, library_name))
        lines.append("")
        
        # Add comment about hierarchical structure
        lines.append("# Hierarchical SHACL Schema Export")
        lines.append("# Components are organized in tree structure with sh:node references")
        lines.append("")
        
        # Export root brick
        if schema.root_brick_id:
            root_shacl = self.brick_integration.export_brick_as_shacl(
                schema.root_brick_id, library_name
            )
            if root_shacl:
                lines.append("# Root Brick")
                lines.append(root_shacl)
                lines.append("")
        
        # Export hierarchical tree structure
        tree = schema.get_hierarchical_tree(self.brick_integration)
        for parent_id, parent_info in tree.items():
            lines.append(f"# Parent Component: {parent_id}")
            lines.append(f"# Type: {parent_info['brick_type']}")
            lines.append("")
            
            # Export parent brick
            parent_brick = self.brick_integration.get_brick_by_id(parent_id, library_name)
            if parent_brick:
                parent_shacl = self._generate_hierarchical_shacl(
                    parent_brick, schema, library_name, None, 0
                )
                if parent_shacl:
                    lines.append(parent_shacl)
                    lines.append("")
            
            # Export children
            for child_id in parent_info['children']:
                child_brick = self.brick_integration.get_brick_by_id(child_id, library_name)
                if child_brick:
                    child_shacl = self._generate_hierarchical_shacl(
                        child_brick, schema, library_name, None, 1
                    )
                    if child_shacl:
                        lines.append(f"# Child Component: {child_id}")
                        lines.append(child_shacl)
                        lines.append("")
        
        # Add schema metadata
        lines.extend(self._generate_schema_metadata(schema))
        
        return "\n".join(lines)
