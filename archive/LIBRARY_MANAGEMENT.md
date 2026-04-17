# Library Management System Documentation

## Overview

The SHACL Brick and Schema Constructor includes a comprehensive library management system that allows users to organize, save, and load bricks and schemas in custom libraries.

## Architecture

### **Storage Structure**

```
project_root/
|
|-- brick_repositories/           # Default brick libraries
|   |-- default/                  # Default brick library
|   |-- custom_library_1/         # User-defined brick library
|   |-- custom_library_2/         # Another user library
|
|-- schema_repositories/          # Default schema libraries
|   |-- default/                  # Default schema library
|   |-- project_schemas/          # User-defined schema library
|   |-- experimental/             # Experimental schemas
```

### **Library Types**

1. **Brick Libraries**: Store individual SHACL bricks
2. **Schema Libraries**: Store composed schemas and daisy chains

## Features

### **1. Library Creation and Management**

#### **Creating Custom Libraries**
- **Access**: Tools > Library Manager
- **Options**:
  - Library name (alphanumeric with underscores/hyphens)
  - Description
  - Author name
  - Custom storage path (optional)

#### **Library Operations**
- **Create**: New libraries with custom names and paths
- **Set Active**: Mark a library as the default for save operations
- **Delete**: Remove entire libraries (with confirmation)
- **List**: View all available libraries with item counts

### **2. Save/Load Functionality**

#### **Brick Operations**
```python
# Save brick to specific library
SaveLoadManager.save_brick_to_library(processor, brick_data, "my_custom_library")

# Load brick from specific library
SaveLoadManager.load_brick_from_library(processor, brick_id, "my_custom_library")
```

#### **Schema Operations**
```python
# Save schema to specific library
SaveLoadManager.save_schema_to_library(processor, schema_data, "project_schemas")

# Load schema from specific library
SaveLoadManager.load_schema_from_library(processor, schema_id, "project_schemas")
```

### **3. Import/Export**

#### **Export Library**
- **Format**: JSON archive with metadata
- **Content**: All items in library with relationships
- **Usage**: Backup, sharing between projects

#### **Import Library**
- **Format**: Previously exported library files
- **Options**: Import with new name or merge existing
- **Validation**: Checks for conflicts and duplicates

## User Interface

### **Library Manager Dialog**

#### **Main Interface**
- **Library Type Selector**: Switch between Brick/Schema libraries
- **Library List**: Shows all libraries with item counts
- **Details Panel**: Library metadata (name, description, author, path)
- **Action Buttons**: Create, Set Active, Delete

#### **Create Library Dialog**
- **Required Fields**: Name, Description
- **Optional Fields**: Author, Custom Path
- **Validation**: Name format checking, path existence

#### **Select Library Dialog**
- **Purpose**: Choose target library for save operations
- **Display**: Library names with item counts
- **Filter**: Shows only libraries of appropriate type

## Usage Workflow

### **1. Setting Up Libraries**

```bash
# Start the application
/home/heinz/.local/bin/uv run python run_schema_app.py
```

1. **Open Library Manager**: Tools > Library Manager
2. **Create Custom Library**: 
   - Click "Create New Library"
   - Enter name (e.g., "project_person_bricks")
   - Add description
   - Choose custom path if desired
3. **Set as Active**: Select library and click "Set Active"

### **2. Creating and Saving Bricks**

1. **Create Brick**: Schema > Create New Brick
2. **Configure Brick**: Use advanced editor with constraints
3. **Select Library**: Choose target library in dialog
4. **Save**: Brick saved to selected library

### **3. Building Schemas**

1. **Load Bricks**: Bricks appear from active library
2. **Compose Schema**: Drag bricks to schema workspace
3. **Configure Interface**: Set up flow and steps
4. **Save Schema**: Choose target schema library

### **4. Library Management**

#### **Switching Libraries**
1. Open Library Manager
2. Select desired library
3. Click "Set Active"
4. Application uses new library for operations

#### **Backing Up Libraries**
1. Open Library Manager
2. Select library to export
3. Choose export location
4. Library saved as JSON archive

#### **Sharing Libraries**
1. Export library to file
2. Share file with other users
3. Recipients import via Library Manager
4. Choose new name or merge option

## Advanced Features

### **1. Custom Paths**

Libraries can be stored outside the default repositories:

```python
# Custom path library
custom_path = "/shared/team_libraries/shacl_bricks"
library_info = {
    "name": "team_bricks",
    "description": "Shared team brick library",
    "author": "Team Name",
    "custom_path": custom_path
}
```

