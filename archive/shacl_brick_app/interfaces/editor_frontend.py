#!/usr/bin/env python3
"""
Frontend Interfaces for Brick Editor
Technology-agnostic interface definitions
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Tuple

class BrickEditorFrontend(ABC):
    """Abstract interface for brick editor frontend"""
    
    @abstractmethod
    def display_brick(self, brick_data: Dict[str, Any]) -> None:
        """Display brick data in the frontend"""
        pass
    
    @abstractmethod
    def get_brick_data(self) -> Dict[str, Any]:
        """Get current brick data from frontend"""
        pass
    
    @abstractmethod
    def show_error(self, message: str) -> None:
        """Display error message to user"""
        pass
    
    @abstractmethod
    def show_success(self, message: str) -> None:
        """Display success message to user"""
        pass
    
    @abstractmethod
    def set_target_class_options(self, options: List[Dict[str, str]]) -> None:
        """Set available target class options"""
        pass
    
    @abstractmethod
    def set_property_options(self, options: List[Dict[str, str]]) -> None:
        """Set available property options"""
        pass

class OntologyBrowserFrontend(ABC):
    """Abstract interface for ontology browser frontend"""
    
    @abstractmethod
    def display_ontologies(self, ontologies: Dict[str, Any]) -> None:
        """Display available ontologies"""
        pass
    
    @abstractmethod
    def display_ontology_terms(self, ontology_name: str, terms: Dict[str, List[Dict[str, str]]]) -> None:
        """Display terms from selected ontology"""
        pass
    
    @abstractmethod
    def get_selected_term(self) -> Optional[Dict[str, str]]:
        """Get currently selected term"""
        pass

class PropertyEditorFrontend(ABC):
    """Abstract interface for property editor frontend"""
    
    @abstractmethod
    def display_property(self, property_data: Dict[str, Any]) -> None:
        """Display property data"""
        pass
    
    @abstractmethod
    def get_property_data(self) -> Dict[str, Any]:
        """Get current property data"""
        pass
    
    @abstractmethod
    def set_constraint_types(self, types: List[str]) -> None:
        """Set available constraint types"""
        pass
    
    @abstractmethod
    def set_data_types(self, types: List[str]) -> None:
        """Set available data types"""
        pass

class SimpleFormFrontend(ABC):
    """Abstract interface for simple form-based frontend"""
    
    @abstractmethod
    def add_field(self, field_name: str, field_type: str, options: Dict[str, Any] = None) -> None:
        """Add a field to the form"""
        pass
    
    @abstractmethod
    def get_field_value(self, field_name: str) -> Any:
        """Get value of a field"""
        pass
    
    @abstractmethod
    def set_field_value(self, field_name: str, value: Any) -> None:
        """Set value of a field"""
        pass
    
    @abstractmethod
    def validate_form(self) -> Tuple[bool, str]:
        """Validate form data"""
        pass
    
    @abstractmethod
    def clear_form(self) -> None:
        """Clear all form fields"""
        pass

class SelectionDialogFrontend(ABC):
    """Abstract interface for selection dialogs"""
    
    @abstractmethod
    def show_selection(self, title: str, items: List[Dict[str, str]], 
                   allow_multiple: bool = False) -> List[Dict[str, str]]:
        """Show selection dialog and return selected items"""
        pass
