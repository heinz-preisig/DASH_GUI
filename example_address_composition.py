#!/usr/bin/env python3
"""
Example: Using sh:node Composition for Alternative Addresses
============================================================

This demonstrates the clean SHACL pattern for handling alternative structures:
- Create separate, focused bricks for each address type
- Reference them via sh:node from a parent brick
- DASH can then render the appropriate form dynamically

Generated SHACL:
    ex:PersonShape sh:property [
        sh:path ex:hasAddress ;
        sh:node ex:USAddressShape  # or EUAddressShape, etc.
    ] .
"""

import uuid
import json
from pathlib import Path
from brick_app.core.brick_core_simple import BrickCore, SHACLBrick, LeafProperty

def create_us_address_brick(core: BrickCore) -> SHACLBrick:
    """Create a US Address brick with US-specific fields"""
    brick = SHACLBrick(
        brick_id=str(uuid.uuid4()),
        name="US Address",
        description="United States address format with state and ZIP code",
        namespace="ex",
        target_class="ex:USAddress",  # This is the class this shape validates
        leaf_properties=[
            LeafProperty(
                path="schema:streetAddress",
                label="Street Address",
                datatype="xsd:string",
                min_count=1,
                description="Street name and number"
            ).to_dict(),
            LeafProperty(
                path="schema:addressLocality",
                label="City",
                datatype="xsd:string",
                min_count=1
            ).to_dict(),
            LeafProperty(
                path="ex:stateCode",
                label="State",
                datatype="xsd:string",
                description="2-letter state code (CA, NY, TX, etc.)",
                min_count=1,
                max_count=1
            ).to_dict(),
            LeafProperty(
                path="schema:postalCode",
                label="ZIP Code",
                datatype="xsd:string",
                description="5-digit ZIP code",
                min_count=1,
                max_count=1
            ).to_dict(),
            LeafProperty(
                path="schema:addressCountry",
                label="Country",
                has_value="US",  # Static value - always US
                min_count=1,
                max_count=1
            ).to_dict(),
        ],
        tags=["address", "us", "location"]
    )
    core.save_brick(brick)
    return brick

def create_eu_address_brick(core: BrickCore) -> SHACLBrick:
    """Create an EU Address brick with European format"""
    brick = SHACLBrick(
        brick_id=str(uuid.uuid4()),
        name="EU Address",
        description="European address format with country selection",
        namespace="ex",
        target_class="ex:EUAddress",
        leaf_properties=[
            LeafProperty(
                path="schema:streetAddress",
                label="Street",
                datatype="xsd:string",
                min_count=1
            ).to_dict(),
            LeafProperty(
                path="schema:addressLocality",
                label="City/Town",
                datatype="xsd:string",
                min_count=1
            ).to_dict(),
            LeafProperty(
                path="ex:postalCode",
                label="Postal Code",
                datatype="xsd:string",
                description="Format varies by country"
            ).to_dict(),
            LeafProperty(
                path="schema:addressCountry",
                label="Country",
                datatype="xsd:string",
                node_kind="sh:IRI",  # Will be a dropdown
                in_values=[
                    "http://example.org/countries/DE",
                    "http://example.org/countries/FR",
                    "http://example.org/countries/IT",
                    "http://example.org/countries/ES",
                    "http://example.org/countries/NL",
                    "http://example.org/countries/BE",
                    "http://example.org/countries/AT",
                ],
                min_count=1,
                max_count=1
            ).to_dict(),
        ],
        tags=["address", "eu", "location"]
    )
    core.save_brick(brick)
    return brick

def create_freeform_address_brick(core: BrickCore) -> SHACLBrick:
    """Create a simple free-form address brick"""
    brick = SHACLBrick(
        brick_id=str(uuid.uuid4()),
        name="Freeform Address",
        description="Simple text-based address entry",
        namespace="ex",
        target_class="ex:FreeformAddress",
        leaf_properties=[
            LeafProperty(
                path="schema:text",
                label="Full Address",
                datatype="xsd:string",
                description="Enter complete address as free text",
                single_line=False,  # Multi-line textarea
                min_count=1,
                max_count=1
            ).to_dict(),
        ],
        tags=["address", "simple", "freeform"]
    )
    core.save_brick(brick)
    return brick

