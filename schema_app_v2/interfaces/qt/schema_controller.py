#!/usr/bin/env python3
"""
Schema Controller Module
Clean separation of business logic from UI following v2 brick app pattern
"""

from typing import Optional, List
from PyQt6.QtWidgets import QMessageBox, QDialog

from schema_app_v2.core.schema_core import SchemaCore, Schema
from schema_app_v2.core.brick_integration import BrickIntegration
from schema_app_v2.core.flow_engine import FlowEngine, FlowConfig


class SchemaController:
    """Controller for schema operations - separates business logic from UI"""
    
    def __init__(self, schema_core: SchemaCore, brick_integration: BrickIntegration, flow_engine: FlowEngine):
        self.schema_core = schema_core
        self.brick_integration = brick_integration
        self.flow_engine = flow_engine
        self.current_schema: Optional[Schema] = None
    
    def create_new_schema(self, name: str, description: str = "") -> Optional[Schema]:
        """Create a new schema"""
        try:
            schema = self.schema_core.create_schema(name.strip(), description.strip())
            self.current_schema = schema
            return schema
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to create schema: {str(e)}")
            return None
    
    def get_all_schemas(self) -> List[Schema]:
        """Get all available schemas"""
        return self.schema_core.get_all_schemas()
    
    def select_schema(self, schema_name: str) -> bool:
        """Select a schema by name"""
        schemas = self.get_all_schemas()
        for schema in schemas:
            if schema.name == schema_name:
                self.current_schema = schema
                return True
        return False
    
    def update_schema_details(self, name: str = None, description: str = None, 
                          root_brick_id: str = None) -> bool:
        """Update current schema details"""
        if not self.current_schema:
            return False
        
        try:
            if name is not None:
                self.current_schema.name = name.strip()
            if description is not None:
                self.current_schema.description = description.strip()
            if root_brick_id is not None:
                self.current_schema.root_brick_id = root_brick_id
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to update schema: {str(e)}")
            return False
    
    def add_component_to_schema(self, brick_id: str) -> bool:
        """Add a component brick to current schema"""
        if not self.current_schema:
            QMessageBox.warning(None, "No Schema", "Please create or select a schema first")
            return False
        
        try:
            # Validate brick exists
            brick = self.brick_integration.get_brick_by_id(brick_id)
            if not brick:
                raise ValueError(f"Brick '{brick_id}' not found")
            
            # Add brick to schema's component list
            if brick_id not in self.current_schema.component_brick_ids:
                self.current_schema.component_brick_ids.append(brick_id)
                return True
            else:
                QMessageBox.warning(None, "Duplicate", f"Brick '{brick_id}' is already a component")
                return False
                
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to add component: {str(e)}")
            return False
    
    def remove_component_from_schema(self, brick_id: str) -> bool:
        """Remove a component brick from current schema"""
        if not self.current_schema:
            return False
        
        try:
            if brick_id in self.current_schema.component_brick_ids:
                self.current_schema.component_brick_ids.remove(brick_id)
                return True
            return False
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to remove component: {str(e)}")
            return False
    
    def delete_current_schema(self) -> bool:
        """Delete the current schema"""
        if not self.current_schema:
            return False
        
        try:
            success = self.schema_core.delete_schema(self.current_schema.schema_id)
            if success:
                self.current_schema = None
                return True
            return False
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to delete schema: {str(e)}")
            return False
    
    def save_current_schema(self) -> bool:
        """Save the current schema"""
        if not self.current_schema:
            return False
        
        try:
            return self.schema_core.save_schema(self.current_schema)
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to save schema: {str(e)}")
            return False
    
    def get_available_bricks(self):
        """Get all available bricks for component selection"""
        return self.brick_integration.get_available_bricks()
    
    def get_brick_by_id(self, brick_id: str):
        """Get a specific brick by ID"""
        return self.brick_integration.get_brick_by_id(brick_id)
    
    def get_node_shape_bricks(self):
        """Get bricks that can be used as root bricks"""
        return self.brick_integration.get_node_shape_bricks()
