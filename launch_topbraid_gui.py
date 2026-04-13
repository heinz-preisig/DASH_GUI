#!/usr/bin/env python3
"""
Launch TopBraid-inspired SHACL Brick Generator GUI
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shacl_brick_app.gui.topbraid_inspired_gui import TopBraidInspiredGUI
from PyQt6.QtWidgets import QApplication

def main():
    """Launch TopBraid-inspired SHACL Brick Generator GUI"""
    app = QApplication(sys.argv)
    gui = TopBraidInspiredGUI()
    gui.show()
    return app.exec()

if __name__ == "__main__":
    main()
