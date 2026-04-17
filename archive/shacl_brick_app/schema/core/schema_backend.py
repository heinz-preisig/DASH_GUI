#!/usr/bin/env python3
"""
Step 2: Schema Backend API
Event-driven backend for schema construction, following the same pattern as Step 1
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json
import uuid
from datetime import datetime

from ...core.brick_backend import BrickBackendAPI
from .schema_constructor import (
    SchemaConstructor, InterfaceFlowType, SchemaComposition, 
    DaisyChain, InterfaceStep
)

class SchemaBackendAPI:
    """Backend API for schema construction with event-driven architecture"""
    
    def __init__(self, repository_path: str = "schema_repositories"):
        self.brick_backend = BrickBackendAPI(repository_path)
        self.schema_constructor = SchemaConstructor(self.brick_backend)
        self._initialize_repository()
    
    def _initialize_repository(self):
        """Initialize repository structure"""
        # Ensure we have an active library
        result = self.get_repository_info()
        if not result["data"]["active_library"]:
            self.set_active_library("default")
    
    # Repository Management
    def get_repository_info(self) -> Dict[str, Any]:
        """Get repository information"""
        return self.brick_backend.get_repository_info()
    
    def set_active_library(self, library_name: str) -> Dict[str, Any]:
        """Set active library"""
        return self.brick_backend.set_active_library(library_name)
    
    def create_library(self, name: str, description: str, author: str = "Unknown") -> Dict[str, Any]:
        """Create new library"""
        return self.brick_backend.create_library(name, description, author)
    
    # Schema Management
    def create_schema(self, name: str, description: str, root_brick_id: str,
                     component_brick_ids: List[str] = None,
                     interface_flow: str = "sequential") -> Dict[str, Any]:
        """Create a new schema composition"""
        try:
            flow_type = InterfaceFlowType(interface_flow)
            schema = self.schema_constructor.create_schema(
                name=name,
                description=description,
                root_brick_id=root_brick_id,
                component_brick_ids=component_brick_ids or [],
                interface_flow=flow_type
            )
            
            return {
                "status": "success",
                "message": f"Schema '{name}' created successfully",
                "data": self._schema_to_dict(schema)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create schema: {str(e)}"
            }
    
    def create_schema_from_template(self, template_name: str, custom_name: str = None,
                                   brick_mappings: Dict[str, str] = None) -> Dict[str, Any]:
        """Create schema from predefined template"""
        try:
            schema = self.schema_constructor.create_schema_from_template(
                template_name=template_name,
                custom_name=custom_name,
                brick_mappings=brick_mappings or {}
            )
            
            return {
                "status": "success",
                "message": f"Schema created from template '{template_name}'",
                "data": self._schema_to_dict(schema)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create schema from template: {str(e)}"
            }
    
    def extend_schema(self, parent_schema_id: str, name: str, description: str,
                     additional_brick_ids: List[str]) -> Dict[str, Any]:
        """Create a schema that extends an existing one"""
        try:
            schema = self.schema_constructor.extend_schema(
                parent_schema_id=parent_schema_id,
                name=name,
                description=description,
                additional_brick_ids=additional_brick_ids
            )
            
            return {
                "status": "success",
                "message": f"Schema '{name}' extended successfully",
                "data": self._schema_to_dict(schema)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to extend schema: {str(e)}"
            }
    
    def get_schema(self, schema_id: str) -> Dict[str, Any]:
        """Get schema by ID"""
        schema = self.schema_constructor.get_schema(schema_id)
        if schema:
            return {
                "status": "success",
                "message": f"Schema '{schema_id}' retrieved",
                "data": self._schema_to_dict(schema)
            }
        else:
            return {
                "status": "error",
                "message": f"Schema '{schema_id}' not found"
            }
    
    def get_all_schemas(self) -> Dict[str, Any]:
        """Get all schemas"""
        schemas = self.schema_constructor.get_all_schemas()
        return {
            "status": "success",
            "message": f"Retrieved {len(schemas)} schemas",
            "data": {
                "schemas": [self._schema_to_dict(schema) for schema in schemas],
                "total_count": len(schemas)
            }
        }
    
    def update_schema(self, schema_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update schema properties"""
        try:
            schema = self.schema_constructor.get_schema(schema_id)
            if not schema:
                return {
                    "status": "error",
                    "message": f"Schema '{schema_id}' not found"
                }
            
            # Update allowed properties
            if "name" in updates:
                schema.name = updates["name"]
            if "description" in updates:
                schema.description = updates["description"]
            if "metadata" in updates:
                schema.metadata.update(updates["metadata"])
            
            schema.modified_at = datetime.now().isoformat()
            
            return {
                "status": "success",
                "message": f"Schema '{schema_id}' updated",
                "data": self._schema_to_dict(schema)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to update schema: {str(e)}"
            }
    
    def delete_schema(self, schema_id: str) -> Dict[str, Any]:
        """Delete schema"""
        try:
            if schema_id in self.schema_constructor.schemas:
                del self.schema_constructor.schemas[schema_id]
                return {
                    "status": "success",
                    "message": f"Schema '{schema_id}' deleted"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Schema '{schema_id}' not found"
                }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete schema: {str(e)}"
            }
    
    # Daisy Chain Management
    def create_daisy_chain(self, name: str, description: str, schema_ids: List[str],
                         navigation_rules: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a daisy-chain of schemas for multi-step interfaces"""
        try:
            daisy_chain = self.schema_constructor.create_daisy_chain(
                name=name,
                description=description,
                schema_ids=schema_ids,
                navigation_rules=navigation_rules or {}
            )
            
            return {
                "status": "success",
                "message": f"Daisy chain '{name}' created successfully",
                "data": self._daisy_chain_to_dict(daisy_chain)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create daisy chain: {str(e)}"
            }
    
    def get_daisy_chain(self, chain_id: str) -> Dict[str, Any]:
        """Get daisy chain by ID"""
        daisy_chain = self.schema_constructor.get_daisy_chain(chain_id)
        if daisy_chain:
            return {
                "status": "success",
                "message": f"Daisy chain '{chain_id}' retrieved",
                "data": self._daisy_chain_to_dict(daisy_chain)
            }
        else:
            return {
                "status": "error",
                "message": f"Daisy chain '{chain_id}' not found"
            }
    
    def get_all_daisy_chains(self) -> Dict[str, Any]:
        """Get all daisy chains"""
        daisy_chains = self.schema_constructor.get_all_daisy_chains()
        return {
            "status": "success",
            "message": f"Retrieved {len(daisy_chains)} daisy chains",
            "data": {
                "daisy_chains": [self._daisy_chain_to_dict(chain) for chain in daisy_chains],
                "total_count": len(daisy_chains)
            }
        }
    
    def update_daisy_chain(self, chain_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update daisy chain properties"""
        try:
            daisy_chain = self.schema_constructor.get_daisy_chain(chain_id)
            if not daisy_chain:
                return {
                    "status": "error",
                    "message": f"Daisy chain '{chain_id}' not found"
                }
            
            # Update allowed properties
            if "name" in updates:
                daisy_chain.name = updates["name"]
            if "description" in updates:
                daisy_chain.description = updates["description"]
            if "navigation_rules" in updates:
                daisy_chain.navigation_rules.update(updates["navigation_rules"])
            if "metadata" in updates:
                daisy_chain.metadata.update(updates["metadata"])
            
            return {
                "status": "success",
                "message": f"Daisy chain '{chain_id}' updated",
                "data": self._daisy_chain_to_dict(daisy_chain)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to update daisy chain: {str(e)}"
            }
    
    def delete_daisy_chain(self, chain_id: str) -> Dict[str, Any]:
        """Delete daisy chain"""
        try:
            if chain_id in self.schema_constructor.daisy_chains:
                del self.schema_constructor.daisy_chains[chain_id]
                return {
                    "status": "success",
                    "message": f"Daisy chain '{chain_id}' deleted"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Daisy chain '{chain_id}' not found"
                }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete daisy chain: {str(e)}"
            }
    
    # Template Management
    def get_templates(self) -> Dict[str, Any]:
        """Get available schema templates"""
        templates = self.schema_constructor.templates
        return {
            "status": "success",
            "message": f"Retrieved {len(templates)} templates",
            "data": {
                "templates": templates,
                "total_count": len(templates)
            }
        }
    
    # Export and Generation
    def export_schema_shacl(self, schema_id: str) -> Dict[str, Any]:
        """Export schema as SHACL"""
        try:
            shacl_data = self.schema_constructor.export_schema_shacl(schema_id)
            return {
                "status": "success",
                "message": f"Schema '{schema_id}' exported as SHACL",
                "data": shacl_data
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to export schema: {str(e)}"
            }
    
    def export_daisy_chain_config(self, chain_id: str) -> Dict[str, Any]:
        """Export daisy chain configuration for HTML GUI generation"""
        try:
            chain_config = self.schema_constructor.export_daisy_chain_config(chain_id)
            return {
                "status": "success",
                "message": f"Daisy chain '{chain_id}' configuration exported",
                "data": chain_config
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to export daisy chain config: {str(e)}"
            }
    
    def generate_interface_config(self, chain_id: str) -> Dict[str, Any]:
        """Generate interface configuration for HTML GUI"""
        try:
            interface_config = self.schema_constructor.generate_interface_config(chain_id)
            return {
                "status": "success",
                "message": f"Interface configuration generated for chain '{chain_id}'",
                "data": interface_config
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to generate interface config: {str(e)}"
            }
    
    # Brick Integration (delegated to brick backend)
    def get_library_bricks(self, library_name: str = None, object_type: str = None, 
                           tags: List[str] = None) -> Dict[str, Any]:
        """Get bricks from library"""
        return self.brick_backend.get_library_bricks(library_name, object_type, tags)
    
    def search_bricks(self, query: str, library_name: str = None) -> Dict[str, Any]:
        """Search bricks"""
        return self.brick_backend.search_bricks(query, library_name)
    
    def get_brick_details(self, brick_id: str, library_name: str = None) -> Dict[str, Any]:
        """Get brick details"""
        return self.brick_backend.get_brick_details(brick_id, library_name)
    
    # Statistics and Utilities
    def get_repository_statistics(self, library_name: str = None) -> Dict[str, Any]:
        """Get repository statistics"""
        try:
            # Get brick statistics
            brick_stats = self.brick_backend.get_library_statistics(library_name)
            
            # Get schema statistics
            schemas = self.schema_constructor.get_all_schemas()
            daisy_chains = self.schema_constructor.get_all_daisy_chains()
            
            # Analyze schemas
            schema_types = {}
            interface_flows = {}
            for schema in schemas:
                schema_type = schema.root_brick_id
                schema_types[schema_type] = schema_types.get(schema_type, 0) + 1
                
                flow_type = schema.interface_flow.value
                interface_flows[flow_type] = interface_flows.get(flow_type, 0) + 1
            
            return {
                "status": "success",
                "message": "Repository statistics retrieved",
                "data": {
                    "bricks": brick_stats.get("data", {}),
                    "schemas": {
                        "total_schemas": len(schemas),
                        "schema_types": schema_types,
                        "interface_flows": interface_flows
                    },
                    "daisy_chains": {
                        "total_chains": len(daisy_chains),
                        "average_schemas_per_chain": sum(len(chain.schemas) for chain in daisy_chains) / len(daisy_chains) if daisy_chains else 0
                    },
                    "templates": {
                        "total_templates": len(self.schema_constructor.templates)
                    }
                }
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get statistics: {str(e)}"
            }
    
    # Helper methods
    def _schema_to_dict(self, schema: SchemaComposition) -> Dict[str, Any]:
        """Convert schema to dictionary"""
        return {
            "schema_id": schema.schema_id,
            "name": schema.name,
            "description": schema.description,
            "root_brick_id": schema.root_brick_id,
            "component_brick_ids": schema.component_brick_ids,
            "inheritance_chain": schema.inheritance_chain,
            "interface_flow": schema.interface_flow.value,
            "interface_steps": [
                {
                    "step_id": step.step_id,
                    "name": step.name,
                    "description": step.description,
                    "brick_ids": step.brick_ids,
                    "next_steps": step.next_steps,
                    "conditions": step.conditions,
                    "ui_template": step.ui_template,
                    "validation_rules": step.validation_rules,
                    "metadata": step.metadata
                }
                for step in schema.interface_steps
            ],
            "relationships": schema.relationships,
            "metadata": schema.metadata,
            "created_at": schema.created_at,
            "modified_at": schema.modified_at
        }
    
    def _daisy_chain_to_dict(self, daisy_chain: DaisyChain) -> Dict[str, Any]:
        """Convert daisy chain to dictionary"""
        return {
            "chain_id": daisy_chain.chain_id,
            "name": daisy_chain.name,
            "description": daisy_chain.description,
            "schemas": daisy_chain.schemas,
            "navigation_rules": daisy_chain.navigation_rules,
            "shared_data": daisy_chain.shared_data,
            "conditional_logic": daisy_chain.conditional_logic,
            "ui_theme": daisy_chain.ui_theme,
            "metadata": daisy_chain.metadata
        }

