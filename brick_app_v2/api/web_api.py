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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../business'))

from core.multi_tenant_backend import MultiTenantBackend
from core.abstract_events import EventType, ClientType
from brick_operations import brick_business_logic


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
            self.backend.brick_core.update_current_brick(**{k: v for k, v in data.items() if k in ('name', 'description', 'target_class', 'property_path', 'object_type')})
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
            
            success, message = brick_business_logic.add_property(data)
            
            if success:
                return jsonify({
                    "status": "success",
                    "message": "Property added successfully"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": message
                }), 400
        
        @self.app.route('/api/session/<session_id>/brick/properties/<property_name>', methods=['DELETE'])
        def remove_property(session_id, property_name):
            """Remove property from current brick"""
            backend_session = self.backend.get_session(session_id)
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404
            
            success, message = brick_business_logic.remove_property(property_name)
            
            if success:
                return jsonify({
                    "status": "success",
                    "message": "Property removed successfully"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": message
                }), 400
        
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
            
            constraint_data = {
                'constraint_type': data.get('constraint_type', 'minLength'),
                'value': data.get('value', ''),
                'name': data.get('constraint_type', 'minLength')
            }
            
            success, message = brick_business_logic.add_constraint(
                property_name, constraint_data
            )
            
            if success:
                return jsonify({
                    "status": "success",
                    "message": "Constraint added successfully"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": message
                }), 400
        
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
            
            constraint_data = {
                'constraint_type': data.get('constraint_type', 'minLength'),
                'value': data.get('value', ''),
                'name': data.get('constraint_type', 'minLength')
            }
            
            success, message = brick_business_logic.update_constraint(
                property_name, index, constraint_data
            )
            
            if success:
                return jsonify({
                    "status": "success",
                    "message": "Constraint updated successfully"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": message
                }), 400
        
        @self.app.route('/api/session/<session_id>/brick/properties/<property_name>/constraints/<int:index>', methods=['DELETE'])
        def remove_constraint(session_id, property_name, index):
            """Remove constraint at specific index"""
            backend_session = self.backend.get_session(session_id)
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404
            
            success, message = brick_business_logic.remove_constraint(
                property_name, index
            )
            
            if success:
                return jsonify({
                    "status": "success",
                    "message": "Constraint removed successfully"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": message
                }), 400
        
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
                return jsonify({
                    "status": "success",
                    "data": ontologies[ontology_name].get('classes', [])
                })
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
                return jsonify({
                    "status": "success",
                    "data": ontologies[ontology_name].get('properties', [])
                })
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
        
        # Pattern presets endpoint - serves from shared_libraries/pattern_presets.json
        @self.app.route('/api/pattern-presets', methods=['GET'])
        def get_pattern_presets():
            """Get pattern presets from shared_libraries/pattern_presets.json"""
            try:
                from pathlib import Path
                # Load from external shared_libraries
                project_root = Path(__file__).resolve().parent.parent.parent
                presets_file = project_root.parent / "shared_libraries" / "pattern_presets.json"
                
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
