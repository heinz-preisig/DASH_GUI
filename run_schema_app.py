#!/usr/bin/env python3
"""
Schema App v2 Launcher
Launcher for the schema construction system that uses bricks from brick_app_v2
"""

import sys
import os
import subprocess
from pathlib import Path

# Change to schema_app_v2 directory for proper path resolution
schema_app_dir = Path(__file__).parent / 'schema_app_v2'
os.chdir(schema_app_dir)

print('Starting Schema App v2...')
print('Schema construction system using bricks from brick_app_v2')
print('Ready to create schemas with bricks and flows')

# Run schema app main directly - need to run from parent directory for proper imports
python_path = Path(__file__).parent / '.venv' / 'bin' / 'python'
os.chdir(Path(__file__).parent)  # Change back to parent directory
subprocess.run([str(python_path), '-m', 'schema_app_v2.main', '--gui'], check=True)
