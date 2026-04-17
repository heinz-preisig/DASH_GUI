#!/usr/bin/env python3
"""
Step 2: Schema Constructor GUI
Interface for combining bricks into complex shapes with daisy-chaining
"""

import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from ..core.brick_backend import BrickBackendAPI, BrickEventProcessor
from ..core.schema_constructor import (
    SchemaConstructor, InterfaceFlowType, SchemaComposition, 
    DaisyChain, InterfaceStep
)

class SchemaConstructorGUI(QMainWindow):
    """Main GUI for schema construction"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Step 2: Schema Constructor - Brick Composition")
        self.setGeometry(50, 50, 1600, 1000)
        
        # Initialize backend
        self.brick_backend = BrickBackendAPI("schema_repositories")
        self.processor = BrickEventProcessor(self.brick_backend)
        self.schema_constructor = SchemaConstructor(self.brick_backend)
        
        # UI setup
        self.init_ui()
        self.load_initial_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Left panel - Brick library and templates
        left_panel = self.create_left_panel()
        layout.addWidget(left_panel, 1)
        
        # Center panel - Schema construction workspace
        center_panel = self.create_center_panel()
        layout.addWidget(center_panel, 2)
        
        # Right panel - Properties and preview
        right_panel = self.create_right_panel()
        layout.addWidget(right_panel, 1)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_schema_action = QAction('New Schema', self)
        new_schema_action.setShortcut('Ctrl+N')
        new_schema_action.triggered.connect(self.new_schema)
        file_menu.addAction(new_schema_action)
        
        save_schema_action = QAction('Save Schema', self)
        save_schema_action.setShortcut('Ctrl+S')
        save_schema_action.triggered.connect(self.save_schema)
        file_menu.addAction(save_schema_action)
        
        file_menu.addSeparator()
        
        export_shacl_action = QAction('Export SHACL', self)
        export_shacl_action.triggered.connect(self.export_shacl)
        file_menu.addAction(export_shacl_action)
        
        # Schema menu
        schema_menu = menubar.addMenu('Schema')
        
        create_daisy_chain_action = QAction('Create Daisy Chain', self)
        create_daisy_chain_action.triggered.connect(self.create_daisy_chain)
        schema_menu.addAction(create_daisy_chain_action)
        
        extend_schema_action = QAction('Extend Schema', self)
        extend_schema_action.triggered.connect(self.extend_schema)
        schema_menu.addAction(extend_schema_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        preview_interface_action = QAction('Preview Interface', self)
        preview_interface_action.triggered.connect(self.preview_interface)
        tools_menu.addAction(preview_interface_action)
        
        generate_config_action = QAction('Generate Interface Config', self)
        generate_config_action.triggered.connect(self.generate_interface_config)
        tools_menu.addAction(generate_config_action)
    
    def create_toolbar(self):
        """Create toolbar"""
        toolbar = self.addToolBar('Main')
        
        # New schema
        new_schema_action = QAction('New Schema', self)
        new_schema_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        new_schema_action.triggered.connect(self.new_schema)
        toolbar.addAction(new_schema_action)
        
        # Save schema
        save_schema_action = QAction('Save Schema', self)
        save_schema_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        save_schema_action.triggered.connect(self.save_schema)
        toolbar.addAction(save_schema_action)
        
        toolbar.addSeparator()
        
        # Create daisy chain
        daisy_chain_action = QAction('Daisy Chain', self)
        daisy_chain_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_LinkIcon))
        daisy_chain_action.triggered.connect(self.create_daisy_chain)
        toolbar.addAction(daisy_chain_action)
        
        # Preview
        preview_action = QAction('Preview', self)
        preview_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
        preview_action.triggered.connect(self.preview_interface)
        toolbar.addAction(preview_action)
    
    def create_left_panel(self):
        """Create left panel with brick library and templates"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Brick library section
        brick_label = QLabel("Brick Library")
        brick_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(brick_label)
        
        # Search bricks
        self.brick_search = QLineEdit()
        self.brick_search.setPlaceholderText("Search bricks...")
        self.brick_search.textChanged.connect(self.search_bricks)
        layout.addWidget(self.brick_search)
        
        # Brick list
        self.brick_list = QListWidget()
        self.brick_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.brick_list.itemDoubleClicked.connect(self.add_brick_to_schema)
        layout.addWidget(self.brick_list)
        
        # Templates section
        template_label = QLabel("Schema Templates")
        template_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(template_label)
        
        self.template_list = QListWidget()
        self.template_list.itemDoubleClicked.connect(self.create_from_template)
        layout.addWidget(self.template_list)
        
        return panel
    
    def create_center_panel(self):
        """Create center panel with schema construction workspace"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Tab widget for different views
        self.workspace_tabs = QTabWidget()
        
        # Schema builder tab
        schema_builder = self.create_schema_builder()
        self.workspace_tabs.addTab(schema_builder, "Schema Builder")
        
        # Interface flow tab
        interface_flow = self.create_interface_flow()
        self.workspace_tabs.addTab(interface_flow, "Interface Flow")
        
        # Daisy chain tab
        daisy_chain = self.create_daisy_chain_builder()
        self.workspace_tabs.addTab(daisy_chain, "Daisy Chain")
        
        # Preview tab
        preview = self.create_preview_panel()
        self.workspace_tabs.addTab(preview, "Preview")
        
        layout.addWidget(self.workspace_tabs)
        
        return panel
    
    def create_right_panel(self):
        """Create right panel with properties and details"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Schema properties
        schema_props_label = QLabel("Schema Properties")
        schema_props_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(schema_props_label)
        
        # Schema details form
        form_layout = QFormLayout()
        
        self.schema_name_edit = QLineEdit()
        form_layout.addRow("Name:", self.schema_name_edit)
        
        self.schema_desc_edit = QTextEdit()
        self.schema_desc_edit.setMaximumHeight(80)
        form_layout.addRow("Description:", self.schema_desc_edit)
        
        self.interface_flow_combo = QComboBox()
        self.interface_flow_combo.addItems([flow.value for flow in InterfaceFlowType])
        form_layout.addRow("Interface Flow:", self.interface_flow_combo)
        
        layout.addLayout(form_layout)
        
        # Component bricks
        components_label = QLabel("Component Bricks")
        components_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(components_label)
        
        self.component_bricks_list = QListWidget()
        self.component_bricks_list.itemDoubleClicked.connect(self.remove_component_brick)
        layout.addWidget(self.component_bricks_list)
        
        # Component controls
        component_controls = QHBoxLayout()
        
        add_btn = QPushButton("Add Selected")
        add_btn.clicked.connect(self.add_selected_bricks)
        component_controls.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_selected_component)
        component_controls.addWidget(remove_btn)
        
        layout.addLayout(component_controls)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        create_btn = QPushButton("Create Schema")
        create_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        create_btn.clicked.connect(self.create_schema)
        actions_layout.addWidget(create_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet("background-color: #9E9E9E; color: white; padding: 8px;")
        clear_btn.clicked.connect(self.clear_schema_form)
        actions_layout.addWidget(clear_btn)
        
        layout.addLayout(actions_layout)
        
        layout.addStretch()
        
        return panel
    
    def create_schema_builder(self):
        """Create schema builder workspace"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Visual schema area
        visual_label = QLabel("Visual Schema Builder")
        visual_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(visual_label)
        
        self.schema_scene = QGraphicsScene()
        self.schema_view = QGraphicsView(self.schema_scene)
        self.schema_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        layout.addWidget(self.schema_view)
        
        # Schema builder toolbar
        toolbar = QToolBar()
        
        add_root_btn = QPushButton("Set Root Brick")
        add_root_btn.clicked.connect(self.set_root_brick)
        toolbar.addWidget(add_root_btn)
        
        add_component_btn = QPushButton("Add Component")
        add_component_btn.clicked.connect(self.add_component_brick)
        toolbar.addWidget(add_component_btn)
        
        auto_layout_btn = QPushButton("Auto Layout")
        auto_layout_btn.clicked.connect(self.auto_layout_schema)
        toolbar.addWidget(auto_layout_btn)
        
        layout.addWidget(toolbar)
        
        return widget
    
    def create_interface_flow(self):
        """Create interface flow designer"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Flow designer
        flow_label = QLabel("Interface Flow Designer")
        flow_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(flow_label)
        
        # Flow type selector
        flow_type_layout = QHBoxLayout()
        flow_type_layout.addWidget(QLabel("Flow Type:"))
        
        self.flow_type_combo = QComboBox()
        self.flow_type_combo.addItems([flow.value for flow in InterfaceFlowType])
        self.flow_type_combo.currentTextChanged.connect(self.on_flow_type_changed)
        flow_type_layout.addWidget(self.flow_type_combo)
        
        flow_type_layout.addStretch()
        layout.addLayout(flow_type_layout)
        
        # Steps editor
        steps_label = QLabel("Interface Steps")
        steps_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(steps_label)
        
        # Steps list with editor
        steps_widget = QWidget()
        steps_layout = QHBoxLayout(steps_widget)
        
        # Steps list
        self.steps_list = QListWidget()
        self.steps_list.itemClicked.connect(self.on_step_selected)
        steps_layout.addWidget(self.steps_list, 1)
        
        # Step editor
        step_editor = QWidget()
        step_editor_layout = QVBoxLayout(step_editor)
        
        step_editor_layout.addWidget(QLabel("Step Details:"))
        
        self.step_name_edit = QLineEdit()
        step_editor_layout.addWidget(QLabel("Step Name:"))
        step_editor_layout.addWidget(self.step_name_edit)
        
        self.step_desc_edit = QTextEdit()
        self.step_desc_edit.setMaximumHeight(60)
        step_editor_layout.addWidget(QLabel("Description:"))
        step_editor_layout.addWidget(self.step_desc_edit)
        
        step_editor_layout.addWidget(QLabel("Bricks in Step:"))
        self.step_bricks_list = QListWidget()
        step_editor_layout.addWidget(self.step_bricks_list)
        
        # Step controls
        step_controls = QHBoxLayout()
        
        add_step_btn = QPushButton("Add Step")
        add_step_btn.clicked.connect(self.add_interface_step)
        step_controls.addWidget(add_step_btn)
        
        update_step_btn = QPushButton("Update Step")
        update_step_btn.clicked.connect(self.update_interface_step)
        step_controls.addWidget(update_step_btn)
        
        remove_step_btn = QPushButton("Remove Step")
        remove_step_btn.clicked.connect(self.remove_interface_step)
        step_controls.addWidget(remove_step_btn)
        
        step_editor_layout.addLayout(step_controls)
        steps_layout.addWidget(step_editor, 1)
        
        layout.addWidget(steps_widget)
        
        return widget
    
    def create_daisy_chain_builder(self):
        """Create daisy chain builder"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Daisy chain builder
        chain_label = QLabel("Daisy Chain Builder")
        chain_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(chain_label)
        
        # Chain configuration
        chain_config = QWidget()
        chain_layout = QFormLayout(chain_config)
        
        self.chain_name_edit = QLineEdit()
        chain_layout.addRow("Chain Name:", self.chain_name_edit)
        
        self.chain_desc_edit = QTextEdit()
        self.chain_desc_edit.setMaximumHeight(60)
        chain_layout.addRow("Description:", self.chain_desc_edit)
        
        layout.addWidget(chain_config)
        
        # Schema sequence
        schema_seq_label = QLabel("Schema Sequence")
        schema_seq_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(schema_seq_label)
        
        # Available schemas and chain sequence
        schemas_widget = QWidget()
        schemas_layout = QHBoxLayout(schemas_widget)
        
        # Available schemas
        available_group = QGroupBox("Available Schemas")
        available_layout = QVBoxLayout(available_group)
        
        self.available_schemas_list = QListWidget()
        available_layout.addWidget(self.available_schemas_list)
        
        add_to_chain_btn = QPushButton("Add to Chain")
        add_to_chain_btn.clicked.connect(self.add_schema_to_chain)
        available_layout.addWidget(add_to_chain_btn)
        
        schemas_layout.addWidget(available_group)
        
        # Chain sequence
        chain_group = QGroupBox("Chain Sequence")
        chain_seq_layout = QVBoxLayout(chain_group)
        
        self.chain_sequence_list = QListWidget()
        self.chain_sequence_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        chain_seq_layout.addWidget(self.chain_sequence_list)
        
        chain_controls = QHBoxLayout()
        
        remove_from_chain_btn = QPushButton("Remove")
        remove_from_chain_btn.clicked.connect(self.remove_from_chain)
        chain_controls.addWidget(remove_from_chain_btn)
        
        move_up_btn = QPushButton("Move Up")
        move_up_btn.clicked.connect(self.move_chain_item_up)
        chain_controls.addWidget(move_up_btn)
        
        move_down_btn = QPushButton("Move Down")
        move_down_btn.clicked.connect(self.move_chain_item_down)
        chain_controls.addWidget(move_down_btn)
        
        chain_seq_layout.addLayout(chain_controls)
        schemas_layout.addWidget(chain_group)
        
        layout.addWidget(schemas_widget)
        
        # Create chain button
        create_chain_btn = QPushButton("Create Daisy Chain")
        create_chain_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        create_chain_btn.clicked.connect(self.create_daisy_chain_from_ui)
        layout.addWidget(create_chain_btn)
        
        return widget
    
    def create_preview_panel(self):
        """Create preview panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Preview options
        preview_options = QHBoxLayout()
        
        preview_options.addWidget(QLabel("Preview Type:"))
        
        self.preview_type_combo = QComboBox()
        self.preview_type_combo.addItems(["SHACL Output", "Interface Config", "JSON Export"])
        preview_options.addWidget(self.preview_type_combo)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_preview)
        preview_options.addWidget(refresh_btn)
        
        preview_options.addStretch()
        layout.addLayout(preview_options)
        
        # Preview content
        self.preview_text = QTextEdit()
        self.preview_text.setFont(QFont("Courier", 10))
        layout.addWidget(self.preview_text)
        
        return widget
    
    def load_initial_data(self):
        """Load initial data"""
        self.load_bricks()
        self.load_templates()
        self.load_schemas()
        
        self.statusBar().showMessage("Schema Constructor ready")
    
    def load_bricks(self):
        """Load available bricks"""
        result = self.processor.process_event({"event": "get_library_bricks"})
        if result["status"] == "success":
            self.brick_list.clear()
            for brick in result["data"]["bricks"]:
                item = QListWidgetItem(f"{brick['name']} ({brick['object_type']})")
                item.setData(Qt.ItemDataRole.UserRole, brick)
                self.brick_list.addItem(item)
    
    def load_templates(self):
        """Load schema templates"""
        templates = self.schema_constructor.templates
        self.template_list.clear()
        for template_name, template_data in templates.items():
            item = QListWidgetItem(f"{template_data['name']} - {template_data['description']}")
            item.setData(Qt.ItemDataRole.UserRole, template_name)
            self.template_list.addItem(item)
    
    def load_schemas(self):
        """Load existing schemas"""
        schemas = self.schema_constructor.get_all_schemas()
        self.available_schemas_list.clear()
        for schema in schemas:
            item = QListWidgetItem(f"{schema.name} ({len(schema.component_brick_ids)} components)")
            item.setData(Qt.ItemDataRole.UserRole, schema.schema_id)
            self.available_schemas_list.addItem(item)
    
    def search_bricks(self):
        """Search bricks"""
        query = self.brick_search.text().strip()
        if not query:
            self.load_bricks()
            return
        
        result = self.processor.process_event({"event": "search_bricks", "query": query})
        if result["status"] == "success":
            self.brick_list.clear()
            for brick in result["data"]["bricks"]:
                item = QListWidgetItem(f"{brick['name']} ({brick['object_type']})")
                item.setData(Qt.ItemDataRole.UserRole, brick)
                self.brick_list.addItem(item)
    
    def add_brick_to_schema(self, item):
        """Add brick to schema from double-click"""
        brick_data = item.data(Qt.ItemDataRole.UserRole)
        if brick_data:
            # Add to component bricks list
            list_item = QListWidgetItem(f"{brick_data['name']} ({brick_data['object_type']})")
            list_item.setData(Qt.ItemDataRole.UserRole, brick_data)
            self.component_bricks_list.addItem(list_item)
    
    def add_selected_bricks(self):
        """Add selected bricks to schema"""
        selected_items = self.brick_list.selectedItems()
        for item in selected_items:
            self.add_brick_to_schema(item)
    
    def remove_component_brick(self, item):
        """Remove component brick"""
        self.component_bricks_list.takeItem(self.component_bricks_list.row(item))
    
    def remove_selected_component(self):
        """Remove selected component bricks"""
        current_row = self.component_bricks_list.currentRow()
        if current_row >= 0:
            self.component_bricks_list.takeItem(current_row)
    
    def create_schema(self):
        """Create new schema"""
        name = self.schema_name_edit.text().strip()
        description = self.schema_desc_edit.toPlainText().strip()
        interface_flow = InterfaceFlowType(self.interface_flow_combo.currentText())
        
        if not name or not description:
            QMessageBox.warning(self, "Missing Information", "Please enter name and description")
            return
        
        # Get root brick (first component brick)
        root_brick_id = None
        component_brick_ids = []
        
        for i in range(self.component_bricks_list.count()):
            item = self.component_bricks_list.item(i)
            brick_data = item.data(Qt.ItemDataRole.UserRole)
            if brick_data:
                if i == 0 and brick_data["object_type"] == "NodeShape":
                    root_brick_id = brick_data["brick_id"]
                else:
                    component_brick_ids.append(brick_data["brick_id"])
        
        if not root_brick_id:
            QMessageBox.warning(self, "Missing Root", "Please add a NodeShape brick as the root")
            return
        
        try:
            schema = self.schema_constructor.create_schema(
                name=name,
                description=description,
                root_brick_id=root_brick_id,
                component_brick_ids=component_brick_ids,
                interface_flow=interface_flow
            )
            
            self.load_schemas()
            self.clear_schema_form()
            self.statusBar().showMessage(f"Created schema: {schema.name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create schema: {str(e)}")
    
    def clear_schema_form(self):
        """Clear schema form"""
        self.schema_name_edit.clear()
        self.schema_desc_edit.clear()
        self.component_bricks_list.clear()
    
    def create_from_template(self, item):
        """Create schema from template"""
        template_name = item.data(Qt.ItemDataRole.UserRole)
        if template_name:
            # Show template configuration dialog
            dialog = TemplateConfigDialog(template_name, self.schema_constructor, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_schemas()
                self.statusBar().showMessage(f"Created schema from template: {template_name}")
    
    def create_daisy_chain(self):
        """Create daisy chain dialog"""
        dialog = DaisyChainDialog(self.schema_constructor, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.statusBar().showMessage("Daisy chain created")
    
    def extend_schema(self):
        """Extend existing schema"""
        # Show schema selection dialog
        dialog = SchemaExtensionDialog(self.schema_constructor, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_schemas()
            self.statusBar().showMessage("Schema extended")
    
    def export_shacl(self):
        """Export schema as SHACL"""
        # Show schema selection dialog
        dialog = ExportDialog(self.schema_constructor, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.statusBar().showMessage("SHACL exported")
    
    def preview_interface(self):
        """Preview interface configuration"""
        # Switch to preview tab
        self.workspace_tabs.setCurrentIndex(3)
        self.refresh_preview()
    
    def generate_interface_config(self):
        """Generate interface configuration for HTML GUI"""
        # Show daisy chain selection dialog
        dialog = InterfaceConfigDialog(self.schema_constructor, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.statusBar().showMessage("Interface configuration generated")
    
    def new_schema(self):
        """Create new schema"""
        self.clear_schema_form()
        self.workspace_tabs.setCurrentIndex(0)
        self.schema_name_edit.setFocus()
    
    def save_schema(self):
        """Save current schema"""
        # Implementation depends on current editing context
        QMessageBox.information(self, "Save Schema", "Save functionality coming soon")
    
    # Interface flow methods
    def on_flow_type_changed(self, flow_type):
        """Handle flow type change"""
        # Update interface based on flow type
        pass
    
    def add_interface_step(self):
        """Add new interface step"""
        step_name = f"Step {self.steps_list.count() + 1}"
        step = InterfaceStep(
            step_id=f"step_{self.steps_list.count() + 1}",
            name=step_name,
            description=f"Interface step {self.steps_list.count() + 1}",
            brick_ids=[],
            next_steps=[]
        )
        
        item = QListWidgetItem(step_name)
        item.setData(Qt.ItemDataRole.UserRole, step)
        self.steps_list.addItem(item)
    
    def update_interface_step(self):
        """Update selected interface step"""
        current_item = self.steps_list.currentItem()
        if not current_item:
            return
        
        step = current_item.data(Qt.ItemDataRole.UserRole)
        if step:
            step.name = self.step_name_edit.text()
            step.description = self.step_desc_edit.toPlainText()
            
            current_item.setText(step.name)
            current_item.setData(Qt.ItemDataRole.UserRole, step)
    
    def remove_interface_step(self):
        """Remove selected interface step"""
        current_row = self.steps_list.currentRow()
        if current_row >= 0:
            self.steps_list.takeItem(current_row)
    
    def on_step_selected(self, item):
        """Handle step selection"""
        step = item.data(Qt.ItemDataRole.UserRole)
        if step:
            self.step_name_edit.setText(step.name)
            self.step_desc_edit.setPlainText(step.description)
            
            # Load step bricks
            self.step_bricks_list.clear()
            for brick_id in step.brick_ids:
                result = self.processor.process_event({"event": "get_brick_details", "brick_id": brick_id})
                if result["status"] == "success":
                    brick_data = result["data"]
                    list_item = QListWidgetItem(f"{brick_data['name']} ({brick_data['object_type']})")
                    list_item.setData(Qt.ItemDataRole.UserRole, brick_data)
                    self.step_bricks_list.addItem(list_item)
    
    # Daisy chain methods
    def add_schema_to_chain(self):
        """Add schema to chain sequence"""
        current_item = self.available_schemas_list.currentItem()
        if not current_item:
            return
        
        schema_id = current_item.data(Qt.ItemDataRole.UserRole)
        schema = self.schema_constructor.get_schema(schema_id)
        
        if schema:
            # Check if already in chain
            for i in range(self.chain_sequence_list.count()):
                item = self.chain_sequence_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == schema_id:
                    return  # Already in chain
            
            item = QListWidgetItem(f"{schema.name}")
            item.setData(Qt.ItemDataRole.UserRole, schema_id)
            self.chain_sequence_list.addItem(item)
    
    def remove_from_chain(self):
        """Remove schema from chain"""
        current_row = self.chain_sequence_list.currentRow()
        if current_row >= 0:
            self.chain_sequence_list.takeItem(current_row)
    
    def move_chain_item_up(self):
        """Move chain item up"""
        current_row = self.chain_sequence_list.currentRow()
        if current_row > 0:
            item = self.chain_sequence_list.takeItem(current_row)
            self.chain_sequence_list.insertItem(current_row - 1, item)
            self.chain_sequence_list.setCurrentRow(current_row - 1)
    
    def move_chain_item_down(self):
        """Move chain item down"""
        current_row = self.chain_sequence_list.currentRow()
        if current_row >= 0 and current_row < self.chain_sequence_list.count() - 1:
            item = self.chain_sequence_list.takeItem(current_row)
            self.chain_sequence_list.insertItem(current_row + 1, item)
            self.chain_sequence_list.setCurrentRow(current_row + 1)
    
    def create_daisy_chain_from_ui(self):
        """Create daisy chain from UI"""
        name = self.chain_name_edit.text().strip()
        description = self.chain_desc_edit.toPlainText().strip()
        
        if not name or not description:
            QMessageBox.warning(self, "Missing Information", "Please enter name and description")
            return
        
        # Get schema sequence
        schema_ids = []
        for i in range(self.chain_sequence_list.count()):
            item = self.chain_sequence_list.item(i)
            schema_ids.append(item.data(Qt.ItemDataRole.UserRole))
        
        if not schema_ids:
            QMessageBox.warning(self, "No Schemas", "Please add schemas to the chain")
            return
        
        try:
            daisy_chain = self.schema_constructor.create_daisy_chain(
                name=name,
                description=description,
                schema_ids=schema_ids
            )
            
            # Clear form
            self.chain_name_edit.clear()
            self.chain_desc_edit.clear()
            self.chain_sequence_list.clear()
            
            self.statusBar().showMessage(f"Created daisy chain: {daisy_chain.name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create daisy chain: {str(e)}")
    
    def refresh_preview(self):
        """Refresh preview content"""
        preview_type = self.preview_type_combo.currentText()
        
        if preview_type == "SHACL Output":
            # Show SHACL output of current schema
            self.preview_text.setPlainText("SHACL output preview...")
        elif preview_type == "Interface Config":
            # Show interface configuration
            self.preview_text.setPlainText("Interface configuration preview...")
        elif preview_type == "JSON Export":
            # Show JSON export
            self.preview_text.setPlainText("JSON export preview...")
    
    # Visual schema methods
    def set_root_brick(self):
        """Set root brick for visual schema"""
        QMessageBox.information(self, "Set Root Brick", "Root brick selection coming soon")
    
    def add_component_brick(self):
        """Add component brick to visual schema"""
        QMessageBox.information(self, "Add Component", "Component addition coming soon")
    
    def auto_layout_schema(self):
        """Auto-layout visual schema"""
        QMessageBox.information(self, "Auto Layout", "Auto-layout coming soon")

# Dialog classes
class TemplateConfigDialog(QDialog):
    """Dialog for configuring template-based schema creation"""
    
    def __init__(self, template_name, schema_constructor, parent=None):
        super().__init__(parent)
        self.template_name = template_name
        self.schema_constructor = schema_constructor
        self.setWindowTitle(f"Create Schema from Template: {template_name}")
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Template info
        template = self.schema_constructor.templates[self.template_name]
        info_label = QLabel(f"Template: {template['name']}\n{template['description']}")
        layout.addWidget(info_label)
        
        # Brick mapping
        layout.addWidget(QLabel("Brick Mapping:"))
        self.brick_mapping = {}
        
        for component in template["components"]:
            mapping_layout = QHBoxLayout()
            mapping_layout.addWidget(QLabel(f"{component}:"))
            
            combo = QComboBox()
            # Load available bricks
            # TODO: Load bricks from backend
            combo.addItem(f"Select brick for {component}")
            mapping_layout.addWidget(combo)
            
            self.brick_mapping[component] = combo
            layout.addLayout(mapping_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_brick_mappings(self):
        """Get brick mappings from UI"""
        mappings = {}
        for component, combo in self.brick_mapping.items():
            if combo.currentText() != f"Select brick for {component}":
                mappings[component] = combo.currentText()
        return mappings

class DaisyChainDialog(QDialog):
    """Dialog for creating daisy chains"""
    
    def __init__(self, schema_constructor, parent=None):
        super().__init__(parent)
        self.schema_constructor = schema_constructor
        self.setWindowTitle("Create Daisy Chain")
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Chain info
        layout.addWidget(QLabel("Chain Name:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        
        layout.addWidget(QLabel("Description:"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(80)
        layout.addWidget(self.desc_edit)
        
        # Schema selection
        layout.addWidget(QLabel("Select Schemas:"))
        self.schema_list = QListWidget()
        self.schema_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        
        # Load schemas
        schemas = self.schema_constructor.get_all_schemas()
        for schema in schemas:
            item = QListWidgetItem(schema.name)
            item.setData(Qt.ItemDataRole.UserRole, schema.schema_id)
            self.schema_list.addItem(item)
        
        layout.addWidget(self.schema_list)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

class SchemaExtensionDialog(QDialog):
    """Dialog for extending existing schemas"""
    
    def __init__(self, schema_constructor, parent=None):
        super().__init__(parent)
        self.schema_constructor = schema_constructor
        self.setWindowTitle("Extend Schema")
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Parent schema selection
        layout.addWidget(QLabel("Select Parent Schema:"))
        self.parent_combo = QComboBox()
        
        schemas = self.schema_constructor.get_all_schemas()
        for schema in schemas:
            self.parent_combo.addItem(schema.name, schema.schema_id)
        
        layout.addWidget(self.parent_combo)
        
        # New schema info
        layout.addWidget(QLabel("New Schema Name:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        
        layout.addWidget(QLabel("Description:"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(80)
        layout.addWidget(self.desc_edit)
        
        # Additional bricks
        layout.addWidget(QLabel("Additional Bricks:"))
        self.bricks_list = QListWidget()
        # TODO: Load available bricks
        layout.addWidget(self.bricks_list)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

class ExportDialog(QDialog):
    """Dialog for exporting schemas"""
    
    def __init__(self, schema_constructor, parent=None):
        super().__init__(parent)
        self.schema_constructor = schema_constructor
        self.setWindowTitle("Export Schema")
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Schema selection
        layout.addWidget(QLabel("Select Schema:"))
        self.schema_combo = QComboBox()
        
        schemas = self.schema_constructor.get_all_schemas()
        for schema in schemas:
            self.schema_combo.addItem(schema.name, schema.schema_id)
        
        layout.addWidget(self.schema_combo)
        
        # Export format
        layout.addWidget(QLabel("Export Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Turtle", "RDF/XML", "JSON-LD"])
        layout.addWidget(self.format_combo)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

class InterfaceConfigDialog(QDialog):
    """Dialog for generating interface configuration"""
    
    def __init__(self, schema_constructor, parent=None):
        super().__init__(parent)
        self.schema_constructor = schema_constructor
        self.setWindowTitle("Generate Interface Configuration")
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Daisy chain selection
        layout.addWidget(QLabel("Select Daisy Chain:"))
        self.chain_combo = QComboBox()
        
        chains = self.schema_constructor.get_all_daisy_chains()
        for chain in chains:
            self.chain_combo.addItem(chain.name, chain.chain_id)
        
        layout.addWidget(self.chain_combo)
        
        # Configuration options
        layout.addWidget(QLabel("Configuration Options:"))
        
        self.show_progress_check = QCheckBox("Show Progress Bar")
        self.show_progress_check.setChecked(True)
        layout.addWidget(self.show_progress_check)
        
        self.allow_skip_check = QCheckBox("Allow Step Skipping")
        layout.addWidget(self.allow_skip_check)
        
        self.auto_save_check = QCheckBox("Auto-save Progress")
        self.auto_save_check.setChecked(True)
        layout.addWidget(self.auto_save_check)
        
        # Theme selection
        layout.addWidget(QLabel("UI Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["default", "bootstrap", "material", "custom"])
        layout.addWidget(self.theme_combo)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

def main():
    """Main entry point for schema constructor GUI"""
    app = QApplication(sys.argv)
    gui = SchemaConstructorGUI()
    gui.show()
    return app.exec()

if __name__ == "__main__":
    main()
