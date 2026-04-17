#!/usr/bin/env python3
"""
Simple Test for Schema App v2 GUI
Bypasses complex import issues
"""

import sys
import os
from PyQt6.QtWidgets import QApplication

# Add schema_app_v2 to path
sys.path.insert(0, os.path.abspath('schema_app_v2'))

try:
    from schema_app_v2.interfaces.qt.schema_gui import SchemaGUI
    print('✅ SchemaGUI import successful')
    
    app = QApplication(sys.argv)
    window = SchemaGUI()
    window.show()
    
    print('🎉 Schema App v2 GUI launched successfully!')
    print('📋 Ready to create schemas with bricks and flows')
    print('💡 Use Help → Help Guide for getting started')
    
    app.exec()
    
except Exception as e:
    print(f'❌ Error launching GUI: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
