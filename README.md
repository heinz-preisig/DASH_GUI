# DASH GUI v2 - Schema Construction System

**Purpose**: Complete system for creating SHACL schemas using reusable bricks.

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended for Distribution)
```bash
# Quick start with Docker (no Python setup needed)
./dev-start-schema-docker.sh          # Schema app on http://localhost:5000
./dev-start-brick-docker.sh           # Brick app on http://localhost:5001

# Or run both simultaneously
./dev-start-schema-docker.sh &
./dev-start-brick-docker.sh &
```

### Option 2: Local Development (5-Minute Quick Start)
```bash
# Desktop interface (PyQt6)
uv run python run_brick_app_qt.py

# Web interface (Flask)
uv run python run_schema_app_web.py --port 5000
uv run python run_brick_app_web.py --port 5001

# 3. Create first schema
# Follow interface instructions or see: docs/QUICK_START.md
```

### Option 3: Web Frontend (Vite + React)
```bash
# Build the web frontend (one-time setup)
./dev-build-frontend-web.sh

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

## 🎯 Launch Commands

```bash
# Desktop interface
uv run python run_brick_app_qt.py       # Brick editor (PyQt6)
uv run python run_schema_app_qt.py      # Schema editor (PyQt6)

# Web interface
uv run python run_brick_app_web.py      # Brick app → http://localhost:5001
uv run python run_schema_app_web.py     # Schema app → http://localhost:5000

# Docker
./dev-start-schema-docker.sh            # Schema app in Docker → http://localhost:5000
./dev-start-brick-docker.sh             # Brick app in Docker → http://localhost:5001
```

## 🏗️ Architecture

### Core Components
- **brick_app_v2/**: Core brick management system
- **schema_app_v2/**: Schema construction and management
- **common/**: Shared library management
- **docs/**: Complete documentation suite

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
- **Build script**: `./dev-build-frontend-web.sh`

## 🐳 Docker Deployment

### Prerequisites
- Docker installed on your system

### Quick Start
```bash
# Build and start Schema App
./dev-start-schema-docker.sh
# → http://localhost:5000

# Build and start Brick App
./dev-start-brick-docker.sh
# → http://localhost:5001

# Or use docker-compose for both
docker-compose up -d
```

### Docker Files
- `Dockerfile` - Multi-stage build (web-only, ~100MB)
- `docker-compose.yml` - Both apps with volume persistence
- `docker-entrypoint.sh` - App selection script
- `dev-start-schema-docker.sh` - Quick start for Schema App
- `dev-start-brick-docker.sh` - Quick start for Brick App

## 🔧 Development Setup

### Virtual Environment (uv)
```bash
# Install uv if not present
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

### Quick Launch Commands
```bash
# Desktop interface
uv run python run_brick_app_qt.py
uv run python run_schema_app_qt.py

# Web interface (Flask)
uv run python run_schema_app_web.py
uv run python run_brick_app_web.py
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
├── Dockerfile                       # Docker build (web-only)
├── docker-compose.yml               # Docker Compose config
├── dev-start-schema-docker.sh       # Quick start: Schema App in Docker
├── dev-start-brick-docker.sh        # Quick start: Brick App in Docker
├── run_schema_app_web.py            # Web launcher: Schema App (Flask)
├── run_brick_app_web.py             # Web launcher: Brick App (Flask)
├── run_schema_app_qt.py             # Desktop launcher: Schema App
└── run_brick_app_qt.py              # Desktop launcher: Brick App
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
# Check imports and environment
uv run python -c "from brick_app_v2.core.brick_core_simple import BrickCore; print('OK')"
```

---

**Complete system for SHACL schema construction with reusable bricks, multiple interface options, and centralized documentation.**
