#!/usr/bin/env python3
"""
Launch combined SHACL Brick Generator GUI with mode switching
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shacl_brick_app.gui.combined_gui import CombinedBrickGUI
from PyQt6.QtWidgets import QApplication

def main():
    """Launch combined SHACL Brick Generator GUI"""
    app = QApplication(sys.argv)
    gui = CombinedBrickGUI()
    gui.show()
    return app.exec()

if __name__ == "__main__":
    main()
