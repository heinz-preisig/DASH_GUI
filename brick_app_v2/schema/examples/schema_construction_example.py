#!/usr/bin/env python3
"""
Step 2: Schema Construction Example
Demonstrates brick composition, schema creation, and daisy-chaining for HTML GUI generation
"""

import sys
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shacl_brick_app.core.brick_backend import BrickBackendAPI, BrickEventProcessor
from shacl_brick_app.schema.core.schema_backend import SchemaBackendAPI, SchemaEventProcessor
from shacl_brick_app.schema.core.schema_constructor import InterfaceFlowType

def create_sample_bricks(backend, processor):
    """Create sample bricks for demonstration"""
    print("Creating sample bricks...")
    
    # Person entity brick
    result = processor.process_event({
        "event": "create_nodeshape_brick",
        "brick_id": "person_entity",
        "name": "Person",
        "description": "A person entity with basic information",
        "target_class": "foaf:Person",
        "properties": {"nodeKind": "sh:BlankNodeOrIRI"},
        "tags": ["entity", "person"]
    })
    
    # Name property brick
    result = processor.process_event({
        "event": "create_propertyshape_brick",
        "brick_id": "person_name",
        "name": "Person Name",
        "description": "Full name of the person",
        "path": "foaf:name",
        "properties": {"datatype": "xsd:string"},
        "constraints": [
            {"constraint_type": "MinCountConstraintComponent", "value": 1},
            {"constraint_type": "MinLengthConstraintComponent", "value": 2},
            {"constraint_type": "MaxLengthConstraintComponent", "value": 100}
        ],
        "tags": ["property", "name"]
    })
    
    # Email property brick
    result = processor.process_event({
        "event": "create_propertyshape_brick",
        "brick_id": "person_email",
        "name": "Email Address",
        "description": "Email address of the person",
        "path": "foaf:mbox",
        "properties": {"datatype": "xsd:string"},
        "constraints": [
            {"constraint_type": "MinCountConstraintComponent", "value": 1},
            {"constraint_type": "PatternConstraintComponent", "value": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"}
        ],
        "tags": ["property", "email"]
    })
    
    # Age property brick
    result = processor.process_event({
        "event": "create_propertyshape_brick",
        "brick_id": "person_age",
        "name": "Age",
        "description": "Age of the person",
        "path": "ex:age",
        "properties": {"datatype": "xsd:integer"},
        "constraints": [
            {"constraint_type": "MinInclusiveConstraintComponent", "value": 0},
            {"constraint_type": "MaxInclusiveConstraintComponent", "value": 150}
        ],
        "tags": ["property", "age"]
    })
    
    # Phone property brick
    result = processor.process_event({
        "event": "create_propertyshape_brick",
        "brick_id": "person_phone",
        "name": "Phone Number",
        "description": "Phone number of the person",
        "path": "foaf:phone",
        "properties": {"datatype": "xsd:string"},
        "constraints": [
            {"constraint_type": "PatternConstraintComponent", "value": "^[+]?[0-9]{10,15}$"}
        ],
        "tags": ["property", "phone"]
    })
    
    # Address entity brick
    result = processor.process_event({
        "event": "create_nodeshape_brick",
        "brick_id": "address_entity",
        "name": "Address",
        "description": "Address information",
        "target_class": "ex:Address",
        "properties": {"nodeKind": "sh:BlankNodeOrIRI"},
        "tags": ["entity", "address"]
    })
    
    # Street property brick
    result = processor.process_event({
        "event": "create_propertyshape_brick",
        "brick_id": "address_street",
        "name": "Street",
        "description": "Street address",
        "path": "ex:street",
        "properties": {"datatype": "xsd:string"},
        "constraints": [
            {"constraint_type": "MinCountConstraintComponent", "value": 1}
        ],
        "tags": ["property", "street"]
    })
    
    # City property brick
    result = processor.process_event({
        "event": "create_propertyshape_brick",
        "brick_id": "address_city",
        "name": "City",
        "description": "City name",
        "path": "ex:city",
        "properties": {"datatype": "xsd:string"},
        "constraints": [
            {"constraint_type": "MinCountConstraintComponent", "value": 1}
        ],
        "tags": ["property", "city"]
    })
    
    # Postal code property brick
    result = processor.process_event({
        "event": "create_propertyshape_brick",
        "brick_id": "address_postal",
        "name": "Postal Code",
        "description": "Postal/ZIP code",
        "path": "ex:postalCode",
        "properties": {"datatype": "xsd:string"},
        "constraints": [
            {"constraint_type": "PatternConstraintComponent", "value": "^[0-9]{5}(-[0-9]{4})?$"}
        ],
        "tags": ["property", "postal"]
    })
    
    print("Sample bricks created successfully!")

def demonstrate_basic_schema_creation(schema_backend, schema_processor):
    """Demonstrate basic schema creation"""
    print("\n=== Basic Schema Creation ===")
    
    # Create a basic person schema
    result = schema_processor.process_event({
        "event": "create_schema",
        "name": "Basic Person Profile",
        "description": "Basic person information schema",
        "root_brick_id": "person_entity",
        "component_brick_ids": ["person_name", "person_email", "person_age"],
        "interface_flow": "sequential"
    })
    
    if result["status"] == "success":
        schema_data = result["data"]
        print(f"Created schema: {schema_data['name']}")
        print(f"Root brick: {schema_data['root_brick_id']}")
        print(f"Component bricks: {schema_data['component_brick_ids']}")
        print(f"Interface steps: {len(schema_data['interface_steps'])}")
        
        # Show interface steps
        for i, step in enumerate(schema_data["interface_steps"]):
            print(f"  Step {i+1}: {step['name']} - {step['description']}")
            print(f"    Bricks: {step['brick_ids']}")
        
        return schema_data
    else:
        print(f"Failed to create schema: {result['message']}")
        return None

def demonstrate_template_usage(schema_backend, schema_processor):
    """Demonstrate template-based schema creation"""
    print("\n=== Template-Based Schema Creation ===")
    
    # Create schema from person profile template
    result = schema_processor.process_event({
        "event": "create_schema_from_template",
        "template_name": "person_profile",
        "custom_name": "Complete Person Profile",
        "brick_mappings": {
            "name": "person_name",
            "email": "person_email", 
            "phone": "person_phone",
            "address": "address_entity"
        }
    })
    
    if result["status"] == "success":
        schema_data = result["data"]
        print(f"Created schema from template: {schema_data['name']}")
        print(f"Interface steps: {len(schema_data['interface_steps'])}")
        return schema_data
    else:
        print(f"Failed to create schema from template: {result['message']}")
        return None

def demonstrate_schema_extension(schema_backend, schema_processor):
    """Demonstrate schema extension"""
    print("\n=== Schema Extension ===")
    
    # First create a basic schema
    basic_result = schema_processor.process_event({
        "event": "create_schema",
        "name": "Basic Person",
        "description": "Basic person information",
        "root_brick_id": "person_entity",
        "component_brick_ids": ["person_name", "person_email"]
    })
    
    if basic_result["status"] != "success":
        print(f"Failed to create basic schema: {basic_result['message']}")
        return None
    
    basic_schema = basic_result["data"]
    print(f"Created basic schema: {basic_schema['name']}")
    
    # Extend the schema with additional bricks
    extend_result = schema_processor.process_event({
        "event": "extend_schema",
        "parent_schema_id": basic_schema["schema_id"],
        "name": "Extended Person Profile",
        "description": "Extended person profile with additional information",
        "additional_brick_ids": ["person_age", "person_phone"]
    })
    
    if extend_result["status"] == "success":
        extended_schema = extend_result["data"]
        print(f"Extended schema: {extended_schema['name']}")
        print(f"Inheritance chain: {extended_schema['inheritance_chain']}")
        print(f"Total components: {len(extended_schema['component_brick_ids'])}")
        return extended_schema
    else:
        print(f"Failed to extend schema: {extend_result['message']}")
        return None

def demonstrate_daisy_chaining(schema_backend, schema_processor):
    """Demonstrate daisy chain creation"""
    print("\n=== Daisy Chain Creation ===")
    
    # Create individual schemas
    basic_info_result = schema_processor.process_event({
        "event": "create_schema",
        "name": "Basic Information",
        "description": "Basic person information",
        "root_brick_id": "person_entity",
        "component_brick_ids": ["person_name", "person_email"]
    })
    
    contact_info_result = schema_processor.process_event({
        "event": "create_schema",
        "name": "Contact Information", 
        "description": "Contact details",
        "root_brick_id": "person_entity",
        "component_brick_ids=["person_phone"]
    })
    
    address_info_result = schema_processor.process_event({
        "event": "create_schema",
        "name": "Address Information",
        "description": "Address details",
        "root_brick_id": "address_entity",
        "component_brick_ids": ["address_street", "address_city", "address_postal"]
    })
    
    # Check if all schemas were created successfully
    if not all(r["status"] == "success" for r in [basic_info_result, contact_info_result, address_info_result]):
        print("Failed to create one or more schemas for daisy chain")
        return None
    
    # Create daisy chain
    daisy_chain_result = schema_processor.process_event({
        "event": "create_daisy_chain",
        "name": "Complete Person Registration",
        "description": "Multi-step person registration process",
        "schema_ids": [
            basic_info_result["data"]["schema_id"],
            contact_info_result["data"]["schema_id"],
            address_info_result["data"]["schema_id"]
        ],
        "navigation_rules": {
            "allow_skip": False,
            "show_progress": True
        }
    })
    
    if daisy_chain_result["status"] == "success":
        daisy_chain = daisy_chain_result["data"]
        print(f"Created daisy chain: {daisy_chain['name']}")
        print(f"Schemas in chain: {len(daisy_chain['schemas'])}")
        for i, schema_id in enumerate(daisy_chain['schemas']):
            schema_result = schema_processor.process_event({"event": "get_schema", "schema_id": schema_id})
            if schema_result["status"] == "success":
                schema = schema_result["data"]
                print(f"  Step {i+1}: {schema['name']}")
        return daisy_chain
    else:
        print(f"Failed to create daisy chain: {daisy_chain_result['message']}")
        return None

def demonstrate_interface_generation(schema_constructor, daisy_chain):
    """Demonstrate interface configuration generation"""
    print("\n=== Interface Configuration Generation ===")
    
    # Generate interface configuration
    interface_config = schema_constructor.generate_interface_config(daisy_chain.chain_id)
    
    print(f"Generated interface configuration: {interface_config['interface_id']}")
    print(f"Title: {interface_config['title']}")
    print(f"Total steps: {len(interface_config['steps'])}")
    
    # Show step configurations
    for i, step in enumerate(interface_config['steps']):
        print(f"\nStep {i+1}: {step['title']}")
        print(f"  Description: {step['description']}")
        print(f"  Fields: {len(step['fields'])}")
        
        for field in step['fields']:
            print(f"    - {field['field_name']} ({field['field_type']})")
            if field['required']:
                print(f"      * Required")
            if field['validation']:
                print(f"      * Validation: {field['validation']}")
    
    return interface_config

def demonstrate_shacl_export(schema_constructor, schema):
    """Demonstrate SHACL export"""
    print("\n=== SHACL Export ===")
    
    # Export schema as SHACL
    shacl_data = schema_constructor.export_schema_shacl(schema.schema_id)
    
    print(f"Exported schema: {shacl_data['name']}")
    print(f"Total bricks: {len(shacl_data['bricks'])}")
    print(f"Interface flow: {shacl_data['interface_flow']}")
    
    # Show brick details
    for brick in shacl_data['bricks']:
        print(f"\nBrick: {brick['name']} ({brick['object_type']})")
        print(f"  Description: {brick['description']}")
        if brick['properties']:
            print(f"  Properties: {brick['properties']}")
        if brick['constraints']:
            print(f"  Constraints: {len(brick['constraints'])}")
    
    return shacl_data

def demonstrate_html_form_generation(interface_config):
    """Demonstrate HTML form generation concept"""
    print("\n=== HTML Form Generation Concept ===")
    
    # Generate sample HTML form structure
    html_forms = []
    
    for step in interface_config['steps']:
        step_html = f"""
        <!-- Step {step['step_id']}: {step['title']} -->
        <div class="form-step" id="{step['step_id']}">
            <h2>{step['title']}</h2>
            <p>{step['description']}</p>
            <form>
        """
        
        for field in step['fields']:
            required_attr = 'required' if field['required'] else ''
            validation_attrs = ''
            
            if field['validation']:
                for rule_type, rule_value in field['validation'].items():
                    if rule_type == 'minlength':
                        validation_attrs += f' minlength="{rule_value}"'
                    elif rule_type == 'maxlength':
                        validation_attrs += f' maxlength="{rule_value}"'
                    elif rule_type == 'pattern':
                        validation_attrs += f' pattern="{rule_value}"'
                    elif rule_type == 'min':
                        validation_attrs += f' min="{rule_value}"'
                    elif rule_type == 'max':
                        validation_attrs += f' max="{rule_value}"'
            
            step_html += f"""
                <div class="form-field">
                    <label for="{field['field_id']}">{field['field_label']}</label>
                    <input type="{field['field_type']}" 
                           id="{field['field_id']}" 
                           name="{field['field_id']}"
                           placeholder="{field['placeholder']}"
                           {required_attr}{validation_attrs}>
                    <small class="help-text">{field['help_text']}</small>
                </div>
            """
        
        step_html += """
                <div class="form-actions">
                    <button type="button" class="btn-prev">Previous</button>
                    <button type="submit" class="btn-next">Next</button>
                </div>
            </form>
        </div>
        """
        
        html_forms.append(step_html)
    
    print("Generated HTML form structure:")
    print("=" * 50)
    
    for i, form_html in enumerate(html_forms):
        print(f"Form {i+1}:")
        print(form_html)
        print("-" * 30)
    
    return html_forms

def main():
    """Main demonstration function"""
    print("Step 2: Schema Construction Demonstration (Frontend/Backend Separated)")
    print("=" * 70)
    
    # Initialize backend systems
    brick_backend = BrickBackendAPI("schema_construction_demo")
    brick_processor = BrickEventProcessor(brick_backend)
    schema_backend = SchemaBackendAPI("schema_construction_demo")
    schema_processor = SchemaEventProcessor(schema_backend)
    
    # Ensure active library
    brick_processor.process_event({"event": "set_active_library", "library_name": "default"})
    
    try:
        # Create sample bricks
        create_sample_bricks(brick_backend, brick_processor)
        
        # Demonstrate schema creation
        basic_schema = demonstrate_basic_schema_creation(schema_backend, schema_processor)
        
        # Demonstrate template usage
        template_schema = demonstrate_template_usage(schema_backend, schema_processor)
        
        # Demonstrate schema extension
        extended_schema = demonstrate_schema_extension(schema_backend, schema_processor)
        
        # Demonstrate daisy chaining
        daisy_chain = demonstrate_daisy_chaining(schema_backend, schema_processor)
        
        # Demonstrate interface generation
        if daisy_chain:
            interface_config = demonstrate_interface_generation(schema_backend, schema_processor, daisy_chain)
        
        # Demonstrate SHACL export
        if basic_schema:
            shacl_data = demonstrate_shacl_export(schema_backend, schema_processor, basic_schema)
        
        # Demonstrate HTML form generation concept
        if daisy_chain:
            interface_config_result = schema_processor.process_event({
                "event": "generate_interface_config",
                "chain_id": daisy_chain["chain_id"]
            })
            if interface_config_result["status"] == "success":
                html_forms = demonstrate_html_form_generation(interface_config_result["data"])
        
        print("\n" + "=" * 70)
        print("Step 2 Demonstration Complete! (Frontend/Backend Separated)")
        print("=" * 70)
        
        # Save generated configurations
        output_dir = "schema_construction_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save interface configuration
        if daisy_chain:
            interface_config_result = schema_processor.process_event({
                "event": "generate_interface_config",
                "chain_id": daisy_chain["chain_id"]
            })
            if interface_config_result["status"] == "success":
                with open(f"{output_dir}/interface_config.json", 'w') as f:
                    json.dump(interface_config_result["data"], f, indent=2)
        
        # Save SHACL data
        if basic_schema:
            shacl_result = schema_processor.process_event({
                "event": "export_schema_shacl",
                "schema_id": basic_schema["schema_id"]
            })
            if shacl_result["status"] == "success":
                with open(f"{output_dir}/schema_shacl.json", 'w') as f:
                    json.dump(shacl_result["data"], f, indent=2)
        
        # Save HTML forms
        if daisy_chain:
            interface_config_result = schema_processor.process_event({
                "event": "generate_interface_config",
                "chain_id": daisy_chain["chain_id"]
            })
            if interface_config_result["status"] == "success":
                html_forms = demonstrate_html_form_generation(interface_config_result["data"])
                with open(f"{output_dir}/html_forms.html", 'w') as f:
                    f.write("<!DOCTYPE html>\n<html>\n<head>\n<title>Generated Forms</title>\n")
                    f.write("<style>\n")
                    f.write(".form-step { margin: 20px 0; padding: 20px; border: 1px solid #ccc; }\n")
                    f.write(".form-field { margin: 10px 0; }\n")
                    f.write(".form-field label { display: block; font-weight: bold; }\n")
                    f.write(".form-field input { width: 100%; padding: 5px; }\n")
                    f.write(".help-text { color: #666; font-size: 0.9em; }\n")
                    f.write(".form-actions { margin-top: 20px; }\n")
                    f.write(".btn-prev, .btn-next { padding: 10px 20px; margin-right: 10px; }\n")
                    f.write("</style>\n</head>\n<body>\n")
                    
                    for i, form_html in enumerate(html_forms):
                        f.write(form_html)
                    
                    f.write("</body>\n</html>")
        
        print(f"Generated files saved to: {output_dir}/")
        
    except Exception as e:
        print(f"Error during demonstration: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
