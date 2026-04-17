#!/usr/bin/env python3
"""
Shared Library Manager
Unified library management for brick_app_v2 and schema_app_v2
"""

import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path


class SharedLibraryManager:
    """Manages shared libraries for both brick and schema applications"""
    
    def __init__(self, base_path: str = "shared_libraries"):
        self.base_path = Path(base_path)
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
        """Get the path to a brick library parent directory"""
        # Return the parent directory of libraries so BrickCore can append library_name/bricks
        return self.config["libraries"]["bricks"]["default_path"]
    
    def get_schema_library_path(self, library_name: str = "default") -> str:
        """Get the path to a schema library parent directory"""
        # Return the parent directory of libraries so SchemaCore can append library_name/schemas
        return self.config["libraries"]["schemas"]["default_path"]
    
    def get_brick_libraries(self) -> List[Dict[str, Any]]:
        """Get all brick libraries"""
        return self.config["libraries"]["bricks"]["libraries"]
    
    def get_schema_libraries(self) -> List[Dict[str, Any]]:
        """Get all schema libraries"""
        return self.config["libraries"]["schemas"]["libraries"]
    
    def add_library(self, lib_type: str, name: str, path: str, description: str = ""):
        """Add a new library"""
        if lib_type not in ["bricks", "schemas"]:
            raise ValueError("Library type must be 'bricks' or 'schemas'")
        
        new_lib = {
            "name": name,
            "path": path,
            "description": description,
            "type": lib_type
        }
        
        self.config["libraries"][lib_type]["libraries"].append(new_lib)
        self._save_config()
    
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
