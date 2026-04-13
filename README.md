# DASH_GUI - Three-Step SHACL Knowledge Graph Authoring System

A comprehensive system for creating SHACL knowledge graphs through a three-step approach:
1. **Step 1**: SHACL Brick Generator - Create reusable SHACL bricks
2. **Step 2**: Schema Construction - Build SHACL schemas using bricks
3. **Step 3**: Form Generation - Generate web forms from SHACL schemas

## Current Status

### Step 1: SHACL Brick Generator - COMPLETED
Located in `shacl_brick_app/` - A complete, production-ready SHACL brick generation system.

**Features:**
- Full SHACL specification support (25 object types, 8 constraint types)
- Multiple brick libraries with repository system
- PyQt6 GUI for visual brick creation and management
- Clean backend API with frontend/backend separation
- Export to SHACL Turtle format
- Comprehensive test suite

**Quick Start:**
```bash
# Run the GUI
python run_brick_app.py --gui

# Run tests
python run_brick_app.py --test
```

### Step 2: Schema Construction - PENDING
Will allow building complete SHACL schemas using bricks with reuse capability.

### Step 3: Form Generation - PENDING  
Will generate web forms from SHACL schemas created in Step 2.

## Project Structure

```
DASH_GUI/
|
|__ shacl_brick_app/         # Step 1: Complete SHACL Brick Generator
|   |__ bricks.py            # Main entry point
|   |__ core/                # Backend components
|   |__ gui/                 # PyQt6 frontend
|   |__ tests/               # Test suite
|   |__ examples/            # Usage examples
|   |__ README.md            # Detailed documentation
|
|__ run_brick_app.py         # Easy launcher for Step 1
|__ project_memory.md        # Main project documentation
|__ archive/                 # Archived old files
|
|__ .venv/                   # Virtual environment
|__ pyproject.toml           # Python project configuration
|__ uv.lock                  # Dependency lock file
```

## Documentation

- **Main Project**: `project_memory.md` - Complete development history and architecture
- **Step 1 Guide**: `shacl_brick_app/README.md` - Detailed usage instructions
- **Examples**: `shacl_brick_app/examples/` - Usage examples

## Development History

This project evolved from initial SHACL experiments to a complete three-step system:
1. Started with basic SHACL form generation
2. Developed comprehensive brick generation system
3. Created clean package structure with GUI
4. Ready for Step 2 schema construction

## Next Steps

1. **Step 2 Implementation**: Build schema construction system using bricks
2. **Step 3 Implementation**: Create form generation from schemas
3. **Integration**: Connect all three steps into complete workflow

## Dependencies

- PyQt6 - GUI framework
- RDFLib - RDF/SHACL processing
- Python 3.8+

## License

Part of the Three-Step SHACL Knowledge Graph Authoring System.
