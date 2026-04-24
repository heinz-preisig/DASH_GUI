#!/usr/bin/env python3
"""
UI Abstraction Layer
Separates UI components from business logic for better testability and web migration
"""

import sys
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton, QListWidget
from PyQt6.QtCore import Qt

# Add brick_app_v2 directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))
sys.path.insert(0, str(app_dir / 'state'))

from state.app_state import UIState, BrickType, UIViewState


class UIComponent(ABC):
    """Abstract base class for UI components"""
    
    @abstractmethod
    def update_from_state(self, ui_state: UIViewState):
        """Update component based on UI state"""
        pass
    
    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """Get data from component"""
        pass


class UIBuilder:
    """Helper class for building UI components with consistent behavior"""
    
    @staticmethod
    def create_label(text: str, visible: bool = True) -> QLabel:
        """Create a label with consistent styling"""
        label = QLabel(text)
        label.setVisible(visible)
        return label
    
    @staticmethod
    def create_line_edit(placeholder: str = "", visible: bool = True) -> QLineEdit:
        """Create a line edit with consistent behavior"""
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setVisible(visible)
        return edit
    
    @staticmethod
    def create_text_edit(placeholder: str = "", visible: bool = True) -> QTextEdit:
        """Create a text edit with consistent behavior"""
        edit = QTextEdit()
        if placeholder:
            edit.setPlaceholderText(placeholder)
        edit.setVisible(visible)
        return edit
    
    @staticmethod
    def create_combo_box(items: List[str], visible: bool = True) -> QComboBox:
        """Create a combo box with consistent behavior"""
        combo = QComboBox()
        combo.addItems(items)
        combo.setVisible(visible)
        return combo
    
    @staticmethod
    def create_button(text: str, visible: bool = True, enabled: bool = True) -> QPushButton:
        """Create a button with consistent styling"""
        button = QPushButton(text)
        button.setVisible(visible)
        button.setEnabled(enabled)
        return button
    
    @staticmethod
    def create_list_widget(visible: bool = True) -> QListWidget:
        """Create a list widget with consistent behavior"""
        list_widget = QListWidget()
        list_widget.setVisible(visible)
        return list_widget


class UIManager:
    """Manages UI components and their interaction with state"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.components = {}
        self.event_handlers = {}
    
    def register_component(self, name: str, component: UIComponent):
        """Register a UI component"""
        self.components[name] = component
    
    def register_event_handler(self, event_name: str, handler: Callable):
        """Register an event handler"""
        self.event_handlers[event_name] = handler
    
    def update_all_components(self, ui_state: UIViewState):
        """Update all registered components based on state"""
        for component in self.components.values():
            try:
                component.update_from_state(ui_state)
            except Exception as e:
                print(f"Error updating component: {e}")
    
    def handle_event(self, event_name: str, *args, **kwargs):
        """Handle an event"""
        if event_name in self.event_handlers:
            try:
                self.event_handlers[event_name](*args, **kwargs)
            except Exception as e:
                print(f"Error handling event {event_name}: {e}")
    
    def get_component_data(self, component_name: str) -> Dict[str, Any]:
        """Get data from a specific component"""
        if component_name in self.components:
            return self.components[component_name].get_data()
        return {}


class BrickEditorComponent(UIComponent):
    """UI component for brick editing"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self._setup_fields()
    
    def _setup_fields(self):
        """Setup brick editor fields"""
        # These should be created by the main window, not here
        # This is a reference to existing UI elements
        pass
    
    def update_from_state(self, ui_state: UIViewState):
        """Update editor visibility and fields based on state"""
        # Update visibility
        if hasattr(self.main_window, 'editorPanel'):
            self.main_window.editorPanel.setVisible(ui_state.show_brick_editor)
        
        # Update field visibility based on brick type
        if hasattr(self.main_window, 'targetLabel'):
            self.main_window.targetLabel.setVisible(ui_state.show_target_class_fields)
        
        if hasattr(self.main_window, 'targetLineEdit'):
            self.main_window.targetLineEdit.setVisible(ui_state.show_target_class_fields)
        
        if hasattr(self.main_window, 'propertyLabel'):
            self.main_window.propertyLabel.setVisible(ui_state.show_property_path_fields)
        
        if hasattr(self.main_window, 'propertyPathEdit'):
            self.main_window.propertyPathEdit.setVisible(ui_state.show_property_path_fields)
        
        if hasattr(self.main_window, 'ontologyTargetBrowser'):
            self.main_window.ontologyTargetBrowser.setVisible(ui_state.show_target_class_fields)
        
        if hasattr(self.main_window, 'ontologyPathBrowser'):
            self.main_window.ontologyPathBrowser.setVisible(ui_state.show_property_path_fields)
    
    def get_data(self) -> Dict[str, Any]:
        """Get data from editor fields"""
        data = {}
        
        if hasattr(self.main_window, 'namelineEdit'):
            data['name'] = self.main_window.namelineEdit.text()
        
        if hasattr(self.main_window, 'description'):
            data['description'] = self.main_window.description.toPlainText()
        
        if hasattr(self.main_window, 'targetLineEdit'):
            data['target_class'] = self.main_window.targetLineEdit.text()
        
        if hasattr(self.main_window, 'propertyPathEdit'):
            data['property_path'] = self.main_window.propertyPathEdit.text()
        
        return data
    
    def set_data(self, data: Dict[str, Any]):
        """Set data to editor fields"""
        if 'name' in data and hasattr(self.main_window, 'namelineEdit'):
            self.main_window.namelineEdit.setText(data['name'])
        
        if 'description' in data and hasattr(self.main_window, 'description'):
            self.main_window.description.setPlainText(data['description'])
        
        if 'target_class' in data and hasattr(self.main_window, 'targetLineEdit'):
            self.main_window.targetLineEdit.setText(data['target_class'])
        
        if 'property_path' in data and hasattr(self.main_window, 'propertyPathEdit'):
            self.main_window.propertyPathEdit.setText(data['property_path'])


