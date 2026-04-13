#!/usr/bin/env python3
"""
SHACL Editor - Two-tier ontology/term builder
Based on PeriConto approach but adapted for SHACL shapes

Architecture:
1. Ontology List - Public ontologies to import terms from
2. Term List - Specific terms available from selected ontology
3. Brick System - Reusable SHACL components
4. Visual Builder - Drag-and-drop SHACL shape creation
5. Export - Generate SHACL Turtle for form generation
"""

import sys
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from rdflib import Graph, Namespace, Literal, URIRef
import json

# SHACL Namespaces
SH = Namespace("http://www.w3.org/ns/shacl#")
DASH = Namespace("http://datashapes.org/dash#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

class SHACLEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SHACL Editor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Data structures
        self.ontologies = {}
        self.current_ontology = None
        self.current_terms = []
        self.brick_types = {
            "NodeShape": {
                "icon": "📋",
                "color": "#4CAF50",
                "properties": ["targetClass", "description"]
            },
            "PropertyShape": {
                "icon": "🔗", 
                "color": "#2196F3",
                "properties": ["path", "name", "datatype", "minCount", "maxCount", "description", "nodeKind", "class"]
            }
        }
        self.primitive_types = {
            "string": {"datatype": XSD.string, "icon": "📝"},
            "integer": {"datatype": XSD.integer, "icon": "🔢"},
            "decimal": {"datatype": XSD.decimal, "icon": "🔢"},
            "date": {"datatype": XSD.date, "icon": "📅"},
            "boolean": {"datatype": XSD.boolean, "icon": "☑️"},
            "uri": {"datatype": XSD.anyURI, "icon": "🔗"}
        }
        
        self.init_ui()
        self.load_sample_ontologies()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Ontology/Term selection
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Center panel - Brick builder
        center_panel = self.create_center_panel()
        main_layout.addWidget(center_panel, 2)
        
        # Right panel - SHACL preview
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
    
    def create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Ontology selection
        layout.addWidget(QLabel("📚 Ontologies"))
        self.ontology_list = QListWidget()
        self.ontology_list.itemClicked.connect(self.on_ontology_selected)
        layout.addWidget(self.ontology_list)
        
        # Term selection
        layout.addWidget(QLabel("📋 Terms"))
        self.term_list = QListWidget()
        self.term_list.itemDoubleClicked.connect(self.on_term_selected)
        layout.addWidget(self.term_list)
        
        return panel
    
    def create_center_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Brick creation toolbar
        toolbar_layout = QHBoxLayout()
        
        # NodeShape brick
        node_btn = QPushButton("📋 NodeShape")
        node_btn.clicked.connect(lambda: self.create_brick("NodeShape"))
        node_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
        toolbar_layout.addWidget(node_btn)
        
        # PropertyShape brick
        prop_btn = QPushButton("🔗 PropertyShape")
        prop_btn.clicked.connect(lambda: self.create_brick("PropertyShape"))
        prop_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 5px;")
        toolbar_layout.addWidget(prop_btn)
        
        # Primitive brick
        primitive_btn = QPushButton("🧩 Primitive")
        primitive_btn.clicked.connect(self.create_primitive)
        primitive_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 5px;")
        toolbar_layout.addWidget(primitive_btn)
        
        layout.addLayout(toolbar_layout)
        
        # Brick tree
        layout.addWidget(QLabel("🧱 SHACL Bricks"))
        self.brick_tree = QTreeWidget()
        self.brick_tree.setHeaderLabels(["Type", "Name", "Properties"])
        self.brick_tree.setColumnWidth(0, 150)
        self.brick_tree.setColumnWidth(1, 200)
        self.brick_tree.itemClicked.connect(self.on_brick_selected)
        layout.addWidget(self.brick_tree)
        
        return panel
    
    def create_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # SHACL preview
        layout.addWidget(QLabel("👁 SHACL Preview"))
        self.shacl_preview = QTextEdit()
        self.shacl_preview.setReadOnly(True)
        self.shacl_preview.setFont(QFont("Courier", 10))
        self.shacl_preview.setStyleSheet("background-color: #f5f5f5; padding: 10px;")
        layout.addWidget(self.shacl_preview)
        
        # Export button
        export_btn = QPushButton("💾 Export SHACL")
        export_btn.clicked.connect(self.export_shacl)
        export_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; font-weight: bold;")
        layout.addWidget(export_btn)
        
        return panel
    
    def load_sample_ontologies(self):
        """Load sample public ontologies"""
        self.ontologies = {
            "FOAF": {
                "uri": "http://xmlns.com/foaf/0.1/",
                "terms": {
                    "Person": {"description": "A person"},
                    "Organization": {"description": "An organization"},
                    "name": {"description": "A name"},
                    "mbox": {"description": "Email address"}
                }
            },
            "Schema.org": {
                "uri": "http://schema.org/",
                "terms": {
                    "Person": {"description": "A person"},
                    "Organization": {"description": "An organization"},
                    "name": {"description": "The name of the item"},
                    "email": {"description": "Email address"},
                    "birthDate": {"description": "Date of birth"},
                    "address": {"description": "Postal address"}
                }
            },
            "DCTERMS": {
                "uri": "http://purl.org/dc/terms/",
                "terms": {
                    "Agent": {"description": "A person, organization, or service"},
                    "title": {"description": "A name for the resource"},
                    "description": {"description": "An account of the resource"},
                    "date": {"description": "Date of creation or modification"}
                }
            }
        }
        
        self.ontology_list.clear()
        for name, data in self.ontologies.items():
            item = QListWidgetItem(f"{name}: {data['uri']}")
            item.setData(Qt.UserRole, data)
            self.ontology_list.addItem(item)
    
    def on_ontology_selected(self, item):
        """Handle ontology selection"""
        ontology_data = item.data(Qt.UserRole)
        self.current_ontology = ontology_data
        
        # Update term list
        self.term_list.clear()
        for term_name, term_data in ontology_data["terms"].items():
            item = QListWidgetItem(f"{term_name}: {term_data.get('description', '')}")
            item.setData(Qt.UserRole, {"name": term_name, **term_data})
            self.term_list.addItem(item)
    
    def on_term_selected(self, item):
        """Handle term double-click - add to brick tree"""
        term_data = item.data(Qt.UserRole)
        if term_data:
            self.create_brick_from_term(term_data)
    
    def create_brick(self, brick_type):
        """Create a new SHACL brick"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Create {brick_type}")
        layout = QVBoxLayout(dialog)
        
        # Brick type selection
        type_group = QGroupBox("Brick Type")
        type_layout = QVBoxLayout(type_group)
        
        for bt_name, bt_data in self.brick_types.items():
            btn = QRadioButton(f"{bt_data['icon']} {bt_name}")
            btn.setProperty("brick_type", bt_name)
            type_layout.addWidget(btn)
        
        layout.addWidget(type_group)
        
        # Properties
        props_group = QGroupBox("Properties")
        props_layout = QFormLayout(props_group)
        
        for prop in self.brick_types[brick_type]["properties"]:
            if prop == "datatype":
                combo = QComboBox()
                combo.addItems(["string", "integer", "decimal", "date", "boolean", "uri"])
                props_layout.addRow(prop, combo)
            else:
                line_edit = QLineEdit()
                props_layout.addRow(prop, line_edit)
        
        layout.addWidget(props_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("Create")
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        if dialog.exec_():
            self.add_brick_to_tree(brick_type, dialog)
    
    def create_primitive(self):
        """Create a primitive brick"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Primitive")
        layout = QVBoxLayout(dialog)
        
        # Primitive type
        type_group = QGroupBox("Primitive Type")
        type_layout = QVBoxLayout(type_group)
        
        for prim_name, prim_data in self.primitive_types.items():
            btn = QRadioButton(f"{prim_data['icon']} {prim_name}")
            btn.setProperty("primitive_type", prim_name)
            type_layout.addWidget(btn)
        
        layout.addWidget(type_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("Create")
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        if dialog.exec_():
            self.add_primitive_to_tree(dialog)
    
    def create_brick_from_term(self, term_data):
        """Create a brick from ontology term"""
        # Create NodeShape for ontology term
        brick_name = f"{term_data['name']}Shape"
        
        # Get selected brick type
        brick_type = "NodeShape"
        
        # Create the brick
        self.add_brick_item(brick_type, brick_name, {
            "targetClass": f"http://example.org/{term_data['name']}",
            "description": term_data.get('description', '')
        })
        
        self.update_shacl_preview()
    
    def add_brick_to_tree(self, brick_type, dialog):
        """Add brick to tree from dialog"""
        # Get selected brick type
        selected_type = None
        for btn in dialog.findChildren(QRadioButton):
            if btn.isChecked():
                selected_type = btn.property("brick_type")
                break
        
        if not selected_type:
            return
        
        # Get properties
        properties = {}
        for prop_name in self.brick_types[selected_type]["properties"]:
            widget = dialog.findChild(QLineEdit, prop_name)
            if widget:
                properties[prop_name] = widget.text()
        
        # Get brick name
        name_widget = dialog.findChild(QLineEdit)
        brick_name = name_widget.text() if name_widget else f"New{selected_type}"
        
        self.add_brick_item(selected_type, brick_name, properties)
        self.update_shacl_preview()
    
    def add_primitive_to_tree(self, dialog):
        """Add primitive to tree from dialog"""
        # Get selected primitive type
        selected_type = None
        for btn in dialog.findChildren(QRadioButton):
            if btn.isChecked():
                selected_type = btn.property("primitive_type")
                break
        
        if not selected_type:
            return
        
        # Get primitive name
        name_widget = dialog.findChild(QLineEdit)
        if not name_widget:
            return
        
        primitive_name = name_widget.text()
        
        # Create primitive brick
        self.add_brick_item("Primitive", primitive_name, {
            "type": selected_type,
            "icon": self.primitive_types[selected_type]["icon"]
        })
        
        self.update_shacl_preview()
    
    def add_brick_item(self, brick_type, brick_name, properties):
        """Add brick item to tree"""
        # Create tree item
        item = QTreeWidgetItem(self.brick_tree)
        item.setText(0, f"{self.brick_types[brick_type]['icon']} {brick_type}")
        item.setText(1, brick_name)
        item.setData(0, Qt.UserRole, brick_type)
        item.setData(1, Qt.UserRole, properties)
        
        # Color coding
        color = QColor(self.brick_types[brick_type]["color"])
        item.setForeground(0, color)
        
        # Add to tree
        self.brick_tree.addTopLevelItem(item)
        item.setExpanded(True)
    
    def on_brick_selected(self, item, column):
        """Handle brick selection"""
        if column == 1:  # Name column
            brick_type = item.data(0, Qt.UserRole)
            properties = item.data(1, Qt.UserRole)
            self.update_shacl_preview()
    
    def update_shacl_preview(self):
        """Update SHACL preview based on current bricks"""
        g = Graph()
        
        # Add prefixes
        g.bind("sh", SH)
        g.bind("dash", DASH)
        g.bind("ex", "http://example.org/")
        g.bind("xsd", XSD)
        
        # Generate SHACL from bricks
        for i in range(self.brick_tree.topLevelItemCount()):
            brick_item = self.brick_tree.topLevelItem(i)
            brick_type = brick_item.data(0, Qt.UserRole)
            brick_name = brick_item.text(1)
            properties = brick_item.data(1, Qt.UserRole) or {}
            
            if brick_type == "NodeShape":
                self.create_node_shape(g, brick_name, properties)
            elif brick_type == "PropertyShape":
                self.create_property_shape(g, brick_name, properties)
            elif brick_type == "Primitive":
                self.create_primitive_shape(g, brick_name, properties)
        
        # Update preview
        self.shacl_preview.setPlainText(g.serialize(format="turtle"))
    
    def create_node_shape(self, g, shape_name, properties):
        """Create a SHACL NodeShape"""
        shape_uri = URIRef(f"http://example.org/{shape_name}")
        g.add((shape_uri, RDF.type, SH.NodeShape))
        
        if "targetClass" in properties:
            g.add((shape_uri, SH.targetClass, URIRef(properties["targetClass"])))
        
        if "description" in properties:
            g.add((shape_uri, SH.description, Literal(properties["description"])))
        
        # Add property shapes
        for prop_name, prop_value in properties.items():
            if prop_name.startswith("property_"):
                self.add_property_to_shape(g, shape_uri, prop_name.replace("property_", ""), prop_value)
    
    def create_property_shape(self, g, shape_name, properties):
        """Create a SHACL PropertyShape"""
        prop_uri = URIRef(f"http://example.org/{shape_name}")
        g.add((prop_uri, RDF.type, SH.PropertyShape))
        
        for prop_name, prop_value in properties.items():
            if prop_name in ["path", "name", "datatype", "minCount", "maxCount", "description"]:
                if prop_value:
                    g.add((prop_uri, getattr(SH, prop_name), URIRef(prop_value) if prop_name == "path" else Literal(prop_value)))
    
    def create_primitive_shape(self, g, primitive_name, properties):
        """Create a primitive shape (for reuse)"""
        prim_uri = URIRef(f"http://example.org/{primitive_name}")
        g.add((prim_uri, RDF.type, SH.NodeShape))
        
        # Add primitive type
        if "type" in properties:
            prim_type = properties["type"]
            if prim_type in self.primitive_types:
                datatype = self.primitive_types[prim_type]["datatype"]
                g.add((prim_uri, SH.targetClass, datatype))
        
        if "icon" in properties:
            g.add((prim_uri, SH.description, Literal(properties["icon"])))
    
    def export_shacl(self):
        """Export SHACL to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export SHACL",
            "",
            "SHACL Files (*.ttl);;All Files (*)"
        )
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.shacl_preview.toPlainText())
            QMessageBox.information(self, "Export Complete", f"SHACL exported to {file_path}")


def main():
    app = QApplication(sys.argv)
    editor = SHACLEditor()
    editor.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
