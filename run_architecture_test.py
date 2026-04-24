#!/usr/bin/env python3
"""
Architecture Test Launcher
Tests the refactored architecture without UI dependencies
"""

import sys
import os
import subprocess
from pathlib import Path

# Change to brick_app_v2 directory for proper path resolution
brick_app_dir = Path(__file__).parent / 'brick_app_v2'
os.chdir(brick_app_dir)

print('🧪 Testing Refactored Architecture...')
print('Verifying clean separation of concerns and web readiness')

# Run architecture test directly
python_path = Path(__file__).parent / '.venv' / 'bin' / 'python'
subprocess.run([str(python_path), 'test_refactored.py'], check=True)
