#!/usr/bin/env python3
"""
Add Component Dialog Module
Clean dialog for selecting bricks to add as schema components
"""

from typing import Optional
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi

from .ui_components import UiLoader


class AddComponentDialog(QDialog):
    """Dialog for adding components to a schema using controller pattern"""
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.selected_brick_id = None
        
        # Load UI from file
        ui_path = Path(__file__).parent / 'ui' / 'add_component_dialog.ui'
        loadUi(str(ui_path), self)
        
        # Connect signals
        self.brickList.itemDoubleClicked.connect(self.on_brick_selected)
        self.searchEdit.textChanged.connect(self.filter_bricks)
        self.typeFilter.currentTextChanged.connect(self.filter_bricks)
        self.buttonBox.accepted.connect(self.on_accept)
        self.buttonBox.rejected.connect(self.reject)
        
        # Load bricks
        self.load_bricks()
    
    def load_bricks(self):
        """Load available bricks from controller"""
        self.brickList.clear()
        
        # Get all bricks from controller
        bricks = self.controller.get_available_bricks()
        for brick in bricks:
            display_text = f"{brick.name} ({brick.object_type})"
            if hasattr(brick, 'description') and brick.description:
                display_text += f" - {brick.description[:50]}..."
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, brick.brick_id)
            item.setData(Qt.ItemDataRole.UserRole + 1, brick)  # Store full brick data
            self.brickList.addItem(item)
    
    def filter_bricks(self):
        """Filter bricks based on search and type"""
        search_text = self.searchEdit.text().lower()
        filter_type = self.typeFilter.currentText()
        
        for i in range(self.brickList.count()):
            item = self.brickList.item(i)
            brick_data = item.data(Qt.ItemDataRole.UserRole + 1)
            
            if not brick_data:
                continue
            
            # Check search filter
            matches_search = True
            if search_text:
                matches_search = (
                    search_text in brick_data.name.lower() or
                    (hasattr(brick_data, 'description') and 
                     search_text in brick_data.description.lower())
                )
            
            # Check type filter
            matches_type = filter_type == "All" or brick_data.object_type == filter_type
            
            # Show/hide item
            item.setHidden(not (matches_search and matches_type))
    
    def on_brick_selected(self, item):
        """Handle brick selection"""
        self.selected_brick_id = item.data(Qt.ItemDataRole.UserRole)
        self.accept()
    
    def on_accept(self):
        """Handle OK button click"""
        current_item = self.brickList.currentItem()
        if current_item:
            self.selected_brick_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.accept()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a brick to add")
    
    def get_selected_brick(self):
        """Get the selected brick ID"""
        return self.selected_brick_id
