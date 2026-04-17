#!/usr/bin/env python3
"""
Step 2: Schema Constructor Launcher
Easy launcher for schema construction system
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shacl_brick_app.schema.main import main

if __name__ == "__main__":
    sys.exit(main())
