# User Guide - DASH GUI v2

**Purpose**: Complete user manual for DASH GUI v2 schema construction system.

## 📚 Table of Contents

1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Schema Construction](#schema-construction)
4. [Brick Management](#brick-management)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)

## Getting Started

### System Requirements
- Python 3.13 or higher
- PyQt6 (for desktop interface)
- Modern web browser (for web interface)
- 100MB free disk space

### Installation
```bash
# Clone or download project
cd DASH_GUI

# Install dependencies (using uv)
uv sync
```

### First Launch
```bash
# Desktop Interface
uv run python run_schema_app_qt.py
uv run python run_brick_app_qt.py

# Web Interface
uv run python run_schema_app_web.py   # → http://localhost:5000
uv run python run_brick_app_web.py    # → http://localhost:5001
```

## Interface Overview

### PyQt6 Desktop Interface
The desktop interface provides a rich, native experience with:

#### Main Window Areas
- **Menu Bar**: File, Tools, Help menus
- **Schema List**: Left panel showing all schemas
- **Brick Browser**: Center panel with available bricks
- **Construction Area**: Right panel for active schema
- **Status Bar**: Bottom status and messages

#### Key Controls
- **New Schema**: Create new schema from scratch
- **Open Schema**: Load existing schema
- **Save Schema**: Save current work
- **Export SHACL**: Generate SHACL Turtle file
- **Generate Web Form**: Export SHACL + HTML form and open preview in browser
- **Validate**: Check schema tree for cycles and orphaned nodes
- **Add Schema Ref**: Attach another schema via `sh:node` to a selected brick
- **Extend Schema**: Create a new schema that inherits all bricks from the current one

### DASH Web Interface
The web interface provides browser-based access with:

#### Web Features
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live schema construction
- **Interactive Components**: Modern web UI elements
- **Browser Access**: No installation required

#### Web Controls
- **Schema Creation**: Web forms for schema details
- **Brick Selection**: Interactive brick browser
- **Component Management**: Drag-and-drop interface
- **Export Options**: Download SHACL files

## Schema Construction

### Creating Your First Schema

#### Step 1: Basic Information
1. Click "New Schema" or use menu: File → New Schema
2. Enter schema name (required)
3. Add description (optional)
4. Click OK to create

#### Step 2: Select Root Brick
1. Browse NodeShape bricks in the root brick dropdown
2. Select appropriate root brick for your schema
3. Review target class information
4. Selection automatically sets the schema foundation

#### Step 3: Add Components
1. Browse PropertyShape bricks in the brick list
2. Double-click bricks to add them as components
3. Components appear in the component list
4. Order and organize components as needed

#### Step 4: Configure Properties
1. Set schema properties in the details panel
2. Configure validation rules
3. Set target classes and constraints
4. Review configuration before saving

### Saving and Exporting

#### Save Schema
1. Click "Save Schema" button or menu: File → Save
2. Schema is saved to `schema_repositories/default/schemas/`
3. Status bar shows save confirmation
4. Schema appears in schema list

#### Export SHACL
1. Click "Export SHACL" or menu: File → Export SHACL
2. SHACL Turtle file saved to the active library directory
3. File is immediately usable in other SHACL tools

#### Generate Web Form & Preview
1. Click "Generate Web Form" button
2. Both a `.ttl` and `_form.html` file are written to the active library directory
3. The form opens automatically in your system browser
4. The form uses the `@ulb-darmstadt/shacl-form` web component (requires internet for CDN)

## Brick Management

### Understanding Bricks

#### Brick Types
- **NodeShape Bricks**: Define schema structure and target classes
- **PropertyShape Bricks**: Define properties and constraints

#### Brick Components
- **Target Class**: What the brick describes (e.g., foaf:Person)
- **Properties**: Data attributes and relationships
- **Constraints**: Validation rules and restrictions
- **Metadata**: Creation info, tags, descriptions

### Working with Brick Libraries

#### Browse Libraries
1. Use library dropdown to switch between libraries
2. Available bricks update automatically
3. Library status shows in status bar

#### Import SHACL Bricks (Brick App)
1. Click "Import SHACL" button in the Brick App
2. Select a `.ttl` file containing `sh:NodeShape` definitions
3. Each NodeShape is converted to a brick and added to the active library

#### Add Custom Bricks
1. Create brick files in JSON format
2. Place in `ShaclForm-library/default/bricks/`
3. Bricks appear automatically in the interface

## Advanced Features

### Semantic Awareness (sh:class)

Link properties to ontology classes for smart form generation and validation hints.

#### What it does

When you set a **Semantic Class** (`sh:class`) on a property, the system:
1. **Recognizes the ontology** (QUDT, Schema.org, FOAF, Brick, etc.)
2. **Provides contextual help** — unit selectors, suggested properties, etc.
3. **Exports standard SHACL** — `sh:class foaf:Person ;` in the Turtle output

#### How to use it

In the **Property Editor** (when adding/editing a brick property):

**Field: Semantic Class (sh:class)**

You can either:
- **Type directly**: `foaf:Person`, `qudt:Mass`, `schema:PostalAddress`
- **Click "Browse"**: Opens ontology browser to search loaded ontologies
- **Click "Clear"**: Removes the semantic link

#### What appears based on the class

| Ontology | Class Example | Smart Widgets Appear |
|----------|---------------|----------------------|
| **QUDT** | `qudt:Mass`, `qudt:Temperature` | Unit dropdown (kg/g/lb/oz, °C/°F/K, etc.) |
| **Schema.org** | `schema:Person`, `schema:Organization` | Suggested properties buttons (givenName, email, etc.) |
| **FOAF** | `foaf:Person`, `foaf:Organization` | Suggested properties buttons (name, mbox, homepage) |
| **Brick** | `brick:Temperature_Sensor` | Suggested Brick properties (measures, hasLocation) |

#### Examples

**Physical Quantity (QUDT)**
```
Property Name: Weight
Property Path: ex:weight
Datatype: xsd:decimal
Semantic Class: qudt:Mass
→ Unit selector appears: [kg ▼] [g] [lb] [oz]
```

**Person (FOAF)**
```
Property Name: Contact Person
Property Path: ex:contact
Datatype: xsd:string
Semantic Class: foaf:Person
→ Suggested properties: [name] [mbox] [homepage] [phone]
  (clicking fills the property path automatically)
```

**Address (Schema.org)**
```
Property Name: Delivery Address
Property Path: ex:deliveryAddress
Datatype: xsd:string
Semantic Class: schema:PostalAddress
→ Suggested: [streetAddress] [addressLocality] [postalCode]
```

#### Why use this?

- **Standards-compliant**: Uses existing ontologies (no custom extensions)
- **Smart defaults**: Unit-aware quantities, context-aware suggestions
- **Interoperable**: Other tools understand `sh:class` and `foaf:Person`
- **Future-proof**: Adding more ontologies (Dublin Core, SIO, etc.) is easy

### Schema Validation
Checks the component tree for structural problems:

#### What is checked
- **Circular references**: detects cycles in parent-child nesting
- **Orphaned nodes**: components whose parent is not in the schema
- **Deep nesting**: warns if any component is nested more than 5 levels deep

#### Validation Process
1. Menu: Tools → Validate Schema
2. Results show component count, max depth, issues (✗) and warnings (⚠)
3. Green dialog = valid; yellow dialog = valid with warnings; red = issues found

### UI Metadata Editor
Double-click any component in the component list or tree to open the metadata editor:

- **Sequence tab**: set `sh:order` for display ordering
- **Grouping tab**: assign the component to a `PropertyGroup` (maps to `sh:group` in SHACL)
- **Nesting tab**: set a parent component (`sh:node` reference)
- **Display tab**: label, help text, visibility, collapsible

### Schema References
Attach one schema's NodeShape to a brick in the current schema:

1. Click "Add Schema Ref" button (or toolbar)
2. Select the target schema from the list
3. Select the brick in the current schema to attach to
4. Enter the `sh:path` IRI (e.g. `ex:hasAddress`)
5. The reference is stored and emitted as `sh:property [ sh:path … ; sh:node … ]` on export

### Extend Schema
Create a new schema pre-loaded with all bricks from an existing one:

1. Open the schema you want to extend
2. Menu: Tools → Extend Schema
3. Enter a name and optional description
4. A new schema is created with the parent's bricks — add more as needed
5. The `inheritance_chain` tracks the lineage

### Library Management
Advanced library operations:

#### Import Libraries
1. Menu: Tools → Manage Libraries
2. Click "Import Library"
3. Select library file or directory
4. Library added to available libraries

#### Export Libraries
1. Menu: Tools → Manage Libraries
2. Select library to export
3. Choose export location
4. Library saved for backup or sharing

## Troubleshooting

### Common Issues

#### Schema Won't Save
**Problem**: "Save failed" error message
**Solution**: 
1. Check all required fields are filled
2. Ensure root brick is selected
3. Verify schema name is unique
4. Check file permissions

#### Bricks Not Loading
**Problem**: No bricks appear in brick list
**Solution**:
1. Check brick repository path
2. Verify brick files are valid JSON
3. Run `uv run python -c "from brick_app_v2.core.brick_core_simple import BrickCore; print('OK')"` to diagnose
4. Restart application

#### Interface Errors
**Problem**: Interface crashes or freezes
**Solution**:
1. Check virtual environment is active
2. Verify all dependencies installed
3. Check system resources (memory, CPU)
4. Restart application

#### Web Interface Issues
**Problem**: Can't access web interface
**Solution**:
1. Schema App: check port 5000 is available
2. Brick App: check port 5001 is available
3. Verify no firewall blocking
4. Try different browser
5. Check terminal output for error messages

### Getting Help

#### Built-in Help
- **Help Menu**: Access comprehensive help system
- **Context Help**: F1 key for context-sensitive help
- **Tool Tips**: Hover over interface elements

#### Documentation
- **Quick Start**: `docs/QUICK_START.md`
- **Task Management**: `docs/TASK_MANAGER.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`

#### Support
- **Environment Check**: `uv sync` then `uv run python -c "import brick_app_v2; print('OK')"`
- **Logs**: Check terminal output when launching

---

**Complete Guide**: This document covers all major features of DASH GUI v2. For specific questions, refer to the troubleshooting section or built-in help system.
