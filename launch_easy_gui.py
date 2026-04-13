#!/usr/bin/env python3
"""
Launch user-friendly SHACL Brick Generator GUI
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shacl_brick_app.gui.user_friendly_gui import UserFriendlyBrickGUI
from PyQt6.QtWidgets import QApplication

def main():
    """Launch user-friendly SHACL Brick Generator GUI"""
    app = QApplication(sys.argv)
    gui = UserFriendlyBrickGUI()
    gui.show()
    return app.exec()

if __name__ == "__main__":
    main()
