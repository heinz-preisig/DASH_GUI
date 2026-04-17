#!/usr/bin/env python3
"""
Session Management for Multi-Tenant Backend
Handles multiple client sessions (Qt, Web, etc.) with isolated state
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from .brick_backend import BrickBackendAPI
from .editor_backend import BrickEditorBackend


@dataclass
class SessionInfo:
    """Session information and metadata"""
    session_id: str
    client_type: str  # "qt", "web", "api"
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    user_info: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


class BackendSession:
    """Isolated backend session for a single client"""
    
    def __init__(self, session_id: str, client_type: str, repository_path: str = "brick_repositories"):
        self.session_id = session_id
        self.client_type = client_type
        self.created_at = datetime.now()
        
        # Create isolated backend instances for this session
        self.brick_api = BrickBackendAPI(repository_path)
        self.editor_backend = BrickEditorBackend(self.brick_api)
        
        # Session-specific state
        self.current_brick = None
        self.session_data = {}
        
        # Event handlers for this session
        self.event_handlers = {
            'brick_created': [],
            'brick_updated': [],
            'brick_loaded': [],
            'brick_saved': [],
            'property_added': [],
            'property_removed': [],
            'constraint_added': [],
            'constraint_removed': [],
            'target_class_set': [],
            'error_occurred': [],
            'dialog_requested': []
        }
        
        # Register session-specific event handlers
        self._setup_session_events()
    
    def _setup_session_events(self):
        """Setup event handling for this session"""
        # Forward backend events to session handlers
        for event_type in self.event_handlers.keys():
            self.editor_backend.register_event_handler(event_type, 
                lambda *args, et=event_type: self._handle_backend_event(et, *args))
    
    def _handle_backend_event(self, event_type: str, *args, **kwargs):
        """Handle backend events and forward to session handlers"""
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                print(f"Session {self.session_id} event handler error: {e}")
    
    def register_event_handler(self, event_type: str, handler):
        """Register event handler for this session"""
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get session information"""
        return {
            "session_id": self.session_id,
            "client_type": self.client_type,
            "created_at": self.created_at.isoformat(),
            "current_brick_id": self.current_brick.get("brick_id") if self.current_brick else None,
            "is_active": True
        }
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.created_at = datetime.now()


class SessionManager:
    """Manages multiple backend sessions for different clients"""
    
    def __init__(self, repository_path: str = "brick_repositories"):
        self.repository_path = repository_path
        self.sessions: Dict[str, BackendSession] = {}
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
        session = BackendSession(session_id, client_type, self.repository_path)
        self.sessions[session_id] = session
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[BackendSession]:
        """Get backend session by ID"""
        if session_id in self.sessions:
            # Update activity
            self.sessions[session_id].update_activity()
            self.session_info[session_id].last_activity = datetime.now()
            return self.sessions[session_id]
        return None
    
    def get_qt_session(self) -> BackendSession:
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
                session._handle_backend_event(event_type, data)
    
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
