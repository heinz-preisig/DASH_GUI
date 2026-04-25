"""
Schema App v2 - Core Module
Clean, modular schema construction system following brick_app_v2 architecture
"""

from .schema_core import Schema, SchemaCore
from .flow_engine import FlowConfig, FlowStep, FlowEngine
from .brick_integration import BrickIntegration
from .schema_helper import SchemaHelper
from .shacl_export import SHACLExporter
from .multi_tenant_backend import MultiTenantBackend
from .session_manager import SessionManager, SchemaBackendSession
from .abstract_events import (
    EventType, ClientType, Event, MultiClientEventManager,
    create_schema_created_event, create_schema_updated_event,
    create_component_added_event, create_error_event, create_status_event
)

__all__ = [
    'Schema', 'SchemaCore',
    'FlowConfig', 'FlowStep', 'FlowEngine',
    'BrickIntegration', 'SchemaHelper', 'SHACLExporter',
    'MultiTenantBackend', 'SessionManager', 'SchemaBackendSession',
    'EventType', 'ClientType', 'Event', 'MultiClientEventManager',
    'create_schema_created_event', 'create_schema_updated_event',
    'create_component_added_event', 'create_error_event', 'create_status_event'
]
