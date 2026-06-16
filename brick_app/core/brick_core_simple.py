"""
Core SHACL Brick Management Module - Fixed Version

This module contains the essential logic for creating, editing, and managing SHACL bricks.
It's designed to be interface-agnostic and can be used by GUI, web, or CLI interfaces.
"""

import json
import os
import re
import sys
import uuid
from pathlib import Path as _Path
_dash_gui_root = str(_Path(__file__).parent.parent.parent)
if _dash_gui_root not in sys.path:
    sys.path.insert(0, _dash_gui_root)
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict


def sanitize_filename(name: str, max_length: int = 30) -> str:
    """Sanitize name for use in filename"""
    # Replace spaces and special chars with underscore
    sanitized = re.sub(r'[^\w\s-]', '', name).strip()
    sanitized = re.sub(r'[\s]+', '_', sanitized)
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    return sanitized.lower() or "brick"



@dataclass
class LeafProperty:
    """Represents a leaf property (sh:property entry) within a NodeShape brick"""
    path: str  # sh:path IRI
    label: str = ""  # rdfs:label
    datatype: Optional[str] = None  # xsd:string, xsd:decimal, etc.
    node_kind: Optional[str] = None  # sh:IRI for dropdowns
    sh_class: Optional[str] = None  # sh:class - semantic class IRI for ontology linking
    in_values: List[str] = field(default_factory=list)  # sh:in (IRIs or literals)
    has_value: Optional[str] = None  # sh:hasValue for static labels
    min_count: int = 1
    max_count: Optional[int] = 1
    description: str = ""
    min_inclusive: Optional[float] = None
    max_inclusive: Optional[float] = None
    single_line: Optional[bool] = None  # dash:singleLine
    default_unit: Optional[str] = None  # preferred unit IRI (e.g. qudt:KiloGM); emitted as sh:defaultValue
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LeafProperty':
        # Migrate legacy 'unit' key saved by older UI versions
        if 'unit' in data and 'default_unit' not in data:
            data = {**data, 'default_unit': data['unit']}
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)


@dataclass
class SHACLBrick:
    """Modern SHACL brick representation - all bricks are NodeShapes with leaf properties"""
    brick_id: str
    name: str
    description: str
    template_type: str = "custom"  # free_text, decimal_with_unit, dropdown_iri, date_field, static_label, file_upload, xone_choice, custom
    namespace: str = "ex"  # IRI prefix
    target_class: str = ""  # sh:targetClass IRI
    display_label: str = ""  # human-readable form title (rdfs:label); falls back to name if empty
    leaf_properties: List[Dict[str, Any]] = field(default_factory=list)  # List of LeafProperty dicts
    xone_alternatives: List[List[Dict[str, Any]]] = field(default_factory=list)  # For xone_choice template type
    tags: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Legacy fields for backward compatibility (will be removed in future)
    object_type: str = "NodeShape"  # Always "NodeShape" in modern format
    properties: Dict[str, Any] = field(default_factory=dict)
    constraints: List[Dict[str, Any]] = field(default_factory=list)
    targets: List[Dict[str, Any]] = field(default_factory=list)
    property_path: str = ""
    
    def __post_init__(self):
        """Set timestamps after initialization"""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SHACLBrick':
        """Create from dictionary - filters out unknown fields for forward compatibility"""
        # Filter to only valid dataclass fields
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def update_timestamp(self):
        """Update the modification timestamp"""
        self.updated_at = datetime.now().isoformat()


