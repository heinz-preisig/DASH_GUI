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
from core.brick_core_simple import sanitize_filename
from ui.ui_abstraction import UIManager, BrickEditorComponent, BrickListComponent, LibraryComponent, PropertyListComponent
from ui.property_formatters import (
    format_property_display, format_property_enhanced_text,
    format_constraint_summary, get_datatype_icon
)
from ui.constraint_manager import show_constraint_manager
from gui_components import (
    PropertyEditorDialog, PropertyBrickBrowser, ConstraintEditorDialog,
    SimpleOntologyBrowser
)


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
        # self.setGeometry(100, 100, 650, 950)
        
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
        self.newNode.clicked.connect(self.on_new_node)
        self.newProperty.clicked.connect(self.on_new_property)
        self.deleteBrick.clicked.connect(self.on_delete_brick)
        self.newLibrary.clicked.connect(self.on_new_library)
        self.deleteLibrary.clicked.connect(self.on_delete_library)
        self.downloadOntology.clicked.connect(self.on_download_ontology)
        
        # Brick selection signals for delete button visibility
        self.nodeBrickList.itemSelectionChanged.connect(self.on_brick_selection_changed)
        self.propertyBrickList.itemSelectionChanged.connect(self.on_brick_selection_changed)
        
        # Editor signals
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
            # Update fields
            self.namelineEdit.setText(brick_state.name)
            self.description.setPlainText(brick_state.description)
            
            # Update type label
            self.currentTypeLabel.setText(brick_state.object_type)
            
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
    
    def on_new_node(self):
        """Handle new node brick button"""
        brick_business_logic.create_new_brick(BrickType.NODE_SHAPE)
    
    def on_new_property(self):
        """Handle new property brick button"""
        brick_business_logic.create_new_brick(BrickType.PROPERTY_SHAPE)
    
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
                    uri = selected_item['uri']
                    if current_type == BrickType.NODE_SHAPE:
                        app_state_manager.update_brick_field("target_class", uri)
                    else:
                        app_state_manager.update_brick_field("property_path", uri)
                    
                    # Auto-set name from last element of URI if name is empty/default
                    current_name = app_state_manager.get_brick_dict().get('name', '')
                    if not current_name or current_name.startswith('New '):
                        # Extract last element from URI (e.g., http://schema.org/ns#Address -> Address)
                        name = uri
                        if '#' in uri:
                            name = uri.split('#')[-1]
                        elif '/' in uri:
                            name = uri.split('/')[-1]
                        if name:
                            app_state_manager.update_brick_field("name", name)
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
        show_constraint_manager(self, prop_data, self._update_property_list)
    
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
        display_text = format_property_enhanced_text(prop_name, prop_data)
        list_item.setText(display_text)
        
        # Set visual styling based on property type
        if isinstance(prop_data, dict) and prop_data.get('is_property_brick'):
            # Property brick references get special styling with blue background only
            list_item.setBackground(QBrush(QColor(230, 240, 255)))  # Light blue background
        elif isinstance(prop_data, dict) and prop_data.get('constraints'):
            # Properties with constraints get subtle highlighting
            list_item.setBackground(QBrush(QColor(255, 248, 220)))  # Light yellow background
        
        return list_item
    
    # Control Operations
    def save_brick(self):
        """Save current brick and auto-generate SHACL Turtle"""
        success, message = brick_business_logic.save_current_brick()
        if success:
            # Auto-generate SHACL Turtle file
            self._generate_shacl_for_saved_brick()
            QMessageBox.information(self, "Success", message)
            self.load_library()
        else:
            QMessageBox.warning(self, "Error", message)

    def _generate_shacl_for_saved_brick(self):
        """Generate SHACL Turtle for the current brick after save"""
        try:
            # Get current brick data
            brick_data = app_state_manager.get_brick_dict()
            brick_id = brick_data.get('brick_id')
            print(f"DEBUG: Generating SHACL for brick_id={brick_id}")
            if not brick_id:
                print("DEBUG: No brick_id, skipping SHACL generation")
                return

            # Get current library path
            library_name = app_state_manager.get_selected_library()
            from shared_libraries.library_manager import SharedLibraryManager
            lib_manager = SharedLibraryManager()

            # Find library directory
            lib_path = None
            lib_info = None
            for lib in lib_manager.scan_brick_libraries():
                if lib['name'] == library_name:
                    lib_path = Path(lib['absolute_path'])
                    lib_info = lib
                    break

            if not lib_path:
                return

            # Validate property brick references
            missing_refs = self._validate_property_references(brick_data, lib_path)
            if missing_refs:
                print(f"Warning: Brick '{brick_id}' references missing property bricks: {missing_refs}")

            # Generate SHACL Turtle
            from core.brick_generator import SHACLBrickGenerator, BrickLibrary, SHACLBrick
            temp_lib = BrickLibrary(library_name, "", "System")
            brick = SHACLBrick.from_dict(brick_data)
            temp_lib.add_brick(brick)

            # Also load referenced property bricks into temp library
            for ref_id in self._get_property_references(brick_data):
                ref_file = lib_path / f"{ref_id}.json"
                if ref_file.exists():
                    import json
                    with open(ref_file, 'r') as f:
                        ref_data = json.load(f)
                        ref_brick = SHACLBrick.from_dict(ref_data)
                        temp_lib.add_brick(ref_brick)

            generator = SHACLBrickGenerator(temp_lib)
            graph = generator.brick_to_shacl(brick)
            shacl_content = graph.serialize(format="turtle")

            # Write to file with name_UUID format (matching JSON filename)
            safe_name = sanitize_filename(brick_data.get('name', ''))
            output_file = lib_path / f"{safe_name}_{brick_id}.ttl"
            with open(output_file, 'w') as f:
                f.write(shacl_content)
            print(f"DEBUG: Wrote TTL file: {output_file}")

        except Exception as e:
            print(f"Warning: Failed to auto-generate SHACL: {e}")
            import traceback
            traceback.print_exc()

    def _get_property_references(self, brick_data: dict) -> list:
        """Extract property brick IDs referenced by this brick"""
        refs = []
        for prop_data in brick_data.get('properties', {}).values():
            if isinstance(prop_data, dict) and prop_data.get('is_property_brick'):
                prop_id = prop_data.get('property_brick_id')
                if prop_id:
                    refs.append(prop_id)
        return refs

    def _validate_property_references(self, brick_data: dict, lib_path: Path) -> list:
        """Check if all referenced property bricks exist"""
        missing = []
        for prop_id in self._get_property_references(brick_data):
            ref_file = lib_path / f"{prop_id}.json"
            if not ref_file.exists():
                missing.append(prop_id)
        return missing
    
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

    def on_download_ontology(self):
        """Handle download ontology button click"""
        dialog = OntologySearchDialog(self, brick_business_logic.ontology_manager)
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
        from pathlib import Path
        
        # Download with extended timeout for large ontologies
        req = urllib.request.Request(url, headers={'Accept': 'text/turtle,application/rdf+xml,application/n-triples'})
        with urllib.request.urlopen(req, timeout=60) as response:
            content = response.read()
        
        # Determine file extension
        content_type = response.headers.get('Content-Type', '')
        if 'turtle' in content_type or 'ttl' in url:
            ext = '.ttl'
        elif 'xml' in content_type or 'rdf' in url:
            ext = '.rdf'
        else:
            ext = '.ttl'  # Default
        
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
