import sys
import re
from pathlib import Path
from PyQt6.QtWidgets import QDialog, QMessageBox, QListWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi

# Add brick_app_v2 directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

# Import from core directory
sys.path.insert(0, str(app_dir / 'core'))

from core.brick_core_simple import BrickCore, SHACLBrick
from core.ontology_manager import OntologyManager
class SimpleOntologyBrowser(QDialog):
    """Ontology browser - loads from ontology_browser_simple.ui"""
    
    def __init__(self, ontology_manager, parent=None, mode="classes"):
        super().__init__(parent)
        self.ontology_manager = ontology_manager
        self.mode = mode  # "classes" or "properties"
        self.selected_item = None
        self.all_items = []
        
        # Load UI from file
        ui_path = Path(__file__).parent / "ui" / "ontology_browser_simple.ui"
        loadUi(str(ui_path), self)
        
        # Set mode combo
        mode_index = 0 if mode == "classes" else 1
        self.mode_combo.setCurrentIndex(mode_index)
        
        # Connect signals
        self.ontology_combo.currentTextChanged.connect(self.on_ontology_changed)
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        self.search_edit.textChanged.connect(self.on_search_changed)
        self.search_all_check.stateChanged.connect(self.on_search_all_toggled)
        self.results_list.itemDoubleClicked.connect(self.on_item_selected)
        self.cancelButton.clicked.connect(self.reject)
        
        # Load data
        self.load_ontology_data()


class PropertyBrickBrowser(QDialog):
    """Property brick browser - loads from property_brick_browser.ui"""
    
    def __init__(self, parent=None, brick_core=None):
        super().__init__(parent)
        self.brick_core = brick_core
        self.selected_item = None
        self.all_items = []
        
        # Load UI from file
        ui_path = Path(__file__).parent / "ui" / "property_brick_browser.ui"
        loadUi(str(ui_path), self)
        
        # Connect signals
        self.library_combo.currentTextChanged.connect(self.on_library_changed)
        self.filter_check.stateChanged.connect(self.apply_search_filter)
        self.search_edit.textChanged.connect(self.apply_search_filter)
        self.brick_list.itemDoubleClicked.connect(self.on_item_selected)
        self.selectButton.clicked.connect(self.on_select_clicked)
        self.cancelButton.clicked.connect(self.reject)
        
        # Load data
        self.load_brick_data()


class ConstraintEditorDialog(QDialog):
    """Constraint editor - loads from constraint_editor.ui"""
    
    def __init__(self, parent=None, prop_data=None):
        super().__init__(parent)
        self.prop_data = prop_data or {}
        self.selected_item = None
        
        # Load UI from file
        ui_path = Path(__file__).parent / "ui" / "constraint_editor.ui"
        loadUi(str(ui_path), self)
        
        # Connect signals
        self.constraintTypeCombo.currentTextChanged.connect(self.on_constraint_type_changed)
        self.okButton.clicked.connect(self.on_accept_clicked)
        self.cancelButton.clicked.connect(self.reject)
        
        # Initialize visibility
        self.on_constraint_type_changed()

class PropertyEditorDialog(QDialog):
    """Property editor dialog - loads from property_editor.ui"""
    pass


# Business logic methods for SimpleOntologyBrowser
def load_ontology_data(self):
    """Load ontology list"""
    ontologies = self.ontology_manager.ontologies
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

SimpleOntologyBrowser.load_ontology_data = load_ontology_data


def load_ontology_items(self):
    """Load ontology classes or properties"""
    if self.ontology_combo.currentIndex() < 0:
        return
    
    ontology_name = self.ontology_combo.currentData()
    if not ontology_name or ontology_name not in self.ontology_manager.ontologies:
        return
    
    ontology_data = self.ontology_manager.ontologies[ontology_name]
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

SimpleOntologyBrowser.load_ontology_items = load_ontology_items


def on_ontology_changed(self):
    """Handle ontology selection change"""
    self.load_ontology_items()

SimpleOntologyBrowser.on_ontology_changed = on_ontology_changed


def on_mode_changed(self):
    """Handle mode change"""
    self.load_ontology_items()

SimpleOntologyBrowser.on_mode_changed = on_mode_changed


def on_search_changed(self):
    """Handle search text change"""
    self.apply_search_filter()

SimpleOntologyBrowser.on_search_changed = on_search_changed


