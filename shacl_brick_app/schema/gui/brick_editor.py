#!/usr/bin/env python3
"""
Advanced Brick Editor for creating complex SHACL bricks
Supports detailed property definition with constraints
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import Dict, List, Any, Optional
import uuid

class ConstraintEditor(QWidget):
    """Widget for editing SHACL constraints"""
    
    constraint_changed = pyqtSignal(dict)
    
    def __init__(self, constraint_data: Dict[str, Any] = None):
        super().__init__()
        self.constraint_data = constraint_data or {}
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout(self)
        
        # Constraint type
        self.constraint_type_combo = QComboBox()
        self.constraint_type_combo.addItems([
            "datatype", "minCount", "maxCount", "minLength", "maxLength",
            "pattern", "minInclusive", "maxInclusive", "description", "example"
        ])
        self.constraint_type_combo.currentTextChanged.connect(self.on_constraint_type_changed)
        layout.addRow("Type:", self.constraint_type_combo)
        
        # Value input
        self.value_stack = QStackedWidget()
        
        # String input (for most constraints)
        self.string_input = QLineEdit()
        self.string_input.textChanged.connect(self.emit_constraint_changed)
        self.value_stack.addWidget(self.string_input)
        
        # Number input (for numeric constraints)
        self.number_input = QSpinBox()
        self.number_input.setRange(0, 999999)
        self.number_input.valueChanged.connect(self.emit_constraint_changed)
        self.value_stack.addWidget(self.number_input)
        
        # Text area (for descriptions/examples)
        self.text_input = QTextEdit()
        self.text_input.setMaximumHeight(80)
        self.text_input.textChanged.connect(self.emit_constraint_changed)
        self.value_stack.addWidget(self.text_input)
        
        # Date input (for date constraints)
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.dateChanged.connect(self.emit_constraint_changed)
        self.value_stack.addWidget(self.date_input)
        
        layout.addRow("Value:", self.value_stack)
        
        # Remove button
        remove_btn = QPushButton("Remove Constraint")
        remove_btn.clicked.connect(self.remove_constraint)
        layout.addRow(remove_btn)
        
        # Load existing data
        if self.constraint_data:
            self.load_constraint_data()
    
    def on_constraint_type_changed(self, constraint_type: str):
        """Handle constraint type change"""
        if constraint_type in ["minCount", "maxCount", "minLength", "maxLength"]:
            self.value_stack.setCurrentWidget(self.number_input)
        elif constraint_type in ["description", "example"]:
            self.value_stack.setCurrentWidget(self.text_input)
        elif constraint_type in ["minInclusive", "maxInclusive"]:
            self.value_stack.setCurrentWidget(self.date_input)
        else:
            self.value_stack.setCurrentWidget(self.string_input)
    
    def load_constraint_data(self):
        """Load existing constraint data"""
        constraint_type = self.constraint_data.get("constraint_type", "datatype")
        self.constraint_type_combo.setCurrentText(constraint_type)
        self.on_constraint_type_changed(constraint_type)
        
        value = self.constraint_data.get("value", "")
        if constraint_type in ["minCount", "maxCount", "minLength", "maxLength"]:
            self.number_input.setValue(int(value) if value.isdigit() else 0)
        elif constraint_type in ["description", "example"]:
            self.text_input.setPlainText(value)
        elif constraint_type in ["minInclusive", "maxInclusive"]:
            # Parse date value
            pass  # Implement date parsing
        else:
            self.string_input.setText(value)
    
    def get_constraint_data(self) -> Dict[str, Any]:
        """Get current constraint data"""
        constraint_type = self.constraint_type_combo.currentText()
        current_widget = self.value_stack.currentWidget()
        
        if current_widget == self.number_input:
            value = str(self.number_input.value())
        elif current_widget == self.text_input:
            value = self.text_input.toPlainText()
        elif current_widget == self.date_input:
            value = self.date_input.date().toString("yyyy-MM-dd")
        else:
            value = self.string_input.text()
        
        return {
            "constraint_type": constraint_type,
            "value": value
        }
    
    def emit_constraint_changed(self):
        """Emit constraint changed signal"""
        self.constraint_changed.emit(self.get_constraint_data())
    
    def remove_constraint(self):
        """Remove this constraint"""
        self.deleteLater()

class PropertyEditor(QWidget):
    """Widget for editing brick properties"""
    
    property_changed = pyqtSignal(dict)
    
    def __init__(self, property_data: Dict[str, Any] = None):
        super().__init__()
        self.property_data = property_data or {}
        self.constraint_editors = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Property basic info
        basic_group = QGroupBox("Property Information")
        basic_layout = QFormLayout(basic_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self.emit_property_changed)
        basic_layout.addRow("Name:", self.name_edit)
        
        self.path_edit = QLineEdit()
        self.path_edit.textChanged.connect(self.emit_property_changed)
        basic_layout.addRow("Path:", self.path_edit)
        
        self.datatype_combo = QComboBox()
        self.datatype_combo.addItems([
            "xsd:string", "xsd:integer", "xsd:decimal", "xsd:boolean",
            "xsd:date", "xsd:anyURI", "xsd:email"
        ])
        self.datatype_combo.currentTextChanged.connect(self.emit_property_changed)
        basic_layout.addRow("Data Type:", self.datatype_combo)
        
        layout.addWidget(basic_group)
        
        # Constraints section
        constraints_group = QGroupBox("Constraints")
        constraints_layout = QVBoxLayout(constraints_group)
        
        # Add constraint button
        add_constraint_btn = QPushButton("Add Constraint")
        add_constraint_btn.clicked.connect(self.add_constraint)
        constraints_layout.addWidget(add_constraint_btn)
        
        # Constraints scroll area
        self.constraints_scroll = QScrollArea()
        self.constraints_widget = QWidget()
        self.constraints_layout = QVBoxLayout(self.constraints_widget)
        self.constraints_scroll.setWidget(self.constraints_widget)
        self.constraints_scroll.setWidgetResizable(True)
        self.constraints_scroll.setMaximumHeight(300)
        constraints_layout.addWidget(self.constraints_scroll)
        
        layout.addWidget(constraints_group)
        
        # Load existing data
        if self.property_data:
            self.load_property_data()
    
    def load_property_data(self):
        """Load existing property data"""
        self.name_edit.setText(self.property_data.get("name", ""))
        self.path_edit.setText(self.property_data.get("path", ""))
        
        datatype = self.property_data.get("datatype", "xsd:string")
        self.datatype_combo.setCurrentText(datatype)
        
        # Load constraints
        constraints = self.property_data.get("constraints", [])
        for constraint in constraints:
            self.add_constraint(constraint)
    
    def add_constraint(self, constraint_data: Dict[str, Any] = None):
        """Add a new constraint editor"""
        constraint_editor = ConstraintEditor(constraint_data)
        constraint_editor.constraint_changed.connect(self.emit_property_changed)
        
        # Add to layout
        self.constraints_layout.addWidget(constraint_editor)
        self.constraint_editors.append(constraint_editor)
        
        self.emit_property_changed()
    
    def get_property_data(self) -> Dict[str, Any]:
        """Get current property data"""
        constraints = []
        for editor in self.constraint_editors:
            if not editor.isHidden():  # Skip removed editors
                constraints.append(editor.get_constraint_data())
        
        return {
            "name": self.name_edit.text(),
            "path": self.path_edit.text(),
            "datatype": self.datatype_combo.currentText(),
            "constraints": constraints
        }
    
    def emit_property_changed(self):
        """Emit property changed signal"""
        self.property_changed.emit(self.get_property_data())

class BrickEditorDialog(QDialog):
    """Dialog for creating/editing complex bricks"""
    
    def __init__(self, brick_data: Dict[str, Any] = None, parent=None):
        super().__init__(parent)
        self.brick_data = brick_data or {}
        self.property_editors = []
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Advanced Brick Editor")
        self.setGeometry(100, 100, 800, 600)
        layout = QVBoxLayout(self)
        
        # Brick basic info
        basic_group = QGroupBox("Brick Information")
        basic_layout = QFormLayout(basic_group)
        
        self.brick_name_edit = QLineEdit()
        basic_layout.addRow("Brick Name:", self.brick_name_edit)
        
        self.object_type_combo = QComboBox()
        self.object_type_combo.addItems(["NodeShape", "PropertyShape"])
        basic_layout.addRow("Object Type:", self.object_type_combo)
        
        # Target class with help
        target_class_layout = QHBoxLayout()
        self.target_class_edit = QLineEdit()
        target_class_layout.addWidget(QLabel("Target Class:"))
        target_class_layout.addWidget(self.target_class_edit)
        
        help_target_btn = QPushButton("?")
        help_target_btn.setFixedSize(20, 20)
        help_target_btn.setToolTip("Click for help with target classes")
        help_target_btn.clicked.connect(self.show_target_class_help)
        target_class_layout.addWidget(help_target_btn)
        
        basic_layout.addRow(target_class_layout)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        basic_layout.addRow("Description:", self.description_edit)
        
        layout.addWidget(basic_group)
        
        # Properties section
        properties_group = QGroupBox("Properties")
        properties_layout = QVBoxLayout(properties_group)
        
        # Add property button with help
        add_property_layout = QHBoxLayout()
        add_property_btn = QPushButton("Add Property")
        add_property_btn.clicked.connect(self.add_property)
        add_property_layout.addWidget(add_property_btn)
        
        help_properties_btn = QPushButton("?")
        help_properties_btn.setFixedSize(20, 20)
        help_properties_btn.setToolTip("Click for help with properties")
        help_properties_btn.clicked.connect(self.show_properties_help)
        add_property_layout.addWidget(help_properties_btn)
        add_property_layout.addStretch()
        
        properties_layout.addLayout(add_property_layout)
        
        # Properties tabs
        self.properties_tabs = QTabWidget()
        properties_layout.addWidget(self.properties_tabs)
        
        layout.addWidget(properties_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept_dialog)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Load existing data
        if self.brick_data:
            self.load_brick_data()
    
    def load_brick_data(self):
        """Load existing brick data"""
        self.brick_name_edit.setText(self.brick_data.get("name", ""))
        self.object_type_combo.setCurrentText(self.brick_data.get("object_type", "NodeShape"))
        self.target_class_edit.setText(self.brick_data.get("target_class", ""))
        self.description_edit.setPlainText(self.brick_data.get("description", ""))
        
        # Load properties
        properties = self.brick_data.get("properties", [])
        for prop_data in properties:
            self.add_property(prop_data)
    
    def add_property(self, property_data: Dict[str, Any] = None):
        """Add a new property editor"""
        # Ensure property_data is a dictionary
        if property_data is None or not isinstance(property_data, dict):
            property_data = {}
        
        property_editor = PropertyEditor(property_data)
        
        # Create tab
        tab_index = self.properties_tabs.addTab(property_editor, 
                                               property_data.get("name", f"Property {self.properties_tabs.count() + 1}"))
        
        # Update tab name when property name changes
        property_editor.property_changed.connect(
            lambda data, idx=tab_index: self.update_property_tab_name(idx, data)
        )
        
        self.property_editors.append(property_editor)
        self.properties_tabs.setCurrentIndex(tab_index)
    
    def update_property_tab_name(self, tab_index: int, property_data: Dict[str, Any]):
        """Update property tab name"""
        name = property_data.get("name", f"Property {tab_index + 1}")
        self.properties_tabs.setTabText(tab_index, name)
    
    def get_brick_data(self) -> Dict[str, Any]:
        """Get current brick data"""
        properties = []
        for editor in self.property_editors:
            if not editor.isHidden():  # Skip removed editors
                properties.append(editor.get_property_data())
        
        return {
            "brick_id": self.brick_data.get("brick_id", str(uuid.uuid4())),
            "name": self.brick_name_edit.text(),
            "object_type": self.object_type_combo.currentText(),
            "target_class": self.target_class_edit.text(),
            "description": self.description_edit.toPlainText(),
            "properties": properties,
            "constraints": [],  # Brick-level constraints
            "metadata": {}
        }
    
    def accept_dialog(self):
        """Handle dialog acceptance"""
        brick_data = self.get_brick_data()
        
        # Basic validation
        if not brick_data["name"]:
            QMessageBox.warning(self, "Validation Error", "Please enter a brick name")
            return
        
        if not brick_data["properties"]:
            QMessageBox.warning(self, "Validation Error", "Please add at least one property")
            return
        
        self.brick_data = brick_data
        self.accept()
    
    def show_target_class_help(self):
        """Show help dialog for target classes"""
        help_text = """
