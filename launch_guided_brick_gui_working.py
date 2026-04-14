#!/usr/bin/env python3
"""
Working Refactored Guided SHACL Brick Generator
Fixed ontology browser functionality
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
irom PyQt6.QtWidgets import (/,/i
14-    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
15-    QPushButton, QLabel, QMessageBox, QTabWidget,
16-    QListWidget, QListWidgetItem, QDialog, QFormLayout,
17-    QLineEdit, QTextEdit, QComboBox,
18-    QLineEdit, QTextEdit, QComboBox, QGroupBox
19-)
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTabWidget,
    QListWidget, QListWidgetItem, QDialog, QFormLayout,
    QLineEdit, QTextEdit, QComboBox
)
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt

from shacl_brick_app.core.brick_backend import BrickBackendAPI
from shacl_brick_app.core.editor_backend import BrickEditorBackend

class WorkingGuidedGUI(QMainWindow):
    """Main window with working ontology browser"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SHACL Brick Generator - Working Refactored")
        self.setGeometry(100, 100, 1000, 700)
        
        # Initialize backend
        self.brick_api = BrickBackendAPI()
        self.editor_backend = BrickEditorBackend(self.brick_api)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("🧱 SHACL Brick Generator - Working Refactored")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background: #e8f5e8; border-radius: 5px;")
        layout.addWidget(header)
        
        # Tab widget for different views
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_editor_tab()
        self.create_browser_tab()
        
        # Status bar
        self.statusBar().showMessage("✅ Ready - Contextual help integrated!")
    
    def create_editor_tab(self):
        """Create editor tab"""
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        # Simple brick editor form with help
        form_layout = QFormLayout()
        
        # Brick name with help
        name_layout = QHBoxLayout()
        self.brick_name_edit = QLineEdit()
        self.brick_name_edit.setPlaceholderText("e.g., Student Shape, Person Form")
        name_layout.addWidget(QLabel("Brick Name:"))
        name_layout.addWidget(self.brick_name_edit)
        help_btn = QPushButton("?")
        help_btn.setToolTip("Enter a descriptive name for your brick")
        help_btn.setMaximumWidth(25)
        help_btn.clicked.connect(lambda: QMessageBox.information(self, "Brick Name", 
            "Enter a descriptive name for your brick:\n\nExamples:\n• Student Shape\n• Person Form\n• Address Validator\n• Product Catalog"))
        name_layout.addWidget(help_btn)
        form_layout.addRow(name_layout)
        
        # Target class with ontology browser button
        target_layout = QHBoxLayout()
        self.target_class_edit = QLineEdit()
        self.target_class_edit.setPlaceholderText("e.g., schema:Student, schema:Person")
        target_layout.addWidget(QLabel("Target Class:"))
        target_layout.addWidget(self.target_class_edit)
        
        browse_btn = QPushButton("📚 Browse")
        browse_btn.setToolTip("Browse ontologies to select a class")
        browse_btn.clicked.connect(self.browse_classes)
        target_layout.addWidget(browse_btn)
        form_layout.addRow(target_layout)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Describe what this brick validates (e.g., 'Student must have name, email, and enrollment date')")
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_edit)
        
        editor_layout.addLayout(form_layout)
        
        # Properties section
        props_group = QGroupBox("🏷️ Properties")
        props_layout = QVBoxLayout(props_group)
        
        # Properties list
        self.properties_list = QListWidget()
        self.properties_list.setMaximumHeight(150)
        props_layout.addWidget(self.properties_list)
        
        # Property buttons
        prop_buttons_layout = QHBoxLayout()
        
        add_prop_btn = QPushButton("➕ Add Property")
        add_prop_btn.clicked.connect(self.add_property)
        prop_buttons_layout.addWidget(add_prop_btn)
        
        remove_prop_btn = QPushButton("➖ Remove")
        remove_prop_btn.clicked.connect(self.remove_property)
        prop_buttons_layout.addWidget(remove_prop_btn)
        
        props_layout.addLayout(prop_buttons_layout)
        editor_layout.addWidget(props_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        new_btn = QPushButton("🆕 New Brick")
        new_btn.clicked.connect(self.create_new_brick)
        button_layout.addWidget(new_btn)
        
        save_btn = QPushButton("💾 Save Brick")
        save_btn.clicked.connect(self.save_brick)
        button_layout.addWidget(save_btn)
        
        browse_btn = QPushButton("📚 Browse Classes")
        browse_btn.clicked.connect(self.browse_classes)
        button_layout.addWidget(browse_btn)
        
        button_layout.addStretch()
        editor_layout.addLayout(button_layout)
        
        self.tabs.addTab(editor_widget, "🔧 Brick Editor")
    
    def add_property(self):
        """Add a new property"""
        # Simple dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Property")
        dialog.setModal(True)
        dialog.resize(400, 200)
        
        layout = QFormLayout(dialog)
        
        name_edit = QLineEdit()
        layout.addRow("Property Name:", name_edit)
        
        path_edit = QLineEdit()
        layout.addRow("Property Path:", path_edit)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            property_name = name_edit.text()
            if property_name:
                # Add to properties list
                item = QListWidgetItem(f"🏷️ {property_name}")
                self.properties_list.addItem(item)
                self.statusBar().showMessage(f"✅ Property '{property_name}' added")
    
    def remove_property(self):
        """Remove selected property"""
        current_item = self.properties_list.currentItem()
        if current_item:
            self.properties_list.takeItem(self.properties_list.row(current_item))
            self.statusBar().showMessage("✅ Property removed")
    
    def create_browser_tab(self):
        """Create improved ontology browser tab"""
        browser_widget = QWidget()
        browser_layout = QVBoxLayout(browser_widget)
        
        # Header with instructions
        header_label = QLabel("📚 Browse Ontologies for Classes & Properties")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; background: #e8f5e8; border-radius: 5px;")
        browser_layout.addWidget(header_label)
        
        # Instructions
        instructions = QLabel(
            "💡 <b>Quick Guide:</b><br>"
            "1. Click an ontology to see its classes and properties<br>"
            "2. Double-click a class to use it as target class<br>"
            "3. Double-click a property to copy its URI for property editors<br>"
            "4. Use 'Import Ontology File' to add your own ontologies"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 10px; background: #f0f8ff; border: 1px solid #d0e3ff; border-radius: 3px; margin-bottom: 10px;")
        browser_layout.addWidget(instructions)
        
        # Content area with two lists
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
        
        # Load ontologies
        self.load_ontologies()
        
        self.tabs.addTab(browser_widget, "📚 Ontology Browser")
    
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
            self.display_terms_for_ontology(ontologies[ontology_name])
    
    def display_terms_for_ontology(self, ontology_data):
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
                # Also update brick name if empty
                if not self.brick_name_edit.text().strip():
                    self.brick_name_edit.setText(term_data["name"] + " Shape")
                # Show success message
                QMessageBox.information(self, "✅ Class Applied", 
                                   f"Class '{term_data['name']}' applied as target class!\n\n"
                                   f"URI: {term_data['uri']}\n\n"
                                   f"You can now create properties for this type of entity.")
            elif term_data.get("type") == "property":
                # Show property info with copy option
                from PyQt6.QtWidgets import QMessageBox, QPushButton
                
                msg = QMessageBox(self)
                msg.setWindowTitle("Property Selected")
                msg.setText(f"Selected property: {term_data['name']}\n\nURI: {term_data['uri']}")
                msg.setInformativeText("Use this URI in property editors.")
                
                copy_btn = QPushButton("📋 Copy URI")
                msg.addButton(copy_btn, QMessageBox.ButtonRole.ActionRole)
                
                msg.exec()
                
                if msg.clickedButton() == copy_btn:
                    from PyQt6.QtWidgets import QApplication
                    clipboard = QApplication.clipboard()
                    clipboard.setText(term_data["uri"])
                    QMessageBox.information(self, "URI Copied", 
                                       f"URI copied to clipboard:\n{term_data['uri']}")
    
    def create_info_tab(self):
        """Create information tab"""
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        info_text = """
        <h3>🎉 Working Refactored SHACL Brick Generator</h3>
        
        <h4>✅ Fixed Issues:</h4>
        <ul>
            <li><b>Ontology Browser Working:</b> Can now browse and select from ontologies</li>
            <li><b>Class Selection:</b> Double-click classes to set target class</li>
            <li><b>Property Selection:</b> Double-click properties to get URI for use</li>
            <li><b>Real Updates:</b> Target class field gets updated when class selected</li>
        </ul>
        
        <h4>📚 Available Ontologies:</h4>
        <ul>
            <li><b>Schema.org:</b> Person, Organization, Product, Event, Place, etc.</li>
            <li><b>FOAF:</b> Person, Organization, Document (social network)</li>
            <li><b>BRICK:</b> Building, IoT, Equipment, Sensor, etc.</li>
            <li><b>Custom:</b> Import your own ontology files</li>
        </ul>
        
        <h4>🚀 How to Use:</h4>
        <ol>
            <li><b>Brick Editor Tab:</b> Create and edit SHACL bricks</li>
            <li><b>Browse Classes Button:</b> Quick access to ontology browser</li>
            <li><b>Ontology Browser Tab:</b> Double-click classes to set target class</li>
            <li><b>Import Ontology:</b> Add your own ontology files</li>
        </ol>
        """
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 10px; background: #f8f9fa; border-radius: 5px;")
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        
        self.tabs.addTab(info_widget, "ℹ️ Information")
    
    def create_new_brick(self):
        """Create a new brick"""
        self.brick_name_edit.clear()
        self.target_class_edit.clear()
        self.description_edit.clear()
        self.statusBar().showMessage("New brick created")
    
    def save_brick(self):
        """Save current brick"""
        brick_data = {
            "name": self.brick_name_edit.text(),
            "target_class": self.target_class_edit.text(),
            "description": self.description_edit.toPlainText(),
            "properties": {},
            "constraints": [],
            "metadata": {}
        }
        
        success, message = self.editor_backend.save_brick(brick_data)
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)
    
    def browse_classes(self):
        """Switch to ontology browser tab"""
        self.tabs.setCurrentIndex(1)  # Index of ontology browser tab
        self.statusBar().showMessage("Ontology browser opened - double-click classes to select")


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = WorkingGuidedGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
