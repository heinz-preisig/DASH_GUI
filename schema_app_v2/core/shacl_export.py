"""
SHACL Export Module
Export schemas and bricks to SHACL Turtle format
"""

import os
from typing import List, Any, Optional
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
                lines.append(f"schema:{attach_name} sh:property [")
                lines.append(f"    sh:path {self._format_uri(prop_path)} ;")
                lines.append(f"    sh:node schema:{ref_shape_name} ;")
                lines.append(f"] .")
                lines.append(f"# schema:{ref_shape_name} is defined in schema: {ref_schema_id}")
                lines.append("")

        # Export property groups (sh:PropertyGroup declarations)
        groups_ttl = self.generate_property_groups(schema)
        if groups_ttl:
            lines.append(groups_ttl)

        # Patch root shape: add sh:property [sh:node; sh:group] for grouped components
        if schema.root_brick_id and schema.groups:
            root_brick = self.brick_integration.get_brick_by_id(schema.root_brick_id, library_name)
            if root_brick:
                root_name = f"schema:{self._safe_name(root_brick.name)}"
                patch_lines = [f"# Group assignments on root shape"]
                for brick_id in schema.component_brick_ids:
                    ui = schema.get_component_ui_metadata(brick_id)
                    if not (ui and ui.group_id):
                        continue
                    comp_brick = self.brick_integration.get_brick_by_id(brick_id, library_name)
                    if not comp_brick:
                        continue
                    safe_group = ui.group_id.replace(' ', '_')
                    path = f"schema:has{self._safe_name(comp_brick.name)}"
                    patch_lines.append(f"{root_name} sh:property [")
                    patch_lines.append(f"    sh:path {path} ;")
                    patch_lines.append(f"    sh:node schema:{self._safe_name(comp_brick.name)} ;")
                    patch_lines.append(f'    sh:name "{comp_brick.name}"@en ;')
                    patch_lines.append(f"    sh:group schema:{safe_group} ;")
                    patch_lines.append(f"    sh:order {ui.sequence} ;")
                    patch_lines.append(f"] .")
                    patch_lines.append("")
                if len(patch_lines) > 1:
                    lines.extend(patch_lines)

        # Add schema metadata
        lines.extend(self._generate_schema_metadata(schema))

        return "\n".join(lines)
    
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
        group_id = ui_metadata.group_id if ui_metadata else None
        
        # Generate hierarchical SHACL
        hierarchical_shacl = self._generate_hierarchical_shacl(
            brick, schema, library_name, sequence, depth, group_id
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

    def _safe_name(self, name: str) -> str:
        """Sanitize a name for use in Turtle prefixed names (replace spaces with underscores)"""
        return name.replace(" ", "_") if name else name

    def _format_uri(self, uri: str) -> str:
        """Format a URI for Turtle syntax - full URLs get wrapped in <> brackets"""
        if not uri:
            return uri
        # If it's already a prefixed name (contains : but not ://), return as-is
        if ":" in uri and "://" not in uri:
            return uri
        # If it's a full URL (contains ://), wrap in angle brackets
        if "://" in uri:
            return f"<{uri}>"
        return uri

    def _generate_hierarchical_shacl(self, brick, schema: Schema, library_name: Optional[str],
                                   sequence: Optional[int], depth: int, group_id: Optional[str] = None) -> str:
        """Generate hierarchical SHACL with DASH annotations for a brick"""
        shacl_lines = []

        # All modern bricks are NodeShapes with leaf_properties
        shacl_lines.append(f"schema:{self._safe_name(brick.name)} a sh:NodeShape ;")
        if getattr(brick, 'target_class', ''):
            shacl_lines.append(f"    sh:targetClass {self._format_uri(brick.target_class)} ;")
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
            shacl_lines.append(f"        sh:path {self._format_uri(path)} ;")
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
            if group_id:
                shacl_lines.append(f"        sh:group schema:{group_id.replace(' ', '_')} ;")
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
                    else f"schema:has{self._safe_name(child_brick.name).capitalize()}")
            label = child_ui.label if child_ui and child_ui.label else child_brick.name
            order = child_ui.sequence if child_ui else 0
            shacl_lines.append("    sh:property [")
            shacl_lines.append(f"        sh:path {path} ;")
            shacl_lines.append(f"        sh:node schema:{self._safe_name(child_brick.name)} ;")
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
