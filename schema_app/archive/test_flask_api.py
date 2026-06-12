"""
Test Flask API endpoints for UI metadata functionality
"""

import requests
import json
import time
import sys
import os

# Add web module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'interfaces', 'web'))

from flask_app import create_app

def test_flask_api():
    """Test Flask API endpoints"""
    
    print("Starting Flask API tests...")
    print("=" * 60)
    
    # Start Flask app in test mode
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        print("\n1. Testing GET /api/schemas")
        response = client.get('/api/schemas')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            schemas = response.get_json()
            print(f"   ✓ Found {len(schemas)} schemas")
            if schemas:
                schema = schemas[0]
                schema_id = schema['schema_id']
                print(f"   First schema ID: {schema_id}")
                print(f"   Name: {schema['name']}")
                
                # Check if UI metadata is included
                if 'component_ui_metadata' in schema:
                    print(f"   ✓ UI metadata included: {len(schema['component_ui_metadata'])} entries")
                else:
                    print(f"   ✗ UI metadata NOT included in response")
            else:
                print("   ✗ No schemas found")
                return False
        else:
            print(f"   ✗ Failed: {response.get_json()}")
            return False
        
        print("\n2. Testing GET /api/schemas/<id>")
        response = client.get(f'/api/schemas/{schema_id}')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            schema = response.get_json()
            print(f"   ✓ Schema retrieved: {schema['name']}")
            if 'component_ui_metadata' in schema:
                print(f"   ✓ UI metadata included: {len(schema['component_ui_metadata'])} entries")
                for brick_id, meta in schema['component_ui_metadata'].items():
                    print(f"      - {brick_id}: sequence={meta.get('sequence')}, label={meta.get('label')}")
            else:
                print(f"   ✗ UI metadata NOT included")
        else:
            print(f"   ✗ Failed: {response.get_json()}")
            return False
        
        # Get a component brick ID
        component_ids = schema['component_brick_ids']
        if component_ids:
            brick_id = component_ids[0]
            
            print(f"\n3. Testing GET /api/schemas/<id>/components/<id>/ui-metadata")
            response = client.get(f'/api/schemas/{schema_id}/components/{brick_id}/ui-metadata')
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                ui_metadata = response.get_json()
                print(f"   ✓ UI metadata retrieved")
                print(f"      sequence: {ui_metadata.get('sequence')}")
                print(f"      label: {ui_metadata.get('label')}")
                print(f"      group_id: {ui_metadata.get('group_id')}")
            else:
                print(f"   ✗ Failed: {response.get_json()}")
            
            print(f"\n4. Testing PUT /api/schemas/<id>/components/<id>/ui-metadata")
            new_metadata = {
                'sequence': 99,
                'label': 'Updated Label',
                'help_text': 'Updated help text',
                'group_id': 'personal-info',
                'is_collapsible': False,
                'is_visible': True
            }
            response = client.put(
                f'/api/schemas/{schema_id}/components/{brick_id}/ui-metadata',
                json=new_metadata,
                content_type='application/json'
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                updated = response.get_json()
                print(f"   ✓ UI metadata updated")
                print(f"      sequence: {updated.get('sequence')} (expected: 99)")
                print(f"      label: {updated.get('label')} (expected: Updated Label)")
            else:
                print(f"   ✗ Failed: {response.get_json()}")
        
        print(f"\n5. Testing GET /api/schemas/<id>/groups")
        response = client.get(f'/api/schemas/{schema_id}/groups')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            groups = response.get_json()
            print(f"   ✓ Groups retrieved: {len(groups)} groups")
            for group in groups:
                print(f"      - {group['id']}: {group['label']}")
        else:
            print(f"   ✗ Failed: {response.get_json()}")
        
        print(f"\n6. Testing POST /api/schemas/<id>/groups (create new group)")
        new_group = {
            'group_id': 'test-group',
            'label': 'Test Group',
            'description': 'Test group description',
            'sequence': 99
        }
        response = client.post(
            f'/api/schemas/{schema_id}/groups',
            json=new_group,
            content_type='application/json'
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            group = response.get_json()
            print(f"   ✓ Group created: {group['label']}")
        else:
            print(f"   ✗ Failed: {response.get_json()}")
        
        print(f"\n7. Testing GET /api/schemas/<id>/tree")
        response = client.get(f'/api/schemas/{schema_id}/tree')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            tree = response.get_json()
            print(f"   ✓ Tree structure retrieved")
            print(f"      Tree: {tree}")
        else:
            print(f"   ✗ Failed: {response.get_json()}")
        
        print(f"\n8. Testing DELETE /api/schemas/<id>/groups/<group_id>")
        response = client.delete(f'/api/schemas/{schema_id}/groups/test-group')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ Group deleted")
        else:
            print(f"   ✗ Failed: {response.get_json()}")
    
    print("\n" + "=" * 60)
    print("Flask API tests completed")
    return True

if __name__ == "__main__":
    try:
        success = test_flask_api()
        if success:
            print("\n✓ All Flask API tests passed")
            sys.exit(0)
        else:
            print("\n✗ Some Flask API tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
