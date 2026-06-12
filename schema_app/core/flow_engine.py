"""
Flow Engine Module
Manages interface flows for schemas - sequential, conditional, parallel, dynamic
"""

import json
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class FlowType(Enum):
    """Types of interface flow"""
    SEQUENTIAL = "sequential"      # Step 1 -> Step 2 -> Step 3
    CONDITIONAL = "conditional"    # If/else branching
    PARALLEL = "parallel"         # Multiple simultaneous steps
    DYNAMIC = "dynamic"           # User-driven navigation


@dataclass
class FlowStep:
    """Single step in interface flow"""
    step_id: str
    name: str
    description: str
    brick_ids: List[str]          # Bricks used in this step
    next_steps: List[str]         # Possible next steps (step_ids)
    conditions: Dict[str, Any] = field(default_factory=dict)  # Conditions for navigation
    ui_template: Optional[str] = None  # UI template to use
    validation_rules: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlowStep':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class FlowConfig:
    """Flow configuration for a schema"""
    flow_id: str
    flow_type: FlowType
    name: str
    description: str
    steps: List[FlowStep] = field(default_factory=list)
    navigation_rules: Dict[str, Any] = field(default_factory=dict)
    shared_data: Dict[str, Any] = field(default_factory=dict)  # Data shared between steps
    ui_theme: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert FlowType to string
        data['flow_type'] = self.flow_type.value
        # Convert FlowStep objects
        data['steps'] = [step.to_dict() for step in self.steps]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlowConfig':
        """Create from dictionary"""
        # Convert flow_type back to enum
        if isinstance(data.get('flow_type'), str):
            data['flow_type'] = FlowType(data['flow_type'])
        
        # Convert steps back to FlowStep objects
        if 'steps' in data and isinstance(data['steps'], list):
            data['steps'] = [FlowStep.from_dict(step) for step in data['steps']]
        
        return cls(**data)


