#!/usr/bin/env python3
"""
Launch Step 2: Schema Constructor GUI (Frontend/Backend Separated)
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shacl_brick_app.schema.gui.schema_gui import SchemaGUI
from PyQt6.QtWidgets import QApplication

def main():
    """Launch Schema Constructor GUI with frontend/backend separation"""
    app = QApplication(sys.argv)
    gui = SchemaGUI()
    gui.show()
    return app.exec()

if __name__ == "__main__":
    main()
