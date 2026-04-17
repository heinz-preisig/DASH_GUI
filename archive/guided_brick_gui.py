#!/usr/bin/env python3
"""
Guided SHACL Brick Generator GUI
User-friendly interface that guides users through SHACL creation without technical jargon
"""

import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from shacl_brick_app.core.brick_backend import BrickBackendAPI, BrickEventProcessor

class GuidedBrickGUI(QMainWindow):
    """Guided GUI for SHACL Brick Generation"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SHACL Brick Generator - Guided Mode")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize backend
        self.backend = BrickBackendAPI("brick_repositories")
        self.processor = BrickEventProcessor(self.backend)
        
        # Ensure we have an active library
        self._ensure_active_library()
        
        # Setup UI
        self.init_ui()
        self.load_existing_bricks()
    
    def _ensure_active_library(self):
        """Ensure we have an active library"""
        result = self.processor.process_event({"event": "get_repository_info"})
        if result["status"] == "success" and not result["data"]["active_library"]:
            # Try to set default library
            libraries_result = self.processor.process_event({"event": "get_libraries"})
            if libraries_result["status"] == "success" and libraries_result["data"]["libraries"]:
                default_lib = libraries_result["data"]["libraries"][0]["name"]
                set_result = self.processor.process_event({
                    "event": "set_active_library",
                    "library_name": default_lib
                })
                if set_result["status"] != "success":
                    print(f"Warning: Could not set active library {default_lib}: {set_result['message']}")
            else:
                print("Warning: No libraries available, creating one...")
                create_result = self.processor.process_event({
                    "event": "create_library",
                    "name": "default",
                    "description": "Default library for guided brick creation",
                    "author": "Guided GUI"
                })
                if create_result["status"] == "success":
                    set_result = self.processor.process_event({
                        "event": "set_active_library",
                        "library_name": "default"
                    })
                    if set_result["status"] != "success":
                        print(f"Warning: Could not set new active library: {set_result['message']}")
    
    def init_ui(self):
        """Initialize user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("🧱 SHACL Brick Generator - Guided Mode")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Main content
        content_layout = QHBoxLayout()
        
        # Left panel - Step-by-step guide
        left_panel = self.create_guide_panel()
        content_layout.addWidget(left_panel, 1)
        
        # Center panel - Brick list
        center_panel = self.create_brick_list_panel()
        content_layout.addWidget(center_panel, 2)
        
        # Right panel - Quick actions
        right_panel = self.create_actions_panel()
        content_layout.addWidget(right_panel, 1)
        
        layout.addLayout(content_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready to create SHACL bricks with guidance")
    
    def create_guide_panel(self):
        """Create step-by-step guide panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("📚 Step-by-Step Guide")
        header.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; background: #e8f5e8; border-radius: 4px;")
        layout.addWidget(header)
        
        # Step 1: What do you want to create?
        step1 = self.create_step_widget("Step 1: What do you want to create?", [
            ("👤 A thing (Person, Organization)", "thing"),
            ("🔗 A relationship between things", "relationship"),
            ("📋 A property (name, email, date)", "property"),
            ("🎯 A validation rule", "rule")
        ], "step1")
        layout.addWidget(step1)
        
        # Step 2: What should it apply to?
        step2 = self.create_step_widget("Step 2: What should it apply to?", [
            ("🏷️ Specific type of thing", "specific_type"),
            ("🏷️ All things of a certain type", "all_of_type"),
            ("🏷️ Things with specific properties", "with_properties"),
            ("🏷️ Things that follow a rule", "following_rule")
        ], "step2")
        layout.addWidget(step2)
        
        # Step 3: What rules should it follow?
        step3 = self.create_step_widget("Step 3: What rules should it follow?", [
            ("✅ Required information", "required"),
            ("🔢 Must be a number", "number_only"),
            ("📏 Text length limits", "text_length"),
            ("📅 Date format", "date_format"),
            ("📧 Email format", "email_format"),
            ("🔗 Link to another thing", "reference")
        ], "step3")
        layout.addWidget(step3)
        
        # Create button
        create_btn = QPushButton("🚀 Create Based on Selection")
        create_btn.clicked.connect(self.create_from_selections)
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        layout.addWidget(create_btn)
        
        layout.addStretch()
        return panel
    
    def create_step_widget(self, title, options, step_name):
        """Create a step selection widget"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        layout = QVBoxLayout(group)
        
        # Initialize step selections dict if not exists
        if not hasattr(self, 'step_selections'):
            self.step_selections = {}
        
        self.step_selections[step_name] = {}
        
        for option_text, option_value in options:
            radio = QRadioButton(option_text)
            radio.setProperty("option_value", option_value)
            layout.addWidget(radio)
            self.step_selections[step_name][option_value] = radio
        
        # Add button group for this step
        button_group = QButtonGroup()
        for radio in self.step_selections[step_name].values():
            button_group.addButton(radio)
        
        layout.addStretch()
        return group
    
    def create_brick_list_panel(self):
        """Create panel showing existing bricks"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("📋 Your Bricks")
        header.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; background: #e8f5e8; border-radius: 4px;")
        layout.addWidget(header)
        
        # Brick list
        self.brick_list = QListWidget()
        self.brick_list.itemDoubleClicked.connect(self.edit_brick)
        layout.addWidget(self.brick_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_existing_bricks)
        button_layout.addWidget(refresh_btn)
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.clicked.connect(self.delete_brick)
        delete_btn.setStyleSheet("background-color: #dc3545; color: white;")
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        return panel
    
    def create_actions_panel(self):
        """Create quick actions panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
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
                    border-color: #2c3e50;
                }
            """)
            layout.addWidget(btn)
        
        # Help text
        help_text = QLabel("💡 Select options from the guide or use quick actions for common bricks.")
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #6c757d; font-style: italic; padding: 10px; background: #f8f9fa; border-radius: 4px;")
        layout.addWidget(help_text)
        
        layout.addStretch()
        return panel
    
    def get_selections(self):
        """Get current selections from guide"""
        selections = {}
        
        # Get selections for each step
        for step_name, step_options in self.step_selections.items():
            for option_value, radio in step_options.items():
                if radio.isChecked():
                    selections[step_name] = option_value
                    break
        
        return selections
    
    def create_from_selections(self):
        """Create brick based on user selections"""
        selections = self.get_selections()
        
        if not selections.get("step1"):
            QMessageBox.warning(self, "Missing Selection", "Please select what you want to create in Step 1")
            return
        
        # Send selections to backend for SHACL creation logic
        result = self.processor.process_event({
            "event": "create_guided_brick",
            "step1": selections["step1"],
            "step2": selections.get("step2"),
            "step3": selections.get("step3"),
            "custom_name": None  # Could add custom name input later
        })
        
        if result["status"] == "success":
            self.load_existing_bricks()
            self.statusBar().showMessage(f"Created {result.get('name', 'brick')} successfully!")
        else:
            QMessageBox.warning(self, "Error", f"Failed to create brick: {result['message']}")
    
    # All SHACL creation logic moved to backend for clean separation
    
    def create_person_brick(self):
        """Create a person brick with common properties"""
        brick_data = {
            "name": "Person_Shape",
            "object_type": "NodeShape",
            "properties": {
                "name": {"datatype": "http://www.w3.org/2001/XMLSchema#string", "min_count": 1},
                "email": {"datatype": "http://www.w3.org/2001/XMLSchema#string"},
                "birthDate": {"datatype": "http://www.w3.org/2001/XMLSchema#date"}
            },
            "targets": [{"target_type": "TargetClass", "value": "http://schema.org/Person"}]
        }
        self.create_brick(brick_data)
    
    def create_organization_brick(self):
        """Create an organization brick"""
        brick_data = {
            "name": "Organization_Shape",
            "object_type": "NodeShape",
            "properties": {
                "name": {"datatype": "http://www.w3.org/2001/XMLSchema#string", "min_count": 1},
                "description": {"datatype": "http://www.w3.org/2001/XMLSchema#string"}
            },
            "targets": [{"target_type": "TargetClass", "value": "http://schema.org/Organization"}]
        }
        self.create_brick(brick_data)
    
    def create_email_property(self):
        """Create an email property"""
        brick_data = {
            "name": "Email_Property",
            "object_type": "PropertyShape",
            "properties": {
                "path": "http://schema.org/email",
                "datatype": "http://www.w3.org/2001/XMLSchema#string"
            }
        }
        self.create_brick(brick_data)
    
    def create_date_property(self):
        """Create a date property"""
        brick_data = {
            "name": "Date_Property",
            "object_type": "PropertyShape",
            "properties": {
                "path": "http://schema.org/date",
                "datatype": "http://www.w3.org/2001/XMLSchema#date"
            }
        }
        self.create_brick(brick_data)
    
    def create_text_property(self):
        """Create a text property"""
        brick_data = {
            "name": "Text_Property",
            "object_type": "PropertyShape",
            "properties": {
                "path": "http://schema.org/text",
                "datatype": "http://www.w3.org/2001/XMLSchema#string"
            },
            "constraints": [
                {"constraint_type": "MaxLengthConstraintComponent", "value": 255}
            ]
        }
        self.create_brick(brick_data)
    
    def create_number_property(self):
        """Create a number property"""
        brick_data = {
            "name": "Number_Property",
            "object_type": "PropertyShape",
            "properties": {
                "path": "http://schema.org/number",
                "datatype": "http://www.w3.org/2001/XMLSchema#decimal"
            }
        }
        self.create_brick(brick_data)
    
    def create_brick(self, brick_data):
        """Create brick using backend"""
        # Determine brick type and use appropriate event
        object_type = brick_data.get("object_type", "NodeShape")
        
        if object_type == "NodeShape":
            event_data = {
                "event": "create_nodeshape_brick",
                "brick_id": brick_data["name"],
                "name": brick_data["name"],
                "description": brick_data.get("description", ""),
                "target_class": brick_data.get("targets", [{}])[0].get("value") if brick_data.get("targets") else None,
                "properties": brick_data.get("properties", {}),
                "constraints": brick_data.get("constraints", []),
                "tags": brick_data.get("tags", [])
            }
        elif object_type == "PropertyShape":
            event_data = {
                "event": "create_propertyshape_brick",
                "brick_id": brick_data["name"],
                "name": brick_data["name"],
                "description": brick_data.get("description", ""),
                "path": brick_data.get("properties", {}).get("path", ""),
                "properties": brick_data.get("properties", {}),
                "constraints": brick_data.get("constraints", []),
                "tags": brick_data.get("tags", [])
            }
        else:
            # Fallback for other types
            event_data = {
                "event": "create_nodeshape_brick",
                "brick_id": brick_data["name"],
                "name": brick_data["name"],
                "description": brick_data.get("description", ""),
                "properties": brick_data.get("properties", {}),
                "constraints": brick_data.get("constraints", []),
                "tags": brick_data.get("tags", [])
            }
        
        result = self.processor.process_event(event_data)
        
        if result["status"] == "success":
            self.load_existing_bricks()
            self.statusBar().showMessage(f"Created {brick_data['name']} successfully!")
        else:
            QMessageBox.warning(self, "Error", f"Failed to create brick: {result['message']}")
    
    def create_brick(self, brick_data):
        """Create brick using backend"""
        # Determine brick type and use appropriate event
        object_type = brick_data.get("object_type", "NodeShape")
        
        if object_type == "NodeShape":
            event_data = {
                "event": "create_nodeshape_brick",
                "brick_id": brick_data["name"],
                "name": brick_data["name"],
                "description": brick_data.get("description", ""),
                "target_class": brick_data.get("targets", [{}])[0].get("value") if brick_data.get("targets") else None,
                "properties": brick_data.get("properties", {}),
                "constraints": brick_data.get("constraints", []),
                "tags": brick_data.get("tags", [])
            }
        elif object_type == "PropertyShape":
            event_data = {
                "event": "create_propertyshape_brick",
                "brick_id": brick_data["name"],
                "name": brick_data["name"],
                "description": brick_data.get("description", ""),
                "path": brick_data.get("properties", {}).get("path", ""),
                "properties": brick_data.get("properties", {}),
                "constraints": brick_data.get("constraints", []),
                "tags": brick_data.get("tags", [])
            }
        else:
            # Fallback for other types
            event_data = {
                "event": "create_nodeshape_brick",
                "brick_id": brick_data["name"],
                "name": brick_data["name"],
                "description": brick_data.get("description", ""),
                "properties": brick_data.get("properties", {}),
                "constraints": brick_data.get("constraints", []),
                "tags": brick_data.get("tags", [])
            }
        
        result = self.processor.process_event(event_data)
        
        if result["status"] == "success":
            self.load_existing_bricks()
            self.statusBar().showMessage(f"Created {brick_data['name']} successfully!")
        else:
            QMessageBox.warning(self, "Error", f"Failed to create brick: {result['message']}")
    
    def load_existing_bricks(self):
        """Load existing bricks into list"""
        result = self.processor.process_event({"event": "get_library_bricks"})
        if result["status"] == "success":
            self.brick_list.clear()
            for brick in result["data"]["bricks"]:
                # User-friendly description
                friendly_name = self.get_friendly_brick_name(brick)
                item = QListWidgetItem(f"🧱 {friendly_name}")
                item.setData(Qt.ItemDataRole.UserRole, brick)
                self.brick_list.addItem(item)
    
    def get_friendly_brick_name(self, brick):
        """Get user-friendly name for brick"""
        name = brick.get("name", "Unknown")
        object_type = brick.get("object_type", "")
        
        # Convert technical names to friendly names
        friendly_names = {
            "NodeShape": "Thing Shape",
            "PropertyShape": "Property Rule",
            "Person_Shape": "Person",
            "Organization_Shape": "Organization",
            "Email_Property": "Email Rule",
            "Date_Property": "Date Rule",
            "Text_Property": "Text Rule",
            "Number_Property": "Number Rule"
        }
        
        return friendly_names.get(name, name)
    
    def edit_brick(self, item):
        """Edit selected brick"""
        brick_data = item.data(Qt.ItemDataRole.UserRole)
        friendly_name = self.get_friendly_brick_name(brick_data)
        
        # Create brick editor dialog
        dialog = BrickEditorDialog(brick_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_brick_data = dialog.get_brick_data()
            result = self.processor.process_event({
                "event": "update_brick",
                "brick_id": brick_data["id"],
                "brick_data": updated_brick_data
            })
            
            if result["status"] == "success":
                self.load_existing_bricks()
                self.statusBar().showMessage(f"Updated {friendly_name} successfully!")
            else:
                QMessageBox.warning(self, "Error", f"Failed to update brick: {result['message']}")


class BrickEditorDialog(QDialog):
    """Dialog for editing SHACL brick properties"""
    
    def __init__(self, brick_data, parent=None):
        super().__init__(parent)
        self.brick_data = brick_data.copy()
        self.setWindowTitle(f"Edit Brick: {brick_data.get('name', 'Unknown')}")
        self.setModal(True)
        self.resize(600, 500)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the editor UI"""
        layout = QVBoxLayout(self)
        
        # Basic info section
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        
        self.name_edit = QLineEdit(self.brick_data.get("name", ""))
        self.name_edit.setPlaceholderText("Brick name")
        basic_layout.addRow("Name:", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlainText(self.brick_data.get("description", ""))
        self.description_edit.setPlaceholderText("Brick description")
        basic_layout.addRow("Description:", self.description_edit)
        
        layout.addWidget(basic_group)
        
        # Properties section
        props_group = QGroupBox("SHACL Properties")
        props_layout = QVBoxLayout(props_group)
        
        # Create property editor
        self.props_table = QTableWidget()
        self.props_table.setColumnCount(3)
        self.props_table.setHorizontalHeaderLabels(["Property", "Value", "Type"])
        self.props_table.horizontalHeader().setStretchLastSection(True)
        
        # Load existing properties
        properties = self.brick_data.get("properties", {})
        for prop_name, prop_data in properties.items():
            row = self.props_table.rowCount()
            self.props_table.insertRow(row)
            
            # Property name
            name_item = QTableWidgetItem(prop_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.props_table.setItem(row, 0, name_item)
            
            # Property value
            if isinstance(prop_data, dict):
                value = prop_data.get("datatype", "")
                prop_type = "datatype"
            else:
                value = str(prop_data)
                prop_type = "value"
            
            value_item = QTableWidgetItem(value)
            self.props_table.setItem(row, 1, value_item)
            
            # Property type
            type_item = QTableWidgetItem(prop_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.props_table.setItem(row, 2, type_item)
        
        props_layout.addWidget(self.props_table)
        
        # Add/Remove property buttons
        prop_buttons = QHBoxLayout()
        add_prop_btn = QPushButton("Add Property")
        add_prop_btn.clicked.connect(self.add_property)
        prop_buttons.addWidget(add_prop_btn)
        
        remove_prop_btn = QPushButton("Remove Selected")
        remove_prop_btn.clicked.connect(self.remove_property)
        prop_buttons.addWidget(remove_prop_btn)
        
        props_layout.addLayout(prop_buttons)
        layout.addWidget(props_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def add_property(self):
        """Add a new property row"""
        row = self.props_table.rowCount()
        self.props_table.insertRow(row)
        
        self.props_table.setItem(row, 0, QTableWidgetItem("new_property"))
        self.props_table.setItem(row, 1, QTableWidgetItem(""))
        self.props_table.setItem(row, 2, QTableWidgetItem("value"))
    
    def remove_property(self):
        """Remove selected property row"""
        current_row = self.props_table.currentRow()
        if current_row >= 0:
            self.props_table.removeRow(current_row)
    
    def get_brick_data(self):
        """Get updated brick data from form"""
        # Get basic info
        self.brick_data["name"] = self.name_edit.text().strip()
        self.brick_data["description"] = self.description_edit.toPlainText().strip()
        
        # Get properties
        properties = {}
        for row in range(self.props_table.rowCount()):
            prop_name = self.props_table.item(row, 0).text().strip()
            prop_value = self.props_table.item(row, 1).text().strip()
            prop_type = self.props_table.item(row, 2).text().strip()
            
            if prop_name and prop_value:
                if prop_type == "datatype":
                    properties[prop_name] = {"datatype": prop_value}
                else:
                    properties[prop_name] = prop_value
        
        self.brick_data["properties"] = properties
        return self.brick_data
    
    def delete_brick(self):
        """Delete selected brick"""
        current_item = self.brick_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a brick to delete")
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                               f"Delete brick '{current_item.text()}'?",
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            brick_data = current_item.data(Qt.ItemDataRole.UserRole)
            result = self.processor.process_event({
                "event": "delete_brick",
                "brick_id": brick_data["id"]
            })
            
            if result["status"] == "success":
                self.load_existing_bricks()
                self.statusBar().showMessage("Brick deleted successfully!")
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete brick: {result['message']}")

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    gui = GuidedBrickGUI()
    gui.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