class FlowEngine:
    """Engine for managing and validating flows"""
    
    def __init__(self):
        self.flows: Dict[str, FlowConfig] = {}
    
    def create_flow(self, name: str, flow_type: FlowType, description: str = "") -> FlowConfig:
        """Create a new flow configuration"""
        flow = FlowConfig(
            flow_id=str(uuid.uuid4()),
            flow_type=flow_type,
            name=name,
            description=description
        )
        self.flows[flow.flow_id] = flow
        return flow
    
    def add_step(self, flow_id: str, step: FlowStep) -> bool:
        """Add a step to a flow"""
        if flow_id not in self.flows:
            return False
        
        self.flows[flow_id].steps.append(step)
        return True
    
    def remove_step(self, flow_id: str, step_id: str) -> bool:
        """Remove a step from a flow"""
        if flow_id not in self.flows:
            return False
        
        flow = self.flows[flow_id]
        flow.steps = [step for step in flow.steps if step.step_id != step_id]
        return True
    
    def get_flow(self, flow_id: str) -> Optional[FlowConfig]:
        """Get a flow by ID"""
        return self.flows.get(flow_id)
    
    def validate_flow(self, flow_id: str) -> List[str]:
        """Validate a flow and return list of issues"""
        issues = []
        
        if flow_id not in self.flows:
            return ["Flow not found"]
        
        flow = self.flows[flow_id]
        
        # Check if flow has steps
        if not flow.steps:
            issues.append("Flow has no steps")
        
        # Validate each step
        step_ids = [step.step_id for step in flow.steps]
        
        for step in flow.steps:
            # Check step has bricks
            if not step.brick_ids:
                issues.append(f"Step '{step.name}' has no bricks")
            
            # Check next_steps exist
            for next_step_id in step.next_steps:
                if next_step_id not in step_ids:
                    issues.append(f"Step '{step.name}' references non-existent next step '{next_step_id}'")
        
        # Check for flow-specific validation
        if flow.flow_type == FlowType.SEQUENTIAL:
            issues.extend(self._validate_sequential_flow(flow))
        elif flow.flow_type == FlowType.CONDITIONAL:
            issues.extend(self._validate_conditional_flow(flow))
        elif flow.flow_type == FlowType.PARALLEL:
            issues.extend(self._validate_parallel_flow(flow))
        
        return issues
    
    def _validate_sequential_flow(self, flow: FlowConfig) -> List[str]:
        """Validate sequential flow"""
        issues = []
        
        if len(flow.steps) > 1:
            # Each step (except last) should have exactly one next step
            for i, step in enumerate(flow.steps[:-1]):
                if len(step.next_steps) != 1:
                    issues.append(f"Sequential flow step '{step.name}' should have exactly one next step")
                
                # Check if next step is the next in sequence
                expected_next = flow.steps[i + 1].step_id
                if step.next_steps and step.next_steps[0] != expected_next:
                    issues.append(f"Sequential flow step '{step.name}' should point to '{flow.steps[i + 1].name}'")
            
            # Last step should have no next steps
            if flow.steps[-1].next_steps:
                issues.append(f"Last sequential step '{flow.steps[-1].name}' should have no next steps")
        
        return issues
    
    def _validate_conditional_flow(self, flow: FlowConfig) -> List[str]:
        """Validate conditional flow"""
        issues = []
        
        # Conditional flows need at least one step with conditions
        has_conditions = any(step.conditions for step in flow.steps)
        if not has_conditions:
            issues.append("Conditional flow should have at least one step with conditions")
        
        # Steps with conditions should have multiple next steps
        for step in flow.steps:
            if step.conditions and len(step.next_steps) < 2:
                issues.append(f"Conditional step '{step.name}' should have multiple next steps")
        
        return issues
    
    def _validate_parallel_flow(self, flow: FlowConfig) -> List[str]:
        """Validate parallel flow"""
        issues = []
        
        # Parallel flows should have a starting step that branches to multiple steps
        if len(flow.steps) > 1:
            first_step = flow.steps[0]
            if len(first_step.next_steps) < 2:
                issues.append("Parallel flow should start with a step that branches to multiple steps")
        
        return issues
    
    def get_next_steps(self, flow_id: str, current_step_id: str, 
                      context: Dict[str, Any] = None) -> List[str]:
        """Get next possible steps based on current step and context"""
        if flow_id not in self.flows:
            return []
        
        flow = self.flows[flow_id]
        current_step = next((step for step in flow.steps if step.step_id == current_step_id), None)
        
        if not current_step:
            return []
        
        # For sequential flows, return the single next step
        if flow.flow_type == FlowType.SEQUENTIAL:
            return current_step.next_steps
        
        # For conditional flows, evaluate conditions
        if flow.flow_type == FlowType.CONDITIONAL:
            return self._evaluate_conditions(current_step, context or {})
        
        # For parallel flows, return all next steps
        if flow.flow_type == FlowType.PARALLEL:
            return current_step.next_steps
        
        # For dynamic flows, return all possible next steps
        if flow.flow_type == FlowType.DYNAMIC:
            return current_step.next_steps
        
        return []
    
    def _evaluate_conditions(self, step: FlowStep, context: Dict[str, Any]) -> List[str]:
        """Evaluate conditions for a conditional step"""
        if not step.conditions:
            return step.next_steps
        
        # Simple condition evaluation - can be extended
        for condition, next_step_id in step.conditions.items():
            if self._check_condition(condition, context):
                return [next_step_id]
        
        # Default to first next step if no conditions match
        return step.next_steps[:1] if step.next_steps else []
    
    def _check_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Check if a condition is met"""
        # Simple implementation - can be extended with more complex logic
        if condition.startswith("field_equals:"):
            field_name, value = condition[len("field_equals:"):].split("=", 1)
            return context.get(field_name) == value
        
        if condition.startswith("field_exists:"):
            field_name = condition[len("field_exists:"):]
            return field_name in context and context[field_name] is not None
        
        # Add more condition types as needed
        return False
    
    def get_flow_summary(self, flow_id: str) -> Dict[str, Any]:
        """Get a summary of a flow"""
        if flow_id not in self.flows:
            return {}
        
        flow = self.flows[flow_id]
        
        return {
            "flow_id": flow.flow_id,
            "name": flow.name,
            "description": flow.description,
            "flow_type": flow.flow_type.value,
            "step_count": len(flow.steps),
            "total_bricks": sum(len(step.brick_ids) for step in flow.steps),
            "has_conditions": any(step.conditions for step in flow.steps),
            "validation_issues": self.validate_flow(flow_id)
        }
