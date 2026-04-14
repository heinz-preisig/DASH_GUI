"""
Brick list panel for displaying existing bricks
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal

class BrickListPanel(QWidget):
    """Panel for displaying and managing existing bricks"""
    
    # Signal for when brick is created
    brick_created = pyqtSignal()
    # Signal for when brick should be edited/viewed
    brick_edit_requested = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.brick_manager = None
        self.init_ui()
    
    def set_brick_manager(self, brick_manager):
        """Set the brick manager for backend operations"""
        self.brick_manager = brick_manager
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("📋 Your Bricks")
        header.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; background: #e8f5e8; border-radius: 4px;")
        layout.addWidget(header)
        
        # Brick list
        self.brick_list = QListWidget()
        self.brick_list.itemDoubleClicked.connect(self.on_brick_double_clicked)
        layout.addWidget(self.brick_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh)
        button_layout.addWidget(refresh_btn)
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.clicked.connect(self.delete_brick)
        delete_btn.setStyleSheet("background-color: #dc3545; color: white;")
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_bricks(self, bricks_result):
        """Load bricks into the list"""
        self.brick_list.clear()
        
        # Handle the actual data structure from backend
        if isinstance(bricks_result, dict) and "bricks" in bricks_result:
            bricks_data = bricks_result["bricks"]
        else:
            bricks_data = bricks_result
            
        for brick in bricks_data:
            # User-friendly name
            friendly_name = self.get_friendly_brick_name(brick)
            item = QListWidgetItem(f"🧱 {friendly_name}")
            item.setData(Qt.ItemDataRole.UserRole, brick)
            self.brick_list.addItem(item)
    
    def on_brick_double_clicked(self, item):
        """Handle double-click on brick item"""
        brick_data = item.data(Qt.ItemDataRole.UserRole)
        friendly_name = self.get_friendly_brick_name(brick_data)
        
        # Emit signal for brick viewing/editing
        self.brick_edit_requested.emit(brick_data)
    
    def refresh(self):
        """Refresh the brick list"""
        if not self.brick_manager:
            print("Error: Brick manager not set")
            return
            
        result = self.brick_manager.get_bricks()
        if result["status"] == "success":
            self.load_bricks(result["data"])
        else:
            print(f"Error loading bricks: {result['message']}")
    
        
    def delete_brick(self):
        """Delete selected brick"""
        current_item = self.brick_list.currentItem()
        if not current_item:
            return
        
        # This will be connected to backend in main window
        pass
    
    def get_friendly_brick_name(self, brick_data):
        """Get user-friendly name for brick"""
        # Handle both string and dictionary brick_data
        if isinstance(brick_data, str):
            return brick_data
        
        if isinstance(brick_data, dict):
            name = brick_data.get("name", "Unknown")
            # If we have a proper name, use it
            if name != "Unknown":
                return name
            
            # Fallback to brick_id if name is not available
            brick_id = brick_data.get("brick_id", "Unknown")
            return brick_id.replace("_", " ").title()
        
        return str(brick_data)
