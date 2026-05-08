"""
Create a test schema with UI metadata for testing both Qt GUI and Flask API
"""

import sys
import os

# Add core modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from schema_core import SchemaCore, Schema
from brick_integration import BrickIntegration

def create_test_schema():
    """Create a test schema with components and UI metadata"""
    
    print("Creating test schema...")
    
    # Initialize components
    schema_core = SchemaCore()
    brick_integration = BrickIntegration()
    
    # Get available bricks
    bricks = brick_integration.get_available_bricks()
    print(f"Found {len(bricks)} available bricks")
    
    if len(bricks) < 4:
        print("Not enough bricks available. Creating minimal test schema...")
        # Create a minimal schema with just a root brick
        schema = schema_core.create_schema(
            name="Test Schema",
            description="Test schema for UI metadata",
            root_brick_id="test-root"
        )
        schema.component_brick_ids = ["comp1", "comp2", "comp3"]
    else:
        # Use actual bricks
        node_shapes = brick_integration.get_node_shape_bricks()
        property_shapes = brick_integration.get_property_shape_bricks()
        
        if not node_shapes:
            print("No NodeShape bricks found. Using mock data...")
            schema = schema_core.create_schema(
                name="Test Schema",
                description="Test schema for UI metadata",
                root_brick_id="mock-root"
            )
            schema.component_brick_ids = ["comp1", "comp2", "comp3", "comp4"]
        else:
            root_brick = node_shapes[0]
            schema = schema_core.create_schema(
                name="Test Schema",
                description="Test schema for UI metadata",
                root_brick_id=root_brick.brick_id
            )
            
            # Add some component bricks
            component_ids = []
            for i, brick in enumerate(property_shapes[:4]):
                schema_core.add_component_brick(brick.brick_id)
                component_ids.append(brick.brick_id)
            schema.component_brick_ids = component_ids
    
    # Add UI metadata to components
    print("\nAdding UI metadata to components...")
    for i, brick_id in enumerate(schema.component_brick_ids):
        schema.set_component_sequence(brick_id, i)
        schema.set_component_label(brick_id, f"Component {i+1}")
        schema.set_component_help_text(brick_id, f"This is component {i+1}")
        schema.initialize_component_ui_metadata(brick_id)
    
    # Create some groups
    print("Creating groups...")
    schema.create_group("personal-info", "Personal Information", "Personal details", 0)
    schema.create_group("address-info", "Address Information", "Address details", 1)
    
    # Assign components to groups
    if len(schema.component_brick_ids) >= 2:
        schema.add_component_to_group(schema.component_brick_ids[0], "personal-info")
    if len(schema.component_brick_ids) >= 3:
        schema.add_component_to_group(schema.component_brick_ids[1], "address-info")
    
    # Set up some nesting
    if len(schema.component_brick_ids) >= 3:
        schema.set_component_parent(schema.component_brick_ids[2], schema.component_brick_ids[0])
    
    # Save schema
    print("\nSaving schema...")
    if schema_core.save_schema(schema):
        print(f"✓ Schema saved successfully")
        print(f"  Schema ID: {schema.schema_id}")
        print(f"  Name: {schema.name}")
        print(f"  Components: {schema.component_brick_ids}")
        print(f"  Groups: {list(schema.groups.keys())}")
        print(f"  UI metadata entries: {len(schema.component_ui_metadata)}")
        
        # Print tree structure
        tree = schema.get_ui_tree()
        print(f"  UI tree: {tree}")
        
        return schema
    else:
        print("✗ Failed to save schema")
        return None

if __name__ == "__main__":
    schema = create_test_schema()
    if schema:
        print("\n✓ Test schema created successfully")
    else:
        print("\n✗ Failed to create test schema")
        sys.exit(1)
