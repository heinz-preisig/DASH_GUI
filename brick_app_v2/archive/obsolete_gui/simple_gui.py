#!/usr/bin/env python3
"""
Simple SHACL Brick Editor

A clean, simple interface focusing only on essential brick functionality.
"""

import sys
import json
import os
from pathlib import Path

# Configuration Constants
PROJECT_ROOT = Path(__file__).parent.parent
ONTOLOGY_CACHE_DIR = str(PROJECT_ROOT / "ontologies" / "cache")
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QLabel, QLineEdit, QTextEdit, QComboBox, 
                            QPushButton, QListWidget, QListWidgetItem, QGroupBox, QFormLayout,
                            QMessageBox, QFileDialog, QDialog)
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
from brick_app_v2.core.editor_backend import OntologyManager


# class CorrectedOntologyManager:
#     """OntologyManager with corrected cache path for simple GUI"""
#
#     def __init__(self):
#         self.ontologies = {}
#         # Use configuration constant for cache path
#         self.cache_dir = ONTOLOGY_CACHE_DIR
#         self.load_cached_ontologies()
#
#     def load_cached_ontologies(self):
#         """Load cached ontologies from cache directory"""
#         if not RDFLIB_AVAILABLE:
#             print("Warning: rdflib not available. Cannot parse ontology files.")
#             return
#
#         if not os.path.exists(self.cache_dir):
#             print(f"Cache directory not found: {self.cache_dir}")
#             return
#
#         try:
#             for filename in os.listdir(self.cache_dir):
#                 if filename.endswith(('.ttl', '.rdf')):
#                     filepath = os.path.join(self.cache_dir, filename)
#                     ontology_name = filename.replace('.ttl', '').replace('.rdf', '')
#
#                     # Parse RDF/TTL file
#                     graph = Graph()
#                     graph.parse(filepath, format='turtle' if filename.endswith('.ttl') else 'xml')
#
#                     # Extract classes and properties
#                     classes = []
#                     properties = []
#
#                     # Get classes
#                     for class_uri in graph.subjects(RDF.type, OWL.Class):
#                         if isinstance(class_uri, URIRef):
#                             class_name = str(class_uri).split('/')[-1].split('#')[-1]
#                             classes.append({
#                                 'name': class_name,
#                                 'uri': str(class_uri)
#                             })
#
#                     # Get properties
#                     for prop_uri in graph.subjects(RDF.type, OWL.ObjectProperty):
#                         if isinstance(prop_uri, URIRef):
#                             prop_name = str(prop_uri).split('/')[-1].split('#')[-1]
#                             properties.append({
#                                 'name': prop_name,
#                                 'uri': str(prop_uri)
#                             })
#
#                     for prop_uri in graph.subjects(RDF.type, OWL.DatatypeProperty):
#                         if isinstance(prop_uri, URIRef):
#                             prop_name = str(prop_uri).split('/')[-1].split('#')[-1]
#                             properties.append({
#                                 'name': prop_name,
#                                 'uri': str(prop_uri)
#                             })
#
#                     self.ontologies[ontology_name] = {
#                         'classes': classes,
#                         'properties': properties,
#                         'name': ontology_name,
#                         'uri': filepath
#                     }
#
#                     print(f"Loaded ontology: {ontology_name} ({len(classes)} classes, {len(properties)} properties)")
#
#         except Exception as e:
#             print(f"Error loading cached ontologies: {e}")
#             import traceback
#             traceback.print_exc()
#
#     def get_available_classes(self):
#         """Get all available classes from all ontologies"""
#         classes = []
#         for ontology_data in self.ontologies.values():
#             classes.extend(ontology_data.get('classes', []))
#         return classes
#
#     def get_available_properties(self):
#         """Get all available properties from all ontologies"""
#         properties = []
#         for ontology_data in self.ontologies.values():
#             properties.extend(ontology_data.get('properties', []))
#         return properties


