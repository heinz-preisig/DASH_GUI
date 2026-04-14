#!/usr/bin/env python3
"""
Refactored Guided SHACL Brick Generator
Uses clean frontend/backend separation with simple interfaces
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt

from shacl_brick_app.core.brick_backend import BrickBackendAPI
from shacl_brick_app.core.editor_backend import BrickEditorBackend
from shacl_brick_app.core.editor_controller import SimpleEditorFactory

class RefactoredGuidedGUI(QMainWindow):
    """Main window for refactored guided brick creation"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SHACL Brick Generator - Refactored")
        self.setGeometry(100, 100, 1000, 700)
        
        # Initialize backend
        self.brick_api = BrickBackendAPI()
        self.editor_backend = BrickEditorBackend(self.brick_api)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("🧱 SHACL Brick Generator - Refactored Architecture")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background: #e8f5e8; border-radius: 5px;")
        layout.addWidget(header)
        
        # Tab widget for different views
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_editor_tab()
        self.create_browser_tab()
        self.create_info_tab()
        
        # Status bar
        self.statusBar().showMessage("Ready - Using clean frontend/backend separation")
    
    def create_editor_tab(self):
        """Create editor tab"""
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        # Create editor using factory
        self.editor_widget, self.editor_controller = SimpleEditorFactory.create_editor(
            self.editor_backend, self
        )
        
        editor_layout.addWidget(self.editor_widget)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        new_btn = QPushButton("🆕 New Brick")
        new_btn.clicked.connect(self.create_new_brick)
        button_layout.addWidget(new_btn)
        
        save_btn = QPushButton("💾 Save Brick")
        save_btn.clicked.connect(self.save_brick)
        button_layout.addWidget(save_btn)
        
        load_btn = QPushButton("📁 Load Brick")
        load_btn.clicked.connect(self.load_brick)
        button_layout.addWidget(load_btn)
        
        button_layout.addStretch()
        
        editor_layout.addLayout(button_layout)
        
        self.tabs.addTab(editor_widget, "🔧 Brick Editor")
    
    def create_browser_tab(self):
        """Create the ontology browser tab"""
        browser_widget = QWidget()
        browser_layout = QVBoxLayout(browser_widget)
        
        # Create ontology browser
        self.ontology_browser = SimpleEditorFactory.create_ontology_browser(
            self.editor_backend, self
        )
        
        browser_layout.addWidget(self.ontology_browser)
        
        # Import button
        import_btn = QPushButton("📥 Import Ontology File")
        import_btn.clicked.connect(self.import_ontology)
        browser_layout.addWidget(import_btn)
        
        self.tabs.addTab(browser_widget, "📚 Ontology Browser")
    
    def create_info_tab(self):
        """Create information tab"""
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        info_text = """
        <h3>Refactored SHACL Brick Generator</h3>
        
        <h4>🏗️ Architecture Benefits:</h4>
        <ul>
            <li><b>Frontend/Backend Separation:</b> Clean separation of UI and business logic</li>
            <li><b>Technology Agnostic:</b> Frontends can be swapped (Qt, Web, etc.)</li>
            <li><b>Simple Interfaces:</b> Easy to understand and maintain</li>
            <li><b>Ontology Freedom:</b> Browse and import any ontology</li>
        </ul>
        
        <h4>🚀 How to Use:</h4>
        <ol>
            <li><b>Brick Editor Tab:</b> Create and edit SHACL bricks with simple forms</li>
            <li><b>Ontology Browser Tab:</b> Explore classes and properties from loaded ontologies</li>
            <li><b>Import Custom Ontologies:</b> Add your own ontology files</li>
        </ol>
        
        <h4>📚 Available Ontologies:</h4>
        <ul>
            <li><b>Schema.org:</b> General web vocabulary (Person, Organization, Product, etc.)</li>
            <li><b>FOAF:</b> Friend of a Friend vocabulary (social network data)</li>
            <li><b>BRICK:</b> Building and IoT vocabulary (sensors, equipment, etc.)</li>
            <li><b>Custom:</b> Import your own ontology files (.ttl, .rdf, .jsonld)</li>
        </ul>
        
        <h4>🔧 Technical Details:</h4>
        <ul>
            <li><b>MVC Pattern:</b> Model-View-Controller architecture</li>
            <li><b>Abstract Interfaces:</b> Technology-agnostic frontend definitions</li>
            <li><b>Factory Pattern:</b> Easy creation of editor components</li>
            <li><b>Clean Separation:</b> Business logic isolated from UI code</li>
        </ul>
        """
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 10px; background: #f8f9fa; border-radius: 5px;")
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        
        self.tabs.addTab(info_widget, "ℹ️ Information")
    
    def create_new_brick(self):
        """Create a new brick"""
        self.editor_controller.create_new_brick("NodeShape")
        self.statusBar().showMessage("New brick created")
    
    def save_brick(self):
        """Save current brick"""
        self.editor_controller.save_brick()
    
    def load_brick(self):
        """Load existing brick"""
        # For now, just show message
        QMessageBox.information(self, "Load Brick", 
                           "Brick loading feature will be implemented with brick list browser")
    
    def import_ontology(self):
        """Import ontology file"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Ontology",
            "",
            "Turtle Files (*.ttl);;RDF/XML Files (*.rdf);;JSON-LD Files (*.jsonld);;All Files (*)"
        )
        
        if file_path:
            self.editor_controller.import_ontology(file_path)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = RefactoredGuidedGUI()
    window.show()
    
    # Load initial brick
    window.create_new_brick()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
