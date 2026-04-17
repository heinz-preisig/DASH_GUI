#!/usr/bin/env python3
"""
Simple launcher for the modular SHACL Brick Editor
"""

import sys
from pathlib import Path

# Add the brick_app_v2 directory to the Python path for proper package imports
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

# Import main function from the parent directory's simple_gui module
import importlib.util
spec = importlib.util.spec_from_file_location("simple_gui", app_dir / "simple_gui.py")
simple_gui_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(simple_gui_module)
main = simple_gui_module.main

if __name__ == "__main__":
    main()
