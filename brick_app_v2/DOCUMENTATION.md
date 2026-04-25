# Brick App v2 - Complete Documentation

## Overview

Brick App v2 is a comprehensive SHACL brick generation system with dual frontend support (PyQt and Web), complete constraint management, and clean architecture. This document provides complete setup, usage, and development instructions.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Frontend Options](#frontend-options)
3. [Architecture](#architecture)
4. [Features](#features)
5. [User Guide](#user-guide)
6. [API Documentation](#api-documentation)
7. [Development](#development)
8. [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

```bash
# Python 3.8+ required
python --version
```

### Installation Options

#### Option 1: Modern Python (Recommended)

**Using uv (fast Python package manager):**
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project in development mode
cd /home/heinz/1_Gits/DASH_GUI/brick_app_v2
uv sync

# Run application
uv run python main.py --gui
uv run python main.py --web --port 5000
```

**Using pip with pyproject.toml:**
```bash
cd /home/heinz/1_Gits/DASH_GUI/brick_app_v2
pip install -e .

# Run application
python main.py --gui
python main.py --web --port 5000
```

#### Option 2: Traditional Installation

```bash
# Install dependencies manually
pip install PyQt6 rdflib flask flask-cors

# For development tools (optional)
pip install pytest black flake8
```

### Environment Configuration

#### Environment Variables (Optional)

Create a `.env` file for configuration:
```bash
# Create .env file
cd /home/heinz/1_Gits/DASH_GUI/brick_app_v2
cat > .env << EOF
# Brick App v2 Environment Configuration

# Repository Settings
BRICK_REPOSITORY_PATH=./shared_libraries

# Web Interface Settings
WEB_HOST=localhost
WEB_PORT=5000
WEB_DEBUG=false

# Development Settings
PYTHONPATH=/home/heinz/1_Gits/DASH_GUI/brick_app_v2
LOG_LEVEL=INFO
EOF
```

#### Using .env File
```bash
# Install python-dotenv for environment variable support
pip install python-dotenv

# Load environment variables before running
export $(cat .env | xargs)
python main.py --web --port $WEB_PORT
```

### Starting the Application

#### Option 1: Using Launcher Scripts (Recommended)
```bash
# From main DASH_GUI directory
python run_brick_app_qt.py              # Launch Qt GUI
python run_brick_app_web.py             # Launch Web Interface
```

#### Option 2: Direct with uv
```bash
cd /home/heinz/1_Gits/DASH_GUI/brick_app_v2
uv run main.py --gui
uv run main.py --web --port 5000
```

#### Option 3: Direct with Python
```bash
cd /home/heinz/1_Gits/DASH_GUI/brick_app_v2
python main.py --gui
python main.py --web --port 5000
```

## Frontend Options

### PyQt GUI Frontend

**Features:**
- Native desktop application
- Rich visual interface
- Advanced brick editing
- Library management
- Export capabilities

**Startup:**
```bash
# Option 1: Launcher script
python run_brick_app_qt.py

# Option 2: Direct with uv
cd brick_app_v2
uv run main.py --gui

# Option 3: Direct with Python
cd brick_app_v2
python main.py --gui
```

**Usage:**
1. Launch application
2. Select or create brick library
3. Add/edit bricks with properties and constraints
4. Export SHACL definitions

### Web Interface Frontend

**Features:**
- Modern web-based interface
- Browser-based access
- Real-time constraint management
- Context-aware constraint suggestions
- Cross-platform compatibility

**Startup:**
```bash
# Option 1: Launcher script
python run_brick_app_web.py

# Option 2: Direct with uv
cd brick_app_v2
uv run main.py --web --port 5000

# Option 3: Direct with Python
cd brick_app_v2
python main.py --web --port 5000
```

**Access:**
```
http://localhost:5000
```

**Usage:**
1. Open browser to localhost:5000
2. Select brick from sidebar
3. Edit brick details, properties, constraints
4. Save changes automatically

## Architecture

### Clean Architecture Design

```
┌─────────────────┐    ┌─────────────────┐
│   PyQt GUI      │    │   Web GUI       │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          ▼                      ▼
┌─────────────────────────────────────────┐
│         Multi-Tenant Backend            │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ Session Mgr │  │ Event Manager  │   │
│  └─────────────┘  └─────────────────┘   │
└─────────┬───────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│        Core Business Logic             │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ Brick Core  │  │ Editor Backend  │   │
│  └─────────────┘  └─────────────────┘   │
└─────────┬───────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│         Storage Layer                  │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │Shared Libs  │  │  Config Files  │   │
│  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────┘
```

### Key Components

#### Multi-Tenant Backend
- **Session Management**: Isolated sessions for each client
- **Event System**: Real-time communication between components
- **Clean Separation**: Frontend-agnostic backend design

#### Shared Libraries
- **Location**: `shared_libraries/`
- **Structure**: Libraries contain bricks with metadata
- **Compatibility**: Both frontends access same libraries

#### Constraint Management
- **SHACL Compliance**: Full SHACL constraint support
- **Context-Aware**: Smart suggestions based on datatype
- **Property-Level**: Constraints on individual properties

## Features

### Brick Management
- ✅ **Create Bricks**: NodeShape and PropertyShape support
- ✅ **Edit Properties**: Full property editing with SHACL terms
- ✅ **Constraint Management**: Add/edit/delete constraints
- ✅ **Library System**: Multiple brick libraries
- ✅ **Real-time Sync**: Changes visible in both frontends

### Constraint Features
- ✅ **14 Constraint Types**: minCount, maxCount, minLength, maxLength, pattern, datatype, class, nodeKind, in, not, equals, disjoint, lessThan, lessThanOrEquals
- ✅ **Context-Aware**: Smart filtering based on property datatype
- ✅ **Property Constraints**: Constraints on individual properties
- ✅ **Validation**: Type-specific constraint validation
- ✅ **Professional UI**: Modal editors with browse functionality

### SHACL Support
- ✅ **NodeShape**: Target class definitions
- ✅ **PropertyShape**: Property path constraints
- ✅ **Full Compliance**: SHACL specification adherence
- ✅ **Export**: SHACL Turtle format export

## User Guide

### Creating Bricks

#### PyQt GUI
1. **Launch**: `python run_brick_app_qt.py` or `cd brick_app_v2 && uv run main.py --gui`
2. **Library**: Select or create library
3. **New Brick**: Click "New Brick"
4. **Details**: Enter name, description, type
5. **Properties**: Add properties with SHACL terms
6. **Constraints**: Add constraints with validation
7. **Save**: Save brick to library

#### Web Interface
1. **Launch**: `python run_brick_app_web.py` or `cd brick_app_v2 && uv run main.py --web --port 5000`
2. **Access**: Open `http://localhost:5000`
3. **Select**: Choose brick from sidebar
4. **Edit**: Modify details in main panel
5. **Properties**: Click "Add Property" for new properties
6. **Constraints**: Click "Add Constraint" for brick constraints
7. **Property Constraints**: Click "+C" on properties for property constraints
8. **Save**: Click "Save" button

### Property Management

#### Adding Properties
1. **Property Path**: Use SHACL property paths (e.g., `foaf:name`)
2. **Datatype**: Select from XSD datatypes
3. **Default Value**: Optional default values
4. **Description**: Property descriptions
5. **Browse**: Use property browser for assistance

#### Property Constraints
1. **Select Property**: Click "+C" next to property
2. **Constraint Type**: Choose from context-aware options
3. **Value**: Enter constraint value with validation
4. **Description**: Optional constraint description
5. **Save**: Apply constraint to property

### Constraint Types

#### Count Constraints
- **minCount**: Minimum number of values (e.g., `1`)
- **maxCount**: Maximum number of values (e.g., `5`)

#### String Constraints
- **minLength**: Minimum string length (e.g., `3`)
- **maxLength**: Maximum string length (e.g., `50`)
- **pattern**: Regular expression pattern (e.g., `^[A-Za-z]+$`)

#### Type Constraints
- **datatype**: Required datatype (e.g., `xsd:string`)
- **class**: Required class (e.g., `foaf:Person`)
- **nodeKind**: Node kind (blank, iri, literal)

#### Value Constraints
- **in**: List of allowed values (e.g., `["red", "green", "blue"]`)
- **not**: Negated constraint (e.g., `foaf:name`)
- **equals**: Equals another property (e.g., `ex:otherProperty`)
- **disjoint**: Disjoint with another property
- **lessThan**: Less than another property
- **lessThanOrEquals**: Less than or equal to another property

## API Documentation

### Web API Endpoints

#### Session Management
```
POST /api/session                    # Create session
GET  /api/session/<session_id>       # Get session info
DELETE /api/session/<session_id>     # Delete session
```

#### Library Management
```
GET  /api/libraries                  # List libraries
GET  /api/libraries/<name>/bricks    # Get library bricks
```

#### Brick Operations
```
GET  /api/bricks                     # List all bricks
POST /api/session/<id>/brick         # Create brick
PUT  /api/session/<id>/brick         # Update brick
POST /api/session/<id>/brick/save    # Save brick
POST /api/session/<id>/brick/load/<id>  # Load brick
```

#### Property Operations
```
POST /api/session/<id>/brick/properties  # Add property
DELETE /api/session/<id>/brick/properties/<name>  # Delete property
```

### Response Format

```json
{
  "status": "success|error",
  "data": { ... },
  "message": "Description"
}
```

## Development

### Modern Development Workflow

#### Using uv for Development
```bash
# Install development dependencies
uv sync --dev

# Run tests with uv
uv run pytest

# Code formatting
uv run black .

# Linting
uv run flake8 .

# Run application in development mode
uv run python main.py --web --debug
```

#### Using pip for Development
```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black .

# Linting
flake8 .

# Run application in development mode
python main.py --web --debug
```

### Project Structure

```
brick_app_v2/
├── main.py                    # Application entry point
├── refactored_gui.py          # Qt GUI frontend
├── gui_components.py          # Dialog components (load from .ui files)
├── pyproject.toml             # Modern Python packaging
├── README.md                  # Basic documentation
├── DOCUMENTATION.md           # This file
├── .env                      # Environment variables (optional)
├── shared_libraries/          # Shared brick libraries
│   ├── config.json           # Library configuration
│   ├── bricks/               # Brick storage
│   └── schemas/              # Schema storage
├── api/                      # Web interface
│   └── web_api.py            # Flask web server
├── core/                     # Backend logic
│   ├── multi_tenant_backend.py
│   ├── brick_generator.py
│   ├── brick_core_simple.py
│   ├── ontology_manager.py
│   ├── session_manager.py
│   └── abstract_events.py
├── ui/                       # Qt Designer .ui files
│   ├── main_window.ui
│   ├── ontology_browser_simple.ui
│   ├── property_brick_browser.ui
│   ├── constraint_editor.ui
│   └── property_editor.ui
├── state/                    # State management
│   └── app_state.py
└── business/                 # Business logic
    └── brick_operations.py
```

### Adding New Features

#### New Constraint Types
1. Add to `SHACLConstraintType` enum in `brick_generator.py`
2. Update constraint validation logic
3. Add to frontend constraint type dropdowns
4. Update constraint browser descriptions

#### New Frontend Features
1. Implement in both PyQt and web frontends
2. Use shared backend APIs
3. Maintain data compatibility
4. Update documentation

### Testing

#### Run Tests
```bash
# From brick_app_v2 directory
python -m pytest tests/
```

#### Test Coverage
- Backend API tests
- Constraint validation tests
- Frontend integration tests
- Library management tests

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Add to Python path
export PYTHONPATH=/home/heinz/1_Gits/DASH_GUI:$PYTHONPATH
```

#### Port Conflicts
```bash
# Use different port
python run_brick_app_web.py  # Or: cd brick_app_v2 && uv run main.py --web --port 5001
```

#### Library Not Found
```bash
# Check shared_libraries directory
ls -la shared_libraries/bricks/
```

#### Constraint Save Errors
- Check constraint data structure
- Verify SHACLConstraint constructor parameters
- Ensure proper datatype validation

### Debug Mode

#### Web Interface
```bash
python main.py --web --debug --port 5000
```

#### PyQt GUI
```bash
python main.py --gui --debug
```

### Logs and Debugging

#### Console Output
- Brick loading information
- Constraint validation results
- Save/load operations
- Error messages with details

#### Browser Console
- Network requests
- JavaScript errors
- Constraint display debugging

## Configuration

### Library Configuration
File: `shared_libraries/config.json`
```json
{
  "version": "2.0",
  "libraries": {
    "bricks": {
      "default_path": "shared_libraries/bricks",
      "libraries": [
        {
          "name": "default",
          "path": "shared_libraries/bricks/default",
          "description": "Default brick library",
          "type": "bricks"
        }
      ]
    }
  }
}
```

### Backend Configuration
- Repository path: `shared_libraries`
- Session management: Automatic
- Event handling: Real-time

## Performance

### Optimization Tips
- Use appropriate constraint types
- Limit constraint complexity
- Regular library cleanup
- Monitor memory usage

### Scalability
- Multi-tenant backend design
- Session isolation
- Shared library access
- Event-driven architecture

## Security

### Data Protection
- Local file storage only
- No external network access
- Session isolation
- Input validation

### Best Practices
- Regular backups of shared_libraries
- Validate constraint inputs
- Monitor file permissions
- Secure session management

---

## Summary

Brick App v2 provides a complete SHACL brick generation system with:
- **Dual Frontend Support**: PyQt GUI and Web Interface
- **Full Constraint Management**: 14 constraint types with validation
- **Clean Architecture**: Multi-tenant backend with session management
- **Real-time Sync**: Shared libraries between frontends
- **Professional UI**: Context-aware constraint suggestions
- **SHACL Compliance**: Full specification adherence

Both frontends provide the same functionality with different user experiences, allowing users to choose their preferred interface while maintaining data compatibility and real-time synchronization.
