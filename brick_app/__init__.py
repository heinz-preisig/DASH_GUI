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

    # Convenience functions
    "create_brick_system",
]

def create_brick_system(repository_path=None):
    """Create a complete brick system with backend and event processor"""
    backend = BrickBackendAPI(repository_path)
    processor = BrickEventProcessor(backend)
    return backend, processor
