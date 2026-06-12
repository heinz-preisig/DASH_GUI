#!/usr/bin/env python3
"""
Dialog Controller - Centralized dialog management with signal/slot architecture
"""

from typing import Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QListWidget, QLineEdit, QComboBox, QPushButton, QDialogButtonBox,
    QGroupBox, QApplication
)
from PyQt6.QtCore import Qt


class DialogController(QObject):
    """Centralized dialog controller with signal/slot communication"""
    
    # Signals for backend communication
    property_dialog_accepted = pyqtSignal(dict)
    class_dialog_accepted = pyqtSignal(str)
    ontology_property_selected = pyqtSignal(str, str)  # name, uri
    
    def __init__(self, main_backend, parent_widget=None):
        super().__init__()
        self.main_backend = main_backend
        self.parent_widget = parent_widget
        
        # Connect to backend signals
        self.main_backend.show_property_dialog.connect(self.show_property_dialog)
        self.main_backend.show_class_browser.connect(self.show_class_browser)
        self.main_backend.show_ontology_browser.connect(self.show_ontology_browser)
    
    def show_property_dialog(self):
        """Show add property dialog with unified ontology browsing"""
        dialog = QDialog(self.parent_widget)
        dialog.setWindowTitle("Add Property")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QFormLayout()
        
        name_edit = QLineEdit()
        form_layout.addRow("Property Name:", name_edit)
        
        path_edit = QLineEdit()
        form_layout.addRow("Property Path:", path_edit)
        
        datatype_combo = QComboBox()
        datatype_combo.addItems(["xsd:string", "xsd:integer", "xsd:decimal", "xsd:boolean", "xsd:date", "xsd:anyURI"])
        form_layout.addRow("Data Type:", datatype_combo)
        
        layout.addLayout(form_layout)
        
        # Browse ontology button
        browse_btn = QPushButton("Browse Ontology for Property")
        browse_btn.clicked.connect(lambda: self._browse_ontology_for_property(name_edit, path_edit))
        layout.addWidget(browse_btn)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(button_box)
        
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            property_data = {
                "name": name_edit.text(),
                "path": path_edit.text(),
                "datatype": datatype_combo.currentText(),
                "constraints": []
            }
            self.property_dialog_accepted.emit(property_data)
    
    def show_class_browser(self):
        """Show class selection dialog with unified ontology browsing"""
        dialog = QDialog(self.parent_widget)
        dialog.setWindowTitle("Select Target Class from Ontology")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Instructions
        instructions = QLabel(
            "Choose from available ontologies by clicking on them.<br>"
            "Double-click a class to use it as the target class."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Ontology list
        ontology_list = QListWidget()
        ontologies = self.main_backend.get_available_ontologies()
        
        for name, data in ontologies.items():
            class_count = len(data.get('classes', []))
            prop_count = len(data.get('properties', []))
            item = QListWidgetItem(f"{name} ({class_count} classes, {prop_count} properties)")
            item.setData(Qt.ItemDataRole.UserRole, name)
            ontology_list.addItem(item)
        
        layout.addWidget(QLabel("Select an ontology:"))
        layout.addWidget(ontology_list)
        
        # Terms list
        terms_list = QListWidget()
        layout.addWidget(QLabel("Select a class:"))
        layout.addWidget(terms_list)
        
        # Handle ontology selection
        def on_ontology_selected(item):
            ontology_name = item.data(Qt.ItemDataRole.UserRole)
            if ontology_name and ontology_name in ontologies:
                terms_list.clear()
                classes = self.main_backend.get_ontology_classes(ontology_name)
                
                for class_info in classes:
                    item = QListWidgetItem(f"Class: {class_info['name']}")
                    item.setData(Qt.ItemDataRole.UserRole, {'type': 'class', **class_info})
                    terms_list.addItem(item)
        
        # Handle class selection
        def on_class_selected(item):
            term_data = item.data(Qt.ItemDataRole.UserRole)
            if term_data and term_data.get("type") == "class":
                self.class_dialog_accepted.emit(term_data["uri"])
                dialog.accept()
        
        ontology_list.itemClicked.connect(on_ontology_selected)
        terms_list.itemDoubleClicked.connect(on_class_selected)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(button_box)
        button_box.rejected.connect(dialog.reject)
        
        dialog.exec()
    
    def show_ontology_browser(self):
        """Show full ontology browser dialog"""
        dialog = QDialog(self.parent_widget)
        dialog.setWindowTitle("Ontology Browser")
        dialog.setModal(True)
        dialog.resize(700, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Ontology list
        ontology_list = QListWidget()
        ontologies = self.main_backend.get_available_ontologies()
        
        for name, data in ontologies.items():
            class_count = len(data.get('classes', []))
            prop_count = len(data.get('properties', []))
            item = QListWidgetItem(f"{name} ({class_count} classes, {prop_count} properties)")
            item.setData(Qt.ItemDataRole.UserRole, name)
            ontology_list.addItem(item)
        
        layout.addWidget(QLabel("Select an ontology:"))
        layout.addWidget(ontology_list)
        
        # Terms list
        terms_list = QListWidget()
        layout.addWidget(QLabel("Classes & Properties:"))
        layout.addWidget(terms_list)
        
        # Handle ontology selection
        def on_ontology_selected(item):
            ontology_name = item.data(Qt.ItemDataRole.UserRole)
            if ontology_name and ontology_name in ontologies:
                terms_list.clear()
                ontology_data = ontologies[ontology_name]
                
                # Show classes
                if 'classes' in ontology_data:
                    class_item = QListWidgetItem("=== Classes ===")
                    class_item.setFlags(Qt.ItemFlag.NoItemFlags)
                    terms_list.addItem(class_item)
                    
                    for class_info in ontology_data['classes']:
                        item = QListWidgetItem(f"Class: {class_info['name']}")
                        item.setData(Qt.ItemDataRole.UserRole, {'type': 'class', **class_info})
                        terms_list.addItem(item)
                
                # Show properties
                if 'properties' in ontology_data:
                    prop_item = QListWidgetItem("=== Properties ===")
                    prop_item.setFlags(Qt.ItemFlag.NoItemFlags)
                    terms_list.addItem(prop_item)
                    
                    for prop_info in ontology_data['properties']:
                        item = QListWidgetItem(f"Property: {prop_info['name']}")
                        item.setData(Qt.ItemDataRole.UserRole, {'type': 'property', **prop_info})
                        terms_list.addItem(item)
        
        # Handle term selection
        def on_term_selected(item):
            term_data = item.data(Qt.ItemDataRole.UserRole)
            if term_data:
                if term_data.get("type") == "class":
                    # Copy class URI to clipboard
                    clipboard = QApplication.clipboard()
                    clipboard.setText(term_data["uri"])
                elif term_data.get("type") == "property":
                    # Emit signal for property selection
                    self.ontology_property_selected.emit(term_data["name"], term_data["uri"])
        
        ontology_list.itemClicked.connect(on_ontology_selected)
        terms_list.itemDoubleClicked.connect(on_term_selected)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        layout.addWidget(button_box)
        button_box.rejected.connect(dialog.reject)
        
        dialog.exec()
    
    def _browse_ontology_for_property(self, name_edit, path_edit):
        """Internal method for property selection"""
        dialog = QDialog(self.parent_widget)
        dialog.setWindowTitle("Select Property from Ontology")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Ontology list
        ontology_list = QListWidget()
        ontologies = self.main_backend.get_available_ontologies()
        
        for name, data in ontologies.items():
            class_count = len(data.get('classes', []))
            prop_count = len(data.get('properties', []))
            item = QListWidgetItem(f"{name} ({class_count} classes, {prop_count} properties)")
            item.setData(Qt.ItemDataRole.UserRole, name)
            ontology_list.addItem(item)
        
        layout.addWidget(QLabel("Select an ontology:"))
        layout.addWidget(ontology_list)
        
        # Terms list
        terms_list = QListWidget()
        layout.addWidget(QLabel("Select a property:"))
        layout.addWidget(terms_list)
        
        # Handle ontology selection
        def on_ontology_selected(item):
            ontology_name = item.data(Qt.ItemDataRole.UserRole)
            if ontology_name and ontology_name in ontologies:
                terms_list.clear()
                properties = self.main_backend.get_ontology_properties(ontology_name)
                
                for prop_info in properties:
                    item = QListWidgetItem(f"Property: {prop_info['name']}")
                    item.setData(Qt.ItemDataRole.UserRole, {'type': 'property', **prop_info})
                    terms_list.addItem(item)
        
        # Handle property selection
        def on_property_selected(item):
            term_data = item.data(Qt.ItemDataRole.UserRole)
            if term_data and term_data.get("type") == "property":
                name_edit.setText(term_data["name"])
                path_edit.setText(term_data["uri"])
                dialog.accept()
        
        ontology_list.itemClicked.connect(on_ontology_selected)
        terms_list.itemDoubleClicked.connect(on_property_selected)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(button_box)
        button_box.rejected.connect(dialog.reject)
        
        dialog.exec()
