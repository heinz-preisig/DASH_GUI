#!/usr/bin/env python3
"""
REST API for SHACL Brick Generator
Provides web interface for multi-tenant backend
"""

import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import asdict

try:
    from flask import Flask, request, jsonify, session
    from flask_cors import CORS
    from werkzeug.exceptions import HTTPException
except ImportError:
    print("Flask not available. Install with: pip install flask flask-cors")
    Flask = None
    CORS = None

import sys
import os
from pathlib import Path as _Path
_dash_gui_root = str(_Path(__file__).parent.parent.parent)
if _dash_gui_root not in sys.path:
    sys.path.insert(0, _dash_gui_root)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../business'))

from core.multi_tenant_backend import MultiTenantBackend
from core.abstract_events import EventType, ClientType


class BrickWebAPI:
    """REST API wrapper for SHACL Brick Generator"""
    
    def __init__(self, backend: MultiTenantBackend, host='localhost', port=5000):
        if Flask is None:
            raise ImportError("Flask is required for web API")
        
        self.backend = backend
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        
        # Configure Flask
        self.app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
        self.app.config['SESSION_TYPE'] = 'filesystem'
        
        # Enable CORS
        CORS(self.app)
        
        # Setup routes
        self._setup_routes()
        
        # Error handlers
        self._setup_error_handlers()
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        # Main page
        @self.app.route('/')
        def index():
            """Main web interface page"""
            from flask import render_template
            return render_template('index.html')
        
        # Session management
        @self.app.route('/api/session', methods=['POST'])
        def create_session():
            """Create a new session"""
            data = request.get_json() or {}
            client_type = data.get('client_type', 'web')
            user_info = data.get('user_info', {})
            
            session_id = self.backend.create_session(client_type, user_info)
            
            return jsonify({
                "status": "success",
                "data": {
                    "session_id": session_id,
                    "client_type": client_type
                }
            })
        
        @self.app.route('/api/session/<session_id>', methods=['GET'])
        def get_session(session_id):
            """Get session information"""
            backend_session = self.backend.get_session(session_id)
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404
            
            return jsonify({
                "status": "success",
                "data": backend_session.get_session_info()
            })
        
        @self.app.route('/api/session/<session_id>', methods=['DELETE'])
        def delete_session(session_id):
            """Delete a session"""
            success = self.backend.remove_session(session_id)
            if success:
                return jsonify({
                    "status": "success",
                    "message": "Session deleted"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Failed to delete session"
                }), 404
        
        # Repository management
        @self.app.route('/api/repository', methods=['GET'])
        def get_repository():
            """Get repository information"""
            result = self.backend.get_repository_info()
            return jsonify(result)
        
        @self.app.route('/api/libraries', methods=['GET'])
        def get_libraries():
            """Get all brick libraries"""
            names = self.backend.brick_core.get_libraries()
            return jsonify({"status": "success", "data": names})

        @self.app.route('/api/libraries', methods=['POST'])
        def create_library():
            """Create a new brick library"""
            data = request.get_json() or {}
            name = data.get('library_name', '').strip()
            if not name:
                return jsonify({"status": "error", "message": "library_name is required"}), 400
            import os as _os
            lib_path = _os.path.join(self.backend.brick_core.repository_path, name)
            _os.makedirs(lib_path, exist_ok=True)
            return jsonify({"status": "success", "data": {"name": name}})

        @self.app.route('/api/libraries/filesystem', methods=['GET'])
        def get_filesystem_libraries():
            """Get libraries from filesystem (shared_libraries)"""
            result = self.backend.get_shared_library_info()
            return jsonify(result)

        @self.app.route('/api/libraries/<library_name>/bricks', methods=['GET'])
        def get_library_bricks(library_name):
            """Get bricks from a specific library"""
            bricks = self.backend.brick_core.get_all_bricks(library_name)
            return jsonify({"status": "success", "data": [b.to_dict() for b in bricks]})
        
        @self.app.route('/api/bricks', methods=['GET'])
        def get_all_bricks():
            """Get all bricks from all libraries"""
            result = self.backend.get_all_bricks()
            return jsonify(result)
        
        @self.app.route('/api/session/<session_id>/brick/<brick_id>', methods=['DELETE'])
        def delete_brick(session_id, brick_id):
            """Delete a specific brick"""
            ok = self.backend.brick_core.delete_brick(brick_id)
            if ok:
                return jsonify({"status": "success", "message": "Brick deleted"})
            return jsonify({"status": "error", "message": "Brick not found"}), 404

        # Brick operations
        @self.app.route('/api/session/<session_id>/brick', methods=['POST'])
        def create_brick(session_id):
            """Create a new brick"""
            data = request.get_json() or {}
            brick_type = data.get('brick_type', 'NodeShape')
            brick = self.backend.brick_core.create_brick(brick_type)
            return jsonify({"status": "success", "data": brick.to_dict()})
        
        @self.app.route('/api/session/<session_id>/brick', methods=['GET'])
        def get_current_brick(session_id):
            """Get current brick"""
            brick = self.backend.brick_core.current_brick
            return jsonify({"status": "success", "data": brick.to_dict() if brick else {}})
        
        @self.app.route('/api/session/<session_id>/brick', methods=['PUT'])
        def update_current_brick(session_id):
            """Update fields on the current brick"""
            brick = self.backend.brick_core.current_brick
            if not brick:
                return jsonify({"status": "error", "message": "No brick loaded"}), 400
            data = request.get_json() or {}
            self.backend.brick_core.update_current_brick(**{k: v for k, v in data.items() if k in ('name', 'description', 'target_class', 'property_path', 'object_type', 'display_label')})
            return jsonify({"status": "success", "data": self.backend.brick_core.current_brick.to_dict()})
        
        @self.app.route('/api/session/<session_id>/brick/save', methods=['POST'])
        def save_brick(session_id):
            """Save the current brick via brick_core"""
            brick = self.backend.brick_core.current_brick
            if not brick:
                return jsonify({"status": "error", "message": "No brick loaded"}), 400
            ok = self.backend.brick_core.save_brick(brick)
            if ok:
                return jsonify({"status": "success", "message": "Brick saved"})
            return jsonify({"status": "error", "message": "Save failed — check name, target class / property path"}), 400
        
        @self.app.route('/api/session/<session_id>/brick/load/<brick_id>', methods=['POST'])
        def load_brick(session_id, brick_id):
            """Load a brick into the shared brick_core (and session if present)"""
            brick = self.backend.brick_core.load_brick(brick_id)
            if not brick:
                return jsonify({"status": "error", "message": f"Brick '{brick_id}' not found"}), 404
            backend_session = self.backend.get_session(session_id)
            if backend_session:
                backend_session.editor_backend.current_brick = brick
            return jsonify({"status": "success", "data": brick.to_dict()})
        
        # Property operations
        @self.app.route('/api/session/<session_id>/brick/properties', methods=['POST'])
        def add_property(session_id):
            """Add property to current brick"""
            backend_session = self.backend.get_session(session_id)
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404
            
            data = request.get_json()
            if not data:
                return jsonify({
                    "status": "error",
                    "message": "No property data provided"
                }), 400
            
            # Convert form data into LeafProperty format and append to leaf_properties
            prop_name = data.get('name')
            if not prop_name:
                return jsonify({"status": "error", "message": "Property name required"}), 400

            brick = self.backend.brick_core.current_brick
            if not brick:
                return jsonify({"status": "error", "message": "No brick loaded"}), 400

            # Build a LeafProperty-compatible dict
            leaf = {
                "path": data.get('property_path', ''),
                "label": prop_name,
                "datatype": data.get('datatype', None),
                "node_kind": None,
                "in_values": [],
                "has_value": None,
                "min_count": int(data['min_count']) if data.get('min_count') not in (None, '') else 0,
                "max_count": int(data['max_count']) if data.get('max_count') not in (None, '') else None,
                "description": data.get('description', ''),
                "min_inclusive": float(data['min_inclusive']) if data.get('min_inclusive') not in (None, '') else None,
                "max_inclusive": float(data['max_inclusive']) if data.get('max_inclusive') not in (None, '') else None,
                "single_line": None,
            }
            if data.get('pattern'):
                leaf['pattern'] = data['pattern']
            if data.get('min_length') not in (None, ''):
                leaf['min_length'] = int(data['min_length'])
            if data.get('max_length') not in (None, ''):
                leaf['max_length'] = int(data['max_length'])
            if data.get('in_values'):
                leaf['in_values'] = [v.strip().strip('"') for v in data['in_values'].split(',') if v.strip()]
            if data.get('has_value'):
                leaf['has_value'] = data['has_value']
            if data.get('language_in'):
                leaf['language_in'] = data['language_in']
            if data.get('unique_lang'):
                leaf['unique_lang'] = bool(data['unique_lang'])

            brick.leaf_properties.append(leaf)
            brick.update_timestamp()

            return jsonify({
                "status": "success",
                "message": f"Property '{prop_name}' added successfully",
                "data": brick.to_dict()
            })
        
        @self.app.route('/api/session/<session_id>/brick/properties/<property_name>', methods=['DELETE'])
        def remove_property(session_id, property_name):
            """Remove property from current brick"""
            backend_session = self.backend.get_session(session_id)
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404
            
            # Remove property from current brick (leaf_properties and legacy dict)
            brick = self.backend.brick_core.current_brick
            if brick:
                brick.leaf_properties = [
                    p for p in brick.leaf_properties
                    if (p.get('label') or p.get('path', '').split(':')[-1]) != property_name
                ]
                brick.properties.pop(property_name, None)
                brick.update_timestamp()
            return jsonify({
                "status": "success",
                "message": f"Property '{property_name}' removed successfully"
            })
        
        # Constraint operations
        @self.app.route('/api/session/<session_id>/brick/properties/<property_name>/constraints', methods=['POST'])
        def add_constraint(session_id, property_name):
            """Add constraint to a property"""
            backend_session = self.backend.get_session(session_id)
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404
            
            data = request.get_json()
            if not data:
                return jsonify({
                    "status": "error",
                    "message": "No constraint data provided"
                }), 400
            
            constraint_type = data.get('constraint_type', 'minLength')
            value = data.get('value', '')
            
            constraint_data = {
                'constraint_type': constraint_type,
                'value': value,
                'name': constraint_type
            }
            
            # Map of constraint types to flat property keys (supports both sh: prefixed and bare)
            flat_key_mapping = {
                'sh:minCount': 'min_count',
                'minCount': 'min_count',
                'sh:maxCount': 'max_count',
                'maxCount': 'max_count',
                'sh:minLength': 'min_length',
                'minLength': 'min_length',
                'sh:maxLength': 'max_length',
                'maxLength': 'max_length',
                'sh:pattern': 'pattern',
                'pattern': 'pattern',
                'sh:minInclusive': 'min_inclusive',
                'minInclusive': 'min_inclusive',
                'sh:maxInclusive': 'max_inclusive',
                'maxInclusive': 'max_inclusive',
                'sh:minExclusive': 'min_exclusive',
                'minExclusive': 'min_exclusive',
                'sh:maxExclusive': 'max_exclusive',
                'maxExclusive': 'max_exclusive',
                'sh:hasValue': 'has_value',
                'hasValue': 'has_value',
            }
            
            # Add/update constraint in leaf_properties (modern format)
            brick = self.backend.brick_core.current_brick
            if brick and brick.leaf_properties:
                # Find property by name/label/path
                for prop in brick.leaf_properties:
                    prop_name_match = prop.get('label') == property_name or prop.get('name') == property_name
                    prop_path_match = prop.get('path', '').split(':')[-1] == property_name
                    if prop_name_match or prop_path_match:
                        # Save to flat key for chip display
                        flat_key = flat_key_mapping.get(constraint_type)
                        if flat_key:
                            if constraint_type in ['sh:minCount', 'sh:maxCount', 'sh:minLength', 'sh:maxLength',
                                                   'minCount', 'maxCount', 'minLength', 'maxLength']:
                                try:
                                    prop[flat_key] = int(value)
                                except ValueError:
                                    prop[flat_key] = value
                            else:
                                prop[flat_key] = value
                        
                        # Update or add to constraints array (to avoid duplicates)
                        if 'constraints' not in prop:
                            prop['constraints'] = []
                        constraints = prop['constraints']
                        existing_idx = None
                        for i, c in enumerate(constraints):
                            if c.get('constraint_type') == constraint_type:
                                existing_idx = i
                                break
                        if existing_idx is not None:
                            constraints[existing_idx] = constraint_data
                        else:
                            constraints.append(constraint_data)
                        break
            
            # Also try legacy properties dict for backward compatibility
            if brick and property_name in brick.properties:
                if 'constraints' not in brick.properties[property_name]:
                    brick.properties[property_name]['constraints'] = []
                brick.properties[property_name]['constraints'].append(constraint_data)
            
            return jsonify({
                "status": "success",
                "message": "Constraint added successfully"
            })
        
        @self.app.route('/api/session/<session_id>/brick/properties/<property_name>/constraints/<int:index>', methods=['PUT'])
        def update_constraint(session_id, property_name, index):
            """Update constraint at specific index"""
            backend_session = self.backend.get_session(session_id)
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404
            
            data = request.get_json()
            if not data:
                return jsonify({
                    "status": "error",
                    "message": "No constraint data provided"
                }), 400
            
            constraint_type = data.get('constraint_type', 'minLength')
            value = data.get('value', '')
            
            constraint_data = {
                'constraint_type': constraint_type,
                'value': value,
                'name': constraint_type
            }
            
            # Map of constraint types to flat property keys (supports both sh: prefixed and bare)
            flat_key_mapping = {
                'sh:minCount': 'min_count',
                'minCount': 'min_count',
                'sh:maxCount': 'max_count',
                'maxCount': 'max_count',
                'sh:minLength': 'min_length',
                'minLength': 'min_length',
                'sh:maxLength': 'max_length',
                'maxLength': 'max_length',
                'sh:pattern': 'pattern',
                'pattern': 'pattern',
                'sh:minInclusive': 'min_inclusive',
                'minInclusive': 'min_inclusive',
                'sh:maxInclusive': 'max_inclusive',
                'maxInclusive': 'max_inclusive',
                'sh:minExclusive': 'min_exclusive',
                'minExclusive': 'min_exclusive',
                'sh:maxExclusive': 'max_exclusive',
                'maxExclusive': 'max_exclusive',
                'sh:hasValue': 'has_value',
                'hasValue': 'has_value',
            }
            
            # Update constraint in leaf_properties (modern format)
            brick = self.backend.brick_core.current_brick
            if brick and brick.leaf_properties:
                for prop in brick.leaf_properties:
                    prop_name_match = prop.get('label') == property_name or prop.get('name') == property_name
                    prop_path_match = prop.get('path', '').split(':')[-1] == property_name
                    if prop_name_match or prop_path_match:
                        # Update constraints array if it exists
                        constraints = prop.get('constraints', [])
                        if isinstance(constraints, list) and 0 <= index < len(constraints):
                            old_ct = constraints[index].get('constraint_type', '')
                            # Remove old flat key
                            old_flat_key = flat_key_mapping.get(old_ct)
                            if old_flat_key and old_flat_key in prop:
                                del prop[old_flat_key]
                            # Update constraint in array
                            constraints[index] = constraint_data
                        
                        # Set new flat key
                        new_flat_key = flat_key_mapping.get(constraint_type)
                        if new_flat_key:
                            if constraint_type in ['sh:minCount', 'sh:maxCount', 'sh:minLength', 'sh:maxLength',
                                                   'minCount', 'maxCount', 'minLength', 'maxLength']:
                                try:
                                    prop[new_flat_key] = int(value)
                                except ValueError:
                                    prop[new_flat_key] = value
                            else:
                                prop[new_flat_key] = value
                        break
            
            # Also update legacy properties dict for backward compatibility
            if brick and property_name in brick.properties:
                constraints = brick.properties[property_name].get('constraints', [])
                if 0 <= index < len(constraints):
                    constraints[index] = constraint_data
            
            return jsonify({
                "status": "success",
                "message": "Constraint updated successfully"
            })
        
        @self.app.route('/api/session/<session_id>/brick/properties/<property_name>/constraints/<int:index>', methods=['DELETE'])
        def remove_constraint(session_id, property_name, index):
            """Remove constraint at specific index or by type if constraint_type param provided"""
            backend_session = self.backend.get_session(session_id)
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404
            
            # Map of constraint types to flat property keys (supports both sh: prefixed and bare)
            flat_key_mapping = {
                'sh:minCount': 'min_count',
                'minCount': 'min_count',
                'sh:maxCount': 'max_count',
                'maxCount': 'max_count',
                'sh:minLength': 'min_length',
                'minLength': 'min_length',
                'sh:maxLength': 'max_length',
                'maxLength': 'max_length',
                'sh:pattern': 'pattern',
                'pattern': 'pattern',
                'sh:minInclusive': 'min_inclusive',
                'minInclusive': 'min_inclusive',
                'sh:maxInclusive': 'max_inclusive',
                'maxInclusive': 'max_inclusive',
                'sh:minExclusive': 'min_exclusive',
                'minExclusive': 'min_exclusive',
                'sh:maxExclusive': 'max_exclusive',
                'maxExclusive': 'max_exclusive',
                'sh:hasValue': 'has_value',
                'hasValue': 'has_value',
            }
            
            # Check for constraint_type query param (for inline constraints)
            constraint_type = request.args.get('constraint_type')
            
            # Remove constraint from leaf_properties (modern format)
            brick = self.backend.brick_core.current_brick
            removed_ct = None
            if brick and brick.leaf_properties:
                for prop in brick.leaf_properties:
                    prop_name_match = prop.get('label') == property_name or prop.get('name') == property_name
                    prop_path_match = prop.get('path', '').split(':')[-1] == property_name
                    if prop_name_match or prop_path_match:
                        if constraint_type:
                            # Delete by constraint type (for inline constraints)
                            removed_ct = constraint_type
                            # Also remove from constraints array if present
                            constraints = prop.get('constraints', [])
                            if isinstance(constraints, list):
                                for i, c in enumerate(constraints):
                                    if c.get('constraint_type') == constraint_type:
                                        constraints.pop(i)
                                        break
                        else:
                            # Delete by index
                            constraints = prop.get('constraints', [])
                            if isinstance(constraints, list) and 0 <= index < len(constraints):
                                removed = constraints.pop(index)
                                removed_ct = removed.get('constraint_type', '')
                            else:
                                # Fallback: find by position in extracted constraints
                                present_keys = [(ct, fk) for ct, fk in flat_key_mapping.items() if fk in prop]
                                if 0 <= index < len(present_keys):
                                    removed_ct = present_keys[index][0]
                        
                        # Remove only the specific flat key for this constraint type
                        flat_key = flat_key_mapping.get(removed_ct)
                        if flat_key and flat_key in prop:
                            del prop[flat_key]
                        break
            
            # Also try legacy properties dict for backward compatibility
            if brick and property_name in brick.properties:
                constraints = brick.properties[property_name].get('constraints', [])
                if 0 <= index < len(constraints):
                    constraints.pop(index)
            return jsonify({
                "status": "success",
                "message": "Constraint removed successfully"
            })
        
        # Target class operations
        @self.app.route('/api/session/<session_id>/brick/target-class', methods=['PUT'])
        def set_target_class(session_id):
            """Set target class for current brick"""
            backend_session = self.backend.get_session(session_id)
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404
            
            data = request.get_json() or {}
            class_uri = data.get('class_uri')
            
            if not class_uri:
                return jsonify({
                    "status": "error",
                    "message": "No class URI provided"
                }), 400
            
            backend_session.editor_backend.set_target_class(class_uri)
            
            return jsonify({
                "status": "success",
                "message": "Target class set successfully"
            })
        
        # Ontology operations
        @self.app.route('/api/session/<session_id>/ontologies', methods=['GET'])
        def get_ontologies(session_id):
            """Get available ontologies for a session"""
            backend_session = self.backend.get_session(session_id)
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404
            
            ontologies = backend_session.editor_backend.ontology_manager.ontologies
            
            return jsonify({
                "status": "success",
                "data": ontologies
            })
        
        @self.app.route('/api/session/<session_id>/ontologies/<ontology_name>/classes', methods=['GET'])
        def get_ontology_classes(session_id, ontology_name):
            """Get classes from specific ontology for a session"""
            backend_session = self.backend.get_session(session_id)
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404
            
            ontologies = backend_session.editor_backend.ontology_manager.ontologies
            if ontology_name in ontologies:
                raw = ontologies[ontology_name].get('classes', {})
                items = [
                    {"uri": uri, "label": meta.get("name", uri.split("#")[-1].split("/")[-1]), "comment": meta.get("comment", "")}
                    for uri, meta in (raw.items() if isinstance(raw, dict) else [])
                ]
                return jsonify({"status": "success", "data": sorted(items, key=lambda x: x["label"].lower())})
            else:
                return jsonify({
                    "status": "error",
                    "message": "Ontology not found"
                }), 404
        
        @self.app.route('/api/session/<session_id>/ontologies/<ontology_name>/properties', methods=['GET'])
        def get_ontology_properties(session_id, ontology_name):
            """Get properties from specific ontology for a session"""
            backend_session = self.backend.get_session(session_id)
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404
            
            ontologies = backend_session.editor_backend.ontology_manager.ontologies
            if ontology_name in ontologies:
                raw = ontologies[ontology_name].get('properties', {})
                items = [
                    {"uri": uri, "label": meta.get("name", uri.split("#")[-1].split("/")[-1]), "comment": meta.get("comment", ""), "domain": meta.get("domain", ""), "range": meta.get("range", "")}
                    for uri, meta in (raw.items() if isinstance(raw, dict) else [])
                ]
                return jsonify({"status": "success", "data": sorted(items, key=lambda x: x["label"].lower())})
            else:
                return jsonify({
                    "status": "error",
                    "message": "Ontology not found"
                }), 404
        
        # Event history
        @self.app.route('/api/session/<session_id>/events', methods=['GET'])
        def get_session_events(session_id):
            """Get event history for session"""
            backend_session = self.backend.get_session(session_id)
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404
            
            event_type = request.args.get('event_type')
            events = self.backend.get_event_history(session_id, 
                EventType(event_type) if event_type else None)
            
            return jsonify({
                "status": "success",
                "data": [event.to_dict() for event in events]
            })
        
        # Session management endpoints
        @self.app.route('/api/sessions', methods=['GET'])
        def get_all_sessions():
            """Get all active sessions"""
            sessions = self.backend.get_all_sessions()
            
            return jsonify({
                "status": "success",
                "data": sessions
            })
        
        @self.app.route('/api/sessions/stats', methods=['GET'])
        def get_session_stats():
            """Get session statistics"""
            stats = self.backend.get_session_stats()
            
            return jsonify({
                "status": "success",
                "data": stats
            })
        
        # Health check
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            })

        # SHACL import
        @self.app.route('/api/import/shacl', methods=['POST'])
        def import_shacl():
            """
            Import SHACL NodeShapes from an uploaded .ttl file.

            Multipart form fields:
              file     – the .ttl file (required)
              library  – target library name (optional; defaults to filename stem)
              prefix   – prepended to library name when no library given (optional)
            """
            from brick_app_v2.core.shacl_importer import SHACLImporter
            from flask import request as _req

            if 'file' not in _req.files:
                return jsonify({"status": "error", "message": "No file uploaded"}), 400

            uploaded = _req.files['file']
            if not uploaded.filename:
                return jsonify({"status": "error", "message": "Empty filename"}), 400

            prefix  = _req.form.get('prefix', 'imported')
            stem    = uploaded.filename.rsplit('.', 1)[0]
            library = _req.form.get('library') or f"{prefix}_{stem}"

            turtle_text = uploaded.read().decode('utf-8', errors='replace')

            try:
                importer = SHACLImporter(self.backend.brick_core.repository_path)
                result   = importer.import_turtle_string(
                    turtle_text, library, source_name=uploaded.filename
                )
            except ImportError as e:
                return jsonify({"status": "error", "message": str(e)}), 500

            if result.errors:
                return jsonify({
                    "status": "error",
                    "message": result.errors[0],
                    "data": result.to_dict(),
                }), 422

            return jsonify({
                "status": "success",
                "data": {**result.to_dict(), "library": library},
            })
        
        # Ontology download endpoints (session-independent, affect shared cache)
        @self.app.route('/api/ontologies/search', methods=['POST'])
        def search_ontologies():
            """Search LOV for ontologies by keyword"""
            import urllib.request
            import urllib.parse

            data = request.get_json() or {}
            query = data.get('query', '').strip()
            if not query:
                return jsonify({"status": "error", "message": "No query provided"}), 400

            url = (
                "https://lov.linkeddata.es/dataset/lov/api/v2/vocabulary/search"
                f"?q={urllib.parse.quote(query)}"
            )
            req = urllib.request.Request(url, headers={'Accept': 'application/json'})
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    raw = json.loads(resp.read().decode('utf-8'))
            except Exception as e:
                return jsonify({"status": "error", "message": f"LOV search failed: {e}"}), 502

            results = []
            for item in raw.get('results', []):
                vocab = item.get('_source', {})
                prefix = vocab.get('prefix', '')
                title = ''
                for key in vocab.keys():
                    if 'title' in key.lower():
                        title = vocab.get(key)
                        break
                results.append({
                    'prefix': prefix,
                    'title': title or prefix,
                    'uri': vocab.get('uri', ''),
                })

            return jsonify({"status": "success", "data": results})

        @self.app.route('/api/ontologies/download', methods=['POST'])
        def download_ontology():
            """
            Download an ontology into the shared cache.

            JSON body (one of):
              { "prefix": "<lov_prefix>" }          – resolves download URL via LOV
              { "url": "<direct_url>", "name": "<filename_stem>" }
            """
            import urllib.request
            import urllib.error

            data = request.get_json() or {}
            prefix = data.get('prefix', '').strip()
            direct_url = data.get('url', '').strip()
            name = data.get('name', '').strip()

            # Resolve via LOV if only prefix given
            if prefix and not direct_url:
                info_url = (
                    "https://lov.linkeddata.es/dataset/lov/api/v2/vocabulary/info"
                    f"?vocab={urllib.parse.quote(prefix)}"
                )
                req = urllib.request.Request(info_url, headers={'Accept': 'application/json'})
                try:
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        vocab_info = json.loads(resp.read().decode('utf-8'))
                except Exception as e:
                    return jsonify({"status": "error", "message": f"LOV info lookup failed: {e}"}), 502

                # Try graphs -> distributions first
                download_url = None
                for graph in vocab_info.get('graphs', []):
                    for dist in graph.get('distributions', []):
                        download_url = dist.get('downloadURL')
                        if download_url:
                            break
                    if download_url:
                        break
                # Fallback: versions fileURL
                if not download_url:
                    versions = vocab_info.get('versions', [])
                    if versions:
                        download_url = versions[0].get('fileURL')
                # Fallback: homepage
                if not download_url:
                    download_url = vocab_info.get('homepage')

                if not download_url:
                    return jsonify({
                        "status": "error",
                        "message": "Could not find a download URL for this ontology in LOV"
                    }), 422
                name = name or prefix
                direct_url = download_url

            if not direct_url:
                return jsonify({"status": "error", "message": "Provide 'prefix' or 'url'"}), 400
            if not name:
                name = direct_url.rstrip('/').split('/')[-1].rsplit('.', 1)[0] or "ontology"

            # Fetch ontology
            req = urllib.request.Request(
                direct_url,
                headers={
                    'Accept': (
                        'application/rdf+xml,text/turtle;q=0.9,'
                        'application/n-triples;q=0.8,*/*;q=0.5'
                    ),
                    'User-Agent': 'Mozilla/5.0 (compatible; BrickApp/2.0; ontology downloader)',
                }
            )
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    content = resp.read()
                    content_type = resp.headers.get('Content-Type', '')
                    final_url = resp.url if hasattr(resp, 'url') else direct_url
            except urllib.error.URLError as e:
                return jsonify({"status": "error", "message": f"Download failed: {e}"}), 502

            # Reject HTML responses
            if content[:200].lstrip().startswith(b'<!') or b'<html' in content[:200].lower():
                return jsonify({
                    "status": "error",
                    "message": (
                        "Server returned an HTML page instead of RDF data. "
                        "Try a direct .rdf/.ttl download URL."
                    )
                }), 422

            # Determine extension
            if 'turtle' in content_type or final_url.endswith('.ttl') or direct_url.endswith('.ttl'):
                ext = '.ttl'
            elif 'xml' in content_type or 'rdf' in content_type or final_url.endswith('.rdf') or direct_url.endswith('.rdf'):
                ext = '.rdf'
            elif content.lstrip().startswith(b'@') or content.lstrip().startswith(b'<http'):
                ext = '.ttl'
            elif content.lstrip().startswith(b'<?xml') or content.lstrip().startswith(b'<rdf'):
                ext = '.rdf'
            else:
                ext = '.rdf'

            # Persist to cache
            from core.ontology_manager import OntologyManager
            om = OntologyManager()
            from pathlib import Path as _P
            cache_dir = _P(om.cache_path)
            cache_dir.mkdir(parents=True, exist_ok=True)
            out_file = cache_dir / f"{name}{ext}"
            out_file.write_bytes(content)

            # Reload all session ontology managers
            for sess in self.backend.session_manager.sessions.values():
                try:
                    sess.editor_backend.ontology_manager.load_cached_ontologies()
                except Exception:
                    pass

            return jsonify({
                "status": "success",
                "message": f"Ontology '{name}' downloaded and cached.",
                "data": {"name": name, "file": str(out_file), "size_bytes": len(content)},
            })

        # Pattern presets endpoint - serves from shared_libraries/pattern_presets.json
        @self.app.route('/api/pattern-presets', methods=['GET'])
        def get_pattern_presets():
            """Get pattern presets from shared_libraries/pattern_presets.json"""
            try:
                from common import shared_library_manager
                presets_file = shared_library_manager.base_path / "pattern_presets.json"
                
                if not presets_file.exists():
                    return jsonify({
                        "status": "error",
                        "message": "Pattern presets file not found"
                    }), 404
                
                with open(presets_file, 'r') as f:
                    presets_data = json.load(f)
                
                # Extract patterns from international section
                patterns = []
                if "presets" in presets_data and "international" in presets_data["presets"]:
                    patterns = presets_data["presets"]["international"].get("patterns", [])
                
                return jsonify({
                    "status": "success",
                    "data": patterns,
                    "version": presets_data.get("version", "unknown")
                })
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": f"Failed to load pattern presets: {str(e)}"
                }), 500
    
    def _setup_error_handlers(self):
        """Setup error handlers"""
        
        @self.app.errorhandler(HTTPException)
        def handle_http_exception(e):
            """Handle HTTP exceptions"""
            return jsonify({
                "status": "error",
                "message": str(e.description),
                "code": e.code
            }), e.code
        
        @self.app.errorhandler(Exception)
        def handle_general_exception(e):
            """Handle general exceptions"""
            return jsonify({
                "status": "error",
                "message": str(e),
                "code": 500
            }), 500
    
    def run(self, debug=True):
        """Run the Flask application"""
        print(f"Starting SHACL Brick Web API on http://{self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=debug)


def create_web_api(backend: MultiTenantBackend, host='localhost', port=5000):
    """Factory function to create web API instance"""
    return BrickWebAPI(backend, host, port)


if __name__ == "__main__":
    # Test the API standalone
    from ..core.multi_tenant_backend import MultiTenantBackend
    
    backend = MultiTenantBackend()
    api = BrickWebAPI(backend)
    api.run()
