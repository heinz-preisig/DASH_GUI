#!/usr/bin/env python3
"""
SHACL Frontend - UI component for SHACL brick editor
Separated from backend for clean architecture
"""

import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from shacl_backend import SHACLBackend, SHACLEventProcessor

class SHACLFrontend(QMainWindow):
    """Frontend UI for SHACL brick editor"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SHACL Brick Editor")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize backend
        self.backend = SHACLBackend()
        self.event_processor = SHACLEventProcessor(self.backend)
        
        # UI components
        self.init_ui()
        self.load_ontologies()
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Ontology/Term browser
        left_panel = self.create_ontology_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Center panel - Brick builder
        center_panel = self.create_brick_panel()
        main_layout.addWidget(center_panel, 2)
        
        # Right panel - SHACL preview
        right_panel = self.create_preview_panel()
        main_layout.addWidget(right_panel, 1)
    
    def create_ontology_panel(self):
        """Create ontology and term browser panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("Ontology Browser")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(header)
        
        # Ontology selection
        layout.addWidget(QLabel("Select Ontology:"))
        self.ontology_list = QListWidget()
        self.ontology_list.itemClicked.connect(self.on_ontology_selected)
        layout.addWidget(self.ontology_list)
        
        # Term selection
        layout.addWidget(QLabel("Available Terms:"))
        self.term_list = QListWidget()
        self.term_list.itemDoubleClicked.connect(self.on_term_double_clicked)
        layout.addWidget(self.term_list)
        
        return panel
    
    def create_brick_panel(self):
        """Create brick building panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("Brick Builder")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(header)
        
        # Brick creation toolbar
        toolbar = self.create_brick_toolbar()
        layout.addLayout(toolbar)
        
        # Brick tree
        layout.addWidget(QLabel("SHACL Bricks:"))
        self.brick_tree = QTreeWidget()
        self.brick_tree.setHeaderLabels(["Type", "Name", "Properties"])
        self.brick_tree.setColumnWidth(0, 150)
        self.brick_tree.setColumnWidth(1, 200)
        self.brick_tree.setColumnWidth(2, 300)
        self.brick_tree.itemClicked.connect(self.on_brick_selected)
        layout.addWidget(self.brick_tree)
        
        # Brick operations
        ops_layout = QHBoxLayout()
        
        remove_btn = QPushButton("Remove Brick")
        remove_btn.clicked.connect(self.remove_selected_brick)
        remove_btn.setStyleSheet("background-color: #f44336; color: white; padding: 5px;")
        ops_layout.addWidget(remove_btn)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_all_bricks)
        clear_btn.setStyleSheet("background-color: #9e9e9e; color: white; padding: 5px;")
        ops_layout.addWidget(clear_btn)
        
        layout.addLayout(ops_layout)
        
        return panel
    
    def create_brick_toolbar(self):
        """Create brick creation toolbar"""
        toolbar = QHBoxLayout()
        
        # NodeShape button
        node_btn = QPushButton("NodeShape")
        node_btn.clicked.connect(self.create_node_shape)
        node_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; font-weight: bold;")
        toolbar.addWidget(node_btn)
        
        # PropertyShape button
        prop_btn = QPushButton("PropertyShape")
        prop_btn.clicked.connect(self.create_property_shape)
        prop_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px; font-weight: bold;")
        toolbar.addWidget(prop_btn)
        
        # Primitive button
        primitive_btn = QPushButton("Primitive")
        primitive_btn.clicked.connect(self.create_primitive)
        primitive_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 8px; font-weight: bold;")
        toolbar.addWidget(primitive_btn)
        
        toolbar.addStretch()
        
        return toolbar
    
    def create_preview_panel(self):
        """Create SHACL preview panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("SHACL Preview")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(header)
        
        # SHACL preview
        self.shacl_preview = QTextEdit()
        self.shacl_preview.setReadOnly(True)
        self.shacl_preview.setFont(QFont("Courier", 10))
        self.shacl_preview.setStyleSheet("background-color: #f5f5f5; padding: 10px;")
        layout.addWidget(self.shacl_preview)
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        export_btn = QPushButton("Export SHACL")
        export_btn.clicked.connect(self.export_shacl)
        export_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; font-weight: bold;")
        export_layout.addWidget(export_btn)
        
        refresh_btn = QPushButton("Refresh Preview")
        refresh_btn.clicked.connect(self.refresh_preview)
        refresh_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        export_layout.addWidget(refresh_btn)
        
        layout.addLayout(export_layout)
        
        return panel
    
    def load_ontologies(self):
        """Load ontologies into UI"""
        result = self.event_processor.process_event({"event": "get_ontology_list"})
        
        if result["status"] == "success":
            self.ontology_list.clear()
            for ontology in result["data"]:
                item = QListWidgetItem(f"{ontology['name']}: {ontology['uri']}")
                item.setData(Qt.ItemDataRole.UserRole, ontology)
                self.ontology_list.addItem(item)
    
    def on_ontology_selected(self, item):
        """Handle ontology selection"""
        ontology_data = item.data(Qt.ItemDataRole.UserRole)
        
        result = self.event_processor.process_event({
            "event": "get_ontology_terms",
            "ontology": ontology_data["name"]
        })
        
        if result["status"] == "success":
            self.term_list.clear()
            for term in result["data"]:
                item = QListWidgetItem(f"{term['name']}: {term.get('description', '')}")
                item.setData(Qt.ItemDataRole.UserRole, term)
                self.term_list.addItem(item)
    
    def on_term_double_clicked(self, item):
        """Handle term double-click - create brick from term"""
        term_data = item.data(Qt.ItemDataRole.UserRole)
        if term_data:
            # Get current ontology name
            current_item = self.ontology_list.currentItem()
            if current_item:
                ontology_data = current_item.data(Qt.ItemDataRole.UserRole)
                
                result = self.event_processor.process_event({
                    "event": "create_brick_from_term",
                    "ontology": ontology_data["name"],
                    "term": term_data["name"]
                })
                
                if result["status"] == "success":
                    self.add_brick_to_tree(result["data"])
                    self.refresh_preview()
                else:
                    QMessageBox.warning(self, "Error", result["message"])
    
    def create_node_shape(self):
        """Create a NodeShape brick"""
        dialog = NodeShapeDialog(self)
        if dialog.exec():
            result = self.event_processor.process_event({
                "event": "create_property_brick",
                **dialog.get_brick_data()
            })
            
            if result["status"] == "success":
                self.add_brick_to_tree(result["data"])
                self.refresh_preview()
            else:
                QMessageBox.warning(self, "Error", result["message"])
    
    def create_property_shape(self):
        """Create a PropertyShape brick"""
        dialog = PropertyShapeDialog(self)
        if dialog.exec():
            result = self.event_processor.process_event({
                "event": "create_property_brick",
                **dialog.get_brick_data()
            })
            
            if result["status"] == "success":
                self.add_brick_to_tree(result["data"])
                self.refresh_preview()
            else:
                QMessageBox.warning(self, "Error", result["message"])
    
    def create_primitive(self):
        """Create a primitive brick"""
        dialog = PrimitiveDialog(self)
        if dialog.exec():
            result = self.event_processor.process_event({
                "event": "create_primitive_brick",
                **dialog.get_brick_data()
            })
            
            if result["status"] == "success":
                self.add_brick_to_tree(result["data"])
                self.refresh_preview()
            else:
                QMessageBox.warning(self, "Error", result["message"])
    
    def add_brick_to_tree(self, brick_data):
        """Add brick to tree widget"""
        # Create tree item
        item = QTreeWidgetItem(self.brick_tree)
        
        brick_type = brick_data["type"]
        brick_name = brick_data["name"]
        properties = brick_data.get("properties", {})
        
        # Set item data
        item.setText(0, self.get_brick_icon(brick_type) + " " + brick_type)
        item.setText(1, brick_name)
        item.setText(2, self.format_properties(properties))
        
        item.setData(0, Qt.ItemDataRole.UserRole, brick_data)
        
        # Color coding
        color = self.get_brick_color(brick_type)
        item.setForeground(0, color)
        
        # Add to tree
        self.brick_tree.addTopLevelItem(item)
        item.setExpanded(True)
    
    def get_brick_icon(self, brick_type):
        """Get icon for brick type"""
        icons = {
            "NodeShape": "NodeShape",
            "PropertyShape": "PropertyShape", 
            "Primitive": "Primitive"
        }
        return icons.get(brick_type, "?")
    
    def get_brick_color(self, brick_type):
        """Get color for brick type"""
        colors = {
            "NodeShape": QColor("#4CAF50"),
            "PropertyShape": QColor("#2196F3"),
            "Primitive": QColor("#FF9800")
        }
        return colors.get(brick_type, QColor("#000000"))
    
    def format_properties(self, properties):
        """Format properties for display"""
        if not properties:
            return ""
        
        props = []
        for key, value in properties.items():
            if key != "type":  # Skip type as it's already shown
                props.append(f"{key}: {value}")
        
        return ", ".join(props[:3]) + ("..." if len(props) > 3 else "")
    
    def on_brick_selected(self, item, column):
        """Handle brick selection"""
        if column == 1:  # Name column
            brick_data = item.data(0, Qt.ItemDataRole.UserRole)
            if brick_data:
                self.show_brick_details(brick_data)
    
    def show_brick_details(self, brick_data):
        """Show brick details in a dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Brick Details: {brick_data['name']}")
        layout = QVBoxLayout(dialog)
        
        # Brick info
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setPlainText(f"Type: {brick_data['type']}\n"
                             f"Name: {brick_data['name']}\n"
                             f"URI: {brick_data['uri']}\n\n"
                             f"Properties:\n")
        
        for key, value in brick_data.get("properties", {}).items():
            info_text.append(f"  {key}: {value}")
        
        layout.addWidget(info_text)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def remove_selected_brick(self):
        """Remove selected brick"""
        current_item = self.brick_tree.currentItem()
        if current_item:
            index = self.brick_tree.indexOfTopLevelItem(current_item)
            
            result = self.event_processor.process_event({
                "event": "remove_brick",
                "index": index
            })
            
            if result["status"] == "success":
                self.brick_tree.takeTopLevelItem(index)
                self.refresh_preview()
            else:
                QMessageBox.warning(self, "Error", result["message"])
    
    def clear_all_bricks(self):
        """Clear all bricks"""
        reply = QMessageBox.question(self, "Clear All", 
                                   "Are you sure you want to clear all bricks?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            result = self.event_processor.process_event({"event": "clear_bricks"})
            
            if result["status"] == "success":
                self.brick_tree.clear()
                self.refresh_preview()
    
    def refresh_preview(self):
        """Refresh SHACL preview"""
        result = self.event_processor.process_event({"event": "export_shacl"})
        
        if result["status"] == "success":
            self.shacl_preview.setPlainText(result["data"])
        else:
            self.shacl_preview.setPlainText(f"Error: {result['message']}")
    
    def export_shacl(self):
        """Export SHACL to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export SHACL",
            "",
            "SHACL Files (*.ttl);;All Files (*)"
        )
        
        if file_path:
            result = self.event_processor.process_event({"event": "export_shacl"})
            
            if result["status"] == "success":
                with open(file_path, 'w') as f:
                    f.write(result["data"])
                QMessageBox.information(self, "Export Complete", f"SHACL exported to {file_path}")
            else:
                QMessageBox.warning(self, "Export Error", result["message"])


