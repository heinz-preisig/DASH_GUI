# Quick Start Guide - DASH GUI v2

**Purpose**: Get started with DASH GUI v2 in 5 minutes

## 🚀 Quick Start Options

### Option A: Docker (No Python Setup Required)
```bash
# Start Schema App
./dev-start-schema-docker.sh
# → Open http://localhost:5000

# Start Brick App (in another terminal)
./dev-start-brick-docker.sh
# → Open http://localhost:5001
```

### Option B: Local Development

#### Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager

#### Quick Setup
```bash
uv sync
```

## 🎯 5-Minute Quick Start (Local)

### Step 1: Launch Interface (30 seconds)
```bash
# PyQt6 Desktop (Recommended)
uv run python run_schema_app_qt.py    # Schema editor
uv run python run_brick_app_qt.py     # Brick editor

# OR Web Interface (Flask)
uv run python run_schema_app_web.py   # → http://localhost:5000
uv run python run_brick_app_web.py    # → http://localhost:5001
```

### Step 2: Create First Schema (2 minutes)
1. Click "New Schema" in the interface
2. Enter schema name (e.g., "My First Schema")
3. Select root brick from dropdown
4. Click "Create"

### Step 3: Add Components (2 minutes)
1. Browse available bricks in the brick list
2. Double-click property bricks to add them
3. Watch your schema build automatically

### Step 4: Save & Export (1 minute)
1. Click "Save Schema" to save your work
2. Click "Export SHACL" to generate SHACL file
3. Choose location and save

## 🎉 Success!

You've created your first schema using DASH GUI v2!

## 📊 What You Can Do Next

### Immediate Next Steps
- [ ] Create more complex schemas
- [ ] Try different root bricks
- [ ] Experiment with flow configurations
- [ ] Export and validate schemas

### Explore Features
- **Library Management**: Switch between brick libraries
- **Schema Validation**: Check your schemas for errors
- **Flow Management**: Configure data flows
- **SHACL Export**: Generate standard SHACL files

## 🔧 Need Help?

### Common Questions
**Q: Where are my schemas saved?**
A: In `shared_libraries/schemas/default/`

**Q: How do I add more bricks?**
A: Place JSON brick files in `shared_libraries/bricks/default/`

**Q: Can I use the web interface?**
A: Yes! Multiple options:
- Docker: `./dev-start-schema-docker.sh` → http://localhost:5000
- Flask: `uv run python run_schema_app_web.py` → http://localhost:5000

**Q: How do I stop the application?**
A:
- Docker: Press Ctrl+C or run `docker stop <container>`
- Local: Close the window or press Ctrl+C in the terminal

## 📚 Further Reading

- **Complete User Guide**: `docs/USER_GUIDE.md`
- **Task Management**: `docs/TASK_MANAGER.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`
- **System Status**: `docs/README_V2_STATUS.md`

---

**Ready to build schemas with bricks! 🧱→🏗️**
