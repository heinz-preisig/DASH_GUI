#!/usr/bin/env python3
"""
PyCharm Launcher for SHACL Brick Generator
Simple brick creation and management interface
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shacl_brick_app.gui.brick_gui import BrickGUI
from PyQt6.QtWidgets import QApplication

def main():
    """Launch SHACL Brick Generator GUI"""
    print("Starting SHACL Brick Generator...")
    app = QApplication(sys.argv)
    gui = BrickGUI()
    gui.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
