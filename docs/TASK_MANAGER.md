# V2 Task Manager - Centralized Running Tasks

**Purpose**: Single place to manage all running tasks, services, and processes for version 2 applications.

## Current Available Tasks

### 🖥️ Interface Launchers
```bash
# PyQt6 Desktop Interface (Primary)
source .venv/bin/activate
python3 run_schema_app_v2.py

# Flask Web Interface (Future)
source .venv/bin/activate
python3 -m schema_app_v2.interfaces.web.flask_app

# DASH Interactive Web Interface
source .venv/bin/activate
python3 -m schema_app_v2.interfaces.web.dash_app
```

### 📊 Service Management
```bash
# Check running processes
ps aux | grep python

# Stop all python processes
pkill -f python

# Check port usage
netstat -tlnp | grep :8050  # DASH default
netstat -tlnp | grep :5000  # Flask default
```

### 🔧 Development Tasks
```bash
# Run tests
source .venv/bin/activate
python3 -m pytest schema_app_v2/tests/

# Check dependencies
source .venv/bin/activate
pip list

# Update dependencies
source .venv/bin/activate
pip install -r pyproject.toml
```

## Task Status Dashboard

### ✅ Ready Tasks
- [x] PyQt6 Interface - Ready to launch
- [x] Flask Interface - Code ready
- [x] DASH Interface - Code ready
- [x] Virtual Environment - Configured
- [x] Dependencies - Installed
- [x] Brick Repository - 7 bricks available
- [x] Schema Repository - Ready

### 🔄 Running Tasks
- [ ] PyQt6 GUI - Launch with `python3 run_schema_app_v2.py`
- [ ] DASH Web - Launch with `python3 -m schema_app_v2.interfaces.web.dash_app`

### 📋 Maintenance Tasks
- [ ] Clean cache files
- [ ] Backup repositories
- [ ] Update documentation
- [ ] Performance testing

## Quick Commands Reference

```bash
# Activate environment
source .venv/bin/activate

# Main launcher
python3 run_schema_app_v2.py

# Web interfaces
python3 -m schema_app_v2.interfaces.web.flask_app
python3 -m schema_app_v2.interfaces.web.dash_app

# Check status
python3 -c "
from schema_app_v2.core.brick_integration import BrickIntegration
from schema_app_v2.core.schema_core import SchemaCore
bi = BrickIntegration('brick_repositories')
sc = SchemaCore('schema_repositories')
print(f'Bricks: {len(bi.get_available_bricks())}')
print(f'Schemas: {len(sc.get_all_schemas())}')
"
```

## Environment Setup Checklist

### Before Starting Tasks
- [ ] Virtual environment activated: `source .venv/bin/activate`
- [ ] Dependencies verified: `pip list`
- [ ] Repositories accessible: Check `brick_repositories/` and `schema_repositories/`
- [ ] Ports available: Check 8050 (DASH), 5000 (Flask)

### After Running Tasks
- [ ] Save work properly
- [ ] Close interfaces gracefully
- [ ] Check for errors in logs
- [ ] Backup important data

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure virtual environment is activated
2. **Port Conflicts**: Check with `netstat -tlnp`
3. **Missing Dependencies**: Run `pip install -r pyproject.toml`
4. **Permission Issues**: Use `source .venv/bin/activate`

### Log Locations
- PyQt6: Console output
- Flask: Console output
- DASH: Console output + browser console

---

**Usage**: This file serves as the central reference for all V2 running tasks and processes.

## Usage Examples

