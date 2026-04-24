#!/usr/bin/env python3
"""
Ontology Browser Dialog
Allows users to explore and select from loaded ontologies
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QLineEdit, QTabWidget, QWidget, QMessageBox,
    QFileDialog, QSplitter, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.uic import loadUi
from pathlib import Path
from typing import Dict, List, Any, Optional
from rdflib import Graph, Namespace, URIRef, RDF, RDFS, OWL
import os
import requests
import hashlib
from urllib.parse import urlparse

class OntologyDownloadThread(QThread):
    """Thread for downloading ontologies in background"""
    
    progress_updated = pyqtSignal(int, str)  # progress, message
    download_completed = pyqtSignal(str, str)  # name, file_path
    download_failed = pyqtSignal(str, str)  # name, error
    
    def __init__(self, name: str, url: str, cache_dir: str):
        super().__init__()
        self.name = name
        self.url = url
        self.cache_dir = cache_dir
    
    def run(self):
        try:
            self.progress_updated.emit(10, f"Starting download of {self.name}...")
            
            # Download the file
            response = requests.get(self.url, timeout=30)
            response.raise_for_status()
            
            self.progress_updated.emit(50, f"Downloaded {self.name}, saving...")
            
            # Determine file extension from URL or content type
            file_ext = self._get_file_extension(response)
            filename = f"{self.name.lower().replace(' ', '_')}.{file_ext}"
            file_path = os.path.join(self.cache_dir, filename)
            
            # Save to cache
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            self.progress_updated.emit(100, f"{self.name} downloaded successfully")
            self.download_completed.emit(self.name, file_path)
            
        except Exception as e:
            self.download_failed.emit(self.name, str(e))
    
    def _get_file_extension(self, response):
        """Determine file extension from URL or content type"""
        # Try to get from URL
        parsed_url = urlparse(self.url)
        path = parsed_url.path.lower()
        if path.endswith('.ttl'):
            return 'ttl'
        elif path.endswith('.rdf'):
            return 'rdf'
        elif path.endswith('.jsonld'):
            return 'jsonld'
        elif path.endswith('.xml'):
            return 'rdf'
        
        # Try content type
        content_type = response.headers.get('content-type', '').lower()
        if 'text/turtle' in content_type:
            return 'ttl'
        elif 'rdf+xml' in content_type:
            return 'rdf'
        elif 'json+ld' in content_type:
            return 'jsonld'
        
        # Default to ttl
        return 'ttl'


class OntologyBrowserDialog(QDialog):
    """Dialog for browsing and selecting from ontologies"""
    
    # Signal emitted when user selects a class/property
    term_selected = pyqtSignal(str, str, str)  # term_type, name, uri
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.loaded_ontologies = {}
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ontologies", "cache")
        self.download_threads = {}
        
        # Load UI from file
        ui_path = Path(__file__).parent.parent.parent / "ui" / "ontology_browser.ui"
        loadUi(str(ui_path), self)
        
        # Set up connections
        self.import_btn.clicked.connect(self.import_ontology)
        self.search_edit.textChanged.connect(self.filter_ontologies)
        self.ontology_tree.itemClicked.connect(self.on_ontology_clicked)
        self.terms_tree.itemDoubleClicked.connect(self.on_term_selected)
        self.use_btn.clicked.connect(self.use_selected_term)
        self.cancel_btn.clicked.connect(self.reject)
        
        # Set splitter sizes
        self.mainSplitter.setSizes([300, 500])
        
        self.load_default_ontologies()
    
        
    def load_default_ontologies(self):
        """Load default ontologies from cache or download if needed"""
        default_ontologies = {
            "Schema.org": {
                "namespace": "http://schema.org/",
                "uri": "https://schema.org/version/latest/schemaorg-current-https.ttl",
                "classes": [
                    "Person", "Student", "Employee", "Organization", "Product", 
                    "Event", "Place", "PostalAddress", "Book", "Vehicle"
                ],
                "properties": [
                    "name", "firstName", "lastName", "email", "telephone", 
                    "birthDate", "address", "description", "url", "price"
                ]
            },
            "FOAF": {
                "namespace": "http://xmlns.com/foaf/0.1/",
                "uri": "http://xmlns.com/foaf/spec/index.rdf",
                "classes": ["Person", "Organization", "Document", "Project", "Group"],
                "properties": ["name", "firstName", "lastName", "mbox", "phone", "knows", "member"]
            },
            "DCTERMS": {
                "namespace": "http://purl.org/dc/terms/",
                "uri": "http://purl.org/dc/terms/",
                "classes": [],
                "properties": ["title", "description", "creator", "date", "subject", "publisher"]
            },
            "BRICK": {
                "namespace": "https://brickschema.org/schema/Brick#",
                "uri": "https://brickschema.org/schema/1.3.0/Brick.ttl",
                "classes": [
                    "Building", "Equipment", "Sensor", "HVAC", "Lighting", 
                    "Meter", "Space", "Point"
                ],
                "properties": [
                    "hasPoint", "hasPart", "isPartOf", "feeds", "isFedBy",
                    "controls", "isControlledBy", "measures", "hasTag"
                ]
            }
        }
        
        self.ontology_tree.clear()
        self.loaded_ontologies = {}
        
        # Check for cached files and load/download as needed
        for name, ontology in default_ontologies.items():
            cached_file = self.get_cached_file_path(name, ontology["uri"])
            
            if cached_file and os.path.exists(cached_file):
                # Load from cache
                try:
                    ontology_data = self.parse_ontology_file(cached_file)
                    if ontology_data:
                        self.loaded_ontologies[name] = ontology_data
                        item = QTreeWidgetItem(self.ontology_tree, [
                            name, 
                            str(len(ontology_data["classes"])), 
                            str(len(ontology_data["properties"]))
                        ])
                        item.setData(0, Qt.ItemDataRole.UserRole, ontology_data)
                        continue
                except Exception as e:
                    print(f"Error loading cached ontology {name}: {e}")
            
            # Download needed - add placeholder and start download
            item = QTreeWidgetItem(self.ontology_tree, [
                f"{name} (Download needed)", "0", "0"
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, ontology)
            self.download_ontology(name, ontology["uri"])
    
    def get_cached_file_path(self, name: str, uri: str) -> Optional[str]:
        """Get the cached file path for an ontology"""
        # Generate filename from name and URI
        parsed_url = urlparse(uri)
        file_ext = 'ttl'  # default
        if parsed_url.path.endswith('.ttl'):
            file_ext = 'ttl'
        elif parsed_url.path.endswith('.rdf'):
            file_ext = 'rdf'
        elif parsed_url.path.endswith('.jsonld'):
            file_ext = 'jsonld'
        
        filename = f"{name.lower().replace(' ', '_')}.{file_ext}"
        return os.path.join(self.cache_dir, filename)
    
    def download_ontology(self, name: str, uri: str):
        """Download ontology in background thread"""
        if name in self.download_threads:
            return  # Already downloading
        
        # Show progress UI
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.status_label.setText(f"Downloading {name}...")
        
        # Create and start download thread
        thread = OntologyDownloadThread(name, uri, self.cache_dir)
        thread.progress_updated.connect(self.on_download_progress)
        thread.download_completed.connect(self.on_download_completed)
        thread.download_failed.connect(self.on_download_failed)
        thread.finished.connect(lambda: self.cleanup_download_thread(name))
        
        self.download_threads[name] = thread
        thread.start()
    
    @pyqtSlot(int, str)
    def on_download_progress(self, progress: int, message: str):
        """Handle download progress updates"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)
    
    @pyqtSlot(str, str)
    def on_download_completed(self, name: str, file_path: str):
        """Handle successful download"""
        try:
            # Parse the downloaded ontology
            ontology_data = self.parse_ontology_file(file_path)
            if ontology_data:
                self.loaded_ontologies[name] = ontology_data
                
                # Update the tree widget item
                for i in range(self.ontology_tree.topLevelItemCount()):
                    item = self.ontology_tree.topLevelItem(i)
                    if name in item.text(0):
                        item.setText(0, name)
                        item.setText(1, str(len(ontology_data["classes"])))
                        item.setText(2, str(len(ontology_data["properties"])))
                        item.setData(0, Qt.ItemDataRole.UserRole, ontology_data)
                        break
                
                self.status_label.setText(f"{name} loaded successfully")
            else:
                self.status_label.setText(f"Failed to parse {name}")
        except Exception as e:
            self.status_label.setText(f"Error loading {name}: {str(e)}")
        
        # Hide progress UI after a delay
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
    
    @pyqtSlot(str, str)
    def on_download_failed(self, name: str, error: str):
        """Handle download failure - fallback to predefined data"""
        self.status_label.setText(f"Failed to download {name}: {error}")
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        
        # Fallback to predefined data if download fails
        self.use_fallback_data(name)
        
        QMessageBox.warning(self, "Download Failed", 
                          f"Failed to download {name}: {error}\n\nUsing predefined classes and properties.")
    
    def use_fallback_data(self, name: str):
        """Use predefined ontology data when download fails"""
        fallback_data = {
            "Schema.org": {
                "namespace": "http://schema.org/",
                "uri": "https://schema.org/version/latest/schemaorg-current-https.ttl",
                "classes": [
                    "Person", "Student", "Employee", "Organization", "Product", 
                    "Event", "Place", "PostalAddress", "Book", "Vehicle"
                ],
                "properties": [
                    "name", "firstName", "lastName", "email", "telephone", 
                    "birthDate", "address", "description", "url", "price"
                ]
            },
            "FOAF": {
                "namespace": "http://xmlns.com/foaf/0.1/",
                "uri": "http://xmlns.com/foaf/spec/index.rdf",
                "classes": ["Person", "Organization", "Document", "Project", "Group"],
                "properties": ["name", "firstName", "lastName", "mbox", "phone", "knows", "member"]
            },
            "DCTERMS": {
                "namespace": "http://purl.org/dc/terms/",
                "uri": "http://purl.org/dc/terms/",
                "classes": [],
                "properties": ["title", "description", "creator", "date", "subject", "publisher"]
            },
            "BRICK": {
                "namespace": "https://brickschema.org/schema/Brick#",
                "uri": "https://brickschema.org/schema/1.3.0/Brick.ttl",
                "classes": [
                    "Building", "Equipment", "Sensor", "HVAC", "Lighting", 
                    "Meter", "Space", "Point"
                ],
                "properties": [
                    "hasPoint", "hasPart", "isPartOf", "feeds", "isFedBy",
                    "controls", "isControlledBy", "measures", "hasTag"
                ]
            }
        }
        
        if name in fallback_data:
            ontology_data = fallback_data[name]
            self.loaded_ontologies[name] = ontology_data
            
            # Update the tree widget item
            for i in range(self.ontology_tree.topLevelItemCount()):
                item = self.ontology_tree.topLevelItem(i)
                if name in item.text(0):
                    item.setText(0, f"{name} (Offline mode)")
                    item.setText(1, str(len(ontology_data["classes"])))
                    item.setText(2, str(len(ontology_data["properties"])))
                    item.setData(0, Qt.ItemDataRole.UserRole, ontology_data)
                    break
    
    def cleanup_download_thread(self, name: str):
        """Clean up completed download thread"""
        if name in self.download_threads:
            del self.download_threads[name]
    
    def import_ontology(self):
        """Import ontology file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Ontology",
            "",
            "Turtle Files (*.ttl);;RDF/XML Files (*.rdf);;JSON-LD Files (*.jsonld);;All Files (*)"
        )
        
        if file_path:
            try:
                ontology_data = self.parse_ontology_file(file_path)
                if ontology_data:
                    name = os.path.basename(file_path).split('.')[0]
                    self.loaded_ontologies[name] = ontology_data
                    
                    # Add to tree
                    item = QTreeWidgetItem(self.ontology_tree, [
                        name,
                        str(len(ontology_data["classes"])),
                        str(len(ontology_data["properties"]))
                    ])
                    item.setData(0, Qt.ItemDataRole.UserRole, ontology_data)
                    
                    QMessageBox.information(self, "Success", f"Ontology '{name}' imported successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Could not parse ontology file")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import ontology: {str(e)}")
    
    def parse_ontology_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse ontology file and extract classes/properties"""
        try:
            graph = Graph()
            graph.parse(file_path)
            
            # Extract classes
            classes = []
            for subject in graph.subjects(RDF.type, OWL.Class):
                if isinstance(subject, URIRef):
                    classes.append(str(subject).split('#')[-1].split('/')[-1])
            
            for subject in graph.subjects(RDF.type, RDFS.Class):
                if isinstance(subject, URIRef):
                    name = str(subject).split('#')[-1].split('/')[-1]
                    if name not in classes:
                        classes.append(name)
            
            # Extract properties
            properties = []
            for subject in graph.subjects(RDF.type, OWL.ObjectProperty):
                if isinstance(subject, URIRef):
                    properties.append(str(subject).split('#')[-1].split('/')[-1])
            
            for subject in graph.subjects(RDF.type, OWL.DatatypeProperty):
                if isinstance(subject, URIRef):
                    name = str(subject).split('#')[-1].split('/')[-1]
                    if name not in properties:
                        properties.append(name)
            
            # Get namespace
            namespaces = list(graph.namespaces())
            namespace = ""
            if namespaces:
                namespace = str(namespaces[0][1])
            
            return {
                "namespace": namespace,
                "uri": file_path,
                "classes": classes,
                "properties": properties
            }
        except Exception as e:
            print(f"Error parsing ontology: {e}")
            return None
    
    def on_ontology_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle ontology selection"""
        ontology_data = item.data(0, Qt.ItemDataRole.UserRole)
        if ontology_data:
            self.display_ontology_terms(ontology_data)
    
    def display_ontology_terms(self, ontology_data: Dict[str, Any]):
        """Display classes and properties from selected ontology"""
        self.terms_tree.clear()
        
        # Add classes
        if ontology_data["classes"]:
            classes_item = QTreeWidgetItem(self.terms_tree, ["Classes", "", ""])
            for class_name in ontology_data["classes"]:
                class_uri = ontology_data["namespace"] + class_name
                class_item = QTreeWidgetItem(classes_item, ["Class", class_name, class_uri])
                class_item.setData(0, Qt.ItemDataRole.UserRole, ("class", class_name, class_uri))
        
        # Add properties
        if ontology_data["properties"]:
            props_item = QTreeWidgetItem(self.terms_tree, ["Properties", "", ""])
            for prop_name in ontology_data["properties"]:
                prop_uri = ontology_data["namespace"] + prop_name
                prop_item = QTreeWidgetItem(props_item, ["Property", prop_name, prop_uri])
                prop_item.setData(0, Qt.ItemDataRole.UserRole, ("property", prop_name, prop_uri))
        
        self.terms_tree.expandAll()
    
    def on_term_selected(self, item: QTreeWidgetItem, column: int):
        """Handle term double-click"""
        term_data = item.data(0, Qt.ItemDataRole.UserRole)
        if term_data:
            term_type, name, uri = term_data
            self.term_selected.emit(term_type, name, uri)
            self.accept()
    
    def use_selected_term(self):
        """Use currently selected term"""
        current_item = self.terms_tree.currentItem()
        if current_item:
            term_data = current_item.data(0, Qt.ItemDataRole.UserRole)
            if term_data:
                term_type, name, uri = term_data
                self.term_selected.emit(term_type, name, uri)
                self.accept()
            else:
                QMessageBox.information(self, "Info", "Please select a class or property from the list")
        else:
            QMessageBox.information(self, "Info", "Please select a class or property from the list")
    
    def filter_ontologies(self, text: str):
        """Filter ontologies based on search"""
        # Simple implementation - could be enhanced
        for i in range(self.ontology_tree.topLevelItemCount()):
            item = self.ontology_tree.topLevelItem(i)
            item.setHidden(text.lower() not in item.text(0).lower())
