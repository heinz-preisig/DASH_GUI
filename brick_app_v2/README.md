# SHACL Brick Generator - Step 1

A comprehensive SHACL brick generation system with full SHACL specification support, multiple brick libraries, and clean frontend/backend separation.

## Features

- **Full SHACL Support**: Complete support for 25 SHACL object types and 8 constraint types
- **Repository System**: Multiple brick libraries with save/load functionality
- **Clean Backend API**: Event-driven architecture supporting Qt, web, or any frontend
- **PyQt6 GUI**: Visual interface for brick creation, management, and export
- **Export Capabilities**: SHACL export to Turtle format
- **Comprehensive Testing**: Complete test suite with 10/10 tests passing

## Installation

```bash
# Navigate to the project directory
cd /home/heinz/1_Gits/DASH_GUI

# Install dependencies (assuming you have a virtual environment)
pip install PyQt6 rdflib
```

## Quick Start

### Option 1: Easy Launcher (Recommended)

```bash
# From the main DASH_GUI directory
python run_brick_app.py --gui          # Launch GUI
python run_brick_app.py --test         # Run tests
```

### Option 2: Package Import

```python
# Import the package
from shacl_brick_app import create_brick_system, run_gui

# Create a brick system
backend, processor = create_brick_system()

# Run the GUI
run_gui()
```

### Option 3: Direct Package Usage

```bash
# Navigate to the package directory
cd shacl_brick_app

# Run the GUI
python bricks.py --gui

# Run tests
python bricks.py --test

# Use custom repository path
python bricks.py --gui --repository ./my_libraries

# Show help
python bricks.py --help
```

### Option 4: Direct GUI Launch

```bash
# Run GUI directly (from package directory)
python gui/brick_gui.py
```

## Usage Examples

### Basic Python Usage

```python
from shacl_brick_app import create_brick_system

# Create brick system
backend, processor = create_brick_system("my_repositories")

# Create a Person NodeShape brick
result = processor.process_event({
    "event": "create_nodeshape_brick",
    "brick_id": "person_nodeshape",
    "name": "Person NodeShape",
    "description": "Basic person shape",
    "target_class": "foaf:Person",
    "tags": ["person", "basic"]
})

# Export to SHACL
result = processor.process_event({
    "event": "export_brick_shacl",
    "brick_id": "person_nodeshape",
    "format_type": "turtle"
})

if result["status"] == "success":
    print(result["data"]["content"])
```

### Running Examples

```bash
# Navigate to package directory
cd shacl_brick_app

# Run basic usage example
python examples/basic_usage.py
```

## Package Structure

```
shacl_brick_app/
|
|__ __init__.py              # Main package interface
|__ bricks.py                # Command line entry point (renamed from main.py)
|__ setup.py                 # Package setup script
|__ README.md                # This file
|
|__ core/                    # Backend components
|   |__ __init__.py
|   |__ brick_generator.py   # Core SHACL brick system
|   |__ brick_backend.py      # Backend API
|
|__ gui/                     # Frontend components
|   |__ __init__.py
|   |__ brick_gui.py         # PyQt6 GUI
|
|__ tests/                   # Test suite
|   |__ __init__.py
|   |__ test_brick_generator.py
|   |__ test_export_fix.py
|
|__ examples/                # Example scripts
|   |__ __init__.py
|   |__ basic_usage.py       # Basic usage example
```

## Core Components

### SHACLBrick
Represents a reusable SHACL brick with:
- Brick ID, name, description
- SHACL object type (NodeShape, PropertyShape)
- Targets, properties, constraints
- Tags and metadata

### BrickLibrary
Manages a collection of SHACL bricks:
- Add/remove/search bricks
- Export/import functionality
- Statistics and usage tracking

### BrickRepository
Manages multiple brick libraries:
- Create/delete libraries
- Set active library
- Repository-wide operations

### BrickBackendAPI
Clean backend API with:
- Event-driven communication
- JSON responses
- Frontend/backend separation

### BrickGUI
PyQt6 frontend with:
- Visual brick creation
- Search and filtering
- SHACL export
- Library management

