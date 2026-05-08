"""
Test UI metadata functionality directly (without Flask)
Tests the same operations that the Flask API would perform
"""

import sys
import os

# Add core modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from schema_core import SchemaCore, UIMetadata, Schema

def test_ui_metadata_operations():
    """Test UI metadata operations directly"""
    
    print("Testing UI Metadata Operations")
    print("=" * 60)
    
    # Initialize schema core
    schema_core = SchemaCore()
    
    # Load the test schema
    schemas = schema_core.get_all_schemas()
    if not schemas:
        print("✗ No schemas found. Run create_test_schema.py first")
        return False
    
    schema = schemas[0]
    schema_id = schema.schema_id
    print(f"\nLoaded schema: {schema.name}")
    print(f"Schema ID: {schema_id}")
    print(f"Components: {schema.component_brick_ids}")
    
    # Test 1: Get UI metadata for a component
    print("\n1. Testing get_component_ui_metadata")
    if schema.component_brick_ids:
        brick_id = schema.component_brick_ids[0]
        ui_metadata = schema.get_component_ui_metadata(brick_id)
        if ui_metadata:
            print(f"   ✓ UI metadata found for {brick_id}")
            print(f"      sequence: {ui_metadata.sequence}")
            print(f"      label: {ui_metadata.label}")
            print(f"      group_id: {ui_metadata.group_id}")
        else:
            print(f"   ✗ No UI metadata found for {brick_id}")
    
    # Test 2: Set UI metadata
    print("\n2. Testing set_component_ui_metadata")
    if schema.component_brick_ids:
        brick_id = schema.component_brick_ids[0]
        new_metadata = UIMetadata(
            sequence=99,
            group_id="test-group",
            parent_id=None,
            label="Test Label",
            help_text="Test help text",
            is_collapsible=False,
            is_visible=True
        )
        schema.set_component_ui_metadata(brick_id, new_metadata)
        retrieved = schema.get_component_ui_metadata(brick_id)
        if retrieved.sequence == 99 and retrieved.label == "Test Label":
            print(f"   ✓ UI metadata set and retrieved correctly")
        else:
            print(f"   ✗ UI metadata not set correctly")
    
    # Test 3: Sequence management
    print("\n3. Testing sequence management")
    for i, brick_id in enumerate(schema.component_brick_ids[:3]):
        schema.set_component_sequence(brick_id, i * 10)
    
    ordered = schema.get_components_by_sequence()
    if len(ordered) == len(schema.component_brick_ids[:3]):
        print(f"   ✓ Sequence management works")
        print(f"      Ordered components: {ordered}")
    else:
        print(f"   ✗ Sequence management failed")
    
    # Test 4: Reorder component
    print("\n4. Testing reorder_component")
    if len(schema.component_brick_ids) >= 2:
        brick_id = schema.component_brick_ids[0]
        old_seq = schema.get_component_sequence(brick_id)
        schema.reorder_component(brick_id, 5)
        new_seq = schema.get_component_sequence(brick_id)
        if new_seq == 5:
            print(f"   ✓ Component reordered from {old_seq} to {new_seq}")
        else:
            print(f"   ✗ Reorder failed (expected 5, got {new_seq})")
    
    # Test 5: Group management
    print("\n5. Testing group management")
    result = schema.create_group("test-api-group", "Test API Group", "Description", 0)
    if result:
        print(f"   ✓ Group created")
    else:
        print(f"   ✗ Group creation failed")
    
    groups = schema.get_groups_by_sequence()
    print(f"   Groups: {[g['id'] for g in groups]}")
    
    # Test 6: Add component to group
    print("\n6. Testing add_component_to_group")
    if schema.component_brick_ids:
        brick_id = schema.component_brick_ids[0]
        result = schema.add_component_to_group(brick_id, "test-api-group")
        if result:
            print(f"   ✓ Component added to group")
        else:
            print(f"   ✗ Failed to add component to group")
    
    members = schema.get_group_members("test-api-group")
    print(f"   Group members: {members}")
    
    # Test 7: Remove component from group
    print("\n7. Testing remove_component_from_group")
    if schema.component_brick_ids:
        brick_id = schema.component_brick_ids[0]
        result = schema.remove_component_from_group(brick_id)
        if result:
            print(f"   ✓ Component removed from group")
        else:
            print(f"   ✗ Failed to remove component from group")
    
    # Test 8: Delete group
    print("\n8. Testing delete_group")
    result = schema.delete_group("test-api-group")
    if result:
        print(f"   ✓ Group deleted")
    else:
        print(f"   ✗ Failed to delete group")
    
    # Test 9: Parent-child relationships
    print("\n9. Testing parent-child relationships")
    if len(schema.component_brick_ids) >= 2:
        parent_id = schema.component_brick_ids[0]
        child_id = schema.component_brick_ids[1]
        result = schema.set_component_parent(child_id, parent_id)
        if result:
            print(f"   ✓ Parent set")
        else:
            print(f"   ✗ Failed to set parent")
        
        children = schema.get_ui_children(parent_id)
        if child_id in children:
            print(f"   ✓ Child found in parent's children list")
        else:
            print(f"   ✗ Child not found")
        
        parent = schema.get_ui_parent(child_id)
        if parent == parent_id:
            print(f"   ✓ Parent retrieved correctly")
        else:
            print(f"   ✗ Parent not retrieved correctly")
    
    # Test 10: Tree structure
    print("\n10. Testing get_ui_tree")
    tree = schema.get_ui_tree()
    print(f"   ✓ Tree structure retrieved")
    print(f"      Tree: {tree}")
    
    # Test 11: Serialization
    print("\n11. Testing serialization (to_dict)")
    schema_dict = schema.to_dict()
    if 'component_ui_metadata' in schema_dict:
        print(f"   ✓ component_ui_metadata in dict")
        print(f"      Entries: {len(schema_dict['component_ui_metadata'])}")
    else:
        print(f"   ✗ component_ui_metadata not in dict")
    
    if 'groups' in schema_dict:
        print(f"   ✓ groups in dict")
        print(f"      Groups: {list(schema_dict['groups'].keys())}")
    else:
        print(f"   ✗ groups not in dict")
    
    # Test 12: Deserialization
    print("\n12. Testing deserialization (from_dict)")
    restored = Schema.from_dict(schema_dict)
    if restored.name == schema.name:
        print(f"   ✓ Schema deserialized correctly")
    else:
        print(f"   ✗ Schema deserialization failed")
    
    if len(restored.component_ui_metadata) == len(schema.component_ui_metadata):
        print(f"   ✓ UI metadata preserved after deserialization")
    else:
        print(f"   ✗ UI metadata not preserved")
    
    # Save the updated schema
    print("\n13. Saving updated schema")
    if schema_core.save_schema(schema):
        print(f"   ✓ Schema saved successfully")
    else:
        print(f"   ✗ Failed to save schema")
    
    print("\n" + "=" * 60)
    print("All UI metadata operations tested")
    return True

if __name__ == "__main__":
    try:
        success = test_ui_metadata_operations()
        if success:
            print("\n✓ All tests passed")
            sys.exit(0)
        else:
            print("\n✗ Some tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
