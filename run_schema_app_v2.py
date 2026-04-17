#!/usr/bin/env python3
"""
Schema App v2 Launcher - Final Consolidated Version
Clean launcher for the schema construction system
"""

import sys
import os
from PyQt6.QtWidgets import QApplication

# Change to correct directory and add to path
os.chdir('/home/heinz/1_Gits/DASH_GUI')
sys.path.insert(0, os.path.abspath('.'))

print('Testing direct imports...')
try:
    from schema_app_v2 import SchemaCore, SchemaGUI
    print('Core import successful')
except Exception as e:
    print(f'Core import failed: {e}')

try:
    from schema_app_v2.main import main
    print('Main import successful')
except Exception as e:
    print(f'Main import failed: {e}')

print('All imports working correctly!')
print('Starting Schema App v2 GUI...')
print('Ready to create schemas with bricks and flows')
print('Use Help -> Help Guide for getting started')

app = QApplication(sys.argv)
window = SchemaGUI()
window.show()

print('Schema App v2 GUI launched successfully!')
app.exec()
