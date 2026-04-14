#!/usr/bin/env python3
"""
Final SHACL Brick Generator
Working ontology browser with property management
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QTabWidget, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QListWidget, QListWidgetItem,
    QDialog, QDialogButtonBox, QFileDialog, QGroupBox
)
from PyQt6.QtCore import Qt

from shacl_brick_app.core.brick_backend import BrickBackendAPI
from shacl_brick_app.core.editor_backend import BrickEditorBackend

class FinalGuidedGUI(QMainWindow):
    """Final brick editor with working ontology browser and property management"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧱 SHACL Brick Generator - Final")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize backend
        self.brick_api = BrickBackendAPI()
        self.editor_backend = BrickEditorBackend(self.brick_api)
        self.current_brick = {}
        self.current_properties = {}
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("🧱 SHACL Brick Generator - Final")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px;")
        layout.addWidget(header)
        
        # Main content
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_editor_tab()
        self.create_browser_tab()
        
        # Status bar
        self.statusBar().showMessage("✅ Ready - Final version with all features")
    
    def create_editor_tab(self):
        """Create editor tab with property management"""
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        # Brick information
        info_group = QGroupBox("📋 Brick Information")
        info_layout = QFormLayout(info_group)
        
        # Brick name
        name_layout = QHBoxLayout()
        self.brick_name_edit = QLineEdit()
        self.brick_name_edit.setPlaceholderText("e.g., Student Registration, Product Catalog")
        name_layout.addWidget(QLabel("Name:"))
        name_layout.addWidget(self.brick_name_edit)
        help_btn = QPushButton("?")
        help_btn.setToolTip("Get help with brick naming")
        help_btn.setMaximumWidth(25)
        help_btn.clicked.connect(lambda: QMessageBox.information(self, "Brick Name", 
            "Enter a descriptive name for your brick:\n\nExamples:\n• Student Registration\n• Product Catalog\n• Address Validator\n• Equipment Monitor"))
        name_layout.addWidget(help_btn)
        info_layout.addRow(name_layout)
        
        # Target class
        target_layout = QHBoxLayout()
        self.target_class_edit = QLineEdit()
        self.target_class_edit.setPlaceholderText("e.g., schema:Student, schema:Product")
        target_layout.addWidget(QLabel("Target Class:"))
        target_layout.addWidget(self.target_class_edit)
        browse_btn = QPushButton("📚 Browse")
        browse_btn.setToolTip("Browse ontologies to select a class")
        browse_btn.clicked.connect(self.browse_classes)
        target_layout.addWidget(browse_btn)
        info_layout.addRow(target_layout)
        
        # Object type
        self.object_type_combo = QComboBox()
        self.object_type_combo.addItems(["NodeShape", "PropertyShape"])
        info_layout.addRow("Object Type:", self.object_type_combo)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Describe what this brick validates...")
        self.description_edit.setMaximumHeight(80)
        info_layout.addRow("Description:", self.description_edit)
        
        editor_layout.addWidget(info_group)
        
        # Properties management
        props_group = QGroupBox("🏷️ Properties")
        props_layout = QVBoxLayout(props_group)
        
        # Properties list
        self.properties_list = QListWidget()
        self.properties_list.setMaximumHeight(200)
        self.properties_list.itemClicked.connect(self.on_property_selected)
        props_layout.addWidget(self.properties_list)
        
        # Property buttons
        prop_buttons_layout = QHBoxLayout()
        
        add_prop_btn = QPushButton("➕ Add Property")
        add_prop_btn.clicked.connect(self.add_property)
        prop_buttons_layout.addWidget(add_prop_btn)
        
        remove_prop_btn = QPushButton("➖ Remove Selected")
        remove_prop_btn.clicked.connect(self.remove_property)
        prop_buttons_layout.addWidget(remove_prop_btn)
        
        props_layout.addLayout(prop_buttons_layout)
        editor_layout.addWidget(props_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        new_btn = QPushButton("🆕 New Brick")
        new_btn.clicked.connect(self.create_new_brick)
        action_layout.addWidget(new_btn)
        
        save_btn = QPushButton("💾 Save Brick")
        save_btn.clicked.connect(self.save_brick)
        action_layout.addWidget(save_btn)
        
        load_btn = QPushButton("📁 Load Brick")
        load_btn.clicked.connect(self.load_brick)
        action_layout.addWidget(load_btn)
        
        export_btn = QPushButton("📤 Export SHACL")
        export_btn.clicked.connect(self.export_shacl)
        action_layout.addWidget(export_btn)
        
        action_layout.addStretch()
        editor_layout.addLayout(action_layout)
        
        self.tabs.addTab(editor_widget, "🔧 Brick Editor")
    
    def browse_classes(self):
        """Browse ontologies for target class selection"""
        self.tabs.setCurrentIndex(1)  # Switch to browser tab
        self.statusBar().showMessage("📚 Switched to ontology browser")
    
    def create_browser_tab(self):
        """Create ontology browser tab (working version)"""
        browser_widget = QWidget()
        browser_layout = QVBoxLayout(browser_widget)
        
        # Header
        header_label = QLabel("📚 Browse Ontologies")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background: #e8f5e8; border-radius: 5px;")
        browser_layout.addWidget(header_label)
        
        # Instructions
        instructions = QLabel(
            "💡 <b>How to use:</b><br>"
            "1. Click an ontology to see its classes and properties<br>"
            "2. Double-click a class to use it as target class<br>"
            "3. Double-click a property to copy its URI for property editors"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 10px; background: #f0f8ff; border: 1px solid #d0e3ff; border-radius: 3px; margin-bottom: 10px;")
        browser_layout.addWidget(instructions)
        
        # Content area
        content_layout = QHBoxLayout()
        
        # Left: Ontology list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("📋 Available Ontologies:"))
        self.ontology_list = QListWidget()
        self.ontology_list.itemClicked.connect(self.on_ontology_selected)
        left_layout.addWidget(self.ontology_list)
        content_layout.addWidget(left_widget)
        
        # Right: Terms list
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel("🏷️ Classes & Properties:"))
        self.terms_list = QListWidget()
        self.terms_list.itemDoubleClicked.connect(self.on_term_selected)
        right_layout.addWidget(self.terms_list)
        content_layout.addWidget(right_widget)
        
        browser_layout.addLayout(content_layout)
        
        # Import button
        import_btn = QPushButton("📥 Import Ontology File")
        import_btn.clicked.connect(self.import_ontology)
        browser_layout.addWidget(import_btn)
        
        self.tabs.addTab(browser_widget, "📚 Ontology Browser")
        
        # Load ontologies
        self.load_ontologies()
    
    def load_ontologies(self):
        """Load and display available ontologies"""
        ontologies = self.editor_backend.ontology_manager.ontologies
        
        self.ontology_list.clear()
        for name, data in ontologies.items():
            class_count = len(data.get('classes', []))
            prop_count = len(data.get('properties', []))
            item = QListWidgetItem(f"{name} ({class_count} classes, {prop_count} properties)")
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.ontology_list.addItem(item)
    
    def on_ontology_selected(self, item):
        """Handle ontology selection"""
        ontology_name = item.data(Qt.ItemDataRole.UserRole)
        ontologies = self.editor_backend.ontology_manager.ontologies
        
        if ontology_name and ontology_name in ontologies:
            # Display terms
            self.display_ontology_terms(ontologies[ontology_name])
    
    def display_ontology_terms(self, ontology_data):
        """Display terms from selected ontology"""
        self.terms_list.clear()
        
        # Display classes
        if 'classes' in ontology_data:
            class_item = QListWidgetItem("=== Classes ===")
            class_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.terms_list.addItem(class_item)
            
            for class_info in ontology_data['classes']:
                item = QListWidgetItem(f"Class: {class_info['name']}")
                item.setData(Qt.ItemDataRole.UserRole, {'type': 'class', **class_info})
                self.terms_list.addItem(item)
        
        # Display properties
        if 'properties' in ontology_data:
            prop_item = QListWidgetItem("=== Properties ===")
            prop_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.terms_list.addItem(prop_item)
            
            for prop_info in ontology_data['properties']:
                item = QListWidgetItem(f"Property: {prop_info['name']}")
                item.setData(Qt.ItemDataRole.UserRole, {'type': 'property', **prop_info})
                self.terms_list.addItem(item)
    
    def on_term_selected(self, item):
        """Handle term double-click"""
        term_data = item.data(Qt.ItemDataRole.UserRole)
        if term_data:
            if term_data.get("type") == "class":
                # Set target class
                self.target_class_edit.setText(term_data["uri"])
                self.statusBar().showMessage(f"✅ Class '{term_data['name']}' selected as target class")
            elif term_data.get("type") == "property":
                # Copy property URI to clipboard
                from PyQt6.QtWidgets import QApplication
                clipboard = QApplication.clipboard()
                clipboard.setText(term_data["uri"])
                self.statusBar().showMessage(f"✅ Property URI '{term_data['uri']}' copied to clipboard")
    
    def add_property(self):
        """Add a new property"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Property")
        dialog.setModal(True)
        dialog.resize(400, 200)
        
        layout = QFormLayout(dialog)
        
        name_edit = QLineEdit()
        layout.addRow("Property Name:", name_edit)
        
        path_edit = QLineEdit()
        layout.addRow("Property Path:", path_edit)
        
        datatype_combo = QComboBox()
        datatype_combo.addItems(["xsd:string", "xsd:integer", "xsd:decimal", "xsd:boolean", "xsd:date", "xsd:anyURI"])
        layout.addRow("Data Type:", datatype_combo)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            property_name = name_edit.text()
            if property_name:
                # Add to current properties
                self.current_properties[property_name] = {
                    "name": property_name,
                    "path": path_edit.text(),
                    "datatype": datatype_combo.currentText(),
                    "constraints": []
                }
                self.update_properties_display()
                self.statusBar().showMessage(f"✅ Property '{property_name}' added")
    
    def remove_property(self):
        """Remove selected property"""
        current_item = self.properties_list.currentItem()
        if current_item:
            prop_name = current_item.text()
            if prop_name in self.current_properties:
                del self.current_properties[prop_name]
                self.update_properties_display()
                self.statusBar().showMessage(f"✅ Property '{prop_name}' removed")
    
    def on_property_selected(self, item):
        """Handle property selection"""
        prop_name = item.text()
        if prop_name in self.current_properties:
            # Show property details
            prop_data = self.current_properties[prop_name]
            QMessageBox.information(self, "Property Details", 
                f"Name: {prop_data['name']}\n"
                f"Path: {prop_data['path']}\n"
                f"Data Type: {prop_data['datatype']}\n"
                f"Constraints: {len(prop_data.get('constraints', []))}")
    
    def update_properties_display(self):
        """Update the properties list display"""
        self.properties_list.clear()
        for prop_name, prop_data in self.current_properties.items():
            constraints_text = ", ".join([f"{c['constraint_type']}: {c['value']}" for c in prop_data.get("constraints", [])])
            display_text = f"🏷️ {prop_name} ({constraints_text})"
            self.properties_list.addItem(display_text)
    
    def create_new_brick(self):
        """Create a new brick"""
        self.current_brick = {}
        self.current_properties = {}
        
        self.brick_name_edit.clear()
        self.target_class_edit.clear()
        self.description_edit.clear()
        self.properties_list.clear()
        self.update_properties_display()
        
        self.statusBar().showMessage("✅ New brick created")
    
    def save_brick(self):
        """Save current brick"""
        if not self.brick_name_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a brick name")
            return
        
        if not self.target_class_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a target class")
            return
        
        # Prepare brick data
        brick_data = {
            "name": self.brick_name_edit.text(),
            "target_class": self.target_class_edit.text(),
            "description": self.description_edit.toPlainText(),
            "properties": self.current_properties,
            "object_type": self.object_type_combo.currentText()
        }
        
        success, message = self.editor_backend.save_brick(brick_data)
        if success:
            self.statusBar().showMessage(f"✅ {message}")
        else:
            QMessageBox.critical(self, "Save Error", message)
    
    def load_brick(self):
        """Load existing brick"""
        QMessageBox.information(self, "Load Brick", 
                           "Brick loading will be implemented in the next version.\n\n"
                           "For now, create new bricks or edit existing ones directly.")
    
    def export_shacl(self):
        """Export current brick to SHACL format"""
        if not self.current_brick:
            QMessageBox.warning(self, "No Brick", "Please create a brick first")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export SHACL",
            f"{self.brick_name_edit.text() or 'brick'}.ttl",
            "Turtle Files (*.ttl);;RDF/XML Files (*.rdf);;JSON-LD Files (*.jsonld)"
        )
        
        if file_path:
            # Simple SHACL export (placeholder)
            shacl_content = f"""@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/> .
@prefix schema: <http://schema.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:{self.brick_name_edit.text()} a sh:NodeShape ;
    sh:targetClass <{self.target_class_edit.text()}> ;
    sh:property [
"""
            
            # Add properties
            for prop_name, prop_data in self.current_properties.items():
                shacl_content += f"""        ex:{prop_name} a sh:property ;
        sh:path <{prop_data['path']}> ;
        sh:datatype <{prop_data['datatype']}> ;
        sh:severity sh:Violation ;
        sh:message "{prop_name} constraint violated"@ ;
"""
            
                # Add constraints
                for constraint in prop_data.get("constraints", []):
                    if constraint['constraint_type'] == 'minCount':
                        shacl_content += f"""        ex:{prop_name} sh:minCount {constraint['value']} ;"""
                    elif constraint['constraint_type'] == 'maxLength':
                        shacl_content += f"""        ex:{prop_name} sh:maxLength {constraint['value']} ;"""
                    elif constraint['constraint_type'] == 'pattern':
                        shacl_content += f"""        ex:{prop_name} sh:pattern "{constraint['value']}" ;"""
            
            shacl_content += """    ] ."""
            
            try:
                with open(file_path, 'w') as f:
                    f.write(shacl_content)
                self.statusBar().showMessage(f"✅ SHACL exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
    
    def import_ontology(self):
        """Import ontology file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Ontology",
            "",
            "Turtle Files (*.ttl);;RDF/XML Files (*.rdf);;JSON-LD Files (*.jsonld);;All Files (*)"
        )
        
        if file_path:
            success, message, ontology_data = self.editor_backend.ontology_manager.import_ontology(file_path)
            if success and ontology_data:
                ontology_name = f"Imported_{len(self.editor_backend.ontology_manager.ontologies)}"
                self.editor_backend.ontology_manager.ontologies[ontology_name] = ontology_data
                self.load_ontologies()
                self.statusBar().showMessage(f"✅ Ontology '{ontology_name}' imported successfully")
            else:
                QMessageBox.critical(self, "Import Error", message)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = FinalGuidedGUI()
    window.show()
    
    # Create initial brick
    window.create_new_brick()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
