#!/usr/bin/env python3
"""
Basic usage example for SHACL Brick Generator
"""

from brick_app_v2 import create_brick_system

def main():
    """Demonstrate basic brick generator usage"""
    print("=== SHACL Brick Generator - Basic Usage ===\n")
    
    # Create brick system
    backend, processor = create_brick_system("example_repositories")
    
    # Create a Person NodeShape brick
    print("Creating Person NodeShape brick...")
    result = processor.process_event({
        "event": "create_nodeshape_brick",
        "brick_id": "example_person",
        "name": "Example Person",
        "description": "A basic person shape for demonstration",
        "target_class": "foaf:Person",
        "properties": {"nodeKind": "sh:BlankNodeOrIRI"},
        "tags": ["example", "person", "demo"]
    })
    
    if result["status"] == "success":
        print(f"  Created: {result['data']['name']}")
    else:
        print(f"  Error: {result['message']}")
        return
    
    # Create an Email PropertyShape brick
    print("\nCreating Email PropertyShape brick...")
    result = processor.process_event({
        "event": "create_propertyshape_brick",
        "brick_id": "example_email",
        "name": "Example Email",
        "description": "Email property with validation",
        "path": "foaf:mbox",
        "properties": {"datatype": "xsd:string"},
        "constraints": [
            {"constraint_type": "MinLengthConstraintComponent", "value": 5},
            {"constraint_type": "PatternConstraintComponent", "value": "^[^@]+@[^@]+\\.[^@]+$"}
        ],
        "tags": ["example", "email", "validated"]
    })
    
    if result["status"] == "success":
        print(f"  Created: {result['data']['name']}")
    else:
        print(f"  Error: {result['message']}")
        return
    
    # List all bricks
    print("\nListing all bricks...")
    result = processor.process_event({"event": "get_library_bricks"})
    if result["status"] == "success":
        for brick in result["data"]["bricks"]:
            print(f"  - {brick['name']} ({brick['object_type']})")
    
    # Export SHACL for Person brick
    print("\nExporting Person brick to SHACL...")
    result = processor.process_event({
        "event": "export_brick_shacl",
        "brick_id": "example_person",
        "format_type": "turtle"
    })
    
    if result["status"] == "success":
        print("SHACL Turtle output:")
        print(result["data"]["content"])
    else:
        print(f"  Error: {result['message']}")
    
    # Get library statistics
    print("\nLibrary statistics:")
    result = processor.process_event({"event": "get_library_statistics"})
    if result["status"] == "success":
        stats = result["data"]
        print(f"  Total bricks: {stats['total_bricks']}")
        print(f"  Object types: {list(stats['object_types'].keys())}")
        print(f"  Common tags: {list(stats['tags'].keys())[:5]}")
    
    print("\n=== Example completed successfully! ===")

if __name__ == "__main__":
    main()
