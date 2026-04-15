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

from ..core.multi_tenant_backend import MultiTenantBackend
from ..core.abstract_events import EventType, ClientType


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
            result = self.backend.get_brick_libraries()
            return jsonify(result)
        
        @self.app.route('/api/libraries/<library_name>/bricks', methods=['GET'])
        def get_library_bricks(library_name):
            """Get bricks from a specific library"""
            result = self.backend.get_library_bricks(library_name)
            return jsonify(result)
        
        @self.app.route('/api/bricks', methods=['GET'])
        def get_all_bricks():
            """Get all bricks from all libraries"""
            result = self.backend.get_all_bricks()
            return jsonify(result)
        
        # Brick operations (session-specific)
        @self.app.route('/api/session/<session_id>/brick', methods=['POST'])
        def create_brick(session_id):
            """Create a new brick in session"""
            backend_session = self.backend.get_session(session_id)
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404
            
            data = request.get_json() or {}
            brick_type = data.get('brick_type', 'NodeShape')
            
            brick_data = backend_session.editor_backend.create_new_brick(brick_type)
            
            return jsonify({
                "status": "success",
                "data": brick_data
            })
        
        @self.app.route('/api/session/<session_id>/brick', methods=['GET'])
        def get_current_brick(session_id):
            """Get current brick from session"""
            backend_session = self.backend.get_session(session_id)
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404
            
            brick_data = backend_session.editor_backend.get_current_brick()
            
            return jsonify({
                "status": "success",
                "data": brick_data
            })
        
        @self.app.route('/api/session/<session_id>/brick', methods=['PUT'])
        def update_current_brick(session_id):
            """Update current brick in session"""
            backend_session = self.backend.get_session(session_id)
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404
            
            data = request.get_json() or {}
            brick_data = backend_session.editor_backend.get_current_brick()
            
            # Update fields
            if 'name' in data:
                brick_data['name'] = data['name']
            if 'target_class' in data:
                brick_data['target_class'] = data['target_class']
            if 'description' in data:
                brick_data['description'] = data['description']
            if 'object_type' in data:
                brick_data['object_type'] = data['object_type']
            
            backend_session.editor_backend.set_current_brick(brick_data)
            
            return jsonify({
                "status": "success",
                "data": brick_data
            })
        
        @self.app.route('/api/session/<session_id>/brick/save', methods=['POST'])
        def save_brick(session_id):
            """Save current brick"""
            backend_session = self.backend.get_session(session_id)
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404
            
            data = request.get_json() or {}
            brick_data = data.get('brick_data')
            
            if not brick_data:
                brick_data = backend_session.editor_backend.get_current_brick()
            
            success, message = backend_session.editor_backend.save_brick(brick_data)
            
            if success:
                return jsonify({
                    "status": "success",
                    "message": "Brick saved successfully"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": message
                }), 400
        
        @self.app.route('/api/session/<session_id>/brick/load/<brick_id>', methods=['POST'])
        def load_brick(session_id, brick_id):
            """Load a brick into session"""
            backend_session = self.backend.get_session(session_id)
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404
            
            brick_data = backend_session.editor_backend.load_brick(brick_id)
            if brick_data:
                return jsonify({
                    "status": "success",
                    "data": brick_data
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Brick not found"
                }), 404
        
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
            
            success = backend_session.editor_backend.add_property_to_current_brick(data)
            
            if success:
                return jsonify({
                    "status": "success",
                    "message": "Property added successfully"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Failed to add property"
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
            
            success = backend_session.editor_backend.remove_property_from_current_brick(property_name)
            
            if success:
                return jsonify({
                    "status": "success",
                    "message": "Property removed successfully"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Failed to remove property"
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
        @self.app.route('/api/ontologies', methods=['GET'])
        def get_ontologies():
            """Get available ontologies"""
            backend_session = self.backend.get_qt_session()
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "No session available"
                }), 500
            
            ontologies = backend_session.editor_backend.ontology_manager.ontologies
            
            return jsonify({
                "status": "success",
                "data": ontologies
            })
        
        @self.app.route('/api/ontologies/<ontology_name>/classes', methods=['GET'])
        def get_ontology_classes(ontology_name):
            """Get classes from specific ontology"""
            backend_session = self.backend.get_qt_session()
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "No session available"
                }), 500
            
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
        
        @self.app.route('/api/ontologies/<ontology_name>/properties', methods=['GET'])
        def get_ontology_properties(ontology_name):
            """Get properties from specific ontology"""
            backend_session = self.backend.get_qt_session()
            if not backend_session:
                return jsonify({
                    "status": "error",
                    "message": "No session available"
                }), 500
            
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
