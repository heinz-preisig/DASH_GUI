#!/usr/bin/env python3
"""
SHACL Backend - Brick generation and SHACL graph management
Separated from frontend for clean architecture
"""

import json
from rdflib import Graph, Namespace, Literal, URIRef
from typing import Dict, List, Any

# SHACL Namespaces
SH = Namespace("http://www.w3.org/ns/shacl#")
DASH = Namespace("http://datashapes.org/dash#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
EX = Namespace("http://example.org/")

class SHACLBrick:
    """Represents a SHACL brick component"""
    
    def __init__(self, brick_type: str, name: str, properties: Dict[str, Any]):
        self.brick_type = brick_type
        self.name = name
        self.properties = properties
        self.uri = f"http://example.org/{name}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert brick to dictionary for serialization"""
        return {
            "type": self.brick_type,
            "name": self.name,
            "uri": self.uri,
            "properties": self.properties
        }

class SHACLBackend:
    """Backend logic for SHACL brick generation and management"""
    
    def __init__(self):
        self.bricks = []
        self.ontologies = {}
        self.current_ontology = None
        self.load_sample_ontologies()
    
    def load_sample_ontologies(self):
        """Load sample public ontologies"""
        self.ontologies = {
            "FOAF": {
                "uri": "http://xmlns.com/foaf/0.1/",
                "terms": {
                    "Person": {"description": "A person"},
                    "Organization": {"description": "An organization"},
                    "name": {"description": "A name"},
                    "mbox": {"description": "Email address"},
                    "knows": {"description": "Knows relationship"}
                }
            },
            "Schema.org": {
                "uri": "http://schema.org/",
                "terms": {
                    "Person": {"description": "A person"},
                    "Organization": {"description": "An organization"},
                    "name": {"description": "The name of the item"},
                    "email": {"description": "Email address"},
                    "birthDate": {"description": "Date of birth"},
                    "address": {"description": "Postal address"},
                    "url": {"description": "URL of the item"}
                }
            },
            "DCTERMS": {
                "uri": "http://purl.org/dc/terms/",
                "terms": {
                    "Agent": {"description": "A person, organization, or service"},
                    "title": {"description": "A name for the resource"},
                    "description": {"description": "An account of the resource"},
                    "date": {"description": "Date of creation or modification"},
                    "creator": {"description": "An entity primarily responsible for making the resource"}
                }
            }
        }
    
    def get_ontology_list(self) -> List[Dict[str, Any]]:
        """Get available ontologies"""
        return [{"name": name, "uri": data["uri"]} for name, data in self.ontologies.items()]
    
    def get_ontology_terms(self, ontology_name: str) -> List[Dict[str, Any]]:
        """Get terms from selected ontology"""
        if ontology_name not in self.ontologies:
            return []
        
        ontology = self.ontologies[ontology_name]
        return [{"name": term, **term_data} for term, term_data in ontology["terms"].items()]
    
    def create_brick_from_term(self, ontology_name: str, term_name: str) -> SHACLBrick:
        """Create a NodeShape brick from ontology term"""
        if ontology_name not in self.ontologies:
            raise ValueError(f"Ontology {ontology_name} not found")
        
        ontology = self.ontologies[ontology_name]
        if term_name not in ontology["terms"]:
            raise ValueError(f"Term {term_name} not found in {ontology_name}")
        
        term_data = ontology["terms"][term_name]
        
        properties = {
            "targetClass": f"{ontology['uri']}{term_name}"
        }
        
        if "description" in term_data:
            properties["description"] = term_data["description"]
        
        return SHACLBrick("NodeShape", f"{term_name}Shape", properties)
    
    def create_property_brick(self, name: str, path: str, datatype: str = None, 
                        min_count: int = None, max_count: int = None,
                        description: str = None, node_kind: str = None,
                        class_constraint: str = None) -> SHACLBrick:
        """Create a PropertyShape brick"""
        properties = {"path": path, "name": name}
        
        if datatype:
            properties["datatype"] = datatype
        if min_count is not None:
            properties["minCount"] = min_count
        if max_count is not None:
            properties["maxCount"] = max_count
        if description:
            properties["description"] = description
        if node_kind:
            properties["nodeKind"] = node_kind
        if class_constraint:
            properties["class"] = class_constraint
        
        return SHACLBrick("PropertyShape", name, properties)
    
    def create_primitive_brick(self, name: str, primitive_type: str, 
                           description: str = None) -> SHACLBrick:
        """Create a primitive brick for reusable types"""
        primitive_types = {
            "string": XSD.string,
            "integer": XSD.integer,
            "decimal": XSD.decimal,
            "date": XSD.date,
            "boolean": XSD.boolean,
            "uri": XSD.anyURI
        }
        
        properties = {"type": primitive_type}
        
        if primitive_type in primitive_types:
            properties["datatype"] = str(primitive_types[primitive_type])
        
        if description:
            properties["description"] = description
        
        return SHACLBrick("Primitive", name, properties)
    
    def add_brick(self, brick: SHACLBrick):
        """Add a brick to the current collection"""
        self.bricks.append(brick)
    
    def remove_brick(self, index: int):
        """Remove a brick by index"""
        if 0 <= index < len(self.bricks):
            del self.bricks[index]
    
    def get_bricks(self) -> List[SHACLBrick]:
        """Get all bricks"""
        return self.bricks.copy()
    
    def clear_bricks(self):
        """Clear all bricks"""
        self.bricks.clear()
    
    def generate_shacl_graph(self) -> Graph:
        """Generate SHACL graph from current bricks"""
        g = Graph()
        
        # Add prefixes
        g.bind("sh", SH)
        g.bind("dash", DASH)
        g.bind("ex", EX)
        g.bind("xsd", XSD)
        
        # Generate SHACL from bricks
        for brick in self.bricks:
            if brick.brick_type == "NodeShape":
                self._add_node_shape(g, brick)
            elif brick.brick_type == "PropertyShape":
                self._add_property_shape(g, brick)
            elif brick.brick_type == "Primitive":
                self._add_primitive_shape(g, brick)
        
        return g
    
    def _add_node_shape(self, g: Graph, brick: SHACLBrick):
        """Add NodeShape to graph"""
        shape_uri = URIRef(brick.uri)
        g.add((shape_uri, RDF.type, SH.NodeShape))
        
        # Add properties
        if "targetClass" in brick.properties:
            g.add((shape_uri, SH.targetClass, URIRef(brick.properties["targetClass"])))
        
        if "description" in brick.properties:
            g.add((shape_uri, SH.description, Literal(brick.properties["description"])))
        
        # Add property shapes
        for prop_name, prop_value in brick.properties.items():
            if prop_name.startswith("property_"):
                self._add_property_to_shape(g, shape_uri, prop_name.replace("property_", ""), prop_value)
    
    def _add_property_shape(self, g: Graph, shape_uri: URIRef, prop_name: str, prop_value: Any):
        """Add a property shape to a node shape"""
        prop_uri = URIRef(f"{shape_uri}/{prop_name}Property")
        g.add((prop_uri, RDF.type, SH.PropertyShape))
        g.add((prop_uri, SH.path, URIRef(prop_value) if isinstance(prop_value, str) else prop_value))
        g.add((prop_uri, SH.name, Literal(prop_name.replace("_", " ").title())))
        g.add((shape_uri, SH.property, prop_uri))
    
    def _add_primitive_shape(self, g: Graph, brick: SHACLBrick):
        """Add primitive shape to graph"""
        prim_uri = URIRef(brick.uri)
        g.add((prim_uri, RDF.type, SH.NodeShape))
        
        # Add primitive type
        if "type" in brick.properties:
            prim_type = brick.properties["type"]
            if prim_type == "string":
                datatype = XSD.string
            elif prim_type == "integer":
                datatype = XSD.integer
            elif prim_type == "decimal":
                datatype = XSD.decimal
            elif prim_type == "date":
                datatype = XSD.date
            elif prim_type == "boolean":
                datatype = XSD.boolean
            elif prim_type == "uri":
                datatype = XSD.anyURI
            else:
                datatype = XSD.string
            
            g.add((prim_uri, SH.targetClass, datatype))
        
        if "description" in brick.properties:
            g.add((prim_uri, SH.description, Literal(brick.properties["description"])))
    
    def export_shacl(self, format: str = "turtle") -> str:
        """Export SHACL graph to string"""
        g = self.generate_shacl_graph()
        return g.serialize(format=format)
    
    def get_brick_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all bricks for UI display"""
        return [brick.to_dict() for brick in self.bricks]


class SHACLEventProcessor:
    """Process SHACL editor events"""
    
    def __init__(self, backend: SHACLBackend):
        self.backend = backend
    
    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process frontend events"""
        event_type = event.get("event")
        
        if event_type == "get_ontology_list":
            return {"status": "success", "data": self.backend.get_ontology_list()}
        
        elif event_type == "get_ontology_terms":
            ontology_name = event.get("ontology")
            if ontology_name:
                terms = self.backend.get_ontology_terms(ontology_name)
                return {"status": "success", "data": terms}
            else:
                return {"status": "error", "message": "No ontology specified"}
        
        elif event_type == "create_brick_from_term":
            try:
                ontology_name = event.get("ontology")
                term_name = event.get("term")
                brick = self.backend.create_brick_from_term(ontology_name, term_name)
                self.backend.add_brick(brick)
                return {"status": "success", "data": brick.to_dict()}
            except ValueError as e:
                return {"status": "error", "message": str(e)}
        
        elif event_type == "create_property_brick":
            try:
                name = event.get("name")
                path = event.get("path")
                datatype = event.get("datatype")
                min_count = event.get("min_count")
                max_count = event.get("max_count")
                description = event.get("description")
                node_kind = event.get("node_kind")
                class_constraint = event.get("class_constraint")
                
                brick = self.backend.create_property_brick(
                    name, path, datatype, min_count, max_count,
                    description, node_kind, class_constraint
                )
                self.backend.add_brick(brick)
                return {"status": "success", "data": brick.to_dict()}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        elif event_type == "create_primitive_brick":
            try:
                name = event.get("name")
                primitive_type = event.get("type")
                description = event.get("description")
                
                brick = self.backend.create_primitive_brick(name, primitive_type, description)
                self.backend.add_brick(brick)
                return {"status": "success", "data": brick.to_dict()}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        elif event_type == "add_brick":
            brick_data = event.get("brick")
            if brick_data:
                brick = SHACLBrick(
                    brick_data.get("type"),
                    brick_data.get("name"),
                    brick_data.get("properties", {})
                )
                self.backend.add_brick(brick)
                return {"status": "success", "data": brick.to_dict()}
            else:
                return {"status": "error", "message": "No brick data provided"}
        
        elif event_type == "remove_brick":
            index = event.get("index")
            if index is not None and 0 <= index < len(self.backend.get_bricks()):
                self.backend.remove_brick(index)
                return {"status": "success", "message": f"Brick {index} removed"}
            else:
                return {"status": "error", "message": "Invalid brick index"}
        
        elif event_type == "clear_bricks":
            self.backend.clear_bricks()
            return {"status": "success", "message": "All bricks cleared"}
        
        elif event_type == "get_bricks":
            return {"status": "success", "data": [brick.to_dict() for brick in self.backend.get_bricks()]}
        
        elif event_type == "export_shacl":
            try:
                format_type = event.get("format", "turtle")
                shacl_data = self.backend.export_shacl(format_type)
                return {"status": "success", "data": shacl_data}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        else:
            return {"status": "error", "message": f"Unknown event type: {event_type}"}
