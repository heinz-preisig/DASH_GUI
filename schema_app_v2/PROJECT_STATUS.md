# Schema App v2 - Project Status Documentation

**Last Updated:** May 3, 2026  
**Purpose:** Documentation for computer switch - summarizes current state and next steps

---

## Project Overview

**Schema App v2** is a SHACL schema editor with brick-based composition. It allows users to create, edit, and export SHACL schemas using reusable brick components. The application supports both Qt desktop and web interfaces through a multi-tenant backend architecture.

### Key Features
- **SHACL Schema Creation**: Build schemas from reusable brick components
- **Multi-Tenant Backend**: Session isolation for concurrent users (Qt, Web, API)
- **UI Metadata System**: Organize components with sequences, groups, and parent-child relationships
- **Flow Engine**: Configure multi-step data entry workflows
- **SHACL Export**: Export schemas to Turtle and JSON-LD formats
- **Event System**: Real-time updates across multiple clients

---

## Architecture

### Directory Structure
```
schema_app_v2/
├── core/                           # Core business logic
│   ├── schema_core.py             # Schema management with UI metadata
│   ├── brick_integration.py       # Brick library integration
│   ├── shacl_export.py            # SHACL export functionality
│   ├── flow_engine.py             # Flow configuration engine
│   ├── schema_helper.py           # User-friendly helper functions
│   ├── abstract_events.py         # Event system for multi-client support
│   ├── session_manager.py         # Session management
│   └── multi_tenant_backend.py    # Multi-tenant backend coordinator
├── interfaces/
│   ├── qt/                        # Qt desktop interface
│   └── web/                       # Web interface (Flask)
├── shared_libraries/              # Shared brick/schema libraries
├── create_test_schema.py          # Test schema creation script
├── test_shacl_export.py           # SHACL export tests
├── test_ui_metadata.py            # UI metadata tests
├── test_flask_api.py              # Flask API tests
├── test_ui_metadata_api.py        # UI metadata API tests
└── schema_todo.txt                # TODO list (this file is outdated)
```

### Multi-Tenant Backend Architecture

**Key Components:**
- **MultiTenantBackend**: Coordinates multiple client sessions
- **SessionManager**: Creates and manages isolated sessions
- **SchemaBackendSession**: Provides isolated backend per session (SchemaCore, FlowEngine, BrickIntegration)
- **EventRouter**: Routes events to appropriate handlers based on client type
- **Event System**: Abstract event types with client-specific handlers

**Session Types:**
- `qt_session`: Qt desktop interface
- `web_session`: Web interface
- `api_session`: API clients

**Event Types:**
- SCHEMA_CREATED, SCHEMA_UPDATED, SCHEMA_LOADED, SCHEMA_SAVED, SCHEMA_DELETED
- COMPONENT_ADDED, COMPONENT_REMOVED
- ROOT_BRICK_SET, FLOW_UPDATED
- LIBRARY_CHANGED
- ERROR_OCCURRED, DIALOG_REQUESTED, STATUS_MESSAGE

### State Management

**UIStateManager with SchemaState Automaton:**
- States: INITIAL, SCHEMA_SELECTED, SCHEMA_MODIFIED, SCHEMA_SAVING, COMPONENT_ADDING, FLOW_EDITING
- Validates state transitions
- Controls widget visibility based on state
- Emits signals for state changes

---

## Completed Work

### Core Functionality
✅ **Schema Management** (`schema_core.py`)
- Schema CRUD operations (create, load, save, delete)
- Component brick management
- Library management (multi-library support)
- Schema extension/inheritance
- Daisy-chain configuration for multi-step interfaces

✅ **UI Metadata System** (`schema_core.py`)
- Component sequence management (ordering)
- Component grouping (logical grouping in UI)
- Parent-child relationships (tree structure for UI)
- UI-specific attributes (label, help text, collapsible, visibility)
- Tree structure queries (get_ui_tree, get_ui_children, etc.)

✅ **Brick Integration** (`brick_integration.py`)
- Brick library management
- NodeShape and PropertyShape brick types
- Brick CRUD operations
- SHACL export per brick
- Integration with shared_libraries

✅ **SHACL Export** (`shacl_export.py`)
- Export schemas to Turtle format
- Export schemas to JSON-LD format
- Schema documentation generation
- Flow configuration export
- Basic SHACL syntax validation

