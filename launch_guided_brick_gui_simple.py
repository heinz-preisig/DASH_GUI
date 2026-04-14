#!/usr/bin/env python3
"""
Simple Launcher for Guided SHACL Brick Generator
"""

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import and run
from guided_brick_gui import main

if __name__ == "__main__":
    print("Starting Guided SHACL Brick Generator...")
    sys.exit(main())
