"""
Quick actions panel for common brick operations
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
)
from PyQt6.QtCore import pyqtSignal

class ActionsPanel(QWidget):
    """Panel for quick brick actions"""
    
    # Signal for when brick is created
    brick_created = pyqtSignal()
    
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
        header = QLabel("⚡ Quick Actions")
        header.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; background: #e8f5e8; border-radius: 4px;")
        layout.addWidget(header)
        
        # Quick action buttons
        actions = [
            ("👤 Create Person", self.create_person_brick),
            ("🏢 Create Organization", self.create_organization_brick),
            ("📧 Create Email Property", self.create_email_property),
            ("📅 Create Date Property", self.create_date_property),
            ("📝 Create Text Property", self.create_text_property),
            ("🔢 Create Number Property", self.create_number_property)
        ]
        
        for action_text, action_method in actions:
            btn = QPushButton(action_text)
            btn.clicked.connect(action_method)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 8px;
                    margin: 2px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    background: white;
                }
                QPushButton:hover {
                    background: #f0f8ff;
                }
            """)
            layout.addWidget(btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def create_person_brick(self):
        """Create a person brick"""
        if not self.brick_manager:
            print("Error: Brick manager not set")
            return
            
        result = self.brick_manager.create_brick(
            step1="thing",
            step2="specific_type", 
            step3="required"
        )
        
        if result["status"] == "success":
            print(f"✅ Person brick created successfully")
            self.brick_created.emit()
        else:
            print(f"❌ Error creating person brick")
    
    def create_organization_brick(self):
        """Create an organization brick"""
        if not self.brick_manager:
            print("Error: Brick manager not set")
            return
            
        result = self.brick_manager.create_brick(
            step1="thing",
            step2="specific_type", 
            step3="required"
        )
        
        if result["status"] == "success":
            print(f"✅ Organization brick created successfully")
            self.brick_created.emit()
        else:
            print(f"❌ Error creating organization brick")
    
    def create_email_property(self):
        """Create an email property brick"""
        if not self.brick_manager:
            print("Error: Brick manager not set")
            return
            
        result = self.brick_manager.create_brick(
            step1="property",
            step2="specific_type", 
            step3="required"
        )
        
        if result["status"] == "success":
            print(f"✅ Email property brick created successfully")
            self.brick_created.emit()
        else:
            print(f"❌ Error creating email property brick")
    
    def create_date_property(self):
        """Create a date property brick"""
        if not self.brick_manager:
            print("Error: Brick manager not set")
            return
            
        result = self.brick_manager.create_brick(
            step1="property",
            step2="specific_type", 
            step3="date_format"
        )
        
        if result["status"] == "success":
            print(f"✅ Date property brick created successfully")
            self.brick_created.emit()
        else:
            print(f"❌ Error creating date property brick")
    
    def create_text_property(self):
        """Create a text property brick"""
        if not self.brick_manager:
            print("Error: Brick manager not set")
            return
            
        result = self.brick_manager.create_brick(
            step1="property",
            step2="specific_type", 
            step3="text_length"
        )
        
        if result["status"] == "success":
            print(f"✅ Text property brick created successfully")
            self.brick_created.emit()
        else:
            print(f"❌ Error creating text property brick")
    
    def create_number_property(self):
        """Create a number property brick"""
        if not self.brick_manager:
            print("Error: Brick manager not set")
            return
            
        result = self.brick_manager.create_brick(
            step1="property",
            step2="specific_type", 
            step3="number_only"
        )
        
        if result["status"] == "success":
            print(f"✅ Number property brick created successfully")
            self.brick_created.emit()
        else:
            print(f"❌ Error creating number property brick")
