#!/usr/bin/env python3
"""
Launcher script for SHACL Brick Generator
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shacl_brick_app.bricks import main

if __name__ == "__main__":
    main()
