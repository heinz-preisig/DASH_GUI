"""
Constraint management dialog.
Extracted from refactored_gui.py for better testability and separation of concerns.
"""

from typing import Dict, Any, List, Callable, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt

from gui_components import ConstraintEditorDialog
from business.brick_operations import brick_business_logic
from state.app_state import app_state_manager


class ConstraintManagerDialog(QDialog):
    """Dialog for managing constraints on a property"""
    
    def __init__(self, parent: QWidget, prop_data: Dict[str, Any], 
                 update_property_list_callback: Callable[[], None]):
        super().__init__(parent)
        
        self.prop_data = prop_data
        self.prop_name = prop_data.get('name', 'Property')
        self.update_property_list = update_property_list_callback
        self.constraints: List[Dict[str, Any]] = []
        
        self._setup_ui()
        self._connect_signals()
        self._refresh_constraint_list()
    
    def _setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle(f"Constraints for {self.prop_name}")
        self.setGeometry(300, 300, 500, 400)
        
        layout = QVBoxLayout()
        
        # Property info
        info_text = f"Property: {self.prop_name}"
        if 'path' in self.prop_data and self.prop_data['path']:
            info_text += f" | Path: {self.prop_data['path']}"
        
        info_label = QLabel(info_text)
        layout.addWidget(info_label)
        
        # Constraints list
        self.constraints_list = QListWidget()
        layout.addWidget(self.constraints_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Constraint")
        self.edit_btn = QPushButton("Edit Constraint")
        self.delete_btn = QPushButton("Delete Constraint")
        self.close_btn = QPushButton("Close")
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Initial button states
        self._update_button_states()
    
    def _connect_signals(self):
        """Connect button signals"""
        self.add_btn.clicked.connect(self._add_new_constraint)
        self.edit_btn.clicked.connect(self._edit_selected_constraint)
        self.delete_btn.clicked.connect(self._delete_selected_constraint)
        self.close_btn.clicked.connect(self.reject)
        
        self.constraints_list.itemSelectionChanged.connect(self._update_button_states)
    
    def _update_button_states(self):
        """Enable/disable buttons based on selection"""
        has_selection = self.constraints_list.currentItem() is not None and bool(self.constraints)
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def _refresh_constraint_list(self):
        """Refresh the constraints list from brick state"""
        self.constraints_list.clear()
        
        # Get fresh constraints from brick state
        brick_state = app_state_manager.get_brick_state()
        if self.prop_name and self.prop_name in brick_state.properties:
            prop_info = brick_state.properties[self.prop_name]
            if isinstance(prop_info, dict):
                self.constraints = prop_info.get('constraints', [])
                # Also update prop_data to stay in sync
                self.prop_data['constraints'] = self.constraints
            else:
                self.constraints = []
        else:
            self.constraints = self.prop_data.get('constraints', [])
        
        if self.constraints:
            for i, constraint in enumerate(self.constraints):
                constraint_text = f"{constraint.get('constraint_type', 'Unknown')}: {constraint.get('value', 'No value')}"
                list_item = QListWidgetItem(constraint_text)
                list_item.setData(Qt.ItemDataRole.UserRole, i)  # Store index
                self.constraints_list.addItem(list_item)
        else:
            self.constraints_list.addItem(QListWidgetItem("No constraints defined"))
        
        self._update_button_states()
    
    def _add_new_constraint(self):
        """Add a new constraint to the property"""
        constraint_dialog = ConstraintEditorDialog(self, self.prop_data)
        if constraint_dialog.exec() == QDialog.DialogCode.Accepted:
            new_constraint = constraint_dialog.get_constraint_data()
            if new_constraint:
                # Update brick state
                success, message = brick_business_logic.add_constraint(
                    self.prop_name, new_constraint, self.prop_data
                )
                if success:
                    self.update_property_list()
                    self._refresh_constraint_list()
                else:
                    QMessageBox.warning(self, "Error", message)
    
    def _edit_selected_constraint(self):
        """Edit the selected constraint"""
        current_item = self.constraints_list.currentItem()
        if not current_item or not self.constraints:
            QMessageBox.warning(self, "Warning", "Please select a constraint to edit.")
            return
        
        constraint_index = current_item.data(Qt.ItemDataRole.UserRole)
        if constraint_index is not None and constraint_index < len(self.constraints):
            # Edit existing constraint
            constraint_dialog = ConstraintEditorDialog(self, self.prop_data)
            constraint_dialog.set_constraint_data(self.constraints[constraint_index])
            
            if constraint_dialog.exec() == QDialog.DialogCode.Accepted:
                updated_constraint = constraint_dialog.get_constraint_data()
                if updated_constraint:
                    success, message = brick_business_logic.update_constraint(
                        self.prop_name, constraint_index, updated_constraint
                    )
                    if success:
                        self.update_property_list()
                        self._refresh_constraint_list()
                    else:
                        QMessageBox.warning(self, "Error", message)
    
    def _delete_selected_constraint(self):
        """Delete the selected constraint"""
        current_item = self.constraints_list.currentItem()
        if not current_item or not self.constraints:
            QMessageBox.warning(self, "Warning", "Please select a constraint to delete.")
            return
        
        constraint_index = current_item.data(Qt.ItemDataRole.UserRole)
        if constraint_index is not None and constraint_index < len(self.constraints):
            # Confirm deletion
            constraint = self.constraints[constraint_index]
            reply = QMessageBox.question(
                self, "Delete Constraint",
                f"Are you sure you want to delete the constraint '{constraint.get('constraint_type', 'Unknown')}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.constraints.pop(constraint_index)
                # Update brick state
                success, message = brick_business_logic.remove_constraint(
                    self.prop_name, constraint_index
                )
                if success:
                    self.update_property_list()
                    self._refresh_constraint_list()
                else:
                    QMessageBox.warning(self, "Error", message)


def show_constraint_manager(parent: QWidget, prop_data: Dict[str, Any],
                          update_property_list_callback: Callable[[], None]) -> None:
    """
    Show the constraint management dialog for a property.
    
    Args:
        parent: Parent widget
        prop_data: Property data dictionary
        update_property_list_callback: Callback to update the property list display
    """
    dialog = ConstraintManagerDialog(parent, prop_data, update_property_list_callback)
    dialog.exec()