def create_person_brick_with_address_choices(
    core: BrickCore,
    us_address: SHACLBrick,
    eu_address: SHACLBrick,
    freeform_address: SHACLBrick
) -> SHACLBrick:
    """
    Create a Person brick that can reference any of the address types.
    
    The key is in the leaf_property: we use 'node_shape_ref' to reference
    another brick via sh:node. This tells SHACL/DASH: "the value of this 
    property must conform to the referenced shape."
    """
    brick = SHACLBrick(
        brick_id=str(uuid.uuid4()),
        name="Person",
        description="Person with address - can use US, EU, or freeform format",
        namespace="ex",
        target_class="schema:Person",
        leaf_properties=[
            # Basic person properties
            LeafProperty(
                path="schema:givenName",
                label="First Name",
                datatype="xsd:string",
                min_count=1
            ).to_dict(),
            LeafProperty(
                path="schema:familyName",
                label="Last Name",
                datatype="xsd:string",
                min_count=1
            ).to_dict(),
            LeafProperty(
                path="schema:email",
                label="Email",
                datatype="xsd:string",
                description="Valid email address"
            ).to_dict(),
            
            # Address property with node reference
            # This is the KEY: sh:node referencing another shape
            {
                "path": "schema:address",
                "label": "Address",
                "description": "Choose address format: US, EU, or freeform",
                "min_count": 0,
                "max_count": 1,
                "node_kind": "sh:BlankNode",  # Address is a nested structure
                # The node_shape_ref tells DASH/SHACL which shapes are valid
                "node_shape_refs": [
                    us_address.brick_id,      # Reference to US Address brick
                    eu_address.brick_id,      # Reference to EU Address brick
                    freeform_address.brick_id # Reference to Freeform Address brick
                ],
                "template_type": "composed_node"  # Custom template for composed nodes
            }
        ],
        tags=["person", "contact", "with-address"]
    )
    core.save_brick(brick)
    return brick

def show_generated_shacl_turtle(core: BrickCore, brick: SHACLBrick):
    """Generate and display SHACL Turtle for the brick"""
    from brick_app.core.brick_generator import SHACLBrickGenerator, BrickLibrary
    
    # Create a temporary library with all bricks for export
    temp_lib = BrickLibrary("temp", "Temporary", "System")
    
    # Add this brick and all referenced bricks
    temp_lib.add_brick(brick)
    
    # Find and add referenced bricks
    for prop in brick.leaf_properties:
        refs = prop.get("node_shape_refs", [])
        for ref_id in refs:
            ref_brick = core.load_brick(ref_id)
            if ref_brick:
                temp_lib.add_brick(ref_brick)
    
    generator = SHACLBrickGenerator(temp_lib)
    graph = generator.brick_to_shacl(brick)
    
    print("\n" + "="*60)
    print(f"Generated SHACL for: {brick.name}")
    print("="*60)
    print(graph.serialize(format='turtle'))

def main():
    print("="*60)
    print("Address Composition Example: sh:node Pattern")
    print("="*60)
    
    # Initialize the brick core (uses default library path)
    core = BrickCore(use_shared_libraries=True)
    
    print("\n1. Creating address type bricks...")
    print("-" * 40)
    
    # Step 1: Create the address type bricks
    us_address = create_us_address_brick(core)
    print(f"   Created: {us_address.name} (ID: {us_address.brick_id[:8]}...)")
    
    eu_address = create_eu_address_brick(core)
    print(f"   Created: {eu_address.name} (ID: {eu_address.brick_id[:8]}...)")
    
    freeform_address = create_freeform_address_brick(core)
    print(f"   Created: {freeform_address.name} (ID: {freeform_address.brick_id[:8]}...)")
    
    print("\n2. Creating Person brick with address choices...")
    print("-" * 40)
    
    # Step 2: Create Person brick that references the addresses
    person = create_person_brick_with_address_choices(
        core, us_address, eu_address, freeform_address
    )
    print(f"   Created: {person.name} (ID: {person.brick_id[:8]}...)")
    print(f"   References {len(person.leaf_properties[-1].get('node_shape_refs', []))} address types")
    
    # Show the person brick structure
    print("\n3. Person brick structure:")
    print("-" * 40)
    for prop in person.leaf_properties:
        refs = prop.get("node_shape_refs", [])
        if refs:
            print(f"   Property: {prop['label']} (path: {prop['path']})")
            print(f"   └── Can reference {len(refs)} shapes:")
            for ref in refs:
                ref_brick = core.load_brick(ref)
                if ref_brick:
                    print(f"       └── {ref_brick.name} → sh:node ex:{ref_brick.target_class.split(':')[-1]}")
        else:
            print(f"   Property: {prop['label']} (path: {prop['path']})")
    
    # Show generated SHACL
    show_generated_shacl_turtle(core, person)
    
    print("\n4. How DASH would render this:")
    print("-" * 40)
    print("""
   User sees a Person form with:
   ├── First Name [text input]
   ├── Last Name [text input]
   ├── Email [email input]
   └── Address [selector/dropdown]
       ├── Choose format: [US Address | EU Address | Freeform]
       └── Based on choice, shows:
           • US: Street, City, State (dropdown), ZIP, Country=US (hidden)
           • EU: Street, City, Postal Code, Country (dropdown)
           • Freeform: Single multi-line text area
   
   SHACL validation ensures the nested address conforms to the 
   chosen shape via sh:node reference.
    """)
    
    print("\n5. Files saved to:")
    print("-" * 40)
    print(f"   {core.repository_path}/default/")
    print("   (Bricks saved as JSON, with .ttl generated alongside)")
    
    print("\n" + "="*60)
    print("Example complete!")
    print("="*60)

if __name__ == "__main__":
    main()
