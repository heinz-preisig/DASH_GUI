#!/usr/bin/env python3
"""
Schema App v2 Launcher
Clean launcher for the schema construction system with multi-tenant backend
"""

import sys
import os
from PyQt6.QtWidgets import QApplication

# Change to correct directory and add to path
os.chdir('/home/heinz/1_Gits/DASH_GUI')
sys.path.insert(0, os.path.abspath('.'))

print('Starting Schema App v2 GUI...')
print('Schema construction system with multi-tenant backend')
print('Ready to create schemas with bricks and flows')

app = QApplication(sys.argv)

# Import and create the GUI
from schema_app_v2.interfaces.qt.schema_gui import SchemaGUI
window = SchemaGUI()
window.show()

print('Schema App v2 GUI launched successfully!')
app.exec()
