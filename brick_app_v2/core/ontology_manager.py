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
            # Explicit path to ontologies/cache directory in DASH_GUI project
            cache_path = Path("/home/heinz/1_Gits/DASH_GUI/ontologies/cache")
        else:
            cache_path = Path(cache_path)
        
        self.cache_path = cache_path
        self.ontologies: Dict[str, Dict[str, Any]] = {}
        self.load_cached_ontologies()
    
    def load_cached_ontologies(self):
        """Load all cached ontologies"""
        if not self.cache_path.exists():
            print(f"Cache directory not found: {self.cache_path}")
            return
        
        if not RDFLIB_AVAILABLE:
            print("Warning: rdflib not available. Cannot parse ontology files.")
            return
        
        try:
            for cache_file in self.cache_path.glob("*.ttl"):
                if cache_file.is_file():
                    self._parse_ttl_file(cache_file)
            for cache_file in self.cache_path.glob("*.rdf"):
                if cache_file.is_file():
                    self._parse_rdf_file(cache_file)
        except Exception as e:
            print(f"Error loading cached ontologies: {e}")
            pass
    
    def _parse_ttl_file(self, cache_file: Path):
        """Parse TTL file and extract ontology data"""
        try:
            graph = Graph()
            graph.parse(str(cache_file), format="turtle")
            self._extract_ontology_data(graph, cache_file.stem)
        except Exception as e:
            print(f"Error parsing TTL file {cache_file}: {e}")
    
    def _parse_rdf_file(self, cache_file: Path):
        """Parse RDF file and extract ontology data"""
        try:
            graph = Graph()
            graph.parse(str(cache_file), format="xml")
            self._extract_ontology_data(graph, cache_file.stem)
        except Exception as e:
            print(f"Error parsing RDF file {cache_file}: {e}")
    
    def _extract_ontology_data(self, graph: Graph, ontology_name: str):
        """Extract classes and properties from RDF graph"""
        classes = {}
        properties = {}
        
        # Extract classes
        for class_uri in graph.subjects(RDF.type, OWL.Class):
            if isinstance(class_uri, URIRef):
                class_name = str(class_uri).split('#')[-1] if '#' in str(class_uri) else str(class_uri).split('/')[-1]
                comment = ""
                for comment_obj in graph.objects(class_uri, URIRef("http://www.w3.org/2000/01/rdf-schema#comment")):
                    comment = str(comment_obj)
                    break
                
                classes[str(class_uri)] = {
                    'name': class_name,
                    'comment': comment
                }
        
        # Extract properties
        for prop_uri in graph.subjects(RDF.type, OWL.ObjectProperty):
            if isinstance(prop_uri, URIRef):
                prop_name = str(prop_uri).split('#')[-1] if '#' in str(prop_uri) else str(prop_uri).split('/')[-1]
                comment = ""
                domain = ""
                range_val = ""
                
                # Get comment
                for comment_obj in graph.objects(prop_uri, URIRef("http://www.w3.org/2000/01/rdf-schema#comment")):
                    comment = str(comment_obj)
                    break
                
                # Get domain
                for domain_obj in graph.objects(prop_uri, URIRef("http://www.w3.org/2000/01/rdf-schema#domain")):
                    domain = str(domain_obj)
                    break
                
                # Get range
                for range_obj in graph.objects(prop_uri, URIRef("http://www.w3.org/2000/01/rdf-schema#range")):
                    range_val = str(range_obj)
                    break
                
                properties[str(prop_uri)] = {
                    'name': prop_name,
                    'comment': comment,
                    'domain': domain,
                    'range': range_val
                }
        
        for prop_uri in graph.subjects(RDF.type, OWL.DatatypeProperty):
            if isinstance(prop_uri, URIRef):
                prop_name = str(prop_uri).split('#')[-1] if '#' in str(prop_uri) else str(prop_uri).split('/')[-1]
                comment = ""
                domain = ""
                range_val = ""
                
                for comment_obj in graph.objects(prop_uri, URIRef("http://www.w3.org/2000/01/rdf-schema#comment")):
                    comment = str(comment_obj)
                    break
                
                for domain_obj in graph.objects(prop_uri, URIRef("http://www.w3.org/2000/01/rdf-schema#domain")):
                    domain = str(domain_obj)
                    break
                
                for range_obj in graph.objects(prop_uri, URIRef("http://www.w3.org/2000/01/rdf-schema#range")):
                    range_val = str(range_obj)
                    break
                
                properties[str(prop_uri)] = {
                    'name': prop_name,
                    'comment': comment,
                    'domain': domain,
                    'range': range_val
                }
        
        # Store ontology data
        self.ontologies[ontology_name] = {
            'name': ontology_name,
            'uri': "",
            'prefix': ontology_name.lower(),
            'classes': classes,
            'properties': properties
        }
        
        print(f"Loaded {ontology_name}: {len(classes)} classes, {len(properties)} properties")
    
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
