"""
SHACL Export Module
Export schemas and bricks to SHACL Turtle format
"""

import json
import os
from typing import Dict, List, Any, Optional
from .schema_core import Schema
from .brick_integration import BrickIntegration


class SHACLExporter:
    """Export schemas and bricks to SHACL format"""
    
    def __init__(self, brick_integration: BrickIntegration):
        self.brick_integration = brick_integration

    # ── High-level convenience ─────────────────────────────────────────────

    def build_form_html(self, schema: Schema, turtle: str) -> str:
        """Build a self-contained shacl-form HTML page with the Turtle embedded."""
        escaped = turtle.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
        desc_html = f'<p>{schema.description}</p>' if schema.description else ''
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{schema.name} \u2014 Form</title>
  <script src="https://cdn.jsdelivr.net/npm/@ulb-darmstadt/shacl-form/dist/bundle.js" type="module"></script>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 860px; margin: 40px auto; padding: 0 20px; }}
    h1 {{ font-size: 1.4rem; color: #333; border-bottom: 2px solid #007bff; padding-bottom: 8px; }}
    .actions {{ margin-top: 20px; display: flex; gap: 10px; }}
    button {{ padding: 9px 18px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }}
    .btn-submit {{ background: #007bff; color: white; }}
    .btn-reset  {{ background: #6c757d; color: white; }}
  </style>
</head>
<body>
  <h1>{schema.name}</h1>
  {desc_html}
  <shacl-form id="shacl-form" data-collapse="open"></shacl-form>
  <div class="actions">
    <button class="btn-submit" onclick="submitForm()">Review &amp; Submit</button>
    <button class="btn-reset" onclick="document.getElementById('shacl-form').reset()">Reset</button>
  </div>
  <pre id="output" style="display:none; background:#f4f4f4; padding:16px; border-radius:4px; font-size:12px; margin-top:20px; white-space:pre-wrap;"></pre>
  <script type="module">
    const form = document.getElementById('shacl-form');
    form.setAttribute('data-shapes', `{escaped}`);
    window.submitForm = async () => {{
      const valid = await form.validate(false);
      if (!valid) return;
      const out = document.getElementById('output');
      out.textContent = form.serialize();
      out.style.display = 'block';
      out.scrollIntoView({{behavior: 'smooth'}});
    }};
  </script>
</body>
</html>"""

    def export_all(self, schema: Schema, output_dir: str, library_name: Optional[str] = None) -> None:
        """Write <schema_id>.ttl and <schema_id>_form.html to output_dir."""
        os.makedirs(output_dir, exist_ok=True)
        turtle = self.export_schema(schema, library_name)
        with open(os.path.join(output_dir, f"{schema.schema_id}.ttl"), 'w') as f:
            f.write(turtle)
        with open(os.path.join(output_dir, f"{schema.schema_id}_form.html"), 'w') as f:
            f.write(self.build_form_html(schema, turtle))

    # ── Schema export ──────────────────────────────────────────────────────

    def export_schema(self, schema: Schema, library_name: Optional[str] = None) -> str:
        """Export a complete schema to SHACL Turtle format"""
        lines = []
        
        # Add prefixes
        lines.extend(self._generate_prefixes(schema, library_name))
        lines.append("")
        
        # Export all shapes using _generate_hierarchical_shacl (consistent schema: prefix)
        exported_bricks = set()

        # Root brick first
        if schema.root_brick_id:
            root_brick = self.brick_integration.get_brick_by_id(schema.root_brick_id, library_name)
            if root_brick:
                lines.append("# Root Shape")
                lines.append(self._generate_hierarchical_shacl(root_brick, schema, library_name, None, 0))
                lines.append("")
                exported_bricks.add(schema.root_brick_id)

        # Component bricks hierarchically
        root_components = schema.get_ui_root_components()
        for brick_id in root_components:
            self._export_component_hierarchy(
                schema, brick_id, library_name, lines, exported_bricks, 0
            )

        # Any remaining components (orphaned or not in tree)
        for brick_id in schema.component_brick_ids:
            if brick_id not in exported_bricks:
                self._export_component_hierarchy(
                    schema, brick_id, library_name, lines, exported_bricks, 0
                )

        # Export schema references as sh:property [ sh:path ... ; sh:node ... ]
        if schema.schema_refs:
            lines.append("# Schema References (sh:node)")
            for ref in schema.schema_refs:
                ref_schema_id = ref["schema_id"]
                prop_path = ref.get("property_path", "")
                label = ref.get("label", ref_schema_id)
                attach_brick_id = ref.get("attach_to_brick_id", "")
                attach_brick = self.brick_integration.get_brick_by_id(attach_brick_id)
                attach_name = attach_brick.name.replace(" ", "_") if attach_brick else attach_brick_id
                ref_shape_name = label.replace(" ", "_")
                lines.append(f"# Reference: {label} attached to {attach_name} via {prop_path}")
                lines.append(f"<{attach_name}Shape> sh:property [")
                lines.append(f"    sh:path {prop_path} ;")
                lines.append(f"    sh:node <{ref_shape_name}Shape> ;")
                lines.append(f"] .")
                lines.append(f"# <{ref_shape_name}Shape> is defined in schema: {ref_schema_id}")
                lines.append("")

        # Export property groups (sh:PropertyGroup with DASH grouping)
        groups_ttl = self.generate_property_groups(schema)
        if groups_ttl:
            lines.append(groups_ttl)

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
            "@prefix dash: <http://datashapes.org/dash#> .",
            "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
            "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
            f"@prefix schema: <http://example.org/schema/{schema.schema_id}/> .",
        ]

        # Collect prefixes from all bricks: target_class + leaf_property paths
        seen_prefixes = set()
        reserved = {"sh", "dash", "xsd", "rdf", "rdfs", "schema"}
        all_brick_ids = ([schema.root_brick_id] if schema.root_brick_id else []) + schema.component_brick_ids
        for brick_id in all_brick_ids:
            brick = self.brick_integration.get_brick_by_id(brick_id, library_name)
            if not brick:
                continue
            candidates = []
            if getattr(brick, 'target_class', '') and ":" in brick.target_class:
                candidates.append(brick.target_class.split(":")[0])
            for lp in (getattr(brick, 'leaf_properties', []) or []):
                path = lp.get('path', '')
                if path and ":" in path:
                    candidates.append(path.split(":")[0])
            for prefix in candidates:
                if prefix and prefix not in seen_prefixes and prefix not in reserved:
                    prefixes.append(f"@prefix {prefix}: <http://example.org/{prefix}/#> .")
                    seen_prefixes.add(prefix)

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
    
    def _get_dash_editor(self, datatype: str) -> str:
        """Map xsd datatype to dash:editor IRI"""
        mapping = {
            "xsd:string": "dash:TextFieldEditor",
            "xsd:integer": "dash:IntegerFieldEditor",
            "xsd:decimal": "dash:DecimalFieldEditor",
            "xsd:boolean": "dash:BooleanSelectEditor",
            "xsd:date": "dash:DatePickerEditor",
            "xsd:dateTime": "dash:DateTimePickerEditor",
            "xsd:anyURI": "dash:URIEditor",
            "rdf:HTML": "dash:TextAreaEditor",
            "rdf:langString": "dash:TextAreaEditor",
        }
        return mapping.get(datatype, "dash:TextFieldEditor")

    def _get_dash_viewer(self, datatype: str) -> str:
        """Map xsd datatype to dash:viewer IRI"""
        mapping = {
            "xsd:string": "dash:LabelViewer",
            "xsd:integer": "dash:LabelViewer",
            "xsd:decimal": "dash:LabelViewer",
            "xsd:boolean": "dash:BooleanViewer",
            "xsd:date": "dash:LabelViewer",
            "xsd:dateTime": "dash:LabelViewer",
            "xsd:anyURI": "dash:URIViewer",
            "rdf:HTML": "dash:HTMLViewer",
            "rdf:langString": "dash:LabelViewer",
        }
        return mapping.get(datatype, "dash:LabelViewer")

    def generate_property_groups(self, schema: Schema) -> str:
        """Generate sh:PropertyGroup declarations for schema groups"""
        if not schema.groups:
            return ""
        lines = ["# Property Groups"]
        for group_id, group_data in schema.groups.items():
            safe_id = group_id.replace(" ", "_")
            label = group_data.get("label", group_id)
            order = group_data.get("sequence", 0)
            lines.append(f"schema:{safe_id} a sh:PropertyGroup ;")
            lines.append(f'    rdfs:label "{label}" ;')
            lines.append(f"    sh:order {order} .")
            lines.append("")
        return "\n".join(lines)

    def _generate_hierarchical_shacl(self, brick, schema: Schema, library_name: Optional[str],
                                   sequence: Optional[int], depth: int) -> str:
        """Generate hierarchical SHACL with DASH annotations for a brick"""
        shacl_lines = []

        # All modern bricks are NodeShapes with leaf_properties
        shacl_lines.append(f"schema:{brick.name} a sh:NodeShape ;")
        if getattr(brick, 'target_class', ''):
            shacl_lines.append(f"    sh:targetClass {brick.target_class} ;")
        if brick.name:
            shacl_lines.append(f'    rdfs:label "{brick.name}" ;')
        if getattr(brick, 'description', ''):
            escaped = brick.description.replace('"', '\\"')
            shacl_lines.append(f'    rdfs:comment "{escaped}" ;')

        # Emit sh:property for each leaf_property (actual form fields)
        leaf_props = getattr(brick, 'leaf_properties', []) or []
        for order, lp in enumerate(leaf_props):
            path = lp.get('path', '')
            label = lp.get('label', path)
            datatype = lp.get('datatype', 'xsd:string')
            min_count = lp.get('min_count', 0)
            max_count = lp.get('max_count', None)
            description = lp.get('description', '')
            in_values = lp.get('in_values', [])
            min_incl = lp.get('min_inclusive', None)
            max_incl = lp.get('max_inclusive', None)
            if not path:
                continue
            shacl_lines.append("    sh:property [")
            shacl_lines.append(f"        sh:path {path} ;")
            shacl_lines.append(f'        sh:name "{label}"@en ;')
            if description:
                shacl_lines.append(f'        sh:description "{description}"@en ;')
            shacl_lines.append(f"        sh:datatype {datatype} ;")
            if min_count is not None:
                shacl_lines.append(f"        sh:minCount {min_count} ;")
            if max_count is not None:
                shacl_lines.append(f"        sh:maxCount {max_count} ;")
            if in_values:
                vals = " ".join(f'"{v}"' for v in in_values)
                shacl_lines.append(f"        sh:in ({vals}) ;")
            if min_incl is not None:
                shacl_lines.append(f"        sh:minInclusive {min_incl} ;")
            if max_incl is not None:
                shacl_lines.append(f"        sh:maxInclusive {max_incl} ;")
            shacl_lines.append(f"        sh:order {order} ;")
            shacl_lines.append(f"        dash:editor {self._get_dash_editor(datatype)} ;")
            shacl_lines.append(f"        dash:viewer {self._get_dash_viewer(datatype)} ;")
            shacl_lines.append("    ] ;")

        # Emit sh:property for nested child NodeShape bricks (schema-level nesting)
        children = schema.get_ui_children(brick.brick_id)
        for child_id in children:
            child_brick = self.brick_integration.get_brick_by_id(child_id, library_name)
            if not child_brick:
                continue
            child_ui = schema.get_component_ui_metadata(child_id)
            edge = schema.get_edge_to(child_id) if hasattr(schema, 'get_edge_to') else None
            path = (edge.path_iri if edge and edge.path_iri
                    else f"schema:has{child_brick.name.capitalize()}")
            label = child_ui.label if child_ui and child_ui.label else child_brick.name
            order = child_ui.sequence if child_ui else 0
            shacl_lines.append("    sh:property [")
            shacl_lines.append(f"        sh:path {path} ;")
            shacl_lines.append(f"        sh:node schema:{child_brick.name} ;")
            shacl_lines.append(f'        sh:name "{label}"@en ;')
            if child_ui and child_ui.help_text:
                shacl_lines.append(f'        sh:description "{child_ui.help_text}"@en ;')
            shacl_lines.append(f"        sh:order {order} ;")
            if child_ui and child_ui.group_id:
                shacl_lines.append(f"        sh:group schema:{child_ui.group_id.replace(' ', '_')} ;")
            if edge:
                if edge.min_count is not None:
                    shacl_lines.append(f"        sh:minCount {edge.min_count} ;")
                if edge.max_count is not None:
                    shacl_lines.append(f"        sh:maxCount {edge.max_count} ;")
            shacl_lines.append("        dash:editor dash:DetailsEditor ;")
            shacl_lines.append("        dash:viewer dash:DetailsViewer ;")
            shacl_lines.append("    ] ;")

        # sh:order at shape level
        if sequence is not None:
            shacl_lines.append(f"    sh:order {sequence} ;")

        # Remove trailing semicolon on last line → period
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
