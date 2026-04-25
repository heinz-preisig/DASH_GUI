#!/usr/bin/env python3
"""
Session Management for Schema App Multi-Tenant Backend
Handles multiple client sessions (Qt, Web, etc.) with isolated state
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class SessionInfo:
    """Session information and metadata"""
    session_id: str
    client_type: str  # "qt", "web", "api"
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    user_info: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


class SchemaBackendSession:
    """Isolated backend session for a single client"""
    
    def __init__(self, session_id: str, client_type: str, schema_repository_path: str = None, 
                 brick_repository_path: str = None):
        self.session_id = session_id
        self.client_type = client_type
        self.created_at = datetime.now()
        
        # Import core components
        from .schema_core import SchemaCore
        from .flow_engine import FlowEngine
        from .brick_integration import BrickIntegration
        
        # Create isolated backend instances for this session
        self.schema_core = SchemaCore(schema_repository_path, use_shared_libraries=True)
        self.flow_engine = FlowEngine()
        self.brick_integration = BrickIntegration(brick_repository_path)
        
        # Session-specific state
        self.current_schema = None
        self.session_data = {}
        
        # Event handlers for this session
        self.event_handlers = {
            'schema_created': [],
            'schema_updated': [],
            'schema_loaded': [],
            'schema_saved': [],
            'schema_deleted': [],
            'component_added': [],
            'component_removed': [],
            'root_brick_set': [],
            'flow_updated': [],
            'library_changed': [],
            'error_occurred': [],
            'dialog_requested': []
        }
    
    def register_event_handler(self, event_type: str, handler):
        """Register event handler for this session"""
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
    
    def _emit_event(self, event_type: str, data: Any):
        """Emit event to session handlers"""
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                print(f"Session {self.session_id} event handler error: {e}")
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get session information"""
        return {
            "session_id": self.session_id,
            "client_type": self.client_type,
            "created_at": self.created_at.isoformat(),
            "current_schema_id": self.current_schema.schema_id if self.current_schema else None,
            "is_active": True
        }
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.created_at = datetime.now()


class SessionManager:
    """Manages multiple backend sessions for different clients"""
    
    def __init__(self, schema_repository_path: str = None, brick_repository_path: str = None):
        self.schema_repository_path = schema_repository_path
        self.brick_repository_path = brick_repository_path
        self.sessions: Dict[str, SchemaBackendSession] = {}
        self.session_info: Dict[str, SessionInfo] = {}
        
        # Special session for Qt frontend (backward compatibility)
        self.qt_session_id = self.create_session("qt", user_info={"client": "PyQt GUI"})
    
    def create_session(self, client_type: str, user_info: Dict[str, Any] = None) -> str:
        """Create a new backend session"""
        session_id = str(uuid.uuid4())
        
        # Create session info
        info = SessionInfo(
            session_id=session_id,
            client_type=client_type,
            user_info=user_info or {}
        )
        self.session_info[session_id] = info
        
        # Create backend session
        session = SchemaBackendSession(
            session_id, 
            client_type, 
            self.schema_repository_path,
            self.brick_repository_path
        )
        self.sessions[session_id] = session
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SchemaBackendSession]:
        """Get backend session by ID"""
        if session_id in self.sessions:
            # Update activity
            self.sessions[session_id].update_activity()
            self.session_info[session_id].last_activity = datetime.now()
            return self.sessions[session_id]
        return None
    
    def get_qt_session(self) -> SchemaBackendSession:
        """Get the special Qt session for backward compatibility"""
        return self.get_session(self.qt_session_id)
    
    def remove_session(self, session_id: str) -> bool:
        """Remove a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.session_info:
            del self.session_info[session_id]
        return True
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get information about all active sessions"""
        sessions = []
        for session_id, info in self.session_info.items():
            if session_id in self.sessions:
                session = self.sessions[session_id]
                sessions.append(session.get_session_info())
        return sessions
    
    def cleanup_inactive_sessions(self, max_age_hours: int = 24) -> int:
        """Remove inactive sessions older than max_age_hours"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        removed_count = 0
        
        sessions_to_remove = []
        for session_id, info in self.session_info.items():
            if info.last_activity.timestamp() < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            if session_id != self.qt_session_id:  # Don't remove Qt session
                self.remove_session(session_id)
                removed_count += 1
        
        return removed_count
    
    def broadcast_event(self, event_type: str, data: Any, exclude_session: str = None):
        """Broadcast event to all sessions (except excluded one)"""
        for session_id, session in self.sessions.items():
            if session_id != exclude_session:
                session._emit_event(event_type, data)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about sessions"""
        total_sessions = len(self.sessions)
        qt_sessions = 1 if self.qt_session_id in self.sessions else 0
        web_sessions = total_sessions - qt_sessions
        
        return {
            "total_sessions": total_sessions,
            "qt_sessions": qt_sessions,
            "web_sessions": web_sessions,
            "active_sessions": len([s for s in self.session_info.values() if s.is_active])
        }