class BrickListComponent(UIComponent):
    """UI component for brick lists"""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def update_from_state(self, ui_state: UIViewState):
        """Update list visibility based on state"""
        if hasattr(self.main_window, 'nodeBrickList'):
            self.main_window.nodeBrickList.setVisible(ui_state.show_brick_list)
        
        if hasattr(self.main_window, 'propertyBrickList'):
            self.main_window.propertyBrickList.setVisible(ui_state.show_property_list)
    
    def get_data(self) -> Dict[str, Any]:
        """Get selected brick data"""
        data = {}
        
        # Get selected node brick
        if hasattr(self.main_window, 'nodeBrickList'):
            current_item = self.main_window.nodeBrickList.currentItem()
            if current_item:
                brick_data = current_item.data(Qt.ItemDataRole.UserRole)
                if brick_data:
                    data['selected_node_brick'] = brick_data
        
        # Get selected property brick
        if hasattr(self.main_window, 'propertyBrickList'):
            current_item = self.main_window.propertyBrickList.currentItem()
            if current_item:
                brick_data = current_item.data(Qt.ItemDataRole.UserRole)
                if brick_data:
                    data['selected_property_brick'] = brick_data
        
        return data


class LibraryComponent(UIComponent):
    """UI component for library management"""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def update_from_state(self, ui_state: UIViewState):
        """Update library component based on state"""
        if hasattr(self.main_window, 'libraryComboBox'):
            self.main_window.libraryComboBox.setVisible(ui_state.show_library_panel)
    
    def get_data(self) -> Dict[str, Any]:
        """Get library data"""
        data = {}
        
        if hasattr(self.main_window, 'libraryComboBox'):
            data['selected_library'] = self.main_window.libraryComboBox.currentText()
        
        return data


class PropertyListComponent(UIComponent):
    """UI component for property lists"""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def update_from_state(self, ui_state: UIViewState):
        """Update property list visibility based on state"""
        if hasattr(self.main_window, 'propertyList'):
            self.main_window.propertyList.setVisible(ui_state.show_property_list)
    
    def get_data(self) -> Dict[str, Any]:
        """Get selected property data"""
        data = {}
        
        if hasattr(self.main_window, 'propertyList'):
            current_item = self.main_window.propertyList.currentItem()
            if current_item:
                prop_data = current_item.data(Qt.ItemDataRole.UserRole)
                if prop_data:
                    data['selected_property'] = prop_data
        
        return data