def on_search_all_toggled(self):
    """Handle 'Search all ontologies' checkbox toggle"""
    search_all = self.search_all_check.isChecked()
    self.ontology_combo.setEnabled(not search_all)
    if search_all:
        self.apply_search_filter()
    else:
        self.load_ontology_items()

SimpleOntologyBrowser.on_search_all_toggled = on_search_all_toggled


def apply_search_filter(self):
    """Apply search filter to items"""
    search_text = self.search_edit.text().lower().strip()
    search_all = self.search_all_check.isChecked()

    self.results_list.clear()

    if search_all and search_text:
        mode = self.mode_combo.currentText().lower()
        match_count = 0
        for ont_name, ont_data in sorted(self.ontology_manager.ontologies.items(), key=lambda x: x[0].lower()):
            if mode == "classes":
                items_dict = ont_data.get('classes', {})
            else:
                items_dict = ont_data.get('properties', {})

            ont_matches = []
            for uri, data in items_dict.items():
                if isinstance(data, dict) and 'name' in data:
                    item = {'name': data['name'], 'uri': uri,
                            'description': data.get('description', ''),
                            'comment': data.get('comment', ''),
                            'ontology': ont_name}
                else:
                    item = {'name': str(data), 'uri': uri,
                            'description': '', 'comment': '', 'ontology': ont_name}

                if search_text in item['name'].lower() or search_text in uri.lower():
                    ont_matches.append(item)

            if ont_matches:
                ont_matches.sort(key=lambda x: x['name'].lower())
                header_item = QListWidgetItem(f"── {ont_name} ({len(ont_matches)}) ──")
                header_item.setFlags(Qt.ItemFlag.NoItemFlags)
                header_item.setForeground(self.palette().mid())
                self.results_list.addItem(header_item)
                for item in ont_matches:
                    display_text = f"  {item['name']}  [{item['uri']}]"
                    list_item = QListWidgetItem(display_text)
                    list_item.setData(Qt.ItemDataRole.UserRole, item)
                    self.results_list.addItem(list_item)
                    match_count += 1

        self.match_count_label.setText(f"{match_count} match{'es' if match_count != 1 else ''} across all ontologies" if match_count else "No matches found")
    else:
        for item in self.all_items:
            name_match = search_text == "" or search_text in item['name'].lower() or search_text in item['uri'].lower()
            if name_match:
                display_text = item['name']
                list_item = QListWidgetItem(display_text)
                list_item.setData(Qt.ItemDataRole.UserRole, item)
                self.results_list.addItem(list_item)
        count = self.results_list.count()
        self.match_count_label.setText(f"{count} match{'es' if count != 1 else ''}" if search_text else "")

SimpleOntologyBrowser.apply_search_filter = apply_search_filter


def on_item_selected(self, item):
    """Handle item double-click"""
    data = item.data(Qt.ItemDataRole.UserRole)
    if data is None:
        return
    self.selected_item = data
    self.accept()

SimpleOntologyBrowser.on_item_selected = on_item_selected


# Business logic methods for PropertyBrickBrowser
def load_brick_data(self):
    """Load brick data"""
    libraries = self.brick_core.get_libraries()
    self.library_combo.clear()
    
    for library in libraries:
        self.library_combo.addItem(library)
    
    if self.library_combo.count() > 0:
        self.load_brick_items()

PropertyBrickBrowser.load_brick_data = load_brick_data


def load_brick_items(self):
    """Load property bricks from selected library"""
    library_name = self.library_combo.currentText()
    if not library_name:
        return
    
    # Get all bricks and filter for PropertyShape
    bricks = self.brick_core.get_all_bricks()
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

PropertyBrickBrowser.load_brick_items = load_brick_items


def on_library_changed(self):
    """Handle library selection change"""
    self.load_brick_items()

PropertyBrickBrowser.on_library_changed = on_library_changed


def apply_search_filter(self):
    """Apply search filter to items"""
    search_text = self.search_edit.text().lower().strip()
    
    self.brick_list.clear()
    
    for item in self.all_items:
        # Filter by search text
        name_match = search_text == "" or search_text in item['name'].lower()
        
        # Additional filtering for bricks
        if self.filter_check.isChecked():
            type_match = item.get('object_type') == 'PropertyShape'
            if not type_match:
                continue
        
        if name_match:
            type_info = f" ({item.get('object_type', 'Unknown')})"
            display_text = f"{item['name']}{type_info}"
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self.brick_list.addItem(list_item)

PropertyBrickBrowser.apply_search_filter = apply_search_filter


