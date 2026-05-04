"""
DASH Integration Module
Generate DASH forms from hierarchical SHACL schemas
"""

import json
from typing import Dict, List, Any, Optional
from .schema_core import Schema
from .brick_integration import BrickIntegration


class DASHFormGenerator:
    """Generate DASH-compatible forms from hierarchical schemas"""
    
    def __init__(self, brick_integration: BrickIntegration):
        self.brick_integration = brick_integration
    
    def generate_dash_form(self, schema: Schema, library_name: Optional[str] = None) -> Dict[str, Any]:
        """Generate a complete DASH form configuration from schema"""
        form_config = {
            "form_title": schema.name,
            "form_description": schema.description,
            "schema_id": schema.schema_id,
            "root_shape": schema.root_brick_id,
            "namespaces": self._generate_namespaces(schema, library_name),
            "shapes": {},
            "property_groups": {},
            "ui_layout": {
                "type": "hierarchical",
                "root_components": schema.get_ui_root_components(),
                "tree_structure": schema.get_hierarchical_tree(self.brick_integration)
            }
        }
        
        # Generate shapes for all components
        for brick_id in schema.component_brick_ids:
            shape = self._generate_dash_shape(schema, brick_id, library_name)
            if shape:
                form_config["shapes"][brick_id] = shape
        
        # Generate property groups from schema groups
        for group_id, group_data in schema.groups.items():
            form_config["property_groups"][group_id] = {
                "label": group_data.get("label", group_id),
                "description": group_data.get("description", ""),
                "order": group_data.get("sequence", 0)
            }
        
        return form_config
    
    def generate_dash_html_form(self, schema: Schema, library_name: Optional[str] = None) -> str:
        """Generate HTML form with DASH markup and structure"""
        html_lines = []
        
        # HTML header with DASH prefixes
        html_lines.extend(self._generate_html_header(schema))
        
        # Form container
        html_lines.append(f'<form id="{schema.schema_id}" class="dash-form">')
        html_lines.append(f'  <h2>{schema.name}</h2>')
        if schema.description:
            html_lines.append(f'  <p class="form-description">{schema.description}</p>')
        
        # Generate hierarchical form structure
        root_components = schema.get_ui_root_components()
        for root_id in root_components:
            self._generate_component_html(
                schema, root_id, library_name, html_lines, depth=0
            )
        
        # Form actions
        html_lines.append('  <div class="form-actions">')
        html_lines.append('    <button type="submit" class="btn-primary">Save</button>')
        html_lines.append('    <button type="reset" class="btn-secondary">Reset</button>')
        html_lines.append('  </div>')
        html_lines.append('</form>')
        
        # JavaScript for dynamic form behavior
        html_lines.extend(self._generate_form_javascript(schema))
        
        return "\n".join(html_lines)
    
    def _generate_dash_shape(self, schema: Schema, brick_id: str, library_name: Optional[str]) -> Optional[Dict[str, Any]]:
        """Generate DASH shape configuration for a brick"""
        brick = self.brick_integration.get_brick_by_id(brick_id, library_name)
        if not brick:
            return None
        
        ui_metadata = schema.get_component_ui_metadata(brick_id)
        shape = {
            "shape_id": brick_id,
            "shape_type": brick.object_type,
            "name": brick.name,
            "target_class": brick.target_class,
            "property_path": getattr(brick, 'property_path', None),
            "properties": {},
            "constraints": brick.constraints or [],
            "ui_metadata": {
                "label": ui_metadata.label if ui_metadata else brick.name,
                "description": ui_metadata.help_text if ui_metadata else brick.description,
                "order": ui_metadata.sequence if ui_metadata else 0,
                "group": ui_metadata.group_id if ui_metadata else None,
                "collapsible": ui_metadata.is_collapsible if ui_metadata else True,
                "visible": ui_metadata.is_visible if ui_metadata else True
            }
        }
        
        # Add brick properties
        if hasattr(brick, 'properties') and brick.properties:
            shape["properties"] = brick.properties
        
        # Add children for hierarchical structures
        children = schema.get_ui_children(brick_id)
        if children:
            shape["children"] = []
            for child_id in children:
                child_shape = self._generate_dash_shape(schema, child_id, library_name)
                if child_shape:
                    shape["children"].append(child_shape)
        
        # Add DASH-specific properties
        if brick.object_type == "NodeShape":
            shape["dash_properties"] = self._generate_node_shape_dash_properties(brick, schema, library_name)
        else:  # PropertyShape
            shape["dash_properties"] = self._generate_property_shape_dash_properties(brick, schema, library_name)
        
        return shape
    
    def _generate_node_shape_dash_properties(self, brick, schema: Schema, library_name: Optional[str]) -> Dict[str, Any]:
        """Generate DASH properties for NodeShape bricks"""
        dash_props = {}
        
        children = schema.get_ui_children(brick.brick_id)
        if children:
            # Generate sh:property statements for children
            properties = []
            for child_id in children:
                child_brick = self.brick_integration.get_brick_by_id(child_id, library_name)
                child_ui_metadata = schema.get_component_ui_metadata(child_id)
                
                if child_brick:
                    prop_statement = {
                        "path": child_brick.property_path or f"has{child_brick.name.capitalize()}",
                        "name": child_ui_metadata.label if child_ui_metadata and child_ui_metadata.label else child_brick.name,
                        "description": child_ui_metadata.help_text if child_ui_metadata else child_brick.description,
                        "order": child_ui_metadata.sequence if child_ui_metadata else 0,
                        "group": child_ui_metadata.group_id if child_ui_metadata else None
                    }
                    
                    # Add node reference for nested structures
                    if child_brick.object_type == "NodeShape":
                        prop_statement["node"] = child_brick.name
                        prop_statement["viewer"] = "dash:DetailsViewer"
                        prop_statement["editor"] = "dash:DetailsEditor"
                    
                    # Add datatype for PropertyShapes
                    if child_brick.object_type == "PropertyShape" and hasattr(child_brick, 'properties'):
                        if "datatype" in child_brick.properties:
                            prop_statement["datatype"] = child_brick.properties["datatype"]
                    
                    properties.append(prop_statement)
            
            dash_props["properties"] = properties
        
        return dash_props
    
    def _generate_property_shape_dash_properties(self, brick, schema: Schema, library_name: Optional[str]) -> Dict[str, Any]:
        """Generate DASH properties for PropertyShape bricks"""
        dash_props = {}
        
        # Add editor/viewer based on datatype
        if hasattr(brick, 'properties') and "datatype" in brick.properties:
            datatype = brick.properties["datatype"]
            dash_props["editor"] = self._get_editor_for_datatype(datatype)
            dash_props["viewer"] = self._get_viewer_for_datatype(datatype)
        
        # Add constraints
        if hasattr(brick, 'constraints') and brick.constraints:
            dash_props["constraints"] = brick.constraints
        
        return dash_props
    
    def _get_editor_for_datatype(self, datatype: str) -> str:
        """Get appropriate DASH editor for datatype"""
        datatype_mapping = {
            "xsd:string": "dash:TextAreaEditor" if True else "dash:TextFieldEditor",  # Could check for multi-line
            "xsd:integer": "dash:IntegerFieldEditor",
            "xsd:decimal": "dash:DecimalFieldEditor",
            "xsd:boolean": "dash:BooleanEditor",
            "xsd:date": "dash:DateEditor",
            "xsd:dateTime": "dash:DateTimeEditor",
            "xsd:anyURI": "dash:URLEditor",
            "rdf:HTML": "dash:HTMLEditor",
            "rdf:langString": "dash:LanguageStringEditor"
        }
        return datatype_mapping.get(datatype, "dash:TextFieldEditor")
    
    def _get_viewer_for_datatype(self, datatype: str) -> str:
        """Get appropriate DASH viewer for datatype"""
        datatype_mapping = {
            "xsd:string": "dash:TextFieldViewer",
            "xsd:integer": "dash:IntegerFieldViewer", 
            "xsd:decimal": "dash:DecimalFieldViewer",
            "xsd:boolean": "dash:BooleanViewer",
            "xsd:date": "dash:DateViewer",
            "xsd:dateTime": "dash:DateTimeViewer",
            "xsd:anyURI": "dash:URLViewer",
            "rdf:HTML": "dash:HTMLViewer",
            "rdf:langString": "dash:LanguageStringViewer"
        }
        return datatype_mapping.get(datatype, "dash:TextFieldViewer")
    
    def _generate_namespaces(self, schema: Schema, library_name: Optional[str]) -> Dict[str, str]:
        """Generate namespace mappings for DASH form"""
        namespaces = {
            "sh": "http://www.w3.org/ns/shacl#",
            "dash": "http://datashapes.org/dash#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
        }
        
        # Add namespaces from bricks
        if schema.root_brick_id:
            root_brick = self.brick_integration.get_brick_by_id(schema.root_brick_id, library_name)
            if root_brick and root_brick.target_class and ":" in root_brick.target_class:
                prefix = root_brick.target_class.split(":")[0]
                namespaces[prefix] = f"http://example.org/{prefix}/#"
        
        return namespaces
    
    def _generate_html_header(self, schema: Schema) -> List[str]:
        """Generate HTML header with DASH prefixes and styling"""
        header = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "    <meta charset='UTF-8'>",
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"    <title>{schema.name} - DASH Form</title>",
            "    <style>",
            self._get_dash_css(),
            "    </style>",
            "</head>",
            "<body>"
        ]
        return header
    
    def _generate_component_html(self, schema: Schema, brick_id: str, library_name: Optional[str], 
                                html_lines: List[str], depth: int):
        """Generate HTML for a component and its children"""
        brick = self.brick_integration.get_brick_by_id(brick_id, library_name)
        if not brick:
            return
        
        ui_metadata = schema.get_component_ui_metadata(brick_id)
        indent = "  " * (depth + 1)
        
        # Component container
        container_class = f"component depth-{depth}"
        if ui_metadata and ui_metadata.is_collapsible:
            container_class += " collapsible"
        
        html_lines.append(f'{indent}<div class="{container_class}" data-brick-id="{brick_id}">')
        
        # Component header/label
        label = ui_metadata.label if ui_metadata and ui_metadata.label else brick.name
        if depth > 0:
            html_lines.append(f'{indent}  <h{3 + min(depth, 3)} class="component-label">{label}</h{3 + min(depth, 3)}>')
        else:
            html_lines.append(f'{indent}  <h3 class="component-label">{label}</h3>')
        
        # Help text
        if ui_metadata and ui_metadata.help_text:
            html_lines.append(f'{indent}  <p class="help-text">{ui_metadata.help_text}</p>')
        
        # Generate fields for PropertyShape or children for NodeShape
        if brick.object_type == "PropertyShape":
            self._generate_property_fields(brick, ui_metadata, html_lines, depth + 1)
        else:  # NodeShape
            children = schema.get_ui_children(brick_id)
            if children:
                for child_id in children:
                    self._generate_component_html(schema, child_id, library_name, html_lines, depth + 1)
        
        html_lines.append(f'{indent}</div>')
    
    def _generate_property_fields(self, brick, ui_metadata, html_lines: List[str], depth: int):
        """Generate HTML input fields for a PropertyShape"""
        indent = "  " * (depth + 1)
        field_name = brick.property_path or brick.name
        field_label = ui_metadata.label if ui_metadata and ui_metadata.label else brick.name
        
        # Determine input type based on datatype
        input_type = "text"
        if hasattr(brick, 'properties') and "datatype" in brick.properties:
            datatype = brick.properties["datatype"]
            input_type = self._get_html_input_type(datatype)
        
        html_lines.append(f'{indent}<div class="field-group">')
        html_lines.append(f'{indent}  <label for="{field_name}">{field_label}:</label>')
        html_lines.append(f'{indent}  <input type="{input_type}" id="{field_name}" name="{field_name}" class="form-field">')
        
        # Add validation attributes from constraints
        if hasattr(brick, 'constraints') and brick.constraints:
            for constraint in brick.constraints:
                for constraint_type, constraint_value in constraint.items():
                    if constraint_type == "minLength":
                        html_lines.append(f'{indent}  <input type="hidden" name="{field_name}_minLength" value="{constraint_value}">')
                    elif constraint_type == "maxLength":
                        html_lines.append(f'{indent}  <input type="hidden" name="{field_name}_maxLength" value="{constraint_value}">')
                    elif constraint_type == "pattern":
                        html_lines.append(f'{indent}  <input type="hidden" name="{field_name}_pattern" value="{constraint_value}">')
        
        html_lines.append(f'{indent}</div>')
    
    def _get_html_input_type(self, datatype: str) -> str:
        """Get HTML input type for SHACL datatype"""
        type_mapping = {
            "xsd:string": "text",
            "xsd:integer": "number",
            "xsd:decimal": "number",
            "xsd:boolean": "checkbox",
            "xsd:date": "date",
            "xsd:dateTime": "datetime-local",
            "xsd:anyURI": "url"
        }
        return type_mapping.get(datatype, "text")
    
    def _get_dash_css(self) -> str:
        """Get CSS styling for DASH forms"""
        return """
        .dash-form {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-family: Arial, sans-serif;
        }
        
        .component {
            margin: 15px 0;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
        }
        
        .component.depth-0 {
            background-color: #ffffff;
            border-color: #007bff;
        }
        
        .component.depth-1 {
            margin-left: 20px;
            background-color: #f0f8ff;
        }
        
        .component.depth-2 {
            margin-left: 40px;
            background-color: #e6f3ff;
        }
        
        .component-label {
            margin-top: 0;
            color: #333;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
        }
        
        .field-group {
            margin: 10px 0;
        }
        
        .field-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .form-field {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 3px;
        }
        
        .form-field:focus {
            border-color: #007bff;
            outline: none;
        }
        
        .help-text {
            font-style: italic;
            color: #666;
            margin-bottom: 10px;
        }
        
        .form-actions {
            margin-top: 20px;
            text-align: right;
        }
        
        .btn-primary {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        
        .btn-secondary {
            background-color: #6c757d;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            margin-left: 10px;
        }
        
        .collapsible {
            position: relative;
        }
        
        .collapsible::before {
            content: "▼";
            position: absolute;
            left: -15px;
            top: 10px;
            cursor: pointer;
        }
        
        .collapsed::before {
            content: "▶";
        }
        """
    
    def _generate_form_javascript(self, schema: Schema) -> List[str]:
        """Generate JavaScript for dynamic form behavior"""
        js = [
            "</body>",
            "</html>",
            "<script>",
            "// DASH Form JavaScript",
            "document.addEventListener('DOMContentLoaded', function() {",
            "    // Handle collapsible components",
            "    const collapsibles = document.querySelectorAll('.collapsible');",
            "    collapsibles.forEach(function(elem) {",
            "        elem.addEventListener('click', function(e) {",
            "            if (e.target === elem || elem.contains(e.target)) {",
            "                elem.classList.toggle('collapsed');",
            "            }",
            "        });",
            "    });",
            "    ",
            "    // Form validation",
            "    const form = document.querySelector('.dash-form');",
            "    if (form) {",
            "        form.addEventListener('submit', function(e) {",
            "            if (!validateForm()) {",
            "                e.preventDefault();",
            "            }",
            "        });",
            "    }",
            "    ",
            "    function validateForm() {",
            "        const fields = document.querySelectorAll('.form-field');",
            "        let isValid = true;",
            "        ",
            "        fields.forEach(function(field) {",
            "            const name = field.name;",
            "            const value = field.value;",
            "            ",
            "            // Check minLength",
            "            const minLength = document.querySelector(name + '_minLength');",
            "            if (minLength && value.length < parseInt(minLength.value)) {",
            "                field.setCustomValidity('Minimum length is ' + minLength.value);",
            "                isValid = false;",
            "            }",
            "            ",
            "            // Check maxLength",
            "            const maxLength = document.querySelector(name + '_maxLength');",
            "            if (maxLength && value.length > parseInt(maxLength.value)) {",
            "                field.setCustomValidity('Maximum length is ' + maxLength.value);",
            "                isValid = false;",
            "            }",
            "            ",
            "            // Check pattern",
            "            const pattern = document.querySelector(name + '_pattern');",
            "            if (pattern && !new RegExp(pattern.value).test(value)) {",
            "                field.setCustomValidity('Invalid format');",
            "                isValid = false;",
            "            }",
            "        });",
            "        ",
            "        return isValid;",
            "    }",
            "});",
            "</script>"
        ]
        return js