### **2. Library Templates**

Pre-configured library setups for common use cases:

- **Person Management**: Person, Address, Contact bricks
- **Product Catalog**: Product, Category, Price bricks
- **Organization**: Org, Department, Role bricks

### **3. Version Control**

Libraries support basic version tracking:

```json
{
  "library_metadata": {
    "version": "1.2.0",
    "created": "2026-04-13T16:00:00Z",
    "modified": "2026-04-13T16:30:00Z",
    "author": "User Name"
  }
}
```

## Configuration

### **Default Settings**

```python
# In schema_gui.py constructor
def __init__(self, repository_path: str = "schema_repositories"):
    # Can be overridden for custom setup
    custom_path = "/my_custom_schema_location"
    super().__init__(repository_path=custom_path)
```

### **Environment Variables**

```bash
# Set custom repository paths
export BRICK_REPOSITORIES="/data/brick_libraries"
export SCHEMA_REPOSITORIES="/data/schema_libraries"
```

## Best Practices

### **1. Library Organization**

- **By Project**: Separate libraries for each project
- **By Domain**: Person, Product, Organization libraries
- **By Status**: Development, Testing, Production libraries

### **2. Naming Conventions**

- **Library Names**: `project_domain_type` (e.g., `myapp_person_dev`)
- **Descriptive Names**: Clear indication of content and purpose
- **Version Suffixes**: `v1`, `v2` for major versions

### **3. Backup Strategy**

- **Regular Exports**: Export libraries after major changes
- **Multiple Locations**: Store backups in different directories
- **Version Control**: Track library files in version control system

### **4. Collaboration**

- **Shared Libraries**: Use network paths for team access
- **Import/Export**: Share libraries between team members
- **Documentation**: Include library purpose in description

## Troubleshooting

### **Common Issues**

#### **Library Not Loading**
- **Cause**: Invalid path or corrupted metadata
- **Solution**: Check library path, verify metadata.json exists

#### **Save Fails**
- **Cause**: No active library or permissions issue
- **Solution**: Set active library, check write permissions

#### **Import Conflicts**
- **Cause**: Duplicate names in target library
- **Solution**: Use different library name or merge option

### **Error Messages**

- **"No Libraries Available"**: Create a library first
- **"Library Name Invalid"**: Use only alphanumeric, underscores, hyphens
- **"Path Does Not Exist"**: Create directory or choose valid path

## API Reference

### **SaveLoadManager Methods**

```python
# Brick operations
SaveLoadManager.save_brick_to_library(processor, brick_data, library_name)
SaveLoadManager.load_brick_from_library(processor, brick_id, library_name)

# Schema operations
SaveLoadManager.save_schema_to_library(processor, schema_data, library_name)
SaveLoadManager.load_schema_from_library(processor, schema_id, library_name)

# Library operations
SaveLoadManager.export_library(processor, library_name, export_path, "brick")
SaveLoadManager.import_library(processor, import_path, library_name, "brick")
```

### **Event Types**

```python
# Library management
{"event": "create_library", "name": "...", "description": "...", "author": "..."}
{"event": "set_active_library", "library_name": "..."}
{"event": "delete_library", "library_name": "..."}

# Brick operations
{"event": "save_brick", "brick_data": {...}, "library_name": "..."}
{"event": "get_brick_details", "brick_id": "...", "library_name": "..."}

# Schema operations
{"event": "save_schema", "schema_data": {...}, "library_name": "..."}
{"event": "get_schema", "schema_id": "...", "library_name": "..."}

# Import/Export
{"event": "export_library", "library_name": "...", "export_path": "..."}
{"event": "import_library", "import_path": "...", "library_name": "..."}
```

## Integration Examples

### **Custom Library Setup**

```python
# Create custom library for project
library_info = {
    "name": "myproject_person_bricks",
    "description": "Person-related bricks for MyProject",
    "author": "Development Team",
    "custom_path": "/projects/myproject/libraries/person_bricks"
}

# Use in application
result = processor.process_event({
    "event": "create_library",
    **library_info
})
```

### **Batch Operations**

```python
# Save multiple bricks to library
bricks = [brick1, brick2, brick3]
for brick in bricks:
    SaveLoadManager.save_brick_to_library(processor, brick, "project_bricks")

# Export entire library
SaveLoadManager.export_library(
    processor, 
    "project_bricks", 
    "/backups/project_bricks_backup.json",
    "brick"
)
```

This comprehensive library management system provides full control over brick and schema organization, enabling efficient workflow management and collaboration.
