import sys
import re
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QMessageBox, QListWidgetItem,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QGroupBox, QWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.uic import loadUi

# Add brick_app_v2 directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

# Import from core directory
sys.path.insert(0, str(app_dir / 'core'))

from core.brick_core_simple import BrickCore, SHACLBrick
from core.ontology_manager import OntologyManager


def load_pattern_presets():
    """Load pattern presets from shared_libraries/pattern_presets.json"""
    try:
        from common import shared_library_manager
        presets_file = shared_library_manager.base_path / "pattern_presets.json"
        
        if presets_file.exists():
            with open(presets_file, 'r') as f:
                data = json.load(f)
            
            # Extract patterns from international section
            patterns = []
            if "presets" in data and "international" in data["presets"]:
                patterns = data["presets"]["international"].get("patterns", [])
            
            return [{"id": p["id"], "name": p["name"], "pattern": p["pattern"], "example": p.get("example", "")} for p in patterns]
    except Exception as e:
        print(f"Error loading pattern presets: {e}")
    
    # Return default presets if file can't be loaded
    return [
        {"id": "email", "name": "Email Address", "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", "example": "user@example.com"},
        {"id": "phone_e164", "name": "Phone (E.164 International)", "pattern": "^\\+[1-9]\\d{1,14}$", "example": "+12345678901"},
        {"id": "url", "name": "URL/Website", "pattern": "^https?://.+\\..+", "example": "https://example.com"},
        {"id": "postal_generic", "name": "Postal Code (Generic)", "pattern": "^[A-Z0-9\\s-]{3,10}$", "example": "12345, NW1 6XE"},
        {"id": "iso_date", "name": "Date (ISO 8601)", "pattern": "^\\d{4}-\\d{2}-\\d{2}$", "example": "2026-05-18"},
        {"id": "uuid", "name": "UUID", "pattern": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", "example": "550e8400-e29b-41d4-a716-446655440000"},
        {"id": "ipv4", "name": "IP Address (IPv4)", "pattern": "^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", "example": "192.168.1.1"}
    ]
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
        self.pattern_presets = load_pattern_presets()
        
        # Load UI from file
        ui_path = Path(__file__).parent / "ui" / "constraint_editor.ui"
        loadUi(str(ui_path), self)
        
        # Populate pattern preset combo if it exists
        self._populate_pattern_presets()
        
        # Connect signals
        self.constraintTypeCombo.currentTextChanged.connect(self.on_constraint_type_changed)
        if hasattr(self, 'patternPresetCombo'):
            self.patternPresetCombo.currentIndexChanged.connect(self.on_pattern_preset_changed)
        self.okButton.clicked.connect(self.on_accept_clicked)
        self.cancelButton.clicked.connect(self.reject)
        
        # Initialize visibility
        self.on_constraint_type_changed()
    
    def _populate_pattern_presets(self):
        """Populate pattern preset combo box from loaded presets"""
        if hasattr(self, 'patternPresetCombo'):
            self.patternPresetCombo.clear()
            # Add "Custom Pattern..." first
            self.patternPresetCombo.addItem("Custom Pattern...", "")
            # Add presets from JSON
            for preset in self.pattern_presets:
                display_text = f"{preset['name']}"
                if preset.get('example'):
                    display_text += f" (e.g., {preset['example']})"
                self.patternPresetCombo.addItem(display_text, preset['pattern'])
    
    def on_pattern_preset_changed(self, index):
        """Handle pattern preset selection"""
        if hasattr(self, 'patternPresetCombo') and hasattr(self, 'patternValueEdit'):
            pattern = self.patternPresetCombo.currentData()
            if pattern:  # Not the "Custom" option
                self.patternValueEdit.setText(pattern)
    
    def on_constraint_type_changed(self):
        """Show/hide pattern preset combo based on constraint type"""
        is_pattern = self.constraintTypeCombo.currentText() == "pattern"
        if hasattr(self, 'patternPresetCombo'):
            self.patternPresetCombo.setVisible(is_pattern)
        if hasattr(self, 'patternPresetLabel'):
            self.patternPresetLabel.setVisible(is_pattern)

_STRING_TYPES  = {"xsd:string", "xsd:anyURI", "rdf:HTML", "rdf:langString"}
_LANG_TYPES    = {"rdf:langString"}
_BOUNDS_TYPES  = {"xsd:integer", "xsd:decimal", "xsd:float", "xsd:date", "xsd:dateTime"}

DEFAULT_NAMESPACE = "http://example.org/shaclbuild#"


class PropertyEditorDialog(QDialog):
    """Property editor dialog - loads from property_editor.ui"""

    def __init__(self, parent=None, property_data=None, ontology_manager=None):
        super().__init__(parent)
        self.property_data = property_data or {}
        self.ontology_manager = ontology_manager

        ui_path = Path(__file__).parent / "ui" / "property_editor.ui"
        loadUi(str(ui_path), self)

        # Connect signals
        self.datatype_combo.currentTextChanged.connect(self._update_group_visibility)
        self.use_custom_namespace.toggled.connect(self._on_namespace_toggled)
        self.browse_btn.clicked.connect(self._browse_ontology)
        self.generate_iri_btn.clicked.connect(self._generate_iri)
        self.browse_class_btn.clicked.connect(self._browse_class)
        self.clear_class_btn.clicked.connect(self._clear_class)
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        # Enrichment area — injected dynamically below sh_class field
        self._enrichment_widget = None
        self._enrichment_timer = QTimer(self)
        self._enrichment_timer.setSingleShot(True)
        self._enrichment_timer.timeout.connect(self._run_enrichment)
        self.sh_class_edit.textChanged.connect(self._on_sh_class_changed)

        # Populate fields if editing
        if property_data and property_data.get('name'):
            self.setWindowTitle(f"Edit Property: {property_data['name']}")
            self._populate_fields(property_data)
        else:
            self.setWindowTitle("Add Property")

        # Initial group visibility + enrichment
        self._update_group_visibility()
        self._run_enrichment()

    # ── visibility ──────────────────────────────────────────────────────────

    def _update_group_visibility(self):
        dt = self.datatype_combo.currentText()
        self.stringConstraintsGroup.setVisible(dt in _STRING_TYPES)
        self.langConstraintsGroup.setVisible(dt in _LANG_TYPES)
        self.boundsConstraintsGroup.setVisible(dt in _BOUNDS_TYPES)
        self.adjustSize()

    def _on_namespace_toggled(self, checked):
        self.namespaceLabel.setEnabled(checked)
        self.namespace_edit.setEnabled(checked)

    # ── slot helpers ─────────────────────────────────────────────────────────

    def _browse_ontology(self):
        if not self.ontology_manager:
            QMessageBox.warning(self, "Error", "Ontology manager not available")
            return
        browser = SimpleOntologyBrowser(self.ontology_manager, self, mode="properties")
        if browser.exec() == QDialog.DialogCode.Accepted and browser.selected_item:
            item = browser.selected_item
            uri = item.get('uri', item) if isinstance(item, dict) else item
            self.path_edit.setText(uri)
            if not self.name_edit.text().strip():
                label = item.get('name', '') if isinstance(item, dict) else ''
                if not label:
                    label = uri.split('#')[-1].split('/')[-1]
                self.name_edit.setText(label)

    def _browse_class(self):
        """Browse for ontology class (sh:class)"""
        if not self.ontology_manager:
            QMessageBox.warning(self, "Error", "Ontology manager not available")
            return
        browser = SimpleOntologyBrowser(self.ontology_manager, self, mode="classes")
        if browser.exec() == QDialog.DialogCode.Accepted and browser.selected_item:
            item = browser.selected_item
            uri = item.get('uri', item) if isinstance(item, dict) else item
            self.sh_class_edit.setText(uri)

    def _clear_class(self):
        """Clear the semantic class field"""
        self.sh_class_edit.clear()

    def _on_sh_class_changed(self, text):
        """Debounce: wait 400 ms after typing stops before querying enrichment"""
        self._enrichment_timer.start(400)

    def _run_enrichment(self):
        """Query EnrichmentEngine and update the dynamic enrichment widget."""
        self._clear_enrichment_widget()
        class_iri = self.sh_class_edit.text().strip()
        if not class_iri:
            return
        try:
            from core.enrichment_engine import EnrichmentEngine
            engine = EnrichmentEngine(self.ontology_manager)
            ctx = engine.enrich(class_iri)
            if ctx.widget == "unit_dropdown" and ctx.enrichments.get("has_units"):
                self._show_unit_dropdown(ctx)
            elif ctx.widget == "property_suggestions" and ctx.enrichments.get("has_suggestions"):
                self._show_property_suggestions(ctx)
        except Exception as e:
            print(f"Enrichment error: {e}")

    def _clear_enrichment_widget(self):
        if self._enrichment_widget is not None:
            self._enrichment_widget.setParent(None)
            self._enrichment_widget.deleteLater()
            self._enrichment_widget = None

    def _find_sh_class_container(self):
        """Return the parent layout to insert enrichment widget after sh_class row."""
        return self.sh_class_edit.parentWidget().layout() if self.sh_class_edit.parentWidget() else None

    def _show_unit_dropdown(self, ctx):
        """Add a unit selector QGroupBox below the sh_class field."""
        units = ctx.enrichments.get("applicable_units", [])
        unit_labels = ctx.enrichments.get("unit_labels", {})
        si_unit = ctx.enrichments.get("si_unit", "")
        qty_kind = ctx.enrichments.get("quantity_kind", "") or ctx.label

        group = QGroupBox(f"{qty_kind} — Unit  (via {ctx.resolution})")
        layout = QHBoxLayout(group)
        combo = QComboBox()
        combo.addItem(f"(SI default: {unit_labels.get(si_unit, si_unit)})", "")
        for u in units:
            lbl = unit_labels.get(u, u.split("/")[-1])
            combo.addItem(f"{lbl}  —  {u}", u)
        combo.currentIndexChanged.connect(
            lambda _: self.setProperty("selected_unit", combo.currentData())
        )
        layout.addWidget(combo)
        self._enrichment_widget = group
        # Insert into dialog's main layout
        main_layout = self.layout()
        if main_layout:
            idx = main_layout.count() - 1  # before OK/Cancel row
            main_layout.insertWidget(idx, group)
        self.adjustSize()

    def _show_property_suggestions(self, ctx):
        """Add property suggestion buttons below the sh_class field."""
        props = ctx.enrichments.get("suggested_properties", [])
        if not props:
            return
        group = QGroupBox(f"Suggested properties for {ctx.label}  (via {ctx.resolution})")
        layout = QHBoxLayout(group)
        layout.setSpacing(4)
        for prop in props[:8]:
            btn = QPushButton(prop)
            btn.setToolTip(f"Set property path to: {prop}")
            btn.clicked.connect(lambda checked, p=prop: self.path_edit.setText(p))
            layout.addWidget(btn)
        layout.addStretch()
        self._enrichment_widget = group
        main_layout = self.layout()
        if main_layout:
            idx = main_layout.count() - 1
            main_layout.insertWidget(idx, group)
        self.adjustSize()

    def _generate_iri(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a property name first")
            return
        ns = self.namespace_edit.text().strip() if self.use_custom_namespace.isChecked() else DEFAULT_NAMESPACE
        fragment = re.sub(r'[^\w]', '_', name).strip('_')
        self.path_edit.setText(f"{ns}{fragment}")

    # ── populate / read ──────────────────────────────────────────────────────

    def _populate_fields(self, data):
        self.name_edit.setText(data.get('name', '') or data.get('label', ''))
        self.path_edit.setText(data.get('path', '') or data.get('property_path', ''))

        dt = data.get('datatype', 'xsd:string') or 'xsd:string'
        idx = self.datatype_combo.findText(dt)
        if idx >= 0:
            self.datatype_combo.setCurrentIndex(idx)

        def _set(widget, key, cast=str):
            v = data.get(key)
            if v not in (None, ''):
                widget.setText(cast(v))

        _set(self.min_count_edit,     'min_count')
        _set(self.max_count_edit,     'max_count')
        _set(self.min_length_edit,    'min_length')
        _set(self.max_length_edit,    'max_length')
        _set(self.pattern_edit,       'pattern')
        _set(self.language_in_edit,   'language_in')
        _set(self.min_inclusive_edit, 'min_inclusive')
        _set(self.max_inclusive_edit, 'max_inclusive')
        _set(self.min_exclusive_edit, 'min_exclusive')
        _set(self.max_exclusive_edit, 'max_exclusive')
        _set(self.has_value_edit,     'has_value')

        in_vals = data.get('in_values', [])
        if isinstance(in_vals, list):
            self.in_values_edit.setText(', '.join(f'"{v}"' for v in in_vals))
        elif in_vals:
            self.in_values_edit.setText(str(in_vals))

        self.unique_lang_check.setChecked(bool(data.get('unique_lang', False)))
        self.description_edit.setPlainText(data.get('description', ''))
        self.sh_class_edit.setText(data.get('sh_class', ''))

    def get_property_data(self):
        """Return a LeafProperty-compatible dict with all filled fields."""
        name = self.name_edit.text().strip()
        data = {
            'name':          name,
            'label':         name,
            'path':          self.path_edit.text().strip(),
            'datatype':      self.datatype_combo.currentText(),
            'description':   self.description_edit.toPlainText().strip(),
            'sh_class':      self.sh_class_edit.text().strip(),
        }

        def _int(widget):
            t = widget.text().strip()
            return int(t) if t else None

        def _float_or_str(widget):
            t = widget.text().strip()
            return t if t else None

        data['min_count'] = _int(self.min_count_edit)
        data['max_count'] = _int(self.max_count_edit)

        if self.stringConstraintsGroup.isVisible():
            data['min_length'] = _int(self.min_length_edit)
            data['max_length'] = _int(self.max_length_edit)
            p = self.pattern_edit.text().strip()
            if p:
                data['pattern'] = p

        if self.langConstraintsGroup.isVisible():
            li = self.language_in_edit.text().strip()
            if li:
                data['language_in'] = li
            data['unique_lang'] = self.unique_lang_check.isChecked()

        if self.boundsConstraintsGroup.isVisible():
            data['min_inclusive'] = _float_or_str(self.min_inclusive_edit)
            data['max_inclusive'] = _float_or_str(self.max_inclusive_edit)
            data['min_exclusive'] = _float_or_str(self.min_exclusive_edit)
            data['max_exclusive'] = _float_or_str(self.max_exclusive_edit)

        in_raw = self.in_values_edit.text().strip()
        if in_raw:
            data['in_values'] = [v.strip().strip('"') for v in in_raw.split(',') if v.strip()]

        hv = self.has_value_edit.text().strip()
        if hv:
            data['has_value'] = hv

        # Remove None values to keep dict clean
        return {k: v for k, v in data.items() if v is not None and v != ''}


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
