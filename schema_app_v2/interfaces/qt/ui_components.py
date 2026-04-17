"""
UI Components Module
Utilities for loading and managing Qt Designer .ui files
"""

import os
from typing import Optional
from PyQt6.QtWidgets import QWidget, QDialog, QMainWindow
from PyQt6.uic import loadUi


class UiLoader:
    """Utility class for loading .ui files"""
    
    def __init__(self, ui_directory: str = None):
        if ui_directory is None:
            ui_directory = os.path.join(os.path.dirname(__file__), 'ui')
        self.ui_directory = ui_directory
    
    def load_main_window(self, parent=None) -> QMainWindow:
        """Load the main window from .ui file"""
        ui_file = os.path.join(self.ui_directory, 'main_window.ui')
        widget = QMainWindow(parent)
        loadUi(ui_file, widget)
        return widget
    
    def load_flow_editor_dialog(self, parent=None) -> QDialog:
        """Load the flow editor dialog from .ui file"""
        ui_file = os.path.join(self.ui_directory, 'flow_editor.ui')
        dialog = QDialog(parent)
        loadUi(ui_file, dialog)
        return dialog
    
    def load_ui_file(self, ui_filename: str, parent=None) -> QMainWindow:
        """Load a generic .ui file"""
        ui_file = os.path.join(self.ui_directory, ui_filename)
        if not os.path.exists(ui_file):
            raise FileNotFoundError(f"UI file not found: {ui_file}")
        
        widget = QMainWindow(parent)
        loadUi(ui_file, widget)
        return widget


class ComponentManager:
    """Manages UI component connections and data binding"""
    
    @staticmethod
    def connect_list_widget_double_click(list_widget, callback):
        """Connect double-click event to list widget"""
        list_widget.itemDoubleClicked.connect(callback)
    
    @staticmethod
    def connect_button_click(button, callback):
        """Connect click event to button"""
        button.clicked.connect(callback)
    
    @staticmethod
    def connect_combo_box_change(combo_box, callback):
        """Connect current index change event to combo box"""
        combo_box.currentIndexChanged.connect(callback)
    
    @staticmethod
    def connect_text_change(line_edit, callback):
        """Connect text change event to line edit"""
        line_edit.textChanged.connect(callback)
    
    @staticmethod
    def populate_combo_box(combo_box, items: list, first_item: str = None):
        """Populate combo box with items"""
        combo_box.clear()
        if first_item:
            combo_box.addItem(first_item)
        combo_box.addItems(items)
    
    @staticmethod
    def populate_list_widget(list_widget, items: list, display_field: str = None):
        """Populate list widget with items"""
        list_widget.clear()
        for item in items:
            if hasattr(item, display_field or 'name'):
                display_text = getattr(item, display_field or 'name', str(item))
            else:
                display_text = str(item)
            list_widget.addItem(display_text)
    
    @staticmethod
    def set_list_widget_data(list_widget, items: list, data_field: str = 'id'):
        """Set list widget items with data"""
        list_widget.clear()
        for i, item in enumerate(items):
            if hasattr(item, 'name'):
                display_text = item.name
            else:
                display_text = str(item)
            
            list_item = list_widget.addItem(display_text)
            
            # Store item data
            if hasattr(item, data_field):
                data_value = getattr(item, data_field)
            elif hasattr(item, f'{data_field}_id'):
                data_value = getattr(item, f'{data_field}_id')
            else:
                data_value = str(item)
            
            list_widget.setItemData(list_widget.count() - 1, data_value)
    
    @staticmethod
    def get_selected_list_data(list_widget, data_role=256):
        """Get data from selected list widget item"""
        current_item = list_widget.currentItem()
        if current_item:
            return current_item.data(data_role)
        return None
    
    @staticmethod
    def get_selected_list_text(list_widget):
        """Get text from selected list widget item"""
        current_item = list_widget.currentItem()
        if current_item:
            return current_item.text()
        return None
    
    @staticmethod
    def clear_list_widget(list_widget):
        """Clear list widget"""
        list_widget.clear()
    
    @staticmethod
    def set_line_edit_text(line_edit, text: str):
        """Set line edit text"""
        line_edit.setText(text or "")
    
    @staticmethod
    def get_line_edit_text(line_edit) -> str:
        """Get line edit text"""
        return line_edit.text().strip()
    
    @staticmethod
    def set_combo_box_current_text(combo_box, text: str):
        """Set combo box current text"""
        index = combo_box.findText(text)
        if index >= 0:
            combo_box.setCurrentIndex(index)
    
    @staticmethod
    def get_combo_box_current_text(combo_box) -> str:
        """Get combo box current text"""
        return combo_box.currentText()
    
    @staticmethod
    def set_enabled(widget, enabled: bool):
        """Enable or disable widget"""
        widget.setEnabled(enabled)
    
    @staticmethod
    def set_visible(widget, visible: bool):
        """Show or hide widget"""
        widget.setVisible(visible)
    
    @staticmethod
    def show_info_message(parent, title: str, message: str):
        """Show information message"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(parent, title, message)
    
    @staticmethod
    def show_warning_message(parent, title: str, message: str):
        """Show warning message"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(parent, title, message)
    
    @staticmethod
    def show_error_message(parent, title: str, message: str):
        """Show error message"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(parent, title, message)
    
    @staticmethod
    def ask_confirmation(parent, title: str, message: str) -> bool:
        """Ask for confirmation"""
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            parent, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
