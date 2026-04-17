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

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r pyproject.toml

# Verify installation
python3 run_tasks.py setup
```

### First Launch
```bash
# Desktop Interface
python3 run_tasks.py qt

# Web Interface
python3 run_tasks.py dash
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
- **Export SHACL**: Generate SHACL file
- **Validate**: Check schema for errors

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
2. Choose file location and name
3. Select format (Turtle recommended)
4. SHACL file generated for use in other tools

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

#### Add Custom Bricks
1. Create brick files in JSON format
2. Place in `brick_repositories/default/bricks/`
3. Bricks appear automatically in interface

## Advanced Features

### Schema Validation
The system provides comprehensive validation:

#### Validation Rules
- **Required Fields**: Name and root brick must be specified
- **Target Class**: NodeShape bricks need valid target class
- **Property Paths**: PropertyShape bricks need valid paths
- **Data Types**: All properties must have valid data types

#### Validation Process
1. Click "Validate Schema" or menu: Tools → Validate
2. System checks all validation rules
3. Results show in validation dialog
4. Fix errors before saving

### Flow Management
Configure data flows for your schemas:

#### Flow Types
- **Linear**: Sequential data processing
- **Branching**: Conditional data flows
- **Looping**: Iterative processing
- **Parallel**: Concurrent processing

#### Flow Configuration
1. Select flow type in flow dropdown
2. Configure flow steps and conditions
3. Test flow with sample data
4. Save flow configuration

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
3. Run `python3 run_tasks.py setup` to diagnose
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
1. Check port 8050 is available
2. Verify no firewall blocking
3. Try different browser
4. Check console for error messages

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
- **Status Check**: `python3 run_tasks.py status`
- **System Tests**: `python3 run_tasks.py test`
- **Environment Info**: `python3 run_tasks.py setup`

---

**Complete Guide**: This document covers all major features of DASH GUI v2. For specific questions, refer to the troubleshooting section or built-in help system.
