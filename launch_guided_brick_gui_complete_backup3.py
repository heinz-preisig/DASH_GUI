#!/usr/bin/env python3
"""
Complete Refactored SHACL Brick Generator
All features restored with improved UX
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QTabWidget, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QListWidget, QListWidgetItem,
    QDialog, QDialogButtonBox, QFileDialog, QSplitter, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt

from shacl_brick_app.core.brick_backend import BrickBackendAPI
from shacl_brick_app.core.editor_backend import BrickEditorBackend

class CompleteGuidedGUI(QMainWindow):
    """Complete brick editor with all features and improved UX"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧱 SHACL Brick Generator - Complete")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize backend as central information source
        self.brick_api = BrickBackendAPI()
        self.editor_backend = BrickEditorBackend(self.brick_api)
        
        # Set backend reference to frontend for dialog control
        self.editor_backend.set_frontend_window(self)
        
        # Register frontend event handlers with backend (automata)
        self._register_backend_event_handlers()
        
        # Frontend will always get brick data from backend
        
        self.init_ui()
    
    def _register_backend_event_handlers(self):
        """Register frontend event handlers with backend (automata)"""
        # Register brick event handlers
        self.editor_backend.register_event_handler('brick_created', self._on_brick_created)
        self.editor_backend.register_event_handler('brick_updated', self._on_brick_updated)
        self.editor_backend.register_event_handler('brick_loaded', self._on_brick_loaded)
        self.editor_backend.register_event_handler('brick_saved', self._on_brick_saved)
        
        # Register property event handlers
        self.editor_backend.register_event_handler('property_added', self._on_property_added)
        self.editor_backend.register_event_handler('property_removed', self._on_property_removed)
        
        # Register constraint event handlers
        self.editor_backend.register_event_handler('constraint_added', self._on_constraint_added)
        self.editor_backend.register_event_handler('constraint_removed', self._on_constraint_removed)
        
        # Register target class event handler
        self.editor_backend.register_event_handler('target_class_set', self._on_target_class_set)
        
        # Register error event handler
        self.editor_backend.register_event_handler('error_occurred', self._on_error_occurred)
        
        # Register dialog event handler
        self.editor_backend.register_event_handler('dialog_requested', self._on_dialog_requested)
    
    # Backend event handlers (minimal frontend methods)
    def _on_brick_created(self, brick_data):
        """Handle brick creation event - update UI with backend data"""
        self._update_ui_from_brick_data()
    
    def _on_brick_updated(self, brick_data):
        """Handle brick update event - sync UI with backend data"""
        self._update_ui_from_brick_data()
    
    def _on_brick_loaded(self, brick_data):
        """Handle brick load event - sync UI with backend data"""
        self._update_ui_from_brick_data()
    
    def _on_brick_saved(self, brick_data):
        """Handle brick save event - show status"""
        self.statusBar().showMessage("Brick saved successfully")
    
    def _on_property_added(self, prop_name, property_data):
        """Handle property addition event - update UI"""
        self._update_properties_display()
        self.statusBar().showMessage(f"Property '{prop_name}' added")
    
    def _on_property_removed(self, prop_name):
        """Handle property removal event - update UI"""
        self._update_properties_display()
        self.statusBar().showMessage(f"Property '{prop_name}' removed")
    
    def _on_constraint_added(self, prop_name, constraint_data):
        """Handle constraint addition event - update UI"""

        self.statusBar().showMessage("Constraint added")
    
    def _on_constraint_removed(self, prop_name):
        """Handle constraint removal event - update UI"""

        self.statusBar().showMessage("Constraint removed")
    
    def _on_target_class_set(self, class_uri):
        """Handle target class set event - update UI"""
        self.target_class_edit.setText(class_uri)
        self.statusBar().showMessage(f"Target class set: {class_uri}")
    
    def _on_error_occurred(self, error_message):
        """Handle error event - show error dialog"""
        QMessageBox.critical(self, "Error", error_message)
    
    def _on_dialog_requested(self, dialog_type):
        """Handle dialog request event - log for debugging"""
        print(f"Backend requested dialog: {dialog_type}")
        self.statusBar().showMessage(f"Opening {dialog_type} dialog...")
    
    # UI synchronization methods - get data from backend
    def _update_ui_from_brick_data(self):
        """Update UI from current brick data from backend"""
        brick_data = self.editor_backend.get_current_brick()
        
        # Update basic fields
        self.brick_name_edit.setText(brick_data.get('name', ''))
        self.target_class_edit.setText(brick_data.get('target_class', ''))
        self.description_edit.setText(brick_data.get('description', ''))
        
        # Update object type
        object_type = brick_data.get('object_type', 'NodeShape')
        index = self.object_type_combo.findText(object_type)
        if index >= 0:
            self.object_type_combo.setCurrentIndex(index)
        
        # Update displays
        self._update_properties_display()

    
    def _update_properties_display(self):
        """Update properties display from backend data"""
        self.properties_list.clear()
        brick_data = self.editor_backend.get_current_brick()
        properties = brick_data.get('properties', {})
        
        for prop_name in properties.keys():
            self.properties_list.addItem(prop_name)
    

    
    # Frontend event trigger methods - minimal, only trigger backend events
    def _request_add_property(self):
        """Request add property - trigger backend dialog"""
        self.editor_backend.request_property_dialog()
    
    def _request_class_browser(self):
        """Request class browser - trigger backend dialog"""
        self.editor_backend.request_class_browser()
    
    def _show_add_property_dialog(self):
        """Show add property dialog and handle result via backend"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Property")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QFormLayout(dialog)
        
        # Property name
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("e.g., firstName, age, email, address")
        layout.addRow("Property Name:", name_edit)
        
        # Property path with help
        path_layout = QHBoxLayout()
        path_edit = QLineEdit()
        path_edit.setPlaceholderText("e.g., schema:firstName, ex:age, foaf:email")
        path_layout.addWidget(path_edit)
        
        browse_btn = QPushButton("📚 Browse")
        browse_btn.setToolTip("Browse ontologies to select property URI")
        browse_btn.setMaximumWidth(80)
        path_layout.addWidget(browse_btn)
        
        layout.addRow("Property Path (URI):", path_layout)
        
        # Data type with help
        datatype_combo = QComboBox()
        datatype_combo.addItems([
            ("xsd:string - Text values"),
            ("xsd:integer - Whole numbers"),
            ("xsd:decimal - Decimal numbers"),
            ("xsd:boolean - True/False values"),
            ("xsd:date - Date values"),
            ("xsd:anyURI - Resource references")
        ])
        layout.addRow("Data Type:", datatype_combo)
        
        # Help text
        help_text = QLabel(
            "📖 <b>Property Path (URI)</b>: The full URI of the property (e.g., schema:firstName)<br>"
            "<b>Property Name</b>: A simple name for display (e.g., firstName)<br>"
            "<b>Data Type</b>: Expected value type for validation"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #666; font-size: 11px; padding: 8px; background: #f5f5f5; border-radius: 4px; margin: 8px 0;")
        layout.addRow(help_text)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)
        
        # Handle dialog result
        def on_accept():
            # Extract just the datatype part (before " - ")
            datatype_full = datatype_combo.currentText()
            datatype = datatype_full.split(" - ")[0] if " - " in datatype_full else datatype_full
            
            property_data = {
                "name": name_edit.text(),
                "path": path_edit.text(),
                "datatype": datatype,
                "constraints": []
            }
            self.editor_backend.add_property_to_current_brick(property_data)
            dialog.accept()
        
        def browse_properties():
            """Open ontology browser to select property"""
            selected_item = self._show_unified_ontology_browser(
                title="Select Property from Ontology",
                context="property",
                instruction="Double-click a property to use its URI as the property path."
            )
            
            if selected_item and selected_item.get("type") == "property":
                path_edit.setText(selected_item["uri"])
                # Extract local name from URI for convenience
                if "#" in selected_item["uri"]:
                    local_name = selected_item["uri"].split("#")[-1]
                elif "/" in selected_item["uri"]:
                    local_name = selected_item["uri"].split("/")[-1]
                else:
                    local_name = selected_item["name"]
                name_edit.setText(local_name)
        
        browse_btn.clicked.connect(browse_properties)
        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)
        
        dialog.exec()
        
    def _show_load_brick_dialog(self):
        """Show load brick dialog - backend controlled"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Load Brick")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Brick list
        bricks_list = QListWidget()
        layout.addWidget(bricks_list)
        
        # Load available bricks
        result = self.brick_api.get_all_bricks()
        if result["status"] == "success":
            for brick in result["data"]["bricks"]:
                item = QListWidgetItem(f"{brick['name']} ({brick['object_type']})")
                item.setData(Qt.ItemDataRole.UserRole, brick)
                bricks_list.addItem(item)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)
        
        # Handle dialog result
        def on_accept():
            current_item = bricks_list.currentItem()
            if current_item:
                brick_data = current_item.data(Qt.ItemDataRole.UserRole)
                loaded_brick = self.editor_backend.load_brick(brick_data["brick_id"])
                if loaded_brick:
                    self._update_ui_from_brick_data()
                    self.statusBar().showMessage(f"Loaded brick: {brick_data['name']}")
            dialog.accept()
        
        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)
        
        dialog.exec()
        
    def _show_class_browser_dialog(self):
        """Show class browser dialog using unified popup interface"""
        selected_item = self._show_unified_ontology_browser(
            title="Select Target Class from Ontology",
            context="class",
            instruction="Choose from available ontologies by clicking on them.<br>Double-click a class to use it as the target class."
        )
        
        if selected_item and selected_item.get("type") == "class":
            # Trigger backend event
            self.editor_backend.set_target_class(selected_item["uri"])
    
    def _sync_ui_to_backend(self):
        """Sync UI values to backend"""
        # Update backend's current brick directly
        self.editor_backend.current_brick["name"] = self.brick_name_edit.text()
        self.editor_backend.current_brick["target_class"] = self.target_class_edit.text()
        self.editor_backend.current_brick["description"] = self.description_edit.toPlainText()
        self.editor_backend.current_brick["object_type"] = self.object_type_combo.currentText()
        
        # Trigger backend update event
        self.editor_backend.emit_event('brick_updated', self.editor_backend.current_brick)
    
    def create_new_brick(self):
        """Create new brick - trigger backend event"""
        self.editor_backend.create_new_brick()
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("🧱 SHACL Brick Generator - Complete")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px;")
        layout.addWidget(header)
        
        # Main content with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Editor
        left_widget = self.create_editor_panel()
        splitter.addWidget(left_widget)
        
        # Right: Browser & Properties
        right_widget = self.create_browser_panel()
        splitter.addWidget(right_widget)
        
        layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("✅ Ready - Complete brick editor with ontology browser")
    
    def create_editor_panel(self):
        """Create the editor panel"""
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        # Brick information group
        info_group = QGroupBox("📋 Brick Information")
        info_layout = QFormLayout(info_group)
        
        # Brick name
        name_layout = QHBoxLayout()
        self.brick_name_edit = QLineEdit()
        self.brick_name_edit.setPlaceholderText("e.g., Student Registration, Product Catalog")
        name_layout.addWidget(QLabel("Name:"))
        name_layout.addWidget(self.brick_name_edit)
        help_btn = QPushButton("?")
        help_btn.setToolTip("Enter a descriptive name for your brick")
        help_btn.setMaximumWidth(25)
        help_btn.clicked.connect(lambda: QMessageBox.information(self, "Brick Name", 
            "Enter a descriptive name for your brick:\n\nExamples:\n• Student Registration\n• Product Catalog\n• Address Validator\n• Equipment Monitor"))
        name_layout.addWidget(help_btn)
        info_layout.addRow(name_layout)
        
        # Target class
        target_layout = QHBoxLayout()
        self.target_class_edit = QLineEdit()
        self.target_class_edit.setPlaceholderText("e.g., schema:Student, schema:Product, brick:Equipment")
        target_layout.addWidget(QLabel("Target Class:"))
        target_layout.addWidget(self.target_class_edit)
        browse_btn = QPushButton("📚 Browse")
        browse_btn.setToolTip("Browse ontologies to select a class")
        browse_btn.clicked.connect(self._request_class_browser)
        target_layout.addWidget(browse_btn)
        info_layout.addRow(target_layout)
        
        # Object type
        self.object_type_combo = QComboBox()
        self.object_type_combo.addItems(["NodeShape", "PropertyShape"])
        info_layout.addRow("Object Type:", self.object_type_combo)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Describe what this brick validates and defines...")
        self.description_edit.setMaximumHeight(100)
        info_layout.addRow("Description:", self.description_edit)
        
        editor_layout.addWidget(info_group)
        
        # Properties group
        props_group = QGroupBox("🏷️ Properties")
        props_layout = QVBoxLayout(props_group)
        
        # Properties list with add/remove
        self.properties_list = QListWidget()
        self.properties_list.setMaximumHeight(200)
        props_layout.addWidget(self.properties_list)
        
        # Property buttons
        prop_buttons_layout = QHBoxLayout()
        
        add_prop_btn = QPushButton("➕ Add Property")
        add_prop_btn.clicked.connect(self._request_add_property)
        prop_buttons_layout.addWidget(add_prop_btn)
        
        remove_prop_btn = QPushButton("➖ Remove Selected")
        remove_prop_btn.clicked.connect(self.remove_property)
        prop_buttons_layout.addWidget(remove_prop_btn)
        
        props_layout.addLayout(prop_buttons_layout)
        
        # Property editor (shown when property selected)
        self.prop_editor_widget = QWidget()
        self.prop_editor_layout = QFormLayout(self.prop_editor_widget)
        self.prop_editor_widget.setVisible(False)
        props_layout.addWidget(self.prop_editor_widget)
        
        editor_layout.addWidget(props_group)
        
        # Constraints are now handled in the property editor area only
        
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
        
        # Connect property selection
        self.properties_list.itemClicked.connect(self.on_property_selected)
        
        return editor_widget
    
    def create_browser_panel(self):
        """Create the browser panel"""
        browser_widget = QWidget()
        browser_layout = QVBoxLayout(browser_widget)
        
        # Header
        header = QLabel("📚 Ontology Browser & Brick Library")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background: #e8f5e8; border-radius: 5px;")
        browser_layout.addWidget(header)
        
        # Tab widget for browser and library
        self.browser_tabs = QTabWidget()
        browser_layout.addWidget(self.browser_tabs)
        
        # Create tabs
        self.create_brick_library_tab()
        
        return browser_widget
    
    def create_brick_library_tab(self):
        """Create brick library tab"""
        library_tab = QWidget()
        library_layout = QVBoxLayout(library_tab)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("📚 Brick Library:"))
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_brick_library)
        header_layout.addWidget(refresh_btn)
        header_layout.addStretch()
        library_layout.addLayout(header_layout)
        
        # Two-level structure: Libraries and Bricks
        content_layout = QHBoxLayout()
        
        # Libraries list (left)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("Libraries:"))
        self.library_list = QListWidget()
        self.library_list.setMaximumWidth(200)
        self.library_list.itemClicked.connect(self.on_library_selected)
        left_layout.addWidget(self.library_list)
        
        # Bricks list (right)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel("Bricks in Library:"))
        self.brick_library_list = QListWidget()
        self.brick_library_list.itemClicked.connect(self.on_brick_library_selected)
        self.brick_library_list.itemDoubleClicked.connect(self.edit_brick_from_library)
        right_layout.addWidget(self.brick_library_list)
        
        content_layout.addWidget(left_widget)
        content_layout.addWidget(right_widget)
        library_layout.addLayout(content_layout)
        
        self.browser_tabs.addTab(library_tab, "📚 Brick Library")
        
        # Load initial bricks
        self.refresh_brick_library()
    
    def add_property(self):
        """Add a new property"""
        # Enhanced dialog with ontology browser integration
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Property")
        dialog.setModal(True)
        dialog.resize(600, 500)
        
    def remove_property(self):
        """Remove selected property - trigger backend event"""
        current_item = self.properties_list.currentItem()
        if current_item:
            prop_name = current_item.text()
            # Trigger backend event
            self.editor_backend.remove_property_from_current_brick(prop_name)
    
    def remove_constraint(self):
        """Remove selected constraint"""
        current_item = self.constraints_list.currentItem()
        if current_item:
            # This is simplified - in a real implementation, we'd need to track which constraint belongs to which property
            self.constraints_list.takeItem(self.constraints_list.row(current_item))
            self.statusBar().showMessage("✅ Constraint removed")
    
    def browse_classes(self):
        """Browse ontologies for target class selection using unified browser"""
        # Create a simple dialog with ontology browser for class selection
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Target Class from Ontology")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        def on_ontology_selected(item):
            ontology_name = item.data(Qt.ItemDataRole.UserRole)
            if ontology_name and ontology_name in ontologies:
                terms_list.clear()
                ontology_data = ontologies[ontology_name]
                
                # Show classes only
                if 'classes' in ontology_data:
                    for class_info in ontology_data['classes']:
                        item = QListWidgetItem(f"Class: {class_info['name']}")
                        item.setData(Qt.ItemDataRole.UserRole, {'type': 'class', **class_info})
                        terms_list.addItem(item)
        
        # Handle class selection
        def on_class_selected(item):
            term_data = item.data(Qt.ItemDataRole.UserRole)
            if term_data and term_data.get("type") == "class":
                self.target_class_edit.setText(term_data["uri"])
                dialog.accept()
        
        ontology_list.itemClicked.connect(on_ontology_selected)
        terms_list.itemDoubleClicked.connect(on_class_selected)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(button_box)
        button_box.rejected.connect(dialog.reject)
        
        dialog.exec()
    
    def display_ontology_terms(self, ontology_data):
        """Display terms from selected ontology"""
        self.terms_list.clear()
        
        # Debug: Print what we're working with
        print(f"DEBUG: Displaying ontology terms for: {ontology_data}")
        print(f"DEBUG: Classes: {len(ontology_data.get('classes', []))}")
        print(f"DEBUG: Properties: {len(ontology_data.get('properties', []))}")
        
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
    
    def populate_ontology_list(self):
        """Populate the ontology list with available ontologies"""
        ontologies = self.editor_backend.ontology_manager.ontologies
        
        # Clear existing items to prevent duplicates
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
            self.display_ontology_terms(ontologies[ontology_name])
    
    def on_term_selected(self, item):
        """Handle term double-click"""
        term_data = item.data(Qt.ItemDataRole.UserRole)
        if term_data:
            if term_data.get("type") == "class":
                self.target_class_edit.setText(term_data["uri"])
                self.statusBar().showMessage(f"✅ Class '{term_data['name']}' selected as target class")
            elif term_data.get("type") == "property":
                from PyQt6.QtWidgets import QApplication
                clipboard = QApplication.clipboard()
                clipboard.setText(term_data["uri"])
                self.statusBar().showMessage(f"✅ Property URI '{term_data['uri']}' copied to clipboard")
    
    def on_property_selected(self, item):
        """Handle property selection"""
        prop_name = item.text()
        current_brick = self.editor_backend.get_current_brick()
        if prop_name in current_brick.get("properties", {}):
            prop_data = current_brick["properties"][prop_name]
            self.show_property_editor(prop_data, prop_name)
    
    def show_property_editor(self, property_data, prop_name):
        """Show property editor for selected property"""
        # Clear and setup property editor form
        for i in reversed(range(self.prop_editor_layout.count())):
            self.prop_editor_layout.itemAt(i).widget().deleteLater()
        
        self.prop_name_edit = QLineEdit()
        self.prop_name_edit.setText(prop_name)
        self.prop_editor_layout.addRow("Property Name:", self.prop_name_edit)
        
        self.prop_path_edit = QLineEdit()
        if isinstance(property_data, dict):
            self.prop_path_edit.setText(property_data.get("path", ""))
        else:
            # Simple property value - use property name as path
            self.prop_path_edit.setText(prop_name)
        self.prop_editor_layout.addRow("Property Path:", self.prop_path_edit)
        
        self.prop_datatype_combo = QComboBox()
        self.prop_datatype_combo.addItems(["xsd:string", "xsd:integer", "xsd:decimal", "xsd:boolean", "xsd:date", "xsd:anyURI"])
        if isinstance(property_data, dict):
            self.prop_datatype_combo.setCurrentText(property_data.get("datatype", "xsd:string"))
            constraints = property_data.get("constraints", [])
        else:
            # Simple property value - use default datatype
            self.prop_datatype_combo.setCurrentText("xsd:string")
            constraints = []
        self.prop_editor_layout.addRow("Data Type:", self.prop_datatype_combo)
        
        # Constraints for this property
        self.prop_constraints_list = QListWidget()
        for constraint in constraints:
            constraint_text = f"{constraint['constraint_type']}: {constraint['value']}"
            self.prop_constraints_list.addItem(constraint_text)
        
        constraint_buttons_layout = QHBoxLayout()
        add_constraint_btn = QPushButton("➕ Add")
        add_constraint_btn.clicked.connect(lambda: self.add_constraint_to_property(prop_name))
        constraint_buttons_layout.addWidget(add_constraint_btn)
        
        remove_constraint_btn = QPushButton("➖ Remove")
        remove_constraint_btn.clicked.connect(lambda: self.remove_constraint_from_property(prop_name))
        constraint_buttons_layout.addWidget(remove_constraint_btn)
        
        self.prop_editor_layout.addRow("Constraints:", self.prop_constraints_list)
        
        # Create a widget for the constraint buttons
        constraint_buttons_widget = QWidget()
        constraint_buttons_widget.setLayout(constraint_buttons_layout)
        self.prop_editor_layout.addRow("", constraint_buttons_widget)
        
        self.prop_editor_widget.setVisible(True)
    
    def add_constraint_to_property(self, prop_name):
        """Add constraint to specific property - trigger backend dialog"""
        # Use backend-controlled dialog like ontology browser
        self.editor_backend.request_constraint_dialog(prop_name)
    def remove_constraint_from_property(self, prop_name):
        """Remove constraint from specific property"""
        current_item = self.prop_constraints_list.currentItem()
        if current_item:
            constraint_text = current_item.text()
            # Parse constraint text to find the constraint
            if ": " in constraint_text:
                constraint_type, value = constraint_text.split(":", 1)
                constraints = self.editor_backend.current_brick["properties"][prop_name]["constraints"]
                for i, constraint in enumerate(constraints):
                    if f"{constraint['constraint_type']}: {constraint['value']}" == constraint_text:
                        constraints.pop(i)
                        break
                
                self.statusBar().showMessage(f"✅ Constraint removed from '{prop_name}'")
    
    def update_properties_display(self):
        """Update the properties list display"""
        self.properties_list.clear()
        for prop_name, prop_data in self.editor_backend.get_current_brick().get("properties", {}).items():
            if isinstance(prop_data, dict):
                # Property is a dictionary with constraints
                constraints = prop_data.get("constraints", [])
                constraints_text = ", ".join([f"{c['constraint_type']}: {c['value']}" for c in constraints])
                display_text = f"{prop_name} ({constraints_text})"
            else:
                # Property is a simple value (like "nodeKind": "IRI")
                display_text = f"{prop_name}: {prop_data}"
            self.properties_list.addItem(display_text)
    
    def update_constraints_display(self):
        """Update constraints display for current property"""
        current_item = self.properties_list.currentItem()
        if current_item:
            prop_name = current_item.text().split(" (")[0]  # Extract property name
            if prop_name in self.editor_backend.get_current_brick().get("properties", {}):
                prop_data = self.editor_backend.get_current_brick()["properties"][prop_name]
                if isinstance(prop_data, dict):
                    constraints = prop_data.get("constraints", [])
                    self.prop_constraints_list.clear()
                    for constraint in constraints:
                        constraint_text = f"{constraint['constraint_type']}: {constraint['value']}"
                        self.prop_constraints_list.addItem(constraint_text)
                else:
                    # Simple property value - no constraints
                    self.prop_constraints_list.clear()
                    self.prop_constraints_list.addItem("No constraints for this property")
    
    def save_brick(self):
        """Save current brick - trigger backend event"""
        # Use backend-controlled save operation
        self.editor_backend.request_save_brick()
    
    def load_brick(self):
        """Load existing brick - use backend-controlled dialog"""
        self.editor_backend.request_load_brick_dialog()
        
    def edit_brick_from_library(self):
        """Edit brick from library"""
        current_item = self.brick_library_list.currentItem()
        if current_item:
            brick_data = current_item.data(Qt.ItemDataRole.UserRole)
            self.editor_backend.set_current_brick(brick_data)
            self.display_current_brick()
            self.statusBar().showMessage(f"✅ Brick '{brick_data['name']}' loaded for editing")
    
    def display_current_brick(self):
        """Display current brick data in editor"""
        current_brick = self.editor_backend.get_current_brick()
        if current_brick:
            self.brick_name_edit.setText(self.editor_backend.get_current_brick().get("name", ""))
            self.target_class_edit.setText(self.editor_backend.get_current_brick().get("target_class", ""))
            self.description_edit.setPlainText(self.editor_backend.get_current_brick().get("description", ""))
            self.update_properties_display()
            
            # Switch to editor tab
            for i in range(self.browser_tabs.count()):
                if self.browser_tabs.tabText(i) == "📚 Brick Library":
                    self.browser_tabs.setCurrentIndex(i)
                    break
    
    def on_brick_library_selected(self, item):
        """Handle brick selection from library - load into backend editor"""
        brick_data = item.data(Qt.ItemDataRole.UserRole)
        if brick_data:
            # Load brick into backend
            self.editor_backend.set_current_brick(brick_data)
            
            # Update UI to show brick data
            self._update_ui_from_brick_data()
            
            # Switch to editor tab for editing
            for i in range(self.browser_tabs.count()):
                if self.browser_tabs.tabText(i) == "Brick Editor":
                    self.browser_tabs.setCurrentIndex(i)
                    break
            
            self.statusBar().showMessage(f"Brick '{brick_data["name"]}' loaded for editing")
    def refresh_brick_library(self):
        """Refresh the brick library with two-level structure"""
        # Refresh libraries list
        result = self.editor_backend.brick_api.get_brick_libraries()
        if result["status"] == "success":
            self.library_list.clear()
            libraries = result["data"]["libraries"]
            for library in libraries:
                item = QListWidgetItem(f" {library["name"]}")
                item.setData(Qt.ItemDataRole.UserRole, library)
                self.library_list.addItem(item)
            
            # Auto-select first library
            if libraries:
                self.library_list.setCurrentRow(0)
                self.on_library_selected(self.library_list.item(0))
        
        self.statusBar().showMessage(f"Brick library refreshed ({len(libraries)} libraries)")
    def export_shacl(self):
        """Export current brick to SHACL format"""
        current_brick = self.editor_backend.get_current_brick()
        if not current_brick:
            QMessageBox.warning(self, "No Brick", "Please create or load a brick first")
            return
        
        # Get SHACL content from backend
        result = self.editor_backend.brick_api.export_brick_shacl(self.editor_backend.get_current_brick()["brick_id"])
        if result["status"] == "success":
            # Save to file
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save SHACL File", "", "SHACL Files (*.ttl);;All Files (*)"
            )
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(result["data"]["shaql_content"])
                self.statusBar().showMessage(f"SHACL exported to {file_path}")
        else:
            QMessageBox.critical(self, "Export Error", result["message"])

    def on_library_selected(self, item):
        """Handle library selection - show bricks in that library"""
        library_data = item.data(Qt.ItemDataRole.UserRole)
        if not library_data:
            return
        
        library_name = library_data["name"]
        result = self.editor_backend.brick_api.get_library_bricks(library_name)
        
        if result["status"] == "success":
            self.brick_library_list.clear()
            bricks = result["data"]["bricks"]
            for brick in bricks:
                item = QListWidgetItem(f" {brick["name"]}")
                item.setData(Qt.ItemDataRole.UserRole, brick)
                self.brick_library_list.addItem(item)
            
            self.statusBar().showMessage(f"Library '{library_name}' loaded ({len(bricks)} bricks)")
        else:
            self.brick_library_list.clear()
            self.statusBar().showMessage(f"Error loading library: {result["message"]}")
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
                self.statusBar().showMessage(f"✅ Ontology '{ontology_name}' imported successfully")
            else:
                QMessageBox.critical(self, "Import Error", message)
    
    def browse_ontology_for_property(self, name_edit, path_edit):
        """Open ontology browser to select a property"""
        # Create a simple dialog with ontology browser
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Property from Ontology")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        def on_ontology_selected(item):
            ontology_name = item.data(Qt.ItemDataRole.UserRole)
            if ontology_name and ontology_name in ontologies:
                terms_list.clear()
                ontology_data = ontologies[ontology_name]
                
                # Show properties only
                if 'properties' in ontology_data:
                    for prop_info in ontology_data['properties']:
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


