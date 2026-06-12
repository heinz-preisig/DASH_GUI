#!/usr/bin/env python3
"""
Simple Qt Implementation of Editor Frontend Interfaces
Clean separation of frontend and backend concerns
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, 
    QTextEdit, QComboBox, QPushButton, QLabel, QMessageBox,
    QDialog, QListWidget, QListWidgetItem, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Dict, List, Any, Optional, Tuple
from ..interfaces.editor_frontend import (
    BrickEditorFrontend, OntologyBrowserFrontend, 
    PropertyEditorFrontend, SimpleFormFrontend,
    SelectionDialogFrontend
)

class SimpleBrickEditor(BrickEditorFrontend):
    """Simple Qt implementation of brick editor frontend"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.widget = QWidget(parent)
        self.property_editors = []
        self.available_properties = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self.widget)
        
        # Basic information form
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        form_layout.addRow("Name:", self.name_edit)
        
        self.object_type_combo = QComboBox()
        self.object_type_combo.addItems(["NodeShape", "PropertyShape"])
        form_layout.addRow("Type:", self.object_type_combo)
        
        # Target class with ontology browser
        target_layout = QHBoxLayout()
        self.target_class_edit = QLineEdit()
        target_layout.addWidget(QLabel("Target Class:"))
        target_layout.addWidget(self.target_class_edit)
        
        self.browse_ontology_btn = QPushButton("Browse Ontologies")
        self.browse_ontology_btn.clicked.connect(self.browse_ontologies)
        target_layout.addWidget(self.browse_ontology_btn)
        
        form_layout.addRow(target_layout)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Properties section
        self.properties_widget = QWidget()
        self.properties_layout = QVBoxLayout(self.properties_widget)
        layout.addWidget(self.properties_widget)
        
        # Add property button
        add_prop_btn = QPushButton("Add Property")
        add_prop_btn.clicked.connect(self.add_property)
        layout.addWidget(add_prop_btn)
    
    def get_widget(self):
        """Get the main widget"""
        return self.widget
    
    def display_brick(self, brick_data: Dict[str, Any]) -> None:
        """Display brick data in frontend"""
        self.name_edit.setText(brick_data.get("name", ""))
        self.object_type_combo.setCurrentText(brick_data.get("object_type", "NodeShape"))
        self.target_class_edit.setText(brick_data.get("target_class", ""))
        self.description_edit.setPlainText(brick_data.get("description", ""))
        
        # Clear and reload properties
        self.clear_properties()
        properties = brick_data.get("properties", {})
        for prop_name, prop_data in properties.items():
            self.add_property_editor(prop_name, prop_data)
    
    def get_brick_data(self) -> Dict[str, Any]:
        """Get current brick data from frontend"""
        properties = {}
        for editor in self.property_editors:
            prop_data = editor.get_property_data()
            prop_name = prop_data.get("name", "")
            if prop_name:
                properties[prop_name] = {
                    "path": prop_data.get("path", ""),
                    "datatype": prop_data.get("datatype", "xsd:string"),
                    "constraints": prop_data.get("constraints", [])
                }
        
        return {
            "name": self.name_edit.text(),
            "object_type": self.object_type_combo.currentText(),
            "target_class": self.target_class_edit.text(),
            "description": self.description_edit.toPlainText(),
            "properties": properties,
            "constraints": [],
            "metadata": {}
        }
    
    def show_error(self, message: str) -> None:
        """Display error message to user"""
        QMessageBox.critical(self.widget, "Error", message)
    
    def show_success(self, message: str) -> None:
        """Display success message to user"""
        QMessageBox.information(self.widget, "Success", message)
    
    def set_target_class_options(self, options: List[Dict[str, str]]) -> None:
        """Set available target class options"""
        # For simple implementation, we could add a dropdown
        # For now, user can type or browse ontologies
        pass
    
    def set_property_options(self, options: List[Dict[str, str]]) -> None:
        """Set available property options"""
        self.available_properties = options
    
    def browse_ontologies(self):
        """Browse ontologies for target class selection"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout
        from ..gui.simple_editor import SimpleOntologyBrowser
        
        # Create dialog
        parent_widget = self.parent.get_widget() if hasattr(self.parent, 'get_widget') else None
        dialog = QDialog(parent_widget)
        dialog.setWindowTitle("Browse Ontologies")
        dialog.setModal(True)
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Create ontology browser
        browser = SimpleOntologyBrowser(self.parent)
        browser.display_ontologies(self.available_properties if hasattr(self, 'available_properties') else [])
        layout.addWidget(browser.get_widget())
        
        # Store reference to this editor for callback
        browser.brick_editor = self
        
        dialog.exec()
    
    def add_property(self):
        """Add a new property editor"""
        self.add_property_editor("", {})
    
    def add_property_editor(self, prop_name: str, prop_data: Dict[str, Any]):
        """Add a property editor widget"""
        editor = SimplePropertyEditor()
        editor.display_property({"name": prop_name, **prop_data})
        self.property_editors.append(editor)
        self.properties_layout.addWidget(editor.get_widget())
    
    def clear_properties(self):
        """Clear all property editors"""
        for editor in self.property_editors:
            self.properties_layout.removeWidget(editor.get_widget())
        self.property_editors.clear()

class SimplePropertyEditor(PropertyEditorFrontend):
    """Simple Qt implementation of property editor frontend"""
    
    def __init__(self):
        self.widget = QWidget()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QFormLayout(self.widget)
        
        self.name_edit = QLineEdit()
        layout.addRow("Name:", self.name_edit)
        
        self.path_edit = QLineEdit()
        layout.addRow("Path:", self.path_edit)
        
        self.datatype_combo = QComboBox()
        self.datatype_combo.addItems([
            "xsd:string", "xsd:integer", "xsd:decimal", "xsd:boolean",
            "xsd:date", "xsd:anyURI"
        ])
        layout.addRow("Data Type:", self.datatype_combo)
        
        # Remove button
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self.remove_self)
        layout.addRow(self.remove_btn)
    
    def get_widget(self):
        """Get the main widget"""
        return self.widget
    
    def display_property(self, property_data: Dict[str, Any]) -> None:
        """Display property data"""
        self.name_edit.setText(property_data.get("name", ""))
        self.path_edit.setText(property_data.get("path", ""))
        self.datatype_combo.setCurrentText(property_data.get("datatype", "xsd:string"))
    
    def get_property_data(self) -> Dict[str, Any]:
        """Get current property data"""
        return {
            "name": self.name_edit.text(),
            "path": self.path_edit.text(),
            "datatype": self.datatype_combo.currentText(),
            "constraints": []
        }
    
    def set_constraint_types(self, types: List[str]) -> None:
        """Set available constraint types"""
        pass  # Could add constraint editing
    
    def set_data_types(self, types: List[str]) -> None:
        """Set available data types"""
        self.datatype_combo.clear()
        self.datatype_combo.addItems(types)
    
    def remove_self(self):
        """Remove this property editor"""
        self.widget.deleteLater()

class SimpleSelectionDialog(SelectionDialogFrontend):
    """Simple Qt implementation of selection dialog"""
    
    def __init__(self, parent=None):
        self.parent = parent
    
    def show_selection(self, title: str, items: List[Dict[str, str]], 
                   allow_multiple: bool = False) -> List[Dict[str, str]]:
        """Show selection dialog and return selected items"""
        dialog = QDialog(self.parent)
        dialog.setWindowTitle(title)
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        # List widget
        list_widget = QListWidget()
        for item in items:
            list_item = QListWidgetItem(f"{item.get('name', '')} ({item.get('ontology', '')})")
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            list_widget.addItem(list_item)
        
        if allow_multiple:
            list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
        layout.addWidget(list_widget)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_items = list_widget.selectedItems()
            return [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]
        
        return []

class SimpleOntologyBrowser(OntologyBrowserFrontend):
    """Simple Qt implementation of ontology browser frontend"""
    
    def __init__(self, parent=None):
        self.widget = QWidget()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self.widget)
        
        # Ontology list
        self.ontology_list = QListWidget()
        self.ontology_list.itemClicked.connect(self.on_ontology_selected)
        layout.addWidget(QLabel("Available Ontologies:"))
        layout.addWidget(self.ontology_list)
        
        # Terms list
        self.terms_list = QListWidget()
        self.terms_list.itemDoubleClicked.connect(self.on_term_selected)
        layout.addWidget(QLabel("Classes and Properties:"))
        layout.addWidget(self.terms_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        use_btn = QPushButton("Use Selected")
        use_btn.clicked.connect(self.use_selected)
        button_layout.addWidget(use_btn)
        layout.addLayout(button_layout)
    
    def get_widget(self):
        """Get the main widget"""
        return self.widget
    
    def display_ontologies(self, ontologies) -> None:
        """Display available ontologies"""
        self.ontology_list.clear()
        self.ontologies = ontologies
        
        # Handle both dict and list formats
        if isinstance(ontologies, dict):
            items = ontologies.items()
        else:
            items = [(name, data) for name, data in ontologies]
        
        for name, data in items:
            class_count = len(data.get('classes', []))
            prop_count = len(data.get('properties', []))
            item = QListWidgetItem(f"{name} ({class_count} classes, {prop_count} properties)")
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.ontology_list.addItem(item)
    
    def display_ontology_terms(self, ontology_name: str, terms: Dict[str, List[Dict[str, str]]]) -> None:
        """Display terms from selected ontology"""
        self.terms_list.clear()
        
        # Handle case where terms is the ontology data directly
        if isinstance(terms, dict) and 'classes' in terms:
            # Display classes
            class_item = QListWidgetItem("=== Classes ===")
            class_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.terms_list.addItem(class_item)
            
            for class_info in terms['classes']:
                item = QListWidgetItem(f"Class: {class_info['name']}")
                item.setData(Qt.ItemDataRole.UserRole, {'type': 'class', **class_info})
                self.terms_list.addItem(item)
        
        # Handle case where terms is the ontology data directly
        if isinstance(terms, dict) and 'properties' in terms:
            # Display properties
            prop_item = QListWidgetItem("=== Properties ===")
            prop_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.terms_list.addItem(prop_item)
            
            for prop_info in terms['properties']:
                item = QListWidgetItem(f"Property: {prop_info['name']}")
                item.setData(Qt.ItemDataRole.UserRole, {'type': 'property', **prop_info})
                self.terms_list.addItem(item)
        
        # Display properties
        if 'properties' in terms:
            prop_item = QListWidgetItem("=== Properties ===")
            prop_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.terms_list.addItem(prop_item)
            
            for prop_info in terms['properties']:
                item = QListWidgetItem(f"Property: {prop_info['name']}")
                item.setData(Qt.ItemDataRole.UserRole, {'type': 'property', **prop_info})
                self.terms_list.addItem(item)
    
    def get_selected_term(self) -> Optional[Dict[str, str]]:
        """Get currently selected term"""
        current_item = self.terms_list.currentItem()
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def on_ontology_selected(self, item):
        """Handle ontology selection"""
        ontology_name = item.data(Qt.ItemDataRole.UserRole)
        if ontology_name and ontology_name in self.ontologies:
            self.display_ontology_terms(ontology_name, self.ontologies[ontology_name])
    
    def on_term_selected(self, item):
        """Handle term double-click"""
        term_data = item.data(Qt.ItemDataRole.UserRole)
        if term_data and hasattr(self, 'brick_editor') and self.brick_editor:
            if term_data.get("type") == "class":
                # Set target class
                self.brick_editor.target_class_edit.setText(term_data["uri"])
                # Also update brick name if empty
                if not self.brick_editor.brick_name_edit.text().strip():
                    self.brick_editor.brick_name_edit.setText(term_data["name"] + " Shape")
            elif term_data.get("type") == "property":
                # For property selection, show info for now
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Property Selected", 
                                   f"Selected property: {term_data['name']}\nURI: {term_data['uri']}\n\nThis can be used in property editors.")
    
    def use_selected(self):
        """Use selected term"""
        term = self.get_selected_term()
        if term and hasattr(self.parent, 'on_term_selected'):
            self.parent.on_term_selected(term)
