"""
Help Dialog Module
User-friendly help system for non-SHACL experts
"""

import sys
import os
from typing import Optional
from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import Qt

from .ui_components import UiLoader, ComponentManager

# Add core modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from ...core.schema_helper import SchemaHelper, SchemaTemplate


class HelpDialog(QDialog):
    """Help dialog with tabs for different types of assistance"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize helper
        self.helper = SchemaHelper()
        
        # Load UI from .ui file
        self.ui_loader = UiLoader()
        self.ui = self.ui_loader.load_ui_file('main_window_help.ui', self)
        
        # Component manager
        self.components = ComponentManager()
        
        # Setup dialog
        self.setup_dialog()
        self.connect_signals()
        self.load_initial_data()
    
    def setup_dialog(self):
        """Setup dialog components"""
        self.setWindowTitle("Schema App v2 - Help")
        self.setModal(True)
        self.resize(800, 600)
    
    def connect_signals(self):
        """Connect UI signals"""
        # Templates tab
        self.ui.templatesListWidget.itemSelectionChanged.connect(self.on_template_selection_changed)
        self.ui.useTemplateButton.clicked.connect(self.use_template)
        
        # Concepts tab
        self.ui.conceptComboBox.currentTextChanged.connect(self.on_concept_changed)
        
        # Tips tab
        self.ui.newTipButton.clicked.connect(self.show_new_tip)
        
        # Dialog buttons
        self.ui.closeButton.clicked.connect(self.accept)
    
    def load_initial_data(self):
        """Load initial data into help tabs"""
        self.load_templates()
        self.load_concepts()
        self.show_random_tip()
    
    def load_templates(self):
        """Load available templates"""
        templates = self.helper.get_all_templates()
        
        # Group templates by category
        categories = self.helper.get_categories()
        
        for category in categories:
            # Add category header
            category_item = self.ui.templatesListWidget.addItem(f"📁 {category}")
            category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            
            # Add templates in category
            category_templates = self.helper.get_templates_by_category(category)
            for template in category_templates:
                item = self.ui.templatesListWidget.addItem(f"  📋 {template.name}")
                item.setData(Qt.ItemDataRole.UserRole, template)
    
    def load_concepts(self):
        """Load concepts for explanation"""
        concepts = [
            ("Select a concept...", ""),
            ("Schema", "schema"),
            ("Brick", "brick"),
            ("Root Brick", "root_brick"),
            ("Component Brick", "component_brick"),
            ("Flow", "flow"),
            ("Sequential Flow", "sequential_flow"),
            ("Conditional Flow", "conditional_flow"),
            ("Parallel Flow", "parallel_flow"),
            ("Dynamic Flow", "dynamic_flow"),
            ("NodeShape", "node_shape"),
            ("PropertyShape", "property_shape"),
            ("Target Class", "target_class"),
            ("Property Path", "property_path"),
            ("Constraints", "constraints"),
            ("SHACL", "shacl"),
            ("Export SHACL", "export_shacl")
        ]
        
        for display_text, concept_key in concepts:
            self.ui.conceptComboBox.addItem(display_text, concept_key)
    
    def show_random_tip(self):
        """Show a random helpful tip"""
        tip = self.helper.get_random_tip()
        tip_html = f"""
        <!DOCTYPE HTML>
        <html>
        <head>
        <style>
        body {{ font-family: Arial, sans-serif; margin: 10px; }}
        .tip {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; border-radius: 4px; margin: 10px 0; }}
        </style>
        </head>
        <body>
        <div class="tip">
        <strong>💡 Tip:</strong> {tip}
        </div>
        </body>
        </html>
        """
        
        self.components.set_text_edit_text(self.ui.tipTextEdit, tip_html)
    
    def on_template_selection_changed(self):
        """Handle template selection change"""
        current_item = self.ui.templatesListWidget.currentItem()
        if not current_item:
            return
        
        template = current_item.data(Qt.ItemDataRole.UserRole)
        if not template:
            return
        
        # Show template description
        description_html = f"""
        <!DOCTYPE HTML>
        <html>
        <head>
        <style>
        body {{ font-family: Arial, sans-serif; margin: 10px; }}
        .template {{ background-color: #e8f4fd; padding: 15px; border-left: 4px solid #3498db; border-radius: 4px; margin: 10px 0; }}
        .use-case {{ background-color: #f8f9fa; padding: 10px; border-radius: 4px; margin: 5px 0; }}
        </style>
        </head>
        <body>
        <div class="template">
        <h3>{template.name}</h3>
        <p><strong>Category:</strong> {template.category}</p>
        <p><strong>Description:</strong> {template.description}</p>
        <p><strong>Explanation:</strong> {template.explanation}</p>
        
        <p><strong>Common Use Cases:</strong></p>
        """
        
        for use_case in template.use_cases:
            description_html += f'<div class="use-case">• {use_case}</div>'
        
        description_html += """
        </div>
        </body>
        </html>
        """
        
        self.components.set_text_edit_text(self.ui.templateDescriptionTextEdit, description_html)
    
    def on_concept_changed(self):
        """Handle concept selection change"""
        concept_key = self.ui.conceptComboBox.currentData()
        if not concept_key:
            self.components.set_text_edit_text(self.ui.conceptExplanationTextEdit, "")
            return
        
        explanation = self.helper.get_explanation(concept_key)
        if not explanation:
            return
        
        explanation_html = f"""
        <!DOCTYPE HTML>
        <html>
        <head>
        <style>
        body {{ font-family: Arial, sans-serif; margin: 10px; }}
        .concept {{ background-color: #d4edda; padding: 15px; border-left: 4px solid #28a745; border-radius: 4px; margin: 10px 0; }}
        .example {{ background-color: #f8f9fa; padding: 10px; border-radius: 4px; margin: 5px 0; font-style: italic; }}
        </style>
        </head>
        <body>
        <div class="concept">
        {explanation}
        </div>
        </body>
        </html>
        """
        
        self.components.set_text_edit_text(self.ui.conceptExplanationTextEdit, explanation_html)
    
    def use_template(self):
        """Use selected template"""
        current_item = self.ui.templatesListWidget.currentItem()
        if not current_item:
            return
        
        template = current_item.data(Qt.ItemDataRole.UserRole)
        if not template:
            return
        
        # Store template data for parent to use
        self.selected_template = template
        self.accept()
    
    def get_selected_template(self) -> Optional[SchemaTemplate]:
        """Get the template selected by user"""
        return getattr(self, 'selected_template', None)