def _show_constraint_dialog(self, prop_name):
        """"Show constraint dialog for a property - backend controlled popup"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Add Constraint to '{prop_name}'")
        dialog.setModal(True)
        dialog.resize(450, 350)
        
        layout = QFormLayout(dialog)
        
        # Get current property data to show compatible constraints
        current_brick = self.editor_backend.get_current_brick()
        prop_data = current_brick.get("properties", {}).get(prop_name, {})
        current_datatype = prop_data.get("datatype", "xsd:string")
        
        # Constraint type with help
        constraint_type_combo = QComboBox()
        
        # Show appropriate constraint types based on datatype
        if current_datatype in ["xsd:string", "xsd:anyURI"]:
            constraint_types = [
                "minLength - Minimum length",
                "maxLength - Maximum length", 
                "pattern - Regular expression pattern"
            ]
        elif current_datatype in ["xsd:integer", "xsd:decimal"]:
            constraint_types = [
                "minInclusive - Minimum value",
                "maxInclusive - Maximum value",
                "minExclusive - Minimum exclusive",
                "maxExclusive - Maximum exclusive"
            ]
        elif current_datatype == "xsd:date"]:
            constraint_types = [
                "minInclusive - Earliest date",
                "maxInclusive - Latest date"
            ]
        else:
            constraint_types = [
                "minCount - Minimum occurrences",
                "maxCount - Maximum occurrences"
            ]
        
        constraint_type_combo.addItems(constraint_types)
        layout.addRow("Constraint Type:", constraint_type_combo)
        
        # Constraint value
        value_edit = QLineEdit()
        value_edit.setPlaceholderText("Enter constraint value...")
        layout.addRow("Constraint Value:", value_edit)
        
        # Help text
        help_text = QLabel(
            f"📖 <b>Constraint Types:</b><br>"
            f"• <b>minLength/maxLength</b>: For text properties<br>"
            f"• <b>pattern</b>: Regular expression pattern (e.g., ^[a-zA-Z0-9]+$)<br>"
            f"• <b>minInclusive/maxInclusive</b>: For numeric properties<br>"
            f"• <b>minCount/maxCount</b>: For array properties<br><br>"
            f"<b>Current Property:</b> {prop_name} ({current_datatype})"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #666; font-size: 10px; padding: 8px; background: #f9f9f9; border-radius: 4px; margin: 8px 0;")
        layout.addRow(help_text)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)
        
        # Handle dialog result
        def on_accept():
            constraint_type_full = constraint_type_combo.currentText()
            # Extract just the constraint type part (before " - ")
            constraint_type = constraint_type_full.split(" - ")[0] if " - " in constraint_type_full else constraint_type_full
            constraint_value = value_edit.text()
            
            if constraint_value.strip():
                constraint_data = {
                    "constraint_type": constraint_type,
                    "value": constraint_value
                }
                self.editor_backend.add_constraint_to_property(prop_name, constraint_data)
                dialog.accept()
            else:
                QMessageBox.warning(self, "Invalid Input", "Please enter a constraint value.")
        
        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)
        
        dialog.exec()
    def update_brick_display(self):
        """Update the display with current brick data"""
        current_brick = self.editor_backend.get_current_brick()
        if not current_brick:
            return
        
        # Update basic fields
        self.brick_name_edit.setText(self.current_brick.get('name', ''))
        self.target_class_edit.setText(self.current_brick.get('target_class', ''))
        self.description_edit.setText(self.current_brick.get('description', ''))
        
        # Update object type
        object_type = self.current_brick.get('object_type', 'NodeShape')
        index = self.object_type_combo.findText(object_type)
        if index >= 0:
            self.object_type_combo.setCurrentIndex(index)
        
        # Update properties and constraints displays
        self.update_properties_display()
        

    def update_constraints_display(self):
        """Update the constraints display"""
        self.constraints_list.clear()
        current_brick = self.editor_backend.get_current_brick()
        if not current_brick:
            return
        
        # Show constraints for all properties
        properties = self.editor_backend.get_current_brick().get('properties', {})
        for prop_name, prop_data in properties.items():
            if isinstance(prop_data, dict):
                constraints = prop_data.get('constraints', [])
                for constraint in constraints:
                    item = QListWidgetItem(f"{prop_name}: {constraint.get('type', 'Unknown')}")
                    self.constraints_list.addItem(item)
            else:
                # Simple property value - no constraints to display
                pass



    def add_constraint(self):
        """Add constraint - trigger backend event"""
        # Simplified constraint addition
        constraint_data = {
            "type": "minCount",
            "value": 1
        }
        # Get selected property
        current_item = self.properties_list.currentItem()
        if current_item:
            prop_name = current_item.text()
            self.editor_backend.add_constraint_to_property(prop_name, constraint_data)
    
    def _browse_ontology_for_property(self, name_edit, path_edit):
        """Open unified ontology browser for property selection"""
        selected_item = self._show_unified_ontology_browser(
            title="Select Property from Ontology",
            context="property",
            instruction="Double-click a property to select it"
        )
        
        if selected_item and selected_item.get("type") == "property":
            name_edit.setText(selected_item["name"])
            path_edit.setText(selected_item["uri"])
    
    def _show_constraint_dialog(self, prop_name):
        """Show constraint dialog for a property - backend-controlled popup"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Constraint")
        dialog.setModal(True)
        dialog.resize(450, 300)
        
        layout = QFormLayout(dialog)
        
        # Use backend methods to get data type and compatible constraints
        data_type = self.editor_backend.get_property_datatype(prop_name)
        compatible_constraints = self.editor_backend.get_property_constraints(prop_name)
        
        # Show detected data type
        data_type_label = QLabel(f"Detected: {data_type}")
        data_type_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addRow("Data Type:", data_type_label)
        
        constraint_type = QComboBox()
        constraint_type.addItems(compatible_constraints)
        layout.addRow("Constraint Type:", constraint_type)
        
        value_edit = QLineEdit()
        layout.addRow("Value:", value_edit)
        
        # Add help text
        help_text = QLabel("Select a constraint type and enter a value. Examples:\n"
                           "MinLengthConstraintComponent: 5\n"
                           "PatternConstraintComponent: ^[a-zA-Z0-9]+$")
        help_text.setStyleSheet("color: #666; font-size: 10px;")
        help_text.setWordWrap(True)
        layout.addRow("Help:", help_text)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(button_box)
        
        # Connect buttons
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        # Show the dialog and handle the result
        if dialog.exec() == QDialog.DialogCode.Accepted:
            constraint_type_name = constraint_type.currentText()
            constraint_value = value_edit.text()
            
            # Validate input
            if not constraint_value.strip():
                QMessageBox.warning(self, "Invalid Input", "Please enter a constraint value.")
                return None
            
            constraint = {
                "constraint_type": constraint_type_name,
                "value": constraint_value,
                "parameters": {}
            }
            
            # Use backend method
            success = self.editor_backend.add_constraint_to_property(prop_name, constraint)
            if success:
                # Update the property constraints display
                self._update_property_constraints_display(prop_name)
                self.statusBar().showMessage(f"Constraint added to '{prop_name}'")
            else:
                self.statusBar().showMessage(f"Failed to add constraint to '{prop_name}'")
        
        return None
    
    def _update_property_constraints_display(self, prop_name):
        """Update property constraints display for a specific property"""
        current_brick = self.editor_backend.get_current_brick()
        if not current_brick:
            return
        
        prop_data = current_brick.get("properties", {}).get(prop_name, {})
        if hasattr(self, 'prop_constraints_list'):
            self.prop_constraints_list.clear()
            if isinstance(prop_data, dict):
                constraints = prop_data.get("constraints", [])
                for constraint in constraints:
                    constraint_text = f"{constraint['constraint_type']}: {constraint['value']}"
                    self.prop_constraints_list.addItem(constraint_text)
            else:
                # Simple property value - no constraints
                self.prop_constraints_list.clear()
                self.prop_constraints_list.addItem("No constraints for this property")
    
    def _show_unified_ontology_browser(self, title="Browse Ontologies", context="all", instruction="Double-click to select"):
        """Unified popup ontology browser for all contexts"""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Instructions
        instructions = QLabel(instruction)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 10px; background: #f0f0f0; border-radius: 5px; margin-bottom: 10px;")
        layout.addWidget(instructions)
        
        # Content layout
        content_layout = QHBoxLayout()
        
        # Ontology list
        ontology_list = QListWidget()
        ontology_list.setMaximumWidth(250)
        ontologies = self.editor_backend.ontology_manager.ontologies
        
        for name, data in ontologies.items():
            class_count = len(data.get('classes', []))
            prop_count = len(data.get('properties', []))
            item = QListWidgetItem(f" {name}\n {class_count} classes, {prop_count} properties")
            item.setData(Qt.ItemDataRole.UserRole, name)
            ontology_list.addItem(item)
        
        content_layout.addWidget(QLabel("Ontologies:"))
        content_layout.addWidget(ontology_list)
        
        # Terms list
        terms_list = QListWidget()
        content_layout.addWidget(QLabel("Terms:"))
        content_layout.addWidget(terms_list)
        
        layout.addLayout(content_layout)
        
        def on_ontology_selected(item):
            ontology_name = item.data(Qt.ItemDataRole.UserRole)
            if ontology_name and ontology_name in ontologies:
                terms_list.clear()
                ontology_data = ontologies[ontology_name]
                
                # Show terms based on context
                if context == "property":
                    if 'properties' in ontology_data:
                        for prop_info in ontology_data['properties']:
                            item = QListWidgetItem(f"Property: {prop_info['name']}")
                            item.setData(Qt.ItemDataRole.UserRole, {'type': 'property', **prop_info})
                            terms_list.addItem(item)
                elif context == "class":
                    if 'classes' in ontology_data:
                        for class_info in ontology_data['classes']:
                            item = QListWidgetItem(f"Class: {class_info['name']}")
                            item.setData(Qt.ItemDataRole.UserRole, {'type': 'class', **class_info})
                            terms_list.addItem(item)
                else:  # "all" context
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
                dialog.selected_item = term_data
                dialog.accept()
        
        ontology_list.itemClicked.connect(on_ontology_selected)
        terms_list.itemDoubleClicked.connect(on_term_selected)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        layout.addWidget(button_box)
        button_box.rejected.connect(dialog.reject)
        
        # Initialize with first ontology
        if ontology_list.count() > 0:
            on_ontology_selected(ontology_list.item(0))
        
        dialog.selected_item = None
        dialog.exec()
        
        return dialog.selected_item



def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = CompleteGuidedGUI()
    window.show()
    
    # Create initial brick
    window.create_new_brick()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
