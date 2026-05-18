# DASH GUI v2 - Schema Construction System

**Purpose**: Complete system for creating SHACL schemas using reusable bricks.

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended for Distribution)
```bash
# Quick start with Docker (no Python setup needed)
./start-schema-app.sh          # Schema app on http://localhost:5000
./start-brick-app.sh           # Brick app on http://localhost:5001

# Or run both simultaneously
./start-schema-app.sh &
./start-brick-app.sh &
```

### Option 2: Local Development (5-Minute Quick Start)
```bash
# 1. System check
python3 run_tasks.py setup

# 2. Launch interface
python3 run_tasks.py qt        # Desktop (PyQt6)
# OR
python3 run_tasks.py dash       # Web (DASH)
# OR
uv run python run_schema_app_web.py --port 5003  # Web (Flask + React)

# 3. Create first schema
# Follow interface instructions or see: docs/QUICK_START.md
```

### Option 3: Web Frontend (Vite + React)
```bash
# Build the web frontend (one-time setup)
./build-web-frontend.sh

# Or manually:
cd schema_app_v2/interfaces/web
npm install
npm run build

# Run Flask backend
uv run python run_schema_app_web.py --port 5003
# Access: http://localhost:5003
```

## 📚 Complete Documentation

**All documentation is now centralized in the `docs/` directory:**

### User Documentation
- **📖 Quick Start**: `docs/QUICK_START.md` - Get started in 5 minutes
- **📖 User Guide**: `docs/USER_GUIDE.md` - Complete manual for all features
- **🔍 Pattern Presets**: `docs/PATTERN_PRESETS.md` - Regex validation patterns guide
- **🔧 Troubleshooting**: `docs/TROUBLESHOOTING.md` - Solutions to common issues

### System Documentation
- **📊 System Status**: `docs/README_V2_STATUS.md` - Architecture and current status
- **🚀 Task Management**: `docs/TASK_MANAGER.md` - Centralized operations guide

### Developer Documentation
- **🧱 Brick Building**: `docs/BRICK_BUILDING_GUIDE.md` - Brick creation guide
- **⚙️ Development Setup**: `docs/DEVELOPMENT.md` - IDE, Docker, local setup
- **🗺️ Roadmap**: `docs/ROADMAP.md` - Future features and enhancements

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
- **🐳 Docker Web**: Containerized deployment (no dependencies)
- **🖥️ PyQt6 Desktop**: Native desktop application
- **📊 DASH Web**: Interactive web interface (local)
- **🔄 Flask Web**: Flask-based web API

### Repositories
- **brick_repositories/**: Active brick library (7 bricks available)
- **schema_repositories/**: Schema storage
- **ontologies/**: Ontology cache for brick system

## 📋 Current Status

✅ **Ready for Testing**:
- Docker deployment (web-only, no Qt dependencies)
- PyQt6 interface working
- **Flask/React web interface working** (May 2026)
- DASH web interface available
- 7 bricks loading successfully
- Task management centralized
- Complete documentation suite

✅ **Features Available**:
- Schema creation and editing (Qt + Web)
- Brick integration and management (Qt + Web)
- SHACL export functionality (Qt + Web)
- Flow configuration
- Library management
- Multi-interface support (Qt, Flask/React, DASH, Docker)

### 🆕 Web Frontend Updates (May 2026)
- **Modular React architecture** with Vite build system
- **Component names display correctly** (fetched from API)
- **Tree view** with hierarchical structure
- **Groups and schema refs** support
- **Build script**: `./build-web-frontend.sh`

## 🐳 Docker Deployment

### Prerequisites
- Docker installed on your system

### Quick Start (Docker Hub - No Build Required)
If you have a Docker Hub account or use a published image:
```bash
# Pull and run published image (replace with your Docker Hub username)
./start-schema-app.sh 5000 hapdocker/dash-gui:latest

# Or directly with docker
docker run -p 5000:5000 -v "$(pwd)/shared_libraries:/app/shared_libraries" hapdocker/dash-gui:latest
```

### Quick Start
```bash
# Build and start Schema App
./start-schema-app.sh
# → http://localhost:5000

# Build and start Brick App
./start-brick-app.sh  
# → http://localhost:5001

# Or use docker-compose for both
docker-compose up -d
```

### Docker Files
- `Dockerfile` - Multi-stage build (web-only, ~100MB)
- `docker-compose.yml` - Both apps with volume persistence
- `docker-entrypoint.sh` - App selection script
- `start-schema-app.sh` - Quick start for Schema App
- `start-brick-app.sh` - Quick start for Brick App

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

# Web interface (Flask)
.venv/bin/python run_schema_app_web.py

# Web interface (DASH)
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
├── shared_libraries/          # Brick & schema libraries (bundled DigiPass)
├── Dockerfile                 # Docker build (web-only)
├── docker-compose.yml         # Docker Compose config
├── start-schema-app.sh       # Quick start: Schema App
├── start-brick-app.sh        # Quick start: Brick App
├── run_tasks.py              # Centralized task runner
├── run_schema_app_web.py     # Web launcher (Flask)
└── run_brick_app_web.py      # Web launcher (Flask)
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

# Development setup
cat docs/DEVELOPMENT.md

# Future features
cat docs/ROADMAP.md
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
