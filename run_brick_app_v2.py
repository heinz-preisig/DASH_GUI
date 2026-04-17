#!/usr/bin/env python3
"""
Brick App v2 Launcher - Simple GUI Version
Clean launcher for the SHACL brick generation system using simple_gui
"""

import sys
import os
import subprocess
from pathlib import Path

# Change to brick_app_v2 directory for proper path resolution
brick_app_dir = Path(__file__).parent / 'brick_app_v2'
os.chdir(brick_app_dir)

print('Starting Brick App v2 Simple GUI...')
print('Ready to create SHACL bricks with full specification support')
print('Use Help -> Help Guide for getting started')

# Run the simple_gui directly
python_path = Path(__file__).parent / '.venv' / 'bin' / 'python'
subprocess.run([str(python_path), 'simple_gui.py'], check=True)
