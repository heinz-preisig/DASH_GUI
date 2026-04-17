#!/usr/bin/env python3
"""
User-Friendly GUI for SHACL Brick Generator
Designed for non-SHACL experts with intuitive primitives and constraints
"""

import sys
import re
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from ..core.brick_backend import BrickBackendAPI, BrickEventProcessor

class UserFriendlyBrickGUI(QMainWindow):
    """User-friendly GUI for SHACL Brick Generator"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SHACL Brick Generator - Easy Mode")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize backend
        self.backend = BrickBackendAPI("default_brick_repository")
        self.processor = BrickEventProcessor(self.backend)
        
        # Editing state
        self.editing_brick_id = None
        self.editing_brick_data = None
        
        # UI setup
        self.init_ui()
        self._ensure_active_library()
        self.load_bricks()
    
    def init_ui(self):
        """Initialize user-friendly interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Left panel - Brick creation
        left_panel = self.create_creation_panel()
        layout.addWidget(left_panel, 1)
        
        # Right panel - Brick library and preview
        right_panel = self.create_library_panel()
        layout.addWidget(right_panel, 1)
        
        # Status bar
        self.statusBar().showMessage("Ready to create bricks!")
    
    def create_creation_panel(self):
        """Create user-friendly brick creation panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("Create New Brick")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3; padding: 10px;")
        layout.addWidget(header)
        
        # Basic info
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout()
        
        self.brick_name_edit = QLineEdit()
        self.brick_name_edit.setPlaceholderText("e.g., Person Information")
        basic_layout.addRow("Brick Name:", self.brick_name_edit)
        
        self.brick_desc_edit = QTextEdit()
        self.brick_desc_edit.setPlaceholderText("Describe what this brick represents...")
        self.brick_desc_edit.setMaximumHeight(80)
        basic_layout.addRow("Description:", self.brick_desc_edit)
        
        # Brick type selection with user-friendly names
        self.brick_type_combo = QComboBox()
        self.brick_type_combo.addItems([
            "Entity/Class Shape", "Property/Field Shape"
        ])
        self.brick_type_combo.currentTextChanged.connect(self.on_brick_type_changed)
        basic_layout.addRow("What is this?:", self.brick_type_combo)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Dynamic fields based on type
        self.dynamic_fields = QWidget()
        self.dynamic_layout = QVBoxLayout(self.dynamic_fields)
        layout.addWidget(self.dynamic_fields)
        
        # Constraints section
        constraints_group = QGroupBox("Validation Rules")
        constraints_layout = QVBoxLayout()
        
        # Common constraints for all types
        self.required_checkbox = QCheckBox("Required field")
        constraints_layout.addWidget(self.required_checkbox)
        
        # String-specific constraints
        string_constraints = QWidget()
        string_layout = QFormLayout()
        
        self.min_length_spin = QSpinBox()
        self.min_length_spin.setMinimum(0)
        self.min_length_spin.setMaximum(1000)
        self.min_length_spin.setSpecialValueText("No limit")
        string_layout.addRow("Minimum length:", self.min_length_spin)
        
        self.max_length_spin = QSpinBox()
        self.max_length_spin.setMinimum(0)
        self.max_length_spin.setMaximum(1000)
        self.max_length_spin.setSpecialValueText("No limit")
        string_layout.addRow("Maximum length:", self.max_length_spin)
        
        self.pattern_edit = QLineEdit()
        self.pattern_edit.setPlaceholderText("e.g., email pattern: [^@]+@[^@]+\\.[^@]+")
        string_layout.addRow("Pattern (regex):", self.pattern_edit)
        
        string_constraints.setLayout(string_layout)
        constraints_layout.addWidget(string_constraints)
        
        # Number-specific constraints
        number_constraints = QWidget()
        number_layout = QFormLayout()
        
        self.min_value_spin = QDoubleSpinBox()
        self.min_value_spin.setMinimum(-999999)
        self.min_value_spin.setMaximum(999999)
        self.min_value_spin.setSpecialValueText("No limit")
        number_layout.addRow("Minimum value:", self.min_value_spin)
        
        self.max_value_spin = QDoubleSpinBox()
        self.max_value_spin.setMinimum(-999999)
        self.max_value_spin.setMaximum(999999)
        self.max_value_spin.setSpecialValueText("No limit")
        number_layout.addRow("Maximum value:", self.max_value_spin)
        
        number_constraints.setLayout(number_layout)
        constraints_layout.addWidget(number_constraints)
        
        constraints_group.setLayout(constraints_layout)
        layout.addWidget(constraints_group)
        
        # Create/Update button
        self.create_update_btn = QPushButton("Create Brick")
        self.create_update_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.create_update_btn.clicked.connect(self.create_or_update_brick)
        layout.addWidget(self.create_update_btn)
        
        # Cancel edit button (hidden initially)
        self.cancel_edit_btn = QPushButton("Cancel Edit")
        self.cancel_edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                padding: 8px;
                font-weight: bold;
                border-radius: 6px;
            }
        """)
        self.cancel_edit_btn.clicked.connect(self.cancel_edit)
        self.cancel_edit_btn.hide()
        layout.addWidget(self.cancel_edit_btn)
        
        layout.addStretch()
        
        # Initialize with entity shape
        self.brick_type_combo.setCurrentText("Entity/Class Shape")
        self.on_brick_type_changed("Entity/Class Shape")
        
        return panel
    
    def create_library_panel(self):
        """Create brick library and preview panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Tabs for library and preview
        tabs = QTabWidget()
        
        # Library tab
        library_tab = QWidget()
        library_layout = QVBoxLayout(library_tab)
        
        # Search
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search your bricks...")
        self.search_edit.textChanged.connect(self.search_bricks)
        search_layout.addWidget(self.search_edit)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_bricks)
        search_layout.addWidget(refresh_btn)
        
        library_layout.addLayout(search_layout)
        
        # Brick list
        self.brick_list = QListWidget()
        self.brick_list.itemClicked.connect(self.on_brick_selected)
        library_layout.addWidget(self.brick_list)
        
        # Brick actions
        actions_layout = QHBoxLayout()
        
        edit_btn = QPushButton("Edit")
        edit_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 8px;")
        edit_btn.clicked.connect(self.edit_brick)
        actions_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px;")
        delete_btn.clicked.connect(self.delete_brick)
        actions_layout.addWidget(delete_btn)
        
        export_btn = QPushButton("Export SHACL")
        export_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        export_btn.clicked.connect(self.export_brick)
        actions_layout.addWidget(export_btn)
        
        library_layout.addLayout(actions_layout)
        
        tabs.addTab(library_tab, "My Bricks")
        
        # Preview tab
        preview_tab = QWidget()
        preview_layout = QVBoxLayout(preview_tab)
        
        preview_label = QLabel("SHACL Preview")
        preview_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")
        preview_layout.addWidget(preview_label)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Courier", 10))
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 10px;
                border-radius: 4px;
            }
        """)
        preview_layout.addWidget(self.preview_text)
        
        tabs.addTab(preview_tab, "SHACL Preview")
        
        layout.addWidget(tabs)
        
        return panel
    
    def on_brick_type_changed(self, type_text):
        """Handle brick type change"""
        # Clear existing dynamic fields
        while self.dynamic_layout.count():
            child = self.dynamic_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if type_text == "Entity/Class Shape":
            self.create_entity_fields()
        elif type_text == "Property/Field Shape":
            self.create_property_fields()
    
    def create_entity_fields(self):
        """Create fields for entity/class shapes"""
        group = QGroupBox("Entity Configuration")
        layout = QFormLayout()
        
        # Target class
        self.target_class_edit = QLineEdit()
        self.target_class_edit.setPlaceholderText("e.g., Person, Organization, Product")
        layout.addRow("Entity Type:", self.target_class_edit)
        
        # Node kind with user-friendly names
        self.node_kind_combo = QComboBox()
        self.node_kind_combo.addItems([
            "Can be anything", "Must be a web address (URI)", 
            "Must be text", "Must be a number", "Must be a date"
        ])
        layout.addRow("What kind of thing?:", self.node_kind_combo)
        
        group.setLayout(layout)
        self.dynamic_layout.addWidget(group)
    
    def create_property_fields(self):
        """Create fields for property/field shapes"""
        group = QGroupBox("Property Configuration")
        layout = QFormLayout()
        
        # Property name
        self.property_name_edit = QLineEdit()
        self.property_name_edit.setPlaceholderText("e.g., name, email, phone, address")
        layout.addRow("Property Name:", self.property_name_edit)
        
        # Data type with user-friendly names
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems([
            "Text", "Number", "Email", "URL", "Date", "True/False", "Choice"
        ])
        self.data_type_combo.currentTextChanged.connect(self.on_data_type_changed)
        layout.addRow("Data Type:", self.data_type_combo)
        
        # Choice options (for Choice type)
        self.choice_options_edit = QTextEdit()
        self.choice_options_edit.setPlaceholderText("Option 1\nOption 2\nOption 3")
        self.choice_options_edit.setMaximumHeight(80)
        self.choice_options_edit.setVisible(False)
        layout.addRow("Choice Options:", self.choice_options_edit)
        
        group.setLayout(layout)
        self.dynamic_layout.addWidget(group)
        
        # Initialize with text type
        self.data_type_combo.setCurrentText("Text")
    
    def on_data_type_changed(self, data_type):
        """Handle data type change"""
        # Show/hide choice options based on data type
        self.choice_options_edit.setVisible(data_type == "Choice")
    
    def _ensure_active_library(self):
        """Ensure we have an active library"""
        result = self.processor.process_event({"event": "get_repository_info"})
        if not result["data"]["active_library"]:
            self.processor.process_event({"event": "set_active_library", "library_name": "default"})
    
    def load_bricks(self):
        """Load bricks from library"""
        result = self.processor.process_event({"event": "get_library_bricks"})
        if result["status"] == "success":
            self.brick_list.clear()
            for brick in result["data"]["bricks"]:
                # Convert to user-friendly display
                display_name = self.get_user_friendly_name(brick)
                item = QListWidgetItem(display_name)
                item.setData(Qt.ItemDataRole.UserRole, brick)
                self.brick_list.addItem(item)
        
        self.statusBar().showMessage(f"Loaded {result['data']['count']} bricks")
    
    def get_user_friendly_name(self, brick):
        """Convert brick to user-friendly display name"""
        name = brick['name']
        obj_type = brick['object_type']
        
        if obj_type == "NodeShape":
            return f"🏢 {name}"
        elif obj_type == "PropertyShape":
            return f"📝 {name}"
        else:
            return f"📦 {name}"
    
    def search_bricks(self):
        """Search bricks"""
        query = self.search_edit.text().strip()
        if not query:
            self.load_bricks()
            return
        
        result = self.processor.process_event({"event": "search_bricks", "query": query})
        if result["status"] == "success":
            self.brick_list.clear()
            for brick in result["data"]["bricks"]:
                display_name = self.get_user_friendly_name(brick)
                item = QListWidgetItem(display_name)
                item.setData(Qt.ItemDataRole.UserRole, brick)
                self.brick_list.addItem(item)
        
        self.statusBar().showMessage(f"Found {result['data']['count']} bricks")
    
    def on_brick_selected(self, item):
        """Handle brick selection"""
        brick_data = item.data(Qt.ItemDataRole.UserRole)
        if brick_data:
            self.preview_brick(brick_data)
    
    def preview_brick(self, brick_data):
        """Preview brick in SHACL format"""
        # Show user-friendly details
        details = f"Name: {brick_data['name']}\n"
        details += f"Type: {brick_data['object_type']}\n"
        details += f"Description: {brick_data['description']}\n"
        
        if brick_data['properties']:
            details += "\nProperties:\n"
            for key, value in brick_data['properties'].items():
                details += f"  {key}: {value}\n"
        
        if brick_data['constraints']:
            details += "\nValidation Rules:\n"
            for constraint in brick_data['constraints']:
                friendly_name = self.get_constraint_friendly_name(constraint)
                details += f"  {friendly_name}: {constraint['value']}\n"
        
        self.preview_text.setPlainText(details)
    
    def get_constraint_friendly_name(self, constraint):
        """Convert constraint to user-friendly name"""
        type_map = {
            "MinLengthConstraintComponent": "Minimum length",
            "MaxLengthConstraintComponent": "Maximum length", 
            "MinCountConstraintComponent": "Minimum occurrences",
            "MaxCountConstraintComponent": "Maximum occurrences",
            "PatternConstraintComponent": "Pattern match",
            "MinInclusiveConstraintComponent": "Minimum value",
            "MaxInclusiveConstraintComponent": "Maximum value",
            "DatatypeConstraintComponent": "Data type"
        }
        return type_map.get(constraint["constraint_type"], constraint["constraint_type"])
    
    def create_or_update_brick(self):
        """Create a new brick or update existing one"""
        name = self.brick_name_edit.text().strip()
        description = self.brick_desc_edit.toPlainText().strip()
        
        if not name or not description:
            QMessageBox.warning(self, "Missing Information", 
                           "Please enter both a name and description.")
            return
        
        try:
            if self.editing_brick_id:
                # Update existing brick
                self.update_brick(name, description)
            else:
                # Create new brick
                brick_type = self.brick_type_combo.currentText()
                
                if brick_type == "Entity/Class Shape":
                    self.create_entity_brick(name, description)
                elif brick_type == "Property/Field Shape":
                    self.create_property_brick(name, description)
            
            self.load_bricks()
            self.clear_form()
            
            if self.editing_brick_id:
                self.statusBar().showMessage(f"Updated brick: {name}")
            else:
                self.statusBar().showMessage(f"Created brick: {name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save brick: {str(e)}")
    
    def edit_brick(self):
        """Edit selected brick"""
        current_item = self.brick_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a brick to edit.")
            return
        
        brick_data = current_item.data(Qt.ItemDataRole.UserRole)
        if not brick_data:
            return
        
        # Set editing state
        self.editing_brick_id = brick_data['brick_id']
        self.editing_brick_data = brick_data
        
        # Populate form with brick data
        self.populate_form_from_brick(brick_data)
        
        # Update UI for editing
        self.create_update_btn.setText("Update Brick")
        self.create_update_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 12px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.cancel_edit_btn.show()
        
        self.statusBar().showMessage(f"Editing brick: {brick_data['name']}")
    
    def cancel_edit(self):
        """Cancel editing and clear form"""
        self.clear_form()
        self.statusBar().showMessage("Edit cancelled")
    
    def clear_form(self):
        """Clear the form and reset editing state"""
        self.editing_brick_id = None
        self.editing_brick_data = None
        
        # Clear form fields
        self.brick_name_edit.clear()
        self.brick_desc_edit.clear()
        
        # Reset UI
        self.create_update_btn.setText("Create Brick")
        self.create_update_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.cancel_edit_btn.hide()
        
        # Clear dynamic fields
        self.clear_dynamic_fields()
    
    def clear_dynamic_fields(self):
        """Clear all dynamic field values"""
        # Entity fields
        if hasattr(self, 'target_class_edit'):
            self.target_class_edit.clear()
        
        # Property fields
        if hasattr(self, 'property_name_edit'):
            self.property_name_edit.clear()
        
        # Constraints
        self.required_checkbox.setChecked(False)
        self.min_length_spin.setValue(0)
        self.max_length_spin.setValue(0)
        self.pattern_edit.clear()
        self.min_value_spin.setValue(-999999)
        self.max_value_spin.setValue(999999)
        
        # Choice options
        if hasattr(self, 'choice_options_edit'):
            self.choice_options_edit.clear()
    
    def populate_form_from_brick(self, brick_data):
        """Populate form with brick data for editing"""
        # Basic info
        self.brick_name_edit.setText(brick_data['name'])
        self.brick_desc_edit.setPlainText(brick_data['description'])
        
        # Brick type
        if brick_data['object_type'] == 'NodeShape':
            self.brick_type_combo.setCurrentText("Entity/Class Shape")
        elif brick_data['object_type'] == 'PropertyShape':
            self.brick_type_combo.setCurrentText("Property/Field Shape")
        
        # Trigger type change to show appropriate fields
        self.on_brick_type_changed(self.brick_type_combo.currentText())
        
        # Populate specific fields based on type
        if brick_data['object_type'] == 'NodeShape':
            self.populate_entity_fields(brick_data)
        elif brick_data['object_type'] == 'PropertyShape':
            self.populate_property_fields(brick_data)
        
        # Populate constraints
        self.populate_constraints(brick_data)
    
    def populate_entity_fields(self, brick_data):
        """Populate entity-specific fields"""
        if 'targetClass' in brick_data['properties']:
            self.target_class_edit.setText(brick_data['properties']['targetClass'])
        
        if 'nodeKind' in brick_data['properties']:
            node_kind = brick_data['properties']['nodeKind']
            node_kind_map = {
                "sh:BlankNodeOrIRI": "Can be anything",
                "sh:IRI": "Must be a web address (URI)",
                "sh:Literal": "Must be text"
            }
            friendly_name = node_kind_map.get(node_kind, "Can be anything")
            self.node_kind_combo.setCurrentText(friendly_name)
    
    def populate_property_fields(self, brick_data):
        """Populate property-specific fields"""
        if 'path' in brick_data['properties']:
            self.property_name_edit.setText(brick_data['properties']['path'])
        
        if 'datatype' in brick_data['properties']:
            datatype = brick_data['properties']['datatype']
            data_type_map = {
                "xsd:string": "Text",
                "xsd:decimal": "Number",
                "xsd:anyURI": "URL",
                "xsd:date": "Date",
                "xsd:boolean": "True/False"
            }
            friendly_name = data_type_map.get(datatype, "Text")
            self.data_type_combo.setCurrentText(friendly_name)
        
        # Choice options
        if 'choiceOptions' in brick_data['properties']:
            options = brick_data['properties']['choiceOptions']
            self.choice_options_edit.setPlainText('\n'.join(options))
    
    def populate_constraints(self, brick_data):
        """Populate constraint fields"""
        for constraint in brick_data['constraints']:
            constraint_type = constraint['constraint_type']
            value = constraint['value']
            
            if constraint_type == "MinCountConstraintComponent" and value >= 1:
                self.required_checkbox.setChecked(True)
            elif constraint_type == "MinLengthConstraintComponent":
                self.min_length_spin.setValue(int(value))
            elif constraint_type == "MaxLengthConstraintComponent":
                self.max_length_spin.setValue(int(value))
            elif constraint_type == "PatternConstraintComponent":
                self.pattern_edit.setText(str(value))
            elif constraint_type == "MinInclusiveConstraintComponent":
                self.min_value_spin.setValue(float(value))
            elif constraint_type == "MaxInclusiveConstraintComponent":
                self.max_value_spin.setValue(float(value))
    
    def update_brick(self, name, description):
        """Update existing brick"""
        # First delete the old brick, then create new one with same ID
        # This is simpler than implementing a full update API
        
        # Store old brick data temporarily
        old_brick_data = self.editing_brick_data
        
        # Delete old brick
        delete_result = self.processor.process_event({
            "event": "delete_brick",
            "brick_id": self.editing_brick_id
        })
        
        if delete_result["status"] != "success":
            raise Exception(f"Failed to delete old brick: {delete_result['message']}")
        
        # Create new brick with same ID
        brick_type = self.brick_type_combo.currentText()
        
        if brick_type == "Entity/Class Shape":
            result = self.create_entity_brick(name, description, self.editing_brick_id)
        elif brick_type == "Property/Field Shape":
            result = self.create_property_brick(name, description, self.editing_brick_id)
        
        if result["status"] != "success":
            # Try to restore old brick if update failed
            self.restore_brick(old_brick_data)
            raise Exception(f"Failed to update brick: {result['message']}")
        
        return result
    
    def restore_brick(self, brick_data):
        """Restore a brick if update failed"""
        try:
            # Recreate the original brick
            if brick_data['object_type'] == 'NodeShape':
                self.processor.process_event({
                    "event": "create_nodeshape_brick",
                    "brick_id": brick_data['brick_id'],
                    "name": brick_data['name'],
                    "description": brick_data['description'],
                    "target_class": brick_data['properties'].get('targetClass'),
                    "properties": brick_data['properties'],
                    "tags": brick_data['tags']
                })
            elif brick_data['object_type'] == 'PropertyShape':
                self.processor.process_event({
                    "event": "create_propertyshape_brick",
                    "brick_id": brick_data['brick_id'],
                    "name": brick_data['name'],
                    "description": brick_data['description'],
                    "path": brick_data['properties']['path'],
                    "properties": brick_data['properties'],
                    "constraints": brick_data['constraints'],
                    "tags": brick_data['tags']
                })
        except:
            pass  # Best effort restore
    
    def create_entity_brick(self, name, description, brick_id=None):
        """Create entity/class brick"""
        target_class = self.target_class_edit.text().strip()
        node_kind_map = {
            "Can be anything": "sh:BlankNodeOrIRI",
            "Must be a web address (URI)": "sh:IRI", 
            "Must be text": "sh:Literal",
            "Must be a number": "sh:Literal",
            "Must be a date": "sh:Literal"
        }
        node_kind = node_kind_map.get(self.node_kind_combo.currentText(), "sh:BlankNodeOrIRI")
        
        if brick_id is None:
            brick_id = name.lower().replace(" ", "_")
        
        result = self.processor.process_event({
            "event": "create_nodeshape_brick",
            "brick_id": brick_id,
            "name": name,
            "description": description,
            "target_class": target_class,
            "properties": {"nodeKind": node_kind},
            "tags": ["entity", "user-friendly"]
        })
        
        return result
    
    def create_property_brick(self, name, description, brick_id=None):
        """Create property/field brick"""
        property_name = self.property_name_edit.text().strip()
        if not property_name:
            QMessageBox.warning(self, "Missing Information", 
                           "Please enter a property name.")
            return
        
        # Map data types to SHACL types
        data_type_map = {
            "Text": "xsd:string",
            "Number": "xsd:decimal", 
            "Email": "xsd:string",
            "URL": "xsd:anyURI",
            "Date": "xsd:date",
            "True/False": "xsd:boolean",
            "Choice": "xsd:string"
        }
        
        data_type = self.data_type_combo.currentText()
        datatype = data_type_map.get(data_type, "xsd:string")
        
        if brick_id is None:
            brick_id = name.lower().replace(" ", "_")
        
        # Build constraints
        constraints = []
        
        # Required constraint
        if self.required_checkbox.isChecked():
            constraints.append({
                "constraint_type": "MinCountConstraintComponent",
                "value": 1
            })
        
        # String constraints
        if data_type in ["Text", "Email"]:
            if self.min_length_spin.value() > 0:
                constraints.append({
                    "constraint_type": "MinLengthConstraintComponent",
                    "value": self.min_length_spin.value()
                })
            if self.max_length_spin.value() > 0:
                constraints.append({
                    "constraint_type": "MaxLengthConstraintComponent", 
                    "value": self.max_length_spin.value()
                })
        
        # Email pattern
        if data_type == "Email" and self.pattern_edit.text().strip():
            constraints.append({
                "constraint_type": "PatternConstraintComponent",
                "value": self.pattern_edit.text().strip()
            })
        
        # Number constraints
        if data_type == "Number":
            if self.min_value_spin.value() > -999998:
                constraints.append({
                    "constraint_type": "MinInclusiveConstraintComponent",
                    "value": self.min_value_spin.value()
                })
            if self.max_value_spin.value() < 999998:
                constraints.append({
                    "constraint_type": "MaxInclusiveConstraintComponent",
                    "value": self.max_value_spin.value()
                })
        
        # Choice options
        choice_options = None
        if data_type == "Choice":
            options_text = self.choice_options_edit.toPlainText().strip()
            if options_text:
                choice_options = [opt.strip() for opt in options_text.split('\n') if opt.strip()]
        
        properties = {
            "path": property_name,
            "datatype": datatype
        }
        
        if choice_options:
            properties["choiceOptions"] = choice_options
        
        result = self.processor.process_event({
            "event": "create_propertyshape_brick",
            "brick_id": brick_id,
            "name": name,
            "description": description,
            "path": property_name,
            "properties": properties,
            "constraints": constraints,
            "tags": ["property", "user-friendly", data_type.lower()]
        })
        
        return result
    
    def delete_brick(self):
        """Delete selected brick"""
        current_item = self.brick_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a brick to delete.")
            return
        
        brick_data = current_item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                               f"Are you sure you want to delete '{brick_data['name']}'?",
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            result = self.processor.process_event({
                "event": "delete_brick",
                "brick_id": brick_data['brick_id']
            })
            
            if result["status"] == "success":
                self.load_bricks()
                self.preview_text.clear()
                self.statusBar().showMessage(f"Deleted brick: {brick_data['name']}")
    
    def export_brick(self):
        """Export selected brick to SHACL"""
        current_item = self.brick_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a brick to export.")
            return
        
        brick_data = current_item.data(Qt.ItemDataRole.UserRole)
        
        result = self.processor.process_event({
            "event": "export_brick_shacl",
            "brick_id": brick_data['brick_id'],
            "format_type": "turtle"
        })
        
        if result["status"] == "success":
            # Show in preview
            self.preview_text.setPlainText(result["data"]["content"])
            
            # Offer to save
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export SHACL",
                f"{brick_data['brick_id']}.ttl",
                "Turtle Files (*.ttl);;All Files (*)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w') as f:
                        f.write(result["data"]["content"])
                    self.statusBar().showMessage(f"Exported to: {file_path}")
                except Exception as e:
                    QMessageBox.warning(self, "Save Error", f"Failed to save file: {str(e)}")

def main():
    """Main entry point for user-friendly GUI"""
    app = QApplication(sys.argv)
    gui = UserFriendlyBrickGUI()
    gui.show()
    return app.exec()

if __name__ == "__main__":
    main()
