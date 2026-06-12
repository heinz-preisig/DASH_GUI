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
cd /home/heinz/1_Gits/DASH_GUI/brick_app
uv sync

# Run application
uv run python main.py --gui
uv run python main.py --web --port 5001
```

**Using pip with pyproject.toml:**
```bash
cd /home/heinz/1_Gits/DASH_GUI/brick_app
pip install -e .

# Run application
python main.py --gui
python main.py --web --port 5001
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
cd /home/heinz/1_Gits/DASH_GUI/brick_app
cat > .env << EOF
# Brick App v2 Environment Configuration

# Repository Settings
BRICK_REPOSITORY_PATH=./shared_libraries

# Web Interface Settings
WEB_HOST=localhost
WEB_PORT=5001
WEB_DEBUG=false

# Development Settings
PYTHONPATH=/home/heinz/1_Gits/DASH_GUI/brick_app
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
python run_brick_app_web.py             # Launch Web Interface (default port 5001)
python run_brick_app_web.py --port 5002 # Launch on custom port
```

#### Option 2: Direct with uv
```bash
cd /home/heinz/1_Gits/DASH_GUI/brick_app
uv run main.py --gui
uv run main.py --web --port 5001
```

#### Option 3: Direct with Python
```bash
cd /home/heinz/1_Gits/DASH_GUI/brick_app
python main.py --gui
python main.py --web --port 5001
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
cd brick_app
uv run main.py --gui

# Option 3: Direct with Python
cd brick_app
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
# Option 1: Launcher script (default port 5001)
python run_brick_app_web.py

# Option 1b: Custom port
python run_brick_app_web.py --port 5002

# Option 2: Direct with uv
cd brick_app
uv run main.py --web --port 5001

