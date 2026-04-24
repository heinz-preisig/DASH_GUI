#!/usr/bin/env python3
"""
Brick App v2 Web Launcher
Web interface launcher for the SHACL brick generation system
"""

import sys
import os
import subprocess
from pathlib import Path

# Change to brick_app_v2 directory for proper path resolution
brick_app_dir = Path(__file__).parent / 'brick_app_v2'
os.chdir(brick_app_dir)

print('Starting Brick App v2 Web Interface...')
print('SHACL brick generation system with clean architecture')
print('Ready for web deployment with proper API endpoints')

# Run brick app web interface
python_path = Path(__file__).parent / '.venv' / 'bin' / 'python'
subprocess.run([str(python_path), '-m', 'main', '--web', '--port', '5000'], check=True)
