"""
Schema App v2 - Clean, Modular Schema Construction System
Following brick_app_v2 architecture with flow features and UI file support
"""

from .core import SchemaCore, Schema, FlowEngine, FlowConfig, BrickIntegration
from .core.shacl_export import SHACLExporter

# Qt GUI is optional (not needed for web-only deployment)
try:
    from .interfaces.qt import SchemaGUI
except ImportError:
    SchemaGUI = None

__version__ = "2.0.0"
__description__ = "Clean, modular schema construction system"

__all__ = [
    # Core components
    'SchemaCore', 'Schema', 'FlowEngine', 'FlowConfig', 'BrickIntegration',
    
    # Interfaces (Qt optional)
    'SchemaGUI',
    
    # Export
    'SHACLExporter'
]
