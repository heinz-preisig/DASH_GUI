#!/usr/bin/env python3
"""
Multi-Tenant Backend Architecture for Schema App
Provides isolated backend instances for multiple clients (Qt, Web, API)
"""

from typing import Dict, Any, Optional, List
from .session_manager import SessionManager, SchemaBackendSession
from .abstract_events import (
    MultiClientEventManager, EventType, ClientType, Event,
    create_schema_created_event, create_schema_updated_event, 
    create_component_added_event, create_error_event, create_status_event
)


class MultiTenantBackend:
    """Main multi-tenant backend coordinator for Schema App"""
    
    def __init__(self, schema_repository_path: str = None, brick_repository_path: str = None):
        self.schema_repository_path = schema_repository_path
        self.brick_repository_path = brick_repository_path
        
        # Session management
        self.session_manager = SessionManager(schema_repository_path, brick_repository_path)
        
        # Event management
        self.event_manager = MultiClientEventManager()
        
        # Setup event forwarding
        self._setup_event_forwarding()
    
    def _setup_event_forwarding(self):
        """Setup event forwarding from sessions to event manager"""
        # This will be called when sessions are created
        pass
    
    def create_session(self, client_type: str, user_info: Dict[str, Any] = None) -> str:
        """Create a new backend session"""
        session_id = self.session_manager.create_session(client_type, user_info)
        session = self.session_manager.get_session(session_id)
        
        # Setup event forwarding for this session
        self._setup_session_events(session)
        
        return session_id
    
    def _setup_session_events(self, session: SchemaBackendSession):
        """Setup event forwarding for a specific session"""
        # Register event handlers that forward to the multi-client event manager
        
        def schema_created_handler(schema_data):
            self.event_manager.emit_event(
                EventType.SCHEMA_CREATED, 
                schema_data, 
                session.session_id
            )
        
        def schema_updated_handler(schema_data):
            self.event_manager.emit_event(
                EventType.SCHEMA_UPDATED, 
                schema_data, 
                session.session_id
            )
        
        def schema_saved_handler(schema_data):
            self.event_manager.emit_event(
                EventType.SCHEMA_SAVED, 
                schema_data, 
                session.session_id
            )
        
        def schema_deleted_handler(schema_id):
            self.event_manager.emit_event(
                EventType.SCHEMA_DELETED, 
                {"schema_id": schema_id}, 
                session.session_id
            )
        
        def component_added_handler(component_data):
            self.event_manager.emit_event(
                EventType.COMPONENT_ADDED, 
                component_data, 
                session.session_id
            )
        
        def component_removed_handler(component_id):
            self.event_manager.emit_event(
                EventType.COMPONENT_REMOVED, 
                {"component_id": component_id}, 
                session.session_id
            )
        
        def root_brick_set_handler(brick_id):
            self.event_manager.emit_event(
                EventType.ROOT_BRICK_SET, 
                {"brick_id": brick_id}, 
                session.session_id
            )
        
        def flow_updated_handler(flow_data):
            self.event_manager.emit_event(
                EventType.FLOW_UPDATED, 
                flow_data, 
                session.session_id
            )
        
        def library_changed_handler(library_name):
            self.event_manager.emit_event(
                EventType.LIBRARY_CHANGED, 
                {"library_name": library_name}, 
                session.session_id
            )
        
        def error_occurred_handler(error_message):
            self.event_manager.emit_event(
                EventType.ERROR_OCCURRED, 
                {"message": error_message}, 
                session.session_id
            )
        
        def dialog_requested_handler(dialog_type):
            self.event_manager.emit_event(
                EventType.DIALOG_REQUESTED, 
                {"dialog_type": dialog_type}, 
                session.session_id
            )
        
        # Register handlers with session
        session.register_event_handler('schema_created', schema_created_handler)
        session.register_event_handler('schema_updated', schema_updated_handler)
        session.register_event_handler('schema_saved', schema_saved_handler)
        session.register_event_handler('schema_deleted', schema_deleted_handler)
        session.register_event_handler('component_added', component_added_handler)
        session.register_event_handler('component_removed', component_removed_handler)
        session.register_event_handler('root_brick_set', root_brick_set_handler)
        session.register_event_handler('flow_updated', flow_updated_handler)
        session.register_event_handler('library_changed', library_changed_handler)
        session.register_event_handler('error_occurred', error_occurred_handler)
        session.register_event_handler('dialog_requested', dialog_requested_handler)
    
    def get_session(self, session_id: str) -> Optional[SchemaBackendSession]:
        """Get backend session by ID"""
        return self.session_manager.get_session(session_id)
    
    def get_qt_session(self) -> Optional[SchemaBackendSession]:
        """Get the Qt session for backward compatibility"""
        return self.session_manager.get_qt_session()
    
    def remove_session(self, session_id: str) -> bool:
        """Remove a session"""
        return self.session_manager.remove_session(session_id)
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get information about all active sessions"""
        return self.session_manager.get_all_sessions()
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        return self.session_manager.get_session_stats()
    
    def cleanup_inactive_sessions(self, max_age_hours: int = 24) -> int:
        """Cleanup inactive sessions"""
        return self.session_manager.cleanup_inactive_sessions(max_age_hours)
    
    # Qt-specific convenience methods for backward compatibility
    def qt_create_new_schema(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create new schema in Qt session (backward compatibility)"""
        qt_session = self.get_qt_session()
        if qt_session:
            schema = qt_session.schema_core.create_schema(name, description)
            return schema.to_dict()
        return {}
    
    def qt_get_current_schema(self) -> Dict[str, Any]:
        """Get current schema from Qt session (backward compatibility)"""
        qt_session = self.get_qt_session()
        if qt_session and qt_session.current_schema:
            return qt_session.current_schema.to_dict()
        return {}
    
    def qt_save_schema(self) -> tuple[bool, str]:
        """Save schema in Qt session (backward compatibility)"""
        qt_session = self.get_qt_session()
        if qt_session and qt_session.current_schema:
            try:
                qt_session.schema_core.save_schema(qt_session.current_schema.schema_id)
                qt_session._emit_event('schema_saved', qt_session.current_schema.to_dict())
                return True, "Schema saved successfully"
            except Exception as e:
                return False, f"Error saving schema: {e}"
        return False, "No current schema to save"
    
    def qt_load_schema(self, schema_id: str) -> Optional[Dict[str, Any]]:
        """Load schema in Qt session (backward compatibility)"""
        qt_session = self.get_qt_session()
        if qt_session:
            schema = qt_session.schema_core.load_schema(schema_id)
            if schema:
                qt_session.current_schema = schema
                qt_session._emit_event('schema_loaded', schema.to_dict())
                return schema.to_dict()
        return None
    
    def qt_add_component(self, brick_id: str) -> bool:
        """Add component to current schema in Qt session (backward compatibility)"""
        qt_session = self.get_qt_session()
        if qt_session and qt_session.current_schema:
            if brick_id not in qt_session.current_schema.component_brick_ids:
                qt_session.current_schema.component_brick_ids.append(brick_id)
                qt_session.current_schema.update_timestamp()
                qt_session._emit_event('component_added', {"brick_id": brick_id})
                return True
        return False
    
    def qt_remove_component(self, brick_id: str) -> bool:
        """Remove component from current schema in Qt session (backward compatibility)"""
        qt_session = self.get_qt_session()
        if qt_session and qt_session.current_schema:
            if brick_id in qt_session.current_schema.component_brick_ids:
                qt_session.current_schema.component_brick_ids.remove(brick_id)
                qt_session.current_schema.update_timestamp()
                qt_session._emit_event('component_removed', {"brick_id": brick_id})
                return True
        return False
    
    def qt_set_root_brick(self, brick_id: str) -> bool:
        """Set root brick in Qt session (backward compatibility)"""
        qt_session = self.get_qt_session()
        if qt_session and qt_session.current_schema:
            qt_session.current_schema.root_brick_id = brick_id
            qt_session.current_schema.update_timestamp()
            qt_session._emit_event('root_brick_set', {"brick_id": brick_id})
            return True
        return False
    
    # Event management methods
    def register_qt_signals(self, qt_signals: Dict[EventType, Any]):
        """Register Qt signals for event handling"""
        self.event_manager.register_qt_signals(qt_signals)
    
    def register_websocket_manager(self, websocket_manager):
        """Register WebSocket manager for web events"""
        self.event_manager.register_websocket_manager(websocket_manager)
    
    def register_api_callback(self, session_id: str, callback_url: str):
        """Register API callback URL"""
        self.event_manager.register_api_callback(session_id, callback_url)
    
    def get_event_history(self, session_id: Optional[str] = None, 
                         event_type: Optional[EventType] = None) -> List[Event]:
        """Get event history"""
        return self.event_manager.get_event_history(session_id, event_type)
    
    # Repository operations (shared across sessions)
    def get_schemas(self, library_name: str = None) -> List[Dict[str, Any]]:
        """Get schemas (shared)"""
        qt_session = self.get_qt_session()
        if qt_session:
            schemas = qt_session.schema_core.get_all_schemas(library_name)
            return [schema.to_dict() for schema in schemas]
        return []
    
    def get_schema_libraries(self) -> List[str]:
        """Get schema libraries (shared)"""
        qt_session = self.get_qt_session()
        if qt_session:
            return qt_session.schema_core.get_libraries()
        return []
    
    def get_available_bricks(self) -> List[Dict[str, Any]]:
        """Get available bricks from brick integration (shared)"""
        qt_session = self.get_qt_session()
        if qt_session:
            bricks = qt_session.brick_integration.get_all_bricks()
            return [brick.to_dict() if hasattr(brick, 'to_dict') else brick for brick in bricks]
        return []
    
    # Utility methods
    def broadcast_message(self, message: str, exclude_session: str = None):
        """Broadcast a message to all sessions"""
        for session_id, session in self.session_manager.sessions.items():
            if session_id != exclude_session:
                self.event_manager.emit_event(
                    EventType.STATUS_MESSAGE,
                    {"message": message},
                    session_id
                )
    
    def get_session_for_client_type(self, client_type: str) -> Optional[SchemaBackendSession]:
        """Get first session for a specific client type"""
        for session_id, session in self.session_manager.sessions.items():
            if session.client_type == client_type:
                return session
        return None
    
    def shutdown(self):
        """Shutdown the multi-tenant backend"""
        # Cleanup all sessions
        session_ids = list(self.session_manager.sessions.keys())
        for session_id in session_ids:
            self.remove_session(session_id)
        
        print("Multi-tenant backend shutdown complete")
