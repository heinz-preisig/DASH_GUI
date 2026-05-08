#!/usr/bin/env python3
"""
Test Tree Structure and DASH Integration
Test hierarchical schemas with complex nested structures
"""

import sys
import os
from pathlib import Path

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'shared_libraries'))

# Import required modules
from core.schema_core import SchemaCore, Schema, UIMetadata
from core.brick_integration import BrickIntegration
from core.shacl_export import SHACLExporter
from core.dash_integration import DASHFormGenerator


def create_test_hierarchical_schema():
    """Create a test schema with complex hierarchical structure"""
    print("Creating test hierarchical schema...")
    
    # Initialize schema core
    schema_core = SchemaCore()
    
    # Create schema
    schema = schema_core.create_schema(
        name="Product Catalog",
        description="Complex product schema with nested structures",
        root_brick_id="ProductNode"
    )
    
    # Add component bricks (simulating hierarchical structure)
    component_bricks = [
        "productName",           # Property
        "productDescription",    # Property  
        "company",               # NodeShape (parent)
        "companyName",           # Property (child of company)
        "companyLogo",           # Property (child of company)
        "address",               # NodeShape (child of company)
        "streetAddress",         # Property (child of address)
        "houseNumber",           # Property (child of address)
        "zipCode",               # Property (child of address)
        "town",                  # Property (child of address)
        "country",               # Property (child of address)
        "properties",            # Grouping node
        "physicalProperties",    # NodeShape (child of properties)
        "weight",                # Property (child of physicalProperties)
        "dimensions",           # Property (child of physicalProperties)
        "looks",                 # NodeShape (child of properties)
        "color",                 # Property (child of looks)
        "material",              # Property (child of looks)
    ]
    
    for brick_id in component_bricks:
        schema_core.add_component_brick(brick_id)
    
    # Set up hierarchical relationships
    # Company structure
    schema.set_component_parent("companyName", "company")
    schema.set_component_parent("companyLogo", "company")
    schema.set_component_parent("address", "company")
    
    # Address structure (nested under company)
    schema.set_component_parent("streetAddress", "address")
    schema.set_component_parent("houseNumber", "address")
    schema.set_component_parent("zipCode", "address")
    schema.set_component_parent("town", "address")
    schema.set_component_parent("country", "address")
    
    # Properties grouping structure
    schema.set_component_parent("physicalProperties", "properties")
    schema.set_component_parent("looks", "properties")
    
    # Physical properties structure
    schema.set_component_parent("weight", "physicalProperties")
    schema.set_component_parent("dimensions", "physicalProperties")
    
    # Looks structure
    schema.set_component_parent("color", "looks")
    schema.set_component_parent("material", "looks")
    
    # Set UI metadata for better organization
    schema.set_component_ui_metadata("company", UIMetadata(
        sequence=1, label="Company Information", help_text="Company details"
    ))
    schema.set_component_ui_metadata("address", UIMetadata(
        sequence=2, label="Address", help_text="Company address information"
    ))
    schema.set_component_ui_metadata("properties", UIMetadata(
        sequence=3, label="Product Properties", help_text="Physical and visual properties"
    ))
    
    # Create groups
    schema.create_group("basic_info", "Basic Information", "Core product details", 0)
    schema.create_group("company_info", "Company Information", "Manufacturer details", 1)
    schema.create_group("properties_info", "Properties", "Product characteristics", 2)
    
    # Add components to groups
    schema.add_component_to_group("productName", "basic_info")
    schema.add_component_to_group("productDescription", "basic_info")
    schema.add_component_to_group("company", "company_info")
    schema.add_component_to_group("properties", "properties_info")
    
    # Set sequences for ordering
    schema.set_component_sequence("productName", 0)
    schema.set_component_sequence("productDescription", 1)
    schema.set_component_sequence("company", 2)
    schema.set_component_sequence("properties", 3)
    
    return schema


def test_tree_structure_validation(schema):
    """Test tree structure validation"""
    print("\n=== Testing Tree Structure Validation ===")
    
    validation_result = schema.validate_tree_structure()
    
    print(f"Tree structure valid: {validation_result['valid']}")
    print(f"Total components: {validation_result['tree_stats']['total_components']}")
    print(f"Root components: {validation_result['tree_stats']['root_components']}")
    print(f"Max depth: {validation_result['tree_stats']['max_depth']}")
    
    if validation_result['issues']:
        print("Issues found:")
        for issue in validation_result['issues']:
            print(f"  - {issue}")
    
    if validation_result['warnings']:
        print("Warnings:")
        for warning in validation_result['warnings']:
            print(f"  - {warning}")
    
    return validation_result['valid']


