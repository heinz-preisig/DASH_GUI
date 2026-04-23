#!/usr/bin/env python3
"""
Shared Library Manager
Unified library management for brick_app_v2 and schema_app_v2
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class SharedLibraryManager:
    """Manages shared libraries for both brick and schema applications"""
    
    def __init__(self, base_path: str = "shared_libraries"):
        self.base_path = Path(base_path).absolute()
        # If the path is relative, resolve it from the current working directory's parent (project root)
        if not Path(base_path).is_absolute():
            # Get the project root by going up from the current working directory
            cwd = Path.cwd()
            if cwd.name in ['brick_app_v2', 'schema_app_v2']:
                # We're in a subdirectory, go up to project root
                self.base_path = cwd.parent / base_path
            else:
                # We're at or near project root
                self.base_path = cwd / base_path
        self.base_path = self.base_path.absolute()
        
        self.config_file = self.base_path / "config.json"
        self.config = self._load_config()
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load library configuration"""
        if not self.config_file.exists():
            return self._create_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        default_config = {
            "version": "2.0",
            "libraries": {
                "bricks": {
                    "default_path": "shared_libraries/bricks",
                    "libraries": [
                        {
                            "name": "default",
                            "path": "shared_libraries/bricks/default",
                            "description": "Default brick library",
                            "type": "bricks"
                        }
                    ]
                },
                "schemas": {
                    "default_path": "shared_libraries/schemas",
                    "libraries": [
                        {
                            "name": "default",
                            "path": "shared_libraries/schemas/default",
                            "description": "Default schema library",
                            "type": "schemas"
                        }
                    ]
                }
            }
        }
        
        # Save default config
        self.base_path.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def _ensure_directories(self):
        """Ensure all library directories exist"""
        for lib_type in ["bricks", "schemas"]:
            libraries = self.config["libraries"][lib_type]["libraries"]
            for lib in libraries:
                lib_path = Path(lib["path"])
                lib_path.mkdir(parents=True, exist_ok=True)
                
                # Create subdirectories
                if lib_type == "bricks":
                    (lib_path / "bricks").mkdir(exist_ok=True)
                else:
                    (lib_path / "schemas").mkdir(exist_ok=True)
    
    def get_brick_library_path(self, library_name: str = "default") -> str:
        """Get the absolute path to a brick library parent directory"""
        # Return the absolute path to the parent directory of libraries
        relative_path = self.config["libraries"]["bricks"]["default_path"]
        # Use the absolute base path to resolve the relative path
        project_root = self.base_path.absolute().parent
        return str(project_root / relative_path)
    
    def get_schema_library_path(self, library_name: str = "default") -> str:
        """Get the absolute path to a schema library parent directory"""
        # Return the absolute path to the parent directory of libraries
        relative_path = self.config["libraries"]["schemas"]["default_path"]
        # Use the absolute base path to resolve the relative path
        project_root = self.base_path.absolute().parent
        return str(project_root / relative_path)
    
    def get_brick_libraries(self) -> List[Dict[str, Any]]:
        """Get all brick libraries"""
        return self.config["libraries"]["bricks"]["libraries"]
    
    def get_schema_libraries(self) -> List[Dict[str, Any]]:
        """Get all schema libraries"""
        return self.config["libraries"]["schemas"]["libraries"]
    
    def add_library(self, lib_type: str, name: str, path: str, description: str = ""):
        """Add a new library (legacy method - use create_library instead)"""
        return self.create_library(lib_type, name, path, description)
    
    def create_library(self, lib_type: str, name: str, path: str = None, description: str = "") -> bool:
        """Create a new library with proper validation and directory creation"""
        if lib_type not in ["bricks", "schemas"]:
            raise ValueError("Library type must be 'bricks' or 'schemas'")
        
        # Validate library name
        if not name or not name.strip():
            raise ValueError("Library name cannot be empty")
        
        name = name.strip()
        
        # Check if library already exists
        existing_libs = self.config["libraries"][lib_type]["libraries"]
        for lib in existing_libs:
            if lib["name"] == name:
                raise ValueError(f"Library '{name}' already exists")
        
        # Generate path if not provided
        if path is None:
            path = f"shared_libraries/{lib_type}/{name}"
        
        # Create the library directory
        lib_path = Path(path)
        if not lib_path.is_absolute():
            # Resolve relative path from project root
            project_root = self.base_path.absolute().parent
            lib_path = project_root / path
        
        try:
            lib_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories based on library type
            if lib_type == "bricks":
                # Bricks are stored directly in the library directory
                pass  # No subdirectory needed based on current structure
            else:
                # Schemas might need subdirectories
                (lib_path / "schemas").mkdir(exist_ok=True)
            
        except Exception as e:
            raise RuntimeError(f"Failed to create library directory: {e}")
        
        # Add to configuration
        new_lib = {
            "name": name,
            "path": path,
            "description": description,
            "type": lib_type,
            "created_at": datetime.now().isoformat() if 'datetime' in globals() else None
        }
        
        self.config["libraries"][lib_type]["libraries"].append(new_lib)
        self._save_config()
        
        return True
    
    def delete_library(self, lib_type: str, name: str, archive: bool = True) -> bool:
        """Delete a library with optional archiving"""
        if lib_type not in ["bricks", "schemas"]:
            raise ValueError("Library type must be 'bricks' or 'schemas'")
        
        # Find the library
        libraries = self.config["libraries"][lib_type]["libraries"]
        lib_to_delete = None
        lib_index = -1
        
        for i, lib in enumerate(libraries):
            if lib["name"] == name:
                lib_to_delete = lib
                lib_index = i
                break
        
        if lib_to_delete is None:
            raise ValueError(f"Library '{name}' not found")
        
        # Prevent deletion of default library
        if name == "default":
            raise ValueError("Cannot delete the default library")
        
        try:
            # Archive the library if requested
            if archive:
                self._archive_library(lib_to_delete)
            
            # Remove the library directory
            lib_path = Path(lib_to_delete["path"])
            if not lib_path.is_absolute():
                project_root = self.base_path.absolute().parent
                lib_path = project_root / lib_to_delete["path"]
            
            if lib_path.exists():
                import shutil
                shutil.rmtree(lib_path)
            
            # Remove from configuration
            libraries.pop(lib_index)
            self._save_config()
            
            return True
            
        except Exception as e:
            raise RuntimeError(f"Failed to delete library: {e}")
    
    def _archive_library(self, library_config: Dict[str, Any]):
        """Archive a library before deletion"""
        lib_path = Path(library_config["path"])
        if not lib_path.is_absolute():
            project_root = self.base_path.absolute().parent
            lib_path = project_root / library_config["path"]
        
        if not lib_path.exists():
            return  # Nothing to archive
        
        # Create archive directory
        archive_dir = self.base_path / "archive" / library_config["type"]
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped archive
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{library_config['name']}_{timestamp}"
        archive_path = archive_dir / archive_name
        
        try:
            import shutil
            shutil.make_archive(
                str(archive_path),
                'zip',
                str(lib_path.parent),
                lib_path.name
            )
            
            # Create archive metadata
            metadata = {
                "original_name": library_config["name"],
                "original_path": library_config["path"],
                "description": library_config.get("description", ""),
                "type": library_config["type"],
                "archived_at": datetime.now().isoformat(),
                "archive_file": f"{archive_name}.zip"
            }
            
            metadata_file = archive_dir / f"{archive_name}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Failed to archive library '{library_config['name']}': {e}")
    
    def get_archived_libraries(self, lib_type: str = None) -> List[Dict[str, Any]]:
        """Get list of archived libraries"""
        archive_dir = self.base_path / "archive"
        if not archive_dir.exists():
            return []
        
        archived = []
        for archive_type in ["bricks", "schemas"]:
            if lib_type and archive_type != lib_type:
                continue
                
            type_archive_dir = archive_dir / archive_type
            if not type_archive_dir.exists():
                continue
            
            for metadata_file in type_archive_dir.glob("*_metadata.json"):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    archived.append(metadata)
                except Exception:
                    continue
        
        return sorted(archived, key=lambda x: x.get('archived_at', ''), reverse=True)
    
    def restore_library(self, archive_name: str, new_name: str = None) -> bool:
        """Restore a library from archive"""
        archive_dir = self.base_path / "archive"
        metadata_file = None
        
        # Find the archive metadata
        for metadata_path in archive_dir.rglob("*_metadata.json"):
            if metadata_path.stem.startswith(archive_name):
                metadata_file = metadata_path
                break
        
        if not metadata_file:
            raise ValueError(f"Archive '{archive_name}' not found")
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Determine new library name
            restore_name = new_name or metadata["original_name"]
            
            # Check if name already exists
            lib_type = metadata["type"]
            existing_libs = [lib["name"] for lib in self.config["libraries"][lib_type]["libraries"]]
            if restore_name in existing_libs:
                raise ValueError(f"Library '{restore_name}' already exists")
            
            # Extract the archive
            archive_file = metadata_file.parent / metadata["archive_file"]
            restore_path = Path(metadata["original_path"])
            if not restore_path.is_absolute():
                project_root = self.base_path.absolute().parent
                restore_path = project_root / metadata["original_path"]
            
            import shutil
            shutil.unpack_archive(str(archive_file), str(restore_path.parent))
            
            # Create library configuration
            self.create_library(
                lib_type=lib_type,
                name=restore_name,
                path=metadata["original_path"],
                description=metadata.get("description", f"Restored from archive on {datetime.now().strftime('%Y-%m-%d')}")
            )
            
            return True
            
        except Exception as e:
            raise RuntimeError(f"Failed to restore library: {e}")
    
    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def migrate_from_legacy(self, brick_source: str = "brick_app_v2/brick_repositories_v2", 
                           schema_source: str = "schema_app_v2/repositories"):
        """Migrate from legacy library structure"""
        # Migrate bricks
        brick_source_path = Path(brick_source)
        if brick_source_path.exists():
            for lib_dir in brick_source_path.iterdir():
                if lib_dir.is_dir():
                    target_dir = self.base_path / "bricks" / lib_dir.name
                    if target_dir.exists():
                        # Copy brick files
                        brick_files = lib_dir / "bricks"
                        if brick_files.exists():
                            target_bricks = target_dir / "bricks"
                            target_bricks.mkdir(parents=True, exist_ok=True)
                            
                            for brick_file in brick_files.glob("*.json"):
                                target_file = target_bricks / brick_file.name
                                if not target_file.exists():
                                    import shutil
                                    shutil.copy2(brick_file, target_file)
        
        # Migrate schemas
        schema_source_path = Path(schema_source)
        if schema_source_path.exists():
            for lib_dir in schema_source_path.iterdir():
                if lib_dir.is_dir():
                    target_dir = self.base_path / "schemas" / lib_dir.name
                    if not target_dir.exists():
                        import shutil
                        shutil.copytree(lib_dir, target_dir)


# Global instance for easy access
shared_library_manager = SharedLibraryManager()
