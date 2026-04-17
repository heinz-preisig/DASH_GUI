# Troubleshooting Guide - DASH GUI v2

**Purpose**: Solutions to common issues and problems with DASH GUI v2.

## 🚨 Quick Issues Index

### Installation & Setup
- [Virtual Environment Issues](#virtual-environment-issues)
- [Dependency Problems](#dependency-problems)
- [Permission Errors](#permission-errors)

### Interface Issues
- [Interface Won't Start](#interface-wont-start)
- [Bricks Not Loading](#bricks-not-loading)
- [Save Failures](#save-failures)
- [Web Interface Problems](#web-interface-problems)

### Schema Issues
- [Validation Errors](#validation-errors)
- [Export Problems](#export-problems)
- [Flow Configuration Issues](#flow-configuration-issues)

## Installation & Setup

### Virtual Environment Issues

#### Problem: Virtual Environment Not Found
**Error**: `Error: .venv not found`
**Causes**: 
- Virtual environment not created
- Running from wrong directory

**Solutions**:
```bash
# Create virtual environment
python3 -m venv .venv

# Activate environment
source .venv/bin/activate

# Verify activation
which python3
```

#### Problem: Dependencies Missing
**Error**: `ModuleNotFoundError: No module named 'xxx'`
**Causes**:
- Dependencies not installed
- Wrong virtual environment activated

**Solutions**:
```bash
# Install all dependencies
source .venv/bin/activate
pip install -r pyproject.toml

# Install specific package
pip install PyQt6 dash plotly pandas

# Check installed packages
pip list
```

#### Problem: Permission Errors
**Error**: `Permission denied` or `externally-managed-environment`
**Causes**:
- System Python package management
- File permission issues

**Solutions**:
```bash
# Use user installation
pip install --user package-name

# Use --break-system-packages (if necessary)
pip install --break-system-packages package-name

# Fix file permissions
chmod +x script_name.py
```

## Interface Issues

### Interface Won't Start

#### Problem: PyQt6 Interface Fails
**Error**: `ImportError: No module named 'PyQt6'`
**Causes**:
- PyQt6 not installed
- Wrong virtual environment
- Python version incompatibility

**Solutions**:
```bash
# Check system requirements
python3 run_tasks.py setup

# Install PyQt6
source .venv/bin/activate
pip install PyQt6

# Use system PyQt6 (if available)
export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH
python3 run_schema_app_v2.py
```

#### Problem: Web Interface Not Accessible
**Error**: `Connection refused` or `404 Not Found`
**Causes**:
- Port already in use
- Firewall blocking
- Service not running

**Solutions**:
```bash
# Check what's running
python3 run_tasks.py ps

# Check port usage
python3 run_tasks.py ports

# Kill conflicting processes
python3 run_tasks.py stop

# Use different port
# Edit dash_app.py: app.run_server(port=8051)
```

### Bricks Not Loading

#### Problem: No Bricks in List
**Error**: Brick list shows empty or "No bricks found"
**Causes**:
- Wrong repository path
- Corrupted brick files
- Invalid JSON format

**Solutions**:
```bash
# Check repository structure
ls -la brick_repositories/default/bricks/

# Verify brick files
python3 -c "
import json
for file in ['brick1.json', 'brick2.json']:
    try:
        with open(file) as f:
            data = json.load(f)
            print(f'{file}: Valid JSON')
    except:
        print(f'{file}: Invalid JSON')
"

# Check brick format
python3 -c "
from schema_app_v2.core.brick_integration import BrickIntegration
bi = BrickIntegration('brick_repositories')
try:
    bricks = bi.get_available_bricks()
    print(f'Found {len(bricks)} bricks')
    for brick in bricks[:3]:
        print(f'  - {brick.name} ({brick.object_type})')
except Exception as e:
    print(f'Error: {e}')
"
```

#### Problem: Brick Import Errors
**Error**: `Failed to load brick: xxx`
**Causes**:
- Missing required fields in brick JSON
- Invalid data types
- Corrupted brick files

**Solutions**:
```bash
# Validate brick format
python3 -c "
import json
import os

def validate_brick(file_path):
    try:
        with open(file_path) as f:
            data = json.load(f)
        required = ['brick_id', 'name', 'description', 'object_type']
        missing = [field for field in required if field not in data]
        if missing:
            print(f'{file_path}: Missing fields: {missing}')
            return False
        print(f'{file_path}: Valid brick')
        return True
    except Exception as e:
        print(f'{file_path}: Error - {e}')
        return False

# Validate all bricks
import os
brick_dir = 'brick_repositories/default/bricks'
for file in os.listdir(brick_dir):
    if file.endswith('.json'):
        validate_brick(os.path.join(brick_dir, file))
"
```

### Save Failures

#### Problem: Schema Won't Save
**Error**: `Save failed` or validation errors
**Causes**:
- Missing required fields
- Invalid data in fields
- File permission issues

**Solutions**:
```bash
# Check schema validation
python3 -c "
from schema_app_v2.core.schema_core import SchemaCore
sc = SchemaCore()

# Test validation
try:
    schema = sc.create_schema('test', 'test description', 'test_brick')
    if sc.save_schema(schema):
        print('Save validation passed')
    else:
        print('Save validation failed')
except Exception as e:
    print(f'Validation error: {e}')
"

# Check file permissions
ls -la schema_repositories/default/schemas/

# Fix permissions
chmod 755 schema_repositories/default/schemas/
```

#### Problem: Export Failures
**Error**: `Export failed` or empty SHACL files
**Causes**:
- Invalid schema structure
- Missing target classes
- Export path issues

**Solutions**:
```bash
# Test export functionality
python3 -c "
from schema_app_v2.core.shacl_export import SHACLExporter
from schema_app_v2.core.schema_core import SchemaCore
from schema_app_v2.core.brick_integration import BrickIntegration

# Create test schema
sc = SchemaCore()
bi = BrickIntegration('brick_repositories')
schema = sc.create_schema('test', 'test', 'test_brick')

# Test export
exporter = SHACLExporter()
try:
    ttl_content = exporter.export_schema(schema)
    print('Export successful')
    print(f'Content length: {len(ttl_content)} characters')
except Exception as e:
    print(f'Export failed: {e}')
"
```

## Schema Issues

### Validation Errors

#### Problem: Target Class Required
**Error**: `"Target class is required for NodeShape"`
**Causes**:
- NodeShape brick missing target_class
- Empty target_class field
- Validation logic issues

**Solutions**:
```bash
# Check brick target classes
python3 -c "
from schema_app_v2.core.brick_integration import BrickIntegration
bi = BrickIntegration('brick_repositories')
bricks = bi.get_node_shape_bricks()
for brick in bricks:
    print(f'{brick.name}: target_class = \"{brick.target_class}\"')
    if not brick.target_class:
        print(f'  -> MISSING TARGET CLASS')
"

# Fix brick files
# Edit brick JSON files to include target_class
# Example: \"target_class\": \"foaf:Person\"
```

#### Problem: Invalid Property Paths
**Error**: `"Invalid property path"` or similar
**Causes**:
- Incorrect URI format
- Missing namespace prefixes
- Invalid property names

**Solutions**:
```bash
# Validate property paths
python3 -c "
# Common namespace prefixes
prefixes = {
    'foaf': 'http://xmlns.com/foaf/0.1/',
    'schema': 'http://schema.org/',
    'dc': 'http://purl.org/dc/elements/1.1/'
}

def validate_property_path(path):
    if ':' not in path:
        return False, 'Missing namespace'
    prefix, name = path.split(':', 1)
    if prefix not in prefixes:
        return False, f'Unknown namespace: {prefix}'
    return True, 'Valid'

# Test paths
test_paths = [
    'foaf:name',
    'schema:email', 
    'dc:title'
]

for path in test_paths:
    valid, msg = validate_property_path(path)
    print(f'{path}: {\"Valid\" if valid else msg}')
"
```

## Performance Issues

### Slow Interface

#### Problem: Interface Response Slow
**Causes**:
- Large repository with many bricks
- Memory constraints
- Inefficient data loading

**Solutions**:
```bash
# Monitor performance
htop  # Check memory/CPU usage
iotop  # Check disk I/O

# Optimize repository
# Keep only necessary bricks in active repository
# Archive unused bricks

# Increase memory limits
export PYTHONMALLOC=malloc_debug
python3 run_tasks.py qt
```

### Memory Issues

#### Problem: Out of Memory Errors
**Error**: `MemoryError` or application crashes
**Causes**:
- Large schemas
- Memory leaks
- Limited system resources

**Solutions**:
```bash
# Check memory usage
free -h
ps aux | grep python3 | head -5

# Increase swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Use memory-efficient settings
export PYTHONOPTIMIZE=2
python3 run_tasks.py qt
```

## Getting Help

### Diagnostic Commands
```bash
# Full system check
python3 run_tasks.py setup

# Check logs
tail -f ~/.local/share/schema_app_*.log

# Generate debug report
python3 run_tasks.py test > debug_report.txt 2>&1
```

### Contact & Support
- **Documentation**: `docs/` directory
- **Task Manager**: `python3 run_tasks.py --help`
- **Status Check**: `python3 run_tasks.py status`

### Report Issues
When reporting issues, include:
1. **System Information**: Output of `python3 run_tasks.py setup`
2. **Error Messages**: Full error text and screenshots
3. **Steps to Reproduce**: What you were doing when error occurred
4. **Expected Behavior**: What you expected to happen
5. **Actual Behavior**: What actually happened

---

**Comprehensive troubleshooting guide for DASH GUI v2 - solutions to common problems and diagnostic procedures.**
