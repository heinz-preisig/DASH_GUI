"""
Brick Integration Module
Interface between schema_app_v2 and brick_app_v2
"""

import os
import sys
from typing import List, Optional, Dict, Any
from pathlib import Path

# Calculate project root and add paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
brick_app_path = os.path.join(project_root, 'brick_app_v2')
shared_libs_path = os.path.join(project_root, 'shared_libraries')

# Add both paths to sys.path
if brick_app_path not in sys.path:
    sys.path.insert(0, brick_app_path)
if shared_libs_path not in sys.path:
    sys.path.insert(0, shared_libs_path)

try:
    # Direct import using exec to avoid module path issues
    brick_core_path = os.path.join(brick_app_path, 'core', 'brick_core_simple.py')
    ontology_path = os.path.join(brick_app_path, 'core', 'ontology_manager.py')
    library_manager_path = os.path.join(shared_libs_path, 'library_manager.py')
    
    # Import brick_core_simple
    with open(brick_core_path, 'r') as f:
        brick_core_code = f.read()
    brick_core_namespace = {}
    exec(brick_core_code, brick_core_namespace)
    BrickCore = brick_core_namespace['BrickCore']
    SHACLBrick = brick_core_namespace['SHACLBrick']
    
    # Import ontology_manager
    with open(ontology_path, 'r') as f:
        ontology_code = f.read()
    ontology_namespace = {}
    exec(ontology_code, ontology_namespace)
    OntologyManager = ontology_namespace['OntologyManager']
    
    # Import library_manager
    with open(library_manager_path, 'r') as f:
        library_code = f.read()
    library_namespace = {}
    exec(library_code, library_namespace)
    shared_library_manager = library_namespace['shared_library_manager']
    
except Exception as e:
    print(f"Warning: Could not import brick_app_v2 modules: {e}")
    BrickCore = None
    SHACLBrick = None
    OntologyManager = None
    shared_library_manager = None


