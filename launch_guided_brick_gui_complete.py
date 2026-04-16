#!/usr/bin/env python3
"""
Complete Refactored SHACL Brick Generator
All features restored with improved UX
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QTabWidget, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QListWidget, QListWidgetItem,
    QDialog, QDialogButtonBox, QFileDialog, QSplitter, QGroupBox, QScrollArea, QInputDialog
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
    
    def _load_config(self):
        """Load configuration from file"""
        import json
        import os
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r') as f:
                    config = json.load(f)
                    self._last_export_dir = config.get('export', {}).get('last_directory')
        except Exception:
            pass
    
    def _save_config(self):
        """Save configuration to file"""
        import json
        try:
            config = {
                'export': {
                    'last_directory': self._last_export_dir
                }
            }
            with open(self._config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass

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
        # Preserve current brick name to prevent it from being overwritten
        current_brick_name = self.brick_name_edit.text()
        self._update_ui_from_brick_data()
        # Restore brick name if it was cleared
        if not self.brick_name_edit.text() and current_brick_name:
            self.brick_name_edit.setText(current_brick_name)

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

    def _request_context_browser(self):
        """Request context-aware ontology browser"""
        current_object_type = self.object_type_combo.currentText()
        
        if current_object_type == "NodeShape":
            # Show class browser for NodeShape
            self._request_class_browser()
        elif current_object_type == "PropertyShape":
            # Show property browser for PropertyShape
            self._request_property_browser()
        else:
            # Default to class browser
            self._request_class_browser()

    def _request_property_browser(self):
        """Request property browser from backend"""
        self.editor_backend.request_property_browser()


    def _on_object_type_changed(self):
        """Handle object type change - update UI context"""
        current_object_type = self.object_type_combo.currentText()
        
        if current_object_type == "NodeShape":
            # Update for NodeShape
            self.browse_btn.setText("📚 Browse Classes")
            self.browse_btn.setToolTip("Browse ontologies to select a target class")
            self.target_class_edit.setPlaceholderText("e.g., schema:Student, schema:Product, brick:Equipment")
            # Update label text
            for i in range(self.target_class_edit.parent().layout().count()):
                widget = self.target_class_edit.parent().layout().itemAt(i).widget()
                if isinstance(widget, QLabel) and "Target" in widget.text():
                    widget.setText("Target Class:")
                    break
        elif current_object_type == "PropertyShape":
            # Update for PropertyShape
            self.browse_btn.setText("📚 Browse Properties")
            self.browse_btn.setToolTip("Browse ontologies to select a property path")
            self.target_class_edit.setPlaceholderText("e.g., schema:name, schema:email, foaf:knows")
            # Update label text
            for i in range(self.target_class_edit.parent().layout().count()):
                widget = self.target_class_edit.parent().layout().itemAt(i).widget()
                if isinstance(widget, QLabel) and "Target" in widget.text():
                    widget.setText("Property Path:")
                    break


    def _show_add_property_dialog(self):
        """Show add property dialog with integrated constraints"""
        # Preserve current brick name
        current_brick_name = self.brick_name_edit.text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Add Property")
        dialog.setModal(True)
        dialog.resize(600, 600)

        # Create main layout with scroll area for longer content
        main_layout = QVBoxLayout(dialog)
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        layout = QFormLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        # Property name
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("e.g., firstName, age, email, address")
        layout.addRow("Property Name:", name_edit)

        # Property path with help
        path_layout = QHBoxLayout()
        path_edit = QLineEdit()
        path_edit.setPlaceholderText("e.g., schema:firstName, ex:age, foaf:email")
        path_layout.addWidget(path_edit)

        self.browse_btn = QPushButton("📚 Browse")
        self.browse_btn.setToolTip("Browse ontologies to select property URI")
        self.browse_btn.setMaximumWidth(80)
        path_layout.addWidget(self.browse_btn)

        layout.addRow("Property Path (URI):", path_layout)

        # Data type
        datatype_combo = QComboBox()
        datatype_combo.addItems([
                "xsd:string - Text values",
                "xsd:integer - Whole numbers",
                "xsd:decimal - Decimal numbers",
                "xsd:boolean - True/False values",
                "xsd:date - Date values",
                "xsd:anyURI - Resource references"
                ])
        layout.addRow("Data Type:", datatype_combo)

        # Constraints section
        constraints_group = QGroupBox("🔒 Constraints (Optional)")
        constraints_layout = QVBoxLayout(constraints_group)

        # Constraints list
        constraints_list = QListWidget()
        constraints_list.setMaximumHeight(120)
        constraints_layout.addWidget(constraints_list)

        # Quick constraint buttons (context-aware)
        quick_constraints_layout = QHBoxLayout()

        # Create constraint buttons
        min_len_btn = QPushButton("Min Length")
        max_len_btn = QPushButton("Max Length")
        pattern_btn = QPushButton("Pattern")
        min_value_btn = QPushButton("Min Value")
        max_value_btn = QPushButton("Max Value")
        required_btn = QPushButton("Required")
        remove_btn = QPushButton("Remove")

        def add_min_length():
            value, ok = QInputDialog.getText(dialog, "Minimum Length", "Enter minimum length:")
            if ok and value.isdigit():
                constraints_list.addItem(f"minLength: {value}")

        def add_max_length():
            value, ok = QInputDialog.getText(dialog, "Maximum Length", "Enter maximum length:")
            if ok and value.isdigit():
                constraints_list.addItem(f"maxLength: {value}")

        def add_pattern():
            value, ok = QInputDialog.getText(dialog, "Pattern", "Enter regex pattern:")
            if ok and value:
                constraints_list.addItem(f"pattern: {value}")

        def add_min_value():
            value, ok = QInputDialog.getText(dialog, "Minimum Value", "Enter minimum value:")
            if ok:
                constraints_list.addItem(f"minInclusive: {value}")

        def add_max_value():
            value, ok = QInputDialog.getText(dialog, "Maximum Value", "Enter maximum value:")
            if ok:
                constraints_list.addItem(f"maxInclusive: {value}")

        def add_required():
            constraints_list.addItem("minCount: 1")

        def remove_constraint():
            current_item = constraints_list.currentItem()
            if current_item:
                constraints_list.takeItem(constraints_list.row(current_item))

        # Connect button signals
        min_len_btn.clicked.connect(add_min_length)
        max_len_btn.clicked.connect(add_max_length)
        pattern_btn.clicked.connect(add_pattern)
        min_value_btn.clicked.connect(add_min_value)
        max_value_btn.clicked.connect(add_max_value)
        required_btn.clicked.connect(add_required)
        remove_btn.clicked.connect(remove_constraint)

        # Add buttons to layout
        quick_constraints_layout.addWidget(min_len_btn)
        quick_constraints_layout.addWidget(max_len_btn)
        quick_constraints_layout.addWidget(pattern_btn)
        quick_constraints_layout.addWidget(min_value_btn)
        quick_constraints_layout.addWidget(max_value_btn)
        quick_constraints_layout.addWidget(required_btn)
        quick_constraints_layout.addWidget(remove_btn)

        # Function to update constraint buttons based on data type
        def update_constraint_buttons():
            datatype = datatype_combo.currentText().split(" - ")[
                0] if " - " in datatype_combo.currentText() else datatype_combo.currentText()

            # Hide all buttons first
            min_len_btn.hide()
            max_len_btn.hide()
            pattern_btn.hide()
            min_value_btn.hide()
            max_value_btn.hide()

            # Show relevant buttons based on data type
            if datatype in ["xsd:string"]:
                min_len_btn.show()
                max_len_btn.show()
                pattern_btn.show()
            elif datatype in ["xsd:integer", "xsd:decimal"]:
                min_value_btn.show()
                max_value_btn.show()
            elif datatype in ["xsd:date"]:
                min_value_btn.show()
                max_value_btn.show()
            elif datatype in ["xsd:boolean"]:
                # Boolean typically doesn't need numeric constraints
                pass
            elif datatype in ["xsd:anyURI"]:
                pattern_btn.show()  # For URI pattern validation

            # Required button is always available
            required_btn.show()
            remove_btn.show()

        # Connect data type change to update buttons
        datatype_combo.currentTextChanged.connect(update_constraint_buttons)

        # Initial update
        update_constraint_buttons()

        constraints_layout.addLayout(quick_constraints_layout)
        layout.addRow(constraints_group)

        # Help text
        help_text = QLabel(
                "📖 <b>Quick Start:</b><br>"
                "1. Enter property name (e.g., firstName)<br>"
                "2. Set property path or browse ontologies (e.g., schema:firstName)<br>"
                "3. Choose data type<br>"
                "4. Add constraints if needed (buttons adapt to data type)<br><br>"
                "<b>Smart Constraints:</b><br>"
                "• Text fields: Min/Max Length, Pattern<br>"
                "• Numbers: Min/Max Value<br>"
                "• Dates: Min/Max Date<br>"
                "• URIs: Pattern validation<br>"
                "• All types: Required field"
                )
        help_text.setWordWrap(True)
        help_text.setStyleSheet(
            "color: #666; font-size: 11px; padding: 8px; background: #f5f5f5; border-radius: 4px; margin: 8px 0;")
        layout.addRow(help_text)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        main_layout.addWidget(buttons)

        # Handle dialog result
        def on_accept():
            # Extract just the datatype part (before " - ")
            datatype_full = datatype_combo.currentText()
            datatype = datatype_full.split(" - ")[0] if " - " in datatype_full else datatype_full

            # Parse constraints from list
            constraints = []
            for i in range(constraints_list.count()):
                constraint_text = constraints_list.item(i).text()
                if ": " in constraint_text:
                    constraint_type, value = constraint_text.split(": ", 1)
                    constraints.append({
                            "constraint_type": constraint_type,
                            "value"          : value
                            })

            property_data = {
                    "name"       : name_edit.text(),
                    "path"       : path_edit.text(),
                    "datatype"   : datatype,
                    "constraints": constraints
                    }
            self.editor_backend.add_property_to_current_brick(property_data)
            # Restore brick name in case it was overwritten during property addition
            self.brick_name_edit.setText(current_brick_name)
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

        self.browse_btn.clicked.connect(browse_properties)
        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)

        dialog.exec()

    def _show_unified_ontology_browser(self, title, context, instruction):
        """Show unified ontology browser dialog for class or property selection"""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setModal(True)
        dialog.resize(600, 500)

        # Create layout
        layout = QVBoxLayout(dialog)

        # Add instruction label
        instruction_label = QLabel(instruction)
        instruction_label.setWordWrap(True)
        instruction_label.setStyleSheet(
            "color: #666; font-size: 11px; padding: 8px; background: #f5f5f5; border-radius: 4px; margin: 8px 0;")
        layout.addWidget(instruction_label)

        # Create horizontal layout for ontology and terms lists
        content_layout = QHBoxLayout()

        # Ontology list (left)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("Available Ontologies:"))
        ontology_list = QListWidget()
        ontology_list.setMaximumWidth(250)
        left_layout.addWidget(ontology_list)
        content_layout.addWidget(left_widget)

        # Terms list (right)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel("Terms:"))
        terms_list = QListWidget()
        right_layout.addWidget(terms_list)
        content_layout.addWidget(right_widget)

        layout.addLayout(content_layout)

        # Get ontologies from backend
        ontologies = self.editor_backend.ontology_manager.ontologies

        # Populate ontology list
        for name, data in ontologies.items():
            class_count = len(data.get('classes', []))
            prop_count = len(data.get('properties', []))
            item = QListWidgetItem(f"{name} ({class_count} classes, {prop_count} properties)")
            item.setData(Qt.ItemDataRole.UserRole, name)
            ontology_list.addItem(item)

        # Store selected item for return
        selected_item = None

        def on_ontology_selected(item):
            ontology_name = item.data(Qt.ItemDataRole.UserRole)
            if ontology_name and ontology_name in ontologies:
                terms_list.clear()
                ontology_data = ontologies[ontology_name]

                if context == "class":
                    # Show classes only
                    if 'classes' in ontology_data:
                        for class_info in ontology_data['classes']:
                            item = QListWidgetItem(f"Class: {class_info['name']}")
                            item.setData(Qt.ItemDataRole.UserRole, {'type': 'class', **class_info})
                            terms_list.addItem(item)
                elif context == "property":
                    # Show properties only
                    if 'properties' in ontology_data:
                        for prop_info in ontology_data['properties']:
                            item = QListWidgetItem(f"Property: {prop_info['name']}")
                            item.setData(Qt.ItemDataRole.UserRole, {'type': 'property', **prop_info})
                            terms_list.addItem(item)
                else:
                    # Show both classes and properties
                    self.display_ontology_terms(ontology_data)

        def on_term_selected(item):
            nonlocal selected_item
            selected_item = item.data(Qt.ItemDataRole.UserRole)
            if selected_item:
                dialog.accept()

        ontology_list.itemClicked.connect(on_ontology_selected)
        terms_list.itemDoubleClicked.connect(on_term_selected)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(button_box)
        button_box.rejected.connect(dialog.reject)

        dialog.exec()
        return selected_item


    def _show_class_browser_dialog(self):
        """Show class browser dialog using unified popup interface"""
        # Preserve current brick name
        current_brick_name = self.brick_name_edit.text()

        selected_item = self._show_unified_ontology_browser(
                title="Select Target Class from Ontology",
                context="class",
                instruction="Choose from available ontologies by clicking on them.<br>Double-click a class to use it as the target class."
                )

        if selected_item and selected_item.get("type") == "class":
            # Trigger backend event
            self.editor_backend.set_target_class(selected_item["uri"])
            # Restore brick name in case it was overwritten
            self.brick_name_edit.setText(current_brick_name)

    def _show_property_browser_dialog(self):
        """Show property browser dialog using unified popup interface"""
        # Preserve current brick name
        current_brick_name = self.brick_name_edit.text()

        selected_item = self._show_unified_ontology_browser(
                title="Select Property Path from Ontology",
                context="property",
                instruction="Choose from available ontologies by clicking on them.<br>Double-click a property to use it as the property path."
                )

        if selected_item and selected_item.get("type") == "property":
            # Trigger backend event - set the property path in the target class field
            self.editor_backend.set_target_class(selected_item["uri"])
            # Restore brick name in case it was overwritten
            self.brick_name_edit.setText(current_brick_name)


    def _sync_ui_to_backend(self):
        """Sync UI values to backend"""
        # Update backend's current brick using SHACLBrick methods
        self.editor_backend.current_brick.update_name(self.brick_name_edit.text())
        self.editor_backend.current_brick.update_target_class(self.target_class_edit.text())
        self.editor_backend.current_brick.update_description(self.description_edit.toPlainText())
        
        # For object_type, use direct attribute access since there's no update method
        self.editor_backend.current_brick.object_type = self.object_type_combo.currentText()
        self.editor_backend.current_brick._mark_modified()

        # Trigger backend update event
        self.editor_backend.emit_event('brick_updated', self.editor_backend.current_brick.to_dict())

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
        header.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px;")
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

        # Object type
        self.object_type_combo = QComboBox()
        self.object_type_combo.addItems(["NodeShape", "PropertyShape"])
        self.object_type_combo.currentTextChanged.connect(self._on_object_type_changed)
        info_layout.addRow("Object Type:", self.object_type_combo)

        # Target class/property (context-dependent)
        target_layout = QHBoxLayout()
        self.target_class_edit = QLineEdit()
        self.target_class_edit.setPlaceholderText("e.g., schema:Student, schema:Product, brick:Equipment")
        target_layout.addWidget(QLabel("Target Class:"))
        target_layout.addWidget(self.target_class_edit)
        self.browse_btn = QPushButton("📚 Browse")
        self.browse_btn.setToolTip("Browse ontologies to select a class")
        self.browse_btn.clicked.connect(self._request_context_browser)
        target_layout.addWidget(self.browse_btn)
        info_layout.addRow(target_layout)

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


        export_btn = QPushButton("📤 Export SHACL")
        export_btn.clicked.connect(self.export_shacl)
        action_layout.addWidget(export_btn)

        action_layout.addStretch()
        editor_layout.addLayout(action_layout)

        # Connect property selection
        self.properties_list.itemClicked.connect(self.on_property_selected)
        self.properties_list.itemDoubleClicked.connect(self.edit_property)

        return editor_widget

    def create_browser_panel(self):
        """Create the browser panel"""
        browser_widget = QWidget()
        browser_layout = QVBoxLayout(browser_widget)

        # Header
        header = QLabel("📚 Ontology Browser & Brick Library")
        header.setStyleSheet(
            "font-size: 16px; font-weight: bold; padding: 10px; background: #e8f5e8; border-radius: 5px;")
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

        # Bricks lists (right)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Node bricks list
        right_layout.addWidget(QLabel("Node Bricks:"))
        self.node_brick_list = QListWidget()
        self.node_brick_list.itemClicked.connect(self.on_node_brick_selected)
        self.node_brick_list.itemDoubleClicked.connect(self.on_node_brick_double_clicked)
        right_layout.addWidget(self.node_brick_list)
        
        # Property bricks list
        right_layout.addWidget(QLabel("Property Bricks:"))
        self.property_brick_list = QListWidget()
        self.property_brick_list.itemClicked.connect(self.on_property_brick_selected)
        self.property_brick_list.itemDoubleClicked.connect(self.on_property_brick_double_clicked)
        right_layout.addWidget(self.property_brick_list)
        
        # Add properties button
        compose_button = QPushButton("Add Selected Properties to Loaded Brick")
        compose_button.clicked.connect(self.compose_brick_with_properties)
        right_layout.addWidget(compose_button)

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
            # Preserve current brick name
            current_brick_name = self.brick_name_edit.text()
            display_text = current_item.text()
            
            # Extract property name from display text
            # Handle both formats: "propertyName" and "propertyName (constraints)"
            if " (" in display_text:
                prop_name = display_text.split(" (")[0]
            elif ": " in display_text:
                # Handle simple properties like "nodeKind: IRI"
                prop_name = display_text.split(": ")[0]
            else:
                prop_name = display_text
            
            # Trigger backend event
            self.editor_backend.remove_property_from_current_brick(prop_name)
            # Restore brick name in case it was overwritten during property removal
            self.brick_name_edit.setText(current_brick_name)

    def remove_constraint(self):
        """Remove selected constraint"""
        current_item = self.constraints_list.currentItem()
        if current_item:
            # This is simplified - in a real implementation, we'd need to track which constraint belongs to which property
            self.constraints_list.takeItem(self.constraints_list.row(current_item))
            self.statusBar().showMessage("✅ Constraint removed")

    # def browse_classes(self):
    #     """Browse ontologies for target class selection using unified browser"""
    #     # Create a simple dialog with ontology browser for class selection
    #     dialog = QDialog(self)
    #     dialog.setWindowTitle("Select Target Class from Ontology")
    #     dialog.setModal(True)
    #     dialog.resize(500, 400)
    #
    #     # Create layout
    #     layout = QVBoxLayout(dialog)
    #
    #     # Create ontology list
    #     ontology_list = QListWidget()
    #     layout.addWidget(ontology_list)
    #
    #     # Create terms list
    #     terms_list = QListWidget()
    #     layout.addWidget(terms_list)
    #
    #     # Get ontologies from backend
    #     ontologies = self.editor_backend.ontology_manager.ontologies
    #
    #     # Populate ontology list
    #     for name, data in ontologies.items():
    #         class_count = len(data.get('classes', []))
    #         prop_count = len(data.get('properties', []))
    #         item = QListWidgetItem(f"{name} ({class_count} classes, {prop_count} properties)")
    #         item.setData(Qt.ItemDataRole.UserRole, name)
    #         ontology_list.addItem(item)
    #
    #     def on_ontology_selected(item):
    #         ontology_name = item.data(Qt.ItemDataRole.UserRole)
    #         if ontology_name and ontology_name in ontologies:
    #             terms_list.clear()
    #             ontology_data = ontologies[ontology_name]
    #
    #             # Show classes only
    #             if 'classes' in ontology_data:
    #                 for class_info in ontology_data['classes']:
    #                     item = QListWidgetItem(f"Class: {class_info['name']}")
    #                     item.setData(Qt.ItemDataRole.UserRole, {'type': 'class', **class_info})
    #                     terms_list.addItem(item)
    #
    #     # Handle class selection
    #     def on_class_selected(item):
    #         term_data = item.data(Qt.ItemDataRole.UserRole)
    #         if term_data and term_data.get("type") == "class":
    #             self.target_class_edit.setText(term_data["uri"])
    #             dialog.accept()
    #
    #     ontology_list.itemClicked.connect(on_ontology_selected)
    #     terms_list.itemDoubleClicked.connect(on_class_selected)
    #
    #     # Buttons
    #     button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
    #     layout.addWidget(button_box)
    #     button_box.rejected.connect(dialog.reject)
    #
    #     dialog.exec()

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

    # def populate_ontology_list(self):
    #     """Populate the ontology list with available ontologies"""
    #     ontologies = self.editor_backend.ontology_manager.ontologies
    #
    #     # Clear existing items to prevent duplicates
    #     self.ontology_list.clear()
    #
    #     for name, data in ontologies.items():
    #         class_count = len(data.get('classes', []))
    #         prop_count = len(data.get('properties', []))
    #         item = QListWidgetItem(f"{name} ({class_count} classes, {prop_count} properties)")
    #         item.setData(Qt.ItemDataRole.UserRole, name)
    #         self.ontology_list.addItem(item)

    # def on_ontology_selected(self, item):
    #     """Handle ontology selection"""
    #     ontology_name = item.data(Qt.ItemDataRole.UserRole)
    #     ontologies = self.editor_backend.ontology_manager.ontologies
    #
    #     if ontology_name and ontology_name in ontologies:
    #         self.display_ontology_terms(ontologies[ontology_name])

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

    def edit_property(self, item):
        """Handle property double-click for editing"""
        prop_name = item.text().split(" (")[0]  # Extract property name from display text
        current_brick = self.editor_backend.get_current_brick()
        if prop_name in current_brick.get("properties", {}):
            prop_data = current_brick["properties"][prop_name]
            # Hide the property editor panel while editing
            self.prop_editor_widget.setVisible(False)
            self.show_property_edit_dialog(prop_data, prop_name)

    def show_property_edit_dialog(self, property_data, prop_name):
        """Show dialog to edit an existing property"""
        # Preserve current brick name
        current_brick_name = self.brick_name_edit.text()

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Property: {prop_name}")
        dialog.setModal(True)
        dialog.resize(600, 600)

        # Create main layout with scroll area
        main_layout = QVBoxLayout(dialog)
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        layout = QFormLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        # Property name
        name_edit = QLineEdit()
        name_edit.setText(prop_name)
        layout.addRow("Property Name:", name_edit)

        # Property path with help
        path_layout = QHBoxLayout()
        path_edit = QLineEdit()
        path_edit.setText(property_data.get("path", "") if isinstance(property_data, dict) else prop_name)
        path_layout.addWidget(path_edit)

        self.browse_btn = QPushButton("📚 Browse")
        self.browse_btn.setToolTip("Browse ontologies to select property URI")
        self.browse_btn.setMaximumWidth(80)
        path_layout.addWidget(self.browse_btn)

        layout.addRow("Property Path (URI):", path_layout)

        # Data type
        datatype_combo = QComboBox()
        datatype_combo.addItems([
                "xsd:string - Text values",
                "xsd:integer - Whole numbers",
                "xsd:decimal - Decimal numbers",
                "xsd:boolean - True/False values",
                "xsd:date - Date values",
                "xsd:anyURI - Resource references"
                ])

        # Set current datatype
        if isinstance(property_data, dict):
            current_datatype = property_data.get("datatype", "xsd:string")
            for i in range(datatype_combo.count()):
                if datatype_combo.itemText(i).startswith(current_datatype):
                    datatype_combo.setCurrentIndex(i)
                    break
        layout.addRow("Data Type:", datatype_combo)

        # Constraints section
        constraints_group = QGroupBox("🔒 Constraints")
        constraints_layout = QVBoxLayout(constraints_group)

        # Constraints list
        constraints_list = QListWidget()
        constraints_list.setMaximumHeight(120)

        # Add existing constraints
        existing_constraints = property_data.get("constraints", []) if isinstance(property_data, dict) else []
        for constraint in existing_constraints:
            constraint_text = f"{constraint['constraint_type']}: {constraint['value']}"
            constraints_list.addItem(constraint_text)

        constraints_layout.addWidget(constraints_list)

        # Quick constraint buttons (context-aware)
        quick_constraints_layout = QHBoxLayout()

        # Create constraint buttons
        min_len_btn = QPushButton("Min Length")
        max_len_btn = QPushButton("Max Length")
        pattern_btn = QPushButton("Pattern")
        min_value_btn = QPushButton("Min Value")
        max_value_btn = QPushButton("Max Value")
        required_btn = QPushButton("Required")
        remove_btn = QPushButton("Remove")

        def add_min_length():
            value, ok = QInputDialog.getText(dialog, "Minimum Length", "Enter minimum length:")
            if ok and value.isdigit():
                constraints_list.addItem(f"minLength: {value}")

        def add_max_length():
            value, ok = QInputDialog.getText(dialog, "Maximum Length", "Enter maximum length:")
            if ok and value.isdigit():
                constraints_list.addItem(f"maxLength: {value}")

        def add_pattern():
            value, ok = QInputDialog.getText(dialog, "Pattern", "Enter regex pattern:")
            if ok and value:
                constraints_list.addItem(f"pattern: {value}")

        def add_min_value():
            value, ok = QInputDialog.getText(dialog, "Minimum Value", "Enter minimum value:")
            if ok:
                constraints_list.addItem(f"minInclusive: {value}")

        def add_max_value():
            value, ok = QInputDialog.getText(dialog, "Maximum Value", "Enter maximum value:")
            if ok:
                constraints_list.addItem(f"maxInclusive: {value}")

        def add_required():
            constraints_list.addItem("minCount: 1")

        def remove_constraint():
            current_item = constraints_list.currentItem()
            if current_item:
                constraints_list.takeItem(constraints_list.row(current_item))

        # Connect button signals
        min_len_btn.clicked.connect(add_min_length)
        max_len_btn.clicked.connect(add_max_length)
        pattern_btn.clicked.connect(add_pattern)
        min_value_btn.clicked.connect(add_min_value)
        max_value_btn.clicked.connect(add_max_value)
        required_btn.clicked.connect(add_required)
        remove_btn.clicked.connect(remove_constraint)

        # Add buttons to layout
        quick_constraints_layout.addWidget(min_len_btn)
        quick_constraints_layout.addWidget(max_len_btn)
        quick_constraints_layout.addWidget(pattern_btn)
        quick_constraints_layout.addWidget(min_value_btn)
        quick_constraints_layout.addWidget(max_value_btn)
        quick_constraints_layout.addWidget(required_btn)
        quick_constraints_layout.addWidget(remove_btn)

        # Function to update constraint buttons based on data type
        def update_constraint_buttons():
            datatype = datatype_combo.currentText().split(" - ")[
                0] if " - " in datatype_combo.currentText() else datatype_combo.currentText()

            # Hide all buttons first
            min_len_btn.hide()
            max_len_btn.hide()
            pattern_btn.hide()
            min_value_btn.hide()
            max_value_btn.hide()

            # Show relevant buttons based on data type
            if datatype in ["xsd:string"]:
                min_len_btn.show()
                max_len_btn.show()
                pattern_btn.show()
            elif datatype in ["xsd:integer", "xsd:decimal"]:
                min_value_btn.show()
                max_value_btn.show()
            elif datatype in ["xsd:date"]:
                min_value_btn.show()
                max_value_btn.show()
            elif datatype in ["xsd:boolean"]:
                pass
            elif datatype in ["xsd:anyURI"]:
                pattern_btn.show()

            required_btn.show()
            remove_btn.show()

        # Connect data type change to update buttons
        datatype_combo.currentTextChanged.connect(update_constraint_buttons)

        # Initial update
        update_constraint_buttons()

        constraints_layout.addLayout(quick_constraints_layout)
        layout.addRow(constraints_group)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        main_layout.addWidget(buttons)

        # Handle dialog result
        def on_accept():
            # Extract just the datatype part (before " - ")
            datatype_full = datatype_combo.currentText()
            datatype = datatype_full.split(" - ")[0] if " - " in datatype_full else datatype_full

            # Parse constraints from list
            constraints = []
            for i in range(constraints_list.count()):
                constraint_text = constraints_list.item(i).text()
                if ": " in constraint_text:
                    constraint_type, value = constraint_text.split(": ", 1)
                    constraints.append({
                            "constraint_type": constraint_type,
                            "value"          : value
                            })

            # Update property in backend
            new_prop_name = name_edit.text()
            new_property_data = {
                    "name"       : new_prop_name,
                    "path"       : path_edit.text(),
                    "datatype"   : datatype,
                    "constraints": constraints
                    }

            # Remove old property and add new one (handles name changes)
            self.editor_backend.remove_property_from_current_brick(prop_name)
            self.editor_backend.add_property_to_current_brick(new_property_data)
            # Restore brick name in case it was overwritten during property editing
            self.brick_name_edit.setText(current_brick_name)

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

        self.browse_btn.clicked.connect(browse_properties)
        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)

        dialog.exec()

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
            constraints = property_data.get("constraints", [])
        else:
            # Simple property value - use property name as path
            self.prop_path_edit.setText(prop_name)
            constraints = []
        self.prop_editor_layout.addRow("Property Path:", self.prop_path_edit)

        # Display constraints (read-only)
        if constraints:
            constraints_group = QGroupBox("🔒 Constraints")
            constraints_layout = QVBoxLayout(constraints_group)

            constraints_list = QListWidget()
            constraints_list.setMaximumHeight(100)
            for constraint in constraints:
                constraint_text = f"{constraint['constraint_type']}: {constraint['value']}"
                constraints_list.addItem(constraint_text)
            constraints_layout.addWidget(constraints_list)

            self.prop_editor_layout.addRow(constraints_group)

            # Add note about editing constraints
            note_label = QLabel("💡 To modify constraints, remove and re-add the property with updated constraints.")
            note_label.setWordWrap(True)
            note_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
            self.prop_editor_layout.addRow(note_label)
        else:
            # Add note about adding constraints
            note_label = QLabel("💡 To add constraints, remove and re-add the property with constraints.")
            note_label.setWordWrap(True)
            note_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
            self.prop_editor_layout.addRow(note_label)

        self.prop_editor_widget.setVisible(True)

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

    # def update_constraints_display(self):
    #     """Update constraints display for current property"""
    #     current_item = self.properties_list.currentItem()
    #     if current_item:
    #         prop_name = current_item.text().split(" (")[0]  # Extract property name
    #         if prop_name in self.editor_backend.get_current_brick().get("properties", {}):
    #             prop_data = self.editor_backend.get_current_brick()["properties"][prop_name]
    #             if isinstance(prop_data, dict):
    #                 constraints = prop_data.get("constraints", [])
    #                 self.prop_constraints_list.clear()
    #                 for constraint in constraints:
    #                     constraint_text = f"{constraint['constraint_type']}: {constraint['value']}"
    #                     self.prop_constraints_list.addItem(constraint_text)
    #             else:
    #                 # Simple property value - no constraints
    #                 self.prop_constraints_list.clear()
    #                 self.prop_constraints_list.addItem("No constraints for this property")

    def save_brick(self):
        """Save current brick - trigger backend event"""
        # Use backend-controlled save operation
        self.editor_backend.request_save_brick()


    def edit_brick_from_library(self):
        """Edit brick from library"""
        current_item = self.node_brick_list.currentItem()
        if current_item:
            brick_data = current_item.data(Qt.ItemDataRole.UserRole)
            self.editor_backend.set_current_brick(brick_data)
            self.display_current_brick()
            self.statusBar().showMessage(f"✅ Brick '{brick_data['name']}' loaded for editing")

    def display_current_brick(self):
        """Display current brick data in editor"""
        current_brick = self.editor_backend.get_current_brick()
        if current_brick:
            # Store working copy to preserve original brick data
            self._working_brick = current_brick.copy()
            
            self.brick_name_edit.setText(current_brick.get("name", ""))
            self.target_class_edit.setText(current_brick.get("target_class", ""))
            self.description_edit.setPlainText(current_brick.get("description", ""))
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

        # Check if brick has been saved (has brick_id)
        if "brick_id" not in current_brick or not current_brick["brick_id"]:
            QMessageBox.warning(self, "Brick Not Saved", "Please save the brick first before exporting to SHACL format")
            return

        # Get SHACL content from backend
        result = self.editor_backend.brick_api.export_brick_shacl(current_brick["brick_id"])
        if result["status"] == "success":
            # Suggest filename based on brick name
            current_brick = self.editor_backend.get_current_brick()
            brick_name = current_brick.get("name", "brick").replace(" ", "_").lower()
            suggested_filename = f"{brick_name}.ttl"
            
            # Save to file with suggested name and .ttl extension, remembering last directory
            import os
            last_dir = getattr(self.editor_backend, 'last_export_dir', None)
            
            # Get full file path from user selection
            # Combine directory and suggested filename for proper pre-filling
            if last_dir:
                full_suggested_path = os.path.join(last_dir, suggested_filename)
            else:
                full_suggested_path = suggested_filename
                
            file_path, _ = QFileDialog.getSaveFileName(
                    self, "Save SHACL File", full_suggested_path, "Turtle Files (*.ttl);;All Files (*)"
                    )
            
            # Update the remembered directory to the actual chosen one
            if file_path:
                self.editor_backend.last_export_dir = os.path.dirname(file_path)
                self.editor_backend.brick_api._save_config()
                
                # Ensure .ttl extension
                if not file_path.endswith('.ttl'):
                    file_path += '.ttl'
                    
                # Write SHACL content to file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(result["data"]["content"])
                    
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
            self.node_brick_list.clear()
            self.property_brick_list.clear()
            bricks = result["data"]["bricks"]
            
            for brick in bricks:
                item = QListWidgetItem(f" {brick["name"]}")
                item.setData(Qt.ItemDataRole.UserRole, brick)
                
                if brick.get("object_type") == "NodeShape":
                    self.node_brick_list.addItem(item)
                elif brick.get("object_type") == "PropertyShape":
                    self.property_brick_list.addItem(item)

            self.statusBar().showMessage(f"Library '{library_name}' loaded ({len(bricks)} bricks)")
        else:
            self.node_brick_list.clear()
            self.property_brick_list.clear()
            self.statusBar().showMessage(f"Error loading library: {result["message"]}")

    def on_node_brick_selected(self, item):
        """Handle node brick selection"""
        brick_data = item.data(Qt.ItemDataRole.UserRole)
        if brick_data:
            self.statusBar().showMessage(f"Node brick selected: {brick_data['name']}")
    
    def on_property_brick_selected(self, item):
        """Handle property brick selection"""
        brick_data = item.data(Qt.ItemDataRole.UserRole)
        if brick_data:
            self.statusBar().showMessage(f"Property brick selected: {brick_data['name']}")
    
    def on_node_brick_double_clicked(self, item):
        """Handle node brick double-click - load into editor"""
        brick_data = item.data(Qt.ItemDataRole.UserRole)
        if brick_data:
            self.editor_backend.set_current_brick(brick_data)
            self.display_current_brick()
            self.statusBar().showMessage(f"Node brick '{brick_data['name']}' loaded for editing")
    
    def on_property_brick_double_clicked(self, item):
        """Handle property brick double-click - load into editor"""
        brick_data = item.data(Qt.ItemDataRole.UserRole)
        if brick_data:
            self.editor_backend.set_current_brick(brick_data)
            self.display_current_brick()
            self.statusBar().showMessage(f"Property brick '{brick_data['name']}' loaded for editing")
    
    def compose_brick_with_properties(self):
        """Add selected property bricks to currently loaded node brick"""
        # Check if a node brick is currently loaded in editor
        current_brick = self.editor_backend.get_current_brick()
        if not current_brick:
            QMessageBox.warning(self, "No Brick Loaded", "Please load a node brick into the editor first")
            return
        
        if current_brick.get("object_type") != "NodeShape":
            QMessageBox.warning(self, "Not a Node Brick", "Current brick is not a node brick. Please load a node brick first")
            return
        
        # Get selected property bricks
        selected_properties = []
        for item in self.property_brick_list.selectedItems():
            selected_properties.append(item.data(Qt.ItemDataRole.UserRole))
        
        if not selected_properties:
            QMessageBox.warning(self, "No Properties", "Please select at least one property brick to add")
            return
        
        # Add each selected property to the current node brick
        added_count = 0
        skipped_count = 0
        
        for prop_brick in selected_properties:
            prop_name = prop_brick["name"]
            
            # Check if property already exists
            if prop_name in current_brick.get("properties", {}):
                skipped_count += 1
                continue
            
            # Extract property data from property brick
            prop_path = prop_brick.get("path", prop_brick.get("properties", {}).get("path", prop_name))
            prop_datatype = prop_brick.get("datatype", prop_brick.get("properties", {}).get("datatype", "xsd:string"))
            prop_constraints = prop_brick.get("constraints", [])
            
            # Add property to current brick
            self.editor_backend.add_property_to_current_brick({
                "name": prop_name,
                "path": prop_path,
                "datatype": prop_datatype,
                "constraints": prop_constraints
            })
            
            added_count += 1
        
        # Update display
        self.display_current_brick()
        
        # Show result message
        if added_count > 0:
            message = f"Added {added_count} properties to '{current_brick['name']}'"
            if skipped_count > 0:
                message += f" (skipped {skipped_count} duplicates)"
            self.statusBar().showMessage(message)
        else:
            self.statusBar().showMessage("No new properties added (all were duplicates)")

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

    # def browse_ontology_for_property(self, name_edit, path_edit):
    #     """Open ontology browser to select a property"""
    #     # Create a simple dialog with ontology browser
    #     dialog = QDialog(self)
    #     dialog.setWindowTitle("Select Property from Ontology")
    #     dialog.setModal(True)
    #     dialog.resize(500, 400)
    #
    #     # Create layout
    #     layout = QVBoxLayout(dialog)
    #
    #     # Create ontology list
    #     ontology_list = QListWidget()
    #     layout.addWidget(ontology_list)
    #
    #     # Create terms list
    #     terms_list = QListWidget()
    #     layout.addWidget(terms_list)
    #
    #     # Get ontologies from backend
    #     ontologies = self.editor_backend.ontology_manager.ontologies
    #
    #     # Populate ontology list
    #     for name, data in ontologies.items():
    #         class_count = len(data.get('classes', []))
    #         prop_count = len(data.get('properties', []))
    #         item = QListWidgetItem(f"{name} ({class_count} classes, {prop_count} properties)")
    #         item.setData(Qt.ItemDataRole.UserRole, name)
    #         ontology_list.addItem(item)
    #
    #     def on_ontology_selected(item):
    #         ontology_name = item.data(Qt.ItemDataRole.UserRole)
    #         if ontology_name and ontology_name in ontologies:
    #             terms_list.clear()
    #             ontology_data = ontologies[ontology_name]
    #
    #             # Show properties only
    #             if 'properties' in ontology_data:
    #                 for prop_info in ontology_data['properties']:
    #                     item = QListWidgetItem(f"Property: {prop_info['name']}")
    #                     item.setData(Qt.ItemDataRole.UserRole, {'type': 'property', **prop_info})
    #                     terms_list.addItem(item)
    #
    #     # Handle property selection
    #     def on_property_selected(item):
    #         term_data = item.data(Qt.ItemDataRole.UserRole)
    #         if term_data and term_data.get("type") == "property":
    #             name_edit.setText(term_data["name"])
    #             path_edit.setText(term_data["uri"])
    #             dialog.accept()
    #
    #     ontology_list.itemClicked.connect(on_ontology_selected)
    #     terms_list.itemDoubleClicked.connect(on_property_selected)
    #
    #     # Buttons
    #     button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
    #     layout.addWidget(button_box)
    #     button_box.rejected.connect(dialog.reject)
    #
    #     dialog.exec()


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
