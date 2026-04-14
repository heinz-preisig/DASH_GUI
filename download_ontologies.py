#!/usr/bin/env python3
"""
Pre-download default ontologies to cache
"""

import os
import sys
import requests
from urllib.parse import urlparse

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def download_ontology(name: str, url: str, cache_dir: str):
    """Download a single ontology"""
    try:
        print(f"Downloading {name} from {url}...")
        
        # Download the file
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Determine file extension
        parsed_url = urlparse(url)
        file_ext = 'ttl'  # default
        if parsed_url.path.endswith('.ttl'):
            file_ext = 'ttl'
        elif parsed_url.path.endswith('.rdf'):
            file_ext = 'rdf'
        elif parsed_url.path.endswith('.jsonld'):
            file_ext = 'jsonld'
        elif parsed_url.path.endswith('.xml'):
            file_ext = 'rdf'
        
        # Try content type
        content_type = response.headers.get('content-type', '').lower()
        if 'text/turtle' in content_type:
            file_ext = 'ttl'
        elif 'rdf+xml' in content_type:
            file_ext = 'rdf'
        elif 'json+ld' in content_type:
            file_ext = 'jsonld'
        
        # Save to cache
        filename = f"{name.lower().replace(' ', '_')}.{file_ext}"
        file_path = os.path.join(cache_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ {name} downloaded to {file_path}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to download {name}: {e}")
        return False

def main():
    """Download all default ontologies"""
    # Create cache directory
    cache_dir = os.path.join(os.getcwd(), 'ontologies', 'cache')
    os.makedirs(cache_dir, exist_ok=True)
    
    print(f"Cache directory: {cache_dir}")
    
    # Default ontologies
    ontologies = {
        "Schema.org": "https://schema.org/version/latest/schemaorg-current-https.ttl",
        "FOAF": "http://xmlns.com/foaf/spec/index.rdf",
        "DCTERMS": "http://purl.org/dc/terms/",
        "BRICK": "https://brickschema.org/schema/1.3.0/Brick.ttl"
    }
    
    print("Downloading default ontologies...")
    success_count = 0
    
    for name, url in ontologies.items():
        if download_ontology(name, url, cache_dir):
            success_count += 1
    
    print(f"\nDownload complete: {success_count}/{len(ontologies)} ontologies downloaded")
    
    # List cached files
    print("\nCached files:")
    for file in os.listdir(cache_dir):
        file_path = os.path.join(cache_dir, file)
        size = os.path.getsize(file_path)
        print(f"  {file} ({size} bytes)")

if __name__ == "__main__":
    main()
