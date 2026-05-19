#!/usr/bin/env python3
"""
Brick App v2 Launcher - Local State Architecture
Launcher for the SHACL brick generation system with simple local state
"""

import sys
import os
import subprocess
from pathlib import Path

# Add parent directory to Python path for common module
parent_dir = Path(__file__).parent
sys.path.insert(0, str(parent_dir))

# Change to brick_app_v2 directory for proper path resolution
brick_app_dir = parent_dir / 'brick_app_v2'
os.chdir(brick_app_dir)

print('Starting Brick App v2 - Local State Architecture')
print('Using simple local state management')

# Run brick app with GUI using uv
subprocess.run(['uv', 'run', 'main.py', '--gui'], check=True)