### 🚀 Quick Start Guide
\`\`\`bash
# 1. Check system status
python3 run_tasks.py status

# 2. Launch PyQt6 interface (recommended for beginners)
python3 run_tasks.py qt

# 3. Launch DASH web interface (interactive)
python3 run_tasks.py dash

# 4. Check what's running
python3 run_tasks.py ps
\`\`\`

### 📊 Development Workflow
\`\`\`bash
# Morning setup
python3 run_tasks.py setup

# Start development
python3 run_tasks.py qt

# Test changes
python3 run_tasks.py test

# Check web services
python3 run_tasks.py ports

# Clean shutdown
python3 run_tasks.py stop
\`\`\`

### 🔧 Advanced Usage
\`\`\`bash
# Multiple interfaces (different terminals)
python3 run_tasks.py qt &      # Background desktop
python3 run_tasks.py dash &     # Background web

# Process monitoring
watch -n 5 'python3 run_tasks.py ps'     # Every 5 seconds

# Port monitoring
watch -n 2 'python3 run_tasks.py ports'    # Every 2 seconds
\`\`\`

## Troubleshooting Guide

### 🚨 Common Issues & Solutions

#### Interface Won't Start
\`\`\`bash
# Check environment
python3 run_tasks.py setup

# Manually activate
source .venv/bin/activate
python3 run_schema_app_v2.py
\`\`\`

#### Port Already in Use
\`\`\`bash
# Find process using port
lsof -i :8050    # DASH default
lsof -i :5000    # Flask default

# Kill specific process
kill -9 <PID>

# Use different port (edit dash_app.py)
app.run_server(port=8051)
\`\`\`

#### Virtual Environment Issues
\`\`\`bash
# Recreate venv
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r pyproject.toml
\`\`\`

#### Import Errors
\`\`\`bash
# Check all dependencies
python3 run_tasks.py setup

# Install missing packages
source .venv/bin/activate
pip install dash plotly pandas PyQt6 flask
\`\`\`

### 📋 Performance Monitoring

#### Memory Usage
\`\`\`bash
# Monitor Python processes
ps aux | grep python | awk '{print $4, $11}'

# Check system resources
htop
\`\`\`

#### Log Monitoring
\`\`\`bash
# Monitor logs in real-time
tail -f /tmp/schema_app_*.log

# Check error logs
find . -name "*.log" -exec tail -n 20 {} \;
\`\`\`

## Integration with IDE

### PyCharm Integration
1. **Run Configuration**: Add "Python" run configuration
   - Script: \`run_tasks.py\`
   - Parameters: \`qt\` or \`dash\`
   - Working directory: \`$PROJECT_DIR$\`

2. **Debug Configuration**: 
   - Script: \`run_tasks.py\`
   - Parameters: \`qt\`
   - Environment: Add \`PYTHONPATH=$PROJECT_DIR$\`

### VS Code Integration
\`\`\`json
// .vscode/tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Launch PyQt6",
            "type": "shell",
            "command": "python3 run_tasks.py qt",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Launch DASH",
            "type": "shell",
            "command": "python3 run_tasks.py dash",
            "group": "build"
        }
    ]
}
\`\`\`

## API Reference

### run_tasks.py Commands
| Command | Description | Example |
|---------|-------------|---------|
| \`status\` | Show system status | \`python3 run_tasks.py status\` |
| \`qt\`, \`pyqt6\` | Launch PyQt6 desktop | \`python3 run_tasks.py qt\` |
| \`flask\` | Launch Flask web interface | \`python3 run_tasks.py flask\` |
| \`dash\` | Launch DASH interactive web | \`python3 run_tasks.py dash\` |
| \`stop\` | Stop all Python processes | \`python3 run_tasks.py stop\` |
| \`ps\`, \`status\` | Check running processes | \`python3 run_tasks.py ps\` |
| \`ports\` | Check web service ports | \`python3 run_tasks.py ports\` |
| \`test\` | Run system tests | \`python3 run_tasks.py test\` |
| \`setup\` | Verify environment setup | \`python3 run_tasks.py setup\` |

### Environment Variables
\`\`\`bash
# Custom repository paths
export BRICK_REPO_PATH="/custom/brick/path"
export SCHEMA_REPO_PATH="/custom/schema/path"

# Custom ports
export DASH_PORT=8051
export FLASK_PORT=5001

# Custom virtual environment
export VENV_PATH="/custom/venv"
\`\`\`

---

**Usage**: This file serves as a central reference for all V2 running tasks and processes, with comprehensive documentation, examples, and troubleshooting guides.