def test_tree_navigation(schema):
    """Test tree navigation methods"""
    print("\n=== Testing Tree Navigation ===")
    
    # Test root components
    root_components = schema.get_ui_root_components()
    print(f"Root components: {root_components}")
    
    # Test tree depth
    for brick_id in schema.component_brick_ids[:5]:  # Test first 5 components
        depth = schema.get_tree_depth(brick_id)
        path = schema.get_component_path(brick_id)
        print(f"Component {brick_id}: depth={depth}, path={' -> '.join(path)}")
    
    # Test tree levels
    for level in range(3):
        components_at_level = schema.get_tree_level(level)
        print(f"Level {level} components: {components_at_level}")
    
    # Test leaf components
    leaf_components = schema.get_leaf_components()
    print(f"Leaf components: {leaf_components[:10]}...")  # Show first 10
    
    # Test nested components
    if "company" in schema.component_brick_ids:
        nested_under_company = schema.get_nested_components("company")
        print(f"Components nested under 'company': {nested_under_company}")
    
    # Test ancestor relationship
    if "company" in schema.component_brick_ids and "streetAddress" in schema.component_brick_ids:
        is_ancestor = schema.is_ancestor("company", "streetAddress")
        print(f"'company' is ancestor of 'streetAddress': {is_ancestor}")


def test_hierarchical_shacl_export(schema, brick_integration):
    """Test hierarchical SHACL export"""
    print("\n=== Testing Hierarchical SHACL Export ===")
    
    try:
        shacl_exporter = SHACLExporter(brick_integration)
        
        # Test regular export
        print("Testing regular SHACL export...")
        regular_shacl = shacl_exporter.export_schema(schema)
        print(f"Regular SHACL export length: {len(regular_shacl)} characters")
        
        # Test hierarchical export
        print("Testing hierarchical SHACL export...")
        hierarchical_shacl = shacl_exporter.export_schema_hierarchical(schema)
        print(f"Hierarchical SHACL export length: {len(hierarchical_shacl)} characters")
        
        # Save to files for inspection
        os.makedirs("test_output", exist_ok=True)
        
        with open("test_output/regular_shacl.ttl", "w") as f:
            f.write(regular_shacl)
        print("Saved regular SHACL to test_output/regular_shacl.ttl")
        
        with open("test_output/hierarchical_shacl.ttl", "w") as f:
            f.write(hierarchical_shacl)
        print("Saved hierarchical SHACL to test_output/hierarchical_shacl.ttl")
        
        return True
        
    except Exception as e:
        print(f"SHACL export failed: {e}")
        return False


def test_dash_form_generation(schema, brick_integration):
    """Test DASH form generation"""
    print("\n=== Testing DASH Form Generation ===")
    
    try:
        dash_generator = DASHFormGenerator(brick_integration)
        
        # Test DASH form configuration
        print("Generating DASH form configuration...")
        dash_config = dash_generator.generate_dash_form(schema)
        
        print(f"DASH form has {len(dash_config['shapes'])} shapes")
        print(f"DASH form has {len(dash_config['property_groups'])} property groups")
        print(f"Root components: {dash_config['ui_layout']['root_components']}")
        
        # Test HTML form generation
        print("Generating DASH HTML form...")
        html_form = dash_generator.generate_dash_html_form(schema)
        
        print(f"HTML form length: {len(html_form)} characters")
        
        # Save HTML form for inspection
        os.makedirs("test_output", exist_ok=True)
        
        # Skip JSON serialization for now due to UIMetadata objects
        print("Skipping JSON config save (UIMetadata serialization issue)")
        
        with open("test_output/dash_form.html", "w") as f:
            f.write(html_form)
        print("Saved DASH HTML form to test_output/dash_form.html")
        
        return True
        
    except Exception as e:
        print(f"DASH form generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("=== Tree Structure and DASH Integration Test ===")
    
    # Create test schema
    schema = create_test_hierarchical_schema()
    
    # Test tree structure validation
    validation_passed = test_tree_structure_validation(schema)
    
    # Test tree navigation
    test_tree_navigation(schema)
    
    # Initialize brick integration (may fail if brick_app_v2 not available)
    try:
        brick_integration = BrickIntegration()
        print("\nBrick integration initialized successfully")
        
        # Test hierarchical SHACL export
        shacl_passed = test_hierarchical_shacl_export(schema, brick_integration)
        
        # Test DASH form generation
        dash_passed = test_dash_form_generation(schema, brick_integration)
        
    except Exception as e:
        print(f"\nBrick integration failed: {e}")
        print("Some tests will be skipped")
        shacl_passed = False
        dash_passed = False
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Tree Structure Validation: {'PASSED' if validation_passed else 'FAILED'}")
    print(f"Hierarchical SHACL Export: {'PASSED' if shacl_passed else 'FAILED'}")
    print(f"DASH Form Generation: {'PASSED' if dash_passed else 'FAILED'}")
    
    if validation_passed and shacl_passed and dash_passed:
        print("\n🎉 All tests passed! Tree structure and DASH integration working correctly.")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    import json
    success = main()
    sys.exit(0 if success else 1)