def on_item_selected(self, item):
    """Handle item double-click"""
    self.selected_item = item.data(Qt.ItemDataRole.UserRole)
    self.accept()

PropertyBrickBrowser.on_item_selected = on_item_selected


def on_select_clicked(self):
    """Handle select button click"""
    current_item = self.brick_list.currentItem()
    if current_item:
        self.selected_item = current_item.data(Qt.ItemDataRole.UserRole)
        self.accept()

PropertyBrickBrowser.on_select_clicked = on_select_clicked


# Business logic methods for ConstraintEditorDialog
def on_constraint_type_changed(self):
    """Handle constraint type change"""
    constraint_type = self.constraintTypeCombo.currentText()
    
    # Hide all value widgets first
    self.numericValueWidget.setVisible(False)
    self.patternValueWidget.setVisible(False)
    self.datatypeValueWidget.setVisible(False)
    self.listValueWidget.setVisible(False)
    
    # Show appropriate widget based on constraint type
    if constraint_type in ["minCount", "maxCount", "minLength", "maxLength"]:
        self.numericValueWidget.setVisible(True)
        self.numericValueLabel.setText("Value:" if "Count" in constraint_type else "Length:")
        self.helpTextLabel.setText(f"Enter {'minimum' if 'min' in constraint_type else 'maximum'} {constraint_type.split('Count')[0].split('Length')[0].lower()} value")
    elif constraint_type == "pattern":
        self.patternValueWidget.setVisible(True)
        self.helpTextLabel.setText("Enter a regular expression pattern (e.g., [A-Za-z]+)")
    elif constraint_type == "datatype":
        self.datatypeValueWidget.setVisible(True)
        self.helpTextLabel.setText("Select an XML Schema datatype")
    elif constraint_type in ["in", "notIn"]:
        self.listValueWidget.setVisible(True)
        self.listValueLabel.setText("Allowed values:" if constraint_type == "in" else "Forbidden values:")
        self.helpTextLabel.setText(f"Add {'allowed' if constraint_type == 'in' else 'forbidden'} values to the list")

ConstraintEditorDialog.on_constraint_type_changed = on_constraint_type_changed


def on_accept_clicked(self):
    """Handle OK button click"""
    constraint_type = self.constraintTypeCombo.currentText()
    
    # Get value based on which widget is visible
    if self.numericValueWidget.isVisible():
        value = str(self.numericValueSpinBox.value())
    elif self.patternValueWidget.isVisible():
        value = self.patternValueEdit.toPlainText().strip()
    elif self.datatypeValueWidget.isVisible():
        value = self.datatypeCombo.currentText()
    elif self.listValueWidget.isVisible():
        values = []
        for i in range(self.valueListWidget.count()):
            values.append(self.valueListWidget.item(i).text())
        value = ",".join(values)
    else:
        value = ""
    
    if not value:
        QMessageBox.warning(self, "Warning", "Please enter a constraint value")
        return
    
    self.selected_item = {
        'constraint_type': constraint_type,
        'value': value,
        'name': constraint_type
    }
    
    self.accept()

ConstraintEditorDialog.on_accept_clicked = on_accept_clicked


def get_constraint_data(self):
    """Get constraint data"""
    if self.selected_item:
        return {
            'constraint_type': self.selected_item.get('constraint_type', 'minLength'),
            'value': self.selected_item.get('value', '1')
        }
    return {'constraint_type': 'minLength', 'value': 1}

ConstraintEditorDialog.get_constraint_data = get_constraint_data


def set_constraint_data(self, constraint_data):
    """Set constraint data"""
    if constraint_data:
        constraint_type = constraint_data.get('constraint_type', 'minLength')
        constraint_value = constraint_data.get('value', '1')
        
        # Find and select the constraint type
        found = False
        for i in range(self.constraintTypeCombo.count()):
            if self.constraintTypeCombo.itemText(i) == constraint_type:
                self.constraintTypeCombo.setCurrentIndex(i)
                found = True
                break
        
        # Update widget visibility based on constraint type
        self.on_constraint_type_changed()
        
        # Set value based on which widget should be visible
        if found:
            if constraint_type in ["minCount", "maxCount", "minLength", "maxLength"]:
                self.numericValueSpinBox.setValue(int(constraint_value))
            elif constraint_type == "pattern":
                self.patternValueEdit.setPlainText(str(constraint_value))
            elif constraint_type == "datatype":
                self.datatypeCombo.setCurrentText(str(constraint_value))
            elif constraint_type in ["in", "notIn"]:
                self.valueListWidget.clear()
                for val in str(constraint_value).split(','):
                    if val.strip():
                        self.valueListWidget.addItem(val.strip())

