#!/usr/bin/env python3
"""
Quick test to verify the SHACL export fix
"""

def test_export_fix():
    """Test the export fix"""
    try:
        from brick_backend import BrickBackendAPI, BrickEventProcessor
        
        print("Testing SHACL export fix...")
        
        # Initialize backend
        backend = BrickBackendAPI("test_repositories")
        processor = BrickEventProcessor(backend)
        
        # Ensure we have an active library
        result = processor.process_event({"event": "get_repository_info"})
        if not result["data"]["active_library"]:
            # Set the default library as active
            processor.process_event({"event": "set_active_library", "library_name": "default"})
        
        # Create a simple test brick
        result = processor.process_event({
            "event": "create_nodeshape_brick",
            "brick_id": "export_test_person",
            "name": "Export Test Person",
            "description": "A test person for export",
            "target_class": "foaf:Person",
            "properties": {"nodeKind": "sh:BlankNodeOrIRI"},
            "tags": ["test", "export"]
        })
        
        if result["status"] != "success":
            print(f"Failed to create test brick: {result}")
            return False
        
        print(f"Created test brick: {result['data']['brick_id']}")
        
        # Test export
        result = processor.process_event({
            "event": "export_brick_shacl",
            "brick_id": "export_test_person",
            "format_type": "turtle"
        })
        
        if result["status"] != "success":
            print(f"Export failed: {result}")
            return False
        
        print(f"Export successful! SHACL content length: {len(result['data']['content'])}")
        print("SHACL content preview:")
        print(result['data']['content'][:200] + "...")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_export_fix()
    if success:
        print("\nExport fix verified!")
    else:
        print("\nExport fix needs more work.")
