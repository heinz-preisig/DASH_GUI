#!/usr/bin/env python3
"""
Multi-Tenant Backend Architecture
Provides isolated backend instances for multiple clients (Qt, Web, API)
"""

from typing import Dict, Any, Optional, List
from .session_manager import SessionManager, BackendSession
from .abstract_events import (
    MultiClientEventManager, EventType, ClientType, Event,
    create_brick_created_event, create_brick_updated_event, 
    create_error_event, create_status_event
)


class MultiTenantBackend:
    """Main multi-tenant backend coordinator"""
    
    def __init__(self, repository_path: str = "brick_repositories"):
        self.repository_path = repository_path
        
        # Session management
        self.session_manager = SessionManager(repository_path)
        
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
    
    def _setup_session_events(self, session: BackendSession):
        """Setup event forwarding for a specific session"""
        # Register event handlers that forward to the multi-client event manager
        
        def brick_created_handler(brick_data):
            self.event_manager.emit_event(
                EventType.BRICK_CREATED, 
                brick_data, 
                session.session_id
            )
        
        def brick_updated_handler(brick_data):
            self.event_manager.emit_event(
                EventType.BRICK_UPDATED, 
                brick_data, 
                session.session_id
            )
        
        def brick_saved_handler(brick_data):
            self.event_manager.emit_event(
                EventType.BRICK_SAVED, 
                brick_data, 
                session.session_id
            )
        
        def property_added_handler(prop_name, prop_data):
            self.event_manager.emit_event(
                EventType.PROPERTY_ADDED, 
                {"property_name": prop_name, "property_data": prop_data}, 
                session.session_id
            )
        
        def property_removed_handler(prop_name):
            self.event_manager.emit_event(
                EventType.PROPERTY_REMOVED, 
                {"property_name": prop_name}, 
                session.session_id
            )
        
        def constraint_added_handler(prop_name, constraint_data):
            self.event_manager.emit_event(
                EventType.CONSTRAINT_ADDED, 
                {"property_name": prop_name, "constraint_data": constraint_data}, 
                session.session_id
            )
        
        def constraint_removed_handler(prop_name):
            self.event_manager.emit_event(
                EventType.CONSTRAINT_REMOVED, 
                {"property_name": prop_name}, 
                session.session_id
            )
        
        def target_class_set_handler(class_uri):
            self.event_manager.emit_event(
                EventType.TARGET_CLASS_SET, 
                {"class_uri": class_uri}, 
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
        session.register_event_handler('brick_created', brick_created_handler)
        session.register_event_handler('brick_updated', brick_updated_handler)
        session.register_event_handler('brick_saved', brick_saved_handler)
        session.register_event_handler('property_added', property_added_handler)
        session.register_event_handler('property_removed', property_removed_handler)
        session.register_event_handler('constraint_added', constraint_added_handler)
        session.register_event_handler('constraint_removed', constraint_removed_handler)
        session.register_event_handler('target_class_set', target_class_set_handler)
        session.register_event_handler('error_occurred', error_occurred_handler)
        session.register_event_handler('dialog_requested', dialog_requested_handler)
    
    def get_session(self, session_id: str) -> Optional[BackendSession]:
        """Get backend session by ID"""
        return self.session_manager.get_session(session_id)
    
    def get_qt_session(self) -> Optional[BackendSession]:
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
    def qt_create_new_brick(self, brick_type: str = "NodeShape") -> Dict[str, Any]:
        """Create new brick in Qt session (backward compatibility)"""
        qt_session = self.get_qt_session()
        if qt_session:
            return qt_session.editor_backend.create_new_brick(brick_type)
        return {}
    
    def qt_get_current_brick(self) -> Dict[str, Any]:
        """Get current brick from Qt session (backward compatibility)"""
        qt_session = self.get_qt_session()
        if qt_session:
            return qt_session.editor_backend.get_current_brick()
        return {}
    
    def qt_save_brick(self, brick_data: Dict[str, Any]) -> tuple[bool, str]:
        """Save brick in Qt session (backward compatibility)"""
        qt_session = self.get_qt_session()
        if qt_session:
            return qt_session.editor_backend.save_brick(brick_data)
        return False, "No Qt session available"
    
    def qt_load_brick(self, brick_id: str) -> Optional[Dict[str, Any]]:
        """Load brick in Qt session (backward compatibility)"""
        qt_session = self.get_qt_session()
        if qt_session:
            return qt_session.editor_backend.load_brick(brick_id)
        return None
    
    def qt_add_property(self, property_data: Dict[str, Any]) -> bool:
        """Add property in Qt session (backward compatibility)"""
        qt_session = self.get_qt_session()
        if qt_session:
            return qt_session.editor_backend.add_property_to_current_brick(property_data)
        return False
    
    def qt_remove_property(self, prop_name: str) -> bool:
        """Remove property in Qt session (backward compatibility)"""
        qt_session = self.get_qt_session()
        if qt_session:
            return qt_session.editor_backend.remove_property_from_current_brick(prop_name)
        return False
    
    def qt_set_target_class(self, class_uri: str) -> bool:
        """Set target class in Qt session (backward compatibility)"""
        qt_session = self.get_qt_session()
        if qt_session:
            qt_session.editor_backend.set_target_class(class_uri)
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
    def get_repository_info(self) -> Dict[str, Any]:
        """Get repository information (shared)"""
        qt_session = self.get_qt_session()
        if qt_session:
            return qt_session.brick_api.get_repository_info()
        return {"status": "error", "message": "No session available"}
    
    def get_brick_libraries(self) -> Dict[str, Any]:
        """Get brick libraries (shared)"""
        qt_session = self.get_qt_session()
        if qt_session:
            return qt_session.brick_api.get_brick_libraries()
        return {"status": "error", "message": "No session available"}
    
    def get_all_bricks(self) -> Dict[str, Any]:
        """Get all bricks (shared)"""
        qt_session = self.get_qt_session()
        if qt_session:
            return qt_session.brick_api.get_all_bricks()
        return {"status": "error", "message": "No session available"}
    
    def get_library_bricks(self, library_name: str) -> Dict[str, Any]:
        """Get bricks from specific library (shared)"""
        qt_session = self.get_qt_session()
        if qt_session:
            return qt_session.brick_api.get_library_bricks(library_name)
        return {"status": "error", "message": "No session available"}
    
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
    
    def get_session_for_client_type(self, client_type: str) -> Optional[BackendSession]:
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
