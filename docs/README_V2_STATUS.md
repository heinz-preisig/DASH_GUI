# Schema App v2 - Current Status & Architecture

**Date**: May 19, 2026  
**Status**: Refactored & Operational

## Architecture Overview

### Core Components
- **brick_app_v2/**: Core brick management system (local state)
- **schema_app_v2/**: Schema construction and management system (local state)
- **brick_repositories/**: Active brick repository (7 bricks available)
- **schema_repositories/**: Schema storage repository
- **ontologies/**: Ontology cache for brick system

### Recent Architecture Changes (May 2026)

#### Local State Refactoring
Both Qt applications have been refactored from **global state** to **local state** architecture:

| Before | After |
|--------|-------|
| Global `app_state_manager` | Instance variables (`self.ui_state`, `self.current_brick`) |
| `state/app_state.py` module | Removed (archived) |
| `business/brick_operations.py` | Replaced by `business/brick_service.py` |
| `ui/ui_abstraction.py` | Removed (archived) |
| `ui/constraint_manager.py` | Removed (archived) |

#### Benefits
- **Simpler to understand**: State is local to each GUI instance
- **No global dependencies**: Each window manages its own state
- **Easier to maintain**: Clear data flow, no hidden state changes
- **Better for testing**: Can create multiple independent instances

#### File Renames
- `brick_app_v2/refactored_gui.py` → `brick_app_v2/brick_editor.py`

#### New Features
- **Property editing**: Double-click any property to edit name/path
- **Schema double-click**: Double-click schema in list to open for editing

### Interface Options

#### ✅ PyQt6 Interface (Working)
- **Location**: `schema_app_v2/interfaces/qt/`
- **Main File**: `schema_gui.py`
- **Launcher**: `run_schema_app_v2.py`
- **Status**: Fully functional, ready for testing
- **Features**:
  - Schema creation, editing, saving
  - Brick integration (7 bricks loading)
  - SHACL export
  - Flow management
  - Library management

#### ✅ Flask Web Interface (Working)
- **Location**: `schema_app_v2/interfaces/web/`
- **Main File**: `flask_app.py`
- **Frontend**: React + Vite modular architecture
- **Build Script**: `dev-build-frontend-web.sh`
- **Status**: Fully functional, ready for testing
- **Features**:
  - Schema creation, editing, saving
  - Component management with proper name display
  - Tree view with hierarchical structure
  - Groups and schema references
  - SHACL export
- **Launch**: `uv run python run_schema_app_web.py --port 5003`

#### 📊 DASH Web Interface (Interactive)
- **Location**: `schema_app_v2/interfaces/web/dash_app.py`
- **Status**: Code available, requires Dash/Plotly/Pandas dependencies
- **Features**: Interactive web interface from SHACL/bricks
- **Ready for**: Installation with `pip install dash plotly pandas`
- **Launch**: `python3 -m schema_app_v2.interfaces.web.dash_app`

## Testing Readiness

### ✅ Ready for Testing
1. **PyQt6 GUI**: Launches successfully with `python3 run_schema_app_v2.py`
2. **Brick Integration**: Loads 7 bricks from repository
3. **Schema Operations**: Create, save, load, export schemas
4. **Repository Management**: Clean, focused structure

### 📋 Testing Checklist
- [ ] Schema creation and editing
- [ ] Brick selection and component addition
- [ ] Schema validation
- [ ] SHACL export functionality
- [ ] Flow configuration
- [ ] Library switching

### 🔧 Dependencies
- **Required**: PyQt6 (installed and working)
- **Optional**: Flask (for web interface, not required for testing)

## Project Structure

```
DASH_GUI/
├── brick_app_v2/              # Core brick system
├── schema_app_v2/             # Schema construction system
│   ├── interfaces/
│   │   ├── qt/              # PyQt6 interface (working)
│   │   └── web/             # Web interfaces
│   │       ├── flask_app.py   # Flask interface (future)
│   │       └── dash_app.py   # DASH interface (interactive)
│   └── core/                 # Core logic
├── brick_repositories/          # Active brick library
├── schema_repositories/        # Schema storage
├── ontologies/               # Ontology cache
├── run_schema_app_v2.py     # Main launcher
└── archive/                  # Legacy components
```

## Launch Commands

```bash
# Desktop
uv run python run_schema_app_qt.py
uv run python run_brick_app_qt.py

# Web
uv run python run_schema_app_web.py   # → http://localhost:5000
uv run python run_brick_app_web.py    # → http://localhost:5001

# Docker
./dev-start-schema-docker.sh
./dev-start-brick-docker.sh
```

## Next Steps

1. **Testing**: Verify all interface launchers work
3. **Enhancement**: Add more bricks to repository
4. **Documentation**: Expand troubleshooting guides

The v2 architecture is clean, modular, and ready for comprehensive testing.