# Target Classes Help

## What is a Target Class?
A target class defines what type of entity your brick represents.

## Common Target Classes:

### Person-Related:
- schema:Person - General person
- schema:Student - Student
- schema:Employee - Employee
- schema:Customer - Customer
- schema:Patient - Patient

### Organization:
- schema:Organization - General organization
- schema:Corporation - Company
- schema:EducationalOrganization - School

### Location:
- schema:PostalAddress - Mailing address
- schema:Place - General place
- schema:City - City/town

### Product:
- schema:Product - General product
- schema:Service - Service offering
- schema:Book - Book

### Event:
- schema:Event - General event
- schema:Meeting - Meeting
- schema:Conference - Conference

## Custom Classes:
You can also create your own:
- ex:StudentRecord - Student record
- ex:ProjectProposal - Project proposal

## Examples:
- schema:Person (for person information)
- schema:PostalAddress (for address data)
- schema:Product (for product details)
        """
        
        dialog = HelpDialog("Target Classes Help", help_text, self)
        dialog.exec()
    
    def show_properties_help(self):
        """Show help dialog for properties"""
        help_text = """
# Properties Help

## Common Property Types:

### Text/String:
- schema:name - Name/title
- schema:firstName - First name
- schema:lastName - Last name
- schema:description - Description
- schema:email - Email address
- schema:telephone - Phone number