# class SimpleOntologyBrowser(QDialog):
#     """Simple ontology browser dialog"""
#
#     def __init__(self, ontology_manager: OntologyManager, parent=None, mode="classes"):
#         super().__init__(parent)
#         self.ontology_manager = ontology_manager
#         self.mode = mode  # "classes" or "properties"
#         self.selected_item = None
#         self.all_items = []  # Store all items for filtering
#
#         self.setWindowTitle(f"Browse Ontology {mode.capitalize()}")
#         self.setGeometry(200, 200, 600, 500)
#
#         self.setup_ui()
#         self.load_data()
#
#     def setup_ui(self):
#         """Setup the dialog UI"""
#         layout = QVBoxLayout()
#
#         # Ontology selector
#         onto_layout = QHBoxLayout()
#         onto_layout.addWidget(QLabel("Ontology:"))
#
#         self.ontology_combo = QComboBox()
#         self.ontology_combo.currentTextChanged.connect(self.on_ontology_changed)
#         onto_layout.addWidget(self.ontology_combo)
#
#         layout.addLayout(onto_layout)
#
#         # Search field
#         search_layout = QHBoxLayout()
#         search_layout.addWidget(QLabel("Search:"))
#
#         self.search_edit = QLineEdit()
#         self.search_edit.setPlaceholderText("Type to filter...")
#         self.search_edit.textChanged.connect(self.on_search_changed)
#         search_layout.addWidget(self.search_edit)
#
#         layout.addLayout(search_layout)
#
#         # Results list
#         self.results_list = QListWidget()
#         self.results_list.itemDoubleClicked.connect(self.on_item_selected)
#         layout.addWidget(self.results_list)
#
#         # Buttons
#         button_layout = QHBoxLayout()
#
#         select_btn = QPushButton("Select")
#         select_btn.clicked.connect(self.on_select_clicked)
#         button_layout.addWidget(select_btn)
#
#         cancel_btn = QPushButton("Cancel")
#         cancel_btn.clicked.connect(self.reject)
#         button_layout.addWidget(cancel_btn)
#
#         layout.addLayout(button_layout)
#         self.setLayout(layout)
#
#     def load_data(self):
#         """Load ontology list"""
#         ontologies = self.ontology_manager.ontologies
#         self.ontology_combo.clear()
#
#         # Sort ontologies alphabetically
#         sorted_ontologies = sorted(ontologies.items(), key=lambda x: x[0].lower())
#
#         for name, data in sorted_ontologies:
#             class_count = len(data.get('classes', []))
#             prop_count = len(data.get('properties', []))
#             display_text = f"{name} ({class_count} classes, {prop_count} properties)"
#             self.ontology_combo.addItem(display_text, name)
#
#         if self.ontology_combo.count() > 0:
#             self.load_ontology_data()
#
#     def on_ontology_changed(self):
#         """Handle ontology selection change"""
#         self.load_ontology_data()
#
#     def load_ontology_data(self):
#         """Load classes or properties for selected ontology"""
#         if self.ontology_combo.currentIndex() < 0:
#             return
#
#         ontology_name = self.ontology_combo.currentData()
#         if not ontology_name or ontology_name not in self.ontology_manager.ontologies:
#             return
#
#         ontology_data = self.ontology_manager.ontologies[ontology_name]
#
#         if self.mode == "classes":
#             items = ontology_data.get('classes', [])
#         else:
#             items = ontology_data.get('properties', [])
#
#         # Sort items alphabetically by name and store all items
#         self.all_items = sorted(items, key=lambda x: x['name'].lower())
#
#         # Apply current search filter
#         self.apply_search_filter()
#
#     def on_search_changed(self):
#         """Handle search text change"""
#         self.apply_search_filter()
#
#     def apply_search_filter(self):
#         """Apply search filter to items"""
#         search_text = self.search_edit.text().lower().strip()
#
#         self.results_list.clear()
#
#         for item in self.all_items:
#             # Filter by search text
#             if search_text == "" or search_text in item['name'].lower():
#                 display_text = item['name']
#                 list_item = QListWidgetItem(display_text)
#                 list_item.setData(Qt.ItemDataRole.UserRole, item)
#                 self.results_list.addItem(list_item)
#
#     def on_item_selected(self, item):
#         """Handle item double-click"""
#         self.selected_item = item.data(Qt.ItemDataRole.UserRole)
#         self.accept()
#
#     def on_select_clicked(self):
#         """Handle select button click"""
#         current_item = self.results_list.currentItem()
#         if current_item:
#             self.selected_item = current_item.data(Qt.ItemDataRole.UserRole)
#             self.accept()


