"""
Flow Editor Dialog
Dialog for editing flow configurations
"""

import uuid
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import QDialog, QMessageBox, QInputDialog
from PyQt6.QtCore import Qt

from ..ui_components import UiLoader, ComponentManager

# Import flow engine components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from flow_engine import FlowEngine, FlowType, FlowStep, FlowConfig
from brick_integration import BrickIntegration


class FlowEditorDialog(QDialog):
    """Dialog for editing flow configurations"""
    
    def __init__(self, flow_engine: FlowEngine, brick_integration: BrickIntegration, 
                 existing_flow: Optional[FlowConfig] = None, parent=None):
        super().__init__(parent)
        
        self.flow_engine = flow_engine
        self.brick_integration = brick_integration
        self.existing_flow = existing_flow
        
        # Load UI from .ui file
        self.ui_loader = UiLoader()
        self.ui = self.ui_loader.load_flow_editor_dialog(self)
        
        # Component manager
        self.components = ComponentManager()
        
        # Current state
        self.current_flow: Optional[FlowConfig] = None
        self.current_step: Optional[FlowStep] = None
        self.available_bricks = []
        
        # Setup dialog
        self.setup_dialog()
        self.connect_signals()
        self.load_initial_data()
    
    def setup_dialog(self):
        """Setup dialog components"""
        self.setWindowTitle("Flow Editor")
        self.setModal(True)
        
        # If existing flow, load it
        if self.existing_flow:
            self.load_flow_into_ui(self.existing_flow)
        else:
            # Create new flow
            flow_type = FlowType.SEQUENTIAL
            self.current_flow = self.flow_engine.create_flow(
                "New Flow", flow_type, "New flow configuration"
            )
            self.load_flow_into_ui(self.current_flow)
    
    def connect_signals(self):
        """Connect UI signals"""
        # Flow information
        self.ui.flowNameLineEdit.textChanged.connect(self.on_flow_info_changed)
        self.ui.flowTypeComboBox.currentTextChanged.connect(self.on_flow_type_changed)
        self.ui.flowDescriptionLineEdit.textChanged.connect(self.on_flow_info_changed)
        
        # Step management
        self.ui.stepsListWidget.itemSelectionChanged.connect(self.on_step_selection_changed)
        self.ui.addStepButton.clicked.connect(self.add_step)
        self.ui.removeStepButton.clicked.connect(self.remove_step)
        self.ui.moveUpButton.clicked.connect(self.move_step_up)
        self.ui.moveDownButton.clicked.connect(self.move_step_down)
        
        # Step details
        self.ui.stepNameLineEdit.textChanged.connect(self.on_step_details_changed)
        self.ui.stepDescriptionLineEdit.textChanged.connect(self.on_step_details_changed)
        self.ui.availableBricksListWidget.itemDoubleClicked.connect(self.add_brick_to_step)
        self.ui.stepBricksListWidget.itemDoubleClicked.connect(self.remove_brick_from_step)
        self.ui.addBrickToStepButton.clicked.connect(self.add_brick_to_step)
        self.ui.removeBrickFromStepButton.clicked.connect(self.remove_brick_from_step)
        
        # Navigation
        self.ui.nextStepsListWidget.itemChanged.connect(self.on_navigation_changed)
        self.ui.conditionsTextEdit.textChanged.connect(self.on_conditions_changed)
        
        # Dialog buttons
        self.ui.validateFlowButton.clicked.connect(self.validate_flow)
        self.ui.okButton.clicked.connect(self.accept_dialog)
        self.ui.cancelButton.clicked.connect(self.reject)
    
    def load_initial_data(self):
        """Load initial data"""
        # Load available bricks
        self.refresh_available_bricks()
        
        # Refresh steps list
        self.refresh_steps_list()
        
        # Set initial UI state
        self.set_step_ui_state(False)
    
    def refresh_available_bricks(self):
        """Refresh available bricks list"""
        try:
            self.available_bricks = self.brick_integration.get_available_bricks()
            self.components.set_list_widget_data(
                self.ui.availableBricksListWidget, 
                self.available_bricks, 
                'brick_id'
            )
        except Exception as e:
            print(f"Error loading available bricks: {e}")
            self.available_bricks = []
            self.components.clear_list_widget(self.ui.availableBricksListWidget)
    
    def refresh_steps_list(self):
        """Refresh steps list"""
        if not self.current_flow:
            return
        
        self.components.clear_list_widget(self.ui.stepsListWidget)
        
        for i, step in enumerate(self.current_flow.steps):
            step_text = f"{i+1}. {step.name}"
            if step.description:
                step_text += f" - {step.description}"
            step_text += f" ({len(step.brick_ids)} bricks)"
            
            self.ui.stepsListWidget.addItem(step_text)
    
    def refresh_step_bricks(self):
        """Refresh step bricks list"""
        if not self.current_step:
            self.components.clear_list_widget(self.ui.stepBricksListWidget)
            return
        
        step_bricks = []
        for brick_id in self.current_step.brick_ids:
            brick = next((b for b in self.available_bricks if b.brick_id == brick_id), None)
            if brick:
                step_bricks.append(brick)
        
        self.components.set_list_widget_data(
            self.ui.stepBricksListWidget, 
            step_bricks, 
            'brick_id'
        )
    
    def refresh_next_steps(self):
        """Refresh next steps list"""
        if not self.current_step:
            self.components.clear_list_widget(self.ui.nextStepsListWidget)
            return
        
        self.components.clear_list_widget(self.ui.nextStepsListWidget)
        
        # Add checkboxes for all possible next steps
        for step in self.current_flow.steps:
            if step.step_id != self.current_step.step_id:
                item = self.ui.nextStepsListWidget.addItem(step.name)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                
                # Check if this is a next step
                is_next = step.step_id in self.current_step.next_steps
                item.setCheckState(Qt.CheckState.Checked if is_next else Qt.CheckState.Unchecked)
    
    def set_step_ui_state(self, step_selected: bool):
        """Set step UI state"""
        self.components.set_enabled(self.ui.stepNameLineEdit, step_selected)
        self.components.set_enabled(self.ui.stepDescriptionLineEdit, step_selected)
        self.components.set_enabled(self.ui.availableBricksListWidget, step_selected)
        self.components.set_enabled(self.ui.stepBricksListWidget, step_selected)
        self.components.set_enabled(self.ui.addBrickToStepButton, step_selected)
        self.components.set_enabled(self.ui.removeBrickFromStepButton, step_selected)
        self.components.set_enabled(self.ui.nextStepsListWidget, step_selected)
        self.components.set_enabled(self.ui.conditionsTextEdit, step_selected)
        
        # Step management buttons
        has_steps = self.current_flow and len(self.current_flow.steps) > 0
        self.components.set_enabled(self.ui.removeStepButton, step_selected)
        self.components.set_enabled(self.ui.moveUpButton, step_selected and has_steps)
        self.components.set_enabled(self.ui.moveDownButton, step_selected and has_steps)
    
    def load_flow_into_ui(self, flow: FlowConfig):
        """Load flow data into UI"""
        self.current_flow = flow
        
        # Flow information
        self.components.set_line_edit_text(self.ui.flowNameLineEdit, flow.name)
        self.components.set_combo_box_current_text(self.ui.flowTypeComboBox, flow.flow_type.value)
        self.components.set_line_edit_text(self.ui.flowDescriptionLineEdit, flow.description)
        
        # Refresh steps
        self.refresh_steps_list()
        
        # Select first step if available
        if flow.steps:
            self.ui.stepsListWidget.setCurrentRow(0)
            self.on_step_selection_changed()
    
    def load_step_into_ui(self, step: FlowStep):
        """Load step data into UI"""
        self.current_step = step
        
        # Step details
        self.components.set_line_edit_text(self.ui.stepNameLineEdit, step.name)
        self.components.set_line_edit_text(self.ui.stepDescriptionLineEdit, step.description)
        
        # Step bricks
        self.refresh_step_bricks()
        
        # Next steps
        self.refresh_next_steps()
        
        # Conditions
        if step.conditions:
            import json
            conditions_text = json.dumps(step.conditions, indent=2)
            self.components.set_text_edit_text(self.ui.conditionsTextEdit, conditions_text)
        else:
            self.components.set_text_edit_text(self.ui.conditionsTextEdit, "")
        
        self.set_step_ui_state(True)
    
    def add_step(self):
        """Add a new step"""
        if not self.current_flow:
            return
        
        # Get step name
        name, ok = QInputDialog.getText(self, "New Step", "Enter step name:")
        if not ok or not name.strip():
            return
        
        # Create new step
        step = FlowStep(
            step_id=str(uuid.uuid4()),
            name=name.strip(),
            description="",
            brick_ids=[],
            next_steps=[]
        )
        
        # Add to flow
        self.current_flow.steps.append(step)
        
        # Refresh UI
        self.refresh_steps_list()
        
        # Select new step
        self.ui.stepsListWidget.setCurrentRow(len(self.current_flow.steps) - 1)
        self.on_step_selection_changed()
    
    def remove_step(self):
        """Remove current step"""
        if not self.current_step or not self.current_flow:
            return
        
        # Confirm removal
        if not self.components.ask_confirmation(
            self, "Confirm Remove", 
            f"Remove step '{self.current_step.name}'?"
        ):
            return
        
        # Remove step
        self.current_flow.steps = [
            step for step in self.current_flow.steps 
            if step.step_id != self.current_step.step_id
        ]
        
        # Clear current step
        self.current_step = None
        
        # Refresh UI
        self.refresh_steps_list()
        self.set_step_ui_state(False)
    
    def move_step_up(self):
        """Move current step up"""
        if not self.current_step or not self.current_flow:
            return
        
        current_index = next(
            (i for i, step in enumerate(self.current_flow.steps) 
             if step.step_id == self.current_step.step_id), 
            -1
        )
        
        if current_index > 0:
            # Swap with previous step
            self.current_flow.steps[current_index], self.current_flow.steps[current_index - 1] = \
                self.current_flow.steps[current_index - 1], self.current_flow.steps[current_index]
            
            # Refresh UI
            self.refresh_steps_list()
            self.ui.stepsListWidget.setCurrentRow(current_index - 1)
    
    def move_step_down(self):
        """Move current step down"""
        if not self.current_step or not self.current_flow:
            return
        
        current_index = next(
            (i for i, step in enumerate(self.current_flow.steps) 
             if step.step_id == self.current_step.step_id), 
            -1
        )
        
        if current_index < len(self.current_flow.steps) - 1:
            # Swap with next step
            self.current_flow.steps[current_index], self.current_flow.steps[current_index + 1] = \
                self.current_flow.steps[current_index + 1], self.current_flow.steps[current_index]
            
            # Refresh UI
            self.refresh_steps_list()
            self.ui.stepsListWidget.setCurrentRow(current_index + 1)
    
    def add_brick_to_step(self):
        """Add selected brick to current step"""
        if not self.current_step:
            return
        
        brick_id = self.components.get_selected_list_data(self.ui.availableBricksListWidget)
        if not brick_id:
            return
        
        if brick_id not in self.current_step.brick_ids:
            self.current_step.brick_ids.append(brick_id)
            self.refresh_step_bricks()
    
    def remove_brick_from_step(self):
        """Remove selected brick from current step"""
        if not self.current_step:
            return
        
        brick_id = self.components.get_selected_list_data(self.ui.stepBricksListWidget)
        if not brick_id:
            return
        
        if brick_id in self.current_step.brick_ids:
            self.current_step.brick_ids.remove(brick_id)
            self.refresh_step_bricks()
    
    def validate_flow(self):
        """Validate current flow"""
        if not self.current_flow:
            self.components.show_error_message(self, "Error", "No flow to validate.")
            return
        
        issues = self.flow_engine.validate_flow(self.current_flow.flow_id)
        
        if issues:
            self.components.show_warning_message(
                self, "Validation Issues", 
                "Flow has validation issues:\n\n" + "\n".join(issues)
            )
        else:
            self.components.show_info_message(self, "Validation", "Flow is valid!")
    
    def accept_dialog(self):
        """Accept dialog and save flow"""
        if not self.current_flow:
            self.components.show_error_message(self, "Error", "No flow to save.")
            return
        
        # Validate flow
        issues = self.flow_engine.validate_flow(self.current_flow.flow_id)
        if issues:
            reply = self.components.ask_confirmation(
                self, "Validation Issues", 
                "Flow has validation issues:\n\n" + "\n".join(issues) + "\n\nSave anyway?"
            )
            if not reply:
                return
        
        # Accept dialog
        self.accept()
    
    def get_flow_config(self) -> Optional[FlowConfig]:
        """Get the configured flow"""
        return self.current_flow
    
    # Event handlers
    def on_flow_info_changed(self):
        """Handle flow information change"""
        if self.current_flow:
            self.current_flow.name = self.components.get_line_edit_text(self.ui.flowNameLineEdit)
            self.current_flow.description = self.components.get_line_edit_text(self.ui.flowDescriptionLineEdit)
    
    def on_flow_type_changed(self):
        """Handle flow type change"""
        if self.current_flow:
            flow_type_str = self.components.get_combo_box_current_text(self.ui.flowTypeComboBox)
            self.current_flow.flow_type = FlowType(flow_type_str.lower())
    
    def on_step_selection_changed(self):
        """Handle step selection change"""
        if not self.current_flow:
            return
        
        current_row = self.ui.stepsListWidget.currentRow()
        if 0 <= current_row < len(self.current_flow.steps):
            self.load_step_into_ui(self.current_flow.steps[current_row])
        else:
            self.current_step = None
            self.set_step_ui_state(False)
    
    def on_step_details_changed(self):
        """Handle step details change"""
        if self.current_step:
            self.current_step.name = self.components.get_line_edit_text(self.ui.stepNameLineEdit)
            self.current_step.description = self.components.get_line_edit_text(self.ui.stepDescriptionLineEdit)
            
            # Update steps list
            self.refresh_steps_list()
            
            # Reselect current step
            current_index = next(
                (i for i, step in enumerate(self.current_flow.steps) 
                 if step.step_id == self.current_step.step_id), 
                -1
            )
            if current_index >= 0:
                self.ui.stepsListWidget.setCurrentRow(current_index)
    
    def on_navigation_changed(self):
        """Handle navigation change"""
        if not self.current_step:
            return
        
        # Get checked next steps
        next_steps = []
        for i in range(self.ui.nextStepsListWidget.count()):
            item = self.ui.nextStepsListWidget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                # Find corresponding step
                step_name = item.text()
                for step in self.current_flow.steps:
                    if step.name == step_name and step.step_id != self.current_step.step_id:
                        next_steps.append(step.step_id)
                        break
        
        self.current_step.next_steps = next_steps
    
    def on_conditions_changed(self):
        """Handle conditions change"""
        if not self.current_step:
            return
        
        conditions_text = self.components.get_text_edit_text(self.ui.conditionsTextEdit).strip()
        
        if conditions_text:
            try:
                import json
                self.current_step.conditions = json.loads(conditions_text)
            except json.JSONDecodeError:
                # Invalid JSON - keep as is for now
                pass
        else:
            self.current_step.conditions = {}
