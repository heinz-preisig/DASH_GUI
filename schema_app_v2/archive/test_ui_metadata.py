"""
Test script for UI metadata functionality
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from schema_core import Schema, UIMetadata, SchemaCore

def test_ui_metadata():
    """Test UI metadata structure"""
    
    print("Testing UI Metadata Structure")
    print("=" * 50)
    
    # Create a test schema
    schema = Schema(
        schema_id="test-schema-001",
        name="Product Schema",
        description="Test schema for product data entry",
        root_brick_id="product-node",
        component_brick_ids=["company-prop", "name-prop", "address-node", "street-prop"]
    )
    
    print(f"\n1. Created schema: {schema.name}")
    print(f"   Components: {schema.component_brick_ids}")
    
    # Test sequence management
    print("\n2. Testing sequence management:")
    schema.set_component_sequence("company-prop", 0)
    schema.set_component_sequence("name-prop", 1)
    schema.set_component_sequence("address-node", 2)
    schema.set_component_sequence("street-prop", 3)
    
    for brick_id in schema.component_brick_ids:
        seq = schema.get_component_sequence(brick_id)
        print(f"   {brick_id}: sequence = {seq}")
    
    ordered = schema.get_components_by_sequence()
    print(f"   Ordered components: {ordered}")
    
    # Test reordering
    print("\n3. Testing reordering (move street-prop to position 1):")
    schema.reorder_component("street-prop", 1)
    for brick_id in schema.component_brick_ids:
        seq = schema.get_component_sequence(brick_id)
        print(f"   {brick_id}: sequence = {seq}")
    
    # Test grouping
    print("\n4. Testing grouping:")
    schema.create_group("personal-info", "Personal Information", "Personal details", 0)
    schema.create_group("address-info", "Address Information", "Address details", 1)
    
    schema.add_component_to_group("name-prop", "personal-info")
    schema.add_component_to_group("street-prop", "address-info")
    
    groups = schema.get_groups_by_sequence()
    print(f"   Groups: {[g['label'] for g in groups]}")
    
    personal_members = schema.get_group_members("personal-info")
    print(f"   Personal info members: {personal_members}")
    
    ungrouped = schema.get_components_without_group()
    print(f"   Ungrouped components: {ungrouped}")
    
    # Test UI nesting (parent-child)
    print("\n5. Testing UI nesting:")
    schema.set_component_parent("street-prop", "address-node")
    schema.set_component_parent("address-node", "company-prop")
    
    address_children = schema.get_ui_children("address-node")
    print(f"   Children of address-node: {address_children}")
    
    ui_parent = schema.get_ui_parent("street-prop")
    print(f"   Parent of street-prop: {ui_parent}")
    
    ui_tree = schema.get_ui_tree()
    print(f"   UI tree structure: {ui_tree}")
    
    # Test labels and help text
    print("\n6. Testing labels and help text:")
    schema.set_component_label("name-prop", "Full Name")
    schema.set_component_help_text("name-prop", "Enter the person's full name")
    
    name_metadata = schema.get_component_ui_metadata("name-prop")
    print(f"   name-prop label: {name_metadata.label}")
    print(f"   name-prop help: {name_metadata.help_text}")
    
    # Test serialization
    print("\n7. Testing serialization:")
    schema_dict = schema.to_dict()
    print(f"   Serialization successful: {len(schema_dict) > 0}")
    print(f"   UI metadata entries: {len(schema_dict['component_ui_metadata'])}")
    
    # Test deserialization
    print("\n8. Testing deserialization:")
    restored_schema = Schema.from_dict(schema_dict)
    print(f"   Deserialization successful: {restored_schema.name == schema.name}")
    print(f"   UI metadata preserved: {len(restored_schema.component_ui_metadata) == len(schema.component_ui_metadata)}")
    
    print("\n" + "=" * 50)
    print("All tests completed successfully!")

if __name__ == "__main__":
    test_ui_metadata()