# class PropertyEditorDialog(QDialog):
#     """Dialog for editing properties with constraints"""
#
#     def __init__(self, parent=None, property_data=None, ontology_manager=None):
#         super().__init__(parent)
#         self.ontology_manager = ontology_manager
#         self.property_data = property_data or {}
#         self.constraints = []
#
#         self.setWindowTitle("Property Editor")
#         self.setGeometry(200, 200, 600, 700)
#
#         self.setup_ui()
#         self.load_property_data()
#
#     def setup_ui(self):
#         """Setup the dialog UI"""
#         layout = QVBoxLayout()
#
#         # Basic properties
#         basic_group = QGroupBox("Basic Properties")
#         basic_layout = QFormLayout()
#
#         self.name_edit = QLineEdit()
#         basic_layout.addRow("Name:", self.name_edit)
#
#         self.path_edit = QLineEdit()
#         self.path_edit.setPlaceholderText("e.g., ex:name, schema:description")
#         basic_layout.addRow("Path:", self.path_edit)
#
#         # Browse button for path
#         path_layout = QHBoxLayout()
#         path_layout.addWidget(self.path_edit)
#         browse_path_btn = QPushButton("Browse")
#         browse_path_btn.clicked.connect(self.browse_properties)
#         path_layout.addWidget(browse_path_btn)
#         basic_layout.addRow("", path_layout)
#
#         self.datatype_combo = QComboBox()
#         self.datatype_combo.addItems([
#             "xsd:string", "xsd:integer", "xsd:decimal", "xsd:boolean",
#             "xsd:date", "xsd:anyURI", "xsd:float", "xsd:double"
#         ])
#         self.datatype_combo.currentTextChanged.connect(self.on_datatype_changed)
#         basic_layout.addRow("Data Type:", self.datatype_combo)
#
#         basic_group.setLayout(basic_layout)
#         layout.addWidget(basic_group)
#
#         # Constraints section
#         constraints_group = QGroupBox("Constraints")
#         constraints_layout = QVBoxLayout()
#
#         # Constraint list
#         self.constraints_list = QListWidget()
#         self.constraints_list.setMaximumHeight(150)
#         constraints_layout.addWidget(self.constraints_list)
#
#         # Constraint buttons
#         constraint_buttons = QHBoxLayout()
#
#         add_constraint_btn = QPushButton("Add Constraint")
#         add_constraint_btn.clicked.connect(self.add_constraint)
#         constraint_buttons.addWidget(add_constraint_btn)
#
#         edit_constraint_btn = QPushButton("Edit")
#         edit_constraint_btn.clicked.connect(self.edit_constraint)
#         constraint_buttons.addWidget(edit_constraint_btn)
#
#         remove_constraint_btn = QPushButton("Remove")
#         remove_constraint_btn.clicked.connect(self.remove_constraint)
#         constraint_buttons.addWidget(remove_constraint_btn)
#
#         constraints_layout.addLayout(constraint_buttons)
#         constraints_group.setLayout(constraints_layout)
#         layout.addWidget(constraints_group)
#
#         # Dialog buttons
#         dialog_buttons = QHBoxLayout()
#
#         save_btn = QPushButton("Save")
#         save_btn.clicked.connect(self.accept)
#         dialog_buttons.addWidget(save_btn)
#
#         cancel_btn = QPushButton("Cancel")
#         cancel_btn.clicked.connect(self.reject)
#         dialog_buttons.addWidget(cancel_btn)
#
#         layout.addLayout(dialog_buttons)
#         self.setLayout(layout)
#
#     def load_property_data(self):
#         """Load existing property data"""
#         self.name_edit.setText(self.property_data.get('name', ''))
#         self.path_edit.setText(self.property_data.get('path', ''))
#         self.datatype_combo.setCurrentText(self.property_data.get('datatype', 'xsd:string'))
#
#         # Load constraints
#         self.constraints = self.property_data.get('constraints', [])
#         self.update_constraints_list()
#
#     def browse_properties(self):
#         """Browse ontology properties"""
#         if not self.ontology_manager:
#             return
#
#         dialog = SimpleOntologyBrowser(self.ontology_manager, self, "properties")
#         if dialog.exec() == QDialog.DialogCode.Accepted:
#             selected_item = dialog.selected_item
#             if selected_item:
#                 self.path_edit.setText(selected_item['uri'])
#
#     def on_datatype_changed(self, datatype):
#         """Handle datatype change - suggest relevant constraints"""
#         # This could suggest constraints based on datatype
#         pass
#
#     def add_constraint(self):
#         """Add a new constraint"""
#         dialog = ConstraintEditorDialog(self)
#         if dialog.exec() == QDialog.DialogCode.Accepted:
#             constraint = dialog.get_constraint()
#             if constraint:
#                 self.constraints.append(constraint)
#                 self.update_constraints_list()
#
#     def edit_constraint(self):
#         """Edit selected constraint"""
#         current_item = self.constraints_list.currentItem()
#         if not current_item:
#             return
#
#         index = self.constraints_list.row(current_item)
#         constraint = self.constraints[index]
#
#         dialog = ConstraintEditorDialog(self, constraint)
#         if dialog.exec() == QDialog.DialogCode.Accepted:
#             updated_constraint = dialog.get_constraint()
#             if updated_constraint:
#                 self.constraints[index] = updated_constraint
#                 self.update_constraints_list()
#
#     def remove_constraint(self):
#         """Remove selected constraint"""
#         current_item = self.constraints_list.currentItem()
#         if not current_item:
#             return
#
#         index = self.constraints_list.row(current_item)
#         del self.constraints[index]
#         self.update_constraints_list()
#
#     def update_constraints_list(self):
#         """Update the constraints display"""
#         self.constraints_list.clear()
#         for constraint in self.constraints:
#             display_text = f"{constraint.get('type', 'Unknown')}: {constraint.get('value', '')}"
#             list_item = QListWidgetItem(display_text)
#             list_item.setData(Qt.ItemDataRole.UserRole, constraint)
#             self.constraints_list.addItem(list_item)
#
#     def get_property_data(self):
#         """Get the complete property data"""
#         return {
#             'name': self.name_edit.text(),
#             'path': self.path_edit.text(),
#             'datatype': self.datatype_combo.currentText(),
#             'constraints': self.constraints
#         }


