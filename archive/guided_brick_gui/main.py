#!/usr/bin/env python3
"""
Main entry point for Guided SHACL Brick Generator
"""

import sys
from PyQt6.QtWidgets import QApplication

from .ui.main_window import MainWindow

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