# Option 3: Direct with Python
cd brick_app
python main.py --web --port 5001
```

**Access:**
```
http://localhost:5001
```

**Usage:**
1. Open browser to localhost:5001
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
- ✅ **Create Bricks**: NodeShape bricks in any library
- ✅ **Edit Properties**: Full property editing with SHACL terms
- ✅ **Constraint Management**: Add/edit/delete constraints via inline editor
- ✅ **Library System**: Multiple brick libraries
- ✅ **Rename Bricks**: Rename a brick and its backing file in one step
- ✅ **Copy Bricks**: Copy any brick from any library to any other library, with automatic conflict resolution

### Leaf Property Presets
- ✅ **Preset Library**: Each library has a `_presets.json` file storing named `LeafProperty` templates
- ✅ **Insert Preset**: Insert a preset from any library into the currently open brick's property list
- ✅ **Save as Preset**: Save any selected leaf property as a reusable named preset
- ✅ **Template Library**: A dedicated `templates` library ships with ready-made presets (see below)
- ✅ **Independent Selection**: Preset library and active brick library are decoupled — browse any preset library while editing any brick

### Template Library
Location: `shared_libraries/bricks/templates/_presets.json`

Shipped presets:
| Name | Path | Type | Notes |
|---|---|---|---|
| Value (decimal) | ex:value | xsd:decimal | Generic numeric value |
| Label (text) | ex:label | xsd:string | Single-line text |
| Description (text) | ex:description | xsd:string | Multi-line description |
| Status (dropdown) | ex:status | sh:IRI, sh:in | Active/Inactive/Pending |
| Country (IRI) | ex:country | sh:IRI, sh:in | DE/FR/NO/US/GB |
| PhysicalQuantity value (decimal) | qudt:value | xsd:decimal | Numeric magnitude |
| PhysicalQuantity unit (IRI) | qudt:unit | sh:IRI, sh:in | 23 SI units from QUDT |

Template bricks (full NodeShapes) in any library can be copied to your target library via the **Template Bricks** panel.

### Ontology Browser
- ✅ **Class Browser**: Browse loaded ontologies for target class selection
- ✅ **Property Browser**: Browse loaded ontologies for `sh:path` selection
- ✅ **QUDT Support**: `qudt:Unit` and `qudt:QuantityKind` individuals extracted and browseable
- ✅ **Path Browse in Leaf Editor**: The `sh:path` field in the leaf property dialog has a Browse button
- ✅ **Auto-fill Label**: Selecting a property from the browser pre-fills the label field

### Constraint Features
- ✅ **Constraint Types**: minCount, maxCount, minLength, maxLength, pattern, datatype, in, notIn
- ✅ **Property Constraints**: Constraints on individual leaf properties
- ✅ **Validation**: Type-specific constraint validation
- ✅ **Professional UI**: Modal editors with type-specific input fields

### SHACL Support
- ✅ **NodeShape**: Target class definitions
- ✅ **PropertyShape (leaf properties)**: Property path constraints embedded in bricks
- ✅ **Full Compliance**: SHACL specification adherence
- ✅ **Export**: SHACL Turtle format export (`.ttl` written alongside `.json`)

## User Guide

### Creating Bricks

#### PyQt GUI
1. **Launch**: `python run_brick_app_qt.py` or `cd brick_app && uv run main.py --gui`
2. **Library**: Select or create library in the **Brick Library** panel
3. **New Node**: Click `new node` to create a fresh NodeShape brick
4. **Details**: Enter name, description, target class (use Browse button to pick from ontologies)
5. **Properties**: Click `add property` to add a leaf property via the editor dialog
6. **Browse Path**: In the leaf property dialog, click **Browse** next to `sh:path` to pick from loaded ontologies
7. **Constraints**: Set datatype, `sh:in` values, min/max counts in the leaf property editor
8. **Save**: Click `save` in the editor panel

### Renaming a Brick
1. Open the brick (double-click in the Node Bricks list)
2. Click **rename** in the editor button row
3. Enter the new name → OK

### Copying a Brick Between Libraries
1. In the right panel, select the **source library** in the library dropdown
2. The **Template Bricks** list shows all bricks in that library
3. Select the brick to copy
4. Click **copy to active library**
5. In the dialog: choose **target library** and optionally change the name
6. If a name conflict exists, the name is automatically suffixed (`_copy1`, `_copy2`, …)

### Using Presets
1. Open a brick for editing
2. In the right panel, select the preset library (e.g. `templates`)
3. The **Leaf Property Presets** list shows available presets
4. Select a preset → click `insert preset` (or double-click)
5. The preset is inserted as a new leaf property in the current brick

### Saving a Preset
1. Open a brick with leaf properties
2. Select a leaf property in the property list
3. Click `save as preset` → enter a name → OK
4. Preset is saved to the active library's `_presets.json`

#### Web Interface
1. **Launch**: `python run_brick_app_web.py` or `cd brick_app && uv run main.py --web --port 5001`
2. **Access**: Open `http://localhost:5001`
3. **Select**: Choose brick from sidebar
4. **Edit**: Modify details in main panel
5. **Properties**: Click "Add Property" for new properties
6. **Constraints**: Click "Add Constraint" for brick constraints
7. **Property Constraints**: Click "+C" on properties for property constraints
8. **Save**: Click "Save" button

### Property Management

#### Adding Properties
1. Click `add property` — opens **Leaf Property Editor**
2. **sh:path**: Type directly or click **Browse** to pick from loaded ontologies
3. **Label**: Human-readable label (auto-filled when browsing)
4. **sh:datatype**: Select XSD type from dropdown (editable)
5. **sh:nodeKind**: Leave blank or set `sh:IRI` for IRI-valued properties
6. **sh:in values**: Add allowed values (IRIs or literals) for constrained choices
7. **sh:minCount / sh:maxCount**: Cardinality (1..1 = required, exactly once)
8. Click **OK** to add to the brick

#### Editing a Property
- Double-click a property in the list to open the **Leaf Property Editor** pre-filled with existing values

