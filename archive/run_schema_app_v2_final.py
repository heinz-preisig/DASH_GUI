#!/usr/bin/env python3
"""
Schema App v2 Launcher - Final Working Version
Simple launcher that bypasses complex import issues
"""

import sys
import os
from PyQt6.QtWidgets import QApplication

# Simple approach - run from correct directory
os.chdir('/home/heinz/1_Gits/DASH_GUI')

# Import directly from the correct location
from schema_app_v2.interfaces.qt.schema_gui import SchemaGUI

if __name__ == "__main__":
    print('🚀 Starting Schema App v2 GUI...')
    print('📋 Ready to create schemas with bricks and flows')
    print('💡 Use Help → Help Guide for getting started')
    
    app = QApplication(sys.argv)
    window = SchemaGUI()
    window.show()
    
    print('🎉 Schema App v2 GUI launched successfully!')
    
    app.exec()
