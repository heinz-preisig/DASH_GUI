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

# Import new architecture components
from state.app_state import app_state_manager, UIState, BrickType
from business.brick_operations import brick_business_logic
from ui.ui_abstraction import UIManager, BrickEditorComponent, BrickListComponent, LibraryComponent, PropertyListComponent
from gui_components import (
    PropertyEditorDialog, PropertyBrickBrowser, ConstraintEditorDialog,
    SimpleOntologyBrowser
)

# Constants
MAX_CONSTRAINTS_IN_SUMMARY = 10  # Maximum constraints shown in property list preview


class RefactoredBrickEditor(QMainWindow):
    """Refactored SHACL Brick Editor using clean architecture"""
    
    def __init__(self):
        super().__init__()
        
        # Load UI from file
        ui_path = Path(__file__).parent / "ui" / "main_window.ui"
        loadUi(str(ui_path), self)
        
        # Initialize new architecture components
        self.ui_manager = UIManager(self)
        self.brick_editor_component = BrickEditorComponent(self)
        self.brick_list_component = BrickListComponent(self)
        self.library_component = LibraryComponent(self)
        self.property_list_component = PropertyListComponent(self)
        
        # Register components with UI manager
        self.ui_manager.register_component("brick_editor", self.brick_editor_component)
        self.ui_manager.register_component("brick_list", self.brick_list_component)
        self.ui_manager.register_component("library", self.library_component)
        self.ui_manager.register_component("property_list", self.property_list_component)
        
        # Subscribe to state changes
        app_state_manager.add_state_listener(self)
        
        # Setup window
        self.setWindowTitle("Refactored SHACL Brick Editor")
        self.setGeometry(100, 100, 650, 950)
        
        # Connect signals
        self._connect_signals()
        
        # Initialize state
        app_state_manager.set_ui_state(UIState.BROWSE)
        
        # Load initial data
        self._load_initial_data()
        
        # Force initial UI update
        ui_state = app_state_manager.get_ui_visibility()
        self.ui_manager.update_all_components(ui_state)
    
    def _connect_signals(self):
        """Connect UI signals to handlers"""
        # Library signals
        self.libraryComboBox.currentTextChanged.connect(self.on_library_changed)
        self.nodeBrickList.itemDoubleClicked.connect(self.on_node_brick_selected)
        self.propertyBrickList.itemDoubleClicked.connect(self.on_property_brick_selected)
        self.newBrick.clicked.connect(self.on_new_brick)
        self.deleteBrick.clicked.connect(self.on_delete_brick)
        self.newLibrary.clicked.connect(self.on_new_library)
        self.deleteLibrary.clicked.connect(self.on_delete_library)
        
        # Brick selection signals for delete button visibility
        self.nodeBrickList.itemSelectionChanged.connect(self.on_brick_selection_changed)
        self.propertyBrickList.itemSelectionChanged.connect(self.on_brick_selection_changed)
        
        # Editor signals
        self.radioNode.toggled.connect(self.on_type_changed)
        self.radioProperty.toggled.connect(self.on_type_changed)
        self.namelineEdit.textChanged.connect(self.on_field_changed)
        self.targetLineEdit.textChanged.connect(self.on_field_changed)
        self.propertyPathEdit.textChanged.connect(self.on_field_changed)
        self.description.textChanged.connect(self.on_field_changed)
        self.ontologyTargetBrowser.clicked.connect(self.browse_ontology)
        self.ontologyPathBrowser.clicked.connect(self.browse_ontology)
        
        # Property signals
        self.propertyList.itemSelectionChanged.connect(self.on_property_selection_changed)
        self.propertyList.itemDoubleClicked.connect(self.on_property_double_clicked)
        self.addProperty.clicked.connect(self.add_property)
        self.addPropertyBrick.clicked.connect(self.add_property_brick)
        self.addConstraint.clicked.connect(self.add_constraint)
        self.deleteProperty.clicked.connect(self.delete_property)
        
        # Control signals
        self.saveBrick.clicked.connect(self.save_brick)
        self.cancelBrickEdit.clicked.connect(self.cancel_edit)
    
    def on_state_changed(self, state_type: str, old_value, new_value):
        """Handle state changes from app state manager"""
        try:
            if state_type in ["ui_state", "brick_type"]:
                # Update UI components when state changes
                ui_state = app_state_manager.get_ui_visibility()
                self.ui_manager.update_all_components(ui_state)
            
            # Handle brick state changes
            elif state_type == "brick_loaded":
                self._update_ui_with_brick_data()
            elif state_type == "brick_created":
                self._clear_editor_fields()
            elif state_type in ["brick_field_name", "brick_field_description", "brick_field_target_class", "brick_field_property_path"]:
                # Update specific UI fields when state changes
                self._update_field_from_state(state_type, new_value)
            elif state_type == "selected_brick":
                self.update_delete_button_visibility()
                
        except Exception as e:
            print(f"Error handling state change {state_type}: {e}")
            QMessageBox.warning(self, "State Error", f"Error updating UI: {e}")
    
    def _update_field_from_state(self, field_type: str, new_value: str):
        """Update specific UI field from state change"""
        try:
            # Block signals to prevent recursion
            if field_type == "brick_field_name" and hasattr(self, 'namelineEdit'):
                self.namelineEdit.blockSignals(True)
                self.namelineEdit.setText(new_value)
                self.namelineEdit.blockSignals(False)
            elif field_type == "brick_field_description" and hasattr(self, 'description'):
                self.description.blockSignals(True)
                self.description.setPlainText(new_value)
                self.description.blockSignals(False)
            elif field_type == "brick_field_target_class" and hasattr(self, 'targetLineEdit'):
                self.targetLineEdit.blockSignals(True)
                self.targetLineEdit.setText(new_value)
                self.targetLineEdit.blockSignals(False)
            elif field_type == "brick_field_property_path" and hasattr(self, 'propertyPathEdit'):
                self.propertyPathEdit.blockSignals(True)
                self.propertyPathEdit.setText(new_value)
                self.propertyPathEdit.blockSignals(False)
        except Exception as e:
            print(f"Error updating field {field_type}: {e}")
            # Re-enable signals on error
            try:
                if field_type == "brick_field_name" and hasattr(self, 'namelineEdit'):
                    self.namelineEdit.blockSignals(False)
                elif field_type == "brick_field_description" and hasattr(self, 'description'):
                    self.description.blockSignals(False)
                elif field_type == "brick_field_target_class" and hasattr(self, 'targetLineEdit'):
                    self.targetLineEdit.blockSignals(False)
                elif field_type == "brick_field_property_path" and hasattr(self, 'propertyPathEdit'):
                    self.propertyPathEdit.blockSignals(False)
            except:
                pass
    
    def _update_ui_with_brick_data(self):
        """Update UI fields with current brick data"""
        try:
            brick_state = app_state_manager.get_brick_state()
            if not brick_state:
                return
            
            # Block signals during UI updates
            self.namelineEdit.blockSignals(True)
            self.description.blockSignals(True)
            self.targetLineEdit.blockSignals(True)
            self.propertyPathEdit.blockSignals(True)
            self.radioNode.blockSignals(True)
            self.radioProperty.blockSignals(True)
            
            # Update fields
            self.namelineEdit.setText(brick_state.name)
            self.description.setPlainText(brick_state.description)
            
            # Update radio buttons
            if brick_state.object_type == "NodeShape":
                self.radioNode.setChecked(True)
            else:
                self.radioProperty.setChecked(True)
            
            # Update type-specific fields
            if brick_state.object_type == "NodeShape":
                self.targetLineEdit.setText(brick_state.target_class)
            else:
                self.propertyPathEdit.setText(brick_state.property_path)
            
            # Update property list
            self._update_property_list()
            
            # Re-enable signals
            self.namelineEdit.blockSignals(False)
            self.description.blockSignals(False)
            self.targetLineEdit.blockSignals(False)
            self.propertyPathEdit.blockSignals(False)
            self.radioNode.blockSignals(False)
            self.radioProperty.blockSignals(False)
            
        except Exception as e:
            print(f"Error updating UI with brick data: {e}")
            # Re-enable signals on error
            try:
                self.namelineEdit.blockSignals(False)
                self.description.blockSignals(False)
                self.targetLineEdit.blockSignals(False)
                self.propertyPathEdit.blockSignals(False)
                self.radioNode.blockSignals(False)
                self.radioProperty.blockSignals(False)
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
            libraries = brick_business_logic.get_libraries()
            self.libraryComboBox.clear()
            self.libraryComboBox.addItems(libraries)
            
            # Load bricks
            self.load_library()
            
        except Exception as e:
            print(f"Error loading initial data: {e}")
    
    # Library Operations
    def on_library_changed(self, library_name: str):
        """Handle library change"""
        brick_business_logic.set_active_library(library_name)
        self.load_library()
    
    def load_library(self):
        """Load library bricks"""
        try:
            # Block signals during library loading to prevent recursion
            self.libraryComboBox.blockSignals(True)
            self.nodeBrickList.blockSignals(True)
            self.propertyBrickList.blockSignals(True)
            
            # Save current selection
            current_library = self.libraryComboBox.currentText()
            
            # Update library list
            libraries = brick_business_logic.get_libraries()
            self.libraryComboBox.clear()
            self.libraryComboBox.addItems(libraries)
            
            # Restore current library selection if it still exists
            if current_library and current_library in libraries:
                self.libraryComboBox.setCurrentText(current_library)
            elif libraries:
                self.libraryComboBox.setCurrentIndex(0)
            
            # Load bricks from the active library
            bricks = brick_business_logic.get_bricks()
            self.nodeBrickList.clear()
            self.propertyBrickList.clear()
            
            for brick in bricks:
                display_text = f"{brick.get('name', 'Unknown')} ({brick.get('object_type', 'Unknown')})"
                list_item = QListWidgetItem(display_text)
                list_item.setData(Qt.ItemDataRole.UserRole, brick)
                
                if brick.get('object_type') == 'NodeShape':
                    self.nodeBrickList.addItem(list_item)
                else:
                    self.propertyBrickList.addItem(list_item)
            
            # Re-enable signals
            self.libraryComboBox.blockSignals(False)
            self.nodeBrickList.blockSignals(False)
            self.propertyBrickList.blockSignals(False)
            
        except Exception as e:
            print(f"Error loading library: {e}")
            # Re-enable signals on error
            self.libraryComboBox.blockSignals(False)
            self.nodeBrickList.blockSignals(False)
            self.propertyBrickList.blockSignals(False)
    
    def on_node_brick_selected(self, item):
        """Handle node brick selection"""
        brick_data = item.data(Qt.ItemDataRole.UserRole)
        if brick_data:
            brick_business_logic.load_brick(brick_data.get('brick_id'))
    
    def on_property_brick_selected(self, item):
        """Handle property brick selection"""
        brick_data = item.data(Qt.ItemDataRole.UserRole)
        if brick_data:
            brick_business_logic.load_brick(brick_data.get('brick_id'))
    
    def on_new_brick(self):
        """Handle new brick button"""
        brick_business_logic.create_new_brick()
    
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
            success, message = brick_business_logic.delete_brick(brick_id)
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_library()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def on_brick_selection_changed(self):
        """Handle brick selection change"""
        self.update_delete_button_visibility()
    
    def update_delete_button_visibility(self):
        """Update delete button visibility based on brick selection"""
        has_selection = self._get_selected_brick() is not None
        self.deleteBrick.setVisible(has_selection)
    
    def _get_selected_brick(self):
        """Get currently selected brick from either list"""
        # Check node brick list first
        if self.nodeBrickList.currentItem():
            return self.nodeBrickList.currentItem().data(Qt.ItemDataRole.UserRole)
        
        # Check property brick list
        if self.propertyBrickList.currentItem():
            return self.propertyBrickList.currentItem().data(Qt.ItemDataRole.UserRole)
        
        return None
    
    # Editor Operations
    def on_type_changed(self):
        """Handle brick type radio button change"""
        if self.radioNode.isChecked():
            brick_type = BrickType.NODE_SHAPE
        else:
            brick_type = BrickType.PROPERTY_SHAPE
        
        app_state_manager.set_brick_type(brick_type)
    
    def on_field_changed(self):
        """Handle field changes"""
        # Get current field values
        brick_data = self.brick_editor_component.get_data()
        
        # Update state (which will trigger business logic)
        app_state_manager.update_brick_field("name", brick_data.get("name", ""))
        app_state_manager.update_brick_field("description", brick_data.get("description", ""))
        app_state_manager.update_brick_field("target_class", brick_data.get("target_class", ""))
        app_state_manager.update_brick_field("property_path", brick_data.get("property_path", ""))
    
    def browse_ontology(self):
        """Handle ontology browser button click"""
        try:
            # Determine mode based on brick type
            current_type = app_state_manager.get_brick_type()
            mode = "classes" if current_type == BrickType.NODE_SHAPE else "properties"
            
            # Create and show ontology browser dialog
            dialog = SimpleOntologyBrowser(brick_business_logic.ontology_manager, self, mode)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_item = dialog.selected_item
                if selected_item:
                    # Set the appropriate field with the selected URI
                    if current_type == BrickType.NODE_SHAPE:
                        app_state_manager.update_brick_field("target_class", selected_item['uri'])
                    else:
                        app_state_manager.update_brick_field("property_path", selected_item['uri'])
        except Exception as e:
            print(f"Error browsing ontology: {e}")
    
    # Property Operations
    def on_property_selection_changed(self):
        """Handle property selection change"""
        # This will be handled by state updates
        pass
    
    def add_property(self):
        """Add a property using property editor"""
        dialog = PropertyEditorDialog(self, ontology_manager=brick_business_logic.ontology_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            property_data = dialog.get_property_data()
            if property_data.get('name'):
                success, message = brick_business_logic.add_property(property_data)
                if success:
                    self._update_property_list()
                else:
                    QMessageBox.warning(self, "Error", message)
    
    def add_property_brick(self):
        """Add an existing property brick to current node brick"""
        # Only allow adding property bricks to node shapes
        current_type = app_state_manager.get_brick_type()
        if current_type != BrickType.NODE_SHAPE:
            QMessageBox.warning(self, "Warning", "Property bricks can only be added to NodeShape bricks.")
            return
        
        dialog = PropertyBrickBrowser(self, brick_business_logic.brick_core)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_brick = dialog.selected_item
            if selected_brick:
                # Add property brick as a reference with full integration
                prop_name = selected_brick.get('name', 'Unknown')
                prop_data = {
                    'name': prop_name,  # Add the name field for validation
                    'property_brick_id': selected_brick.get('brick_id', ''),
                    'property_brick_name': selected_brick.get('name', 'Unknown'),
                    'property_path': selected_brick.get('property_path', ''),
                    'datatype': selected_brick.get('properties', {}).get('datatype', 'xsd:string'),
                    'constraints': selected_brick.get('properties', {}).get('constraints', []),
                    'is_property_brick': True,
                    'description': selected_brick.get('description', '')
                }
                
                success, message = brick_business_logic.add_property(prop_data)
                if success:
                    self._update_property_list()
                else:
                    QMessageBox.warning(self, "Error", message)
    
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
                success, message = brick_business_logic.add_constraint(prop_name, constraint_data, property_data)
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
            success, message = brick_business_logic.remove_property(prop_name)
            if success:
                self._update_property_list()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def on_property_double_clicked(self, item):
        """Handle property double-click - show constraint management dialog"""
        if not item:
            return
        
        prop_data = item.data(Qt.ItemDataRole.UserRole)
        if not prop_data:
            return
        
        # Show constraint management dialog
        self.show_constraint_manager(prop_data)
    
    def _get_selected_property(self):
        """Get currently selected property"""
        current_item = self.propertyList.currentItem()
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def _update_property_list(self):
        """Update property list display with enhanced formatting"""
        brick_state = app_state_manager.get_brick_state()
        if not brick_state or not hasattr(self, 'propertyList'):
            return
        
        # Block signals during updates to prevent recursion
        self.propertyList.blockSignals(True)
        
        try:
            self.propertyList.clear()
            added_properties = set()  # Track added properties to prevent duplicates
            
            for prop_name, prop_data in brick_state.properties.items():
                # Skip if this property was already added (prevent duplicates)
                if prop_name in added_properties:
                    continue
                added_properties.add(prop_name)
                
                # Create enhanced property display
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
        display_text = self._format_property_enhanced_text(prop_name, prop_data)
        list_item.setText(display_text)
        
        # Set visual styling based on property type
        if isinstance(prop_data, dict) and prop_data.get('is_property_brick'):
            # Property brick references get special styling with blue background only
            list_item.setBackground(QBrush(QColor(230, 240, 255)))  # Light blue background
        elif isinstance(prop_data, dict) and prop_data.get('constraints'):
            # Properties with constraints get subtle highlighting
            list_item.setBackground(QBrush(QColor(255, 248, 220)))  # Light yellow background
        
        return list_item
    
    def _format_property_display(self, prop_name: str, prop_data):
        """Format property information as rich HTML for better readability"""
        if isinstance(prop_data, dict):
            # Check if this is a property brick reference
            if prop_data.get('is_property_brick'):
                return self._format_property_brick_display(prop_name, prop_data)
            else:
                return self._format_regular_property_display(prop_name, prop_data)
        elif isinstance(prop_data, str):
            # Handle string prop_data (likely a simple property path)
            return f"""
            <div style="margin: 2px 0;">
                <div style="font-weight: bold; color: #2c3e50;">{prop_name}</div>
                <div style="font-size: 11px; color: #7f8c8d; margin-left: 10px;">📁 {prop_data}</div>
            </div>
            """
        else:
            # Handle other types
            return f"""
            <div style="margin: 2px 0;">
                <div style="font-weight: bold; color: #2c3e50;">{prop_name}</div>
                <div style="font-size: 11px; color: #7f8c8d; margin-left: 10px;">📄 {str(prop_data)}</div>
            </div>
            """
    
    def _format_property_brick_display(self, prop_name: str, prop_data):
        """Format property brick reference with enhanced display"""
        property_path = prop_data.get('property_path', '')
        description = prop_data.get('description', '')
        constraints = prop_data.get('constraints', [])
        
        constraint_info = ""
        if constraints:
            constraint_count = len(constraints)
            constraint_info = f'<div style="font-size: 10px; color: #e74c3c; margin-left: 10px;">🔒 {constraint_count} constraint{"s" if constraint_count != 1 else ""}</div>'
        
        description_info = ""
        if description:
            # Truncate long descriptions
            desc_text = description[:50] + "..." if len(description) > 50 else description
            description_info = f'<div style="font-size: 10px; color: #27ae60; margin-left: 10px;">📝 {desc_text}</div>'
        
        return f"""
        <div style="margin: 3px 0; padding: 2px;">
            <div style="font-weight: bold; color: #2980b9;">🧱 {prop_name}</div>
            <div style="font-size: 11px; color: #34495e; margin-left: 10px;">📁 {property_path}</div>
            {description_info}
            {constraint_info}
        </div>
        """
    
    def _format_regular_property_display(self, prop_name: str, prop_data):
        """Format regular property with enhanced display"""
        property_path = prop_data.get('path', '')
        datatype = prop_data.get('datatype', '')
        constraints = prop_data.get('constraints', [])
        
        # Build detail lines
        details = []
        
        if property_path:
            details.append(f'<div style="font-size: 11px; color: #7f8c8d; margin-left: 10px;">📁 {property_path}</div>')
        
        if datatype:
            # Show datatype with icon
            datatype_icon = self._get_datatype_icon(datatype)
            details.append(f'<div style="font-size: 11px; color: #8e44ad; margin-left: 10px;">{datatype_icon} {datatype}</div>')
        
        # Show constraints with better formatting
        if constraints:
            constraint_count = len(constraints)
            constraint_summary = self._format_constraint_summary(constraints)
            details.append(f'<div style="font-size: 10px; color: #e74c3c; margin-left: 10px;">🔒 {constraint_count} constraint{"s" if constraint_count != 1 else ""}: {constraint_summary}</div>')
        
        details_html = "".join(details)
        
        return f"""
        <div style="margin: 2px 0; padding: 2px;">
            <div style="font-weight: bold; color: #2c3e50;">📋 {prop_name}</div>
            {details_html}
        </div>
        """
    
    def _get_datatype_icon(self, datatype) -> str:
        """Get appropriate icon for datatype"""
        # Handle dict datatype
        if isinstance(datatype, dict):
            datatype_str = datatype.get('value', str(datatype))
        else:
            datatype_str = str(datatype)
        
        datatype_lower = datatype_str.lower()
        if 'string' in datatype_lower:
            return '📝'
        elif 'int' in datatype_lower or 'decimal' in datatype_lower:
            return '🔢'
        elif 'bool' in datatype_lower:
            return '☑️'
        elif 'date' in datatype_lower or 'time' in datatype_lower:
            return '📅'
        elif 'uri' in datatype_lower:
            return '🔗'
        else:
            return '📄'
    
    def _format_constraint_summary(self, constraints):
        """Create a concise summary of constraints"""
        if not constraints:
            return ""
        
        constraint_types = []
        for constraint in constraints[:MAX_CONSTRAINTS_IN_SUMMARY]:  # Show max constraints in summary
            constraint_type = constraint.get('constraint_type', 'unknown')
            constraint_value = constraint.get('value', '')
            
            # Format constraint type nicely
            type_mapping = {
                'minLength': 'min len',
                'maxLength': 'max len',
                'minInclusive': 'min',
                'maxInclusive': 'max',
                'minExclusive': 'min excl',
                'maxExclusive': 'max excl',
                'pattern': 'pattern',
                'datatype': 'type'
            }
            
            nice_type = type_mapping.get(constraint_type, constraint_type)
            constraint_types.append(f"{nice_type}={constraint_value}")
        
        if len(constraints) > MAX_CONSTRAINTS_IN_SUMMARY:
            constraint_types.append(f"... ({len(constraints) - MAX_CONSTRAINTS_IN_SUMMARY} more)")
        
        return ", ".join(constraint_types)
    
    def _html_to_formatted_text(self, html_text):
        """Convert HTML to formatted plain text for QListWidget display"""
        import re
        
        # Remove HTML tags but keep the content with proper formatting
        # Extract text content and preserve structure
        
        # Remove div tags and replace with newlines
        text = re.sub(r'<div[^>]*>', '', html_text)
        text = re.sub(r'</div>', '\n', text)
        
        # Remove other HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Clean up extra whitespace and newlines
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Add indentation for sub-items
                if line.startswith('📁') or line.startswith('📝') or line.startswith('🔒') or line.startswith('🔢'):
                    formatted_lines.append('  ' + line)
                else:
                    formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _format_property_enhanced_text(self, prop_name: str, prop_data):
        """Format property information as enhanced plain text for QListWidget"""
        if isinstance(prop_data, dict):
            # Check if this is a property brick reference
            if prop_data.get('is_property_brick'):
                return self._format_property_brick_text(prop_name, prop_data)
            else:
                return self._format_regular_property_text(prop_name, prop_data)
        elif isinstance(prop_data, str):
            # Handle string prop_data (likely a simple property path)
            return f"{prop_name}\n  📁 {prop_data}"
        else:
            # Handle other types
            return f"{prop_name}\n  📄 {str(prop_data)}"
    
    def _format_property_brick_text(self, prop_name: str, prop_data):
        """Format property brick reference with enhanced text display"""
        property_path = prop_data.get('property_path', '')
        description = prop_data.get('description', '')
        constraints = prop_data.get('constraints', [])
        
        lines = [f"🧱 {prop_name}"]
        
        if property_path:
            lines.append(f"  📁 {property_path}")
        
        if description:
            # Truncate long descriptions
            desc_text = description[:50] + "..." if len(description) > 50 else description
            lines.append(f"  📝 {desc_text}")
        
        if constraints:
            constraint_count = len(constraints)
            constraint_summary = self._format_constraint_summary(constraints)
            lines.append(f"  🔒 {constraint_count} constraint{'s' if constraint_count != 1 else ''}: {constraint_summary}")
        
        return "\n".join(lines)
    
    def _format_regular_property_text(self, prop_name: str, prop_data):
        """Format regular property with enhanced text display"""
        property_path = prop_data.get('path', '')
        datatype = prop_data.get('datatype', '')
        constraints = prop_data.get('constraints', [])
        
        lines = [f"📋 {prop_name}"]
        
        if property_path:
            lines.append(f"  📁 {property_path}")
        
        if datatype:
            # Show datatype with icon
            # Handle dict datatype
            if isinstance(datatype, dict):
                datatype_str = datatype.get('value', str(datatype))
            else:
                datatype_str = str(datatype)
            datatype_icon = self._get_datatype_icon(datatype)
            lines.append(f"  {datatype_icon} {datatype_str}")
        
        # Show constraints with better formatting
        if constraints:
            constraint_count = len(constraints)
            constraint_summary = self._format_constraint_summary(constraints)
            lines.append(f"  🔒 {constraint_count} constraint{'s' if constraint_count != 1 else ''}: {constraint_summary}")
        
        return "\n".join(lines)
    
    def show_constraint_manager(self, prop_data):
        """Show constraint management dialog for a property"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel, QMessageBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Constraints for {prop_data.get('name', 'Property')}")
        dialog.setGeometry(300, 300, 500, 400)
        
        layout = QVBoxLayout()
        
        # Property info
        info_label = QLabel(f"Property: {prop_data.get('name', 'Unknown')}")
        if 'path' in prop_data and prop_data['path']:
            info_label.setText(f"{info_label.text()} | Path: {prop_data['path']}")
        layout.addWidget(info_label)
        
        # Constraints list
        constraints_list = QListWidget()
        constraints = prop_data.get('constraints', [])
        
        if constraints:
            for i, constraint in enumerate(constraints):
                constraint_text = f"{constraint.get('constraint_type', 'Unknown')}: {constraint.get('value', 'No value')}"
                list_item = QListWidgetItem(constraint_text)
                list_item.setData(Qt.ItemDataRole.UserRole, i)  # Store index
                constraints_list.addItem(list_item)
        else:
            constraints_list.addItem(QListWidgetItem("No constraints defined"))
        
        layout.addWidget(constraints_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Constraint")
        edit_btn = QPushButton("Edit Constraint")
        delete_btn = QPushButton("Delete Constraint")
        close_btn = QPushButton("Close")
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # Button functions
        def add_new_constraint():
            constraint_dialog = ConstraintEditorDialog(self, prop_data)
            if constraint_dialog.exec() == QDialog.DialogCode.Accepted:
                new_constraint = constraint_dialog.get_constraint_data()
                if new_constraint:
                    # Update brick state (pass prop_data to ensure full property data is stored)
                    success, message = brick_business_logic.add_constraint(prop_data.get('name'), new_constraint, prop_data)
                    if success:
                        self._update_property_list()
                        refresh_constraint_list()
                    else:
                        QMessageBox.warning(self, "Error", message)
        
        def refresh_constraint_list():
            nonlocal constraints
            constraints_list.clear()
            # Get fresh constraints from brick state
            brick_state = app_state_manager.get_brick_state()
            prop_name = prop_data.get('name')
            if prop_name and prop_name in brick_state.properties:
                constraints = brick_state.properties[prop_name].get('constraints', [])
                # Also update prop_data to stay in sync
                prop_data['constraints'] = constraints
            else:
                constraints = prop_data.get('constraints', [])
            
            if constraints:
                for i, constraint in enumerate(constraints):
                    constraint_text = f"{constraint.get('constraint_type', 'Unknown')}: {constraint.get('value', 'No value')}"
                    list_item = QListWidgetItem(constraint_text)
                    list_item.setData(Qt.ItemDataRole.UserRole, i)  # Store index
                    constraints_list.addItem(list_item)
            else:
                constraints_list.addItem(QListWidgetItem("No constraints defined"))
        
        def edit_selected_constraint():
            current_item = constraints_list.currentItem()
            if not current_item or not constraints:
                QMessageBox.warning(dialog, "Warning", "Please select a constraint to edit.")
                return
            
            constraint_index = current_item.data(Qt.ItemDataRole.UserRole)
            if constraint_index is not None and constraint_index < len(constraints):
                # Edit existing constraint
                constraint_dialog = ConstraintEditorDialog(self, prop_data)
                constraint_dialog.set_constraint_data(constraints[constraint_index])
                if constraint_dialog.exec() == QDialog.DialogCode.Accepted:
                    updated_constraint = constraint_dialog.get_constraint_data()
                    if updated_constraint:
                        # Update constraint at the same index
                        prop_name = prop_data.get('name')
                        if prop_name:
                            success, message = brick_business_logic.update_constraint(prop_name, constraint_index, updated_constraint)
                            if success:
                                self._update_property_list()
                                refresh_constraint_list()
                            else:
                                QMessageBox.warning(self, "Error", message)
        
        def delete_selected_constraint():
            current_item = constraints_list.currentItem()
            if not current_item or not constraints:
                QMessageBox.warning(dialog, "Warning", "Please select a constraint to delete.")
                return
            
            constraint_index = current_item.data(Qt.ItemDataRole.UserRole)
            if constraint_index is not None and constraint_index < len(constraints):
                # Confirm deletion
                constraint = constraints[constraint_index]
                reply = QMessageBox.question(
                    dialog, "Delete Constraint",
                    f"Are you sure you want to delete the constraint '{constraint.get('constraint_type', 'Unknown')}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    constraints.pop(constraint_index)
                    # Update brick state
                    prop_name = prop_data.get('name')
                    if prop_name:
                        # Remove constraint by updating property without that constraint
                        success, message = brick_business_logic.remove_constraint(prop_name, constraint_index)
                        if success:
                            self._update_property_list()
                            refresh_constraint_list()
                        else:
                            QMessageBox.warning(self, "Error", message)
        
        # Connect buttons
        add_btn.clicked.connect(add_new_constraint)
        edit_btn.clicked.connect(edit_selected_constraint)
        delete_btn.clicked.connect(delete_selected_constraint)
        close_btn.clicked.connect(dialog.reject)
        
        # Enable/disable buttons based on selection
        def update_button_states():
            has_selection = constraints_list.currentItem() is not None and bool(constraints)
            edit_btn.setEnabled(has_selection)
            delete_btn.setEnabled(has_selection)
        
        constraints_list.itemSelectionChanged.connect(update_button_states)
        update_button_states()  # Initial state
        
        dialog.exec()
    
    # Control Operations
    def save_brick(self):
        """Save current brick"""
        success, message = brick_business_logic.save_current_brick()
        if success:
            QMessageBox.information(self, "Success", message)
            self.load_library()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def cancel_edit(self):
        """Cancel edit and return to browse mode"""
        app_state_manager.set_ui_state(UIState.BROWSE)
    
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
            current_libraries = brick_business_logic.get_libraries()
            if library_name in current_libraries:
                QMessageBox.warning(self, "Warning", f"Library '{library_name}' already exists.")
                return
            
            try:
                # For now, just show a message
                QMessageBox.information(self, "Success", 
                    f"Library '{library_name}' would be created here!")
                
                # Reload libraries
                self._load_initial_data()
                
                # Switch to the new library
                self.libraryComboBox.setCurrentText(library_name)
                
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
                libraries = brick_business_logic.get_libraries()
                if current_library not in libraries:
                    QMessageBox.warning(self, "Error", f"Library '{current_library}' not found.")
                    return
                
                # Archive before deletion
                repository_path = brick_business_logic.brick_core.repository.repository_path
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


def main():
    """Main entry point for refactored GUI"""
    app = QApplication(sys.argv)
    gui = RefactoredBrickEditor()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
