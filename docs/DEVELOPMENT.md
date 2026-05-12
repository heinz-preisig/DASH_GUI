# PyCharm Setup for SHACL Brick Generator

## Quick Setup for PyCharm Development

### Option 1: Run Configuration (Recommended)

1. **Open PyCharm** and load the DASH_GUI project
2. **Create Run Configuration:**
   - Go to `Run` → `Edit Configurations...`
   - Click `+` → `Python`
   - Name: `SHACL Brick Generator GUI`
   - Script path: `run_brick_app.py`
   - Parameters: `--gui --repository ./default_brick_repository`
   - Python interpreter: Select your `.venv` Python
   - Working directory: Project root
3. **Click Apply and Run**

### Option 2: Direct Script Execution

1. **Open Terminal** in PyCharm (Alt+F12)
2. **Navigate to project root:**
   ```bash
   cd /home/heinz/1_Gits/DASH_GUI
   ```
3. **Run the GUI:**
   ```bash
   python launch_gui.py
   ```

### Option 3: Use Existing Run Configuration

1. **Select** the pre-configured `SHACL_Brick_Generator` from the run dropdown
2. **Click the green run button** (Shift+F10)

## Repository Setup

The GUI will automatically create and use:
- `default_brick_repository/` - Main brick storage
- `default_brick_repository/default/` - Default library
- `default_brick_repository/default/metadata.json` - Library metadata
- `default_brick_repository/default/bricks/` - Individual brick files

## First Time Setup

Run this once to initialize the default repository:

```bash
python launch_gui.py
```

This will create the repository structure and you can start creating bricks immediately.

## Development Tips

- **Repository Location**: All bricks are stored in `default_brick_repository/`
- **Auto-creation**: Repository and default library are created automatically
- **PyCharm Integration**: Use the run configuration for easy debugging
- **File Monitoring**: PyCharm will detect changes to brick files automatically

## Troubleshooting

If you get import errors:
1. Make sure you're using the `.venv` Python interpreter
2. Check that you're running from the project root
3. Verify the `shacl_brick_app` package is properly structured

## GUI Features

- **Create Bricks**: Visual forms for NodeShape and PropertyShape
- **Manage Libraries**: Create, export, import brick libraries
- **Search & Filter**: Find bricks by name, type, tags
- **Export SHACL**: Convert bricks to valid SHACL Turtle format
- **Real-time Preview**: See SHACL output as you create bricks
