"""
Brick GUI - Stub file for compatibility.
The main GUI is now in refactored_gui.py.
This file exists for backward compatibility with package imports.
"""

from typing import Optional


class BrickGUI:
    """Stub GUI class for backward compatibility."""
    
    def __init__(self, repository_path: Optional[str] = None):
        self.repository_path = repository_path or "brick_repositories"
    
    def show(self):
        """Show the GUI - delegates to refactored_gui"""
        print("GUI should be launched via refactored_gui.py")
        print("Run: python refactored_gui.py")
