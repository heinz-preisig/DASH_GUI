#!/usr/bin/env python3
"""
Simple test for the SHACL brick generator
"""

def test_brick_generator():
    """Test the brick generator functionality"""
    try:
        from brick_backend import BrickBackendAPI, BrickEventProcessor
        
        print("=== SHACL Brick Generator Test ===\n")
        
        # Initialize backend
        backend = BrickBackendAPI("test_repositories")
        processor = BrickEventProcessor(backend)
        
        # Ensure we have an active library
        result = processor.process_event({"event": "get_repository_info"})
        if not result["data"]["active_library"]:
            # Set the default library as active
            processor.process_event({"event": "set_active_library", "library_name": "default"})
        
        # Test 1: Repository info
        print("1. Testing repository info...")
        result = processor.process_event({"event": "get_repository_info"})
        assert result["status"] == "success", "Repository info failed"
        print(f"   Repository has {len(result['data']['libraries'])} libraries")
        
        # Test 2: Get SHACL object types
        print("2. Testing SHACL object types...")
        result = processor.process_event({"event": "get_shacl_object_types"})
        assert result["status"] == "success", "SHACL object types failed"
        print(f"   Found {len(result['data']['object_types'])} object types")
        
        # Test 3: Get constraint templates
        print("3. Testing constraint templates...")
        result = processor.process_event({"event": "get_constraint_templates"})
        assert result["status"] == "success", "Constraint templates failed"
        print(f"   Found {len(result['data'])} constraint templates")
        
        # Test 4: Create NodeShape brick
        print("4. Creating NodeShape brick...")
        result = processor.process_event({
            "event": "create_nodeshape_brick",
            "brick_id": "test_person_nodeshape",
            "name": "Test Person NodeShape",
            "description": "A test person shape for testing",
            "target_class": "foaf:Person",
            "properties": {"nodeKind": "sh:BlankNodeOrIRI"},
            "tags": ["test", "person", "nodeshape"]
        })
        assert result["status"] == "success", "NodeShape creation failed"
        print(f"   Created NodeShape: {result['data']['brick_id']}")
        
        # Test 5: Create PropertyShape brick
        print("5. Creating PropertyShape brick...")
        result = processor.process_event({
            "event": "create_propertyshape_brick",
            "brick_id": "test_email_property",
            "name": "Test Email Property",
            "description": "A test email property",
            "path": "foaf:mbox",
            "properties": {"datatype": "xsd:string"},
            "constraints": [
                {"constraint_type": "MinLengthConstraintComponent", "value": 5},
                {"constraint_type": "PatternConstraintComponent", "value": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"}
            ],
            "tags": ["test", "email", "property"]
        })
        assert result["status"] == "success", "PropertyShape creation failed"
        print(f"   Created PropertyShape: {result['data']['brick_id']}")
        
        # Test 6: List bricks
        print("6. Listing bricks...")
        result = processor.process_event({"event": "get_library_bricks"})
        assert result["status"] == "success", "List bricks failed"
        print(f"   Found {result['data']['count']} bricks in library")
        
        # Test 7: Search bricks
        print("7. Searching bricks...")
        result = processor.process_event({"event": "search_bricks", "query": "test"})
        assert result["status"] == "success", "Search bricks failed"
        print(f"   Found {result['data']['count']} bricks matching 'test'")
        
        # Test 8: Get brick details
        print("8. Getting brick details...")
        result = processor.process_event({
            "event": "get_brick_details",
            "brick_id": "test_person_nodeshape"
        })
        assert result["status"] == "success", "Get brick details failed"
        print(f"   Retrieved details for: {result['data']['name']}")
        
        # Test 9: Export SHACL
        print("9. Exporting SHACL...")
        result = processor.process_event({
            "event": "export_brick_shacl",
            "brick_id": "test_person_nodeshape",
            "format_type": "turtle"
        })
        if result["status"] != "success":
            print(f"   Export failed with error: {result.get('message', 'Unknown error')}")
            assert result["status"] == "success", f"Export SHACL failed: {result.get('message', 'Unknown error')}"
        print(f"   Exported SHACL ({len(result['data']['content'])} characters)")
        
        # Test 10: Library statistics
        print("10. Getting library statistics...")
        result = processor.process_event({"event": "get_library_statistics"})
        assert result["status"] == "success", "Library statistics failed"
        print(f"   Library has {result['data']['total_bricks']} bricks")
        
        print("\n=== All Tests Passed! ===")
        print("The SHACL Brick Generator is working correctly.")
        
        return True
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_brick_generator()
    if success:
        print("\nStep 1 (Brick Generator) is ready for use!")
    else:
        print("\nStep 1 has issues that need to be resolved.")
