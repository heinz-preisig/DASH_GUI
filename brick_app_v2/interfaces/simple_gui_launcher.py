#!/usr/bin/env python3
"""
Simple launcher for the modular SHACL Brick Editor
"""

import sys
from pathlib import Path

# Add the brick_app_v2 directory to the Python path for proper package imports
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

try:
    from interfaces.simple_gui import main
except ImportError:
    # Fallback for when running directly
    sys.path.insert(0, str(app_dir / 'interfaces'))
    from simple_gui import main

if __name__ == "__main__":
    main()
