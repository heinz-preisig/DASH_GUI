"""
Backend manager for SHACL brick operations
"""

from PyQt6.QtCore import QObject, pyqtSignal
from shacl_brick_app.core.brick_backend import BrickBackendAPI, BrickEventProcessor

class BrickManager(QObject):
    """Manages backend communication for brick operations"""
    
    # Signals
    brick_created = pyqtSignal(dict)
    brick_updated = pyqtSignal(dict)
    brick_deleted = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.backend = BrickBackendAPI("brick_repositories")
        self.processor = BrickEventProcessor(self.backend)
        
        # Ensure active library exists
        self._ensure_active_library()
    
    def _ensure_active_library(self):
        """Ensure we have an active library"""
        result = self.processor.process_event({"event": "get_repository_info"})
        if result["status"] == "success" and not result["data"]["active_library"]:
            # Try to set default library
            libraries_result = self.processor.process_event({"event": "get_libraries"})
            if libraries_result["status"] == "success" and libraries_result["data"]["libraries"]:
                default_lib = libraries_result["data"]["libraries"][0]["name"]
                set_result = self.processor.process_event({
                    "event": "set_active_library",
                    "library_name": default_lib
                })
                if set_result["status"] != "success":
                    print(f"Warning: Could not set active library {default_lib}: {set_result['message']}")
            else:
                print("Warning: No libraries available, creating one...")
                create_result = self.processor.process_event({
                    "event": "create_library",
                    "name": "default",
                    "description": "Default library for guided brick creation",
                    "author": "Guided GUI"
                })
                if create_result["status"] == "success":
                    set_result = self.processor.process_event({
                        "event": "set_active_library",
                        "library_name": "default"
                    })
                    if set_result["status"] != "success":
                        print(f"Warning: Could not set new active library: {set_result['message']}")
    
    def create_brick(self, step1, step2, step3, custom_name=None):
        """Create brick based on guided selections"""
        return self.processor.process_event({
            "event": "create_guided_brick",
            "step1": step1,
            "step2": step2, 
            "step3": step3,
            "custom_name": custom_name
        })
    
    def get_bricks(self):
        """Get all bricks from active library"""
        result = self.processor.process_event({"event": "get_library_bricks"})
        if result["status"] == "success":
            self.brick_created.emit(result["data"])
        return result
    
    def delete_brick(self, brick_id):
        """Delete a brick"""
        result = self.processor.process_event({
            "event": "delete_brick",
            "brick_id": brick_id
        })
        
        if result["status"] == "success":
            self.brick_deleted.emit(brick_id)
        return result
    
    def update_brick(self, brick_id, brick_data):
        """Update an existing brick"""
        result = self.processor.process_event({
            "event": "update_brick",
            "brick_id": brick_id,
            "brick_data": brick_data
        })
        
        if result["status"] == "success":
            self.brick_updated.emit(result["data"])
        return result