class BrickIntegration:
    """Integration layer for working with brick_app_v2"""
    
    def __init__(self, brick_repository_path: str = None, use_shared_libraries: bool = True):
        if BrickCore is None:
            raise ImportError("brick_app_v2 is not available. Please ensure it's properly installed.")
        
        # Use shared libraries by default
        if use_shared_libraries and brick_repository_path is None:
            # Use the same path as brick_app_v2 - direct path to shared_libraries/bricks
            brick_repository_path = os.path.join(shared_libs_path, 'bricks')
            self.brick_core = BrickCore(repository_path=brick_repository_path, use_shared_libraries=False)
        else:
            self.brick_core = BrickCore(brick_repository_path, use_shared_libraries=False)
        
        self.ontology_manager = OntologyManager()
        
    def get_available_bricks(self, library_name: Optional[str] = None) -> List[SHACLBrick]:
        """Get all available bricks from brick_app_v2"""
        return self.brick_core.get_all_bricks(library_name)
    
    def get_brick_by_id(self, brick_id: str, library_name: Optional[str] = None) -> Optional[SHACLBrick]:
        """Get a specific brick by ID"""
        return self.brick_core.load_brick(brick_id, library_name)
    
    def get_brick_libraries(self) -> List[str]:
        """Get all available brick libraries"""
        return self.brick_core.get_libraries()
    
    def validate_brick_ids(self, brick_ids: List[str], library_name: Optional[str] = None) -> Dict[str, bool]:
        """Validate that all brick IDs exist"""
        results = {}
        for brick_id in brick_ids:
            brick = self.get_brick_by_id(brick_id, library_name)
            results[brick_id] = brick is not None
        return results
    
    def get_node_shape_bricks(self, library_name: Optional[str] = None) -> List[SHACLBrick]:
        """Get only NodeShape bricks (can be root bricks)"""
        bricks = self.get_available_bricks(library_name)
        return [brick for brick in bricks if brick.object_type == "NodeShape"]
    
    def get_property_shape_bricks(self, library_name: Optional[str] = None) -> List[SHACLBrick]:
        """Get only PropertyShape bricks (component bricks)"""
        bricks = self.get_available_bricks(library_name)
        return [brick for brick in bricks if brick.object_type == "PropertyShape"]
    
    def get_brick_compatibility(self, root_brick_id: str, component_brick_ids: List[str], 
                               library_name: Optional[str] = None) -> Dict[str, Any]:
        """Check compatibility between root and component bricks"""
        root_brick = self.get_brick_by_id(root_brick_id, library_name)
        if not root_brick:
            return {"compatible": False, "issues": ["Root brick not found"]}
        
        if root_brick.object_type != "NodeShape":
            return {"compatible": False, "issues": ["Root brick must be a NodeShape"]}
        
        issues = []
        compatible_bricks = []
        
        for component_id in component_brick_ids:
            component_brick = self.get_brick_by_id(component_id, library_name)
            if not component_brick:
                issues.append(f"Component brick {component_id} not found")
                continue
            
            # Check if component brick is compatible with root brick
            if self._is_compatible(root_brick, component_brick):
                compatible_bricks.append(component_id)
            else:
                issues.append(f"Component brick {component_id} may not be compatible with root brick")
        
        return {
            "compatible": len(issues) == 0,
            "issues": issues,
            "compatible_bricks": compatible_bricks,
            "root_brick": {
                "id": root_brick.brick_id,
                "name": root_brick.name,
                "target_class": root_brick.target_class
            }
        }
    
    def _is_compatible(self, root_brick: SHACLBrick, component_brick: SHACLBrick) -> bool:
        """Check if a component brick is compatible with a root brick"""
        # Basic compatibility check - can be extended
        
        # PropertyShape bricks are generally compatible with NodeShape bricks
        if component_brick.object_type == "PropertyShape":
            return True
        
        # NodeShape bricks can be components if they represent related entities
        if component_brick.object_type == "NodeShape":
            # Could check for inheritance relationships, etc.
            return True
        
        return False
    
    def get_brick_suggestions(self, root_brick_id: str, library_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get suggested component bricks for a root brick"""
        root_brick = self.get_brick_by_id(root_brick_id, library_name)
        if not root_brick or root_brick.object_type != "NodeShape":
            return []
        
        suggestions = []
        all_bricks = self.get_available_bricks(library_name)
        
        for brick in all_bricks:
            if brick.brick_id == root_brick_id:
                continue  # Skip the root brick itself
            
            # Suggest PropertyShape bricks
            if brick.object_type == "PropertyShape":
                suggestions.append({
                    "brick_id": brick.brick_id,
                    "name": brick.name,
                    "description": brick.description,
                    "type": brick.object_type,
                    "property_path": brick.property_path,
                    "suggestion_reason": "Property shape for data entry"
                })
            
            # Suggest related NodeShape bricks
            elif brick.object_type == "NodeShape":
                # Could implement more sophisticated logic here
                suggestions.append({
                    "brick_id": brick.brick_id,
                    "name": brick.name,
                    "description": brick.description,
                    "type": brick.object_type,
                    "target_class": brick.target_class,
                    "suggestion_reason": "Related entity"
                })
        
        return suggestions
    
    def get_ontology_classes_for_target(self, target_class: str) -> List[Dict[str, Any]]:
        """Get ontology classes related to a target class"""
        try:
            return self.ontology_manager.get_classes_for_prefix(target_class.split(":")[0])
        except Exception:
            return []
    
    def get_ontology_properties_for_class(self, target_class: str) -> List[Dict[str, Any]]:
        """Get ontology properties for a target class"""
        try:
            return self.ontology_manager.get_properties_for_class(target_class)
        except Exception:
            return []
    
    def export_brick_as_shacl(self, brick_id: str, library_name: Optional[str] = None, 
                           sequence: Optional[int] = None) -> Optional[str]:
        """Export a brick as SHACL Turtle format"""
        brick = self.get_brick_by_id(brick_id, library_name)
        if not brick:
            return None
        
        # Generate SHACL Turtle format
        shacl_lines = []
        
        # Prefix declarations
        shacl_lines.append("@prefix sh: <http://www.w3.org/ns/shacl#> .")
        shacl_lines.append("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .")
        
        if brick.target_class and ":" in brick.target_class:
            prefix = brick.target_class.split(":")[0]
            shacl_lines.append(f"@prefix {prefix}: <http://example.org/{prefix}/#> .")
        
        shacl_lines.append("")
        
        # Shape definition
        if brick.object_type == "NodeShape":
            shacl_lines.append(f"{brick.name} a sh:NodeShape ;")
            if brick.target_class:
                shacl_lines.append(f"    sh:targetClass {brick.target_class} ;")
        else:  # PropertyShape
            shacl_lines.append(f"{brick.name} a sh:PropertyShape ;")
            if brick.property_path:
                shacl_lines.append(f"    sh:path {brick.property_path} ;")
        
        # Add properties
        for prop_name, prop_value in brick.properties.items():
            if prop_name == "datatype":
                shacl_lines.append(f"    sh:datatype {prop_value} ;")
            elif prop_name == "minCount":
                shacl_lines.append(f"    sh:minCount {prop_value} ;")
            elif prop_name == "maxCount":
                shacl_lines.append(f"    sh:maxCount {prop_value} ;")
            elif prop_name == "minLength":
                shacl_lines.append(f"    sh:minLength {prop_value} ;")
            elif prop_name == "maxLength":
                shacl_lines.append(f"    sh:maxLength {prop_value} ;")
        
        # Add constraints
        for constraint in brick.constraints:
            for constraint_type, constraint_value in constraint.items():
                if constraint_type == "pattern":
                    shacl_lines.append(f"    sh:pattern \"{constraint_value}\" ;")
                elif constraint_type == "minInclusive":
                    shacl_lines.append(f"    sh:minInclusive {constraint_value} ;")
                elif constraint_type == "maxInclusive":
                    shacl_lines.append(f"    sh:maxInclusive {constraint_value} ;")
        
        # Add sh:order if sequence is provided
        if sequence is not None:
            shacl_lines.append(f"    sh:order {sequence} ;")
        
        # Remove trailing semicolon from last line
        if shacl_lines and shacl_lines[-1].endswith(" ;"):
            shacl_lines[-1] = shacl_lines[-1][:-2] + " ."
        
        return "\n".join(shacl_lines)
    
    def search_bricks(self, query: str, library_name: Optional[str] = None) -> List[SHACLBrick]:
        """Search bricks by name, description, or tags"""
        bricks = self.get_available_bricks(library_name)
        query_lower = query.lower()
        
        matching_bricks = []
        for brick in bricks:
            if (query_lower in brick.name.lower() or 
                query_lower in brick.description.lower() or
                any(query_lower in tag.lower() for tag in brick.tags)):
                matching_bricks.append(brick)
        
        return matching_bricks
    
    def add_component_to_schema(self, schema_id: str, brick_id: str) -> bool:
        """Add a component brick to a schema"""
        # This is a simplified implementation for the schema_app_v2
        # In a full implementation, this would update the schema structure
        try:
            # For now, we'll just validate that the brick exists
            brick = self.get_brick_by_id(brick_id)
            if not brick:
                raise ValueError(f"Brick '{brick_id}' not found")
            
            # In a full implementation, this would:
            # 1. Load the schema
            # 2. Add the brick to the schema's component list
            # 3. Save the updated schema
            
            return True
        except Exception as e:
            raise ValueError(f"Failed to add component to schema: {str(e)}")