#### Ontology-Driven Path Selection
- In the leaf property editor, the **Browse** button next to `sh:path` opens the **Ontology Browser** in properties mode
- Browse by ontology, filter by name
- Double-click a property to confirm and close
- QUDT unit/quantity individuals are browseable (loaded from `qudt-units`, `qudt-quantitykinds`)

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
brick_app/
├── main.py                    # Application entry point
├── refactored_gui.py          # Qt GUI frontend (main window logic)
├── gui_components.py          # Dialog components: LeafPropertyEditorDialog,
│                              #   SimpleOntologyBrowser, ConstraintEditorDialog, …
├── pyproject.toml             # Modern Python packaging
├── README.md                  # Basic documentation
├── DOCUMENTATION.md           # This file
├── core/
│   ├── brick_core_simple.py   # BrickCore, SHACLBrick, LeafProperty,
│   │                          #   LeafPresetStore, BrickTemplateType
│   ├── ontology_manager.py    # OntologyManager: load/cache/browse ontologies
│   │                          #   (supports owl:Class, rdf:Property, qudt:Unit,
│   │                          #    qudt:QuantityKind, sh:NodeShape)
│   ├── brick_ttl_serialiser.py # Serialize bricks to SHACL Turtle (.ttl)
│   ├── multi_tenant_backend.py
│   ├── brick_generator.py
│   ├── session_manager.py
│   └── abstract_events.py
├── ui/                        # Qt Designer .ui files
│   ├── main_window.ui         # Main window layout
│   ├── ontology_browser_simple.ui
│   ├── constraint_editor.ui
│   └── property_editor.ui
├── state/
│   └── app_state.py           # AppStateManager, UIState
├── business/
│   └── brick_operations.py    # BrickBusinessLogic:
│                              #   create, save, delete, rename, copy bricks;
│                              #   preset CRUD; ontology management
└── api/
    └── web_api.py             # Flask web server (secondary frontend)

shared_libraries/bricks/       # Brick storage root
├── default/                   # Example library
│   ├── <name>_<uuid>.json     # Brick files
│   ├── <name>_<uuid>.ttl      # SHACL Turtle export (auto-generated)
│   └── _presets.json          # Leaf property presets for this library
└── templates/                 # Shared template library
    └── _presets.json          # Shipped presets (PhysicalQuantity, etc.)
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
# From brick_app directory
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
# Port 5000 or 5001 already in use? Use different port:
python run_brick_app_web.py --port 5002
# Or: cd brick_app && uv run main.py --web --port 5002
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
python main.py --web --debug --port 5001
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

## Ontology Management

### Loading Ontologies
Ontologies are loaded at startup from `ontologies/cache/`. Use the **Download Ontology** button in the library panel to cache new ontologies by URL.

### Supported ontology patterns
| Pattern | Extracted as |
|---|---|
| `owl:Class`, `rdfs:Class` | Classes |
| `owl:ObjectProperty`, `owl:DatatypeProperty`, `rdf:Property` | Properties |
| `sh:NodeShape` | Classes (SHACL shapes) |
| `sh:path` values | Properties (from shape files) |
| `qudt:Unit` individuals | Classes (QUDT units vocabulary) |
| `qudt:QuantityKind` individuals | Classes (QUDT quantity kinds) |

### Recommended ontologies for physical modelling
| Name | URL | Contents |
|---|---|---|
| `qudt-units` | `https://raw.githubusercontent.com/qudt/qudt-public-repo/main/vocab/unit/VOCAB_QUDT-UNITS-ALL-v2.1.ttl` | ~1500 SI unit individuals |
| `qudt-quantitykinds` | `https://raw.githubusercontent.com/qudt/qudt-public-repo/main/vocab/quantitykinds/VOCAB_QUDT-QUANTITY-KINDS-ALL-v2.1.ttl` | Mass, Length, Pressure, … |

---

## Summary

Brick App v2 provides a complete SHACL brick generation system with:
- **Brick Library System**: Multiple libraries, copy/rename bricks across libraries
- **Leaf Property Editor**: Path browser, datatype, cardinality, `sh:in` list
- **Preset System**: Save and insert reusable leaf property templates per library
- **Template Library**: Shipped presets for common patterns (text, decimal, physical quantities)
- **Ontology Browser**: Browse classes and properties from cached ontologies, including QUDT
- **SHACL Export**: Auto-generated `.ttl` alongside each `.json` brick file
- **Clean Architecture**: Business logic, state, and UI strictly separated
