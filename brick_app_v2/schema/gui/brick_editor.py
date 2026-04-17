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
from .ontology_browser import OntologyBrowserDialog

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
        
        # Property path with dropdown for common options
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.textChanged.connect(self.emit_property_changed)
        path_layout.addWidget(self.path_edit)
        
        # Add dropdown for common property paths
        self.path_combo = QComboBox()
        self.path_combo.setEditable(True)
        self.populate_common_properties()
        self.path_combo.currentTextChanged.connect(self.on_path_selected)
        path_layout.addWidget(self.path_combo)
        
        # Add ontology browser button for properties
        prop_ontology_btn = QPushButton("📚 Browse")
        prop_ontology_btn.setToolTip("Browse ontologies for properties")
        prop_ontology_btn.setMaximumWidth(80)
        prop_ontology_btn.clicked.connect(self.browse_ontologies_for_property)
        path_layout.addWidget(prop_ontology_btn)
        
        basic_layout.addRow("Property:", path_layout)
        
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
    
    def populate_common_properties(self):
        """Populate common property dropdown with user-friendly options"""
        common_props = [
            ("--- Person Properties ---", ""),
            ("First Name", "schema:firstName"),
            ("Last Name", "schema:lastName"),
            ("Full Name", "schema:name"),
            ("Email", "schema:email"),
            ("Phone", "schema:telephone"),
            ("Birth Date", "schema:birthDate"),
            ("Age", "schema:age"),
            ("Gender", "schema:gender"),
            
            ("--- Address Properties ---", ""),
            ("Street Address", "schema:streetAddress"),
            ("City", "schema:addressLocality"),
            ("State/Region", "schema:addressRegion"),
            ("Postal Code", "schema:postalCode"),
            ("Country", "schema:addressCountry"),
            
            ("--- Organization Properties ---", ""),
            ("Organization Name", "schema:legalName"),
            ("Department", "schema:department"),
            ("Employee Count", "schema:numberOfEmployees"),
            ("Website", "schema:url"),
            
            ("--- Product Properties ---", ""),
            ("Product Name", "schema:name"),
            ("Brand", "schema:brand"),
            ("Price", "schema:price"),
            ("Color", "schema:color"),
            ("Size", "schema:size"),
            ("Weight", "schema:weight"),
            
            ("--- Document Properties ---", ""),
            ("Title", "schema:name"),
            ("Description", "schema:description"),
            ("Author", "schema:author"),
            ("Creation Date", "schema:dateCreated"),
            ("Modified Date", "schema:dateModified"),
            
            ("--- Custom ---", ""),
            ("Custom Property", "")
        ]
        
        for display_text, value in common_props:
            if display_text.startswith("---"):
                # Add separator
                self.path_combo.addItem(display_text)
                self.path_combo.model().item(self.path_combo.count() - 1).setEnabled(False)
            else:
                self.path_combo.addItem(display_text, value)
    
    def on_path_selected(self, text):
        """Handle property path selection from dropdown"""
        # Get the data associated with the selected item
        current_data = self.path_combo.currentData()
        if current_data:
            self.path_edit.setText(current_data)
    
    def load_property_data(self):
        """Load existing property data"""
        self.name_edit.setText(self.property_data.get("name", ""))
        self.path_edit.setText(self.property_data.get("path", ""))
        
        # Set path combo if matching value exists
        path_value = self.property_data.get("path", "")
        if path_value:
            for i in range(self.path_combo.count()):
                if self.path_combo.itemData(i) == path_value:
                    self.path_combo.setCurrentIndex(i)
                    break
        
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
        
        # Target class with user-friendly dropdown
        target_class_layout = QHBoxLayout()
        target_class_layout.addWidget(QLabel("What does this brick represent?"))
        
        self.target_class_combo = QComboBox()
        self.target_class_combo.setEditable(True)  # Allow custom entries
        self.populate_target_classes()
        target_class_layout.addWidget(self.target_class_combo)
        
        help_target_btn = QPushButton("?")
        help_target_btn.setFixedSize(20, 20)
        help_target_btn.setToolTip("Click for help with target classes")
        help_target_btn.clicked.connect(self.show_target_class_help)
        target_class_layout.addWidget(help_target_btn)
        
        # Add ontology browser button
        ontology_btn = QPushButton("📚 Browse Ontologies")
        ontology_btn.setToolTip("Browse and select from loaded ontologies")
        ontology_btn.clicked.connect(self.browse_ontologies_for_class)
        target_class_layout.addWidget(ontology_btn)
        
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
    
    def populate_target_classes(self):
        """Populate target class combo with user-friendly options"""
        # Add user-friendly options with technical values
        common_classes = [
            ("--- People ---", ""),
            ("Person (general person)", "schema:Person"),
            ("Student", "schema:Student"),
            ("Employee", "schema:Employee"),
            ("Customer", "schema:Customer"),
            ("Patient", "schema:Patient"),
            ("Teacher", "schema:Teacher"),
            
            ("--- Organizations ---", ""),
            ("Organization (general)", "schema:Organization"),
            ("Company/Corporation", "schema:Corporation"),
            ("School/University", "schema:EducationalOrganization"),
            ("Government", "schema:GovernmentOrganization"),
            
            ("--- Locations ---", ""),
            ("Address", "schema:PostalAddress"),
            ("Place (general)", "schema:Place"),
            ("City/Town", "schema:City"),
            ("Country", "schema:Country"),
            
            ("--- Products & Services ---", ""),
            ("Product (general)", "schema:Product"),
            ("Service", "schema:Service"),
            ("Book", "schema:Book"),
            ("Vehicle", "schema:Vehicle"),
            
            ("--- Events ---", ""),
            ("Event (general)", "schema:Event"),
            ("Meeting", "schema:Meeting"),
            ("Conference", "schema:Conference"),
            
            ("--- Documents & Media ---", ""),
            ("Document", "schema:DigitalDocument"),
            ("Image", "schema:ImageObject"),
            ("Video", "schema:VideoObject"),
            
            ("--- Custom ---", ""),
            ("Custom entity (enter your own)", "")
        ]
        
        for display_text, value in common_classes:
            if display_text.startswith("---"):
                # Add separator
                self.target_class_combo.addItem(display_text)
                self.target_class_combo.model().item(self.target_class_combo.count() - 1).setEnabled(False)
            else:
                self.target_class_combo.addItem(display_text, value)
    
    def load_brick_data(self):
        """Load existing brick data"""
        self.brick_name_edit.setText(self.brick_data.get("name", ""))
        self.object_type_combo.setCurrentText(self.brick_data.get("object_type", "NodeShape"))
        
        # Set target class from combo box
        target_class = self.brick_data.get("target_class", "")
        if target_class:
            # Find matching item in combo
            for i in range(self.target_class_combo.count()):
                if self.target_class_combo.itemData(i) == target_class:
                    self.target_class_combo.setCurrentIndex(i)
                    break
            else:
                # If not found, set as custom text
                self.target_class_combo.setCurrentText(target_class)
        
        self.description_edit.setPlainText(self.brick_data.get("description", ""))
        
        # Load properties - handle both dict and list formats
        properties = self.brick_data.get("properties", {})
        if isinstance(properties, dict):
            # Convert dict to list format for the editor
            for prop_name, prop_data in properties.items():
                prop_data_for_editor = {
                    "name": prop_name,
                    "path": prop_data.get("path", ""),
                    "datatype": prop_data.get("datatype", "xsd:string"),
                    "constraints": prop_data.get("constraints", [])
                }
                self.add_property(prop_data_for_editor)
        elif isinstance(properties, list):
            # Handle legacy list format
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
        # Convert property list to dictionary format expected by backend
        properties_dict = {}
        for editor in self.property_editors:
            if not editor.isHidden():  # Skip removed editors
                prop_data = editor.get_property_data()
                prop_name = prop_data.get("name", "")
                if prop_name:
                    properties_dict[prop_name] = {
                        "path": prop_data.get("path", ""),
                        "datatype": prop_data.get("datatype", "xsd:string"),
                        "constraints": prop_data.get("constraints", [])
                    }
        
        # Get target class from combo
        target_class = self.target_class_combo.currentData()
        if not target_class:
            # Use custom text if no data associated
            target_class = self.target_class_combo.currentText().strip()
        
        return {
            "brick_id": self.brick_data.get("brick_id", str(uuid.uuid4())),
            "name": self.brick_name_edit.text(),
            "object_type": self.object_type_combo.currentText(),
            "target_class": target_class,
            "description": self.description_edit.toPlainText(),
            "properties": properties_dict,
            "constraints": [],  # Brick-level constraints
            "metadata": {}
        }
    
    def accept_dialog(self):
        """Handle dialog acceptance"""
        brick_data = self.get_brick_data()
        
        # Basic validation
        if not brick_data["name"].strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a brick name")
            return
        
        # Allow empty properties for new bricks (they can be added later)
        # Only validate properties if we're editing an existing brick with properties
        existing_props = self.brick_data.get("properties", {})
        current_props = brick_data.get("properties", {})
        
        # Check if we're editing an existing brick that had properties
        if self.brick_data and isinstance(existing_props, dict) and existing_props and not current_props:
            QMessageBox.warning(self, "Validation Error", "Please add at least one property")
            return
        
        self.brick_data = brick_data
        self.accept()
    
    def show_target_class_help(self):
        """Show help dialog for target classes"""
        help_text = """
# What Does This Brick Represent?

## Simple Explanation
Think of a "Target Class" as telling the system: **"What kind of thing am I describing?"**

## Easy Examples

### For People:
- **Person** - General information about any person
- **Student** - Someone who studies at a school
- **Employee** - Someone who works for a company
- **Customer** - Someone who buys products/services
- **Patient** - Someone receiving medical care

### For Organizations:
- **Organization** - Any company, club, or group
- **Company** - A business or corporation
- **School** - Educational institution

### For Places:
- **Address** - Street address information
- **Place** - Any location or venue
- **City** - A town or city

### For Products:
- **Product** - Any item you can buy
- **Service** - Something someone does for you
- **Book** - A book or publication

### For Events:
- **Event** - Any happening or occasion
- **Meeting** - A scheduled get-together

## How to Use
1. **Pick from the dropdown** - Choose the closest match
2. **Don't see what you need?** - Type your own description
3. **Not sure?** - Start with "Person" or "Organization"

## Real Examples
- Creating a student form? Choose "Student"
- Making an address book? Choose "Address" 
- Describing a product? Choose "Product"
- Building a contact list? Choose "Person"

**Tip:** The dropdown shows the most common options. You can also type anything that describes what you're working with!
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
    
    def browse_ontologies_for_class(self):
        """Browse ontologies to select target class"""
        dialog = OntologyBrowserDialog(self)
        dialog.term_selected.connect(self.on_class_selected_from_ontology)
        dialog.exec()
    
    def browse_ontologies_for_property(self):
        """Browse ontologies to select property"""
        dialog = OntologyBrowserDialog(self)
        dialog.term_selected.connect(self.on_property_selected_from_ontology)
        dialog.exec()
    
    def on_class_selected_from_ontology(self, term_type: str, name: str, uri: str):
        """Handle class selection from ontology browser"""
        if term_type == "class":
            # Set the target class
            self.target_class_combo.setCurrentText(uri)
            # Also update the brick name if it's empty
            if not self.brick_name_edit.text().strip():
                self.brick_name_edit.setText(name + " Shape")
    
    def on_property_selected_from_ontology(self, term_type: str, name: str, uri: str):
        """Handle property selection from ontology browser"""
        if term_type == "property":
            # Find the current property editor (from the parent tab)
            current_tab = self.parent().parent().properties_tabs.currentWidget()
            if current_tab and hasattr(current_tab, 'path_edit'):
                current_tab.path_edit.setText(uri)
                current_tab.name_edit.setText(name)

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