## API Usage

### Creating Bricks

```python
from shacl_brick_app import create_brick_system

backend, processor = create_brick_system()

# Create a NodeShape brick
result = processor.process_event({
    "event": "create_nodeshape_brick",
    "brick_id": "person_nodeshape",
    "name": "Person NodeShape",
    "description": "Basic person shape",
    "target_class": "foaf:Person",
    "tags": ["person", "basic"]
})

# Create a PropertyShape brick
result = processor.process_event({
    "event": "create_propertyshape_brick",
    "brick_id": "email_property",
    "name": "Email Property",
    "description": "Email property with validation",
    "path": "foaf:mbox",
    "properties": {"datatype": "xsd:string"},
    "constraints": [
        {"constraint_type": "MinLengthConstraintComponent", "value": 5},
        {"constraint_type": "PatternConstraintComponent", "value": "^[^@]+@[^@]+\\.[^@]+$"}
    ],
    "tags": ["email", "validated"]
})
```

### Exporting SHACL

```python
# Export a brick to SHACL Turtle format
result = processor.process_event({
    "event": "export_brick_shacl",
    "brick_id": "person_nodeshape",
    "format_type": "turtle"
})

if result["status"] == "success":
    shacl_content = result["data"]["content"]
    print(shacl_content)
```

### Managing Libraries

```python
# Create a new library
result = processor.process_event({
    "event": "create_library",
    "name": "my_library",
    "description": "My custom brick library",
    "author": "User"
})

# Set active library
result = processor.process_event({
    "event": "set_active_library",
    "library_name": "my_library"
})

# Export library
result = processor.process_event({
    "event": "export_library",
    "file_path": "my_library.json"
})
```

## Testing

Run the complete test suite:

```bash
python main.py --test
```

Or run individual tests:

```python
from shacl_brick_app.tests import test_brick_generator, test_export_fix

# Run all tests
success = test_brick_generator()

# Run export fix test
success = test_export_fix()
```

## SHACL Objects Supported

### Object Types
- NodeShape, PropertyShape
- All 25 SHACL object types

### Constraint Types
- MinCountConstraintComponent
- MaxCountConstraintComponent  
- MinLengthConstraintComponent
- MaxLengthConstraintComponent
- PatternConstraintComponent
- DatatypeConstraintComponent
- ClassConstraintComponent
- NodeKindConstraintComponent

### Node Kinds
- BlankNode, IRI, Literal
- BlankNodeOrIRI, BlankNodeOrLiteral
- IRIOrLiteral

### Target Types
- TargetClass, TargetNode
- TargetObjectsOf, TargetSubjectsOf

## Project Documentation

The main project documentation is maintained in `../project_memory.md` and contains:
- Complete development history
- Architecture decisions
- Technical solutions
- Next development steps

## Step 1 Status: COMPLETE

### What's Been Accomplished
- **Full SHACL Specification Support**: 25 object types, 8 constraint types
- **Repository System**: Multiple brick libraries with persistence
- **Clean Backend API**: Event-driven architecture for any frontend
- **PyQt6 GUI**: Visual brick creation and management
- **Package Structure**: Well-organized, reusable components
- **Comprehensive Testing**: 10/10 tests passing
- **Documentation**: Complete usage examples and API reference

### Files Created
- `shacl_brick_app/core/brick_generator.py` - Core SHACL brick system
- `shacl_brick_app/core/brick_backend.py` - Backend API
- `shacl_brick_app/gui/brick_gui.py` - PyQt6 GUI
- `shacl_brick_app/tests/` - Complete test suite
- `shacl_brick_app/examples/` - Usage examples
- `run_brick_app.py` - Easy launcher script

## Next Steps

This is Step 1 of the Three-Step SHACL System:

1. **Step 1: Brick Generator** - Create reusable SHACL bricks (COMPLETED) 
2. **Step 2: Schema Construction** - Build SHACL schemas using bricks with reuse capability
3. **Step 3: Form Generation** - Generate web forms from SHACL schemas

## License

This project is part of the Three-Step SHACL Knowledge Graph Authoring System.
