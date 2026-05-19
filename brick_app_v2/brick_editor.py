#!/usr/bin/env python3
"""
Refactored Stateful SHACL Brick Editor
Uses clean architecture with proper separation of concerns
"""

import sys
import os
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QMessageBox, QDialog, QListWidgetItem, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi

# Add brick_app_v2 directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))
sys.path.insert(0, str(app_dir / 'state'))
sys.path.insert(0, str(app_dir / 'business'))
sys.path.insert(0, str(app_dir / 'ui'))

# Import components
from business.brick_service import brick_service, OperationResult
from core.brick_core_simple import sanitize_filename
from ui.property_formatters import (
    format_property_enhanced_text,
    format_constraint_summary, get_datatype_icon
)
from gui_components import (
    PropertyEditorDialog, ConstraintEditorDialog, SimpleOntologyBrowser
)


class BrickEditor(QMainWindow):
    """SHACL Brick Editor with local state management"""
    
    # UI States
    BROWSE = "browse"
    EDIT = "edit"
    CREATE = "create"
    
    def __init__(self):
        super().__init__()
        
        # Load UI from file
        ui_path = Path(__file__).parent / "ui" / "main_window.ui"
        loadUi(str(ui_path), self)
        
        # Local state only - no global state manager
        self.ui_state = self.BROWSE
        self.current_brick = None  # Current brick being edited
        self.current_brick_type = "NodeShape"
        self.active_library = None
        
        # Setup window
        self.setWindowTitle("SHACL Brick Editor")
        
        # Connect signals
        self._connect_signals()
        
        # Load initial data
        self._load_initial_data()
        
        # Initialize UI
        self._update_ui_visibility()
        
        # Hide delete button initially (no brick selected)
        self.update_delete_button_visibility()
    
    def _connect_signals(self):
        """Connect UI signals to handlers"""
        # Library signals
        self.libraryComboBox.currentTextChanged.connect(self.on_library_changed)
        self.nodeBrickList.itemDoubleClicked.connect(self.on_node_brick_selected)
        self.newNode.clicked.connect(self.on_new_node)
        self.deleteBrick.clicked.connect(self.on_delete_brick)
        self.newLibrary.clicked.connect(self.on_new_library)
        self.deleteLibrary.clicked.connect(self.on_delete_library)
        self.downloadOntology.clicked.connect(self.on_download_ontology)
        
        # Brick selection signals for delete button visibility
        self.nodeBrickList.itemSelectionChanged.connect(self.on_brick_selection_changed)
        
        # Editor signals
        self.namelineEdit.textChanged.connect(self.on_field_changed)
        self.targetLineEdit.textChanged.connect(self.on_field_changed)
        self.propertyPathEdit.textChanged.connect(self.on_field_changed)
        self.description.textChanged.connect(self.on_field_changed)
        self.ontologyTargetBrowser.clicked.connect(self.browse_ontology)
        self.ontologyPathBrowser.clicked.connect(self.browse_ontology)
        self.generateIriBtn.clicked.connect(self.generate_property_path_iri)
        self.datatypeCombo.currentTextChanged.connect(self.on_datatype_changed)
        
        # Property signals
        self.propertyList.itemSelectionChanged.connect(self.on_property_selection_changed)
        self.propertyList.itemDoubleClicked.connect(self.on_property_double_clicked)
        self.addProperty.clicked.connect(self.add_property)
        self.addConstraint.clicked.connect(self.add_constraint)
        self.deleteProperty.clicked.connect(self.delete_property)
        
        # Control signals
        self.saveBrick.clicked.connect(self.save_brick)
        self.cancelBrickEdit.clicked.connect(self.cancel_edit)
    
    def _update_ui_visibility(self):
        """Update UI visibility based on local state"""
        try:
            if self.ui_state == self.BROWSE:
                # Show lists, hide editor
                self.nodeBrickList.setVisible(True)
                self.propertyList.setVisible(True)
                self.editorPanel.setVisible(False)
            elif self.ui_state == self.EDIT:
                # Hide lists, show editor for editing existing brick
                self.nodeBrickList.setVisible(False)
                self.propertyList.setVisible(True)
                self.editorPanel.setVisible(True)
            elif self.ui_state == self.CREATE:
                # Hide lists, show editor for new brick
                self.nodeBrickList.setVisible(False)
                self.propertyList.setVisible(False)
                self.editorPanel.setVisible(True)
            
            # Update field visibility based on brick type
            self._update_field_visibility()
            
        except Exception as e:
            print(f"Error updating UI visibility: {e}")
    
    def _update_field_visibility(self):
        """Show/hide fields based on brick type (NodeShape vs PropertyShape)"""
        try:
            if self.current_brick_type == "NodeShape":
                # Show target class fields
                if hasattr(self, 'targetLabel'):
                    self.targetLabel.show()
                if hasattr(self, 'targetLineEdit'):
                    self.targetLineEdit.show()
                if hasattr(self, 'ontologyTargetBrowser'):
                    self.ontologyTargetBrowser.show()
                # Hide property path fields
                if hasattr(self, 'propertyLabel'):
                    self.propertyLabel.hide()
                if hasattr(self, 'propertyPathEdit'):
                    self.propertyPathEdit.hide()
                if hasattr(self, 'ontologyPathBrowser'):
                    self.ontologyPathBrowser.hide()
                if hasattr(self, 'datatypeLabel'):
                    self.datatypeLabel.hide()
                if hasattr(self, 'datatypeCombo'):
                    self.datatypeCombo.hide()
                if hasattr(self, 'generateIriBtn'):
                    self.generateIriBtn.hide()
            else:  # PropertyShape
                # Hide target class fields
                if hasattr(self, 'targetLabel'):
                    self.targetLabel.hide()
                if hasattr(self, 'targetLineEdit'):
                    self.targetLineEdit.hide()
                if hasattr(self, 'ontologyTargetBrowser'):
                    self.ontologyTargetBrowser.hide()
                # Show property path fields
                if hasattr(self, 'propertyLabel'):
                    self.propertyLabel.show()
                if hasattr(self, 'propertyPathEdit'):
                    self.propertyPathEdit.show()
                if hasattr(self, 'ontologyPathBrowser'):
                    self.ontologyPathBrowser.show()
                if hasattr(self, 'datatypeLabel'):
                    self.datatypeLabel.show()
                if hasattr(self, 'datatypeCombo'):
                    self.datatypeCombo.show()
                if hasattr(self, 'generateIriBtn'):
                    self.generateIriBtn.show()
        except Exception as e:
            print(f"Error updating field visibility: {e}")
    
    def _update_ui_with_brick_data(self):
        """Update UI fields with current brick data (from local state)"""
        try:
            if not self.current_brick:
                return
            
            # Block signals during UI updates
            self.namelineEdit.blockSignals(True)
            self.description.blockSignals(True)
            self.targetLineEdit.blockSignals(True)
            self.propertyPathEdit.blockSignals(True)
            
            # Update fields
            self.namelineEdit.setText(self.current_brick.get('name', ''))
            self.description.setPlainText(self.current_brick.get('description', ''))
            
            # Update type label
            self.currentTypeLabel.setText(self.current_brick.get('object_type', 'NodeShape'))
            
            # Update type-specific fields
            object_type = self.current_brick.get('object_type', 'NodeShape')
            if object_type == "NodeShape":
                self.targetLineEdit.setText(self.current_brick.get('target_class', ''))
            else:
                self.propertyPathEdit.setText(self.current_brick.get('property_path', ''))
                # Restore datatype from properties
                properties = self.current_brick.get('properties', {})
                datatype = properties.get('datatype', 'xsd:string')
                self.datatypeCombo.blockSignals(True)
                index = self.datatypeCombo.findText(datatype)
                if index >= 0:
                    self.datatypeCombo.setCurrentIndex(index)
                self.datatypeCombo.blockSignals(False)
            
            # Update property list
            self._update_property_list()
            
            # Re-enable signals
            self.namelineEdit.blockSignals(False)
            self.description.blockSignals(False)
            self.targetLineEdit.blockSignals(False)
            self.propertyPathEdit.blockSignals(False)
            
        except Exception as e:
            print(f"Error updating UI with brick data: {e}")
            # Re-enable signals on error
            try:
                self.namelineEdit.blockSignals(False)
                self.description.blockSignals(False)
                self.targetLineEdit.blockSignals(False)
                self.propertyPathEdit.blockSignals(False)
            except:
                pass
    
    def _clear_editor_fields(self):
        """Clear all editor fields for new brick creation"""
        try:
            # Block signals during updates
            self.namelineEdit.blockSignals(True)
            self.description.blockSignals(True)
            self.targetLineEdit.blockSignals(True)
            self.propertyPathEdit.blockSignals(True)
            
            # Clear fields
            self.namelineEdit.clear()
            self.description.clear()
            self.targetLineEdit.clear()
            self.propertyPathEdit.clear()
            
            # Clear property list
            if hasattr(self, 'propertyList'):
                self.propertyList.clear()
            
            # Re-enable signals
            self.namelineEdit.blockSignals(False)
            self.description.blockSignals(False)
            self.targetLineEdit.blockSignals(False)
            self.propertyPathEdit.blockSignals(False)
            
        except Exception as e:
            print(f"Error clearing editor fields: {e}")
            # Re-enable signals on error
            try:
                self.namelineEdit.blockSignals(False)
                self.description.blockSignals(False)
                self.targetLineEdit.blockSignals(False)
                self.propertyPathEdit.blockSignals(False)
            except:
                pass
    
    def _load_initial_data(self):
        """Load initial data"""
        try:
            # Load libraries
            libraries = brick_service.get_libraries()
            self.libraryComboBox.clear()
            self.libraryComboBox.addItems(libraries)
            
            # Sync service with first library
            if libraries:
                brick_service.set_active_library(libraries[0])
                self.active_library = libraries[0]
            
            # Load bricks
            self.load_library()
            
        except Exception as e:
            print(f"Error loading initial data: {e}")
    
    # Library Operations
    def on_library_changed(self, library_name: str):
        """Handle library change"""
        brick_service.set_active_library(library_name)
        self.active_library = library_name
        self.load_library()
    
    def load_library(self):
        """Load library bricks"""
        try:
            # Block signals during library loading to prevent recursion
            self.libraryComboBox.blockSignals(True)
            self.nodeBrickList.blockSignals(True)
            
            # Save current selection
            current_library = self.libraryComboBox.currentText()
            
            # Update library list
            libraries = brick_service.get_libraries()
            self.libraryComboBox.clear()
            self.libraryComboBox.addItems(libraries)
            
            # Restore current library selection if it still exists
            if current_library and current_library in libraries:
                self.libraryComboBox.setCurrentText(current_library)
            elif libraries:
                self.libraryComboBox.setCurrentIndex(0)
            
            # Load bricks from the active library (all bricks are NodeShapes)
            bricks = brick_service.get_bricks()
            self.nodeBrickList.clear()
            
            for brick in bricks:
                display_text = f"{brick.get('name', 'Unknown')}"
                list_item = QListWidgetItem(display_text)
                list_item.setData(Qt.ItemDataRole.UserRole, brick)
                self.nodeBrickList.addItem(list_item)
            
            # Re-enable signals
            self.libraryComboBox.blockSignals(False)
            self.nodeBrickList.blockSignals(False)
            
        except Exception as e:
            print(f"Error loading library: {e}")
            # Re-enable signals on error
            self.libraryComboBox.blockSignals(False)
            self.nodeBrickList.blockSignals(False)
    
    def on_node_brick_selected(self, item):
        """Handle node brick selection - opens editor"""
        if not item:
            return
        brick_data = item.data(Qt.ItemDataRole.UserRole)
        if brick_data:
            brick_id = brick_data.get('brick_id')
            loaded_brick = brick_service.load_brick(brick_id)
            if loaded_brick:
                # Update local state
                self.current_brick = loaded_brick
                self.current_brick_type = loaded_brick.get('object_type', 'NodeShape')
                self.ui_state = self.EDIT
                # Update UI
                self._update_ui_visibility()
                self._update_ui_with_brick_data()
    
    def on_new_node(self):
        """Handle new node brick button - opens editor for new brick"""
        new_brick = brick_service.create_brick("NodeShape")
        # Update local state
        self.current_brick = new_brick
        self.current_brick_type = "NodeShape"
        self.ui_state = self.CREATE
        # Clear and update UI
        self._clear_editor_fields()
        self._update_ui_visibility()
    
    def on_delete_brick(self):
        """Handle delete brick button"""
        selected_brick_data = self._get_selected_brick()
        if not selected_brick_data:
            QMessageBox.warning(self, "Warning", "Please select a brick to delete.")
            return
        
        brick_id = selected_brick_data.get('brick_id')
        brick_name = selected_brick_data.get('name', 'Unknown')
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Delete Brick", 
            f"Are you sure you want to delete '{brick_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result = brick_service.delete_brick(brick_id)
            if result.success:
                QMessageBox.information(self, "Success", result.message)
                self.load_library()
            else:
                QMessageBox.warning(self, "Error", result.message)

    def on_brick_selection_changed(self):
        """Handle brick selection change"""
        self.update_delete_button_visibility()
    
    def update_delete_button_visibility(self):
        """Update delete button visibility based on brick selection"""
        has_selection = self._get_selected_brick() is not None
        self.deleteBrick.setVisible(has_selection)
    
    def _get_selected_brick(self):
        """Get currently selected brick"""
        if self.nodeBrickList.currentItem():
            return self.nodeBrickList.currentItem().data(Qt.ItemDataRole.UserRole)
        return None
    
    # Editor Operations
    def on_field_changed(self):
        """Handle field changes - update local current_brick"""
        if not self.current_brick:
            return
        # Update local brick data from UI fields
        self.current_brick['name'] = self.namelineEdit.text()
        self.current_brick['description'] = self.description.toPlainText()
        if self.current_brick_type == "NodeShape":
            self.current_brick['target_class'] = self.targetLineEdit.text()
        else:
            self.current_brick['property_path'] = self.propertyPathEdit.text()
    
    def on_datatype_changed(self, datatype: str):
        """Handle datatype combo change (stores in brick properties)"""
        if not self.current_brick:
            return
        if 'properties' not in self.current_brick:
            self.current_brick['properties'] = {}
        self.current_brick['properties']['datatype'] = datatype

    def browse_ontology(self):
        """Handle ontology browser button click"""
        try:
            # Determine mode based on brick type
            mode = "classes" if self.current_brick_type == "NodeShape" else "properties"
            
            # Create and show ontology browser dialog
            dialog = SimpleOntologyBrowser(brick_service.ontology_manager, self, mode)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_item = dialog.selected_item
                if selected_item:
                    # Set the appropriate field with the selected URI
                    uri = selected_item['uri']
                    if self.current_brick:
                        if self.current_brick_type == "NodeShape":
                            self.current_brick['target_class'] = uri
                            self.targetLineEdit.setText(uri)
                        else:
                            self.current_brick['property_path'] = uri
                            self.propertyPathEdit.setText(uri)
                    
                    # Auto-set name from last element of URI if name is empty/default
                    current_name = self.current_brick.get('name', '') if self.current_brick else ''
                    if not current_name or current_name.startswith('New '):
                        # Extract last element from URI (e.g., http://schema.org/ns#Address -> Address)
                        name = uri
                        if '#' in uri:
                            name = uri.split('#')[-1]
                        elif '/' in uri:
                            name = uri.split('/')[-1]
                        if name and self.current_brick:
                            self.current_brick['name'] = name
                            self.namelineEdit.setText(name)
        except Exception as e:
            print(f"Error browsing ontology: {e}")
    
    # Property Operations
    def on_property_selection_changed(self):
        """Handle property selection change"""
        # This will be handled by state updates
        pass
    
    def generate_property_path_iri(self):
        """Generate a custom IRI for the property path from the brick name"""
        from gui_components import DEFAULT_NAMESPACE
        import re
        name = self.namelineEdit.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a brick name first")
            return

        # Convert name to camelCase IRI fragment
        cleaned = re.sub(r'[^\w\s-]', '', name)
        words = cleaned.split()
        if not words:
            QMessageBox.warning(self, "Warning", "Name contains no valid characters")
            return
        iri_fragment = words[0].lower() + ''.join(w.capitalize() for w in words[1:])

        full_iri = f"{DEFAULT_NAMESPACE}{iri_fragment}"
        self.propertyPathEdit.setText(full_iri)
        if self.current_brick:
            self.current_brick['property_path'] = full_iri

    def add_property(self):
        """Add a property using property editor"""
        if not self.current_brick:
            QMessageBox.warning(self, "Error", "No brick being edited")
            return
        dialog = PropertyEditorDialog(self, ontology_manager=brick_service.ontology_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            property_data = dialog.get_property_data()
            if property_data.get('name'):
                brick_id = self.current_brick.get('brick_id')
                result = brick_service.add_property(brick_id, property_data)
                if result.success:
                    # Update local brick with new property
                    if 'properties' not in self.current_brick:
                        self.current_brick['properties'] = {}
                    self.current_brick['properties'][property_data['name']] = property_data
                    self._update_property_list()
                else:
                    QMessageBox.warning(self, "Error", result.message)
    
    def add_constraint(self):
        """Add constraint to selected property"""
        property_data = self._get_selected_property()
        if not property_data:
            QMessageBox.warning(self, "Warning", "Please select a property first.")
            return
        
        # Open constraint editor dialog
        dialog = ConstraintEditorDialog(self, property_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            constraint_data = dialog.get_constraint_data()
            if constraint_data:
                prop_name = property_data.get('name')
                # Add constraint to local brick (simplified - would need proper implementation)
                success, message = True, "Constraint added"
                if success:
                    self._update_property_list()
                else:
                    QMessageBox.warning(self, "Error", message)
    
    def delete_property(self):
        """Delete selected property from current brick"""
        property_data = self._get_selected_property()
        if not property_data:
            QMessageBox.warning(self, "Warning", "Please select a property to delete.")
            return
        
        prop_name = property_data.get('name')
        if not prop_name:
            QMessageBox.warning(self, "Error", "Selected property has no name.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Delete Property",
            f"Are you sure you want to delete the property '{prop_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove property from local brick
            if 'properties' in self.current_brick and prop_name in self.current_brick['properties']:
                del self.current_brick['properties'][prop_name]
                success, message = True, f"Property '{prop_name}' removed"
            if success:
                self._update_property_list()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def on_property_double_clicked(self, item):
        """Handle property double-click - edit property"""
        if not item:
            return
        
        prop_data = item.data(Qt.ItemDataRole.UserRole)
        if not prop_data:
            return
        
        # Open property editor dialog
        dialog = PropertyEditorDialog(self, prop_data, ontology_manager=brick_service.ontology_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_property_data()
            if updated_data.get('name'):
                # Update property in current brick
                old_name = prop_data.get('name')
                new_name = updated_data['name']
                
                # Handle both legacy properties dict and modern leaf_properties list
                if 'leaf_properties' in self.current_brick and self.current_brick['leaf_properties']:
                    # Find and update in leaf_properties
                    for prop in self.current_brick['leaf_properties']:
                        if (prop.get('label') == old_name or 
                            prop.get('path', '').split(':')[-1] == old_name):
                            prop['label'] = new_name
                            prop['path'] = updated_data.get('path', prop.get('path'))
                            break
                elif 'properties' in self.current_brick:
                    # Update in legacy properties dict
                    if old_name in self.current_brick['properties']:
                        # Remove old key, add with new key if name changed
                        if old_name != new_name:
                            self.current_brick['properties'][new_name] = self.current_brick['properties'].pop(old_name)
                        # Update path if provided
                        if updated_data.get('path'):
                            self.current_brick['properties'][new_name]['path'] = updated_data['path']
                
                self._update_property_list()
                self.statusBar().showMessage(f"Updated property: {new_name}")
    
    def _get_selected_property(self):
        """Get currently selected property"""
        current_item = self.propertyList.currentItem()
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def _update_property_list(self):
        """Update property list display with enhanced formatting"""
        if not self.current_brick or not hasattr(self, 'propertyList'):
            return
        
        # Block signals during updates to prevent recursion
        self.propertyList.blockSignals(True)
        
        try:
            self.propertyList.clear()
            added_properties = set()  # Track added properties to prevent duplicates
            
            # Handle modern leaf_properties list format
            leaf_properties = self.current_brick.get('leaf_properties', [])
            for prop in leaf_properties:
                prop_name = prop.get('label') or prop.get('path', '').split(':')[-1] or 'Unnamed'
                if prop_name in added_properties:
                    continue
                added_properties.add(prop_name)
                list_item = self._create_property_list_item(prop_name, prop)
                if list_item:
                    self.propertyList.addItem(list_item)
            
            # Handle legacy properties dict format
            properties = self.current_brick.get('properties', {})
            for prop_name, prop_data in properties.items():
                if prop_name in added_properties:
                    continue
                added_properties.add(prop_name)
                list_item = self._create_property_list_item(prop_name, prop_data)
                if list_item:
                    self.propertyList.addItem(list_item)
                
        finally:
            # Re-enable signals
            self.propertyList.blockSignals(False)
    
    def _create_property_list_item(self, prop_name: str, prop_data):
        """Create an enhanced property list item with rich formatting"""
        from PyQt6.QtGui import QFont, QColor, QBrush
        from PyQt6.QtCore import Qt
        
        # Store the complete property data for editing
        if isinstance(prop_data, dict):
            full_prop_data = {
                'name': prop_name,
                **prop_data
            }
        else:
            # For non-dict prop_data, create a simple structure
            full_prop_data = {
                'name': prop_name,
                'value': prop_data,
                'path': prop_data if isinstance(prop_data, str) else str(prop_data)
            }
        
        # Create list item
        list_item = QListWidgetItem()
        list_item.setData(Qt.ItemDataRole.UserRole, full_prop_data)
        
        # Use enhanced text formatting that works with QListWidget
        display_text = format_property_enhanced_text(prop_name, prop_data)
        list_item.setText(display_text)
        
        # Set visual styling based on property constraints
        if isinstance(prop_data, dict) and prop_data.get('constraints'):
            # Properties with constraints get subtle highlighting
            list_item.setBackground(QBrush(QColor(255, 248, 220)))  # Light yellow background
        
        return list_item
    
    # Control Operations
    def save_brick(self):
        """Save current brick (JSON + SHACL .ttl written by BrickCore)"""
        if not self.current_brick:
            QMessageBox.warning(self, "Error", "No brick to save")
            return
        
        # Update current brick from UI fields before saving
        self.current_brick['name'] = self.namelineEdit.text()
        self.current_brick['description'] = self.description.toPlainText()
        if self.current_brick_type == "NodeShape":
            self.current_brick['target_class'] = self.targetLineEdit.text()
        else:
            self.current_brick['property_path'] = self.propertyPathEdit.text()
        
        result = brick_service.save_brick(self.current_brick)
        if result.success:
            QMessageBox.information(self, "Success", result.message)
            # Return to browse mode
            self.ui_state = self.BROWSE
            self.current_brick = None
            self._update_ui_visibility()
            self.load_library()
        else:
            QMessageBox.warning(self, "Error", result.message)
    
    def cancel_edit(self):
        """Cancel edit and return to browse mode"""
        self.ui_state = self.BROWSE
        self.current_brick = None
        self._update_ui_visibility()
    
    # Library Management
    def on_new_library(self):
        """Handle new library button click"""
        library_name, ok = QInputDialog.getText(
            self,
            "New Library",
            "Enter name for new library:",
            text=""
        )
        
        if ok and library_name.strip():
            library_name = library_name.strip()
            
            # Check if library already exists
            current_libraries = brick_service.get_libraries()
            if library_name in current_libraries:
                QMessageBox.warning(self, "Warning", f"Library '{library_name}' already exists.")
                return
            
            try:
                brick_service.brick_core.shared_library_manager.create_library(
                    lib_type="bricks",
                    name=library_name,
                    description=f"Brick library '{library_name}'"
                )
                self._load_initial_data()
                self.libraryComboBox.setCurrentText(library_name)
                self.statusBar().showMessage(f"Created library: {library_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create library: {e}")
    
    def on_delete_library(self):
        """Handle delete library button click"""
        current_library = self.libraryComboBox.currentText()
        if not current_library or current_library == "default":
            QMessageBox.warning(self, "Warning", "Cannot delete the default library.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Library",
            f"Are you sure you want to delete library '{current_library}'? This will archive the library first.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                import shutil
                from datetime import datetime
                
                # Get library path
                libraries = brick_service.get_libraries()
                if current_library not in libraries:
                    QMessageBox.warning(self, "Error", f"Library '{current_library}' not found.")
                    return
                
                # Archive before deletion
                repository_path = brick_service.brick_core.repository_path
                lib_path = Path(repository_path) / current_library
                
                if lib_path.exists():
                    # Create archive directory
                    archive_dir = Path(repository_path).parent / 'archive' / 'bricks'
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Create timestamped archive
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    archive_name = f"{current_library}_{timestamp}"
                    archive_path = archive_dir / archive_name
                    
                    # Create archive
                    shutil.make_archive(str(archive_path), 'zip', str(lib_path.parent), lib_path.name)
                    
                    # Create metadata
                    metadata = {
                        "original_name": current_library,
                        "original_path": str(lib_path),
                        "type": "bricks",
                        "archived_at": datetime.now().isoformat(),
                        "archive_file": f"{archive_name}.zip"
                    }
                    
                    metadata_file = archive_dir / f"{archive_name}_metadata.json"
                    import json
                    with open(metadata_file, 'w') as f:
                        json.dump(metadata, f, indent=2)
                
                # Remove the directory
                if lib_path.exists():
                    shutil.rmtree(lib_path)
                
                QMessageBox.information(self, "Success", 
                    f"Library '{current_library}' deleted and archived successfully!")
                
                # Reload libraries
                self._load_initial_data()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete library: {e}")

    def on_download_ontology(self):
        """Handle download ontology button click"""
        dialog = OntologySearchDialog(self, brick_service.ontology_manager)
        dialog.exec()


class OntologySearchDialog(QDialog):
    """Dialog for searching and downloading ontologies"""
    
    def __init__(self, parent=None, ontology_manager=None):
        super().__init__(parent)
        self.ontology_manager = ontology_manager
        self.selected_ontology = None
        
        # Load UI
        from pathlib import Path
        ui_file = Path(__file__).parent / "ui" / "ontology_search_dialog.ui"
        loadUi(str(ui_file), self)
        
        # Connect signals
        self.searchButton.clicked.connect(self.on_search)
        self.resultsList.itemClicked.connect(self.on_result_selected)
        self.downloadButton.clicked.connect(self.on_download)
        self.cancelButton.clicked.connect(self.reject)
        self.tabWidget.currentChanged.connect(self._update_download_button)
        self.urlLineEdit.textChanged.connect(self._update_download_button)
        
        # Disable download button initially
        self.downloadButton.setEnabled(False)
        
        self.search_results = []
    
    def on_search(self):
        """Search LOV for ontologies"""
        query = self.searchLineEdit.text().strip()
        if not query:
            return
        
        self.resultsList.clear()
        self.infoLabel.setText("Searching...")
        self.search_results = []
        
        try:
            # Search LOV API
            import urllib.request
            import urllib.parse
            import json
            
            url = f"https://lov.linkeddata.es/dataset/lov/api/v2/vocabulary/search?q={urllib.parse.quote(query)}"
            
            req = urllib.request.Request(url, headers={'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            # Parse results - LOV API returns data in _source field
            for result in data.get('results', []):
                vocab = result.get('_source', {})
                prefix = vocab.get('prefix', 'unknown')
                
                # Title is in a field like "http://purl.org/dc/terms/title@en"
                title = None
                for key in vocab.keys():
                    if 'title' in key.lower():
                        title = vocab.get(key)
                        break
                if not title:
                    title = prefix
                
                uri = vocab.get('uri', '')
                
                item_text = f"{prefix}: {title}"
                self.resultsList.addItem(item_text)
                self.search_results.append({
                    'prefix': prefix,
                    'title': title,
                    'uri': uri
                })
            
            if not self.search_results:
                self.infoLabel.setText("No results found. Try different keywords.")
            else:
                self.infoLabel.setText(f"Found {len(self.search_results)} ontologies. Select one to download.")
                
        except Exception as e:
            self.infoLabel.setText(f"Search failed: {str(e)}")
    
    def on_result_selected(self, item):
        """Handle result selection"""
        index = self.resultsList.currentRow()
        if 0 <= index < len(self.search_results):
            self.selected_ontology = self.search_results[index]
            self.infoLabel.setText(f"Selected: {self.selected_ontology['prefix']}\n{self.selected_ontology['uri']}")
            self.downloadButton.setEnabled(True)

    def _update_download_button(self):
        """Enable Download button based on the active tab"""
        if self.tabWidget.currentIndex() == 1:
            # URL tab: enable when URL field is non-empty
            self.downloadButton.setEnabled(bool(self.urlLineEdit.text().strip()))
        else:
            # Search tab: enable only when a result is selected
            self.downloadButton.setEnabled(self.selected_ontology is not None)

    def on_download(self):
        """Download the selected or URL ontology"""
        try:
            if self.tabWidget.currentIndex() == 0:
                # Search tab - download selected
                if not self.selected_ontology:
                    QMessageBox.warning(self, "Warning", "Please select an ontology first.")
                    return
                
                prefix = self.selected_ontology['prefix']
                uri = self.selected_ontology['uri']
                
                # Get download URL from LOV
                import urllib.request
                import urllib.parse
                import json
                
                url = f"https://lov.linkeddata.es/dataset/lov/api/v2/vocabulary/info?vocab={prefix}"
                req = urllib.request.Request(url, headers={'Accept': 'application/json'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode('utf-8'))
                
                # Find download URL - try graphs first, then fall back to homepage
                download_url = None
                print(f"DEBUG: Looking for download URL in data with keys: {list(data.keys())}")
                for graph in data.get('graphs', []):
                    for dist in graph.get('distributions', []):
                        download_url = dist.get('downloadURL')
                        if download_url:
                            print(f"DEBUG: Found download URL in distributions: {download_url}")
                            break
                    if download_url:
                        break
                
                # Fallback to homepage if no distribution URL found
                if not download_url:
                    download_url = data.get('homepage')
                    if download_url:
                        print(f"DEBUG: Using homepage as fallback: {download_url}")
                
                # Fallback to versions fileURL
                if not download_url:
                    versions = data.get('versions', [])
                    if versions:
                        download_url = versions[0].get('fileURL')
                        if download_url:
                            print(f"DEBUG: Using versions fileURL as fallback: {download_url}")
                
                if not download_url:
                    print(f"DEBUG: No download URL found. data.get('homepage')={data.get('homepage')}")
                    QMessageBox.critical(self, "Error", "Could not find download URL for this ontology.")
                    return
                
                # Download to cache
                self._download_ontology(prefix, download_url)
                
            else:
                # URL tab - download from direct URL
                url = self.urlLineEdit.text().strip()
                name = self.nameLineEdit.text().strip()
                
                if not url:
                    QMessageBox.warning(self, "Warning", "Please enter a URL.")
                    return
                
                if not name:
                    name = url.split('/')[-1].split('.')[0] or "ontology"
                
                self._download_ontology(name, url)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Download failed: {str(e)}")
    
    def _download_ontology(self, name: str, url: str):
        """Download ontology from URL to cache"""
        import urllib.request
        import urllib.error
        from pathlib import Path
        
        # Build request — prefer RDF/XML then Turtle so GeoNames-style servers respond correctly
        req = urllib.request.Request(
            url,
            headers={
                'Accept': 'application/rdf+xml,text/turtle;q=0.9,application/n-triples;q=0.8,*/*;q=0.5',
                'User-Agent': 'Mozilla/5.0 (compatible; BrickApp/2.0; ontology downloader)'
            }
        )
        
        # Download with extended timeout; urllib follows redirects automatically
        with urllib.request.urlopen(req, timeout=60) as response:
            content = response.read()
            content_type = response.headers.get('Content-Type', '')
            final_url = response.url if hasattr(response, 'url') else url
        
        # Reject HTML responses (server returned an error/landing page, not the ontology)
        if content[:200].lstrip().startswith(b'<!') or b'<html' in content[:200].lower():
            raise ValueError(
                f"Server returned an HTML page instead of RDF data.\n"
                f"Try downloading the file manually and use the URL tab to point to the direct .rdf/.ttl file.\n"
                f"Final URL was: {final_url}"
            )
        
        # Determine file extension from Content-Type or URL
        if 'turtle' in content_type or final_url.endswith('.ttl') or url.endswith('.ttl'):
            ext = '.ttl'
        elif 'xml' in content_type or 'rdf' in content_type or final_url.endswith('.rdf') or url.endswith('.rdf'):
            ext = '.rdf'
        elif content.lstrip().startswith(b'@') or content.lstrip().startswith(b'<http'):
            ext = '.ttl'  # Likely Turtle
        elif content.lstrip().startswith(b'<?xml') or content.lstrip().startswith(b'<rdf'):
            ext = '.rdf'  # Likely RDF/XML
        else:
            ext = '.rdf'  # Default for unknown
        
        # Save to cache
        cache_path = Path(self.ontology_manager.cache_path)
        cache_path.mkdir(parents=True, exist_ok=True)
        
        output_file = cache_path / f"{name}{ext}"
        with open(output_file, 'wb') as f:
            f.write(content)
        
        # Reload ontologies
        self.ontology_manager.load_cached_ontologies()
        
        QMessageBox.information(self, "Success", 
            f"Ontology '{name}' downloaded successfully!\nSaved to: {output_file}")
        self.accept()


def main():
    """Main entry point for refactored GUI"""
    app = QApplication(sys.argv)
    gui = RefactoredBrickEditor()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
