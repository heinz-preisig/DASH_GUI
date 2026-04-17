#!/usr/bin/env python3
"""
Combined SHACL Brick Generator GUI with mode switching
Allows users to switch between technical and user-friendly interfaces
"""

import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from ..core.brick_backend import BrickBackendAPI, BrickEventProcessor

class CombinedBrickGUI(QMainWindow):
    """Combined GUI with mode switching between technical and user-friendly"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SHACL Brick Generator - Combined Interface")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize backend
        self.backend = BrickBackendAPI("default_brick_repository")
        self.processor = BrickEventProcessor(self.backend)
        
        # UI setup
        self.init_ui()
        self._ensure_active_library()
        self.load_bricks()
    
    def init_ui(self):
        """Initialize combined interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Mode selector at top
        mode_selector = self.create_mode_selector()
        layout.addWidget(mode_selector)
        
        # Main content area with stacked widgets
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Create both interfaces
        self.user_friendly_widget = self.create_user_friendly_interface()
        self.technical_widget = self.create_technical_interface()
        
        # Add to stacked widget
        self.stacked_widget.addWidget(self.user_friendly_widget)
        self.stacked_widget.addWidget(self.technical_widget)
        
        # Start with user-friendly mode
        self.stacked_widget.setCurrentIndex(0)
        
        # Status bar
        self.statusBar().showMessage("User-Friendly Mode - Ready to create bricks!")
    
    def create_mode_selector(self):
        """Create mode selection widget"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Mode label
        label = QLabel("Interface Mode:")
        label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(label)
        
        # Mode buttons
        self.mode_button_group = QButtonGroup()
        
        self.user_friendly_btn = QRadioButton("User-Friendly")
        self.user_friendly_btn.setChecked(True)
        self.user_friendly_btn.toggled.connect(self.on_mode_changed)
        self.mode_button_group.addButton(self.user_friendly_btn)
        layout.addWidget(self.user_friendly_btn)
        
        self.technical_btn = QRadioButton("Technical")
        self.technical_btn.toggled.connect(self.on_mode_changed)
        self.mode_button_group.addButton(self.technical_btn)
        layout.addWidget(self.technical_btn)
        
        # Description
        self.mode_desc = QLabel("Simple interface for non-SHACL experts")
        self.mode_desc.setStyleSheet("color: #666; font-style: italic; margin-left: 20px;")
        layout.addWidget(self.mode_desc)
        
        layout.addStretch()
        
        # Help button
        help_btn = QPushButton("?")
        help_btn.setMaximumSize(30, 30)
        help_btn.clicked.connect(self.show_help)
        layout.addWidget(help_btn)
        
        return widget
    
    def create_user_friendly_interface(self):
        """Create user-friendly interface (simplified version)"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Left panel - Brick creation
        left_panel = self.create_uf_creation_panel()
        layout.addWidget(left_panel, 1)
        
        # Right panel - Brick library
        right_panel = self.create_uf_library_panel()
        layout.addWidget(right_panel, 1)
        
        return widget
    
    def create_technical_interface(self):
        """Create technical interface (import from original)"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Left panel - Library management
        left_panel = self.create_tech_library_panel()
        layout.addWidget(left_panel, 1)
        
        # Center panel - Brick list and details
        center_panel = self.create_tech_brick_panel()
        layout.addWidget(center_panel, 2)
        
        # Right panel - Brick creation and SHACL output
        right_panel = self.create_tech_creation_panel()
        layout.addWidget(right_panel, 1)
        
        return widget
    
    def on_mode_changed(self):
        """Handle mode change"""
        if self.user_friendly_btn.isChecked():
            self.stacked_widget.setCurrentIndex(0)
            self.mode_desc.setText("Simple interface for non-SHACL experts")
            self.statusBar().showMessage("User-Friendly Mode - Ready to create bricks!")
        else:
            self.stacked_widget.setCurrentIndex(1)
            self.mode_desc.setText("Full SHACL interface for experts")
            self.statusBar().showMessage("Technical Mode - Full SHACL access")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
        <h3>SHACL Brick Generator - Help</h3>
        
        <h4>User-Friendly Mode:</h4>
        <ul>
        <li><b>Entity/Class Shape:</b> Define types of things (Person, Product, etc.)</li>
        <li><b>Property/Field Shape:</b> Define properties (name, email, age, etc.)</li>
        <li><b>Data Types:</b> Text, Number, Email, URL, Date, True/False, Choice</li>
        <li><b>Validation Rules:</b> Required, Min/Max length, Pattern, Min/Max value</li>
        <li><b>Perfect for:</b> Users who don't know SHACL terminology</li>
        </ul>
        
        <h4>Technical Mode:</h4>
        <ul>
        <li><b>NodeShape:</b> Technical SHACL NodeShape creation</li>
        <li><b>PropertyShape:</b> Technical SHACL PropertyShape creation</li>
        <li><b>Full SHACL Access:</b> All constraint types and properties</li>
        <li><b>SHACL Export:</b> Direct Turtle format export</li>
        <li><b>Perfect for:</b> SHACL experts who want full control</li>
        </ul>
        
        <h4>Common Workflow:</h4>
        <ol>
        <li>Start in User-Friendly mode to create basic bricks</li>
        <li>Switch to Technical mode for advanced SHACL features</li>
        <li>Export bricks to SHACL format for use in other systems</li>
        </ol>
        """
        
        msg = QMessageBox()
        msg.setWindowTitle("Help")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(help_text)
        msg.exec()
    
    # User-Friendly Interface Methods (simplified versions)
    def create_uf_creation_panel(self):
        """Create user-friendly creation panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("Create New Brick")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3; padding: 5px;")
        layout.addWidget(header)
        
        # Quick creation form
        form_group = QGroupBox("Quick Creation")
        form_layout = QFormLayout()
        
        self.uf_name_edit = QLineEdit()
        self.uf_name_edit.setPlaceholderText("e.g., Person Information")
        form_layout.addRow("Name:", self.uf_name_edit)
        
        self.uf_desc_edit = QTextEdit()
        self.uf_desc_edit.setPlaceholderText("Describe what this brick represents...")
        self.uf_desc_edit.setMaximumHeight(60)
        form_layout.addRow("Description:", self.uf_desc_edit)
        
        self.uf_type_combo = QComboBox()
        self.uf_type_combo.addItems(["Entity/Class", "Property/Field"])
        form_layout.addRow("Type:", self.uf_type_combo)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Create button
        create_btn = QPushButton("Create Brick")
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 6px;
            }
        """)
        create_btn.clicked.connect(self.uf_create_brick)
        layout.addWidget(create_btn)
        
        layout.addStretch()
        return panel
    
    def create_uf_library_panel(self):
        """Create user-friendly library panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("My Bricks")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3; padding: 5px;")
        layout.addWidget(header)
        
        # Search
        self.uf_search_edit = QLineEdit()
        self.uf_search_edit.setPlaceholderText("Search bricks...")
        self.uf_search_edit.textChanged.connect(self.uf_search_bricks)
        layout.addWidget(self.uf_search_edit)
        
        # Brick list
        self.uf_brick_list = QListWidget()
        self.uf_brick_list.itemClicked.connect(self.uf_on_brick_selected)
        layout.addWidget(self.uf_brick_list)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        self.uf_edit_btn = QPushButton("Edit")
        self.uf_edit_btn.clicked.connect(self.uf_edit_brick)
        actions_layout.addWidget(self.uf_edit_btn)
        
        self.uf_delete_btn = QPushButton("Delete")
        self.uf_delete_btn.clicked.connect(self.uf_delete_brick)
        actions_layout.addWidget(self.uf_delete_btn)
        
        layout.addLayout(actions_layout)
        
        return panel
    
    # Technical Interface Methods (imported from original)
    def create_tech_library_panel(self):
        """Create technical library management panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("Library Management")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(header)
        
        # Library info
        self.tech_lib_info = QTextEdit()
        self.tech_lib_info.setReadOnly(True)
        self.tech_lib_info.setMaximumHeight(100)
        layout.addWidget(QLabel("Library Info:"))
        layout.addWidget(self.tech_lib_info)
        
        # Statistics
        self.tech_stats_text = QTextEdit()
        self.tech_stats_text.setReadOnly(True)
        self.tech_stats_text.setMaximumHeight(150)
        layout.addWidget(QLabel("Statistics:"))
        layout.addWidget(self.tech_stats_text)
        
        layout.addStretch()
        return panel
    
    def create_tech_brick_panel(self):
        """Create technical brick panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("Brick Library")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(header)
        
        # Search and filter
        search_layout = QHBoxLayout()
        self.tech_search_edit = QLineEdit()
        self.tech_search_edit.setPlaceholderText("Search bricks...")
        self.tech_search_edit.textChanged.connect(self.tech_search_bricks)
        search_layout.addWidget(self.tech_search_edit)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_bricks)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)
        
        # Brick list
        self.tech_brick_list = QListWidget()
        self.tech_brick_list.itemClicked.connect(self.tech_on_brick_selected)
        self.tech_brick_list.itemDoubleClicked.connect(self.tech_edit_brick)
        layout.addWidget(self.tech_brick_list)
        
        # Brick details
        layout.addWidget(QLabel("Brick Details:"))
        self.tech_brick_details = QTextEdit()
        self.tech_brick_details.setReadOnly(True)
        self.tech_brick_details.setMaximumHeight(150)
        layout.addWidget(self.tech_brick_details)
        
        return panel
    
    def create_tech_creation_panel(self):
        """Create technical creation panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("Create Brick")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(header)
        
        # Brick type
        self.tech_brick_type_combo = QComboBox()
        self.tech_brick_type_combo.addItems(["NodeShape", "PropertyShape"])
        self.tech_brick_type_combo.currentTextChanged.connect(self.tech_on_brick_type_changed)
        layout.addWidget(QLabel("Brick Type:"))
        layout.addWidget(self.tech_brick_type_combo)
        
        # Basic fields
        self.tech_brick_id_edit = QLineEdit()
        self.tech_brick_id_edit.setPlaceholderText("Brick ID (e.g., my_brick)")
        layout.addWidget(QLabel("Brick ID:"))
        layout.addWidget(self.tech_brick_id_edit)
        
        self.tech_name_edit = QLineEdit()
        self.tech_name_edit.setPlaceholderText("Brick Name")
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.tech_name_edit)
        
        self.tech_description_edit = QTextEdit()
        self.tech_description_edit.setPlaceholderText("Description")
        self.tech_description_edit.setMaximumHeight(80)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.tech_description_edit)
        
        # Dynamic fields
        self.tech_dynamic_fields = QWidget()
        self.tech_dynamic_layout = QVBoxLayout(self.tech_dynamic_fields)
        layout.addWidget(self.tech_dynamic_fields)
        
        # Create button
        create_btn = QPushButton("Create Brick")
        create_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        create_btn.clicked.connect(self.tech_create_brick)
        layout.addWidget(create_btn)
        
        # SHACL Output
        layout.addWidget(QLabel("SHACL Output:"))
        self.tech_shacl_output = QTextEdit()
        self.tech_shacl_output.setReadOnly(True)
        self.tech_shacl_output.setFont(QFont("Courier", 10))
        layout.addWidget(self.tech_shacl_output)
        
        layout.addStretch()
        return panel
    
    # Shared methods
    def _ensure_active_library(self):
        """Ensure we have an active library"""
        result = self.processor.process_event({"event": "get_repository_info"})
        if not result["data"]["active_library"]:
            self.processor.process_event({"event": "set_active_library", "library_name": "default"})
    
    def load_bricks(self):
        """Load bricks for both interfaces"""
        # Load for user-friendly interface
        result = self.processor.process_event({"event": "get_library_bricks"})
        if result["status"] == "success":
            self.uf_brick_list.clear()
            self.tech_brick_list.clear()
            
            for brick in result["data"]["bricks"]:
                # User-friendly display
                display_name = self.get_user_friendly_name(brick)
                uf_item = QListWidgetItem(display_name)
                uf_item.setData(Qt.ItemDataRole.UserRole, brick)
                self.uf_brick_list.addItem(uf_item)
                
                # Technical display
                tech_item = QListWidgetItem(f"{brick['name']} ({brick['object_type']})")
                tech_item.setData(Qt.ItemDataRole.UserRole, brick)
                self.tech_brick_list.addItem(tech_item)
        
        # Update library info
        self.update_library_info()
    
    def get_user_friendly_name(self, brick):
        """Convert brick to user-friendly display name"""
        name = brick['name']
        obj_type = brick['object_type']
        
        if obj_type == "NodeShape":
            return f"Entity: {name}"
        elif obj_type == "PropertyShape":
            return f"Property: {name}"
        else:
            return f"{name}"
    
    def update_library_info(self):
        """Update library information displays"""
        result = self.processor.process_event({"event": "get_repository_info"})
        if result["status"] == "success":
            info_text = f"Active Library: {result['data']['active_library']}\n"
            info_text += f"Total Libraries: {len(result['data']['libraries'])}\n"
            for lib in result['data']['libraries']:
                info_text += f"- {lib['name']}: {lib['brick_count']} bricks\n"
            
            if hasattr(self, 'tech_lib_info'):
                self.tech_lib_info.setPlainText(info_text)
        
        # Update statistics
        result = self.processor.process_event({"event": "get_library_statistics"})
        if result["status"] == "success":
            stats = result["data"]
            stats_text = f"Total Bricks: {stats['total_bricks']}\n\n"
            stats_text += "Object Types:\n"
            for obj_type, count in stats['object_types'].items():
                stats_text += f"  {obj_type}: {count}\n"
            
            if hasattr(self, 'tech_stats_text'):
                self.tech_stats_text.setPlainText(stats_text)
    
    # User-Friendly Interface Methods
    def uf_create_brick(self):
        """Create brick in user-friendly mode"""
        name = self.uf_name_edit.text().strip()
        description = self.uf_desc_edit.toPlainText().strip()
        brick_type = self.uf_type_combo.currentText()
        
        if not name or not description:
            QMessageBox.warning(self, "Missing Information", "Please enter name and description.")
            return
        
        try:
            if brick_type == "Entity/Class":
                # Create NodeShape
                brick_id = name.lower().replace(" ", "_")
                result = self.processor.process_event({
                    "event": "create_nodeshape_brick",
                    "brick_id": brick_id,
                    "name": name,
                    "description": description,
                    "tags": ["entity", "user-friendly"]
                })
            else:
                # Create PropertyShape
                brick_id = name.lower().replace(" ", "_")
                result = self.processor.process_event({
                    "event": "create_propertyshape_brick",
                    "brick_id": brick_id,
                    "name": name,
                    "description": description,
                    "path": "property",  # Default path
                    "tags": ["property", "user-friendly"]
                })
            
            if result["status"] == "success":
                self.load_bricks()
                self.uf_name_edit.clear()
                self.uf_desc_edit.clear()
                self.statusBar().showMessage(f"Created brick: {name}")
            else:
                QMessageBox.warning(self, "Error", f"Failed to create brick: {result['message']}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating brick: {str(e)}")
    
    def uf_search_bricks(self):
        """Search bricks in user-friendly mode"""
        query = self.uf_search_edit.text().strip()
        if not query:
            self.load_bricks()
            return
        
        result = self.processor.process_event({"event": "search_bricks", "query": query})
        if result["status"] == "success":
            self.uf_brick_list.clear()
            for brick in result["data"]["bricks"]:
                display_name = self.get_user_friendly_name(brick)
                item = QListWidgetItem(display_name)
                item.setData(Qt.ItemDataRole.UserRole, brick)
                self.uf_brick_list.addItem(item)
    
    def uf_on_brick_selected(self, item):
        """Handle brick selection in user-friendly mode"""
        brick_data = item.data(Qt.ItemDataRole.UserRole)
        if brick_data:
            # Update technical details display
            details = f"Name: {brick_data['name']}\n"
            details += f"Type: {brick_data['object_type']}\n"
            details += f"Description: {brick_data['description']}\n"
            
            if hasattr(self, 'tech_brick_details'):
                self.tech_brick_details.setPlainText(details)
    
    def uf_edit_brick(self):
        """Edit brick - switch to technical mode for full editing"""
        current_item = self.uf_brick_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a brick to edit.")
            return
        
        # Switch to technical mode
        self.technical_btn.setChecked(True)
        
        # Find and select the same brick in technical list
        brick_data = current_item.data(Qt.ItemDataRole.UserRole)
        for i in range(self.tech_brick_list.count()):
            item = self.tech_brick_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole)['brick_id'] == brick_data['brick_id']:
                self.tech_brick_list.setCurrentItem(item)
                self.tech_on_brick_selected(item)
                break
        
        self.statusBar().showMessage("Switched to Technical Mode for editing")
    
    def uf_delete_brick(self):
        """Delete brick in user-friendly mode"""
        current_item = self.uf_brick_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a brick to delete.")
            return
        
        brick_data = current_item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                               f"Are you sure you want to delete '{brick_data['name']}'?",
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            result = self.processor.process_event({
                "event": "delete_brick",
                "brick_id": brick_data['brick_id']
            })
            
            if result["status"] == "success":
                self.load_bricks()
                self.statusBar().showMessage(f"Deleted brick: {brick_data['name']}")
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete brick: {result['message']}")
    
    # Technical Interface Methods (simplified versions)
    def tech_search_bricks(self):
        """Search bricks in technical mode"""
        query = self.tech_search_edit.text().strip()
        if not query:
            self.load_bricks()
            return
        
        result = self.processor.process_event({"event": "search_bricks", "query": query})
        if result["status"] == "success":
            self.tech_brick_list.clear()
            for brick in result["data"]["bricks"]:
                item = QListWidgetItem(f"{brick['name']} ({brick['object_type']})")
                item.setData(Qt.ItemDataRole.UserRole, brick)
                self.tech_brick_list.addItem(item)
    
    def tech_on_brick_selected(self, item):
        """Handle brick selection in technical mode"""
        brick_data = item.data(Qt.ItemDataRole.UserRole)
        if brick_data:
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
            
            self.tech_brick_details.setPlainText(details_text)
    
    def tech_on_brick_type_changed(self):
        """Handle brick type change in technical mode"""
        # Clear existing dynamic fields
        while self.tech_dynamic_layout.count():
            child = self.tech_dynamic_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add appropriate fields based on type
        brick_type = self.tech_brick_type_combo.currentText()
        
        if brick_type == "NodeShape":
            # Target class
            target_class_edit = QLineEdit()
            target_class_edit.setPlaceholderText("Target Class (e.g., foaf:Person)")
            self.tech_dynamic_layout.addWidget(QLabel("Target Class:"))
            self.tech_dynamic_layout.addWidget(target_class_edit)
            self.tech_target_class_edit = target_class_edit
            
        elif brick_type == "PropertyShape":
            # Path
            path_edit = QLineEdit()
            path_edit.setPlaceholderText("Property Path (e.g., foaf:name)")
            self.tech_dynamic_layout.addWidget(QLabel("Property Path:"))
            self.tech_dynamic_layout.addWidget(path_edit)
            self.tech_path_edit = path_edit
            
            # Datatype
            datatype_combo = QComboBox()
            datatype_combo.addItems(["xsd:string", "xsd:integer", "xsd:decimal", "xsd:boolean", "xsd:date"])
            self.tech_dynamic_layout.addWidget(QLabel("Datatype:"))
            self.tech_dynamic_layout.addWidget(datatype_combo)
            self.tech_datatype_combo = datatype_combo
    
    def tech_create_brick(self):
        """Create brick in technical mode"""
        brick_id = self.tech_brick_id_edit.text().strip()
        name = self.tech_name_edit.text().strip()
        description = self.tech_description_edit.toPlainText().strip()
        brick_type = self.tech_brick_type_combo.currentText()
        
        if not brick_id or not name or not description:
            QMessageBox.warning(self, "Missing Information", "Please fill in all required fields.")
            return
        
        try:
            if brick_type == "NodeShape":
                target_class = getattr(self, 'tech_target_class_edit', None)
                target_class_value = target_class.text().strip() if target_class else None
                
                result = self.processor.process_event({
                    "event": "create_nodeshape_brick",
                    "brick_id": brick_id,
                    "name": name,
                    "description": description,
                    "target_class": target_class_value,
                    "tags": ["technical"]
                })
                
            elif brick_type == "PropertyShape":
                path = getattr(self, 'tech_path_edit', None)
                path_value = path.text().strip() if path else None
                
                if not path_value:
                    QMessageBox.warning(self, "Missing Information", "Property Path is required for PropertyShape")
                    return
                
                datatype = getattr(self, 'tech_datatype_combo', None)
                datatype_value = datatype.currentText() if datatype else "xsd:string"
                
                properties = {"path": path_value, "datatype": datatype_value}
                
                result = self.processor.process_event({
                    "event": "create_propertyshape_brick",
                    "brick_id": brick_id,
                    "name": name,
                    "description": description,
                    "path": path_value,
                    "properties": properties,
                    "tags": ["technical"]
                })
            
            if result["status"] == "success":
                self.load_bricks()
                self.tech_brick_id_edit.clear()
                self.tech_name_edit.clear()
                self.tech_description_edit.clear()
                self.statusBar().showMessage(f"Created brick: {name}")
                
                # Export and show SHACL
                export_result = self.processor.process_event({
                    "event": "export_brick_shacl",
                    "brick_id": brick_id,
                    "format_type": "turtle"
                })
                
                if export_result["status"] == "success":
                    self.tech_shacl_output.setPlainText(export_result["data"]["content"])
                
            else:
                QMessageBox.warning(self, "Error", f"Failed to create brick: {result['message']}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating brick: {str(e)}")
    
    def tech_edit_brick(self):
        """Edit brick in technical mode"""
        current_item = self.tech_brick_list.currentItem()
        if not current_item:
            return
        
        brick_data = current_item.data(Qt.ItemDataRole.UserRole)
        if brick_data:
            # Populate form for editing
            self.tech_brick_id_edit.setText(brick_data['brick_id'])
            self.tech_name_edit.setText(brick_data['name'])
            self.tech_description_edit.setPlainText(brick_data['description'])
            
            # Set brick type
            if brick_data['object_type'] == "NodeShape":
                self.tech_brick_type_combo.setCurrentText("NodeShape")
            elif brick_data['object_type'] == "PropertyShape":
                self.tech_brick_type_combo.setCurrentText("PropertyShape")
            
            self.tech_on_brick_type_changed()
            
            # Populate specific fields
            if brick_data['object_type'] == "NodeShape":
                if hasattr(self, 'tech_target_class_edit') and 'targetClass' in brick_data['properties']:
                    self.tech_target_class_edit.setText(brick_data['properties']['targetClass'])
            elif brick_data['object_type'] == "PropertyShape":
                if hasattr(self, 'tech_path_edit') and 'path' in brick_data['properties']:
                    self.tech_path_edit.setText(brick_data['properties']['path'])
                
                if hasattr(self, 'tech_datatype_combo') and 'datatype' in brick_data['properties']:
                    self.tech_datatype_combo.setCurrentText(brick_data['properties']['datatype'])
            
            self.statusBar().showMessage(f"Editing brick: {brick_data['name']}")

def main():
    """Main entry point for combined GUI"""
    app = QApplication(sys.argv)
    gui = CombinedBrickGUI()
    gui.show()
    return app.exec()

if __name__ == "__main__":
    main()
