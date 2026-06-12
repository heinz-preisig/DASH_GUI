"""
Ontology Management Module

Handles loading and browsing of ontologies for class and property selection.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from rdflib import Graph, RDF, OWL, URIRef, Literal
    RDFLIB_AVAILABLE = True
except ImportError:
    RDFLIB_AVAILABLE = False
    print("Warning: rdflib not available. Ontology parsing will be limited.")


class OntologyManager:
    """Manages ontology loading and browsing"""
    
    def __init__(self, cache_path: str = None):
        if cache_path is None:
            # Default to the ontologies/cache directory in the DASH_GUI project
            app_dir = Path(__file__).parent.parent.parent
            cache_path = app_dir / "ontologies" / "cache"
        self.cache_path = Path(cache_path)
        self.ontologies: Dict[str, Dict[str, Any]] = {}
        self.load_cached_ontologies()
    
    def load_cached_ontologies(self):
        """Load all cached ontologies"""
        if not self.cache_path.exists():
            return
        
        if not RDFLIB_AVAILABLE:
            print("RDFlib not available, cannot parse ontologies")
            return
        
        for filename in os.listdir(self.cache_path):
            if filename.endswith(('.ttl', '.rdf')):
                filepath = self.cache_path / filename
                ontology_name = filename.replace('.ttl', '').replace('.rdf', '')
                
                try:
                    # Parse RDF/TTL file
                    graph = Graph()
                    format_type = 'turtle' if filename.endswith('.ttl') else 'xml'
                    graph.parse(filepath, format=format_type)
                    
                    # Extract classes and properties
                    classes = []
                    properties = []
                    
                    # Get classes
                    for class_uri in graph.subjects(RDF.type, OWL.Class):
                        if isinstance(class_uri, URIRef):
                            class_name = str(class_uri).split('/')[-1].split('#')[-1]
                            comment = ""
                            for comment_obj in graph.objects(class_uri, URIRef("http://www.w3.org/2000/01/rdf-schema#comment")):
                                if isinstance(comment_obj, Literal):
                                    comment = str(comment_obj)
                                    break
                            
                            classes.append({
                                'uri': str(class_uri),
                                'name': class_name,
                                'comment': comment
                            })
                    
                    # Get properties
                    for prop_uri in graph.subjects(RDF.type, OWL.ObjectProperty):
                        if isinstance(prop_uri, URIRef):
                            prop_name = str(prop_uri).split('/')[-1].split('#')[-1]
                            comment = ""
                            domain = ""
                            range_val = ""
                            
                            # Get comment
                            for comment_obj in graph.objects(prop_uri, URIRef("http://www.w3.org/2000/01/rdf-schema#comment")):
                                if isinstance(comment_obj, Literal):
                                    comment = str(comment_obj)
                                    break
                            
                            # Get domain
                            for domain_obj in graph.objects(prop_uri, URIRef("http://www.w3.org/2000/01/rdf-schema#domain")):
                                if isinstance(domain_obj, URIRef):
                                    domain = str(domain_obj)
                                    break
                            
                            # Get range
                            for range_obj in graph.objects(prop_uri, URIRef("http://www.w3.org/2000/01/rdf-schema#range")):
                                if isinstance(range_obj, URIRef):
                                    range_val = str(range_obj)
                                    break
                            
                            properties.append({
                                'uri': str(prop_uri),
                                'name': prop_name,
                                'comment': comment,
                                'domain': domain,
                                'range': range_val
                            })
                    
                    # Get datatype properties
                    for prop_uri in graph.subjects(RDF.type, OWL.DatatypeProperty):
                        if isinstance(prop_uri, URIRef):
                            prop_name = str(prop_uri).split('/')[-1].split('#')[-1]
                            comment = ""
                            domain = ""
                            range_val = ""
                            
                            # Get comment
                            for comment_obj in graph.objects(prop_uri, URIRef("http://www.w3.org/2000/01/rdf-schema#comment")):
                                if isinstance(comment_obj, Literal):
                                    comment = str(comment_obj)
                                    break
                            
                            # Get domain
                            for domain_obj in graph.objects(prop_uri, URIRef("http://www.w3.org/2000/01/rdf-schema#domain")):
                                if isinstance(domain_obj, URIRef):
                                    domain = str(domain_obj)
                                    break
                            
                            # Get range
                            for range_obj in graph.objects(prop_uri, URIRef("http://www.w3.org/2000/01/rdf-schema#range")):
                                if isinstance(range_obj, URIRef):
                                    range_val = str(range_obj)
                                    break
                            
                            properties.append({
                                'uri': str(prop_uri),
                                'name': prop_name,
                                'comment': comment,
                                'domain': domain,
                                'range': range_val
                            })
                    
                    # Store ontology data
                    self.ontologies[ontology_name] = {
                        'name': ontology_name,
                        'uri': f"http://example.org/{ontology_name}",
                        'prefix': ontology_name.lower(),
                        'classes': {cls['uri']: cls for cls in classes},
                        'properties': {prop['uri']: prop for prop in properties}
                    }
                    
                except Exception as e:
                    print(f"Error parsing ontology {filename}: {e}")
                    continue
    
    def get_ontology_list(self) -> List[Dict[str, Any]]:
        """Get list of available ontologies"""
        result = []
        for name, data in self.ontologies.items():
            result.append({
                'name': name,
                'prefix': data.get('prefix', ''),
                'uri': data.get('uri', ''),
                'class_count': len(data.get('classes', {})),
                'property_count': len(data.get('properties', {}))
            })
        return result
    
    def get_classes(self, ontology_name: str) -> List[Dict[str, Any]]:
        """Get classes from a specific ontology"""
        if ontology_name not in self.ontologies:
            return []
        
        classes = []
        for class_uri, class_data in self.ontologies[ontology_name].get('classes', {}).items():
            classes.append({
                'uri': class_uri,
                'name': class_data.get('name', class_uri.split('#')[-1] if '#' in class_uri else class_uri.split('/')[-1]),
                'comment': class_data.get('comment', ''),
                'ontology': ontology_name
            })
        return sorted(classes, key=lambda x: x['name'])
    
    def get_properties(self, ontology_name: str) -> List[Dict[str, Any]]:
        """Get properties from a specific ontology"""
        if ontology_name not in self.ontologies:
            return []
        
        properties = []
        for prop_uri, prop_data in self.ontologies[ontology_name].get('properties', {}).items():
            properties.append({
                'uri': prop_uri,
                'name': prop_data.get('name', prop_uri.split('#')[-1] if '#' in prop_uri else prop_uri.split('/')[-1]),
                'comment': prop_data.get('comment', ''),
                'domain': prop_data.get('domain', ''),
                'range': prop_data.get('range', ''),
                'ontology': ontology_name
            })
        return sorted(properties, key=lambda x: x['name'])
    
    def search_classes(self, query: str, ontology_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search classes across ontologies"""
        results = []
        ontologies_to_search = [ontology_name] if ontology_name else list(self.ontologies.keys())
        
        for onto_name in ontologies_to_search:
            if onto_name not in self.ontologies:
                continue
            
            for class_uri, class_data in self.ontologies[onto_name].get('classes', {}).items():
                class_name = class_data.get('name', class_uri.split('#')[-1] if '#' in class_uri else class_uri.split('/')[-1])
                comment = class_data.get('comment', '')
                
                if (query.lower() in class_name.lower() or 
                    query.lower() in comment.lower() or 
                    query.lower() in class_uri.lower()):
                    results.append({
                        'uri': class_uri,
                        'name': class_name,
                        'comment': comment,
                        'ontology': onto_name
                    })
        
        return results
    
    def search_properties(self, query: str, ontology_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search properties across ontologies"""
        results = []
        ontologies_to_search = [ontology_name] if ontology_name else list(self.ontologies.keys())
        
        for onto_name in ontologies_to_search:
            if onto_name not in self.ontologies:
                continue
            
            for prop_uri, prop_data in self.ontologies[onto_name].get('properties', {}).items():
                prop_name = prop_data.get('name', prop_uri.split('#')[-1] if '#' in prop_uri else prop_uri.split('/')[-1])
                comment = prop_data.get('comment', '')
                
                if (query.lower() in prop_name.lower() or 
                    query.lower() in comment.lower() or 
                    query.lower() in prop_uri.lower()):
                    results.append({
                        'uri': prop_uri,
                        'name': prop_name,
                        'comment': comment,
                        'domain': prop_data.get('domain', ''),
                        'range': prop_data.get('range', ''),
                        'ontology': onto_name
                    })
        
        return results
