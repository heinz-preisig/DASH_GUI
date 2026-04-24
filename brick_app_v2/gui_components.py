import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QLabel, QLineEdit, QTextEdit, QComboBox, 
    QPushButton, QListWidget, QListWidgetItem, QGroupBox, QFormLayout,
    QMessageBox, QFileDialog, QDialog, QDialogButtonBox,
    QGridLayout, QRadioButton, QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi

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
from core.ontology_manager import OntologyManager

# Temporary stub classes to make the application start
# These should be replaced with proper implementations
class GenericBrowser(QDialog):
    """Unified browser dialog for ontology, bricks, and constraints"""
    
    def __init__(self, data_source, browser_type="ontology", parent=None, **kwargs):
        super().__init__(parent)
        self.data_source = data_source
        self.browser_type = browser_type  # "ontology", "brick", "constraint"
        self.selected_item = None
        self.all_items = []  # Store all items for filtering
        self.options = kwargs  # Additional options (mode, filters, etc.)
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        
        # Setup type-specific controls
        self.setup_type_controls(layout)
        
        # For constraint editor, don't add search and list
        if self.browser_type != "constraint":
            # Search field (for browser types)
            search_layout = QHBoxLayout()
            search_layout.addWidget(QLabel("Search:"))
            
            self.search_edit = QLineEdit()
            self.search_edit.setPlaceholderText("Type to filter...")
            self.search_edit.textChanged.connect(self.on_search_changed)
            search_layout.addWidget(self.search_edit)
            
            layout.addLayout(search_layout)
            
            # Results list (for browser types)
            self.results_list = QListWidget()
            self.results_list.itemDoubleClicked.connect(self.on_item_selected)
            layout.addWidget(self.results_list)
        
        # Buttons (common to all types)
        button_layout = QHBoxLayout()
        
        if self.browser_type == "constraint":
            ok_btn = QPushButton("OK")
            ok_btn.clicked.connect(self.on_accept_clicked)
            button_layout.addWidget(ok_btn)
        else:
            select_btn = QPushButton("Select")
            select_btn.clicked.connect(self.on_select_clicked)
            button_layout.addWidget(select_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def setup_type_controls(self, layout):
        """Setup type-specific controls"""
        if self.browser_type == "ontology":
            self.setup_ontology_controls(layout)
        elif self.browser_type == "brick":
            self.setup_brick_controls(layout)
        elif self.browser_type == "constraint":
            self.setup_constraint_controls(layout)
    
    def setup_ontology_controls(self, layout):
        """Setup ontology-specific controls"""
        self.setWindowTitle("Browse Ontology")
        self.setGeometry(200, 200, 600, 500)
        
        # Ontology selector
        onto_layout = QHBoxLayout()
        onto_layout.addWidget(QLabel("Ontology:"))
        
        self.ontology_combo = QComboBox()
        self.ontology_combo.currentTextChanged.connect(self.on_ontology_changed)
        onto_layout.addWidget(self.ontology_combo)
        
        layout.addLayout(onto_layout)
        
        # Mode selector (classes vs properties)
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Browse:"))
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Classes", "Properties"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        
        layout.addLayout(mode_layout)
    
    def setup_brick_controls(self, layout):
        """Setup brick-specific controls"""
        self.setWindowTitle("Browse Property Bricks")
        self.setGeometry(200, 200, 500, 400)
        
        # Library selector
        lib_layout = QHBoxLayout()
        lib_layout.addWidget(QLabel("Library:"))
        
        self.library_combo = QComboBox()
        self.library_combo.currentTextChanged.connect(self.on_library_changed)
        lib_layout.addWidget(self.library_combo)
        
        layout.addLayout(lib_layout)
        
        # Filter for PropertyShape bricks only
        filter_layout = QHBoxLayout()
        self.filter_check = QCheckBox("PropertyShape only")
        self.filter_check.setChecked(True)
        self.filter_check.stateChanged.connect(self.apply_search_filter)
        filter_layout.addWidget(self.filter_check)
        layout.addLayout(filter_layout)
    
    def setup_constraint_controls(self, layout):
        """Setup constraint-specific controls"""
        self.setWindowTitle("Constraint Editor")
        self.setGeometry(200, 200, 450, 350)
        
        # Constraint type selector with user-friendly names
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        
        self.constraint_type_combo = QComboBox()
        self.constraint_type_combo.addItems([
            "Minimum Length", "Maximum Length", "Minimum Value", "Maximum Value",
            "Minimum Value (Exclusive)", "Maximum Value (Exclusive)", 
            "Pattern Match", "Data Type"
        ])
        self.constraint_type_combo.currentTextChanged.connect(self.on_constraint_type_changed)
        type_layout.addWidget(self.constraint_type_combo)
        
        layout.addLayout(type_layout)
        
        # Value input with dynamic placeholder
        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel("Value:"))
        
        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText("Enter constraint value...")
        value_layout.addWidget(self.value_edit)
        
        layout.addLayout(value_layout)
        
        # Description/Help text
        self.help_label = QLabel("Select a constraint type and enter a value")
        self.help_label.setWordWrap(True)
        self.help_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(self.help_label)
    
    def load_data(self):
        """Load data based on browser type"""
        if self.browser_type == "ontology":
            self.load_ontology_data()
        elif self.browser_type == "brick":
            self.load_brick_data()
        elif self.browser_type == "constraint":
            self.load_constraint_data()
    
    def load_ontology_data(self):
        """Load ontology list"""
        ontologies = self.data_source.ontologies
        self.ontology_combo.clear()
        
        # Sort ontologies alphabetically
        sorted_ontologies = sorted(ontologies.items(), key=lambda x: x[0].lower())
        
        for name, data in sorted_ontologies:
            classes = data.get('classes', {})
            properties = data.get('properties', {})
            class_count = len(classes)
            prop_count = len(properties)
            display_text = f"{name} ({class_count} classes, {prop_count} properties)"
            self.ontology_combo.addItem(display_text, name)
        
        if self.ontology_combo.count() > 0:
            self.load_ontology_items()
    
    def load_ontology_items(self):
        """Load ontology classes or properties"""
        if self.ontology_combo.currentIndex() < 0:
            return
        
        ontology_name = self.ontology_combo.currentData()
        if not ontology_name or ontology_name not in self.data_source.ontologies:
            return
        
        ontology_data = self.data_source.ontologies[ontology_name]
        mode = self.mode_combo.currentText().lower()
        
        if mode == "classes":
            items_dict = ontology_data.get('classes', {})
        else:
            items_dict = ontology_data.get('properties', {})
        
        # Convert dictionary to list of items
        items = []
        for uri, data in items_dict.items():
            if isinstance(data, dict) and 'name' in data:
                items.append({
                    'name': data['name'],
                    'uri': uri,
                    'description': data.get('description', ''),
                    'comment': data.get('comment', '')
                })
            else:
                items.append({
                    'name': str(data),
                    'uri': uri,
                    'description': '',
                    'comment': ''
                })
        
        self.all_items = sorted(items, key=lambda x: x['name'].lower())
        self.apply_search_filter()
    
    def load_brick_data(self):
        """Load brick data"""
        libraries = self.data_source.get_libraries()
        self.library_combo.clear()
        
        for library in libraries:
            self.library_combo.addItem(library)
        
        if self.library_combo.count() > 0:
            self.load_brick_items()
    
    def load_brick_items(self):
        """Load property bricks from selected library"""
        library_name = self.library_combo.currentText()
        if not library_name:
            return
        
        # Get all bricks and filter for PropertyShape
        bricks = self.data_source.get_all_bricks()
        items = []
        
        for brick in bricks:
            # Handle both SHACLBrick objects and dictionary data
            if hasattr(brick, 'object_type'):
                # SHACLBrick object - access attributes directly
                brick_type = brick.object_type
                brick_name = getattr(brick, 'name', 'Unknown')
                brick_id = getattr(brick, 'brick_id', '')
                property_path = getattr(brick, 'property_path', '')
                description = getattr(brick, 'description', '')
                properties = getattr(brick, 'properties', {})
            else:
                # Dictionary data - use .get() method
                brick_type = brick.get('object_type', '')
                brick_name = brick.get('name', 'Unknown')
                brick_id = brick.get('brick_id', '')
                property_path = brick.get('property_path', '')
                description = brick.get('description', '')
                properties = brick.get('properties', {})
            
            # Filter by PropertyShape if checkbox is checked
            if self.filter_check.isChecked() and brick_type != 'PropertyShape':
                continue
            
            items.append({
                'name': brick_name,
                'brick_id': brick_id,
                'object_type': brick_type,
                'property_path': property_path,
                'description': description,
                'properties': properties
            })
        
        self.all_items = sorted(items, key=lambda x: x['name'].lower())
        self.apply_search_filter()
    
    def load_constraint_data(self):
        """Initialize constraint editor - no list needed"""
        # Constraint editor doesn't need to load a list
        # It's a direct editor interface
        pass
    
    def on_constraint_type_changed(self):
        """Handle constraint type change"""
        type_name = self.constraint_type_combo.currentText()
        
        # Update placeholder and help text based on type
        help_texts = {
            "Minimum Length": "Minimum number of characters (e.g., 5)",
            "Maximum Length": "Maximum number of characters (e.g., 100)",
            "Minimum Value": "Minimum numeric value (e.g., 0)",
            "Maximum Value": "Maximum numeric value (e.g., 999)",
            "Minimum Value (Exclusive)": "Minimum value not included (e.g., 0)",
            "Maximum Value (Exclusive)": "Maximum value not included (e.g., 100)",
            "Pattern Match": "Regular expression pattern (e.g., [A-Za-z]+)",
            "Data Type": "XML Schema datatype (e.g., xsd:string)"
        }
        
        placeholders = {
            "Minimum Length": "Enter minimum length...",
            "Maximum Length": "Enter maximum length...",
            "Minimum Value": "Enter minimum value...",
            "Maximum Value": "Enter maximum value...",
            "Minimum Value (Exclusive)": "Enter exclusive minimum...",
            "Maximum Value (Exclusive)": "Enter exclusive maximum...",
            "Pattern Match": "Enter regex pattern...",
            "Data Type": "Enter datatype..."
        }
        
        self.value_edit.setPlaceholderText(placeholders.get(type_name, "Enter value..."))
        self.help_label.setText(help_texts.get(type_name, "Select a constraint type and enter a value"))
    
    def on_ontology_changed(self):
        """Handle ontology selection change"""
        self.load_ontology_items()
    
    def on_mode_changed(self):
        """Handle mode change"""
        self.load_ontology_items()
    
    def on_library_changed(self):
        """Handle library selection change"""
        self.load_brick_items()
    
    def on_search_changed(self):
        """Handle search text change"""
        self.apply_search_filter()
    
    def apply_search_filter(self):
        """Apply search filter to items"""
        search_text = self.search_edit.text().lower().strip()
        
        self.results_list.clear()
        
        for item in self.all_items:
            # Filter by search text
            name_match = search_text == "" or search_text in item['name'].lower()
            
            # Additional filtering for bricks
            if self.browser_type == "brick" and self.filter_check.isChecked():
                type_match = item.get('object_type') == 'PropertyShape'
                if not type_match:
                    continue
            
            if name_match:
                display_text = self.get_display_text(item)
                list_item = QListWidgetItem(display_text)
                list_item.setData(Qt.ItemDataRole.UserRole, item)
                self.results_list.addItem(list_item)
    
    def get_display_text(self, item):
        """Get display text for item based on browser type"""
        if self.browser_type == "ontology":
            return item['name']
        elif self.browser_type == "brick":
            type_info = f" ({item.get('object_type', 'Unknown')})"
            return f"{item['name']}{type_info}"
        elif self.browser_type == "constraint":
            return item['name']
        return item['name']
    
    def on_item_selected(self, item):
        """Handle item double-click"""
        self.selected_item = item.data(Qt.ItemDataRole.UserRole)
        
        # Special handling for constraint browser
        if self.browser_type == "constraint":
            # Get current values from UI
            constraint_type = self.constraint_type_combo.currentText()
            constraint_value = self.value_edit.text()
            
            self.selected_item = {
                'type': constraint_type,
                'value': constraint_value,
                'name': self.selected_item['name']
            }
        
        self.accept()
    
    def on_accept_clicked(self):
        """Handle OK button click for constraint editor"""
        constraint_type = self.constraint_type_combo.currentText()
        constraint_value = self.value_edit.text().strip()
        
        if not constraint_value:
            QMessageBox.warning(self, "Warning", "Please enter a constraint value")
            return
        
        # Map user-friendly names to constraint types
        type_mapping = {
            "Minimum Length": "minLength",
            "Maximum Length": "maxLength", 
            "Minimum Value": "minInclusive",
            "Maximum Value": "maxInclusive",
            "Minimum Value (Exclusive)": "minExclusive",
            "Maximum Value (Exclusive)": "maxExclusive",
            "Pattern Match": "pattern",
            "Data Type": "datatype"
        }
        
        actual_type = type_mapping.get(constraint_type, constraint_type)
        
        self.selected_item = {
            'type': actual_type,
            'value': constraint_value,
            'name': constraint_type
        }
        
        self.accept()
    
    def on_select_clicked(self):
        """Handle select button click"""
        current_item = self.results_list.currentItem()
        if current_item:
            self.selected_item = current_item.data(Qt.ItemDataRole.UserRole)
            
            # Special handling for constraint browser
            if self.browser_type == "constraint":
                constraint_type = self.constraint_type_combo.currentText()
                constraint_value = self.value_edit.text()
                
                self.selected_item = {
                    'type': constraint_type,
                    'value': constraint_value,
                    'name': self.selected_item['name']
                }
            
            self.accept()

