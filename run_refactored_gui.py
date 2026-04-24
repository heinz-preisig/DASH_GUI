#!/usr/bin/env python3
"""
Brick App v2 Launcher - Refactored GUI Version
Launcher for the refactored SHACL brick generation system with clean architecture
"""

import sys
import os
import subprocess
from pathlib import Path

# Change to brick_app_v2 directory for proper path resolution
brick_app_dir = Path(__file__).parent / 'brick_app_v2'
os.chdir(brick_app_dir)

print('Starting Brick App v2 Refactored GUI...')
print('Using clean architecture with separated concerns')
print('Ready for web migration with proper state management')

# Run refactored_gui directly
python_path = Path(__file__).parent / '.venv' / 'bin' / 'python'
subprocess.run([str(python_path), 'refactored_gui.py'], check=True)
