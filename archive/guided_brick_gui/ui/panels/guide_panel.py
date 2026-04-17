"""
Step-by-step guide panel for SHACL brick creation
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QRadioButton, QButtonGroup, QPushButton
)
from PyQt6.QtCore import pyqtSignal

class GuidePanel(QWidget):
    """Step-by-step guide panel"""
    
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
        """Initialize the guide UI"""
        layout = QVBoxLayout(self)
        
        # Step 1: What do you want to create?
        step1_group = QGroupBox("Step 1: What do you want to create?")
        step1_layout = QVBoxLayout(step1_group)
        
        step1_options = [
            ("👤 A thing (Person, Organization)", "thing"),
            ("🔗 A relationship between things", "relationship"),
            ("📋 A property (name, email, date)", "property"),
            ("🎯 A validation rule", "rule")
        ]
        
        for option_text, option_value in step1_options:
            radio = QRadioButton(option_text)
            radio.setProperty("option_value", option_value)
            step1_layout.addWidget(radio)
        
        step1_group.setLayout(step1_layout)
        layout.addWidget(step1_group)
        
        # Step 2: What should it apply to?
        step2_group = QGroupBox("Step 2: What should it apply to?")
        step2_layout = QVBoxLayout(step2_group)
        
        step2_options = [
            ("🏷️ Specific type of thing", "specific_type"),
            ("🏷️ All things of a certain type", "all_of_type"),
            ("🏷️ Things with specific properties", "with_properties"),
            ("🏷️ Things that follow a rule", "following_rule")
        ]
        
        for option_text, option_value in step2_options:
            radio = QRadioButton(option_text)
            radio.setProperty("option_value", option_value)
            step2_layout.addWidget(radio)
        
        step2_group.setLayout(step2_layout)
        layout.addWidget(step2_group)
        
        # Step 3: What rules should it follow?
        step3_group = QGroupBox("Step 3: What rules should it follow?")
        step3_layout = QVBoxLayout(step3_group)
        
        step3_options = [
            ("✅ Required information", "required"),
            ("🔢 Must be a number", "number_only"),
            ("📏 Text length limits", "text_length"),
            ("📅 Date format", "date_format"),
            ("📧 Email format", "email_format"),
            ("🔗 Link to another thing", "reference")
        ]
        
        for option_text, option_value in step3_options:
            radio = QRadioButton(option_text)
            radio.setProperty("option_value", option_value)
            step3_layout.addWidget(radio)
        
        step3_group.setLayout(step3_layout)
        layout.addWidget(step3_group)
        
        # Create button
        create_btn = QPushButton("🚀 Create Based on Selection")
        create_btn.clicked.connect(self.create_brick)
        layout.addWidget(create_btn)
        
        self.setLayout(layout)
    
    def get_selections(self):
        """Get current selections from guide"""
        selections = {}
        
        # Find all radio buttons and check which ones are selected
        all_radio_buttons = self.findChildren(QRadioButton)
        
        for radio in all_radio_buttons:
            if radio.isChecked():
                option_value = radio.property("option_value")
                if option_value:
                    # Determine which step this radio button belongs to
                    parent = radio.parent()
                    if parent:
                        parent_title = parent.title()
                        if "Step 1" in parent_title:
                            selections["step1"] = option_value
                        elif "Step 2" in parent_title:
                            selections["step2"] = option_value
                        elif "Step 3" in parent_title:
                            selections["step3"] = option_value
        
        return selections
    
    def create_brick(self):
        """Handle brick creation and emit signal"""
        if not self.brick_manager:
            print("Error: Brick manager not set")
            return
            
        # Get current selections
        selections = self.get_selections()
        print(f"Debug - Selections: {selections}")
        
        # Validate that selections are made
        if not selections.get("step1"):
            print("Error: Please select an option in Step 1")
            return
        if not selections.get("step2"):
            print("Error: Please select an option in Step 2")
            return
        if not selections.get("step3"):
            print("Error: Please select an option in Step 3")
            return
        
        # Create brick using backend
        result = self.brick_manager.create_brick(
            step1=selections.get("step1"),
            step2=selections.get("step2"),
            step3=selections.get("step3")
        )
        print(f"Debug - Brick creation result: {result}")
        
        if result["status"] == "success":
            print(f"✅ Brick created successfully")
            self.brick_created.emit()
        else:
            print(f"❌ Error creating brick")
