#!/usr/bin/env python3
"""
SHACL Brick Generator Backend Interface
Clean backend API that can work with different frontend types (Qt, web, etc.)
"""

import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from brick_generator import (
    BrickRepository, BrickLibrary, SHACLBrickGenerator, SHACLBrick,
    SHACLConstraint, SHACLTarget, SHACLObjectType
)

class BrickBackendAPI:
    """Backend API for SHACL brick generation with clean frontend separation"""
    
    def __init__(self, repository_path: str = "brick_repositories"):
        """Initialize the backend"""
        self.repository = BrickRepository(repository_path)
        self._initialize_default_library()
    
    def _initialize_default_library(self):
        """Initialize default library if none exists"""
        if not self.repository.libraries:
            default_lib = self.repository.create_library(
                "default", 
                "Default SHACL Brick Library",
                "System"
            )
            self.repository.set_active_library("default")
    
    # ========== REPOSITORY MANAGEMENT ==========
    
    def get_repository_info(self) -> Dict[str, Any]:
        """Get repository information"""
        return {
            "status": "success",
            "data": {
                "libraries": self.repository.list_libraries(),
                "active_library": self.repository.active_library,
                "repository_path": str(self.repository.repository_path)
            }
        }
    
    def create_library(self, name: str, description: str, author: str = "Unknown") -> Dict[str, Any]:
        """Create a new brick library"""
        try:
            library = self.repository.create_library(name, description, author)
            return {
                "status": "success",
                "data": {
                    "library_id": library.name,
                    "name": library.name,
                    "description": library.description,
                    "author": library.author
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def set_active_library(self, library_name: str) -> Dict[str, Any]:
        """Set the active library"""
        try:
            self.repository.set_active_library(library_name)
            return {
                "status": "success",
                "data": {"active_library": library_name}
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": str(e)
            }
    
    def delete_library(self, library_name: str) -> Dict[str, Any]:
        """Delete a library"""
        try:
            self.repository.delete_library(library_name)
            return {
                "status": "success",
                "data": {"deleted_library": library_name}
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    # ========== BRICK MANAGEMENT ==========
    
    def get_library_bricks(self, library_name: Optional[str] = None,
                           object_type: Optional[str] = None,
                           tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get bricks from a library with optional filtering"""
        try:
            if library_name:
                library = self.repository.get_library(library_name)
                if not library:
                    return {"status": "error", "message": f"Library {library_name} not found"}
            else:
                library = self.repository.get_active_library()
                if not library:
                    return {"status": "error", "message": "No active library set"}
            
            bricks = library.list_bricks(object_type, tags)
            brick_data = [brick.to_dict() for brick in bricks]
            
            return {
                "status": "success",
                "data": {
                    "bricks": brick_data,
                    "count": len(brick_data),
                    "library": library.name
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def search_bricks(self, query: str, library_name: Optional[str] = None) -> Dict[str, Any]:
        """Search bricks by query"""
        try:
            if library_name:
                library = self.repository.get_library(library_name)
                if not library:
                    return {"status": "error", "message": f"Library {library_name} not found"}
            else:
                library = self.repository.get_active_library()
                if not library:
                    return {"status": "error", "message": "No active library set"}
            
            bricks = library.search_bricks(query)
            brick_data = [brick.to_dict() for brick in bricks]
            
            return {
                "status": "success",
                "data": {
                    "bricks": brick_data,
                    "count": len(brick_data),
                    "query": query
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_brick_details(self, brick_id: str, library_name: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed information about a specific brick"""
        try:
            if library_name:
                library = self.repository.get_library(library_name)
                if not library:
                    return {"status": "error", "message": f"Library {library_name} not found"}
            else:
                library = self.repository.get_active_library()
                if not library:
                    return {"status": "error", "message": "No active library set"}
            
            brick = library.get_brick(brick_id)
            if not brick:
                return {"status": "error", "message": f"Brick {brick_id} not found"}
            
            return {
                "status": "success",
                "data": brick.to_dict()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    # ========== BRICK CREATION ==========
    
    def get_shacl_object_types(self) -> Dict[str, Any]:
        """Get all supported SHACL object types"""
        return {
            "status": "success",
            "data": {
                "object_types": [t.value for t in SHACLObjectType],
                "node_shape_types": [t.value for t in SHACLObjectType if "NodeShape" in t.value],
                "property_shape_types": [t.value for t in SHACLObjectType if "PropertyShape" in t.value],
                "constraint_types": [t.value for t in SHACLObjectType if "Constraint" in t.value],
                "target_types": [t.value for t in SHACLObjectType if "Target" in t.value],
                "node_kinds": [t.value for t in SHACLObjectType if "Node" in t.value and "Kind" in t.value]
            }
        }
    
    def get_constraint_templates(self) -> Dict[str, Any]:
        """Get constraint templates for brick creation"""
        try:
            library = self.repository.get_active_library()
            if not library:
                return {"status": "error", "message": "No active library set"}
            
            generator = SHACLBrickGenerator(library)
            return {
                "status": "success",
                "data": generator.get_constraint_templates()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_property_templates(self) -> Dict[str, Any]:
        """Get property templates for brick creation"""
        try:
            library = self.repository.get_active_library()
            if not library:
                return {"status": "error", "message": "No active library set"}
            
            generator = SHACLBrickGenerator(library)
            return {
                "status": "success",
                "data": generator.get_property_templates()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def create_nodeshape_brick(self, brick_id: str, name: str, description: str,
                             target_class: Optional[str] = None,
                             properties: Optional[Dict[str, Any]] = None,
                             constraints: Optional[List[Dict[str, Any]]] = None,
                             tags: Optional[List[str]] = None,
                             library_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a NodeShape brick"""
        try:
            if library_name:
                library = self.repository.get_library(library_name)
                if not library:
                    return {"status": "error", "message": f"Library {library_name} not found"}
            else:
                library = self.repository.get_active_library()
                if not library:
                    return {"status": "error", "message": "No active library set"}
            
            generator = SHACLBrickGenerator(library)
            
            # Convert constraint dictionaries to SHACLConstraint objects
            constraint_objects = []
            if constraints:
                for c in constraints:
                    constraint_objects.append(SHACLConstraint(
                        constraint_type=c["constraint_type"],
                        value=c["value"],
                        parameters=c.get("parameters", {})
                    ))
            
            brick = generator.create_nodeshape_brick(
                brick_id, name, description, target_class,
                properties, constraint_objects, tags
            )
            
            return {
                "status": "success",
                "data": brick.to_dict()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def create_propertyshape_brick(self, brick_id: str, name: str, description: str,
                                 path: str,
                                 properties: Optional[Dict[str, Any]] = None,
                                 constraints: Optional[List[Dict[str, Any]]] = None,
                                 tags: Optional[List[str]] = None,
                                 library_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a PropertyShape brick"""
        try:
            if library_name:
                library = self.repository.get_library(library_name)
                if not library:
                    return {"status": "error", "message": f"Library {library_name} not found"}
            else:
                library = self.repository.get_active_library()
                if not library:
                    return {"status": "error", "message": "No active library set"}
            
            generator = SHACLBrickGenerator(library)
            
            # Convert constraint dictionaries to SHACLConstraint objects
            constraint_objects = []
            if constraints:
                for c in constraints:
                    constraint_objects.append(SHACLConstraint(
                        constraint_type=c["constraint_type"],
                        value=c["value"],
                        parameters=c.get("parameters", {})
                    ))
            
            brick = generator.create_propertyshape_brick(
                brick_id, name, description, path,
                properties, constraint_objects, tags
            )
            
            return {
                "status": "success",
                "data": brick.to_dict()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def create_brick_from_template(self, template_type: str, name: str,
                                 parameters: Optional[Dict[str, Any]] = None,
                                 library_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a brick from a predefined template"""
        try:
            if library_name:
                library = self.repository.get_library(library_name)
                if not library:
                    return {"status": "error", "message": f"Library {library_name} not found"}
            else:
                library = self.repository.get_active_library()
                if not library:
                    return {"status": "error", "message": "No active library set"}
            
            generator = SHACLBrickGenerator(library)
            brick = generator.create_brick_from_template(template_type, name, parameters or {})
            
            return {
                "status": "success",
                "data": brick.to_dict()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def update_brick(self, brick_id: str, updates: Dict[str, Any],
                     library_name: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing brick"""
        try:
            if library_name:
                library = self.repository.get_library(library_name)
                if not library:
                    return {"status": "error", "message": f"Library {library_name} not found"}
            else:
                library = self.repository.get_active_library()
                if not library:
                    return {"status": "error", "message": "No active library set"}
            
            brick = library.get_brick(brick_id)
            if not brick:
                return {"status": "error", "message": f"Brick {brick_id} not found"}
            
            # Update brick properties
            if "name" in updates:
                brick.name = updates["name"]
            if "description" in updates:
                brick.description = updates["description"]
            if "properties" in updates:
                brick.properties.update(updates["properties"])
            if "tags" in updates:
                brick.tags = updates["tags"]
            
            return {
                "status": "success",
                "data": brick.to_dict()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def delete_brick(self, brick_id: str, library_name: Optional[str] = None) -> Dict[str, Any]:
        """Delete a brick"""
        try:
            if library_name:
                library = self.repository.get_library(library_name)
                if not library:
                    return {"status": "error", "message": f"Library {library_name} not found"}
            else:
                library = self.repository.get_active_library()
                if not library:
                    return {"status": "error", "message": "No active library set"}
            
            success = library.remove_brick(brick_id)
            if success:
                return {
                    "status": "success",
                    "data": {"deleted_brick": brick_id}
                }
            else:
                return {
                    "status": "error",
                    "message": f"Brick {brick_id} not found"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    # ========== EXPORT/IMPORT ==========
    
    def export_library(self, library_name: Optional[str] = None,
                      file_path: Optional[str] = None) -> Dict[str, Any]:
        """Export library to JSON file"""
        try:
            if library_name:
                library = self.repository.get_library(library_name)
                if not library:
                    return {"status": "error", "message": f"Library {library_name} not found"}
            else:
                library = self.repository.get_active_library()
                if not library:
                    return {"status": "error", "message": "No active library set"}
            
            if not file_path:
                file_path = f"{library.name}_export.json"
            
            library.export_to_json(file_path)
            
            return {
                "status": "success",
                "data": {
                    "exported_library": library.name,
                    "file_path": file_path,
                    "brick_count": len(library.bricks)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def import_library(self, file_path: str, library_name: Optional[str] = None) -> Dict[str, Any]:
        """Import library from JSON file"""
        try:
            if library_name:
                # Create new library with specified name
                library = self.repository.create_library(library_name, "Imported library", "Import")
                library.import_from_json(file_path)
                imported_name = library_name
            else:
                # Import into active library
                library = self.repository.get_active_library()
                if not library:
                    return {"status": "error", "message": "No active library set"}
                library.import_from_json(file_path)
                imported_name = library.name
            
            return {
                "status": "success",
                "data": {
                    "imported_library": imported_name,
                    "file_path": file_path,
                    "brick_count": len(library.bricks)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def export_brick_shacl(self, brick_id: str, library_name: Optional[str] = None,
                          format_type: str = "turtle") -> Dict[str, Any]:
        """Export a brick to SHACL format"""
        try:
            if library_name:
                library = self.repository.get_library(library_name)
                if not library:
                    return {"status": "error", "message": f"Library {library_name} not found"}
            else:
                library = self.repository.get_active_library()
                if not library:
                    return {"status": "error", "message": "No active library set"}
            
            brick = library.get_brick(brick_id)
            if not brick:
                return {"status": "error", "message": f"Brick {brick_id} not found"}
            
            generator = SHACLBrickGenerator(library)
            graph = generator.brick_to_shacl(brick)
            
            shacl_content = graph.serialize(format=format_type)
            
            return {
                "status": "success",
                "data": {
                    "brick_id": brick_id,
                    "format": format_type,
                    "content": shacl_content
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    # ========== STATISTICS ==========
    
    def get_library_statistics(self, library_name: Optional[str] = None) -> Dict[str, Any]:
        """Get library statistics"""
        try:
            if library_name:
                library = self.repository.get_library(library_name)
                if not library:
                    return {"status": "error", "message": f"Library {library_name} not found"}
            else:
                library = self.repository.get_active_library()
                if not library:
                    return {"status": "error", "message": "No active library set"}
            
            stats = library.get_statistics()
            
            return {
                "status": "success",
                "data": stats
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_repository_statistics(self) -> Dict[str, Any]:
        """Get repository-wide statistics"""
        try:
            all_stats = []
            total_bricks = 0
            
            for library in self.repository.libraries.values():
                stats = library.get_statistics()
                all_stats.append(stats)
                total_bricks += stats["total_bricks"]
            
            return {
                "status": "success",
                "data": {
                    "total_libraries": len(self.repository.libraries),
                    "total_bricks": total_bricks,
                    "active_library": self.repository.active_library,
                    "library_stats": all_stats
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

# Event processor for clean frontend/backend communication
class BrickEventProcessor:
    """Process events from frontend with clean API calls"""
    
    def __init__(self, backend: BrickBackendAPI):
        self.backend = backend
    
    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process an event from the frontend"""
        event_type = event.get("event")
        
        if event_type == "get_repository_info":
            return self.backend.get_repository_info()
        
        elif event_type == "create_library":
            return self.backend.create_library(
                event["name"],
                event["description"],
                event.get("author", "Unknown")
            )
        
        elif event_type == "set_active_library":
            return self.backend.set_active_library(event["library_name"])
        
        elif event_type == "get_library_bricks":
            return self.backend.get_library_bricks(
                event.get("library_name"),
                event.get("object_type"),
                event.get("tags")
            )
        
        elif event_type == "search_bricks":
            return self.backend.search_bricks(
                event["query"],
                event.get("library_name")
            )
        
        elif event_type == "get_brick_details":
            return self.backend.get_brick_details(
                event["brick_id"],
                event.get("library_name")
            )
        
        elif event_type == "create_nodeshape_brick":
            return self.backend.create_nodeshape_brick(
                event["brick_id"],
                event["name"],
                event["description"],
                event.get("target_class"),
                event.get("properties"),
                event.get("constraints"),
                event.get("tags"),
                event.get("library_name")
            )
        
        elif event_type == "create_propertyshape_brick":
            return self.backend.create_propertyshape_brick(
                event["brick_id"],
                event["name"],
                event["description"],
                event["path"],
                event.get("properties"),
                event.get("constraints"),
                event.get("tags"),
                event.get("library_name")
            )
        
        elif event_type == "delete_brick":
            return self.backend.delete_brick(
                event["brick_id"],
                event.get("library_name")
            )
        
        elif event_type == "export_library":
            return self.backend.export_library(
                event.get("library_name"),
                event.get("file_path")
            )
        
        elif event_type == "get_shacl_object_types":
            return self.backend.get_shacl_object_types()
        
        elif event_type == "get_constraint_templates":
            return self.backend.get_constraint_templates()
        
        elif event_type == "get_property_templates":
            return self.backend.get_property_templates()
        
        elif event_type == "export_brick_shacl":
            return self.backend.export_brick_shacl(
                event["brick_id"],
                event.get("library_name"),
                event.get("format_type", "turtle")
            )
        
        elif event_type == "get_library_statistics":
            return self.backend.get_library_statistics(event.get("library_name"))
        
        else:
            return {
                "status": "error",
                "message": f"Unknown event type: {event_type}"
            }

def main():
    """Test the backend API"""
    backend = BrickBackendAPI()
    processor = BrickEventProcessor(backend)
    
    print("=== Backend API Test ===\n")
    
    # Test repository info
    result = processor.process_event({"event": "get_repository_info"})
    print("Repository info:", result)
    
    # Test getting bricks
    result = processor.process_event({"event": "get_library_bricks"})
    print(f"\nBricks in library: {result['data']['count']}")
    
    # Test creating a brick
    result = processor.process_event({
        "event": "create_nodeshape_brick",
        "brick_id": "test_person",
        "name": "Test Person",
        "description": "A test person brick",
        "target_class": "foaf:Person",
        "tags": ["test", "person"]
    })
    print(f"\nCreated brick: {result['status']}")
    
    # Test searching
    result = processor.process_event({"event": "search_bricks", "query": "person"})
    print(f"\nSearch results: {result['data']['count']} bricks found")

if __name__ == "__main__":
    main()
