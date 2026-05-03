"""
UI Metadata Panel Dialog
Dialog for editing UI metadata (sequence, grouping, nesting, display)
"""

from PyQt6.QtWidgets import QDialog, QTreeWidgetItem, QMessageBox
from PyQt6.QtCore import Qt
from typing import Optional
from ..core.schema_core import Schema, UIMetadata


class UIMetadataPanelDialog(QDialog):
    """Dialog for editing UI metadata of schema components"""
    
    def __init__(self, schema: Schema, brick_id: str, parent=None):
        super().__init__(parent)
        
        self.schema = schema
        self.brick_id = brick_id
        self.brick_name = self._get_brick_name(brick_id)
        
        # Load UI file
        from PyQt6.uic import loadUi
        import os
        ui_file = os.path.join(os.path.dirname(__file__), 'ui', 'ui_metadata_panel.ui')
        
        if os.path.exists(ui_file):
            loadUi(ui_file, self)
            self.setWindowTitle(f"UI Metadata - {self.brick_name}")
        else:
            # Fallback: create basic UI programmatically
            from PyQt6.QtWidgets import QVBoxLayout, QLabel, QDialogButtonBox
            layout = QVBoxLayout()
            layout.addWidget(QLabel(f"UI file not found: {ui_file}"))
            self.setLayout(layout)
            return
        
        # Connect signals
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        # Connect custom signals
        self.moveUpButton.clicked.connect(self._move_up)
        self.moveDownButton.clicked.connect(self._move_down)
        self.createGroupButton.clicked.connect(self._create_group)
        self.removeFromGroupButton.clicked.connect(self._remove_from_group)
        self.removeParentButton.clicked.connect(self._remove_parent)
        self.groupComboBox.currentTextChanged.connect(self._on_group_changed)
        self.parentComboBox.currentTextChanged.connect(self._on_parent_changed)
        
        # Load current data
        self._load_current_data()
        self._populate_groups()
        self._populate_parents()
        self._update_tree_preview()
    
    def _get_brick_name(self, brick_id: str) -> str:
        """Get brick name from ID"""
        # Try to get from brick integration if available
        # For now, just return the ID
        return brick_id
    
    def _load_current_data(self):
        """Load current UI metadata into the dialog"""
        self.componentNameLabel.setText(self.brick_name)
        
        # Get UI metadata
        ui_metadata = self.schema.get_component_ui_metadata(self.brick_id)
        
        if ui_metadata:
            # Sequence tab
            self.sequenceSpinBox.setValue(ui_metadata.sequence)
            
            # Grouping tab
            if ui_metadata.group_id:
                self.groupComboBox.setCurrentText(ui_metadata.group_id)
                self._load_group_details(ui_metadata.group_id)
            
            # Nesting tab
            if ui_metadata.parent_id:
                self.parentComboBox.setCurrentText(ui_metadata.parent_id)
            
            # Display tab
            self.displayLabelLineEdit.setText(ui_metadata.label)
            self.helpTextEdit.setPlainText(ui_metadata.help_text)
            self.collapsibleCheckBox.setChecked(ui_metadata.is_collapsible)
            self.visibleCheckBox.setChecked(ui_metadata.is_visible)
        else:
            # Set defaults
            self.sequenceSpinBox.setValue(0)
            self.collapsibleCheckBox.setChecked(True)
            self.visibleCheckBox.setChecked(True)
    
    def _populate_groups(self):
        """Populate group dropdown with available groups"""
        self.groupComboBox.clear()
        self.groupComboBox.addItem("")  # Empty for no group
        
        groups = self.schema.get_groups_by_sequence()
        for group in groups:
            self.groupComboBox.addItem(group['id'], group['label'])
    
    def _populate_parents(self):
        """Populate parent dropdown with available components"""
        self.parentComboBox.clear()
        self.parentComboBox.addItem("")  # Empty for no parent
        
        for brick_id in self.schema.component_brick_ids:
            if brick_id != self.brick_id:  # Can't be parent of itself
                self.parentComboBox.addItem(brick_id)
    
    def _load_group_details(self, group_id: str):
        """Load group details into the group details section"""
        if group_id in self.schema.groups:
            group = self.schema.groups[group_id]
            self.groupLabelLineEdit.setText(group.get('label', ''))
            self.groupDescLineEdit.setText(group.get('description', ''))
            self.groupSeqSpinBox.setValue(group.get('sequence', 0))
    
    def _on_group_changed(self, group_id: str):
        """Handle group selection change"""
        if group_id:
            self._load_group_details(group_id)
    
    def _on_parent_changed(self, parent_id: str):
        """Handle parent selection change"""
        self._update_tree_preview()
    
    def _move_up(self):
        """Move component up in sequence"""
        current_seq = self.sequenceSpinBox.value()
        if current_seq > 0:
            self.sequenceSpinBox.setValue(current_seq - 1)
    
    def _move_down(self):
        """Move component down in sequence"""
        self.sequenceSpinBox.setValue(self.sequenceSpinBox.value() + 1)
    
    def _create_group(self):
        """Create a new group"""
        group_id = self.groupComboBox.currentText().strip()
        
        if not group_id:
            QMessageBox.warning(self, "Error", "Please enter a group ID")
            return
        
        label = self.groupLabelLineEdit.text().strip()
        if not label:
            label = group_id
        
        description = self.groupDescLineEdit.text().strip()
        sequence = self.groupSeqSpinBox.value()
        
        if self.schema.create_group(group_id, label, description, sequence):
            self._populate_groups()
            self.groupComboBox.setCurrentText(group_id)
            QMessageBox.information(self, "Success", f"Group '{group_id}' created")
        else:
            QMessageBox.warning(self, "Error", f"Group '{group_id}' already exists")
    
    def _remove_from_group(self):
        """Remove component from its group"""
        if self.schema.remove_component_from_group(self.brick_id):
            self.groupComboBox.setCurrentText("")
            QMessageBox.information(self, "Success", "Removed from group")
        else:
            QMessageBox.warning(self, "Error", "Failed to remove from group")
    
    def _remove_parent(self):
        """Remove parent component"""
        if self.schema.remove_component_parent(self.brick_id):
            self.parentComboBox.setCurrentText("")
            self._update_tree_preview()
            QMessageBox.information(self, "Success", "Parent removed")
        else:
            QMessageBox.warning(self, "Error", "Failed to remove parent")
    
    def _update_tree_preview(self):
        """Update tree preview widget"""
        self.treePreviewWidget.clear()
        
        # Build tree
        root_items = {}
        
        # Create items for all components
        for brick_id in self.schema.component_brick_ids:
            item = QTreeWidgetItem(self.treePreviewWidget)
            item.setText(0, brick_id)
            root_items[brick_id] = item
        
        # Set up parent-child relationships
        for brick_id in self.schema.component_brick_ids:
            parent_id = self.schema.get_ui_parent(brick_id)
            if parent_id and parent_id in root_items:
                child_item = root_items[brick_id]
                parent_item = root_items[parent_id]
                parent_item.removeChild(child_item)
                parent_item.addChild(child_item)
        
        # Expand all
        self.treePreviewWidget.expandAll()
        
        # Highlight current component
        if self.brick_id in root_items:
            root_items[self.brick_id].setForeground(0, Qt.GlobalColor.blue)
    
    def get_ui_metadata(self) -> UIMetadata:
        """Get UI metadata from dialog"""
        return UIMetadata(
            sequence=self.sequenceSpinBox.value(),
            group_id=self.groupComboBox.currentText() or None,
            parent_id=self.parentComboBox.currentText() or None,
            label=self.displayLabelLineEdit.text(),
            help_text=self.helpTextEdit.toPlainText(),
            is_collapsible=self.collapsibleCheckBox.isChecked(),
            is_visible=self.visibleCheckBox.isChecked()
        )
    
    def accept(self):
        """Handle OK button - save metadata"""
        ui_metadata = self.get_ui_metadata()
        self.schema.set_component_ui_metadata(self.brick_id, ui_metadata)
        
        # Update group details if group is selected
        group_id = self.groupComboBox.currentText()
        if group_id and group_id in self.schema.groups:
            self.schema.groups[group_id]['label'] = self.groupLabelLineEdit.text()
            self.schema.groups[group_id]['description'] = self.groupDescLineEdit.text()
            self.schema.groups[group_id]['sequence'] = self.groupSeqSpinBox.value()
        
        super().accept()
