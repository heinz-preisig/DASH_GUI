"""
Test SHACL export with sh:order from UI metadata
"""

import sys
import os

# Add core modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from schema_core import SchemaCore, Schema
from shacl_export import SHACLExporter
from brick_integration import BrickIntegration

def test_shacl_export_with_order():
    """Test SHACL export includes sh:order from UI metadata"""
    
    print("Testing SHACL Export with sh:order")
    print("=" * 60)
    
    # Initialize components
    schema_core = SchemaCore()
    brick_integration = BrickIntegration()
    shacl_exporter = SHACLExporter(brick_integration)
    
    # Load a schema
    schemas = schema_core.get_all_schemas()
    if not schemas:
        print("✗ No schemas found. Run create_test_schema.py first")
        return False
    
    # Find a schema with real brick IDs (not mock IDs)
    schema = None
    for s in schemas:
        # Check if any component IDs look like real UUIDs or known brick names
        if any(len(cid) > 10 or '_' in cid for cid in s.component_brick_ids):
            schema = s
            break
    
    if not schema:
        schema = schemas[0]  # Fallback to first schema
    
    print(f"\nLoaded schema: {schema.name}")
    print(f"Components: {schema.component_brick_ids}")
    
    # Ensure UI metadata has sequences set
    for i, brick_id in enumerate(schema.component_brick_ids):
        schema.set_component_sequence(brick_id, i)
        schema.initialize_component_ui_metadata(brick_id)
    
    # Save updated schema
    schema_core.save_schema(schema)
    
    # Export to SHACL
    print("\nExporting to SHACL...")
    shacl_content = shacl_exporter.export_schema(schema)
    
    if shacl_content:
        print("✓ SHACL export successful")
        print("\n" + "-" * 60)
        print(shacl_content)
        print("-" * 60)
        
        # Check if sh:order is present
        if 'sh:order' in shacl_content:
            print("\n✓ sh:order found in SHACL export")
            
            # Count occurrences
            order_count = shacl_content.count('sh:order')
            print(f"  Found {order_count} sh:order statements")
            
            # Extract and display sh:order values
            for line in shacl_content.split('\n'):
                if 'sh:order' in line:
                    print(f"  {line.strip()}")
        else:
            print("\n✗ sh:order NOT found in SHACL export")
            return False
        
        return True
    else:
        print("✗ SHACL export failed")
        return False

if __name__ == "__main__":
    try:
        success = test_shacl_export_with_order()
        if success:
            print("\n✓ SHACL export test passed")
            sys.exit(0)
        else:
            print("\n✗ SHACL export test failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