### Numeric:
- schema:age - Age
- schema:price - Price/amount
- schema:weight - Weight
- schema:height - Height

### Date/Time:
- schema:birthDate - Birth date
- schema:date - General date
- schema:dateTime - Date and time
- schema:startDate - Start date
- schema:endDate - End date

### Boolean:
- schema:isActive - Active status
- schema:isRequired - Required field

### URL/URI:
- schema:url - Website URL
- schema:image - Image URL
- schema:website - Website

### Address Properties:
- schema:streetAddress - Street address
- schema:addressLocality - City
- schema:addressRegion - State/region
- schema:postalCode - ZIP/Postal code
- schema:addressCountry - Country

### Relationships:
- schema:parent - Parent relationship
- schema:child - Child relationship
- schema:employer - Employer
- schema:employee - Employee
- schema:member - Member of

### Product Properties:
- schema:brand - Brand name
- schema:manufacturer - Manufacturer
- schema:model - Model number
- schema:color - Color
- schema:size - Size

## Constraint Examples:

### Required Field:
- minCount: 1 (required)
- maxCount: 1 (single value only)

### Text Validation:
- pattern: ^[A-Z][a-z]*$ (capital first letter)
- minLength: 3 (minimum 3 characters)
- maxLength: 50 (maximum 50 characters)

