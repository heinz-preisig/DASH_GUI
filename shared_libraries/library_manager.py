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

    def __init__(self):
        # Check for Docker environment override (data mounted at /app/data)
        docker_data_path = os.environ.get('SHARED_LIBRARIES_ROOT', '/app/data')
        if os.path.exists(docker_data_path):
            # Docker mode: data is mounted at /app/shared_libraries
            self.base_path = Path(docker_data_path).resolve()
            self.config_file = self.base_path / "library_registry.json"
            self.config = self._load_config()
        else:
            # Local dev mode: external shared_libraries at sibling of DASH_GUI project
            project_root = Path(__file__).resolve().parent.parent
            self.base_path = (project_root.parent / "shared_libraries").resolve()
            self.config_file = self.base_path / "library_registry.json"
            self.config = self._load_config()

        # Ensure all registered library directories exist
        self._ensure_directories()

    def _load_config_local(self) -> Dict[str, Any]:
        """Load config for local development (config.json in project root)"""
        project_root = Path(__file__).resolve().parent.parent
        config_file = project_root / "library_registry.json"
        if not config_file.exists():
            return self._create_default_config()
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception:
            return self._create_default_config()
    
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
            "shared_library_root": "shared_libraries",
            "libraries": {
                "bricks": {
                    "libraries": [
                        {"name": "default", "description": "Default brick library"}
                    ]
                },
                "schemas": {
                    "libraries": [
                        {"name": "default", "description": "Default schema library"}
                    ]
                }
            }
        }
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        return default_config
    
    def lib_path(self, lib_type: str, name: str) -> Path:
        """Canonical path for a library: base_path / lib_type / name"""
        return self.base_path / lib_type / name

    def _ensure_directories(self):
        """Ensure all registered library directories exist"""
        for lib_type in ["bricks", "schemas"]:
            for lib in self.config["libraries"][lib_type]["libraries"]:
                self.lib_path(lib_type, lib["name"]).mkdir(parents=True, exist_ok=True)
    
    def get_brick_library_path(self, library_name: str = "default") -> str:
        """Absolute path to the bricks root (parent of all brick libraries)"""
        return str(self.base_path / "bricks")

    def get_schema_library_path(self, library_name: str = "default") -> str:
        """Absolute path to the schemas root (parent of all schema libraries)"""
        return str(self.base_path / "schemas")
    
    def get_brick_libraries(self) -> List[Dict[str, Any]]:
        """Get all brick libraries from config"""
        return self.config["libraries"]["bricks"]["libraries"]

    def get_schema_libraries(self) -> List[Dict[str, Any]]:
        """Get all schema libraries from config"""
        return self.config["libraries"]["schemas"]["libraries"]

    def scan_brick_libraries(self) -> List[Dict[str, Any]]:
        """Scan filesystem to discover all brick libraries in the bricks directory"""
        brick_libs = []
        bricks_dir = self.base_path / "bricks"

        if not bricks_dir.exists():
            return brick_libs

        for lib_dir in bricks_dir.iterdir():
            if lib_dir.is_dir():
                # Count brick files (json files excluding metadata.json)
                brick_count = 0
                for f in lib_dir.glob("*.json"):
                    if f.name != "metadata.json":
                        brick_count += 1

                # Check if already in config to get description
                config_lib = next(
                    (lib for lib in self.config["libraries"]["bricks"]["libraries"]
                     if lib["name"] == lib_dir.name), None
                )

                # Compute relative path if project_root is available (local dev), else use absolute
                try:
                    rel_path = str(lib_dir.relative_to(self.project_root)) if hasattr(self, 'project_root') else str(lib_dir)
                except ValueError:
                    rel_path = str(lib_dir)

                brick_libs.append({
                    "name": lib_dir.name,
                    "path": rel_path,
                    "description": config_lib.get("description", f"Brick library '{lib_dir.name}'") if config_lib else f"Brick library '{lib_dir.name}'",
                    "type": "bricks",
                    "brick_count": brick_count,
                    "absolute_path": str(lib_dir.absolute())
                })

        return brick_libs

    def scan_schema_libraries(self) -> List[Dict[str, Any]]:
        """Scan filesystem to discover all schema libraries in the schemas directory"""
        schema_libs = []
        schemas_dir = self.base_path / "schemas"

        if not schemas_dir.exists():
            return schema_libs

        for lib_dir in schemas_dir.iterdir():
            if lib_dir.is_dir():
                # Check if already in config to get description
                config_lib = next(
                    (lib for lib in self.config["libraries"]["schemas"]["libraries"]
                     if lib["name"] == lib_dir.name), None
                )

                # Compute relative path if project_root is available (local dev), else use absolute
                try:
                    rel_path = str(lib_dir.relative_to(self.project_root)) if hasattr(self, 'project_root') else str(lib_dir)
                except ValueError:
                    rel_path = str(lib_dir)

                schema_libs.append({
                    "name": lib_dir.name,
                    "path": rel_path,
                    "description": config_lib.get("description", f"Schema library '{lib_dir.name}'") if config_lib else f"Schema library '{lib_dir.name}'",
                    "type": "schemas",
                    "absolute_path": str(lib_dir.absolute())
                })

        return schema_libs
    
    def add_library(self, lib_type: str, name: str, path: str = None, description: str = ""):
        """Add a new library (legacy method - use create_library instead)"""
        return self.create_library(lib_type=lib_type, name=name, description=description)
    
    def create_library(self, lib_type: str, name: str, description: str = "", path: str = None) -> bool:
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
        
        # Create the library directory
        new_lib_path = self.lib_path(lib_type, name)
        try:
            new_lib_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Failed to create library directory: {e}")

        # Add to configuration — no path stored, it is always derived
        new_lib = {
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat()
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
            if archive:
                self._archive_library(lib_type, lib_to_delete)

            lib_path = self.lib_path(lib_type, name)
            if lib_path.exists():
                import shutil
                shutil.rmtree(lib_path)
            
            # Remove from configuration
            libraries.pop(lib_index)
            self._save_config()
            
            return True
            
        except Exception as e:
            raise RuntimeError(f"Failed to delete library: {e}")
    
    def _archive_library(self, lib_type: str, library_config: Dict[str, Any]):
        """Archive a library before deletion"""
        lib_path = self.lib_path(lib_type, library_config["name"])
        if not lib_path.exists():
            return

        archive_dir = self.base_path / "archive" / lib_type
        archive_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{library_config['name']}_{timestamp}"

        try:
            import shutil
            shutil.make_archive(str(archive_dir / archive_name), 'zip',
                                str(lib_path.parent), lib_path.name)
            metadata = {
                "original_name": library_config["name"],
                "lib_type": lib_type,
                "description": library_config.get("description", ""),
                "archived_at": datetime.now().isoformat(),
                "archive_file": f"{archive_name}.zip"
            }
            with open(archive_dir / f"{archive_name}_metadata.json", 'w') as f:
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
            lib_type = metadata.get("lib_type") or metadata.get("type")
            existing_libs = [lib["name"] for lib in self.config["libraries"][lib_type]["libraries"]]
            if restore_name in existing_libs:
                raise ValueError(f"Library '{restore_name}' already exists")
            
            archive_file = metadata_file.parent / metadata["archive_file"]
            restore_path = self.lib_path(lib_type, restore_name)
            import shutil
            shutil.unpack_archive(str(archive_file), str(restore_path.parent))
            self.create_library(
                lib_type=lib_type,
                name=restore_name,
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
