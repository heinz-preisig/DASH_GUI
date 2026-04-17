#!/usr/bin/env python3
"""
Abstract Event System for Multi-Client Support
Provides event handling abstraction for Qt, Web, and other client types
"""

from typing import Dict, Any, List, Callable, Optional, Union
from enum import Enum
from dataclasses import dataclass
import json
from datetime import datetime


class ClientType(Enum):
    """Supported client types"""
    QT = "qt"
    WEB = "web"
    API = "api"


class EventType(Enum):
    """Standardized event types"""
    BRICK_CREATED = "brick_created"
    BRICK_UPDATED = "brick_updated"
    BRICK_LOADED = "brick_loaded"
    BRICK_SAVED = "brick_saved"
    PROPERTY_ADDED = "property_added"
    PROPERTY_REMOVED = "property_removed"
    CONSTRAINT_ADDED = "constraint_added"
    CONSTRAINT_REMOVED = "constraint_removed"
    TARGET_CLASS_SET = "target_class_set"
    ERROR_OCCURRED = "error_occurred"
    DIALOG_REQUESTED = "dialog_requested"
    STATUS_MESSAGE = "status_message"


@dataclass
class Event:
    """Standardized event structure"""
    event_type: EventType
    data: Dict[str, Any]
    session_id: str
    timestamp: datetime
    target_client: Optional[ClientType] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            "event_type": self.event_type.value,
            "data": self.data,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "target_client": self.target_client.value if self.target_client else None
        }
    
    def to_json(self) -> str:
        """Convert event to JSON string"""
        return json.dumps(self.to_dict())