### Email Validation:
- pattern: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$

### Phone Validation:
- pattern: ^\\+?[0-9]{3}-?[0-9]{3}-?[0-9]{4}$

### ZIP Code:
- pattern: ^\\d{5}(-\\d{4})?$ (US ZIP)
- pattern: ^[A-Z]{1}[0-9]{1}[A-Z]{1} [0-9]{1}[A-Z]{1}[0-9]{1}$ (Canada)

### Numeric Ranges:
- minInclusive: 0 (minimum value)
- maxInclusive: 100 (maximum value)

### Date Ranges:
- minInclusive: 1900-01-01 (earliest date)
- maxInclusive: 2025-12-31 (latest date)

## Common Patterns:

### Person Brick:
- firstName (required, capital first letter)
- lastName (required, capital first letter)
- email (optional, email format)
- birthDate (optional, reasonable date range)

### Address Brick:
- streetAddress (required, max 200 chars)
- city (required, max 100 chars)
- postalCode (required, ZIP format)
- country (required, 2-letter code)

### Product Brick:
- name (required, max 100 chars)
- description (optional, max 500 chars)
- price (optional, positive number)
- brand (optional, max 50 chars)
        """
        
        dialog = HelpDialog("Properties Help", help_text, self)
        dialog.exec()

class HelpDialog(QDialog):
    """Dialog for displaying help information"""
    
    def __init__(self, title: str, help_text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(600, 500)
        self.init_ui(help_text)
    
    def init_ui(self, help_text: str):
        layout = QVBoxLayout(self)
        
        # Help text display
        text_widget = QTextEdit()
        text_widget.setPlainText(help_text)
        text_widget.setReadOnly(True)
        text_widget.setFont(QFont("Courier", 10))
        layout.addWidget(text_widget)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

# Template generators for Person and Address bricks
def create_person_brick_template() -> Dict[str, Any]:
    """Create a Person brick template"""
    return {
        "brick_id": str(uuid.uuid4()),
        "name": "Person",
        "object_type": "NodeShape",
        "target_class": "schema:Person",
        "description": "A person with basic personal information",
        "properties": [
            {
                "name": "first name",
                "path": "schema:firstName",
                "datatype": "xsd:string",
                "constraints": [
                    {"constraint_type": "datatype", "value": "xsd:string"},
                    {"constraint_type": "minCount", "value": "1"},
                    {"constraint_type": "pattern", "value": "^[A-Z][a-z]*$"},
                    {"constraint_type": "description", "value": "Name"}
                ]
            },
            {
                "name": "last name",
                "path": "schema:lastName",
                "datatype": "xsd:string",
                "constraints": [
                    {"constraint_type": "datatype", "value": "xsd:string"},
                    {"constraint_type": "minCount", "value": "1"},
                    {"constraint_type": "maxCount", "value": "1"},
                    {"constraint_type": "maxLength", "value": "20"},
                    {"constraint_type": "pattern", "value": "^[A-Z][a-z]*$"},
                    {"constraint_type": "description", "value": "Familyname"}
                ]
            },
            {
                "name": "date of birth",
                "path": "schema:birthDate",
                "datatype": "xsd:date",
                "constraints": [
                    {"constraint_type": "datatype", "value": "xsd:date"},
                    {"constraint_type": "minInclusive", "value": "1990-01-01"},
                    {"constraint_type": "maxInclusive", "value": "2025-12-31"},
                    {"constraint_type": "maxCount", "value": "1"},
                    {"constraint_type": "example", "value": "1985-07-23"}
                ]
            },
            {
                "name": "social security number",
                "path": "schema:ssn",
                "datatype": "xsd:string",
                "constraints": [
                    {"constraint_type": "datatype", "value": "xsd:string"},
                    {"constraint_type": "pattern", "value": "^\\d{3}-\\d{2}-\\d{4}$"},
                    {"constraint_type": "maxCount", "value": "1"},
                    {"constraint_type": "description", "value": "123-45-6789"}
                ]
            }
        ],
        "constraints": [],
        "metadata": {}
    }

def create_address_brick_template() -> Dict[str, Any]:
    """Create an Address brick template"""
    return {
        "brick_id": str(uuid.uuid4()),
        "name": "Address",
        "object_type": "NodeShape",
        "target_class": "schema:PostalAddress",
        "description": "A postal address with street, city, and country information",
        "properties": [
            {
                "name": "street address",
                "path": "schema:streetAddress",
                "datatype": "xsd:string",
                "constraints": [
                    {"constraint_type": "datatype", "value": "xsd:string"},
                    {"constraint_type": "minCount", "value": "1"},
                    {"constraint_type": "maxLength", "value": "200"}
                ]
            },
            {
                "name": "house number",
                "path": "ex:houseNumber",
                "datatype": "xsd:string",
                "constraints": [
                    {"constraint_type": "datatype", "value": "xsd:string"},
                    {"constraint_type": "pattern", "value": "^[0-9]+[a-zA-Z]*$"},
                    {"constraint_type": "maxCount", "value": "1"}
                ]
            },
            {
                "name": "postal code",
                "path": "schema:postalCode",
                "datatype": "xsd:string",
                "constraints": [
                    {"constraint_type": "datatype", "value": "xsd:string"},
                    {"constraint_type": "minCount", "value": "1"},
                    {"constraint_type": "pattern", "value": "^[0-9]{5}(-[0-9]{4})?$"}
                ]
            },
            {
                "name": "city",
                "path": "schema:addressLocality",
                "datatype": "xsd:string",
                "constraints": [
                    {"constraint_type": "datatype", "value": "xsd:string"},
                    {"constraint_type": "minCount", "value": "1"},
                    {"constraint_type": "maxLength", "value": "100"}
                ]
            },
            {
                "name": "country",
                "path": "schema:addressCountry",
                "datatype": "xsd:string",
                "constraints": [
                    {"constraint_type": "datatype", "value": "xsd:string"},
                    {"constraint_type": "minCount", "value": "1"},
                    {"constraint_type": "maxLength", "value": "2"},
                    {"constraint_type": "pattern", "value": "^[A-Z]{2}$"}
                ]
            }
        ],
        "constraints": [],
        "metadata": {}
    }