class BrickCore:
    """Core brick management functionality"""

    def __init__(self, repository_path: str = None, use_shared_libraries: bool = True):
        # Use shared libraries by default
        if use_shared_libraries and repository_path is None:
            from common import shared_library_manager
            self.repository_path = shared_library_manager.get_brick_library_path()
            self.shared_library_manager = shared_library_manager
        else:
            # Use provided repository path
            if repository_path is None:
                raise ValueError("Repository path must be provided when not using shared libraries")
            self.repository_path = os.path.abspath(repository_path)
            self.shared_library_manager = None
        
        os.makedirs(self.repository_path, exist_ok=True)
        self.current_brick: Optional[SHACLBrick] = None
        self.active_library: str = "default"
        
        # Ensure default library exists
        self._ensure_library_exists("default")
    
    def _ensure_library_exists(self, library_name: str):
        """Ensure a library directory exists"""
        library_path = os.path.join(self.repository_path, library_name)
        # Bricks are stored directly in the library directory, no nested bricks subdirectory needed
        
        os.makedirs(library_path, exist_ok=True)
    
    def create_brick(self, brick_type: str = "NodeShape", name: str = "") -> SHACLBrick:
        """Create a new brick"""
        brick = SHACLBrick(
            brick_id=str(uuid.uuid4()),
            name=name or f"New {brick_type}",
            description="",
            object_type=brick_type
        )
        self.current_brick = brick
        return brick
    
    def load_brick(self, brick_id: str, library_name: Optional[str] = None) -> Optional[SHACLBrick]:
        """Load a brick from storage by ID, searching all libraries if needed"""
        search_libs = [library_name] if library_name else self.get_libraries()

        for lib_name in search_libs:
            library_path = os.path.join(self.repository_path, lib_name)
            if not os.path.exists(library_path):
                continue

            for filename in os.listdir(library_path):
                # Match full brick_id or partial (first 8 chars of UUID)
                if (filename.endswith(f"_{brick_id}.json") or 
                    filename == f"{brick_id}.json" or
                    filename.endswith(f"_{brick_id[:8]}.json") or
                    filename == f"{brick_id[:8]}.json"):
                    brick_file = os.path.join(library_path, filename)
                    try:
                        with open(brick_file, 'r') as f:
                            data = json.load(f)
                        brick = SHACLBrick.from_dict(data)
                        self.current_brick = brick
                        self.active_library = lib_name
                        return brick
                    except Exception:
                        continue
        return None
    
    def save_brick(self, brick: Optional[SHACLBrick] = None) -> bool:
        """Save current brick to storage"""
        brick_to_save = brick or self.current_brick
        if not brick_to_save:
            print("DEBUG: No brick to save")
            return False
        
        # Validate brick
        if not brick_to_save.name.strip():
            print(f"DEBUG: Brick name is empty")
            return False
        
        if not brick_to_save.brick_id:
            print(f"DEBUG: Brick ID is missing")
            return False
        
        if brick_to_save.object_type == "PropertyShape" and not brick_to_save.property_path.strip():
            print(f"DEBUG: PropertyShape missing property_path")
            return False
        
        # Update timestamp
        brick_to_save.update_timestamp()
        
        # Save to file with name_UUID format
        lib_name = self.active_library
        # Bricks are stored directly in the library directory, not in a nested bricks subdirectory
        library_path = os.path.join(self.repository_path, lib_name)
        safe_name = sanitize_filename(brick_to_save.name)
        brick_file = os.path.join(library_path, f"{safe_name}_{brick_to_save.brick_id}.json")
        
        # Ensure directory exists
        os.makedirs(library_path, exist_ok=True)
        
        try:
            with open(brick_file, 'w') as f:
                json.dump(brick_to_save.to_dict(), f, indent=2)
        except Exception as e:
            print(f"DEBUG: Save failed with error: {e}")
            return False

        # Write .ttl alongside .json
        try:
            from brick_app.core.brick_generator import SHACLBrickGenerator, BrickLibrary
            temp_lib = BrickLibrary(lib_name, "", "System")
            temp_lib.add_brick(brick_to_save)
            generator = SHACLBrickGenerator(temp_lib)
            graph = generator.brick_to_shacl(brick_to_save)
            ttl_file = os.path.splitext(brick_file)[0] + ".ttl"
            with open(ttl_file, 'w') as f:
                f.write(graph.serialize(format="turtle"))
        except Exception as e:
            print(f"DEBUG: TTL generation failed: {e}")

        return True
    
    def get_all_bricks(self, library_name: Optional[str] = None) -> List[SHACLBrick]:
        """Get all bricks from a library"""
        lib_name = library_name or self.active_library
        # Bricks are stored directly in the library directory, not in a nested bricks subdirectory
        bricks_dir = os.path.join(self.repository_path, lib_name)
        
        if not os.path.exists(bricks_dir):
            return []
        
        bricks = []
        try:
            brick_files = [f for f in os.listdir(bricks_dir) if f.endswith('.json')]
                
            for brick_file in brick_files:
                brick_path = os.path.join(bricks_dir, brick_file)
                try:
                    with open(brick_path, 'r') as f:
                        data = json.load(f)
                    brick = SHACLBrick.from_dict(data)
                    bricks.append(brick)
                except Exception:
                    continue
        except Exception:
            # Return empty list on any error
            pass
        
        return bricks
    
    def delete_brick(self, brick_id: str, library_name: Optional[str] = None) -> bool:
        """Delete a brick"""
        lib_name = library_name or self.active_library
        library_path = os.path.join(self.repository_path, lib_name)
        
        # Find file ending with brick_id.json (supports full UUID or first 8 chars)
        brick_file = None
        for filename in os.listdir(library_path):
            if (filename.endswith(f"_{brick_id}.json") or 
                filename == f"{brick_id}.json" or
                filename.endswith(f"_{brick_id[:8]}.json") or
                filename == f"{brick_id[:8]}.json"):
                brick_file = os.path.join(library_path, filename)
                break
        
        if not brick_file:
            return False
        
        try:
            os.remove(brick_file)
            # Also try to delete corresponding TTL file
            ttl_file = brick_file.replace('.json', '.ttl')
            if os.path.exists(ttl_file):
                os.remove(ttl_file)
            if self.current_brick and (self.current_brick.brick_id == brick_id or 
                                        self.current_brick.brick_id.startswith(brick_id[:8])):
                self.current_brick = None
            return True
        except Exception:
            return False
    
    def update_current_brick(self, **kwargs):
        """Update current brick with new values"""
        if not self.current_brick:
            return
        
        for key, value in kwargs.items():
            if hasattr(self.current_brick, key):
                setattr(self.current_brick, key, value)
        
        self.current_brick.update_timestamp()
    
    def add_property(self, prop_name: str, prop_data: Dict[str, Any]):
        """Add a property to current brick"""
        if not self.current_brick:
            return
        
        self.current_brick.properties[prop_name] = prop_data
        self.current_brick.update_timestamp()
    
    def remove_property(self, prop_name: str):
        """Remove a property from current brick"""
        if not self.current_brick or prop_name not in self.current_brick.properties:
            return
        
        del self.current_brick.properties[prop_name]
        self.current_brick.update_timestamp()
    
    def add_constraint(self, constraint_data: Dict[str, Any]):
        """Add a constraint to current brick"""
        if not self.current_brick:
            return
        
        self.current_brick.constraints.append(constraint_data)
        self.current_brick.update_timestamp()
    
    def remove_constraint(self, index: int):
        """Remove a constraint by index"""
        if not self.current_brick or 0 <= index >= len(self.current_brick.constraints):
            return
        
        del self.current_brick.constraints[index]
        self.current_brick.update_timestamp()
    
    def add_constraint_to_property(self, prop_name: str, constraint_data: Dict[str, Any]) -> tuple[bool, str]:
        """Add constraint to a specific property"""
        if not self.current_brick:
            return False, "No brick is currently being edited"
        
        if prop_name not in self.current_brick.properties:
            return False, f"Property '{prop_name}' not found"
        
        prop = self.current_brick.properties[prop_name]
        if not isinstance(prop, dict):
            return False, f"Property '{prop_name}' has invalid data type"
        
        if 'constraints' not in prop:
            prop['constraints'] = []
        
        prop['constraints'].append(constraint_data)
        self.current_brick.update_timestamp()
        return True, "Constraint added successfully"
    
    def update_constraint_on_property(self, prop_name: str, index: int, constraint_data: Dict[str, Any]) -> tuple[bool, str]:
        """Update constraint at specific index on a property"""
        if not self.current_brick:
            return False, "No brick is currently being edited"
        
        if prop_name not in self.current_brick.properties:
            return False, f"Property '{prop_name}' not found"
        
        prop = self.current_brick.properties[prop_name]
        if not isinstance(prop, dict):
            return False, f"Property '{prop_name}' has invalid data type"
        
        constraints = prop.get('constraints', [])
        if not (0 <= index < len(constraints)):
            return False, f"Invalid constraint index {index}"
        
        constraints[index] = constraint_data
        self.current_brick.update_timestamp()
        return True, "Constraint updated successfully"
    
    def remove_constraint_from_property(self, prop_name: str, index: int) -> tuple[bool, str]:
        """Remove constraint at specific index from a property"""
        if not self.current_brick:
            return False, "No brick is currently being edited"
        
        if prop_name not in self.current_brick.properties:
            return False, f"Property '{prop_name}' not found"
        
        prop = self.current_brick.properties[prop_name]
        if not isinstance(prop, dict):
            return False, f"Property '{prop_name}' has invalid data type"
        
        constraints = prop.get('constraints', [])
        if not (0 <= index < len(constraints)):
            return False, f"Invalid constraint index {index}"
        
        constraints.pop(index)
        self.current_brick.update_timestamp()
        return True, "Constraint removed successfully"
    
    def get_libraries(self) -> List[str]:
        """Get list of all libraries"""
        libraries = []
        
        try:
            if not os.path.exists(self.repository_path):
                return ["default"]
            
            for item_name in os.listdir(self.repository_path):
                item_path = os.path.join(self.repository_path, item_name)
                if os.path.isdir(item_path) and item_name != "_archive":
                    # Any directory except archive is considered a library
                    libraries.append(item_name)
        except Exception as e:
            print(f"Error getting libraries: {e}")
            return ["default"]
        
        if not libraries:
            return ["default"]
        
        return sorted(libraries)
    
    def delete_library(self, library_name: str) -> bool:
        """Delete a library by archiving to ZIP and removing directory (matches PyQt behavior)"""
        if library_name == "default":
            return False  # Don't allow deleting the default library
        
        lib_path = os.path.join(self.repository_path, library_name)
        if not os.path.exists(lib_path):
            return False
        
        try:
            import shutil
            import json
            import zipfile
            from datetime import datetime
            from pathlib import Path
            
            # Archive to external archive folder (outside repo)
            repo_path = Path(self.repository_path)
            archive_dir = repo_path.parent / 'archive' / 'bricks'
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            # Create timestamped archive
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{library_name}_{timestamp}"
            archive_path = archive_dir / archive_name
            
            # Create ZIP archive of the library
            zip_file = shutil.make_archive(str(archive_path), 'zip', str(repo_path), library_name)
            
            # Create metadata JSON
            metadata = {
                "original_name": library_name,
                "original_path": str(lib_path),
                "type": "bricks",
                "archived_at": datetime.now().isoformat(),
                "archive_file": f"{archive_name}.zip"
            }
            
            metadata_file = archive_dir / f"{archive_name}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Remove the original directory
            if os.path.exists(lib_path):
                shutil.rmtree(lib_path)
            
            # If this was the active library, switch to default
            if self.active_library == library_name:
                self.active_library = "default"
            
            return True
        except Exception as e:
            print(f"DEBUG: Failed to archive library: {e}")
            return False
    
    def set_active_library(self, library_name: str):
        """Set the active library"""
        lib_path = os.path.join(self.repository_path, library_name)
        if os.path.exists(lib_path):
            self.active_library = library_name
            return True
        return False
    
    def list_archived_libraries(self) -> List[Dict[str, Any]]:
        """List all archived libraries with metadata"""
        from pathlib import Path
        import json
        
        archive_dir = Path(self.repository_path).parent / 'archive' / 'bricks'
        if not archive_dir.exists():
            return []
        
        archives = []
        for metadata_file in archive_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                    archives.append(data)
            except Exception:
                continue
        
        # Sort by archived_at date (newest first)
        archives.sort(key=lambda x: x.get('archived_at', ''), reverse=True)
        return archives
    
    def restore_library(self, archive_name: str) -> Tuple[bool, str, str]:
        """Restore an archived library with auto-versioning for conflicts
        
        Returns: (success, message, restored_name)
        """
        from pathlib import Path
        import zipfile
        import shutil
        
        archive_dir = Path(self.repository_path).parent / 'archive' / 'bricks'
        zip_file = archive_dir / f"{archive_name}.zip"
        metadata_file = archive_dir / f"{archive_name}_metadata.json"
        
        if not zip_file.exists():
            return False, f"Archive '{archive_name}' not found", ""
        
        try:
            # Read metadata to get original name
            original_name = archive_name.rsplit('_', 1)[0]  # Remove timestamp
            if '_' in archive_name:
                # Try to get from metadata first
                try:
                    import json
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        original_name = metadata.get('original_name', original_name)
                except Exception:
                    pass
            
            # Determine target name (handle conflicts with versioning)
            target_name = original_name
            counter = 2
            while os.path.exists(os.path.join(self.repository_path, target_name)):
                target_name = f"{original_name}_v{counter}"
                counter += 1
            
            # Extract ZIP to repository
            target_path = Path(self.repository_path) / target_name
            with zipfile.ZipFile(zip_file, 'r') as zf:
                zf.extractall(self.repository_path)
            
            # If extracted folder name differs from target_name, rename it
            extracted_path = Path(self.repository_path) / original_name
            if extracted_path.exists() and target_name != original_name:
                extracted_path.rename(target_path)
            
            # Clean up archive files (move semantics)
            try:
                zip_file.unlink()
                if metadata_file.exists():
                    metadata_file.unlink()
            except Exception as cleanup_error:
                print(f"Warning: Failed to clean up archive files: {cleanup_error}")
            
            return True, f"Library restored as '{target_name}'", target_name
            
        except Exception as e:
            return False, f"Failed to restore library: {e}", ""

    def copy_library(self, source_name: str, target_name: str) -> Tuple[bool, str]:
        """Copy a library with a new name

        Args:
            source_name: Name of the library to copy
            target_name: Desired name for the new copy

        Returns:
            Tuple of (success, message)
        """
        import shutil

        source_path = Path(self.repository_path) / source_name
        target_path = Path(self.repository_path) / target_name

        # Validate source exists
        if not source_path.exists():
            return False, f"Source library '{source_name}' not found"

        # Validate target doesn't already exist
        if target_path.exists():
            return False, f"Library '{target_name}' already exists"

        # Validate target name is valid
        if not target_name.strip() or target_name.startswith("_"):
            return False, "Invalid library name"

        try:
            # Copy entire directory tree
            shutil.copytree(source_path, target_path)

            # Update brick IDs in copied library to avoid conflicts
            for brick_file in target_path.glob("*.json"):
                try:
                    with open(brick_file, 'r') as f:
                        data = json.load(f)

                    # Generate new brick ID
                    old_id = data.get('brick_id', '')
                    if old_id:
                        new_id = str(uuid.uuid4())
                        data['brick_id'] = new_id
                        data['name'] = data.get('name', 'Unnamed') + f" (copy)"
                        data['updated_at'] = datetime.now().isoformat()

                        # Save with new filename reflecting new ID
                        safe_name = sanitize_filename(data['name'])
                        new_filename = f"{safe_name}_{new_id}.json"

                        with open(target_path / new_filename, 'w') as f:
                            json.dump(data, f, indent=2)

                        # Remove old file
                        brick_file.unlink()

                        # Also rename TTL if exists
                        old_ttl = brick_file.with_suffix('.ttl')
                        if old_ttl.exists():
                            old_ttl.unlink()
                except Exception as e:
                    print(f"Warning: Failed to update brick ID in {brick_file}: {e}")
                    continue

            return True, f"Library '{source_name}' copied as '{target_name}'"

        except Exception as e:
            return False, f"Failed to copy library: {e}"
