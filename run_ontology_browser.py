#!/usr/bin/env python3
"""
Standalone Ontology Browser Application
Independent app for browsing ontologies and testing ontology functionality
"""

import sys
from pathlib import Path

# Add brick_app_v2 to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'brick_app_v2'))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QTextEdit
from PyQt6.QtCore import Qt

from core.ontology_manager import OntologyManager
from gui_components import SimpleOntologyBrowser


class OntologyBrowserApp(QMainWindow):
    """Standalone ontology browser application"""
    
    def __init__(self):
        super().__init__()
        self.ontology_manager = None
        self.init_ui()
        self.load_ontologies()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Standalone Ontology Browser")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Header
        header_label = QLabel("Ontology Browser")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.browse_classes_btn = QPushButton("Browse Classes")
        self.browse_classes_btn.clicked.connect(self.browse_classes)
        button_layout.addWidget(self.browse_classes_btn)
        
        self.browse_properties_btn = QPushButton("Browse Properties")
        self.browse_properties_btn.clicked.connect(self.browse_properties)
        button_layout.addWidget(self.browse_properties_btn)
        
        self.refresh_btn = QPushButton("Refresh Ontologies")
        self.refresh_btn.clicked.connect(self.load_ontologies)
        button_layout.addWidget(self.refresh_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Status text
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(200)
        layout.addWidget(QLabel("Status:"))
        layout.addWidget(self.status_text)
        
        # Initial status
        self.update_status("Initializing ontology browser...")
    
    def load_ontologies(self):
        """Load ontologies"""
        try:
            self.update_status("Loading ontologies...")
            self.ontology_manager = OntologyManager()
            
            ontologies = list(self.ontology_manager.ontologies.keys())
            self.update_status(f"Loaded {len(ontologies)} ontologies: {', '.join(ontologies)}")
            
            # Show ontology details
            details = []
            for name, data in self.ontology_manager.ontologies.items():
                class_count = len(data.get('classes', {}))
                prop_count = len(data.get('properties', {}))
                details.append(f"{name}: {class_count} classes, {prop_count} properties")
            
            self.update_status("Ontology Details:\n" + "\n".join(details))
            
        except Exception as e:
            self.update_status(f"Error loading ontologies: {e}")
    
    def browse_classes(self):
        """Browse ontology classes"""
        if not self.ontology_manager:
            self.update_status("Please load ontologies first")
            return
        
        try:
            self.update_status("Opening class browser...")
            browser = SimpleOntologyBrowser(self.ontology_manager, mode='classes', parent=self)
            browser.load_data()
            
            # Debug info
            self.update_status(f"Class browser opened with {len(browser.all_items)} items")
            self.update_status(f"Selected ontology: {browser.ontology_combo.currentText()}")
            
            if browser.exec() == browser.DialogCode.Accepted:
                selected = browser.selected_item
                if selected:
                    self.update_status(f"Selected class: {selected['name']}\nURI: {selected['uri']}")
                else:
                    self.update_status("No class selected")
            else:
                self.update_status("Class browser cancelled")
                
        except Exception as e:
            self.update_status(f"Error opening class browser: {e}")
            import traceback
            self.update_status(f"Traceback: {traceback.format_exc()}")
    
    def browse_properties(self):
        """Browse ontology properties"""
        if not self.ontology_manager:
            self.update_status("Please load ontologies first")
            return
        
        try:
            self.update_status("Opening property browser...")
            browser = SimpleOntologyBrowser(self.ontology_manager, mode='properties', parent=self)
            browser.load_data()
            
            # Debug info
            self.update_status(f"Property browser opened with {len(browser.all_items)} items")
            self.update_status(f"Selected ontology: {browser.ontology_combo.currentText()}")
            
            if browser.exec() == browser.DialogCode.Accepted:
                selected = browser.selected_item
                if selected:
                    self.update_status(f"Selected property: {selected['name']}\nURI: {selected['uri']}")
                else:
                    self.update_status("No property selected")
            else:
                self.update_status("Property browser cancelled")
                
        except Exception as e:
            self.update_status(f"Error opening property browser: {e}")
            import traceback
            self.update_status(f"Traceback: {traceback.format_exc()}")
    
    def update_status(self, message):
        """Update status text"""
        current_text = self.status_text.toPlainText()
        timestamp = f"[{QApplication.applicationName() or 'App'}]"
        new_text = f"{timestamp} {message}\n{current_text}"
        self.status_text.setPlainText(new_text)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("OntologyBrowser")
    
    window = OntologyBrowserApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
