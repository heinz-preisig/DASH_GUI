#!/usr/bin/env python3
"""
Editor Controller - Connects frontend and backend
Implements MVC pattern for clean separation
"""

from typing import Dict, List, Any, Optional
from .editor_backend import BrickEditorBackend, OntologyManager
from ..interfaces.editor_frontend import (
    BrickEditorFrontend, OntologyBrowserFrontend,
    SelectionDialogFrontend
)

class BrickEditorController:
    """Controller that connects frontend and backend"""
    
    def __init__(self, backend: BrickEditorBackend, frontend: BrickEditorFrontend):
        self.backend = backend
        self.frontend = frontend
        self.current_brick = {}
        self.init_connections()
    
    def init_connections(self):
        """Initialize connections between frontend and backend"""
        # Load initial data
        self.refresh_ontology_options()
        
        # Load brick if provided
        if self.current_brick:
            self.frontend.display_brick(self.current_brick)
    
    def create_new_brick(self, brick_type: str = "NodeShape"):
        """Create a new brick"""
        self.current_brick = self.backend.create_new_brick(brick_type)
        self.frontend.display_brick(self.current_brick)
    
    def load_brick(self, brick_id: str):
        """Load existing brick"""
        brick_data = self.backend.load_brick(brick_id)
        if brick_data:
            self.current_brick = brick_data
            self.frontend.display_brick(brick_data)
        else:
            self.frontend.show_error(f"Failed to load brick: {brick_id}")
    
    def save_brick(self):
        """Save current brick"""
        brick_data = self.frontend.get_brick_data()
        success, message = self.backend.save_brick(brick_data)
        
        if success:
            self.current_brick = brick_data
            self.frontend.show_success(message)
        else:
            self.frontend.show_error(message)
    
    def refresh_ontology_options(self):
        """Refresh ontology options in frontend"""
        # Get options from backend
        target_classes = self.backend.get_available_target_classes()
        properties = self.backend.get_available_properties()
        
        # Set in frontend
        self.frontend.set_target_class_options(target_classes)
        self.frontend.set_property_options(properties)
    
    def browse_ontologies(self, selection_type: str):
        """Browse ontologies for selection"""
        # Create ontology browser dialog
        from ..gui.simple_editor import SimpleOntologyBrowser, SimpleSelectionDialog
        
        browser = SimpleOntologyBrowser()
        browser.display_ontologies(self.backend.ontology_manager.ontologies)
        
        # Connect selection handler
        def on_term_selected(term_data):
            if selection_type == "target_class" and term_data.get("type") == "class":
                # Set target class in current brick
                self.set_target_class(term_data["uri"], term_data["name"])
            elif selection_type == "property" and term_data.get("type") == "property":
                # Set property in current property editor
                self.set_selected_property(term_data["uri"], term_data["name"])
        
        # This would need to be connected to actual UI
        # For now, just show the browser
        browser.get_widget().show()
    
    def set_target_class(self, uri: str, name: str):
        """Set target class from ontology selection"""
        if self.current_brick:
            self.current_brick["target_class"] = uri
            if not self.current_brick.get("name", "").strip():
                self.current_brick["name"] = f"{name} Shape"
            self.frontend.display_brick(self.current_brick)
    
    def set_selected_property(self, uri: str, name: str):
        """Set property from ontology selection"""
        # This would need to be implemented based on current property editor
        pass
    
    def add_property_to_brick(self, property_name: str, property_data: Dict[str, Any]):
        """Add property to current brick"""
        if self.current_brick:
            self.backend.add_property(self.current_brick, property_name, property_data)
            self.frontend.display_brick(self.current_brick)
    
    def remove_property_from_brick(self, property_name: str):
        """Remove property from current brick"""
        if self.current_brick:
            self.backend.remove_property(self.current_brick, property_name)
            self.frontend.display_brick(self.current_brick)
    
    def import_ontology(self, file_path: str):
        """Import ontology file"""
        success, message, ontology_data = self.backend.ontology_manager.import_ontology(file_path)
        
        if success and ontology_data:
            # Add to manager
            ontology_name = f"Imported_{len(self.backend.ontology_manager.ontologies)}"
            self.backend.ontology_manager.ontologies[ontology_name] = ontology_data
            
            # Refresh frontend options
            self.refresh_ontology_options()
            self.frontend.show_success(f"Ontology '{ontology_name}' imported successfully")
        else:
            self.frontend.show_error(message)


class SimpleEditorFactory:
    """Factory for creating simple editor components"""
    
    @staticmethod
    def create_editor(backend, parent=None):
        """Create a complete editor with frontend and controller"""
        from ..gui.simple_editor import SimpleBrickEditor
        
        # Create frontend
        frontend = SimpleBrickEditor(parent)
        
        # Create controller
        controller = BrickEditorController(backend, frontend)
        
        # Connect browser functionality
        frontend.parent = controller
        
        return frontend.get_widget(), controller
    
    @staticmethod
    def create_ontology_browser(backend, parent=None):
        """Create ontology browser component"""
        from ..gui.simple_editor import SimpleOntologyBrowser
        
        browser = SimpleOntologyBrowser(parent)
        browser.display_ontologies(backend.ontology_manager.ontologies)
        
        return browser.get_widget()
    
    @staticmethod
    def create_selection_dialog(title: str, items: List[Dict[str, str]], parent=None):
        """Create selection dialog"""
        from ..gui.simple_editor import SimpleSelectionDialog
        
        dialog = SimpleSelectionDialog(parent)
        return dialog.show_selection(title, items)
