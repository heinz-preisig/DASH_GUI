#!/usr/bin/env python3
"""
Step 2: Schema Constructor Package
Combines bricks into complex shapes with daisy-chaining capabilities for HTML GUI generation
"""

__version__ = "2.0.0"
__author__ = "SHACL Brick Generator Team"
__description__ = "Step 2: Schema Construction - Brick composition and daisy-chaining system"

# Import core components
from .core.schema_backend import SchemaBackendAPI, SchemaEventProcessor
from .core.schema_constructor import (
    SchemaConstructor, InterfaceFlowType, SchemaComposition, 
    DaisyChain, InterfaceStep
)

# Import GUI components
from .gui.schema_gui import SchemaGUI

# Convenience functions
def create_schema_system(repository_path: str = "schema_repositories"):
    """Create a complete schema construction system"""
    backend = SchemaBackendAPI(repository_path)
    processor = SchemaEventProcessor(backend)
    return backend, processor

def run_schema_gui(repository_path: str = "schema_repositories"):
    """Run the schema constructor GUI"""
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    gui = SchemaGUI(repository_path)
    gui.show()
    return app.exec()

# Export main classes
__all__ = [
    # Core classes
    "SchemaBackendAPI",
    "SchemaEventProcessor", 
    "SchemaConstructor",
    "InterfaceFlowType",
    "SchemaComposition",
    "DaisyChain",
    "InterfaceStep",
    
    # GUI classes
    "SchemaGUI",
    
    # Convenience functions
    "create_schema_system",
    "run_schema_gui"
]