ConstraintEditorDialog.set_constraint_data = set_constraint_data


# Business logic methods for PropertyEditorDialog
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

PropertyEditorDialog.browse_property_path = browse_property_path


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

PropertyEditorDialog.get_property_data = get_property_data


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

PropertyEditorDialog.set_property_data = set_property_data


# PropertyEditorDialog __init__ and additional methods
DEFAULT_NAMESPACE = "http://example.org/shaclbuild#"

def property_editor_init(self, parent=None, ontology_manager=None):
    """Initialize property editor dialog"""
    super(PropertyEditorDialog, self).__init__(parent)
    self.ontology_manager = ontology_manager
    
    # Load UI from file
    ui_path = Path(__file__).parent / "ui" / "property_editor.ui"
    loadUi(str(ui_path), self)
    
    # Make datatype combo editable
    self.datatype_combo.setEditable(True)
    
    # Add missing datatypes if not present
    datatypes = ["xsd:string", "xsd:integer", "xsd:decimal", "xsd:boolean",
                "xsd:date", "xsd:dateTime", "xsd:time", "xsd:anyURI"]
    for dt in datatypes:
        if self.datatype_combo.findText(dt) == -1:
            self.datatype_combo.addItem(dt)
    
    # Set default namespace if field is empty
    if hasattr(self, 'namespace_edit') and not self.namespace_edit.text().strip():
        self.namespace_edit.setText(DEFAULT_NAMESPACE)
    
    # Connect signals
    self.browse_btn.clicked.connect(self.browse_property_path)
    self.okButton.clicked.connect(self.accept)
    self.cancelButton.clicked.connect(self.reject)
    
    # Connect new custom IRI generation signals
    if hasattr(self, 'generate_iri_btn'):
        self.generate_iri_btn.clicked.connect(self.generate_custom_iri)
    if hasattr(self, 'use_custom_namespace'):
        self.use_custom_namespace.stateChanged.connect(self.on_custom_namespace_toggled)

PropertyEditorDialog.__init__ = property_editor_init


def on_custom_namespace_toggled(self, state):
    """Enable/disable namespace field based on checkbox"""
    if hasattr(self, 'namespace_edit') and hasattr(self, 'namespaceLabel'):
        enabled = state == Qt.CheckState.Checked.value
        self.namespace_edit.setEnabled(enabled)
        self.namespaceLabel.setEnabled(enabled)

PropertyEditorDialog.on_custom_namespace_toggled = on_custom_namespace_toggled


def generate_custom_iri(self):
    """Generate a custom IRI from the property name and namespace"""
    name = self.name_edit.text().strip()
    if not name:
        QMessageBox.warning(self, "Warning", "Please enter a property name first")
        return
    
    # Get namespace - use custom if enabled, otherwise default
    if hasattr(self, 'use_custom_namespace') and self.use_custom_namespace.isChecked() and hasattr(self, 'namespace_edit'):
        namespace = self.namespace_edit.text().strip()
    else:
        namespace = DEFAULT_NAMESPACE
    
    if not namespace:
        namespace = DEFAULT_NAMESPACE
        if hasattr(self, 'namespace_edit'):
            self.namespace_edit.setText(namespace)
    
    # Ensure namespace ends with # or /
    if not namespace.endswith(('#', '/')):
        namespace += '#'
    
    # Convert property name to valid IRI fragment (camelCase)
    # Remove invalid characters and convert to camelCase
    iri_fragment = self._name_to_iri_fragment(name)
    
    # Generate full IRI
    full_iri = f"{namespace}{iri_fragment}"
    self.path_edit.setText(full_iri)

PropertyEditorDialog.generate_custom_iri = generate_custom_iri


def _name_to_iri_fragment(self, name: str) -> str:
    """Convert a property name to a valid IRI fragment"""
    # Remove or replace invalid characters
    # Keep alphanumeric, spaces, hyphens, and underscores
    cleaned = re.sub(r'[^\w\s-]', '', name)
    
    # Split into words
    words = cleaned.split()
    
    if not words:
        return "property"
    
    # Convert to camelCase (first word lowercase, rest capitalized)
    first_word = words[0].lower()
    rest_words = [word.capitalize() for word in words[1:]]
    
    return first_word + ''.join(rest_words)

PropertyEditorDialog._name_to_iri_fragment = _name_to_iri_fragment