✅ **Flow Engine** (`flow_engine.py`)
- Flow configuration (linear, branching, conditional)
- Step management with conditions
- Navigation rules
- Daisy-chain support

✅ **Multi-Tenant Backend** (`multi_tenant_backend.py`)
- Session isolation for concurrent users
- Event-driven architecture
- Support for Qt, Web, and API clients
- Real-time updates across sessions

### UI Components
✅ **Qt Interface** (`interfaces/qt/`)
- Main window with Qt Designer UI (`main_window.ui`)
- Component selection dialog (`add_component_dialog.ui`)
- Flow editor dialog (`flow_editor.ui`)
- Help dialog (`main_window_help.ui`)
- State machine integration
- Backend integration via qt_session

✅ **Web Interface** (`interfaces/web/`)
- Flask API endpoints
- RESTful API for schema operations
- UI metadata API endpoints
- Backend integration via web_session

### Testing
✅ **Test Scripts**
- `create_test_schema.py`: Creates test schemas with UI metadata
- `test_shacl_export.py`: Tests SHACL export functionality
- `test_ui_metadata.py`: Tests UI metadata operations
- `test_flask_api.py`: Tests Flask API endpoints
- `test_ui_metadata_api.py`: Tests UI metadata API

---

## Current Status (from Memories)

### Previously Completed (from DASH_GUI main project)

#### Ontology Browser Fix
- **Issue**: Complete GUI missing `populate_ontology_list()` method call
- **Fix**: Added method call and fixed cache directory path in OntologyManager
- **Status**: ✅ Resolved
- **Details**: Ontology list shows 3 cached ontologies (Schema.org, FOAF, BRICK)

#### Constraint Editor Implementation
- **Status**: ✅ Complete
- **Features**:
  - Constraint editor UI with Qt Designer (`constraint_editor.ui`)
  - State controller for UI management
  - Support for 8 constraint types (minCount, maxCount, minLength, maxLength, pattern, datatype, in, notIn)
  - Double-click property to open constraint manager
  - Full CRUD operations for constraints
  - Data persistence to brick core and JSON files

#### Tree Structure Extension (DISCUSSION PHASE)
- **Status**: 🔄 Discussed, not implemented
- **Goal**: Build complex hierarchical schemas with nested structures
- **Example Structure**:
  ```
  Product (NodeShape)
  ├── Company (PropertyShape → NodeShape)
  │   ├── name, logo (PropertyShapes)
  │   └── Address (PropertyShape → NodeShape)
  │       └── street, houseNumber, zipCode, town, country
  └── Properties (grouping)
      ├── Looks (grouping)
      └── PhysicalProperties (grouping)
  ```
- **Key Questions**:
  1. PropertyShape vs NodeShape nesting (sh:node vs relationships)
  2. Grouping representation (virtual nodes, sh:group, or metadata)
  3. DASH integration for hierarchical forms
- **Proposed Approach**: Extend parent-child system, allow PropertyShapes to reference NodeShapes via sh:node, add grouping in schema metadata (not SHACL)

---

## Remaining Work / Next Steps

### High Priority

1. **Tree Structure Implementation**
   - Implement hierarchical schema structure in UI
   - Add drag-drop for setting parent-child relationships in tree view
   - Update SHACL export to handle hierarchy (sh:node references)
   - Implement grouping in UI metadata (virtual grouping nodes)
   - Test with complex nested schemas

2. **DASH Integration**
   - Generate hierarchical DASH forms from tree structure
   - Handle nested data entry (address within company)
   - Support dynamic addition of repeated elements
   - Test end-to-end form generation

3. **UI Enhancements**
   - Tree view component in Qt interface
   - List/tree toggle functionality
   - Drag-drop for parent-child relationships
   - Visual representation of groups

### Medium Priority

4. **Testing**
   - Comprehensive unit tests for core modules
   - Integration tests for multi-tenant backend
   - End-to-end tests for Qt and web interfaces
   - Performance testing for large schemas

5. **Documentation**
   - API documentation for Flask endpoints
   - User guide for Qt interface
   - Architecture documentation
   - Developer guide for extending the system

6. **Error Handling**
   - Robust error handling in backend
   - User-friendly error messages in UI
   - Validation for schema constraints
   - Recovery mechanisms for corrupted data

