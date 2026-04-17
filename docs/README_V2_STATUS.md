# Schema App v2 - Current Status & Architecture

**Date**: April 17, 2026  
**Status**: Ready for Testing

## Architecture Overview

### Core Components
- **brick_app_v2/**: Core brick management system
- **schema_app_v2/**: Schema construction and management system
- **brick_repositories/**: Active brick repository (7 bricks available)
- **schema_repositories/**: Schema storage repository
- **ontologies/**: Ontology cache for brick system

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

#### 🔄 Flask Web Interface (Future)
- **Location**: `schema_app_v2/interfaces/web/`
- **Main File**: `flask_app.py`
- **Status**: Code available, requires Flask dependency
- **Ready for**: Future web development

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

## Task Management

### 🚀 Centralized Task Runner
- **Script**: `run_tasks.py` - Unified command-line interface
- **Documentation**: `TASK_MANAGER.md` - Complete reference guide
- **Commands**: Status, launch interfaces, process management, testing

### 📋 Available Commands
```bash
python3 run_tasks.py status    # System status
python3 run_tasks.py qt        # PyQt6 interface
python3 run_tasks.py dash       # DASH web interface
python3 run_tasks.py stop      # Stop all processes
python3 run_tasks.py setup     # Environment check
```

## Next Steps

1. **Immediate**: Use `run_tasks.py` for all operations
2. **Testing**: Verify all interface launchers work
3. **Enhancement**: Add more bricks to repository
4. **Documentation**: Expand troubleshooting guides

The v2 architecture is clean, modular, and ready for comprehensive testing.
