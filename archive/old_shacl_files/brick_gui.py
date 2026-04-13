#!/usr/bin/env python3
"""
PyQt6 GUI Frontend for SHACL Brick Generator (Step 1)
Visual testing interface for the brick generator backend
"""

import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from brick_backend import BrickBackendAPI, BrickEventProcessor

class BrickGUI(QMainWindow):
    """Main GUI for SHACL Brick Generator"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SHACL Brick Generator - Step 1")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize backend
        self.backend = BrickBackendAPI("gui_repositories")
        self.processor = BrickEventProcessor(self.backend)
        
        # Ensure active library
        self._ensure_active_library()
        
        # UI setup
        self.init_ui()
        self.load_data()
    
    def _ensure_active_library(self):
        """Ensure we have an active library"""
        result = self.processor.process_event({"event": "get_repository_info"})
        if not result["data"]["active_library"]:
            self.processor.process_event({"event": "set_active_library", "library_name": "default"})
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Library management
        left_panel = self.create_library_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Center panel - Brick list and details
        center_panel = self.create_brick_panel()
        main_layout.addWidget(center_panel, 2)
        
        # Right panel - Brick creation and SHACL output
        right_panel = self.create_creation_panel()
        main_layout.addWidget(right_panel, 1)
    
    def create_library_panel(self):
        """Create library management panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("Library Management")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(header)
        
        # Library info
        self.library_info = QTextEdit()
        self.library_info.setReadOnly(True)
        self.library_info.setMaximumHeight(100)
        layout.addWidget(QLabel("Library Info:"))
        layout.addWidget(self.library_info)
        
        # Library controls
        lib_controls = QVBoxLayout()
        
        create_lib_btn = QPushButton("Create New Library")
        create_lib_btn.clicked.connect(self.create_library)
        lib_controls.addWidget(create_lib_btn)
        
        export_lib_btn = QPushButton("Export Library")
        export_lib_btn.clicked.connect(self.export_library)
        lib_controls.addWidget(export_lib_btn)
        
        import_lib_btn = QPushButton("Import Library")
        import_lib_btn.clicked.connect(self.import_library)
        lib_controls.addWidget(import_lib_btn)
        
        layout.addLayout(lib_controls)
        
        # Statistics
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(150)
        layout.addWidget(QLabel("Statistics:"))
        layout.addWidget(self.stats_text)
        
        layout.addStretch()
        return panel
    
    def create_brick_panel(self):
        """Create brick list and details panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("Brick Library")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(header)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search bricks...")
        self.search_edit.textChanged.connect(self.search_bricks)
        search_layout.addWidget(self.search_edit)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_bricks)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Filter options
        filter_layout = QHBoxLayout()
        self.object_type_combo = QComboBox()
        self.object_type_combo.addItems(["All", "NodeShape", "PropertyShape"])
        self.object_type_combo.currentTextChanged.connect(self.filter_bricks)
        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.object_type_combo)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_bricks)
        filter_layout.addWidget(refresh_btn)
        
        layout.addLayout(filter_layout)
        
        # Brick list
        self.brick_list = QListWidget()
        self.brick_list.itemClicked.connect(self.on_brick_selected)
        self.brick_list.itemDoubleClicked.connect(self.edit_brick)
        layout.addWidget(self.brick_list)
        
        # Brick details
        layout.addWidget(QLabel("Brick Details:"))
        self.brick_details = QTextEdit()
        self.brick_details.setReadOnly(True)
        self.brick_details.setMaximumHeight(200)
        layout.addWidget(self.brick_details)
        
        # Brick actions
        actions_layout = QHBoxLayout()
        
        delete_btn = QPushButton("Delete Brick")
        delete_btn.clicked.connect(self.delete_brick)
        delete_btn.setStyleSheet("background-color: #f44336; color: white; padding: 5px;")
        actions_layout.addWidget(delete_btn)
        
        export_btn = QPushButton("Export SHACL")
        export_btn.clicked.connect(self.export_brick_shacl)
        export_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
        actions_layout.addWidget(export_btn)
        
        layout.addLayout(actions_layout)
        
        return panel
    
    def create_creation_panel(self):
        """Create brick creation and SHACL output panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("Create Brick")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(header)
        
        # Brick type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Brick Type:"))
        self.brick_type_combo = QComboBox()
        self.brick_type_combo.addItems(["NodeShape", "PropertyShape"])
        self.brick_type_combo.currentTextChanged.connect(self.on_brick_type_changed)
        type_layout.addWidget(self.brick_type_combo)
        layout.addLayout(type_layout)
        
        # Basic fields
        self.brick_id_edit = QLineEdit()
        self.brick_id_edit.setPlaceholderText("Brick ID (e.g., my_brick)")
        layout.addWidget(QLabel("Brick ID:"))
        layout.addWidget(self.brick_id_edit)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Brick Name")
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Description")
        self.description_edit.setMaximumHeight(80)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.description_edit)
        
        # Dynamic fields based on brick type
        self.dynamic_fields = QWidget()
        self.dynamic_layout = QVBoxLayout(self.dynamic_fields)
        layout.addWidget(self.dynamic_fields)
        
        # Tags
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Tags (comma-separated)")
        layout.addWidget(QLabel("Tags:"))
        layout.addWidget(self.tags_edit)
        
        # Create button
        create_btn = QPushButton("Create Brick")
        create_btn.clicked.connect(self.create_brick)
        create_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; font-weight: bold;")
        layout.addWidget(create_btn)
        
        # SHACL Output
        layout.addWidget(QLabel("SHACL Output:"))
        self.shacl_output = QTextEdit()
        self.shacl_output.setReadOnly(True)
        self.shacl_output.setFont(QFont("Courier", 10))
        self.shacl_output.setStyleSheet("background-color: #f5f5f5; padding: 10px;")
        layout.addWidget(self.shacl_output)
        
        layout.addStretch()
        return panel
    
    def on_brick_type_changed(self):
        """Handle brick type change"""
        brick_type = self.brick_type_combo.currentText()
        
        # Clear existing dynamic fields
        while self.dynamic_layout.count():
            child = self.dynamic_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if brick_type == "NodeShape":
            # Add target class field
            target_class_edit = QLineEdit()
            target_class_edit.setPlaceholderText("Target Class (e.g., foaf:Person)")
            self.dynamic_layout.addWidget(QLabel("Target Class:"))
            self.dynamic_layout.addWidget(target_class_edit)
            self.target_class_edit = target_class_edit
            
            # Add node kind field
            node_kind_combo = QComboBox()
            node_kind_combo.addItems(["sh:BlankNode", "sh:IRI", "sh:BlankNodeOrIRI", "sh:Literal", "sh:IRIOrLiteral", "sh:BlankNodeOrLiteral"])
            node_kind_combo.setCurrentText("sh:BlankNodeOrIRI")
            self.dynamic_layout.addWidget(QLabel("Node Kind:"))
            self.dynamic_layout.addWidget(node_kind_combo)
            self.node_kind_combo = node_kind_combo
            
        elif brick_type == "PropertyShape":
            # Add path field
            path_edit = QLineEdit()
            path_edit.setPlaceholderText("Property Path (e.g., foaf:name)")
            self.dynamic_layout.addWidget(QLabel("Property Path:"))
            self.dynamic_layout.addWidget(path_edit)
            self.path_edit = path_edit
            
            # Add datatype field
            datatype_combo = QComboBox()
            datatype_combo.addItems(["xsd:string", "xsd:integer", "xsd:decimal", "xsd:boolean", "xsd:date", "xsd:anyURI"])
            datatype_combo.setCurrentText("xsd:string")
            self.dynamic_layout.addWidget(QLabel("Datatype:"))
            self.dynamic_layout.addWidget(datatype_combo)
            self.datatype_combo = datatype_combo
            
            # Add constraint fields
            constraints_group = QGroupBox("Constraints")
            constraints_layout = QVBoxLayout(constraints_group)
            
            # Min count
            min_count_layout = QHBoxLayout()
            min_count_layout.addWidget(QLabel("Min Count:"))
            min_count_spin = QSpinBox()
            min_count_spin.setMinimum(0)
            min_count_spin.setMaximum(999)
            min_count_layout.addWidget(min_count_spin)
            constraints_layout.addLayout(min_count_layout)
            self.min_count_spin = min_count_spin
            
            # Max count
            max_count_layout = QHBoxLayout()
            max_count_layout.addWidget(QLabel("Max Count:"))
            max_count_spin = QSpinBox()
            max_count_spin.setMinimum(0)
            max_count_spin.setMaximum(999)
            max_count_layout.addWidget(max_count_spin)
            constraints_layout.addLayout(max_count_layout)
            self.max_count_spin = max_count_spin
            
            # Min length
            min_length_layout = QHBoxLayout()
            min_length_layout.addWidget(QLabel("Min Length:"))
            min_length_spin = QSpinBox()
            min_length_spin.setMinimum(0)
            min_length_spin.setMaximum(9999)
            min_length_layout.addWidget(min_length_spin)
            constraints_layout.addLayout(min_length_layout)
            self.min_length_spin = min_length_spin
            
            # Max length
            max_length_layout = QHBoxLayout()
            max_length_layout.addWidget(QLabel("Max Length:"))
            max_length_spin = QSpinBox()
            max_length_spin.setMinimum(0)
            max_length_spin.setMaximum(9999)
            max_length_layout.addWidget(max_length_spin)
            constraints_layout.addLayout(max_length_layout)
            self.max_length_spin = max_length_spin
            
            # Pattern
            pattern_edit = QLineEdit()
            pattern_edit.setPlaceholderText("Pattern (regex)")
            constraints_layout.addWidget(QLabel("Pattern:"))
            constraints_layout.addWidget(pattern_edit)
            self.pattern_edit = pattern_edit
            
            self.dynamic_layout.addWidget(constraints_group)
    
    def load_data(self):
        """Load initial data"""
        self.load_library_info()
        self.load_bricks()
        self.load_statistics()
    
    def load_library_info(self):
        """Load library information"""
        result = self.processor.process_event({"event": "get_repository_info"})
        if result["status"] == "success":
            info_text = f"Active Library: {result['data']['active_library']}\n"
            info_text += f"Total Libraries: {len(result['data']['libraries'])}\n"
            for lib in result['data']['libraries']:
                info_text += f"- {lib['name']}: {lib['brick_count']} bricks\n"
            self.library_info.setPlainText(info_text)
    
    def load_bricks(self):
        """Load brick list"""
        object_type = self.object_type_combo.currentText()
        if object_type == "All":
            object_type = None
            
        result = self.processor.process_event({
            "event": "get_library_bricks",
            "object_type": object_type
        })
        
        if result["status"] == "success":
            self.brick_list.clear()
            for brick in result["data"]["bricks"]:
                item = QListWidgetItem(f"{brick['name']} ({brick['object_type']})")
                item.setData(Qt.ItemDataRole.UserRole, brick)
                self.brick_list.addItem(item)
    
    def load_statistics(self):
        """Load library statistics"""
        result = self.processor.process_event({"event": "get_library_statistics"})
        if result["status"] == "success":
            stats = result["data"]
            stats_text = f"Total Bricks: {stats['total_bricks']}\n\n"
            stats_text += "Object Types:\n"
            for obj_type, count in stats['object_types'].items():
                stats_text += f"  {obj_type}: {count}\n"
            stats_text += "\nTags:\n"
            for tag, count in list(stats['tags'].items())[:10]:  # Show top 10
                stats_text += f"  {tag}: {count}\n"
            self.stats_text.setPlainText(stats_text)
    
    def search_bricks(self):
        """Search bricks"""
        query = self.search_edit.text().strip()
        if not query:
            self.load_bricks()
            return
            
        result = self.processor.process_event({
            "event": "search_bricks",
            "query": query
        })
        
        if result["status"] == "success":
            self.brick_list.clear()
            for brick in result["data"]["bricks"]:
                item = QListWidgetItem(f"{brick['name']} ({brick['object_type']})")
                item.setData(Qt.ItemDataRole.UserRole, brick)
                self.brick_list.addItem(item)
    
    def filter_bricks(self):
        """Filter bricks by object type"""
        self.load_bricks()
    
    def on_brick_selected(self, item):
        """Handle brick selection"""
        brick_data = item.data(Qt.ItemDataRole.UserRole)
        if brick_data:
            # Show details
            details_text = f"ID: {brick_data['brick_id']}\n"
            details_text += f"Name: {brick_data['name']}\n"
            details_text += f"Type: {brick_data['object_type']}\n"
            details_text += f"Description: {brick_data['description']}\n"
            details_text += f"Tags: {', '.join(brick_data['tags'])}\n"
            
            if brick_data['properties']:
                details_text += "\nProperties:\n"
                for key, value in brick_data['properties'].items():
                    details_text += f"  {key}: {value}\n"
            
            if brick_data['constraints']:
                details_text += "\nConstraints:\n"
                for constraint in brick_data['constraints']:
                    details_text += f"  {constraint['constraint_type']}: {constraint['value']}\n"
            
            self.brick_details.setPlainText(details_text)
    
    def create_brick(self):
        """Create a new brick"""
        brick_id = self.brick_id_edit.text().strip()
        name = self.name_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        tags = [tag.strip() for tag in self.tags_edit.text().split(",") if tag.strip()]
        
        if not brick_id or not name or not description:
            QMessageBox.warning(self, "Input Error", "Please fill in Brick ID, Name, and Description")
            return
        
        brick_type = self.brick_type_combo.currentText()
        
        try:
            if brick_type == "NodeShape":
                target_class = getattr(self, 'target_class_edit', None)
                target_class_value = target_class.text().strip() if target_class else None
                
                node_kind = getattr(self, 'node_kind_combo', None)
                node_kind_value = node_kind.currentText() if node_kind else "sh:BlankNodeOrIRI"
                
                properties = {"nodeKind": node_kind_value}
                if target_class_value:
                    properties["targetClass"] = target_class_value
                
                result = self.processor.process_event({
                    "event": "create_nodeshape_brick",
                    "brick_id": brick_id,
                    "name": name,
                    "description": description,
                    "target_class": target_class_value,
                    "properties": properties,
                    "tags": tags
                })
                
            elif brick_type == "PropertyShape":
                path = getattr(self, 'path_edit', None)
                path_value = path.text().strip() if path else None
                
                datatype = getattr(self, 'datatype_combo', None)
                datatype_value = datatype.currentText() if datatype else "xsd:string"
                
                if not path_value:
                    QMessageBox.warning(self, "Input Error", "Property Path is required for PropertyShape")
                    return
                
                properties = {"path": path_value, "datatype": datatype_value}
                
                # Collect constraints
                constraints = []
                min_count = getattr(self, 'min_count_spin', None)
                if min_count and min_count.value() > 0:
                    constraints.append({
                        "constraint_type": "MinCountConstraintComponent",
                        "value": min_count.value()
                    })
                
                max_count = getattr(self, 'max_count_spin', None)
                if max_count and max_count.value() > 0:
                    constraints.append({
                        "constraint_type": "MaxCountConstraintComponent", 
                        "value": max_count.value()
                    })
                
                min_length = getattr(self, 'min_length_spin', None)
                if min_length and min_length.value() > 0:
                    constraints.append({
                        "constraint_type": "MinLengthConstraintComponent",
                        "value": min_length.value()
                    })
                
                max_length = getattr(self, 'max_length_spin', None)
                if max_length and max_length.value() > 0:
                    constraints.append({
                        "constraint_type": "MaxLengthConstraintComponent",
                        "value": max_length.value()
                    })
                
                pattern = getattr(self, 'pattern_edit', None)
                if pattern and pattern.text().strip():
                    constraints.append({
                        "constraint_type": "PatternConstraintComponent",
                        "value": pattern.text().strip()
                    })
                
                result = self.processor.process_event({
                    "event": "create_propertyshape_brick",
                    "brick_id": brick_id,
                    "name": name,
                    "description": description,
                    "path": path_value,
                    "properties": properties,
                    "constraints": constraints,
                    "tags": tags
                })
            
            if result["status"] == "success":
                QMessageBox.information(self, "Success", f"Brick '{name}' created successfully!")
                self.clear_creation_form()
                self.load_bricks()
                self.load_statistics()
            else:
                QMessageBox.warning(self, "Error", f"Failed to create brick: {result['message']}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating brick: {str(e)}")
    
    def clear_creation_form(self):
        """Clear the creation form"""
        self.brick_id_edit.clear()
        self.name_edit.clear()
        self.description_edit.clear()
        self.tags_edit.clear()
        
        # Clear dynamic fields
        if hasattr(self, 'target_class_edit'):
            self.target_class_edit.clear()
        if hasattr(self, 'path_edit'):
            self.path_edit.clear()
        if hasattr(self, 'pattern_edit'):
            self.pattern_edit.clear()
        if hasattr(self, 'min_count_spin'):
            self.min_count_spin.setValue(0)
        if hasattr(self, 'max_count_spin'):
            self.max_count_spin.setValue(0)
        if hasattr(self, 'min_length_spin'):
            self.min_length_spin.setValue(0)
        if hasattr(self, 'max_length_spin'):
            self.max_length_spin.setValue(0)
    
    def edit_brick(self, item):
        """Edit selected brick (populate form)"""
        brick_data = item.data(Qt.ItemDataRole.UserRole)
        if brick_data:
            self.brick_id_edit.setText(brick_data['brick_id'])
            self.name_edit.setText(brick_data['name'])
            self.description_edit.setPlainText(brick_data['description'])
            self.tags_edit.setText(', '.join(brick_data['tags']))
            
            # Set brick type
            self.brick_type_combo.setCurrentText(brick_data['object_type'])
            self.on_brick_type_changed()  # Refresh dynamic fields
            
            # Populate dynamic fields based on brick type
            if brick_data['object_type'] == "NodeShape":
                if hasattr(self, 'target_class_edit') and 'targetClass' in brick_data['properties']:
                    self.target_class_edit.setText(brick_data['properties']['targetClass'])
                if hasattr(self, 'node_kind_combo') and 'nodeKind' in brick_data['properties']:
                    self.node_kind_combo.setCurrentText(brick_data['properties']['nodeKind'])
                    
            elif brick_data['object_type'] == "PropertyShape":
                if hasattr(self, 'path_edit') and 'path' in brick_data['properties']:
                    self.path_edit.setText(brick_data['properties']['path'])
                if hasattr(self, 'datatype_combo') and 'datatype' in brick_data['properties']:
                    self.datatype_combo.setCurrentText(brick_data['properties']['datatype'])
                
                # Populate constraints
                for constraint in brick_data['constraints']:
                    if constraint['constraint_type'] == "MinCountConstraintComponent":
                        if hasattr(self, 'min_count_spin'):
                            self.min_count_spin.setValue(int(constraint['value']))
                    elif constraint['constraint_type'] == "MaxCountConstraintComponent":
                        if hasattr(self, 'max_count_spin'):
                            self.max_count_spin.setValue(int(constraint['value']))
                    elif constraint['constraint_type'] == "MinLengthConstraintComponent":
                        if hasattr(self, 'min_length_spin'):
                            self.min_length_spin.setValue(int(constraint['value']))
                    elif constraint['constraint_type'] == "MaxLengthConstraintComponent":
                        if hasattr(self, 'max_length_spin'):
                            self.max_length_spin.setValue(int(constraint['value']))
                    elif constraint['constraint_type'] == "PatternConstraintComponent":
                        if hasattr(self, 'pattern_edit'):
                            self.pattern_edit.setText(constraint['value'])
    
    def delete_brick(self):
        """Delete selected brick"""
        current_item = self.brick_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Selection Error", "Please select a brick to delete")
            return
        
        brick_data = current_item.data(Qt.ItemDataRole.UserRole)
        if not brick_data:
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   f"Are you sure you want to delete brick '{brick_data['name']}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            result = self.processor.process_event({
                "event": "delete_brick",
                "brick_id": brick_data['brick_id']
            })
            
            if result["status"] == "success":
                QMessageBox.information(self, "Success", "Brick deleted successfully")
                self.load_bricks()
                self.load_statistics()
                self.brick_details.clear()
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete brick: {result['message']}")
    
    def export_brick_shacl(self):
        """Export selected brick to SHACL"""
        current_item = self.brick_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Selection Error", "Please select a brick to export")
            return
        
        brick_data = current_item.data(Qt.ItemDataRole.UserRole)
        if not brick_data:
            return
        
        result = self.processor.process_event({
            "event": "export_brick_shacl",
            "brick_id": brick_data['brick_id'],
            "format_type": "turtle"
        })
        
        if result["status"] == "success":
            self.shacl_output.setPlainText(result["data"]["content"])
            
            # Also offer to save to file
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export SHACL",
                f"{brick_data['brick_id']}.ttl",
                "Turtle Files (*.ttl);;All Files (*)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w') as f:
                        f.write(result["data"]["content"])
                    QMessageBox.information(self, "Success", f"SHACL exported to {file_path}")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to save file: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", f"Failed to export SHACL: {result['message']}")
    
    def create_library(self):
        """Create a new library"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Create New Library")
        layout = QVBoxLayout(dialog)
        
        # Name
        layout.addWidget(QLabel("Library Name:"))
        name_edit = QLineEdit()
        layout.addWidget(name_edit)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        desc_edit = QTextEdit()
        desc_edit.setMaximumHeight(100)
        layout.addWidget(desc_edit)
        
        # Author
        layout.addWidget(QLabel("Author:"))
        author_edit = QLineEdit()
        author_edit.setText("User")
        layout.addWidget(author_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("Create")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = name_edit.text().strip()
            description = desc_edit.toPlainText().strip()
            author = author_edit.text().strip()
            
            if not name or not description:
                QMessageBox.warning(self, "Input Error", "Please fill in all fields")
                return
            
            result = self.processor.process_event({
                "event": "create_library",
                "name": name,
                "description": description,
                "author": author
            })
            
            if result["status"] == "success":
                QMessageBox.information(self, "Success", f"Library '{name}' created successfully!")
                self.load_library_info()
            else:
                QMessageBox.warning(self, "Error", f"Failed to create library: {result['message']}")
    
    def export_library(self):
        """Export current library"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Library",
            "library_export.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            result = self.processor.process_event({
                "event": "export_library",
                "file_path": file_path
            })
            
            if result["status"] == "success":
                QMessageBox.information(self, "Success", f"Library exported to {file_path}")
            else:
                QMessageBox.warning(self, "Error", f"Failed to export library: {result['message']}")
    
    def import_library(self):
        """Import a library"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Library",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            # Ask if create new library or import to current
            reply = QMessageBox.question(self, "Import Options",
                                       "Create new library or import to current?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                                       QMessageBox.StandardButton.Cancel)
            
            if reply == QMessageBox.StandardButton.Cancel:
                return
            
            create_new = reply == QMessageBox.StandardButton.Yes
            
            if create_new:
                # Get library name
                name, ok = QInputDialog.getText(self, "Library Name", "Enter library name:")
                if not ok or not name.strip():
                    return
                
                result = self.processor.process_event({
                    "event": "import_library",
                    "file_path": file_path,
                    "library_name": name.strip()
                })
            else:
                result = self.processor.process_event({
                    "event": "import_library",
                    "file_path": file_path
                })
            
            if result["status"] == "success":
                QMessageBox.information(self, "Success", f"Library imported successfully!")
                self.load_library_info()
                self.load_bricks()
                self.load_statistics()
            else:
                QMessageBox.warning(self, "Error", f"Failed to import library: {result['message']}")

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    gui = BrickGUI()
    gui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