### Low Priority

7. **Features**
   - Schema templates
   - Import/export from other formats (JSON Schema, XML Schema)
   - Schema validation against brick library
   - Version control for schemas
   - Collaboration features (multi-user editing)

8. **Performance**
   - Caching for brick library lookups
   - Lazy loading for large schemas
   - Optimization for SHACL export
   - Database backend option (currently file-based)

---

## How to Run

### Prerequisites
- Python 3.8+
- PyQt5 (for Qt interface)
- Flask (for web interface)
- rdflib (for RDF/SHACL operations)

### Running Qt Interface
```bash
cd /home/heinz/1_Gits/DASH_GUI/schema_app_v2
python main.py
```

### Running Web Interface
```bash
cd /home/heinz/1_Gits/DASH_GUI/schema_app_v2/interfaces/web
python app.py
```

### Creating Test Schema
```bash
cd /home/heinz/1_Gits/DASH_GUI/schema_app_v2
python create_test_schema.py
```

### Running Tests
```bash
# Test SHACL export
python test_shacl_export.py

# Test UI metadata
python test_ui_metadata.py

# Test Flask API
python test_flask_api.py

# Test UI metadata API
python test_ui_metadata_api.py
```

---

## Key Files to Reference

### Core Logic
- `core/schema_core.py` - Schema and UI metadata data structures
- `core/brick_integration.py` - Brick library operations
- `core/shacl_export.py` - SHACL export logic
- `core/multi_tenant_backend.py` - Backend architecture

### UI Files
- `interfaces/qt/schema_gui.py` - Main Qt GUI
- `interfaces/qt/add_component_dialog.py` - Component selection
- `interfaces/qt/flow_editor_dialog.py` - Flow editor
- `interfaces/web/app.py` - Flask web application

### Test Files
- `create_test_schema.py` - Test schema creation
- `test_shacl_export.py` - SHACL export tests
- `test_ui_metadata_api.py` - API tests

### UI Designer Files
- `interfaces/qt/ui/main_window.ui`
- `interfaces/qt/ui/add_component_dialog.ui`
- `interfaces/qt/ui/flow_editor.ui`
- `interfaces/qt/ui/main_window_help.ui`

---

## Important Notes

### Shared Libraries
- The application uses the `shared_libraries` mechanism for brick and schema storage
- Library path is managed by `library_manager.py` in the parent directory
- Ensure shared_libraries directory structure is maintained when switching computers

### Data Persistence
- Schemas are stored as JSON files in `schema_repositories/{library_name}/schemas/`
- Bricks are stored in shared libraries
- UI metadata is embedded in schema JSON files

### Session Isolation
- Each client session has isolated SchemaCore, FlowEngine, and BrickIntegration instances
- Shared data is accessed through shared_libraries
- Events are routed to appropriate handlers based on client type

### State Machine
- UI operations must respect the SchemaState automaton
- State transitions are validated before execution
- Widget visibility is controlled by state

---

## Contact / Context

This project is part of the larger DASH_GUI system. The goal is to create browser-based data entry interfaces from SHACL schemas using DASH.

**Related Projects:**
- DASH_GUI main project (parent directory)
- OntoBuild_v1 (mentioned as reference for RDF tree structures)

**Key Decision Points:**
1. How to represent hierarchical schemas in SHACL (sh:node vs flat structure)
2. How to represent groupings in UI (virtual nodes vs SHACL groups)
3. How to integrate with DASH for form generation

---

## Quick Start Checklist for New Computer

1. **Clone Repository**
   ```bash
   cd /home/heinz/1_Gits/DASH_GUI
   git clone <repository-url>
   ```

2. **Install Dependencies**
   ```bash
   pip install PyQt5 Flask rdflib
   ```

3. **Verify Shared Libraries**
   - Ensure `shared_libraries` directory exists
   - Verify `library_manager.py` is present
   - Check brick library has required bricks

4. **Run Test Schema**
   ```bash
   cd schema_app_v2
   python create_test_schema.py
   ```

5. **Launch Qt Interface**
   ```bash
   python main.py
   ```

6. **Verify Functionality**
   - Create a new schema
   - Add component bricks
   - Set UI metadata (sequence, groups, parent-child)
   - Export to SHACL
   - Test web interface if needed

---

**End of Documentation**