# Convenience wrappers for backward compatibility
class SimpleOntologyBrowser(GenericBrowser):
    """Ontology browser wrapper"""
    
    def __init__(self, ontology_manager, parent=None, mode="classes"):
        mode_index = 0 if mode == "classes" else 1
        super().__init__(ontology_manager, "ontology", parent)
        self.mode_combo.setCurrentIndex(mode_index)

class PropertyBrickBrowser(GenericBrowser):
    """Property brick browser wrapper"""
    
    def __init__(self, parent=None, brick_core=None):
        super().__init__(brick_core, "brick", parent)

class ConstraintEditorDialog(GenericBrowser):
    """Constraint editor wrapper"""
    
    def __init__(self, parent=None, prop_data=None):
        super().__init__(None, "constraint", parent)
        self.prop_data = prop_data or {}
    
    def get_constraint_data(self):
        """Get constraint data"""
        if self.selected_item:
            return {
                'constraint_type': self.selected_item.get('type', 'minLength'),
                'value': self.selected_item.get('value', '1')
            }
        return {'constraint_type': 'minLength', 'value': 1}
    
    def set_constraint_data(self, constraint_data):
        """Set constraint data"""
        if constraint_data:
            constraint_type = constraint_data.get('constraint_type', 'minLength')
            constraint_value = constraint_data.get('value', '1')
            
            # Find and select the constraint type
            for i in range(self.constraint_type_combo.count()):
                if self.constraint_type_combo.itemText(i) == constraint_type:
                    self.constraint_type_combo.setCurrentIndex(i)
                    break
            
            self.value_edit.setText(str(constraint_value))

