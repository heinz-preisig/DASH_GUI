# Quick Start Guide - DASH GUI v2

**Purpose**: Get started with DASH GUI v2 in 5 minutes

## 🚀 Quick Start Options

### Option A: Docker (No Python Setup Required)
```bash
# Start Schema App
./start-schema-app.sh
# → Open http://localhost:5000

# Start Brick App (in another terminal)
./start-brick-app.sh
# → Open http://localhost:5001
```

### Option B: Local Development

#### Prerequisites
- Python 3.13+
- Virtual environment (`.venv/`)
- Dependencies installed (see `pyproject.toml`)

#### Quick Setup Check
```bash
# Verify everything is ready
python3 run_tasks.py setup
```

## 🎯 5-Minute Quick Start (Local)

### Step 1: Launch Interface (30 seconds)
```bash
# PyQt6 Desktop (Recommended)
python3 run_tasks.py qt

# OR DASH Web Interface
python3 run_tasks.py dash

# OR Flask Web Interface
.venv/bin/python run_schema_app_web.py
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
A: In `schema_repositories/default/schemas/`

**Q: How do I add more bricks?**
A: Place JSON brick files in `brick_repositories/default/bricks/`

**Q: Can I use the web interface?**
A: Yes! Multiple options:
- Docker: `./start-schema-app.sh` → http://localhost:5000
- Flask: `.venv/bin/python run_schema_app_web.py` → http://localhost:5000
- DASH: `python3 run_tasks.py dash` → http://localhost:8050

**Q: How do I stop the application?**
A: 
- Docker: Press Ctrl+C or run `docker stop <container>`
- Local: Run `python3 run_tasks.py stop` or close the window

## 📚 Further Reading

- **Complete User Guide**: `docs/USER_GUIDE.md`
- **Task Management**: `docs/TASK_MANAGER.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`
- **System Status**: `docs/README_V2_STATUS.md`

---

**Ready to build schemas with bricks! 🧱→🏗️**
