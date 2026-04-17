# DASH GUI v2 - Schema Construction System

**Purpose**: Complete system for creating SHACL schemas using reusable bricks.

## 🚀 Quick Start

### 5-Minute Quick Start
```bash
# 1. System check
python3 run_tasks.py setup

# 2. Launch interface
python3 run_tasks.py qt        # Desktop
# OR
python3 run_tasks.py dash       # Web

# 3. Create first schema
# Follow interface instructions or see: docs/QUICK_START.md
```

## 📚 Complete Documentation

**All documentation is now centralized in the `docs/` directory:**

### User Documentation
- **📖 Quick Start**: `docs/QUICK_START.md` - Get started in 5 minutes
- **📖 User Guide**: `docs/USER_GUIDE.md` - Complete manual for all features
- **🔧 Troubleshooting**: `docs/TROUBLESHOOTING.md` - Solutions to common issues

### System Documentation
- **📊 System Status**: `docs/README_V2_STATUS.md` - Architecture and current status
- **🚀 Task Management**: `docs/TASK_MANAGER.md` - Centralized operations guide

### Developer Documentation
- **🧱 Brick Building**: `BRICK_BUILDING_GUIDE.md` - Brick creation guide
- **⚙️ Development Setup**: `PYCHARM_SETUP.md` - IDE configuration

## 🎯 Task Management

**All operations are centralized through the task manager:**
```bash
python3 run_tasks.py status    # System status
python3 run_tasks.py qt        # PyQt6 desktop interface
python3 run_tasks.py dash       # DASH web interface
python3 run_tasks.py setup     # Environment check
python3 run_tasks.py stop      # Stop all processes
```

## 🏗️ Architecture

### Core Components
- **brick_app_v2/**: Core brick management system
- **schema_app_v2/**: Schema construction and management
- **docs/**: Complete documentation suite
- **run_tasks.py**: Centralized task runner

### Interface Options
- **🖥️ PyQt6 Desktop**: Native desktop application
- **📊 DASH Web**: Interactive web interface
- **🔄 Flask Web**: Basic web interface (future)

### Repositories
- **brick_repositories/**: Active brick library (7 bricks available)
- **schema_repositories/**: Schema storage
- **ontologies/**: Ontology cache for brick system

## 📋 Current Status

✅ **Ready for Testing**:
- PyQt6 interface working
- DASH web interface available
- 7 bricks loading successfully
- Task management centralized
- Complete documentation suite

✅ **Features Available**:
- Schema creation and editing
- Brick integration and management
- SHACL export functionality
- Flow configuration
- Library management
- Multi-interface support

## 🔧 Development Setup

### Virtual Environment
```bash
# Create and activate
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r pyproject.toml
```

### Quick Launch Commands
```bash
# Desktop interface
python3 run_tasks.py qt

# Web interface
python3 run_tasks.py dash

# System status
python3 run_tasks.py status
```

## 📁 Project Structure

```
DASH_GUI/
├── 📚 docs/                   # Complete documentation suite
│   ├── README.md             # Documentation index
│   ├── QUICK_START.md        # 5-minute quick start
│   ├── USER_GUIDE.md         # Complete user manual
│   ├── TROUBLESHOOTING.md    # Common issues & solutions
│   ├── README_V2_STATUS.md  # System status & architecture
│   └── TASK_MANAGER.md       # Task management guide
├── brick_app_v2/              # Core brick management system
├── schema_app_v2/             # Schema construction system
├── brick_repositories/          # Active brick library
├── schema_repositories/        # Schema storage
├── ontologies/               # Ontology cache
├── run_tasks.py              # Centralized task runner
├── run_schema_app_v2.py       # Main launcher
└── archive/                  # Legacy components
```

## 🎯 Getting Help

### Documentation
```bash
# Quick start
cat docs/QUICK_START.md

# Complete guide
cat docs/USER_GUIDE.md

# Troubleshooting
cat docs/TROUBLESHOOTING.md
```

### System Commands
```bash
# All available commands
python3 run_tasks.py --help

# Current status
python3 run_tasks.py status

# Environment check
python3 run_tasks.py setup
```

---

**Complete system for SHACL schema construction with reusable bricks, multiple interface options, and centralized documentation.**