class SchemaEventProcessor:
    """Event processor for schema operations"""
    
    def __init__(self, backend: SchemaBackendAPI):
        self.backend = backend
    
    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process an event from the frontend"""
        event_type = event.get("event")
        
        # Repository events
        if event_type == "get_repository_info":
            return self.backend.get_repository_info()
        
        elif event_type == "create_library":
            return self.backend.create_library(
                event["name"],
                event["description"],
                event.get("author", "Unknown")
            )
        
        elif event_type == "set_active_library":
            return self.backend.set_active_library(event["library_name"])
        
        # Schema events
        elif event_type == "create_schema":
            return self.backend.create_schema(
                event["name"],
                event["description"],
                event["root_brick_id"],
                event.get("component_brick_ids"),
                event.get("interface_flow", "sequential")
            )
        
        elif event_type == "create_schema_from_template":
            return self.backend.create_schema_from_template(
                event["template_name"],
                event.get("custom_name"),
                event.get("brick_mappings")
            )
        
        elif event_type == "extend_schema":
            return self.backend.extend_schema(
                event["parent_schema_id"],
                event["name"],
                event["description"],
                event["additional_brick_ids"]
            )
        
        elif event_type == "get_schema":
            return self.backend.get_schema(event["schema_id"])
        
        elif event_type == "get_all_schemas":
            return self.backend.get_all_schemas()
        
        elif event_type == "update_schema":
            return self.backend.update_schema(event["schema_id"], event["updates"])
        
        elif event_type == "delete_schema":
            return self.backend.delete_schema(event["schema_id"])
        
        # Daisy chain events
        elif event_type == "create_daisy_chain":
            return self.backend.create_daisy_chain(
                event["name"],
                event["description"],
                event["schema_ids"],
                event.get("navigation_rules")
            )
        
        elif event_type == "get_daisy_chain":
            return self.backend.get_daisy_chain(event["chain_id"])
        
        elif event_type == "get_all_daisy_chains":
            return self.backend.get_all_daisy_chains()
        
        elif event_type == "update_daisy_chain":
            return self.backend.update_daisy_chain(event["chain_id"], event["updates"])
        
        elif event_type == "delete_daisy_chain":
            return self.backend.delete_daisy_chain(event["chain_id"])
        
        # Template events
        elif event_type == "get_templates":
            return self.backend.get_templates()
        
        # Export events
        elif event_type == "export_schema_shacl":
            return self.backend.export_schema_shacl(event["schema_id"])
        
        elif event_type == "export_daisy_chain_config":
            return self.backend.export_daisy_chain_config(event["chain_id"])
        
        elif event_type == "generate_interface_config":
            return self.backend.generate_interface_config(event["chain_id"])
        
        # Brick integration events
        elif event_type == "get_library_bricks":
            return self.backend.get_library_bricks(
                event.get("library_name"),
                event.get("object_type"),
                event.get("tags")
            )
        
        elif event_type == "search_bricks":
            return self.backend.search_bricks(
                event["query"],
                event.get("library_name")
            )
        
        elif event_type == "get_brick_details":
            return self.backend.get_brick_details(
                event["brick_id"],
                event.get("library_name")
            )
        
        # Statistics events
        elif event_type == "get_repository_statistics":
            return self.backend.get_repository_statistics(event.get("library_name"))
        
        else:
            return {
                "status": "error",
                "message": f"Unknown event type: {event_type}"
            }
