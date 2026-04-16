#!/usr/bin/env python3
"""
GUI Components for Stateful SHACL Brick Editor

Contains reusable GUI components used by the stateful GUI.
"""

import sys
import json
import os
from pathlib import Path

# Configuration Constants
PROJECT_ROOT = Path(__file__).parent.parent
ONTOLOGY_CACHE_DIR = str(PROJECT_ROOT / "ontologies" / "cache")

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QLabel, QLineEdit, QTextEdit, QComboBox, 
    QPushButton, QListWidget, QListWidgetItem, QGroupBox, QFormLayout,
    QMessageBox, QFileDialog, QDialog, QDialogButtonBox,
    QGridLayout, QRadioButton, QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt

# RDF imports for ontology parsing
try:
    from rdflib import Graph, RDF, OWL, URIRef
    RDFLIB_AVAILABLE = True
except ImportError:
    RDFLIB_AVAILABLE = False
    print("Warning: rdflib not available. Ontology parsing will be limited.")

# Add brick_app_v2 directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

# Import from core directory
sys.path.insert(0, str(app_dir / 'core'))

from core.brick_core_simple import BrickCore, SHACLBrick


class CorrectedOntologyManager:
    """OntologyManager with corrected cache path for GUI"""
    
    def __init__(self):
        self.ontologies = {}
        # Use configuration constant for cache path
        self.cache_dir = ONTOLOGY_CACHE_DIR
        self.load_cached_ontologies()
    
    def load_cached_ontologies(self):
        """Load all cached ontologies"""
        if not self.cache_dir or not os.path.exists(self.cache_dir):
            return
        
        try:
            for cache_file in os.listdir(self.cache_dir):
                if cache_file.endswith('.ttl') or cache_file.endswith('.rdf'):
                    cache_path = os.path.join(self.cache_dir, cache_file)
                    try:
                        # Parse TTL/RDF file directly
                        graph = Graph()
                        graph.parse(cache_path, format='turtle' if cache_file.endswith('.ttl') else 'xml')
                        
                        # Extract ontology information
                        ontology_info = self._extract_ontology_info(graph, cache_file)
                        if ontology_info:
                            self.ontologies[ontology_info['name']] = ontology_info
                    except Exception as e:
                        print(f"Error parsing {cache_file}: {e}")
                        continue
        except Exception as e:
            print(f"Error loading cached ontologies: {e}")
    
    def _extract_ontology_info(self, graph, filename):
        """Extract ontology information from RDF graph"""
        try:
            # Get ontology name from filename or URI
            base_name = os.path.splitext(filename)[0]
            ontology_name = base_name.replace('_', ' ').title()
            
            # Extract classes
            classes = []
            for class_uri in graph.subjects(RDF.type, OWL.Class):
                if isinstance(class_uri, URIRef):
                    class_name = class_uri.split('/')[-1] or class_uri.split('#')[-1]
                    if class_name and class_name != 'Class':
                        classes.append({
                            'name': class_name,
                            'uri': str(class_uri)
                        })
            
            # Extract properties
            properties = []
            for prop_uri in graph.subjects(RDF.type, OWL.ObjectProperty):
                if isinstance(prop_uri, URIRef):
                    prop_name = prop_uri.split('/')[-1] or prop_uri.split('#')[-1]
                    if prop_name and prop_name != 'ObjectProperty':
                        properties.append({
                            'name': prop_name,
                            'uri': str(prop_uri)
                        })
            
            for prop_uri in graph.subjects(RDF.type, OWL.DatatypeProperty):
                if isinstance(prop_uri, URIRef):
                    prop_name = prop_uri.split('/')[-1] or prop_uri.split('#')[-1]
                    if prop_name and prop_name != 'DatatypeProperty':
                        properties.append({
                            'name': prop_name,
                            'uri': str(prop_uri)
                        })
            
            return {
                'name': ontology_name,
                'classes': classes,
                'properties': properties
            }
        except Exception as e:
            print(f"Error extracting ontology info: {e}")
            return None


