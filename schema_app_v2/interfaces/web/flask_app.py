"""
Flask Web Application
Web interface for schema construction with multi-tenant backend support
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sys
import os

# Add core modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from schema_core import SchemaCore, Schema
from flow_engine import FlowEngine, FlowType
from brick_integration import BrickIntegration
from multi_tenant_backend import MultiTenantBackend


def create_app(schema_repository_path: str = None,
               brick_repository_path: str = None):
    """Create Flask application with multi-tenant backend"""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for web interface
    
    # Initialize multi-tenant backend
    backend = MultiTenantBackend(schema_repository_path, brick_repository_path)
    
    # Create a session for web requests
    web_session_id = backend.create_session("web", user_info={"client": "Web Interface"})
    web_session = backend.get_session(web_session_id)
    
    # Store backend in app context
    app.config['BACKEND'] = backend
    app.config['WEB_SESSION_ID'] = web_session_id
    
    # API Routes
    
    @app.route('/')
    def index():
        """Main page"""
        return render_template('index.html')
    
    @app.route('/api/schemas', methods=['GET'])
    def get_schemas():
        """Get all schemas"""
        library = request.args.get('library')
        schemas = web_session.schema_core.get_all_schemas(library)
        return jsonify([schema.to_dict() for schema in schemas])
    
    @app.route('/api/schemas', methods=['POST'])
    def create_schema():
        """Create a new schema"""
        data = request.get_json()
        
        schema = web_session.schema_core.create_schema(
            name=data.get('name', ''),
            description=data.get('description', ''),
            root_brick_id=data.get('root_brick_id', '')
        )
        web_session.current_schema = schema
        web_session._emit_event('schema_created', schema.to_dict())
        
        return jsonify(schema.to_dict()), 201
    
    @app.route('/api/schemas/<schema_id>', methods=['GET'])
    def get_schema(schema_id):
        """Get a specific schema"""
        library = request.args.get('library')
        schema = web_session.schema_core.load_schema(schema_id, library)
        
        if schema:
            web_session.current_schema = schema
            web_session._emit_event('schema_loaded', schema.to_dict())
            return jsonify(schema.to_dict())
        else:
            return jsonify({'error': 'Schema not found'}), 404
    
    @app.route('/api/schemas/<schema_id>', methods=['PUT'])
    def update_schema(schema_id):
        """Update a schema"""
        library = request.args.get('library')
        schema = web_session.schema_core.load_schema(schema_id, library)
        
        if not schema:
            return jsonify({'error': 'Schema not found'}), 404
        
        data = request.get_json()
        
        # Update schema fields
        if 'name' in data:
            schema.name = data['name']
        if 'description' in data:
            schema.description = data['description']
        if 'root_brick_id' in data:
            schema.root_brick_id = data['root_brick_id']
        if 'component_brick_ids' in data:
            schema.component_brick_ids = data['component_brick_ids']
        
        schema.update_timestamp()
        web_session._emit_event('schema_updated', schema.to_dict())
        
        # Save schema
        if web_session.schema_core.save_schema(schema):
            web_session._emit_event('schema_saved', schema.to_dict())
            return jsonify(schema.to_dict())
        else:
            return jsonify({'error': 'Failed to save schema'}), 500
    
    @app.route('/api/schemas/<schema_id>', methods=['DELETE'])
    def delete_schema(schema_id):
        """Delete a schema"""
        library = request.args.get('library')
        
        if web_session.schema_core.delete_schema(schema_id, library):
            web_session._emit_event('schema_deleted', {'schema_id': schema_id})
            return jsonify({'message': 'Schema deleted'})
        else:
            return jsonify({'error': 'Failed to delete schema'}), 500
    
    @app.route('/api/schemas/<schema_id>/components', methods=['POST'])
    def add_component(schema_id):
        """Add component brick to schema"""
        library = request.args.get('library')
        data = request.get_json()
        brick_id = data.get('brick_id')
        
        schema = web_session.schema_core.load_schema(schema_id, library)
        if not schema:
            return jsonify({'error': 'Schema not found'}), 404
        
        if brick_id not in schema.component_brick_ids:
            schema.component_brick_ids.append(brick_id)
            schema.update_timestamp()
            web_session._emit_event('component_added', {'brick_id': brick_id})
            web_session.schema_core.save_schema(schema)
            return jsonify({'message': 'Component added'})
        else:
            return jsonify({'error': 'Component already exists'}), 400
    
    @app.route('/api/schemas/<schema_id>/components/<brick_id>', methods=['DELETE'])
    def remove_component(schema_id, brick_id):
        """Remove component brick from schema"""
        library = request.args.get('library')
        
        schema = web_session.schema_core.load_schema(schema_id, library)
        if not schema:
            return jsonify({'error': 'Schema not found'}), 404
        
        if brick_id in schema.component_brick_ids:
            schema.component_brick_ids.remove(brick_id)
            schema.update_timestamp()
            web_session._emit_event('component_removed', {'brick_id': brick_id})
            web_session.schema_core.save_schema(schema)
            return jsonify({'message': 'Component removed'})
        else:
            return jsonify({'error': 'Component not found'}), 404
    
    @app.route('/api/bricks', methods=['GET'])
    def get_bricks():
        """Get available bricks"""
        library = request.args.get('library')
        search = request.args.get('search')
        
        if search:
            bricks = web_session.brick_integration.search_bricks(search, library)
        else:
            bricks = web_session.brick_integration.get_available_bricks(library)
        
        return jsonify([brick.to_dict() for brick in bricks])
    
    @app.route('/api/bricks/<brick_id>', methods=['GET'])
    def get_brick(brick_id):
        """Get a specific brick"""
        library = request.args.get('library')
        brick = web_session.brick_integration.get_brick_by_id(brick_id, library)
        
        if brick:
            return jsonify(brick.to_dict())
        else:
            return jsonify({'error': 'Brick not found'}), 404
    
    @app.route('/api/bricks/node-shapes', methods=['GET'])
    def get_node_shapes():
        """Get NodeShape bricks (for root selection)"""
        library = request.args.get('library')
        bricks = web_session.brick_integration.get_node_shape_bricks(library)
        return jsonify([brick.to_dict() for brick in bricks])
    
    @app.route('/api/bricks/property-shapes', methods=['GET'])
    def get_property_shapes():
        """Get PropertyShape bricks (for components)"""
        library = request.args.get('library')
        bricks = web_session.brick_integration.get_property_shape_bricks(library)
        return jsonify([brick.to_dict() for brick in bricks])
    
    @app.route('/api/libraries', methods=['GET'])
    def get_libraries():
        """Get available libraries"""
        schema_libraries = web_session.schema_core.get_libraries()
        brick_libraries = web_session.brick_integration.get_brick_libraries()
        
        return jsonify({
            'schema_libraries': schema_libraries,
            'brick_libraries': brick_libraries
        })
    
    @app.route('/api/flows', methods=['POST'])
    def create_flow():
        """Create a new flow"""
        data = request.get_json()
        
        flow_type = FlowType(data.get('flow_type', 'sequential'))
        flow = web_session.flow_engine.create_flow(
            name=data.get('name', ''),
            flow_type=flow_type,
            description=data.get('description', '')
        )
        
        return jsonify(flow.to_dict()), 201
    
    @app.route('/api/flows/<flow_id>', methods=['GET'])
    def get_flow(flow_id):
        """Get a specific flow"""
        flow = web_session.flow_engine.get_flow(flow_id)
        
        if flow:
            return jsonify(flow.to_dict())
        else:
            return jsonify({'error': 'Flow not found'}), 404
    
    @app.route('/api/flows/<flow_id>/validate', methods=['POST'])
    def validate_flow(flow_id):
        """Validate a flow"""
        issues = web_session.flow_engine.validate_flow(flow_id)
        return jsonify({'issues': issues})
    
    @app.route('/api/schemas/<schema_id>/export/shacl', methods=['GET'])
    def export_shacl(schema_id):
        """Export schema as SHACL"""
        library = request.args.get('library')
        schema = web_session.schema_core.load_schema(schema_id, library)
        
        if not schema:
            return jsonify({'error': 'Schema not found'}), 404
        
        try:
            # Generate SHACL content
            shacl_lines = []
            
            # Prefixes
            shacl_lines.append("@prefix sh: <http://www.w3.org/ns/shacl#> .")
            shacl_lines.append("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .")
            shacl_lines.append("")
            
            # Add root brick SHACL
            root_brick = web_session.brick_integration.get_brick_by_id(schema.root_brick_id, library)
            if root_brick:
                root_shacl = web_session.brick_integration.export_brick_as_shacl(schema.root_brick_id, library)
                if root_shacl:
                    shacl_lines.append("# Root Brick")
                    shacl_lines.append(root_shacl)
                    shacl_lines.append("")
            
            # Add component bricks SHACL
            for brick_id in schema.component_brick_ids:
                component_shacl = web_session.brick_integration.export_brick_as_shacl(brick_id, library)
                if component_shacl:
                    shacl_lines.append(f"# Component Brick: {brick_id}")
                    shacl_lines.append(component_shacl)
                    shacl_lines.append("")
            
            shacl_content = "\n".join(shacl_lines)
            
            return shacl_content, 200, {
                'Content-Type': 'text/turtle',
                'Content-Disposition': f'attachment; filename="{schema.name}.ttl"'
            }
            
        except Exception as e:
            return jsonify({'error': f'Export failed: {str(e)}'}), 500
    
    @app.route('/api/schemas/<schema_id>/validate', methods=['POST'])
    def validate_schema(schema_id):
        """Validate a schema"""
        library = request.args.get('library')
        schema = web_session.schema_core.load_schema(schema_id, library)
        
        if not schema:
            return jsonify({'error': 'Schema not found'}), 404
        
        issues = []
        
        # Basic validation
        if not schema.name.strip():
            issues.append("Schema name is required")
        
        if not schema.root_brick_id:
            issues.append("Root brick is required")
        
        # Check root brick exists and is NodeShape
        if schema.root_brick_id:
            root_brick = web_session.brick_integration.get_brick_by_id(schema.root_brick_id, library)
            if not root_brick:
                issues.append("Root brick not found")
            elif root_brick.object_type != "NodeShape":
                issues.append("Root brick must be a NodeShape")
        
        # Check component bricks exist
        for brick_id in schema.component_brick_ids:
            brick = web_session.brick_integration.get_brick_by_id(brick_id, library)
            if not brick:
                issues.append(f"Component brick not found: {brick_id}")
        
        # Validate flow if present
        if schema.flow_config:
            flow_issues = web_session.flow_engine.validate_flow(schema.flow_config.flow_id)
            issues.extend([f"Flow: {issue}" for issue in flow_issues])
        
        return jsonify({
            'valid': len(issues) == 0,
            'issues': issues
        })
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
