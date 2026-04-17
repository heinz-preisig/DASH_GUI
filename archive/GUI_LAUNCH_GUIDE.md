# SHACL Brick Generator - GUI Launch Guide

## Available Interfaces

The SHACL Brick Generator now offers multiple interfaces for different user needs and expertise levels.

### 1. Technical Interface (Original)
**For:** SHACL experts who want full control
**Features:** Complete SHACL specification access, technical terminology
```bash
python launch_gui.py
```

### 2. User-Friendly Interface
**For:** Non-SHACL experts, beginners
**Features:** Simple primitives, intuitive constraints, plain language
```bash
python launch_easy_gui.py
```

### 3. Combined Interface (Recommended)
**For:** Users who want both simplicity and advanced features
**Features:** Mode switching between user-friendly and technical
```bash
python launch_combined_gui.py
```

### 4. TopBraid-Inspired Advanced Interface
**For:** Power users, semantic web professionals
**Features:** Visual schema design, ontology integration, advanced validation
```bash
python launch_topbraid_gui.py
```

## Interface Comparison

| Feature | Technical | User-Friendly | Combined | TopBraid |
|---------|-----------|---------------|----------|----------|
| **Ease of Use** | Low | High | Medium | Medium |
| **SHACL Knowledge** | Required | None Required | Optional | Recommended |
| **Visual Design** | Basic | Simple | Moderate | Advanced |
| **Ontology Support** | Limited | Basic | Basic | Full |
| **Validation** | Basic | Basic | Basic | Advanced |
| **Export Options** | Standard | Standard | Standard | Multiple |
| **Editing** | Full | Full | Full | Full |
| **Mode Switching** | No | No | Yes | No |

## TopBraid-Inspired Features

### Advanced Capabilities:
- **Visual Schema Editor**: Drag-and-drop class and property design
- **Constraint Builder**: Visual constraint composition with templates
- **Ontology Integration**: Import FOAF, Schema.org, DCTERMS
- **Project Management**: Save/load complete projects
- **Validation Engine**: Real-time validation with detailed reports
- **Test Data Input**: Validate with sample data
- **Multiple Export Formats**: Turtle, RDF/XML, JSON-LD

### Interface Components:
- **Project Explorer**: Hierarchical view of classes, properties, constraints
- **Workspace Tabs**: Schema Editor, Constraint Builder, Validation, Test Data
- **Properties Panel**: Detailed brick properties, constraints, metadata
- **Menu System**: Complete file operations, tools, help
- **Toolbar**: Quick access to common actions

## Recommended Usage

### For Beginners:
1. Start with **User-Friendly Interface** (`launch_easy_gui.py`)
2. Learn basic brick creation concepts
3. Progress to **Combined Interface** when comfortable

### For Intermediate Users:
1. Use **Combined Interface** (`launch_combined_gui.py`)
2. Start in user-friendly mode
3. Switch to technical mode for advanced features
4. Use editing capabilities to refine bricks

### For Experts:
1. Use **Technical Interface** (`launch_gui.py`) for direct SHACL access
2. Or use **TopBraid Interface** (`launch_topbraid_gui.py`) for advanced features
3. Leverage ontology integration and visual design tools

## Quick Start Examples

### Create a Simple Person Brick:
```bash
# Launch user-friendly interface
python launch_easy_gui.py

# 1. Select "Entity/Class Shape"
# 2. Enter "Person" as name
# 3. Enter "Basic person entity" as description
# 4. Click "Create Brick"
```

### Create an Email Property with Validation:
```bash
# Launch combined interface
python launch_combined_gui.py

# 1. Start in User-Friendly mode
# 2. Select "Property/Field Shape"
# 3. Enter "Email" as name
# 4. Select "Email" as data type
# 5. Check "Required field"
# 6. Enter email pattern in "Pattern (regex)"
# 7. Click "Create Brick"
```

### Advanced Schema Design:
```bash
# Launch TopBraid interface
python launch_topbraid_gui.py

# 1. Import ontologies (FOAF, Schema.org)
# 2. Create classes in visual schema editor
# 3. Add properties with constraints
# 4. Validate with test data
# 5. Export schema in multiple formats
```

## File Locations

All interfaces share the same brick repository:
- **Repository Location**: `default_brick_repository/`
- **Active Library**: `default_brick_repository/default/`
- **Brick Files**: `default_brick_repository/default/bricks/*.json`

This means bricks created in any interface are available in all other interfaces.

## Next Steps

After creating bricks in Step 1, you'll be ready for:
- **Step 2: Schema Construction** - Build complete schemas using bricks
- **Step 3: Form Generation** - Generate web forms from schemas

Choose the interface that best matches your expertise level and requirements!
