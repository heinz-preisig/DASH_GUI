#!/usr/bin/env python3
"""
Library Manager for bricks and schemas
Allows users to create, select, and manage custom libraries
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import Dict, List, Any, Optional
import os
from pathlib import Path
from PyQt6.uic import loadUi

class LibraryManagerDialog(QDialog):
    """Dialog for managing libraries"""
    
    def __init__(self, processor, workflow=None, parent=None):
        super().__init__(parent)
        self.processor = processor
        self.workflow = workflow
        
        # Load UI from file
        ui_path = Path(__file__).parent.parent.parent / "ui" / "library_manager.ui"
        loadUi(str(ui_path), self)
        
        # Set up connections
        self.library_type_combo.currentTextChanged.connect(self.on_library_type_changed)
        self.library_list.itemSelectionChanged.connect(self.on_library_selected)
        self.create_btn.clicked.connect(self.create_library)
        self.set_active_btn.clicked.connect(self.set_active_library)
        self.delete_btn.clicked.connect(self.delete_library)
        self.dialogButtons.accepted.connect(self.accept)
        self.dialogButtons.rejected.connect(self.reject)
        
        self.register_widgets()
        self.load_libraries()
        
        # Update interface based on current workflow state
        if self.workflow:
            self.workflow.interface_manager.update_interface()
    
    def register_widgets(self):
        """Register widgets with workflow state manager"""
        if self.workflow:
            self.workflow.interface_manager.register_widget("library_manager_create", self.create_btn)
            self.workflow.interface_manager.register_widget("library_manager_set_active", self.set_active_btn)
            self.workflow.interface_manager.register_widget("library_manager_delete", self.delete_btn)
    
        
    def on_library_type_changed(self, library_type: str):
        """Handle library type change"""
        self.load_libraries()
    
    def load_libraries(self):
        """Load libraries based on selected type"""
        self.library_list.clear()
        
        if self.library_type_combo.currentText() == "Brick Libraries":
            result = self.processor.process_event({"event": "get_libraries"})
        else:  # Schema Libraries
            result = self.processor.process_event({"event": "get_schema_libraries"})
        
        if result["status"] == "success":
            libraries = result["data"]["libraries"]
            for library in libraries:
                item = QListWidgetItem(f"{library['name']} ({library['brick_count']} items)")
                item.setData(Qt.ItemDataRole.UserRole, library)
                self.library_list.addItem(item)
    
    def on_library_selected(self):
        """Handle library selection"""
        current_item = self.library_list.currentItem()
        if current_item:
            library_data = current_item.data(Qt.ItemDataRole.UserRole)
            self.name_edit.setText(library_data["name"])
            self.description_edit.setPlainText(library_data["description"])
            self.author_edit.setText(library_data.get("author", "Unknown"))
            self.path_edit.setText(library_data.get("path", ""))
        else:
            self.clear_details()
    
    def clear_details(self):
        """Clear library details"""
        self.name_edit.clear()
        self.description_edit.clear()
        self.author_edit.clear()
        self.path_edit.clear()
    
    def create_library(self):
        """Create a new library"""
        dialog = CreateLibraryDialog(self.library_type_combo.currentText(), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            library_info = dialog.get_library_info()
            
            if self.library_type_combo.currentText() == "Brick Libraries":
                result = self.processor.process_event({
                    "event": "create_library",
                    **library_info
                })
            else:  # Schema Libraries
                result = self.processor.process_event({
                    "event": "create_schema_library",
                    **library_info
                })
            
            if result["status"] == "success":
                self.load_libraries()
                QMessageBox.information(self, "Success", f"Library '{library_info['name']}' created successfully")
            else:
                QMessageBox.critical(self, "Error", f"Failed to create library: {result['message']}")
    
    def set_active_library(self):
        """Set selected library as active"""
        current_item = self.library_list.currentItem()
        if current_item:
            library_data = current_item.data(Qt.ItemDataRole.UserRole)
            library_name = library_data["name"]
            
            if self.library_type_combo.currentText() == "Brick Libraries":
                result = self.processor.process_event({
                    "event": "set_active_library",
                    "library_name": library_name
                })
            else:  # Schema Libraries
                result = self.processor.process_event({
                    "event": "set_active_schema_library",
                    "library_name": library_name
                })
            
            if result["status"] == "success":
                QMessageBox.information(self, "Success", f"Library '{library_name}' set as active")
            else:
                QMessageBox.critical(self, "Error", f"Failed to set active library: {result['message']}")
    
    def delete_library(self):
        """Delete selected library"""
        current_item = self.library_list.currentItem()
        if current_item:
            library_data = current_item.data(Qt.ItemDataRole.UserRole)
            library_name = library_data["name"]
            
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Are you sure you want to delete library '{library_name}'?\n\nThis will permanently delete all items in this library.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.library_type_combo.currentText() == "Brick Libraries":
                    result = self.processor.process_event({
                        "event": "delete_library",
                        "library_name": library_name
                    })
                else:  # Schema Libraries
                    result = self.processor.process_event({
                        "event": "delete_schema_library",
                        "library_name": library_name
                    })
                
                if result["status"] == "success":
                    self.load_libraries()
                    self.clear_details()
                    QMessageBox.information(self, "Success", f"Library '{library_name}' deleted successfully")
                else:
                    QMessageBox.critical(self, "Error", f"Failed to delete library: {result['message']}")

class CreateLibraryDialog(QDialog):
    """Dialog for creating a new library"""
    
    def __init__(self, library_type: str, parent=None):
        super().__init__(parent)
        self.library_type = library_type
        self.setWindowTitle(f"Create New {library_type.rstrip('s')}")
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Library information
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter library name...")
        form_layout.addRow("Library Name:", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Enter library description...")
        form_layout.addRow("Description:", self.description_edit)
        
        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Enter author name...")
        self.author_edit.setText("User")
        form_layout.addRow("Author:", self.author_edit)
        
        # Custom path option
        self.custom_path_check = QCheckBox("Use Custom Path")
        self.custom_path_check.toggled.connect(self.on_custom_path_toggled)
        form_layout.addRow(self.custom_path_check)
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Enter custom path...")
        form_layout.addRow("Custom Path:", self.path_edit)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_path)
        form_layout.addRow("", self.browse_btn)
        
        layout.addLayout(form_layout)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept_dialog)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def on_custom_path_toggled(self, checked: bool):
        """Handle custom path checkbox toggle"""
        # State-based control will handle visibility/enable state
        pass
    
    def browse_path(self):
        """Browse for custom path"""
        path = QFileDialog.getExistingDirectory(self, "Select Library Directory")
        if path:
            self.path_edit.setText(path)
    
    def get_library_info(self) -> Dict[str, Any]:
        """Get library information from form"""
        return {
            "name": self.name_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
            "author": self.author_edit.text().strip(),
            "custom_path": self.path_edit.text().strip() if self.custom_path_check.isChecked() else None
        }
    
    def accept_dialog(self):
        """Validate and accept dialog"""
        name = self.name_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter a library name")
            return
        
        if not description:
            QMessageBox.warning(self, "Validation Error", "Please enter a library description")
            return
        
        # Validate library name (no special characters)
        if not name.replace("_", "").replace("-", "").isalnum():
            QMessageBox.warning(self, "Validation Error", "Library name can only contain letters, numbers, underscores, and hyphens")
            return
        
        self.accept()

class SaveLoadManager:
    """Utility class for save/load operations"""
    
    @staticmethod
    def save_brick_to_library(processor, brick_data: Dict[str, Any], library_name: str = None):
        """Save brick to specified library"""
        event_data = {
            "event": "save_brick",
            "brick_data": brick_data
        }
        
        if library_name:
            event_data["library_name"] = library_name
        
        return processor.process_event(event_data)
    
    @staticmethod
    def load_brick_from_library(processor, brick_id: str, library_name: str = None):
        """Load brick from specified library"""
        event_data = {
            "event": "get_brick_details",
            "brick_id": brick_id
        }
        
        if library_name:
            event_data["library_name"] = library_name
        
        return processor.process_event(event_data)
    
    @staticmethod
    def save_schema_to_library(processor, schema_data: Dict[str, Any], library_name: str = None):
        """Save schema to specified library"""
        event_data = {
            "event": "save_schema",
            "schema_data": schema_data
        }
        
        if library_name:
            event_data["library_name"] = library_name
        
        return processor.process_event(event_data)
    
    @staticmethod
    def load_schema_from_library(processor, schema_id: str, library_name: str = None):
        """Load schema from specified library"""
        event_data = {
            "event": "get_schema",
            "schema_id": schema_id
        }
        
        if library_name:
            event_data["library_name"] = library_name
        
        return processor.process_event(event_data)
    
    @staticmethod
    def export_library(processor, library_name: str, export_path: str, library_type: str = "brick"):
        """Export entire library to file"""
        if library_type == "brick":
            result = processor.process_event({
                "event": "export_library",
                "library_name": library_name,
                "export_path": export_path
            })
        else:  # schema
            result = processor.process_event({
                "event": "export_schema_library",
                "library_name": library_name,
                "export_path": export_path
            })
        
        return result
    
    @staticmethod
    def import_library(processor, import_path: str, library_name: str = None, library_type: str = "brick"):
        """Import library from file"""
        event_data = {
            "event": "import_library",
            "import_path": import_path,
            "library_type": library_type
        }
        
        if library_name:
            event_data["library_name"] = library_name
        
        return processor.process_event(event_data)

class SelectLibraryDialog(QDialog):
    """Dialog for selecting a library"""
    
    def __init__(self, processor, library_type: str, parent=None):
        super().__init__(parent)
        self.processor = processor
        self.library_type = library_type
        self.selected_library = None
        self.setWindowTitle(f"Select {library_type.title()} Library")
        self.setModal(True)
        self.init_ui()
        self.load_libraries()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel(f"Select a {self.library_type} library:"))
        
        self.library_combo = QComboBox()
        layout.addWidget(self.library_combo)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept_dialog)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def load_libraries(self):
        """Load available libraries"""
        if self.library_type == "brick":
            result = self.processor.process_event({"event": "get_libraries"})
        else:  # schema
            result = self.processor.process_event({"event": "get_schema_libraries"})
        
        if result["status"] == "success":
            libraries = result["data"]["libraries"]
            for library in libraries:
                self.library_combo.addItem(
                    f"{library['name']} ({library['brick_count']} items)", 
                    library['name']
                )
    
    def get_selected_library(self) -> str:
        """Get selected library name"""
        return self.selected_library
    
    def accept_dialog(self):
        """Validate and accept dialog"""
        if self.library_combo.count() == 0:
            QMessageBox.warning(self, "No Libraries", "No libraries available. Please create a library first.")
            return
        
        self.selected_library = self.library_combo.currentData()
        self.accept()
