#!/usr/bin/env python3
"""
PyCharm Launcher for Guided SHACL Brick Generator
User-friendly interface that guides users through SHACL creation without technical jargon
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from guided_brick_gui import main

if __name__ == "__main__":
    sys.exit(main())