# class ConstraintEditorDialog(QDialog):
#     """Dialog for editing individual constraints"""
#
#     def __init__(self, parent=None, constraint_data=None):
#         super().__init__(parent)
#         self.constraint_data = constraint_data or {}
#
#         self.setWindowTitle("Constraint Editor")
#         self.setGeometry(300, 300, 400, 300)
#
#         self.setup_ui()
#         self.load_constraint_data()
#
#     def setup_ui(self):
#         """Setup the constraint editor UI"""
#         layout = QVBoxLayout()
#
#         form_layout = QFormLayout()
#
#         # Constraint type
#         self.type_combo = QComboBox()
#         self.type_combo.addItems([
#             "minLength", "maxLength", "minInclusive", "maxInclusive",
#             "minExclusive", "maxExclusive", "pattern", "datatype",
#             "nodeKind", "class", "in", "hasValue"
#         ])
#         self.type_combo.currentTextChanged.connect(self.on_type_changed)
#         form_layout.addRow("Type:", self.type_combo)
#
#         # Value field
#         self.value_edit = QLineEdit()
#         form_layout.addRow("Value:", self.value_edit)
#
#         # Additional fields for specific constraint types
#         self.additional_fields = QWidget()
#         self.additional_layout = QVBoxLayout(self.additional_fields)
#         form_layout.addRow("", self.additional_fields)
#
#         layout.addLayout(form_layout)
#
#         # Dialog buttons
#         button_layout = QHBoxLayout()
#
#         save_btn = QPushButton("Save")
#         save_btn.clicked.connect(self.accept)
#         button_layout.addWidget(save_btn)
#
#         cancel_btn = QPushButton("Cancel")
#         cancel_btn.clicked.connect(self.reject)
#         button_layout.addWidget(cancel_btn)
#
#         layout.addLayout(button_layout)
#         self.setLayout(layout)
#
#     def load_constraint_data(self):
#         """Load existing constraint data"""
#         constraint_type = self.constraint_data.get('type', '')
#         if constraint_type:
#             index = self.type_combo.findText(constraint_type)
#             if index >= 0:
#                 self.type_combo.setCurrentIndex(index)
#
#         self.value_edit.setText(self.constraint_data.get('value', ''))
#         self.on_type_changed(self.type_combo.currentText())
#
#     def on_type_changed(self, constraint_type):
#         """Handle constraint type change - show/hide relevant fields"""
#         # Clear additional fields
#         while self.additional_layout.count():
#             child = self.additional_layout.takeAt(0)
#             if child.widget():
#                 child.widget().deleteLater()
#
#         # Add type-specific fields
#         if constraint_type == "datatype":
#             datatype_combo = QComboBox()
#             datatype_combo.addItems([
#                 "xsd:string", "xsd:integer", "xsd:decimal", "xsd:boolean",
#                 "xsd:date", "xsd:anyURI", "xsd:float", "xsd:double"
#             ])
#             self.additional_layout.addWidget(QLabel("Datatype:"))
#             self.additional_layout.addWidget(datatype_combo)
#             self.datatype_combo = datatype_combo
#
#         elif constraint_type == "nodeKind":
#             nodekind_combo = QComboBox()
#             nodekind_combo.addItems(["BlankNode", "IRI", "Literal"])
#             self.additional_layout.addWidget(QLabel("Node Kind:"))
#             self.additional_layout.addWidget(nodekind_combo)
#             self.nodekind_combo = nodekind_combo
#
#         elif constraint_type == "class":
#             class_edit = QLineEdit()
#             class_edit.setPlaceholderText("e.g., ex:Person, schema:Organization")
#             self.additional_layout.addWidget(QLabel("Class URI:"))
#             self.additional_layout.addWidget(class_edit)
#             self.class_edit = class_edit
#
#         elif constraint_type == "in":
#             values_edit = QTextEdit()
#             values_edit.setPlaceholderText("Enter values, one per line")
#             values_edit.setMaximumHeight(80)
#             self.additional_layout.addWidget(QLabel("Allowed Values:"))
#             self.additional_layout.addWidget(values_edit)
#             self.values_edit = values_edit
#
#     def get_constraint(self):
#         """Get the constraint data"""
#         constraint = {
#             'type': self.type_combo.currentText(),
#             'value': self.value_edit.text()
#         }
#
#         # Add type-specific data
#         constraint_type = self.type_combo.currentText()
#         if constraint_type == "datatype" and hasattr(self, 'datatype_combo'):
#             constraint['datatype'] = self.datatype_combo.currentText()
#         elif constraint_type == "nodeKind" and hasattr(self, 'nodekind_combo'):
#             constraint['nodeKind'] = self.nodekind_combo.currentText()
#         elif constraint_type == "class" and hasattr(self, 'class_edit'):
#             constraint['class'] = self.class_edit.text()
#         elif constraint_type == "in" and hasattr(self, 'values_edit'):
#             values = [v.strip() for v in self.values_edit.toPlainText().split('\n') if v.strip()]
#             constraint['values'] = values
#
#         return constraint


