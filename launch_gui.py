#!/usr/bin/env python3
"""
Simple launcher for SHACL Brick Generator GUI in PyCharm
"""

import sys
import os

# Add current directory to Python path for PyCharm
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shacl_brick_app.gui.brick_gui import BrickGUI
from PyQt6.QtWidgets import QApplication

def main():
    """Launch the SHACL Brick Generator GUI"""
    app = QApplication(sys.argv)
    gui = BrickGUI()
    gui.show()
    return app.exec()

if __name__ == "__main__":
    main()
