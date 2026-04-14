"""
Main window for Guided SHACL Brick Generator
"""
from PyQt6.QtWidgets import QDialog
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt

from .panels.brick_list import BrickListPanel
from .panels.guide_panel import GuidePanel
from .panels.actions_panel import ActionsPanel
from ..backend.brick_manager import BrickManager
from shacl_brick_app.schema.gui.brick_editor import BrickEditorDialog

class MainWindow(QMainWindow):
    """Main window for guided brick creation"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SHACL Brick Generator - Guided Mode")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize backend
        self.brick_manager = BrickManager()
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create panels with backend reference
        guide_panel = GuidePanel()
        guide_panel.set_brick_manager(self.brick_manager)
        
        brick_list_panel = BrickListPanel()
        brick_list_panel.set_brick_manager(self.brick_manager)
        
        actions_panel = ActionsPanel()
        actions_panel.set_brick_manager(self.brick_manager)
        
        # Add panels to layout
        layout.addWidget(guide_panel, 1)
        layout.addWidget(brick_list_panel, 2)
        layout.addWidget(actions_panel, 1)
        
        # Connect signals
        guide_panel.brick_created.connect(brick_list_panel.refresh)
        actions_panel.brick_created.connect(brick_list_panel.refresh)
        brick_list_panel.brick_edit_requested.connect(self.open_brick_editor)
        
        # Load initial bricks
        brick_list_panel.refresh()
        
        self.statusBar().showMessage("Ready to create SHACL bricks")
    
    def open_brick_editor(self, brick_data):
        """Open brick editor dialog for viewing/editing brick"""
        dialog = BrickEditorDialog(brick_data, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get the updated brick data using the editor's method
            updated_brick_data = dialog.get_brick_data()
            
            # Update the brick in the repository
            brick_id = updated_brick_data.get("brick_id")
            if brick_id:
                result = self.brick_manager.update_brick(brick_id, updated_brick_data)
                if result["status"] == "success":
                    print("?? Brick updated successfully")
                    # Refresh the brick list to show changes
                    for widget in self.findChildren(BrickListPanel):
                        widget.refresh()
                        break
                else:
                    print(f"?? Error updating brick: {result.get('message', 'Unknown error')}")
            else:
                print("?? Error: No brick_id found in updated data")