# class PropertyBrickBrowser(QDialog):
#     """Dialog for browsing and selecting existing property bricks"""
#
#     def __init__(self, parent=None, brick_core=None):
#         super().__init__(parent)
#         self.brick_core = brick_core
#         self.selected_brick = None
#
#         self.setWindowTitle("Browse Property Bricks")
#         self.setGeometry(200, 200, 600, 500)
#
#         self.setup_ui()
#         self.load_property_bricks()
#
#     def setup_ui(self):
#         """Setup the dialog UI"""
#         layout = QVBoxLayout()
#
#         # Search field
#         search_layout = QHBoxLayout()
#         search_layout.addWidget(QLabel("Search:"))
#
#         self.search_edit = QLineEdit()
#         self.search_edit.setPlaceholderText("Type to filter property bricks...")
#         self.search_edit.textChanged.connect(self.filter_bricks)
#         search_layout.addWidget(self.search_edit)
#
#         layout.addLayout(search_layout)
#
#         # Property bricks list
#         self.bricks_list = QListWidget()
#         self.bricks_list.itemDoubleClicked.connect(self.on_brick_selected)
#         layout.addWidget(self.bricks_list)
#
#         # Buttons
#         button_layout = QHBoxLayout()
#
#         select_btn = QPushButton("Select")
#         select_btn.clicked.connect(self.on_select_clicked)
#         button_layout.addWidget(select_btn)
#
#         cancel_btn = QPushButton("Cancel")
#         cancel_btn.clicked.connect(self.reject)
#         button_layout.addWidget(cancel_btn)
#
#         layout.addLayout(button_layout)
#         self.setLayout(layout)
#
#     def load_property_bricks(self):
#         """Load only PropertyShape bricks from library"""
#         if not self.brick_core:
#             return
#
#         try:
#             bricks = self.brick_core.get_all_bricks()
#             self.all_bricks = []
#
#             for brick in bricks:
#                 # Only include PropertyShape bricks
#                 if brick.object_type == "PropertyShape":
#                     self.all_bricks.append(brick)
#
#             self.filter_bricks()  # Apply current filter
#
#         except Exception as e:
#             print(f"Error loading property bricks: {e}")
#
#     def filter_bricks(self):
#         """Filter property bricks based on search text"""
#         search_text = self.search_edit.text().lower().strip()
#
#         self.bricks_list.clear()
#
#         for brick in self.all_bricks:
#             # Filter by search text
#             if (search_text == "" or
#                 search_text in brick.name.lower() or
#                 search_text in brick.description.lower()):
#
#                 display_text = f"{brick.name}"
#                 if brick.description:
#                     display_text += f" - {brick.description}"
#                 if brick.property_path:
#                     display_text += f" (path: {brick.property_path})"
#
#                 list_item = QListWidgetItem(display_text)
#                 list_item.setData(Qt.ItemDataRole.UserRole, brick)
#                 self.bricks_list.addItem(list_item)
#
#     def on_brick_selected(self, item):
#         """Handle brick double-click"""
#         self.selected_brick = item.data(Qt.ItemDataRole.UserRole)
#         self.accept()
#
#     def on_select_clicked(self):
#         """Handle select button click"""
#         current_item = self.bricks_list.currentItem()
#         if current_item:
#             self.selected_brick = current_item.data(Qt.ItemDataRole.UserRole)
#             self.accept()


