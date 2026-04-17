#!/usr/bin/env python3
"""
Add Component Dialog Module
Clean dialog for selecting bricks to add as schema components
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QListWidget, QListWidgetItem, QDialogButtonBox
)
from PyQt6.QtCore import Qt


class AddComponentDialog(QDialog):
    """Dialog for adding components to a schema using controller pattern"""
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.selected_brick_id = None
        self.setWindowTitle("Add Component")
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Instructions
        info_label = QLabel("Select a brick to add as a component:")
        layout.addWidget(info_label)
        
        # Brick list
        self.brick_list = QListWidget()
        self.brick_list.itemDoubleClicked.connect(self.on_brick_selected)
        layout.addWidget(self.brick_list)
        
        # Search/filter
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.filter_bricks)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # Filter by type
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "NodeShape", "PropertyShape"])
        self.type_filter.currentTextChanged.connect(self.filter_bricks)
        filter_layout.addWidget(self.type_filter)
        layout.addLayout(filter_layout)
        
        # Load bricks
        self.load_bricks()
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def load_bricks(self):
        """Load available bricks from controller"""
        self.brick_list.clear()
        
        # Get all bricks from controller
        bricks = self.controller.get_available_bricks()
        for brick in bricks:
            display_text = f"{brick.name} ({brick.object_type})"
            if hasattr(brick, 'description') and brick.description:
                display_text += f" - {brick.description[:50]}..."
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, brick.brick_id)
            item.setData(Qt.ItemDataRole.UserRole + 1, brick)  # Store full brick data
            self.brick_list.addItem(item)
    
    def filter_bricks(self):
        """Filter bricks based on search and type"""
        search_text = self.search_edit.text().lower()
        filter_type = self.type_filter.currentText()
        
        for i in range(self.brick_list.count()):
            item = self.brick_list.item(i)
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
        current_item = self.brick_list.currentItem()
        if current_item:
            self.selected_brick_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.accept()
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Selection", "Please select a brick to add")
    
    def get_selected_brick(self):
        """Get the selected brick ID"""
        return self.selected_brick_id