class PropertyEditorDialog(QDialog):
    """Property editor dialog for creating/editing properties"""
    
    def __init__(self, parent=None, ontology_manager=None):
        super().__init__(parent)
        self.ontology_manager = ontology_manager
        self.setWindowTitle("Property Editor")
        self.setGeometry(200, 200, 500, 400)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the property editor UI"""
        layout = QVBoxLayout()
        
        # Property name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Property Name:"))
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter property name...")
        name_layout.addWidget(self.name_edit)
        
        layout.addLayout(name_layout)
        
        # Property path (URI)
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Property Path:"))
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Enter property URI or browse...")
        path_layout.addWidget(self.path_edit)
        
        self.browse_path_btn = QPushButton("Browse")
        self.browse_path_btn.clicked.connect(self.browse_property_path)
        path_layout.addWidget(self.browse_path_btn)
        
        layout.addLayout(path_layout)
        
        # Data type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Data Type:"))
        
        self.datatype_combo = QComboBox()
        self.datatype_combo.addItems([
            "xsd:string", "xsd:integer", "xsd:decimal", "xsd:boolean",
            "xsd:date", "xsd:dateTime", "xsd:time", "xsd:anyURI"
        ])
        self.datatype_combo.setEditable(True)
        type_layout.addWidget(self.datatype_combo)
        
        layout.addLayout(type_layout)
        
        # Description
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter property description...")
        self.description_edit.setMaximumHeight(80)
        desc_layout.addWidget(self.description_edit)
        
        layout.addLayout(desc_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def browse_property_path(self):
        """Browse for property path using ontology browser"""
        if not self.ontology_manager:
            QMessageBox.warning(self, "Warning", "Ontology manager not available")
            return
        
        # Create and show ontology browser in properties mode
        dialog = SimpleOntologyBrowser(self.ontology_manager, self, mode="properties")
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_item = dialog.selected_item
            if selected_item and 'uri' in selected_item:
                self.path_edit.setText(selected_item['uri'])
                if not self.name_edit.text().strip():
                    # Auto-fill name from URI if name is empty
                    name = selected_item.get('name', '')
                    if name:
                        self.name_edit.setText(name)
    
    def get_property_data(self):
        """Get property data from dialog"""
        name = self.name_edit.text().strip()
        path = self.path_edit.text().strip()
        datatype = self.datatype_combo.currentText().strip()
        description = self.description_edit.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a property name")
            return None
        
        if not path:
            QMessageBox.warning(self, "Warning", "Please enter a property path")
            return None
        
        return {
            'name': name,
            'path': path,
            'datatype': datatype if datatype else 'xsd:string',
            'description': description,
            'constraints': []
        }
    
    def set_property_data(self, property_data):
        """Set property data in dialog"""
        if not property_data:
            return
        
        self.name_edit.setText(property_data.get('name', ''))
        self.path_edit.setText(property_data.get('path', property_data.get('uri', '')))
        
        datatype = property_data.get('datatype', 'xsd:string')
        # Find datatype in combo or add it
        index = self.datatype_combo.findText(datatype)
        if index >= 0:
            self.datatype_combo.setCurrentIndex(index)
        else:
            self.datatype_combo.setCurrentText(datatype)
        
        self.description_edit.setPlainText(property_data.get('description', ''))


# UIStateController is now in stateful_gui.py to avoid duplication
