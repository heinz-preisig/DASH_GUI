#!/usr/bin/env python3
"""
Create Sample Address Library with sh:node Composition
======================================================

This script creates a new brick library with:
- US Address brick
- EU Address brick  
- Freeform Address brick
- Person brick that references all three via sh:node

The bricks are saved to: ShaclForm-library/bricks/address_samples/
"""

import uuid
import json
from datetime import datetime
from pathlib import Path
from common import shared_library_manager


def create_us_address_brick():
    """US Address format with state code and ZIP"""
    return {
        "brick_id": str(uuid.uuid4()),
        "name": "US Address",
        "description": "United States address format with state code and ZIP",
        "namespace": "ex",
        "target_class": "ex:USAddress",
        "object_type": "NodeShape",
        "template_type": "custom",
        "leaf_properties": [
            {
                "path": "schema:streetAddress",
                "label": "Street Address",
                "datatype": "xsd:string",
                "min_count": 1,
                "description": "Street name and number"
            },
            {
                "path": "schema:addressLocality",
                "label": "City",
                "datatype": "xsd:string",
                "min_count": 1
            },
            {
                "path": "ex:stateCode",
                "label": "State",
                "datatype": "xsd:string",
                "description": "2-letter state code",
                "min_count": 1,
                "max_count": 1
            },
            {
                "path": "schema:postalCode",
                "label": "ZIP Code",
                "datatype": "xsd:string",
                "pattern": "^[0-9]{5}(-[0-9]{4})?$",
                "description": "5-digit ZIP or ZIP+4",
                "min_count": 1,
                "max_count": 1
            },
            {
                "path": "schema:addressCountry",
                "label": "Country",
                "has_value": "US",
                "min_count": 1,
                "max_count": 1
            }
        ],
        "xone_alternatives": [],
        "tags": ["address", "us", "location"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "metadata": {"sample": True, "region": "us"}
    }


def create_eu_address_brick():
    """EU Address format with country selection"""
    return {
        "brick_id": str(uuid.uuid4()),
        "name": "EU Address",
        "description": "European address format with country selection",
        "namespace": "ex",
        "target_class": "ex:EUAddress",
        "object_type": "NodeShape",
        "template_type": "custom",
        "leaf_properties": [
            {
                "path": "schema:streetAddress",
                "label": "Street",
                "datatype": "xsd:string",
                "min_count": 1
            },
            {
                "path": "schema:addressLocality",
                "label": "City/Town",
                "datatype": "xsd:string",
                "min_count": 1
            },
            {
                "path": "ex:postalCode",
                "label": "Postal Code",
                "datatype": "xsd:string",
                "description": "Format varies by country"
            },
            {
                "path": "schema:addressCountry",
                "label": "Country",
                "datatype": "xsd:string",
                "node_kind": "sh:IRI",
                "in_values": [
                    "ex:DE", "ex:FR", "ex:IT", "ex:ES",
                    "ex:NL", "ex:BE", "ex:AT", "ex:PL"
                ],
                "min_count": 1,
                "max_count": 1
            }
        ],
        "xone_alternatives": [],
        "tags": ["address", "eu", "location"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "metadata": {"sample": True, "region": "eu"}
    }


def create_freeform_address_brick():
    """Simple free-form address"""
    return {
        "brick_id": str(uuid.uuid4()),
        "name": "Freeform Address",
        "description": "Simple text-based address entry",
        "namespace": "ex",
        "target_class": "ex:FreeformAddress",
        "object_type": "NodeShape",
        "template_type": "free_text",
        "leaf_properties": [
            {
                "path": "schema:text",
                "label": "Full Address",
                "datatype": "xsd:string",
                "description": "Enter complete address as free text",
                "single_line": False,
                "min_count": 1,
                "max_count": 1
            }
        ],
        "xone_alternatives": [],
        "tags": ["address", "simple", "freeform"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "metadata": {"sample": True, "region": "any"}
    }


def create_person_brick(us_id, eu_id, freeform_id):
    """Person brick that references address types via node_shape_refs"""
    return {
        "brick_id": str(uuid.uuid4()),
        "name": "Person with Address",
        "description": "Person that can have US, EU, or freeform address",
        "namespace": "ex",
        "target_class": "schema:Person",
        "object_type": "NodeShape",
        "template_type": "custom",
        "leaf_properties": [
            {
                "path": "schema:givenName",
                "label": "First Name",
                "datatype": "xsd:string",
                "min_count": 1
            },
            {
                "path": "schema:familyName",
                "label": "Last Name",
                "datatype": "xsd:string",
                "min_count": 1
            },
            {
                "path": "schema:email",
                "label": "Email",
                "datatype": "xsd:string",
                "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
            },
            {
                "path": "schema:address",
                "label": "Address",
                "description": "Choose address format",
                "node_kind": "sh:BlankNode",
                "min_count": 0,
                "max_count": 1,
                # KEY: This property can reference any of these shapes via sh:node
                "node_shape_refs": [us_id, eu_id, freeform_id],
                "template_type": "composed_node"
            }
        ],
        "xone_alternatives": [],
        "tags": ["person", "contact", "address", "sample"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "metadata": {"sample": True, "composed": True}
    }


def generate_shacl_turtle(bricks):
    """Generate SHACL Turtle for the bricks showing sh:node composition"""
    lines = [
        "@prefix ex: <http://example.org/> .",
        "@prefix schema: <http://schema.org/> .",
        "@prefix sh: <http://www.w3.org/ns/shacl#> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        ""
    ]
    
    for brick in bricks:
        shape_name = brick["target_class"].split(":")[-1]
        lines.append(f"ex:{shape_name} a sh:NodeShape ;")
        lines.append(f'    rdfs:label "{brick["name"]}" ;')
        if brick.get("description"):
            lines.append(f'    rdfs:comment "{brick["description"]}" ;')
        
        # targetClass if specified
        target = brick.get("target_class", "")
        if target and target != f"ex:{shape_name}":
            lines.append(f"    sh:targetClass {target} ;")
        
        # Properties
        for i, prop in enumerate(brick.get("leaf_properties", [])):
            lines.append("    sh:property [")
            lines.append(f'        sh:path {prop["path"]} ;')
            if prop.get("label"):
                lines.append(f'        rdfs:label "{prop["label"]}" ;')
            if prop.get("datatype"):
                lines.append(f'        sh:datatype {prop["datatype"]} ;')
            if prop.get("min_count") is not None:
                lines.append(f'        sh:minCount {prop["min_count"]} ;')
            if prop.get("max_count") is not None:
                lines.append(f'        sh:maxCount {prop["max_count"]} ;')
            if prop.get("has_value"):
                lines.append(f'        sh:hasValue "{prop["has_value"]}" ;')
            
            # KEY: node shape reference via sh:node
            refs = prop.get("node_shape_refs", [])
            if refs:
                # Find the referenced brick names
                for ref_id in refs:
                    ref = next((b for b in bricks if b["brick_id"] == ref_id), None)
                    if ref:
                        ref_name = ref["target_class"].split(":")[-1]
                        lines.append(f"        sh:node ex:{ref_name} ;")
                        lines.append(f'        ## Can also be: ex:{ref_name} ##')
            
            lines.append("    ] ;")
        
        lines.append(".")
        lines.append("")
    
    return "\n".join(lines)


def main():
    print("="*60)
    print("Creating Address Sample Library")
    print("="*60)
    
    # Create the library
    lib_name = "address_samples"
    try:
        shared_library_manager.create_library(
            lib_type="bricks",
            name=lib_name,
            description="Sample library demonstrating sh:node composition for alternative addresses"
        )
        print(f"\nCreated library: {lib_name}")
    except ValueError as e:
        if "already exists" in str(e):
            print(f"\nLibrary '{lib_name}' already exists - will overwrite bricks")
        else:
            raise
    
    # Get library path
    lib_path = shared_library_manager.lib_path("bricks", lib_name)
    print(f"Library path: {lib_path}")
    
    # Create the bricks
    print("\n1. Creating address bricks...")
    us_brick = create_us_address_brick()
    eu_brick = create_eu_address_brick()
    freeform_brick = create_freeform_address_brick()
    
    print(f"   US Address: {us_brick['name']} ({us_brick['brick_id'][:8]}...)")
    print(f"   EU Address: {eu_brick['name']} ({eu_brick['brick_id'][:8]}...)")
    print(f"   Freeform:   {freeform_brick['name']} ({freeform_brick['brick_id'][:8]}...)")
    
    # Create person brick with references
    print("\n2. Creating Person brick with address references...")
    person_brick = create_person_brick(
        us_brick["brick_id"],
        eu_brick["brick_id"],
        freeform_brick["brick_id"]
    )
    print(f"   Person: {person_brick['name']} ({person_brick['brick_id'][:8]}...)")
    
    # Save all bricks
    print("\n3. Saving bricks to library...")
    bricks = [us_brick, eu_brick, freeform_brick, person_brick]
    
    for brick in bricks:
        # Save JSON
        safe_name = brick["name"].lower().replace(" ", "_")
        json_file = lib_path / f"{safe_name}_{brick['brick_id'][:8]}.json"
        with open(json_file, 'w') as f:
            json.dump(brick, f, indent=2)
        print(f"   {json_file.name}")
    
    # Generate and save TTL
    print("\n4. Generating SHACL TTL...")
    ttl_content = generate_shacl_turtle(bricks)
    ttl_file = lib_path / "address_samples.ttl"
    with open(ttl_file, 'w') as f:
        f.write(ttl_content)
    print(f"   {ttl_file.name}")
    
    # Show summary
    print("\n" + "="*60)
    print("Library created successfully!")
    print("="*60)
    print(f"\nLocation: {lib_path}")
    print(f"Bricks: {len(bricks)}")
    print("\nSHACL Composition Pattern:")
    print("-" * 40)
    print("""
Person with Address
├── hasAddress property
│   └── sh:node → US Address  (ex:USAddress)
│   └── sh:node → EU Address  (ex:EUAddress)  
│   └── sh:node → Freeform Address (ex:FreeformAddress)
│
US Address           EU Address          Freeform Address
├── street           ├── street          └── full text
├── city             ├── city
├── state            ├── postal code
├── ZIP              └── country (dropdown)
└── country=US
    """)
    print("\nTo use:")
    print("  1. Launch brick app: ./run_brick_app_qt.sh")
    print("  2. Switch to 'address_samples' library")
    print("  3. Open 'Person with Address' brick")
    print("  4. See the composed address property")


if __name__ == "__main__":
    main()
