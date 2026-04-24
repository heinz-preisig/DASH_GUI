"""
SHACL Brick Generator - Step 1 of Three-Step SHACL System

A comprehensive SHACL brick generation system with:
- Full SHACL specification support
- Multiple brick libraries with repository system
- Clean backend API for frontend integration
- PyQt6 GUI for visual brick management
"""

__version__ = "1.0.0"
__author__ = "SHACL System Developer"
__description__ = "SHACL Brick Generator - Step 1 of Three-Step SHACL System"

# Import main components for easy access
from .core.brick_generator import (
    SHACLBrick,
    BrickLibrary,
    BrickRepository,
    SHACLBrickGenerator,
    SHACLObjectType,
    SHACLConstraint,
    SHACLTarget
)

from .core.brick_backend import (
    BrickBackendAPI,
    BrickEventProcessor
)

from .gui.brick_gui import BrickGUI

# Schema components moved to separate schema_app_v2 module

__all__ = [
    # Core classes
    "SHACLBrick",
    "BrickLibrary", 
    "BrickRepository",
    "SHACLBrickGenerator",
    "SHACLObjectType",
    "SHACLConstraint",
    "SHACLTarget",
    
    # Backend API
    "BrickBackendAPI",
    "BrickEventProcessor",
    
    # GUI
    "BrickGUI",
    
    # Schema Backend API
    "SchemaBackendAPI",
    "SchemaEventProcessor",
    
    # Schema Core
    "SchemaConstructor",
    "InterfaceFlowType",
    "SchemaComposition",
    "DaisyChain",
    "InterfaceStep",
    
    # Schema GUI
    "SchemaGUI",
    
    # Convenience functions
    "create_brick_system",
    "run_gui",
    "create_schema_system",
    "run_schema_gui"
]

def create_brick_system(repository_path=None):
    """Create a complete brick system with backend and event processor"""
    backend = BrickBackendAPI(repository_path)
    processor = BrickEventProcessor(backend)
    return backend, processor

def run_gui(repository_path=None):
    """Run the PyQt6 GUI for brick management"""
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    gui = BrickGUI(repository_path)
    gui.show()
    return app.exec()

def create_schema_system(repository_path=None):
    """Create a complete schema system with backend and event processor"""
    backend = SchemaBackendAPI(repository_path)
    processor = SchemaEventProcessor(backend)
    return backend, processor

def run_schema_gui(repository_path=None):
    """Run the PyQt6 GUI for schema construction"""
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    gui = SchemaGUI(repository_path)
    gui.show()
    return app.exec()
