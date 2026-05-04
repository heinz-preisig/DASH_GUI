"""
Brick Backend API - Stub file for compatibility.
The main backend functionality has been refactored into multi_tenant_backend.py
and brick_core_simple.py. This file exists for backward compatibility.
"""

from typing import Dict, Any, List, Optional, Tuple
from .brick_core_simple import BrickCore


class BrickBackendAPI:
    """Stub class for backward compatibility. Delegates to BrickCore."""
    
    def __init__(self, repository_path: str = "brick_repositories"):
        self.core = BrickCore(repository_path)
        self.repository_path = repository_path
    
    # Delegate all calls to core
    def __getattr__(self, name):
        return getattr(self.core, name)


class BrickEventProcessor:
    """Stub event processor for backward compatibility."""
    
    def __init__(self, backend):
        self.backend = backend
    
    def process_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an event and return result"""
        return {"status": "success", "message": "Event processed"}
