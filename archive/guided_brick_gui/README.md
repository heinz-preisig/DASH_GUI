# Guided SHACL Brick Generator

A user-friendly interface for creating and managing SHACL bricks without requiring deep technical knowledge.

## Architecture

```
guided_brick_gui/
├── main.py                 # Main entry point
├── ui/
│   ├── main_window.py      # Main window class
│   ├── panels/
│   │   ├── brick_list.py    # Brick list panel
│   │   ├── guide_panel.py   # Step-by-step guide
│   │   └── actions_panel.py # Quick actions
│   └── dialogs/
│       ├── brick_editor.py    # Brick editing dialog
│       └── message_boxes.py  # Common dialogs
└── backend/
    ├── brick_manager.py       # Backend communication
    └── events.py           # Event definitions
```

## Features

- **Step-by-step guidance** - User-friendly SHACL creation process
- **Clean frontend/backend separation** - UI only handles user input
- **Real-time brick editing** - Visual SHACL property editor
- **Automatic library management** - No manual setup required
- **Error handling** - Graceful handling of backend issues

## Usage

```python
from guided_brick_gui.main import main

main()
```

## Key Improvements

1. **Modular design** - Each component has focused responsibility
2. **Clean interfaces** - Clear separation between UI and backend
3. **Signal-based communication** - Loose coupling between components
4. **User-friendly terminology** - No technical SHACL jargon
5. **Maintainable code** - Easy to extend and modify
