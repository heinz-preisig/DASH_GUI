"""
Daisy Chain Editor Dialog
Dialog for creating and editing daisy chains of schemas
"""

from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import Qt

from .ui_components import UiLoader


class DaisyChainEditorDialog(QDialog):
    """Dialog for editing daisy chain configurations"""
    
    def __init__(self, schema_core, available_schemas: List[Any], 
                 parent=None, existing_chain=None):
        super().__init__(parent)
        self.schema_core = schema_core
        self.available_schemas = available_schemas
        self.existing_chain = existing_chain
        
        # Load UI from .ui file
        self.ui_loader = UiLoader()
        self.ui = self.ui_loader.load_dialog('daisy_chain_editor.ui')
        
        # Connect signals
        self.ui.addSchemaButton.clicked.connect(self.add_schema_to_chain)
        self.ui.removeSchemaButton.clicked.connect(self.remove_schema_from_chain)
        self.ui.moveUpButton.clicked.connect(self.move_schema_up)
        self.ui.moveDownButton.clicked.connect(self.move_schema_down)
        self.ui.buttonBox.accepted.connect(self.on_accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        # Load available schemas
        self.load_available_schemas()
        
        # Load existing chain data if provided
        if existing_chain:
            self.load_existing_chain()
    
    def load_available_schemas(self):
        """Load available schemas into combo box"""
        self.ui.availableSchemasComboBox.clear()
        for schema in self.available_schemas:
            self.ui.availableSchemasComboBox.addItem(schema.name, schema.schema_id)
    
    def load_existing_chain(self):
        """Load existing daisy chain data"""
        if self.existing_chain:
            self.ui.chainNameLineEdit.setText(self.existing_chain.name)
            self.ui.chainDescLineEdit.setText(self.existing_chain.description or "")
            
            # Load schemas in chain
            self.ui.chainSchemasListWidget.clear()
            for schema_id in self.existing_chain.schema_ids:
                # Find schema by ID
                for schema in self.available_schemas:
                    if schema.schema_id == schema_id:
                        self.ui.chainSchemasListWidget.addItem(schema.name)
                        break
            
            # Load navigation rules
            nav_rules = self.existing_chain.navigation_rules
            self.ui.allowSkipCheckBox.setChecked(nav_rules.get('allow_skip', False))
            self.ui.showProgressCheckBox.setChecked(nav_rules.get('show_progress', True))
    
    def add_schema_to_chain(self):
        """Add selected schema to chain"""
        current_data = self.ui.availableSchemasComboBox.currentData()
        current_text = self.ui.availableSchemasComboBox.currentText()
        
        if current_data and current_text:
            # Check if already in chain
            for i in range(self.ui.chainSchemasListWidget.count()):
                if self.ui.chainSchemasListWidget.item(i).data(Qt.ItemDataRole.UserRole) == current_data:
                    return  # Already in chain
            
            # Add to list
            item = self.ui.chainSchemasListWidget.addItem(current_text)
            # Store schema_id as user data
            self.ui.chainSchemasListWidget.item(self.ui.chainSchemasListWidget.count() - 1).setData(
                Qt.ItemDataRole.UserRole, current_data
            )
    
    def remove_schema_from_chain(self):
        """Remove selected schema from chain"""
        current_item = self.ui.chainSchemasListWidget.currentItem()
        if current_item:
            row = self.ui.chainSchemasListWidget.row(current_item)
            self.ui.chainSchemasListWidget.takeItem(row)
    
    def move_schema_up(self):
        """Move selected schema up in chain"""
        current_row = self.ui.chainSchemasListWidget.currentRow()
        if current_row > 0:
            item = self.ui.chainSchemasListWidget.takeItem(current_row)
            self.ui.chainSchemasListWidget.insertItem(current_row - 1, item)
            self.ui.chainSchemasListWidget.setCurrentRow(current_row - 1)
    
    def move_schema_down(self):
        """Move selected schema down in chain"""
        current_row = self.ui.chainSchemasListWidget.currentRow()
        if current_row < self.ui.chainSchemasListWidget.count() - 1:
            item = self.ui.chainSchemasListWidget.takeItem(current_row)
            self.ui.chainSchemasListWidget.insertItem(current_row + 1, item)
            self.ui.chainSchemasListWidget.setCurrentRow(current_row + 1)
    
    def on_accept(self):
        """Handle OK button click"""
        name = self.ui.chainNameLineEdit.text().strip()
        if not name:
            # Show error and don't accept
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Validation Error", "Please enter a chain name")
            return
        
        if self.ui.chainSchemasListWidget.count() == 0:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Validation Error", "Please add at least one schema to the chain")
            return
        
        self.accept()
    
    def get_chain_data(self) -> Dict[str, Any]:
        """Get the daisy chain data from the dialog"""
        # Get schema IDs in order
        schema_ids = []
        for i in range(self.ui.chainSchemasListWidget.count()):
            item = self.ui.chainSchemasListWidget.item(i)
            schema_id = item.data(Qt.ItemDataRole.UserRole)
            if schema_id:
                schema_ids.append(schema_id)
        
        # Get navigation rules
        navigation_rules = {
            'allow_skip': self.ui.allowSkipCheckBox.isChecked(),
            'show_progress': self.ui.showProgressCheckBox.isChecked()
        }
        
        return {
            'name': self.ui.chainNameLineEdit.text().strip(),
            'description': self.ui.chainDescLineEdit.text().strip(),
            'schema_ids': schema_ids,
            'navigation_rules': navigation_rules
        }
