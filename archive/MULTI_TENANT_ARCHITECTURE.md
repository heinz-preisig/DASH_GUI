# Multi-Tenant Backend Architecture

## Overview

The SHACL Brick Generator has been enhanced with a multi-tenant backend architecture to support multiple client types simultaneously:
- **PyQt Desktop Client** (existing)
- **Web Browser Client** (new)
- **API Client** (future)

## Architecture Components

### 1. Session Management (`session_manager.py`)

#### BackendSession
- **Purpose**: Isolated backend instance for a single client
- **Features**:
  - Independent `BrickBackendAPI` and `BrickEditorBackend` instances
  - Session-specific state and event handlers
  - Automatic activity tracking

#### SessionManager
- **Purpose**: Manages multiple client sessions
- **Features**:
  - Creates and destroys sessions
  - Automatic cleanup of inactive sessions
  - Special Qt session for backward compatibility

### 2. Abstract Event System (`abstract_events.py`)

#### Event Types
```python
class EventType(Enum):
    BRICK_CREATED = "brick_created"
    BRICK_UPDATED = "brick_updated"
    BRICK_SAVED = "brick_saved"
    PROPERTY_ADDED = "property_added"
    PROPERTY_REMOVED = "property_removed"
    CONSTRAINT_ADDED = "constraint_added"
    CONSTRAINT_REMOVED = "constraint_removed"
    TARGET_CLASS_SET = "target_class_set"
    ERROR_OCCURRED = "error_occurred"
    DIALOG_REQUESTED = "dialog_requested"
    STATUS_MESSAGE = "status_message"
```

#### Client Handlers
- **QtEventHandler**: Routes events to Qt signals/slots
- **WebEventHandler**: Routes events to WebSocket connections
- **APIEventHandler**: Routes events to HTTP callbacks

#### EventRouter
- **Purpose**: Routes events to appropriate handlers based on client type
- **Features**:
  - Client-specific routing
  - Global event broadcasting
  - Event history tracking

### 3. Multi-Tenant Backend (`multi_tenant_backend.py`)

#### MultiTenantBackend
- **Purpose**: Central coordinator for all client sessions
- **Features**:
  - Session lifecycle management
  - Event forwarding between sessions
  - Qt compatibility methods
  - Repository operation sharing

## API Endpoints

### Session Management
- `POST /api/session` - Create new session
- `GET /api/session/<session_id>` - Get session info
- `DELETE /api/session/<session_id>` - Delete session
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/stats` - Get session statistics

### Repository Operations
- `GET /api/repository` - Get repository info
- `GET /api/libraries` - Get all libraries
- `GET /api/libraries/<library_name>/bricks` - Get library bricks
- `GET /api/bricks` - Get all bricks

### Brick Operations (Session-Specific)
- `POST /api/session/<session_id>/brick` - Create new brick
- `GET /api/session/<session_id>/brick` - Get current brick
- `PUT /api/session/<session_id>/brick` - Update current brick
- `POST /api/session/<session_id>/brick/save` - Save current brick
- `POST /api/session/<session_id>/brick/load/<brick_id>` - Load brick

### Property Operations
- `POST /api/session/<session_id>/brick/properties` - Add property
- `DELETE /api/session/<session_id>/brick/properties/<property_name>` - Remove property

### Ontology Operations
- `GET /api/ontologies` - Get available ontologies
- `GET /api/ontologies/<ontology_name>/classes` - Get ontology classes
- `GET /api/ontologies/<ontology_name>/properties` - Get ontology properties

### Event Operations
- `GET /api/session/<session_id>/events` - Get session event history

### Health Check
- `GET /api/health` - Health check endpoint

## Usage Examples

### PyQt Client
```python
from shacl_brick_app.core.multi_tenant_backend import MultiTenantBackend

# Initialize multi-tenant backend
backend = MultiTenantBackend()

# Get Qt session (backward compatibility)
qt_session = backend.get_qt_session()
qt_backend = qt_session.editor_backend

# Use as before
brick_data = qt_backend.create_new_brick()
```

### Web Client
```python
import requests

# Create session
response = requests.post('http://localhost:5000/api/session', 
                        json={'client_type': 'web'})
session_id = response.json()['data']['session_id']

# Create brick
response = requests.post(f'http://localhost:5000/api/session/{session_id}/brick',
                        json={'brick_type': 'NodeShape'})
brick_data = response.json()['data']

# Update brick
requests.put(f'http://localhost:5000/api/session/{session_id}/brick',
              json={'name': 'My Brick', 'description': 'Test brick'})
```

## Benefits

### 1. **Session Isolation**
- Each client has isolated state
- No conflicts between users
- Safe concurrent operations

### 2. **Event-Driven Architecture**
- Real-time updates across clients
- Extensible event system
- Easy to add new client types

### 3. **Backward Compatibility**
- PyQt client works unchanged
- Existing code preserved
- Gradual migration possible

### 4. **Scalability**
- Supports unlimited concurrent clients
- Efficient resource usage
- Easy horizontal scaling

### 5. **Flexibility**
- Multiple client types supported
- Pluggable event handlers
- Extensible API design

## Launch Scripts

### PyQt Multi-Tenant Client
```bash
python launch_guided_brick_gui_multi_tenant.py
```

### Web API Server
```bash
python launch_web_api.py
```

## Development Status

### ✅ **Completed**
- [x] Session management system
- [x] Abstract event system
- [x] Multi-tenant backend coordinator
- [x] PyQt client integration
- [x] REST API wrapper
- [x] Basic web API endpoints

### 🚧 **In Progress**
- [ ] WebSocket support for real-time updates
- [ ] Advanced web UI components
- [ ] Session authentication
- [ ] Performance optimization

### 📋 **Planned**
- [ ] WebSocket event broadcasting
- [ ] User authentication system
- [ ] Advanced collaboration features
- [ ] Mobile web interface
- [ ] API documentation (Swagger)

## File Structure

```
shacl_brick_app/
├── core/
│   ├── session_manager.py      # Session management
│   ├── abstract_events.py       # Event system
│   ├── multi_tenant_backend.py # Multi-tenant coordinator
│   ├── brick_backend.py        # Original backend (unchanged)
│   └── editor_backend.py       # Original editor (unchanged)
├── api/
│   └── web_api.py            # REST API wrapper
├── gui/
│   └── ...                   # PyQt GUI (unchanged)
└── schema/
    └── ...                   # Schema GUI (unchanged)

Launch Scripts:
├── launch_guided_brick_gui_multi_tenant.py  # PyQt multi-tenant client
├── launch_web_api.py                     # Web API server
└── launch_schema_constructor.py            # Original schema constructor
```

## Migration Guide

### For PyQt Users
No changes required - existing PyQt launcher continues to work with enhanced architecture.

### For Web Developers
1. Start web API server: `python launch_web_api.py`
2. Use REST endpoints to interact with backend
3. Implement WebSocket client for real-time updates
4. Use session-based operations for state management

### For API Users
1. Create session via `/api/session`
2. Use session ID in all subsequent requests
3. Handle events via `/api/session/{session_id}/events`
4. Clean up sessions when done

## Performance Considerations

### Memory Usage
- Each session creates isolated backend instances
- Automatic cleanup prevents memory leaks
- Configurable session timeout

### Concurrency
- Thread-safe session management
- Event-driven updates prevent race conditions
- Isolated state prevents conflicts

### Scalability
- Horizontal scaling possible via load balancer
- Session state can be externalized
- Event system supports distributed deployment
