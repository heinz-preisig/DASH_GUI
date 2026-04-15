#!/usr/bin/env python3
"""
Multi-Tenant SHACL Brick Generator - PyQt Frontend
Updated to use new session-based backend architecture for web compatibility
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
from PyQt6.QtCore import Qt, pyqtSignal

from shacl_brick_app.core.multi_tenant_backend import MultiTenantBackend
from shacl_brick_app.core.abstract_events import EventType


class MultiTenantGuidedGUI(QMainWindow):
    """Multi-tenant brick editor with session-based backend"""
    
    # Qt signals for event handling
    brick_created = pyqtSignal(dict)
    brick_updated = pyqtSignal(dict)
    brick_saved = pyqtSignal(dict)
    property_added = pyqtSignal(str, dict)
    property_removed = pyqtSignal(str)
    constraint_added = pyqtSignal(str, dict)
    constraint_removed = pyqtSignal(str)
    target_class_set = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    status_message = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Tenant SHACL Brick Generator")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize multi-tenant backend
        self.backend = MultiTenantBackend()
        self.qt_session_id = self.backend.get_qt_session().session_id
        
        # Register Qt signals with event manager
        self._register_qt_events()
        
        # Get Qt session backend for direct operations
        self.qt_session = self.backend.get_qt_session()
        self.qt_backend = self.qt_session.editor_backend
        
        # Setup UI
        self.init_ui()
        
        # Load initial data
        self.load_initial_data()
        
        # Create initial brick
        self.create_new_brick()
    
    def _register_qt_events(self):
        """Register Qt signals with the multi-tenant event manager"""
        qt_signals = {
            EventType.BRICK_CREATED: self.brick_created,
            EventType.BRICK_UPDATED: self.brick_updated,
            EventType.BRICK_SAVED: self.brick_saved,
            EventType.PROPERTY_ADDED: self.property_added,
            EventType.PROPERTY_REMOVED: self.property_removed,
            EventType.CONSTRAINT_ADDED: self.constraint_added,
            EventType.CONSTRAINT_REMOVED: self.constraint_removed,
            EventType.TARGET_CLASS_SET: self.target_class_set,
            EventType.ERROR_OCCURRED: self.error_occurred,
            EventType.STATUS_MESSAGE: self.status_message,
        }
        
        self.backend.register_qt_signals(qt_signals)
        
        # Connect Qt signals to UI update methods
        self.brick_created.connect(self._on_brick_created)
        self.brick_updated.connect(self._on_brick_updated)
        self.brick_saved.connect(self._on_brick_saved)
        self.property_added.connect(self._on_property_added)
        self.property_removed.connect(self._on_property_removed)
        self.constraint_added.connect(self._on_constraint_added)
        self.constraint_removed.connect(self._on_constraint_removed)
        self.target_class_set.connect(self._on_target_class_set)
        self.error_occurred.connect(self._on_error_occurred)
        self.status_message.connect(self._on_status_message)
    
    # Qt event handlers
    def _on_brick_created(self, brick_data):
        """Handle brick creation event"""
        self._update_ui_from_brick_data()
        self.statusBar().showMessage("Brick created successfully")
    
    def _on_brick_updated(self, brick_data):
        """Handle brick update event"""
        self._update_ui_from_brick_data()
    
    def _on_brick_saved(self, brick_data):
        """Handle brick save event"""
        self.statusBar().showMessage("Brick saved successfully")
        self.refresh_brick_library()
    
    def _on_property_added(self, prop_name, prop_data):
        """Handle property addition event"""
        self._update_properties_display()
        self.statusBar().showMessage(f"Property '{prop_name}' added")
    
    def _on_property_removed(self, prop_name):
        """Handle property removal event"""
        self._update_properties_display()
        self.statusBar().showMessage(f"Property '{prop_name}' removed")
    
    def _on_constraint_added(self, prop_name, constraint_data):
        """Handle constraint addition event"""
        self.statusBar().showMessage(f"Constraint added to '{prop_name}'")
    
    def _on_constraint_removed(self, prop_name):
        """Handle constraint removal event"""
        self.statusBar().showMessage(f"Constraint removed from '{prop_name}'")
    
    def _on_target_class_set(self, class_uri):
        """Handle target class set event"""
        self.target_class_edit.setText(class_uri)
        self.statusBar().showMessage(f"Target class set: {class_uri}")
    
    def _on_error_occurred(self, error_message):
        """Handle error event"""
        QMessageBox.critical(self, "Error", error_message)
    
    def _on_status_message(self, message):
        """Handle status message event"""
        self.statusBar().showMessage(message)
    
    def _update_ui_from_brick_data(self):
        """Update UI from current brick data"""
        brick_data = self.qt_backend.get_current_brick()
        
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
        brick_data = self.qt_backend.get_current_brick()
        properties = brick_data.get('properties', {})
        
        for prop_name in properties.keys():
            self.properties_list.addItem(prop_name)
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("Multi-Tenant SHACL Brick Generator")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px;")
        layout.addWidget(header)
        
        # Session info
        session_info = QLabel(f"Session ID: {self.qt_session_id}")
        session_info.setStyleSheet("font-size: 12px; color: #666; padding: 5px;")
        layout.addWidget(session_info)
        
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
        self.statusBar().showMessage("Multi-tenant backend ready")
    
    def create_editor_panel(self):
        """Create the editor panel"""
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        # Brick information group
        info_group = QGroupBox("Brick Information")
        info_layout = QFormLayout(info_group)
        
        # Brick name
        self.brick_name_edit = QLineEdit()
        self.brick_name_edit.setPlaceholderText("e.g., Student Registration, Product Catalog")
        self.brick_name_edit.textChanged.connect(self._sync_ui_to_backend)
        info_layout.addRow("Name:", self.brick_name_edit)
        
        # Target class
        target_layout = QHBoxLayout()
        self.target_class_edit = QLineEdit()
        self.target_class_edit.setPlaceholderText("e.g., schema:Student, schema:Product")
        self.target_class_edit.textChanged.connect(self._sync_ui_to_backend)
        target_layout.addWidget(self.target_class_edit)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._request_class_browser)
        target_layout.addWidget(browse_btn)
        info_layout.addRow("Target Class:", target_layout)
        
        # Object type
        self.object_type_combo = QComboBox()
        self.object_type_combo.addItems(["NodeShape", "PropertyShape"])
        self.object_type_combo.currentTextChanged.connect(self._sync_ui_to_backend)
        info_layout.addRow("Object Type:", self.object_type_combo)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Describe what this brick validates...")
        self.description_edit.setMaximumHeight(100)
        self.description_edit.textChanged.connect(self._sync_ui_to_backend)
        info_layout.addRow("Description:", self.description_edit)
        
        editor_layout.addWidget(info_group)
        
        # Properties group
        props_group = QGroupBox("Properties")
        props_layout = QVBoxLayout(props_group)
        
        self.properties_list = QListWidget()
        self.properties_list.setMaximumHeight(200)
        self.properties_list.itemClicked.connect(self.on_property_selected)
        props_layout.addWidget(self.properties_list)
        
        # Property buttons
        prop_buttons_layout = QHBoxLayout()
        
        add_prop_btn = QPushButton("Add Property")
        add_prop_btn.clicked.connect(self._request_add_property)
        prop_buttons_layout.addWidget(add_prop_btn)
        
        remove_prop_btn = QPushButton("Remove Selected")
        remove_prop_btn.clicked.connect(self.remove_property)
        prop_buttons_layout.addWidget(remove_prop_btn)
        
        props_layout.addLayout(prop_buttons_layout)
        editor_layout.addWidget(props_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        new_btn = QPushButton("New Brick")
        new_btn.clicked.connect(self.create_new_brick)
        action_layout.addWidget(new_btn)
        
        save_btn = QPushButton("Save Brick")
        save_btn.clicked.connect(self.save_brick)
        action_layout.addWidget(save_btn)
        
        load_btn = QPushButton("Load Brick")
        load_btn.clicked.connect(self.load_brick)
        action_layout.addWidget(load_btn)
        
        export_btn = QPushButton("Export SHACL")
        export_btn.clicked.connect(self.export_shacl)
        action_layout.addWidget(export_btn)
        
        action_layout.addStretch()
        editor_layout.addLayout(action_layout)
        
        return editor_widget
    
    def create_browser_panel(self):
        """Create the browser panel"""
        browser_widget = QWidget()
        browser_layout = QVBoxLayout(browser_widget)
        
        # Header
        header = QLabel("Brick Library")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background: #e8f5e8; border-radius: 5px;")
        browser_layout.addWidget(header)
        
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
        browser_layout.addLayout(content_layout)
        
        return browser_widget
    
    def _sync_ui_to_backend(self):
        """Sync UI values to backend"""
        # Update backend's current brick
        current_brick = self.qt_backend.get_current_brick()
        if current_brick:
            current_brick["name"] = self.brick_name_edit.text()
            current_brick["target_class"] = self.target_class_edit.text()
            current_brick["description"] = self.description_edit.toPlainText()
            current_brick["object_type"] = self.object_type_combo.currentText()
            
            # Trigger update event
            self.qt_backend.set_current_brick(current_brick)
    
    def create_new_brick(self):
        """Create new brick"""
        self.qt_backend.create_new_brick()
        self._update_ui_from_brick_data()
    
    def save_brick(self):
        """Save current brick"""
        current_brick = self.qt_backend.get_current_brick()
        if current_brick:
            success, message = self.qt_backend.save_brick(current_brick)
            if success:
                self.statusBar().showMessage("Brick saved successfully")
                self.refresh_brick_library()
            else:
                QMessageBox.critical(self, "Save Error", message)
    
    def load_brick(self):
        """Load existing brick"""
        # Show brick selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Load Brick")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        bricks_list = QListWidget()
        layout.addWidget(bricks_list)
        
        # Load available bricks
        result = self.backend.get_all_bricks()
        if result["status"] == "success":
            for brick in result["data"]["bricks"]:
                item = QListWidgetItem(f"{brick['name']} ({brick['object_type']})")
                item.setData(Qt.ItemDataRole.UserRole, brick)
                bricks_list.addItem(item)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            current_item = bricks_list.currentItem()
            if current_item:
                brick_data = current_item.data(Qt.ItemDataRole.UserRole)
                loaded_brick = self.qt_backend.load_brick(brick_data["brick_id"])
                if loaded_brick:
                    self._update_ui_from_brick_data()
                    self.statusBar().showMessage(f"Loaded brick: {brick_data['name']}")
    
    def export_shacl(self):
        """Export current brick to SHACL format"""
        current_brick = self.qt_backend.get_current_brick()
        if not current_brick:
            QMessageBox.warning(self, "No Brick", "Please create or load a brick first")
            return
        
        # Get SHACL content from backend
        result = self.qt_session.brick_api.export_brick_shacl(current_brick["brick_id"])
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
    
    def _request_add_property(self):
        """Request add property dialog"""
        # Simplified property addition
        prop_name = "new_property"
        prop_data = {
            "name": prop_name,
            "path": f"ex:{prop_name}",
            "datatype": "xsd:string",
            "constraints": []
        }
        self.qt_backend.add_property_to_current_brick(prop_data)
    
    def _request_class_browser(self):
        """Request class browser"""
        # Simplified class selection
        class_uri = "schema:Person"
        self.qt_backend.set_target_class(class_uri)
    
    def remove_property(self):
        """Remove selected property"""
        current_item = self.properties_list.currentItem()
        if current_item:
            prop_name = current_item.text()
            self.qt_backend.remove_property_from_current_brick(prop_name)
    
    def on_property_selected(self, item):
        """Handle property selection"""
        prop_name = item.text()
        current_brick = self.qt_backend.get_current_brick()
        if prop_name in current_brick.get("properties", {}):
            prop_data = current_brick["properties"][prop_name]
            self.statusBar().showMessage(f"Selected property: {prop_name}")
    
    def load_initial_data(self):
        """Load initial data"""
        self.refresh_brick_library()
    
    def refresh_brick_library(self):
        """Refresh the brick library"""
        # Refresh libraries list
        result = self.backend.get_brick_libraries()
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
    
    def on_library_selected(self, item):
        """Handle library selection"""
        library_data = item.data(Qt.ItemDataRole.UserRole)
        if not library_data:
            return
        
        library_name = library_data["name"]
        result = self.backend.get_library_bricks(library_name)
        
        if result["status"] == "success":
            self.brick_library_list.clear()
            bricks = result["data"]["bricks"]
            for brick in bricks:
                item = QListWidgetItem(f" {brick["name"]}")
                item.setData(Qt.ItemDataRole.UserRole, brick)
                self.brick_library_list.addItem(item)
            
            self.statusBar().showMessage(f"Library '{library_name}' loaded ({len(bricks)} bricks)")
    
    def on_brick_library_selected(self, item):
        """Handle brick selection from library"""
        brick_data = item.data(Qt.ItemDataRole.UserRole)
        if brick_data:
            # Load brick into backend
            self.qt_backend.set_current_brick(brick_data)
            self._update_ui_from_brick_data()
            self.statusBar().showMessage(f"Brick '{brick_data["name"]}' selected")
    
    def edit_brick_from_library(self, item):
        """Edit brick from library (double-click)"""
        self.on_brick_library_selected(item)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MultiTenantGuidedGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