class AbstractEventHandler:
    """Abstract base class for event handlers"""
    
    def handle_event(self, event: Event) -> None:
        """Handle an event - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement handle_event")


class QtEventHandler(AbstractEventHandler):
    """Qt-specific event handler using signals/slots"""
    
    def __init__(self):
        # Qt signals will be connected by the frontend
        self.qt_signals = {}
    
    def connect_signal(self, event_type: EventType, qt_signal):
        """Connect a Qt signal to an event type"""
        self.qt_signals[event_type] = qt_signal
    
    def handle_event(self, event: Event) -> None:
        """Handle event by emitting corresponding Qt signal"""
        if event.event_type in self.qt_signals:
            qt_signal = self.qt_signals[event.event_type]
            # Emit Qt signal with event data
            qt_signal.emit(event.data)
        else:
            print(f"No Qt signal connected for event type: {event.event_type}")


class WebEventHandler(AbstractEventHandler):
    """Web-specific event handler using WebSocket"""
    
    def __init__(self, websocket_manager=None):
        self.websocket_manager = websocket_manager
    
    def handle_event(self, event: Event) -> None:
        """Handle event by sending via WebSocket"""
        if self.websocket_manager:
            # Send event to web client
            message = event.to_json()
            self.websocket_manager.send_to_session(event.session_id, message)
        else:
            print(f"No WebSocket manager available for web event: {event.event_type}")


class APIEventHandler(AbstractEventHandler):
    """API-specific event handler for REST callbacks"""
    
    def __init__(self):
        self.callbacks = {}  # session_id -> callback_url
    
    def register_callback(self, session_id: str, callback_url: str):
        """Register callback URL for API session"""
        self.callbacks[session_id] = callback_url
    
    def handle_event(self, event: Event) -> None:
        """Handle event by sending HTTP callback"""
        if event.session_id in self.callbacks:
            callback_url = self.callbacks[event.session_id]
            # In real implementation, would send HTTP POST
            print(f"API Event: Would POST to {callback_url}: {event.to_json()}")


class EventRouter:
    """Routes events to appropriate handlers based on client type"""
    
    def __init__(self):
        self.handlers: Dict[ClientType, AbstractEventHandler] = {}
        self.global_handlers: List[AbstractEventHandler] = []
    
    def register_handler(self, client_type: ClientType, handler: AbstractEventHandler):
        """Register handler for specific client type"""
        self.handlers[client_type] = handler
    
    def register_global_handler(self, handler: AbstractEventHandler):
        """Register global handler (receives all events)"""
        self.global_handlers.append(handler)
    
    def route_event(self, event: Event) -> None:
        """Route event to appropriate handler(s)"""
        # Route to specific client handler
        if event.target_client and event.target_client in self.handlers:
            self.handlers[event.target_client].handle_event(event)
        
        # Route to all global handlers
        for handler in self.global_handlers:
            handler.handle_event(event)
    
    def create_event(self, event_type: EventType, data: Dict[str, Any], 
                    session_id: str, target_client: Optional[ClientType] = None) -> Event:
        """Create a new event"""
        return Event(
            event_type=event_type,
            data=data,
            session_id=session_id,
            timestamp=datetime.now(),
            target_client=target_client
        )


class MultiClientEventManager:
    """Manages events for multiple client types"""
    
    def __init__(self):
        self.router = EventRouter()
        self.event_history: List[Event] = []
        self.max_history = 1000
        
        # Setup default handlers
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default event handlers"""
        # These will be replaced by actual implementations
        self.router.register_handler(ClientType.QT, QtEventHandler())
        self.router.register_handler(ClientType.WEB, WebEventHandler())
        self.router.register_handler(ClientType.API, APIEventHandler())
    
    def emit_event(self, event_type: EventType, data: Dict[str, Any], 
                   session_id: str, target_client: Optional[ClientType] = None) -> None:
        """Emit an event to all appropriate clients"""
        event = self.router.create_event(event_type, data, session_id, target_client)
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Route event
        self.router.route_event(event)
    
    def get_event_history(self, session_id: Optional[str] = None, 
                         event_type: Optional[EventType] = None) -> List[Event]:
        """Get event history with optional filtering"""
        filtered_events = self.event_history
        
        if session_id:
            filtered_events = [e for e in filtered_events if e.session_id == session_id]
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]
        
        return filtered_events
    
    def register_qt_signals(self, qt_signals: Dict[EventType, Any]):
        """Register Qt signals with the Qt handler"""
        qt_handler = self.router.handlers.get(ClientType.QT)
        if isinstance(qt_handler, QtEventHandler):
            for event_type, signal in qt_signals.items():
                qt_handler.connect_signal(event_type, signal)
    
    def register_websocket_manager(self, websocket_manager):
        """Register WebSocket manager with the web handler"""
        web_handler = self.router.handlers.get(ClientType.WEB)
        if isinstance(web_handler, WebEventHandler):
            web_handler.websocket_manager = websocket_manager
    
    def register_api_callback(self, session_id: str, callback_url: str):
        """Register API callback URL"""
        api_handler = self.router.handlers.get(ClientType.API)
        if isinstance(api_handler, APIEventHandler):
            api_handler.register_callback(session_id, callback_url)


# Convenience functions for creating common events
def create_brick_created_event(brick_data: Dict[str, Any], session_id: str) -> Event:
    """Create a brick created event"""
    return Event(
        event_type=EventType.BRICK_CREATED,
        data=brick_data,
        session_id=session_id,
        timestamp=datetime.now()
    )


def create_brick_updated_event(brick_data: Dict[str, Any], session_id: str) -> Event:
    """Create a brick updated event"""
    return Event(
        event_type=EventType.BRICK_UPDATED,
        data=brick_data,
        session_id=session_id,
        timestamp=datetime.now()
    )


def create_error_event(error_message: str, session_id: str, error_details: Dict[str, Any] = None) -> Event:
    """Create an error event"""
    return Event(
        event_type=EventType.ERROR_OCCURRED,
        data={
            "message": error_message,
            "details": error_details or {}
        },
        session_id=session_id,
        timestamp=datetime.now()
    )


def create_status_event(message: str, session_id: str) -> Event:
    """Create a status message event"""
    return Event(
        event_type=EventType.STATUS_MESSAGE,
        data={"message": message},
        session_id=session_id,
        timestamp=datetime.now()
    )
