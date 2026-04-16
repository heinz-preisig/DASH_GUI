#!/usr/bin/env python3
"""
Stateful SHACL Brick Editor using Qt Designer UI file
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QMessageBox, QDialog, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi

# Import existing components
from core.brick_core_simple import BrickCore
from core.ontology_manager import OntologyManager
from gui_components import (
    PropertyEditorDialog, PropertyBrickBrowser, ConstraintEditorDialog,
    SimpleOntologyBrowser, CorrectedOntologyManager
)


class UIStateController:
    """Controls UI state and component visibility"""
    
    BROWSE = "browse"
    EDIT = "edit" 
    CREATE = "create"
    
    def __init__(self, ui_components):
        self.state = self.BROWSE
        self.ui = ui_components
        self.current_brick_type = "NodeShape"
        
    def set_state(self, new_state):
        """Set new state and update UI"""
        self.state = new_state
        self.update_visibility()
        
    def update_brick_type(self, brick_type):
        """Update brick type and field visibility"""
        self.current_brick_type = brick_type
        self._update_field_visibility()
        
    def update_visibility(self):
        """Update component visibility based on current state"""
        if self.state == self.BROWSE:
            self._apply_browse_visibility()
        elif self.state == self.EDIT:
            self._apply_edit_visibility()
        elif self.state == self.CREATE:
            self._apply_create_visibility()
            
        # Always update field visibility based on brick type
        self._update_field_visibility()
        self._update_button_states()
    
    def _update_field_visibility(self):
        """Show/hide target vs property path fields"""
        if self.current_brick_type == "NodeShape":
            # Show target class fields
            self.ui.targetLabel.show()
            self.ui.targetLineEdit.show()
            self.ui.propertyLabel.hide()
            self.ui.propertyPathEdit.hide()
            self.ui.ontologyTargetBrowser.show()
            self.ui.ontologyPathBrowser.hide()
        else:  # PropertyShape
            # Show property path fields
            self.ui.targetLabel.hide()
            self.ui.targetLineEdit.hide()
            self.ui.propertyLabel.show()
            self.ui.propertyPathEdit.show()
            self.ui.ontologyTargetBrowser.hide()
            self.ui.ontologyPathBrowser.show()
    
    def _update_button_states(self):
        """Update button states based on current context"""
        has_selected_property = self._has_selected_property()
        is_node_shape = self.current_brick_type == "NodeShape"
        
        if self.state == self.BROWSE:
            self.ui.addProperty.setEnabled(False)
            self.ui.addPropertyBrick.setEnabled(False)
            self.ui.addConstraint.setEnabled(False)
            
        elif self.state == self.EDIT:
            self.ui.addProperty.setEnabled(True)
            self.ui.addPropertyBrick.setEnabled(is_node_shape)  # Only for NodeShape
            self.ui.addConstraint.setEnabled(has_selected_property)
            
        elif self.state == self.CREATE:
            self.ui.addProperty.setEnabled(True)
            self.ui.addPropertyBrick.setEnabled(is_node_shape)  # Only for NodeShape
            self.ui.addConstraint.setEnabled(False)  # No property selected yet
    
    def _has_selected_property(self):
        """Check if a property is selected in propertyList"""
        return self.ui.propertyList.currentItem() is not None
    
    def _apply_browse_visibility(self):
        """Apply browse state visibility"""
        self.ui.newBrick.show()
        self.ui.editorPanel.hide()
        self.ui.radioNode.hide()
        self.ui.radioProperty.hide()
        # Delete button visibility handled by selection state
        
    def _apply_edit_visibility(self):
        """Apply edit state visibility"""
        self.ui.newBrick.hide()
        self.ui.editorPanel.show()
        self.ui.radioNode.hide()
        self.ui.radioProperty.hide()
        
    def _apply_create_visibility(self):
        """Apply create state visibility"""
        self.ui.newBrick.hide()
        self.ui.editorPanel.show()
        self.ui.radioNode.show()
        self.ui.radioProperty.show()


class StatefulBrickEditor(QMainWindow):
    """Stateful SHACL Brick Editor using Qt Designer UI"""
    
    def __init__(self):
        super().__init__()
        
        # Load UI from file
        ui_path = Path(__file__).parent / "ui" / "main_window.ui"
        loadUi(str(ui_path), self)
        
        # Initialize components
        self.brick_core = BrickCore()
        self.ontology_manager = CorrectedOntologyManager()
        self.state_controller = UIStateController(self)
        
        # Setup window
        self.setWindowTitle("Stateful SHACL Brick Editor")
        self.setGeometry(100, 100, 800, 700)
        
        # Connect signals
        self._connect_signals()
        
        # Initialize state
        self.state_controller.set_state(UIStateController.BROWSE)
        
        # Initialize delete button visibility
        self.update_delete_button_visibility()
        
        # Load library
        self.load_library()
    
    def _connect_signals(self):
        """Connect UI signals to handlers"""
        # Library signals
        self.libraryComboBox.currentTextChanged.connect(self.on_library_changed)
        self.nodeBrickList.itemDoubleClicked.connect(self.on_node_brick_selected)
        self.propertyBrickList.itemDoubleClicked.connect(self.on_property_brick_selected)
        self.newBrick.clicked.connect(self.on_new_brick)
        self.deleteBrick.clicked.connect(self.on_delete_brick)
        
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
        
        # Control signals
        self.saveBrick.clicked.connect(self.save_brick)
        self.cancelBrickEdit.clicked.connect(self.cancel_edit)
    
    def on_library_changed(self, library_name: str):
        """Handle library change"""
        try:
            self.brick_core.set_active_library(library_name)
            self.load_library()
        except Exception as e:
            print(f"Error loading library: {e}")
    
    def on_node_brick_selected(self, item):
        """Handle node brick selection"""
        brick = item.data(Qt.ItemDataRole.UserRole)
        if brick:
            self.brick_core.load_brick(brick.brick_id)
            self.state_controller.set_state(UIStateController.EDIT)
            self.update_ui()
    
    def on_property_brick_selected(self, item):
        """Handle property brick selection"""
        brick = item.data(Qt.ItemDataRole.UserRole)
        if brick:
            self.brick_core.load_brick(brick.brick_id)
            self.state_controller.set_state(UIStateController.EDIT)
            self.update_ui()
    
    def on_new_brick(self):
        """Handle new brick button"""
        self.brick_core.create_brick()  # Will use default NodeShape
        self.state_controller.set_state(UIStateController.CREATE)
        self.update_ui()
    
    def on_delete_brick(self):
        """Handle delete brick button"""
        selected_brick = self._get_selected_brick()
        if not selected_brick:
            QMessageBox.warning(self, "Warning", "Please select a brick to delete.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Delete Brick", 
            f"Are you sure you want to delete '{selected_brick.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.brick_core.delete_brick(selected_brick.brick_id):
                QMessageBox.information(self, "Success", "Brick deleted successfully!")
                self.load_library()
                self.update_delete_button_visibility()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete brick.")
    
    def on_brick_selection_changed(self):
        """Handle brick selection change"""
        self.update_delete_button_visibility()
    
    def _get_selected_brick(self):
        """Get currently selected brick from either list"""
        # Check node brick list first
        if self.nodeBrickList.currentItem():
            return self.nodeBrickList.currentItem().data(Qt.ItemDataRole.UserRole)
        
        # Check property brick list
        if self.propertyBrickList.currentItem():
            return self.propertyBrickList.currentItem().data(Qt.ItemDataRole.UserRole)
        
        return None
    
    def update_delete_button_visibility(self):
        """Update delete button visibility based on brick selection"""
        has_selection = self._get_selected_brick() is not None
        self.deleteBrick.setVisible(has_selection)
    
    def on_type_changed(self):
        """Handle brick type radio button change"""
        if self.radioNode.isChecked():
            brick_type = "NodeShape"
        else:
            brick_type = "PropertyShape"
        
        self.state_controller.update_brick_type(brick_type)
        
        # Update brick core if we have a current brick
        if self.brick_core.current_brick:
            self.brick_core.current_brick.object_type = brick_type
    
    def on_field_changed(self):
        """Handle field changes"""
        if not self.brick_core.current_brick:
            return
        
        # Block signals to prevent recursive updates
        self.namelineEdit.blockSignals(True)
        self.description.blockSignals(True)
        self.targetLineEdit.blockSignals(True)
        self.propertyPathEdit.blockSignals(True)
        
        current_type = self.state_controller.current_brick_type
        if current_type == "NodeShape":
            self.brick_core.update_current_brick(
                name=self.namelineEdit.text(),
                description=self.description.toPlainText(),
                target_class=self.targetLineEdit.text(),
                property_path=""
            )
        else:  # PropertyShape
            self.brick_core.update_current_brick(
                name=self.namelineEdit.text(),
                description=self.description.toPlainText(),
                target_class="",
                property_path=self.propertyPathEdit.text()
            )
        
        # Re-enable signals
        self.namelineEdit.blockSignals(False)
        self.description.blockSignals(False)
        self.targetLineEdit.blockSignals(False)
        self.propertyPathEdit.blockSignals(False)
    
    def on_property_selection_changed(self):
        """Handle property selection change"""
        self.state_controller.update_visibility()
    
    def browse_ontology(self):
        """Handle ontology browser button click"""
        try:
            # Determine mode based on brick type
            if self.state_controller.current_brick_type == "NodeShape":
                mode = "classes"
            else:
                mode = "properties"
            
            # Create and show ontology browser dialog
            dialog = SimpleOntologyBrowser(self.ontology_manager, self, mode)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_item = dialog.selected_item
                if selected_item:
                    # Set the appropriate field with the selected URI
                    if self.state_controller.current_brick_type == "NodeShape":
                        self.targetLineEdit.setText(selected_item['uri'])
                    else:
                        self.propertyPathEdit.setText(selected_item['uri'])
        except Exception as e:
            print(f"Error browsing ontology: {e}")
    
    def add_property(self):
        """Add a property using property editor"""
        if not self.brick_core.current_brick:
            return
        
        # Open property editor dialog
        dialog = PropertyEditorDialog(self, ontology_manager=self.ontology_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            property_data = dialog.get_property_data()
            if property_data.get('name'):
                self.brick_core.add_property(property_data['name'], property_data)
                self.update_ui()
    
    def add_property_brick(self):
        """Add an existing property brick to current node brick"""
        if not self.brick_core.current_brick:
            return
        
        # Only allow adding property bricks to node shapes
        if self.brick_core.current_brick.object_type != "NodeShape":
            QMessageBox.warning(self, "Warning", "Property bricks can only be added to NodeShape bricks.")
            return
        
        # Open property brick browser
        dialog = PropertyBrickBrowser(self, self.brick_core)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_brick = dialog.selected_brick
            if selected_brick:
                # Add property brick as a reference
                self.add_property_brick_reference(selected_brick)
                self.update_ui()
    
    def add_property_brick_reference(self, property_brick):
        """Add a property brick reference to current node brick"""
        # Create a property reference that points to the property brick
        prop_name = property_brick.name
        prop_data = {
            'property_brick_id': property_brick.brick_id,
            'property_brick_name': property_brick.name,
            'property_path': property_brick.property_path,
            'datatype': property_brick.properties.get('datatype', 'xsd:string') if property_brick.properties else 'xsd:string',
            'constraints': property_brick.properties.get('constraints', []) if property_brick.properties else [],
            'is_property_brick': True,
            'description': property_brick.description
        }
        
        self.brick_core.add_property(prop_name, prop_data)
    
    def add_constraint(self):
        """Add constraint to selected property"""
        if not self.brick_core.current_brick:
            return
        
        current_item = self.propertyList.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a property first.")
            return
        
        prop_data = current_item.data(Qt.ItemDataRole.UserRole)
        if not prop_data:
            return
        
        # Open constraint editor dialog
        dialog = ConstraintEditorDialog(self, prop_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            constraint_data = dialog.get_constraint_data()
            if constraint_data:
                # Add constraint to property
                if 'constraints' not in prop_data:
                    prop_data['constraints'] = []
                prop_data['constraints'].append(constraint_data)
                # Update brick core property data to persist changes
                prop_name = prop_data.get('name')
                if prop_name:
                    self.brick_core.add_property(prop_name, prop_data)
                self.update_ui()
    
    def on_property_double_clicked(self, item):
        """Handle property double-click - show constraint management dialog"""
        if not item:
            return
        
        prop_data = item.data(Qt.ItemDataRole.UserRole)
        if not prop_data:
            return
        
        # Show constraint management dialog
        self.show_constraint_manager(prop_data)
    
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
                constraint_text = f"{constraint.get('type', 'Unknown')}: {constraint.get('value', 'No value')}"
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
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        # Function to refresh constraint list
        def refresh_constraint_list():
            constraints_list.clear()
            constraints = prop_data.get('constraints', [])
            
            if constraints:
                for i, constraint in enumerate(constraints):
                    constraint_text = f"{constraint.get('type', 'Unknown')}: {constraint.get('value', 'No value')}"
                    list_item = QListWidgetItem(constraint_text)
                    list_item.setData(Qt.ItemDataRole.UserRole, i)  # Store index
                    constraints_list.addItem(list_item)
            else:
                constraints_list.addItem(QListWidgetItem("No constraints defined"))
            
            update_button_states()
        
        # Button connections
        def add_new_constraint():
            constraint_dialog = ConstraintEditorDialog(self, prop_data)
            if constraint_dialog.exec() == QDialog.DialogCode.Accepted:
                constraint_data = constraint_dialog.get_constraint_data()
                if constraint_data:
                    if 'constraints' not in prop_data:
                        prop_data['constraints'] = []
                    prop_data['constraints'].append(constraint_data)
                    # Update brick core property data to persist changes
                    prop_name = prop_data.get('name')
                    if prop_name:
                        self.brick_core.add_property(prop_name, prop_data)
                    self.update_ui()
                    # Refresh constraint list instead of closing dialog
                    refresh_constraint_list()
        
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
                        constraints[constraint_index] = updated_constraint
                        # Update brick core property data to persist changes
                        prop_name = prop_data.get('name')
                        if prop_name:
                            self.brick_core.add_property(prop_name, prop_data)
                        self.update_ui()
                        # Refresh constraint list instead of closing dialog
                        refresh_constraint_list()
        
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
                    f"Are you sure you want to delete the constraint '{constraint.get('type', 'Unknown')}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    constraints.pop(constraint_index)
                    # Update brick core property data to persist changes
                    prop_name = prop_data.get('name')
                    if prop_name:
                        self.brick_core.add_property(prop_name, prop_data)
                    self.update_ui()
                    # Refresh constraint list instead of closing dialog
                    refresh_constraint_list()
        
        add_btn.clicked.connect(add_new_constraint)
        edit_btn.clicked.connect(edit_selected_constraint)
        delete_btn.clicked.connect(delete_selected_constraint)
        close_btn.clicked.connect(dialog.reject)
        
        # Enable/disable buttons based on selection
        def update_button_states():
            has_selection = constraints_list.currentItem() is not None and constraints
            edit_btn.setEnabled(has_selection)
            delete_btn.setEnabled(has_selection)
        
        constraints_list.itemSelectionChanged.connect(update_button_states)
        update_button_states()  # Initial state
        
        dialog.exec()
    
    def save_brick(self):
        """Save current brick"""
        if self.brick_core.save_brick():
            QMessageBox.information(self, "Success", "Brick saved successfully!")
            self.load_library()
            self.state_controller.set_state(UIStateController.BROWSE)
            self.update_ui()
        else:
            QMessageBox.warning(self, "Error", "Failed to save brick. Please check required fields.")
    
    def cancel_edit(self):
        """Cancel edit and return to browse mode"""
        self.brick_core.current_brick = None
        self.state_controller.set_state(UIStateController.BROWSE)
        self.update_ui()
    
    def load_library(self):
        """Load library bricks"""
        try:
            # Block signals during library loading to prevent recursion
            self.libraryComboBox.blockSignals(True)
            self.nodeBrickList.blockSignals(True)
            self.propertyBrickList.blockSignals(True)
            
            libraries = self.brick_core.get_libraries()
            self.libraryComboBox.clear()
            self.libraryComboBox.addItems(libraries)
            
            bricks = self.brick_core.get_all_bricks()
            self.nodeBrickList.clear()
            self.propertyBrickList.clear()
            
            for brick in bricks:
                display_text = f"{brick.name} ({brick.object_type})"
                list_item = QListWidgetItem(display_text)
                list_item.setData(Qt.ItemDataRole.UserRole, brick)
                
                if brick.object_type == "NodeShape":
                    self.nodeBrickList.addItem(list_item)
                else:
                    self.propertyBrickList.addItem(list_item)
            
            # Re-enable signals
            self.libraryComboBox.blockSignals(False)
            self.nodeBrickList.blockSignals(False)
            self.propertyBrickList.blockSignals(False)
            
        except Exception as e:
            print(f"Error loading library: {e}")
            self.libraryComboBox.clear()
            self.libraryComboBox.addItems(["default"])
            # Re-enable signals on error
            self.libraryComboBox.blockSignals(False)
            self.nodeBrickList.blockSignals(False)
            self.propertyBrickList.blockSignals(False)
    
    def update_ui(self):
        """Update UI to reflect current brick"""
        brick = self.brick_core.current_brick
        if not brick:
            return
        
        # Block signals during UI updates
        self.libraryComboBox.blockSignals(True)
        self.namelineEdit.blockSignals(True)
        self.description.blockSignals(True)
        self.targetLineEdit.blockSignals(True)
        self.propertyPathEdit.blockSignals(True)
        
        self.namelineEdit.setText(brick.name)
        self.description.setText(brick.description)
        
        # Update radio buttons
        if brick.object_type == "NodeShape":
            self.radioNode.setChecked(True)
        else:
            self.radioProperty.setChecked(True)
        
        self.state_controller.update_brick_type(brick.object_type)
        
        if brick.object_type == "NodeShape":
            self.targetLineEdit.setText(brick.target_class)
        else:
            self.propertyPathEdit.setText(brick.property_path)
        
        # Update properties list
        self.propertyList.clear()
        for prop_name, prop_data in brick.properties.items():
            # Create detailed display text
            display_parts = [prop_name]
            
            if isinstance(prop_data, dict):
                # Check if this is a property brick reference
                if prop_data.get('is_property_brick'):
                    display_parts.append("[Property Brick]")
                    if 'property_path' in prop_data and prop_data['property_path']:
                        display_parts.append(f"path: {prop_data['property_path']}")
                    if 'description' in prop_data and prop_data['description']:
                        display_parts.append(f"brick: {prop_data['description']}")
                else:
                    # Regular property
                    if 'path' in prop_data and prop_data['path']:
                        display_parts.append(f"path: {prop_data['path']}")
                    if 'datatype' in prop_data and prop_data['datatype']:
                        display_parts.append(f"type: {prop_data['datatype']}")
                    if 'constraints' in prop_data and prop_data['constraints']:
                        constraint_count = len(prop_data['constraints'])
                        display_parts.append(f"{constraint_count} constraints")
            
            display_text = " | ".join(display_parts)
            
            # Create list item with full property data
            list_item = QListWidgetItem(display_text)
            # Store the complete property data for editing
            full_prop_data = {
                'name': prop_name,
                **prop_data
            }
            list_item.setData(Qt.ItemDataRole.UserRole, full_prop_data)
            self.propertyList.addItem(list_item)
        
        # Re-enable signals
        self.libraryComboBox.blockSignals(False)
        self.namelineEdit.blockSignals(False)
        self.description.blockSignals(False)
        self.targetLineEdit.blockSignals(False)
        self.propertyPathEdit.blockSignals(False)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = StatefulBrickEditor()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