class SimpleOntologyBrowser(QDialog):
    """Simple ontology browser dialog"""
    
    def __init__(self, ontology_manager: CorrectedOntologyManager, parent=None, mode="classes"):
        super().__init__(parent)
        self.ontology_manager = ontology_manager
        self.mode = mode  # "classes" or "properties"
        self.selected_item = None
        self.all_items = []  # Store all items for filtering
        
        self.setWindowTitle(f"Browse Ontology {mode.capitalize()}")
        self.setGeometry(200, 200, 600, 500)
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        
        # Ontology selector
        onto_layout = QHBoxLayout()
        onto_layout.addWidget(QLabel("Ontology:"))
        
        self.ontology_combo = QComboBox()
        self.ontology_combo.currentTextChanged.connect(self.on_ontology_changed)
        onto_layout.addWidget(self.ontology_combo)
        
        layout.addLayout(onto_layout)
        
        # Search field
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Type to filter...")
        self.search_edit.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_edit)
        
        layout.addLayout(search_layout)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.on_item_selected)
        layout.addWidget(self.results_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(QPushButton("Cancel", clicked=self.reject))
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Load ontology data"""
        self.ontology_combo.clear()
        self.ontology_combo.addItems(list(self.ontology_manager.ontologies.keys()))
        
        if self.ontology_combo.count() > 0:
            self.load_ontology_data()
    
    def on_ontology_changed(self):
        """Handle ontology selection change"""
        self.load_ontology_data()
    
    def on_search_changed(self):
        """Handle search text change"""
        self.apply_search_filter()
    
    def apply_search_filter(self):
        """Apply search filter to items"""
        search_text = self.search_edit.text().lower().strip()
        
        self.results_list.clear()
        
        for item in self.all_items:
            # Filter by search text
            if search_text == "" or search_text in item['name'].lower():
                display_text = item['name']
                list_item = QListWidgetItem(display_text)
                list_item.setData(Qt.ItemDataRole.UserRole, item)
                self.results_list.addItem(list_item)
    
    def load_ontology_data(self):
        """Load classes or properties for selected ontology"""
        if self.ontology_combo.currentIndex() < 0:
            return
        
        ontology_name = self.ontology_combo.currentText()
        if not ontology_name or ontology_name not in self.ontology_manager.ontologies:
            return
        
        ontology_data = self.ontology_manager.ontologies[ontology_name]
        
        if self.mode == "classes":
            items = ontology_data.get('classes', [])
        else:
            items = ontology_data.get('properties', [])
        
        # Sort items alphabetically by name
        sorted_items = sorted(items, key=lambda x: x['name'].lower())
        
        self.all_items = sorted_items
        self.apply_search_filter()
    
    def on_item_selected(self, item):
        """Handle item selection"""
        self.selected_item = item.data(Qt.ItemDataRole.UserRole)
        self.accept()


class PropertyEditorDialog(QDialog):
    """Dialog for editing properties"""
    
    def __init__(self, parent=None, ontology_manager=None):
        super().__init__(parent)
        self.ontology_manager = ontology_manager
        self.property_data = {}
        
        self.setWindowTitle("Property Editor")
        self.setGeometry(200, 200, 500, 400)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        
        # Property name
        layout.addWidget(QLabel("Property Name:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        
        # Property path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Property Path:"))
        self.path_edit = QLineEdit()
        path_layout.addWidget(self.path_edit)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_ontology)
        path_layout.addWidget(browse_btn)
        
        layout.addLayout(path_layout)
        
        # Datatype
        layout.addWidget(QLabel("Datatype:"))
        self.datatype_combo = QComboBox()
        self.datatype_combo.addItems([
            "xsd:string", "xsd:integer", "xsd:float", "xsd:boolean", 
            "xsd:date", "xsd:dateTime", "xsd:anyURI"
        ])
        layout.addWidget(self.datatype_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(QPushButton("Cancel", clicked=self.reject))
        button_layout.addWidget(QPushButton("OK", clicked=self.accept))
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def browse_ontology(self):
        """Browse ontology for properties"""
        if self.ontology_manager:
            dialog = SimpleOntologyBrowser(self.ontology_manager, self, "properties")
            if dialog.exec() == QDialog.DialogCode.Accepted:
                if dialog.selected_item:
                    self.path_edit.setText(dialog.selected_item['uri'])
                    if not self.name_edit.text():
                        self.name_edit.setText(dialog.selected_item['name'])
    
    def get_property_data(self):
        """Get property data from dialog"""
        return {
            'name': self.name_edit.text(),
            'path': self.path_edit.text(),
            'datatype': self.datatype_combo.currentText()
        }
    
    def set_property_data(self, data):
        """Set property data in dialog"""
        self.name_edit.setText(data.get('name', ''))
        self.path_edit.setText(data.get('path', ''))
        datatype = data.get('datatype', 'xsd:string')
        index = self.datatype_combo.findText(datatype)
        if index >= 0:
            self.datatype_combo.setCurrentIndex(index)


class ConstraintEditorStateController:
    """State controller for constraint editor UI"""
    
    def __init__(self, ui_components):
        self.ui = ui_components
        self.current_constraint_type = ""
        
    def set_constraint_type(self, constraint_type):
        """Set constraint type and update UI visibility"""
        self.current_constraint_type = constraint_type
        self.update_visibility()
        
    def update_visibility(self):
        """Update component visibility based on constraint type"""
        # Ensure parent group is visible
        self.ui.valueConfigGroup.setVisible(True)
        
        # Hide all value widgets first
        self.ui.numericValueWidget.setVisible(False)
        self.ui.patternValueWidget.setVisible(False)
        self.ui.datatypeValueWidget.setVisible(False)
        self.ui.listValueWidget.setVisible(False)
        
        # Show appropriate widget based on type
        if self.current_constraint_type in ["minCount", "maxCount", "minLength", "maxLength"]:
            self.ui.numericValueWidget.setVisible(True)
            # Update label based on type
            if self.current_constraint_type in ["minCount", "maxCount"]:
                self.ui.numericValueLabel.setText("Count:")
            else:  # minLength, maxLength
                self.ui.numericValueLabel.setText("Length:")
                
        elif self.current_constraint_type == "pattern":
            self.ui.patternValueWidget.setVisible(True)
            
        elif self.current_constraint_type == "datatype":
            self.ui.datatypeValueWidget.setVisible(True)
            
        elif self.current_constraint_type in ["in", "notIn"]:
            self.ui.listValueWidget.setVisible(True)
            # Update label based on type
            if self.current_constraint_type == "in":
                self.ui.listValueLabel.setText("Allowed Values:")
            else:  # notIn
                self.ui.listValueLabel.setText("Forbidden Values:")
        
        # Update help text
        self.update_help_text()
        
        # Force layout update
        self.ui.valueConfigGroup.layout().update()
    
    def update_help_text(self):
        """Update help text based on current constraint type"""
        help_texts = {
            "minCount": "Minimum number of values this property must have. Use 0 or greater.",
            "maxCount": "Maximum number of values this property can have. Use 0 or greater.",
            "minLength": "Minimum length of string values. Use 0 or greater.",
            "maxLength": "Maximum length of string values. Use 0 or greater.",
            "pattern": "Regular expression pattern that string values must match. Example: ^[A-Za-z0-9]+$",
            "datatype": "Required datatype for property values. Select from available XSD datatypes.",
            "in": "Property value must be one of these allowed values. Add values to the list.",
            "notIn": "Property value must not be any of these forbidden values. Add values to the list."
        }
        
        help_text = help_texts.get(self.current_constraint_type, "Select a constraint type to see help information.")
        self.ui.helpTextLabel.setText(help_text)


class ConstraintEditorDialog(QDialog):
    """Dialog for editing constraints with Qt Designer UI"""
    
    def __init__(self, parent=None, property_data=None):
        super().__init__(parent)
        self.property_data = property_data or {}
        self.constraint_data = {}
        
        # Load UI from file
        ui_path = Path(__file__).parent / "ui" / "constraint_editor.ui"
        from PyQt6.uic import loadUi
        loadUi(str(ui_path), self)
        
        # Initialize state controller
        self.state_controller = ConstraintEditorStateController(self)
        
        # Setup connections and initial state
        self.setup_connections()
        self.setup_initial_state()
    
    def setup_connections(self):
        """Setup signal connections"""
        # Constraint type change
        self.constraintTypeCombo.currentTextChanged.connect(self.on_type_changed)
        
        # List value management
        self.addValueButton.clicked.connect(self.add_value_to_list)
        self.removeValueButton.clicked.connect(self.remove_value_from_list)
        self.newValueEdit.returnPressed.connect(self.add_value_to_list)
        
        # Button connections
        self.cancelButton.clicked.connect(self.reject)
        self.okButton.clicked.connect(self.accept)
    
    def setup_initial_state(self):
        """Setup initial UI state"""
        # Ensure dialog is properly sized
        self.resize(600, 500)
        
        # Ensure parent group is visible
        self.valueConfigGroup.setVisible(True)
        self.valueConfigGroup.show()
        
        # Ensure widgets are properly initialized
        self.numericValueWidget.setVisible(False)
        self.patternValueWidget.setVisible(False)
        self.datatypeValueWidget.setVisible(False)
        self.listValueWidget.setVisible(False)
        
        # Force layout update
        self.updateGeometry()
        self.valueConfigGroup.updateGeometry()
        
        # Trigger initial type change to show default state
        if self.constraintTypeCombo.count() > 0:
            self.on_type_changed(self.constraintTypeCombo.currentText())
    
    def on_type_changed(self, constraint_type):
        """Handle constraint type change using state controller"""
        if constraint_type:
            self.state_controller.set_constraint_type(constraint_type)
    
    def add_value_to_list(self):
        """Add a new value to the list widget"""
        value = self.newValueEdit.text().strip()
        if value:
            # Check if value already exists
            for i in range(self.valueListWidget.count()):
                item = self.valueListWidget.item(i)
                if item.text() == value:
                    return  # Value already exists
            
            # Add new value
            self.valueListWidget.addItem(value)
            self.newValueEdit.clear()
            self.newValueEdit.setFocus()
    
    def remove_value_from_list(self):
        """Remove selected value from list widget"""
        current_item = self.valueListWidget.currentItem()
        if current_item:
            self.valueListWidget.takeItem(self.valueListWidget.row(current_item))
    
    def get_constraint_data(self):
        """Get constraint data from dialog"""
        constraint_type = self.constraintTypeCombo.currentText()
        
        if constraint_type in ["minCount", "maxCount", "minLength", "maxLength"]:
            return {
                'type': constraint_type,
                'value': str(self.numericValueSpinBox.value())
            }
        elif constraint_type == "pattern":
            return {
                'type': constraint_type,
                'value': self.patternValueEdit.text()
            }
        elif constraint_type == "datatype":
            return {
                'type': constraint_type,
                'value': self.datatypeCombo.currentText()
            }
        elif constraint_type in ["in", "notIn"]:
            values = []
            for i in range(self.valueListWidget.count()):
                item = self.valueListWidget.item(i)
                values.append(item.text())
            return {
                'type': constraint_type,
                'value': values
            }
        else:
            return {
                'type': constraint_type,
                'value': ""
            }
    
    def set_constraint_data(self, data):
        """Set constraint data in dialog"""
        constraint_type = data.get('type', '')
        constraint_value = data.get('value', '')
        
        # Set constraint type
        index = self.constraintTypeCombo.findText(constraint_type)
        if index >= 0:
            self.constraintTypeCombo.setCurrentIndex(index)
        
        # Set constraint value based on type
        if constraint_type in ["minCount", "maxCount", "minLength", "maxLength"]:
            try:
                self.numericValueSpinBox.setValue(int(constraint_value))
            except (ValueError, TypeError):
                pass
        elif constraint_type == "pattern":
            self.patternValueEdit.setText(constraint_value)
        elif constraint_type == "datatype":
            index = self.datatypeCombo.findText(constraint_value)
            if index >= 0:
                self.datatypeCombo.setCurrentIndex(index)
        elif constraint_type in ["in", "notIn"] and isinstance(constraint_value, list):
            self.valueListWidget.clear()
            for value in constraint_value:
                self.valueListWidget.addItem(value)


class PropertyBrickBrowser(QDialog):
    """Dialog for browsing property bricks"""
    
    def __init__(self, parent=None, brick_core=None):
        super().__init__(parent)
        self.brick_core = brick_core
        self.selected_brick = None
        
        self.setWindowTitle("Property Brick Browser")
        self.setGeometry(200, 200, 600, 500)
        
        self.setup_ui()
        self.load_property_bricks()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        
        # Brick list
        self.brick_list = QListWidget()
        self.brick_list.itemDoubleClicked.connect(self.on_brick_selected)
        layout.addWidget(self.brick_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(QPushButton("Cancel", clicked=self.reject))
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_property_bricks(self):
        """Load property bricks from library"""
        try:
            bricks = self.brick_core.get_all_bricks()
            self.brick_list.clear()
            
            for brick in bricks:
                if brick.object_type == "PropertyShape":
                    display_text = f"{brick.name} - {brick.property_path}"
                    list_item = QListWidgetItem(display_text)
                    list_item.setData(Qt.ItemDataRole.UserRole, brick)
                    self.brick_list.addItem(list_item)
        except Exception as e:
            print(f"Error loading property bricks: {e}")
    
    def on_brick_selected(self, item):
        """Handle brick selection"""
        self.selected_brick = item.data(Qt.ItemDataRole.UserRole)
        self.accept()