class NodeShapeDialog(QDialog):
    """Dialog for creating NodeShape bricks"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create NodeShape")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Name
        layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        
        # Target Class
        layout.addWidget(QLabel("Target Class:"))
        self.target_class_edit = QLineEdit()
        layout.addWidget(self.target_class_edit)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        layout.addWidget(self.description_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("Create")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def get_brick_data(self):
        """Get brick data from dialog"""
        return {
            "event": "create_property_brick",
            "name": self.name_edit.text(),
            "path": self.target_class_edit.text(),
            "description": self.description_edit.toPlainText()
        }


class PropertyShapeDialog(QDialog):
    """Dialog for creating PropertyShape bricks"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create PropertyShape")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Name
        layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        
        # Path
        layout.addWidget(QLabel("Path:"))
        self.path_edit = QLineEdit()
        layout.addWidget(self.path_edit)
        
        # Datatype
        layout.addWidget(QLabel("Datatype:"))
        self.datatype_combo = QComboBox()
        self.datatype_combo.addItems(["string", "integer", "decimal", "date", "boolean", "uri"])
        layout.addWidget(self.datatype_combo)
        
        # Constraints
        constraints_layout = QHBoxLayout()
        
        min_layout = QVBoxLayout()
        min_layout.addWidget(QLabel("Min Count:"))
        self.min_count_spin = QSpinBox()
        self.min_count_spin.setMinimum(0)
        self.min_count_spin.setMaximum(999)
        min_layout.addWidget(self.min_count_spin)
        constraints_layout.addLayout(min_layout)
        
        max_layout = QVBoxLayout()
        max_layout.addWidget(QLabel("Max Count:"))
        self.max_count_spin = QSpinBox()
        self.max_count_spin.setMinimum(0)
        self.max_count_spin.setMaximum(999)
        max_layout.addWidget(self.max_count_spin)
        constraints_layout.addLayout(max_layout)
        
        layout.addLayout(constraints_layout)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        layout.addWidget(self.description_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("Create")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def get_brick_data(self):
        """Get brick data from dialog"""
        return {
            "event": "create_property_brick",
            "name": self.name_edit.text(),
            "path": self.path_edit.text(),
            "datatype": self.datatype_combo.currentText(),
            "min_count": self.min_count_spin.value() if self.min_count_spin.value() > 0 else None,
            "max_count": self.max_count_spin.value() if self.max_count_spin.value() > 0 else None,
            "description": self.description_edit.toPlainText()
        }


class PrimitiveDialog(QDialog):
    """Dialog for creating primitive bricks"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Primitive")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Name
        layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        
        # Type
        layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["string", "integer", "decimal", "date", "boolean", "uri"])
        layout.addWidget(self.type_combo)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        layout.addWidget(self.description_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("Create")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def get_brick_data(self):
        """Get brick data from dialog"""
        return {
            "event": "create_primitive_brick",
            "name": self.name_edit.text(),
            "type": self.type_combo.currentText(),
            "description": self.description_edit.toPlainText()
        }


def main():
    app = QApplication(sys.argv)
    frontend = SHACLFrontend()
    frontend.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
