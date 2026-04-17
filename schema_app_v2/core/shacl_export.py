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
        
        # Export component bricks
        for brick_id in schema.component_brick_ids:
            component_shacl = self.brick_integration.export_brick_as_shacl(brick_id, library_name)
            if component_shacl:
                lines.append(f"# Component Brick: {brick_id}")
                lines.append(component_shacl)
                lines.append("")
        
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