# class SimpleBrickEditor(QMainWindow):
#     """Minimal SHACL Brick Editor"""
#
#     def __init__(self):
#         super().__init__()
#         self.brick_core = BrickCore()
#         self.ontology_manager = CorrectedOntologyManager()
#
#         self.setWindowTitle("Simple SHACL Brick Editor")
#         self.setGeometry(100, 100, 800, 600)
#
#         self.setup_ui()
#         self.setup_connections()
#
#         # Create initial brick
#         self.brick_core.create_brick()
#         self.update_ui()
#
#     def setup_ui(self):
#         """Setup minimal UI"""
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
#
#         # Main layout
#         main_layout = QVBoxLayout()
#         central_widget.setLayout(main_layout)
#
#         # Brick info group
#         info_group = QGroupBox("Brick Information")
#         info_layout = QFormLayout()
#
#         # Name
#         self.name_edit = QLineEdit()
#         info_layout.addRow("Name:", self.name_edit)
#
#         # Object type
#         self.object_type_combo = QComboBox()
#         self.object_type_combo.addItems(["NodeShape", "PropertyShape"])
#         self.object_type_combo.currentTextChanged.connect(self.on_field_changed)
#         info_layout.addRow("Type:", self.object_type_combo)
#
#         # Target field
#         self.target_edit = QLineEdit()
#         self.target_label = QLabel("Target Class:")
#         self.browse_btn = QPushButton("Browse")
#         self.browse_btn.clicked.connect(self.browse_ontology)
#
#         target_layout = QHBoxLayout()
#         target_layout.addWidget(self.target_edit)
#         target_layout.addWidget(self.browse_btn)
#         info_layout.addRow(self.target_label, target_layout)
#
#         # Description
#         self.description_edit = QTextEdit()
#         self.description_edit.setMaximumHeight(80)
#         info_layout.addRow("Description:", self.description_edit)
#
#         info_group.setLayout(info_layout)
#         main_layout.addWidget(info_group)
#
#         # Properties list
#         props_group = QGroupBox("Properties")
#         props_layout = QVBoxLayout()
#
#         self.properties_list = QListWidget()
#         props_layout.addWidget(self.properties_list)
#
#         # Property buttons
#         prop_buttons = QHBoxLayout()
#
#         add_prop_btn = QPushButton("Add Property")
#         add_prop_btn.clicked.connect(self.add_property)
#         prop_buttons.addWidget(add_prop_btn)
#
#         add_prop_brick_btn = QPushButton("Add Property Brick")
#         add_prop_brick_btn.clicked.connect(self.add_property_brick)
#         prop_buttons.addWidget(add_prop_brick_btn)
#
#         edit_prop_btn = QPushButton("Edit")
#         edit_prop_btn.clicked.connect(self.edit_property)
#         prop_buttons.addWidget(edit_prop_btn)
#
#         remove_prop_btn = QPushButton("Remove")
#         remove_prop_btn.clicked.connect(self.remove_property)
#         prop_buttons.addWidget(remove_prop_btn)
#
#         props_layout.addLayout(prop_buttons)
#         props_group.setLayout(props_layout)
#         main_layout.addWidget(props_group)
#
#         # Action buttons
#         action_buttons = QHBoxLayout()
#
#         save_btn = QPushButton("Save Brick")
#         save_btn.clicked.connect(self.save_brick)
#         action_buttons.addWidget(save_btn)
#
#         new_btn = QPushButton("New Brick")
#         new_btn.clicked.connect(self.new_brick)
#         action_buttons.addWidget(new_btn)
#
#         main_layout.addLayout(action_buttons)
#
#         # Library browser
#         library_group = QGroupBox("Library")
#         lib_layout = QVBoxLayout()
#
#         # Library selector
#         self.library_combo = QComboBox()
#         self.library_combo.currentTextChanged.connect(self.on_library_changed)
#         lib_layout.addWidget(QLabel("Library:"))
#         lib_layout.addWidget(self.library_combo)
#
#         # Bricks list
#         self.bricks_list = QListWidget()
#         self.bricks_list.itemDoubleClicked.connect(self.load_brick_from_list)
#         lib_layout.addWidget(QLabel("Bricks:"))
#         lib_layout.addWidget(self.bricks_list)
#
#         # Library buttons
#         lib_buttons = QHBoxLayout()
#
#         refresh_btn = QPushButton("Refresh")
#         refresh_btn.clicked.connect(self.load_library)
#         lib_buttons.addWidget(refresh_btn)
#
#         delete_btn = QPushButton("Delete")
#         delete_btn.clicked.connect(self.delete_brick)
#         lib_buttons.addWidget(delete_btn)
#
#         lib_layout.addLayout(lib_buttons)
#         library_group.setLayout(lib_layout)
#         main_layout.addWidget(library_group)
#
#         # Update library list
#         self.load_library()
#
#     def setup_connections(self):
#         """Setup signal connections"""
#         self.name_edit.textChanged.connect(self.on_field_changed)
#         self.description_edit.textChanged.connect(self.on_field_changed)
#         self.target_edit.textChanged.connect(self.on_field_changed)
#
#     def browse_ontology(self):
#         """Browse ontology for class or property selection"""
#         try:
#             # Determine mode based on object type
#             if self.object_type_combo.currentText() == "NodeShape":
#                 mode = "classes"
#             else:
#                 mode = "properties"
#
#             # Create and show ontology browser dialog
#             dialog = SimpleOntologyBrowser(self.ontology_manager, self, mode)
#
#             if dialog.exec() == QDialog.DialogCode.Accepted:
#                 selected_item = dialog.selected_item
#                 if selected_item:
#                     # Set the target field with the selected URI
#                     self.target_edit.setText(selected_item['uri'])
#         except Exception as e:
#             print(f"Error browsing ontology: {e}")
#
#     def on_field_changed(self):
#         """Handle field changes"""
#         if self.brick_core.current_brick:
#             # Update the brick object type when user changes it
#             current_type = self.object_type_combo.currentText()
#             if self.brick_core.current_brick.object_type != current_type:
#                 self.brick_core.current_brick.object_type = current_type
#
#             self.brick_core.update_current_brick(
#                 name=self.name_edit.text(),
#                 description=self.description_edit.toPlainText(),
#                 target_class=self.target_edit.text() if current_type == "NodeShape" else "",
#                 property_path=self.target_edit.text() if current_type == "PropertyShape" else ""
#             )
#
#         # Update the target field label based on brick type
#         if self.object_type_combo.currentText() == "PropertyShape":
#             self.target_label.setText("Property Path:")
#             self.target_edit.setPlaceholderText("e.g., ex:name, schema:description")
#         else:
#             self.target_label.setText("Target Class:")
#             self.target_edit.setPlaceholderText("e.g., ex:Person, schema:Organization")
#
#     def add_property(self):
#         """Add a property using the property editor"""
#         if not self.brick_core.current_brick:
#             return
#
#         # Open property editor dialog
#         dialog = PropertyEditorDialog(self, ontology_manager=self.ontology_manager)
#         if dialog.exec() == QDialog.DialogCode.Accepted:
#             property_data = dialog.get_property_data()
#             if property_data.get('name'):  # Only add if name is provided
#                 self.brick_core.add_property(property_data['name'], property_data)
#                 self.update_ui()
#
#     def add_property_brick(self):
#         """Add an existing property brick to current node brick"""
#         if not self.brick_core.current_brick:
#             return
#
#         # Only allow adding property bricks to node shapes
#         if self.brick_core.current_brick.object_type != "NodeShape":
#             QMessageBox.warning(self, "Warning", "Property bricks can only be added to NodeShape bricks.")
#             return
#
#         # Open property brick browser
#         dialog = PropertyBrickBrowser(self, self.brick_core)
#         if dialog.exec() == QDialog.DialogCode.Accepted:
#             selected_brick = dialog.selected_brick
#             if selected_brick:
#                 # Add property brick as a reference
#                 self.add_property_brick_reference(selected_brick)
#                 self.update_ui()
#
#     def add_property_brick_reference(self, property_brick):
#         """Add a property brick reference to current node brick"""
#         # Create a property reference that points to the property brick
#         prop_name = property_brick.name
#         prop_data = {
#             'property_brick_id': property_brick.brick_id,
#             'property_brick_name': property_brick.name,
#             'property_path': property_brick.property_path,
#             'datatype': property_brick.properties.get('datatype', 'xsd:string') if property_brick.properties else 'xsd:string',
#             'constraints': property_brick.properties.get('constraints', []) if property_brick.properties else [],
#             'is_property_brick': True,
#             'description': property_brick.description
#         }
#
#         self.brick_core.add_property(prop_name, prop_data)
#
#     def edit_property(self):
#         """Edit selected property"""
#         if not self.brick_core.current_brick:
#             return
#
#         current_item = self.properties_list.currentItem()
#         if not current_item:
#             return
#
#         prop_data = current_item.data(Qt.ItemDataRole.UserRole)
#         if not prop_data:
#             return
#
#         # Open property editor dialog with existing data
#         dialog = PropertyEditorDialog(self, property_data=prop_data, ontology_manager=self.ontology_manager)
#         if dialog.exec() == QDialog.DialogCode.Accepted:
#             updated_property_data = dialog.get_property_data()
#             if updated_property_data.get('name'):
#                 # Update the property in the brick
#                 self.brick_core.remove_property(prop_data['name'])
#                 self.brick_core.add_property(updated_property_data['name'], updated_property_data)
#                 self.update_ui()
#
#     def remove_property(self):
#         """Remove selected property"""
#         if not self.brick_core.current_brick:
#             return
#
#         current_item = self.properties_list.currentItem()
#         if not current_item:
#             return
#
#         prop_data = current_item.data(Qt.ItemDataRole.UserRole)
#         if not prop_data:
#             return
#
#         prop_name = prop_data.get('name')
#         if prop_name:
#             self.brick_core.remove_property(prop_name)
#             self.update_ui()
#
#     def save_brick(self):
#         """Save current brick"""
#         if self.brick_core.save_brick():
#             QMessageBox.information(self, "Success", "Brick saved successfully!")
#             self.load_library()
#         else:
#             QMessageBox.warning(self, "Error", "Failed to save brick. Please check required fields.")
#
#     def new_brick(self):
#         """Create new brick"""
#         # Use the currently selected brick type from the UI
#         brick_type = self.object_type_combo.currentText()
#         self.brick_core.create_brick(brick_type=brick_type)
#         self.update_ui()
#
#     def on_library_changed(self, library_name: str):
#         """Handle library change"""
#         try:
#             self.brick_core.set_active_library(library_name)
#             bricks = self.brick_core.get_all_bricks()
#             self.bricks_list.clear()
#
#             for brick in bricks:
#                 display_text = f"{brick.name} ({brick.object_type})"
#                 self.bricks_list.addItem(display_text)
#                 self.bricks_list.item(self.bricks_list.count() - 1).setData(Qt.ItemDataRole.UserRole, brick)
#         except Exception as e:
#             print(f"Error loading library: {e}")
#
#     def load_library(self):
#         """Load library bricks"""
#         try:
#             libraries = self.brick_core.get_libraries()
#             self.library_combo.clear()
#             self.library_combo.addItems(libraries)
#
#             bricks = self.brick_core.get_all_bricks()
#             self.bricks_list.clear()
#
#             for brick in bricks:
#                 display_text = f"{brick.name} ({brick.object_type})"
#                 self.bricks_list.addItem(display_text)
#                 self.bricks_list.item(self.bricks_list.count() - 1).setData(Qt.ItemDataRole.UserRole, brick)
#         except Exception as e:
#             print(f"Error loading library: {e}")
#             self.library_combo.clear()
#             self.library_combo.addItems(["default"])
#
#     def load_brick_from_list(self, item):
#         """Load brick from list"""
#         brick = item.data(Qt.ItemDataRole.UserRole)
#         if brick:
#             self.brick_core.load_brick(brick.brick_id)
#             self.update_ui()
#
#     def delete_brick(self):
#         """Delete selected brick"""
#         current_item = self.bricks_list.currentItem()
#         if not current_item:
#             return
#
#         brick = current_item.data(Qt.ItemDataRole.UserRole)
#         if not brick:
#             return
#
#         reply = QMessageBox.question(
#             self,
#             "Confirm Delete",
#             f"Delete brick '{brick.name}'?",
#             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
#             QMessageBox.StandardButton.No
#         )
#
#         if reply == QMessageBox.StandardButton.Yes:
#             if self.brick_core.delete_brick(brick.brick_id):
#                 self.load_library()
#                 QMessageBox.information(self, "Success", "Brick deleted successfully!")
#
#     def update_ui(self):
#         """Update UI to reflect current brick"""
#         brick = self.brick_core.current_brick
#         if not brick:
#             return
#
#         # Block signals to prevent interference during UI updates
#         self.object_type_combo.blockSignals(True)
#
#         self.name_edit.setText(brick.name)
#         self.description_edit.setText(brick.description)
#         self.object_type_combo.setCurrentText(brick.object_type)
#
#         # Update target field label and content based on brick type
#         if brick.object_type == "NodeShape":
#             self.target_label.setText("Target Class:")
#             self.target_edit.setPlaceholderText("e.g., ex:Person, schema:Organization")
#             self.target_edit.setText(brick.target_class)
#         else:
#             self.target_label.setText("Property Path:")
#             self.target_edit.setPlaceholderText("e.g., ex:name, schema:description")
#             self.target_edit.setText(brick.property_path)
#
#         # Re-enable signals
#         self.object_type_combo.blockSignals(False)
#
#         # Update properties list
#         self.properties_list.clear()
#         for prop_name, prop_data in brick.properties.items():
#             # Create detailed display text
#             display_parts = [prop_name]
#
#             if isinstance(prop_data, dict):
#                 # Check if this is a property brick reference
#                 if prop_data.get('is_property_brick'):
#                     display_parts.append("[Property Brick]")
#                     if 'property_path' in prop_data and prop_data['property_path']:
#                         display_parts.append(f"path: {prop_data['property_path']}")
#                     if 'description' in prop_data and prop_data['description']:
#                         display_parts.append(f"brick: {prop_data['description']}")
#                 else:
#                     # Regular property
#                     if 'path' in prop_data and prop_data['path']:
#                         display_parts.append(f"path: {prop_data['path']}")
#                     if 'datatype' in prop_data and prop_data['datatype']:
#                         display_parts.append(f"type: {prop_data['datatype']}")
#                     if 'constraints' in prop_data and prop_data['constraints']:
#                         constraint_count = len(prop_data['constraints'])
#                         display_parts.append(f"{constraint_count} constraints")
#
#             display_text = " | ".join(display_parts)
#
#             # Create list item with full property data
#             list_item = QListWidgetItem(display_text)
#             # Store the complete property data for editing
#             full_prop_data = {
#                 'name': prop_name,
#                 **prop_data
#             }
#             list_item.setData(Qt.ItemDataRole.UserRole, full_prop_data)
#             self.properties_list.addItem(list_item)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Use the original stateful GUI with Qt Designer UI
    from stateful_gui import StatefulBrickEditor
    window = StatefulBrickEditor()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
