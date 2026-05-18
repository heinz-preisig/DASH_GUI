"""
Flask Web Application for Schema App v2
REST API matching the brick_app_v2 architecture:
  - Class-based SchemaWebAPI
  - Per-request session_id in URL
  - Consistent {"status": "success"/"error", "data": ...} response envelope
"""

from datetime import datetime

import os

try:
    from flask import Flask, request, jsonify, render_template, send_from_directory
    from flask_cors import CORS
    from werkzeug.exceptions import HTTPException
except ImportError:
    print("Flask not available. Install with: pip install flask flask-cors")
    Flask = None
    CORS = None

from schema_app_v2.core.multi_tenant_backend import MultiTenantBackend
from schema_app_v2.core.flow_engine import FlowType


class SchemaWebAPI:
    """REST API for Schema App v2 — mirrors BrickWebAPI architecture"""

    def __init__(self, backend: MultiTenantBackend, host: str = 'localhost', port: int = 5000):
        if Flask is None:
            raise ImportError("Flask is required for web API")

        self.backend = backend
        self.host = host
        self.port = port
        self.app = Flask(__name__, template_folder='templates')
        self.app.config['SECRET_KEY'] = 'schema-app-secret-change-in-production'
        CORS(self.app)
        self._setup_routes()
        self._setup_error_handlers()

    # ── helpers ──────────────────────────────────────────────────────────────

    def _ok(self, data, code: int = 200):
        return jsonify({"status": "success", "data": data}), code

    def _err(self, message: str, code: int = 400):
        return jsonify({"status": "error", "message": message}), code

    def _get_session(self, session_id: str):
        s = self.backend.get_session(session_id)
        return s

    def _slib(self, s):
        """Schema library: request param, else session default"""
        return request.args.get('library') or s.active_schema_library

    def _blib(self, s):
        """Brick library: request param, else session default"""
        return request.args.get('library') or s.active_brick_library

    def _serialize_schema(self, schema):
        d = schema.to_dict()
        if 'component_ui_metadata' in d:
            d['component_ui_metadata'] = {
                k: v if isinstance(v, dict) else v.to_dict()
                for k, v in d['component_ui_metadata'].items()
            }
        return d

    def _export_all(self, s, schema, library: str):
        """Write .ttl and _form.html alongside the schema .json — called on every save."""
        try:
            from schema_app_v2.core.shacl_export import SHACLExporter
            output_dir = os.path.join(s.schema_core.repository_path, library or s.schema_core.active_library)
            SHACLExporter(s.brick_integration).export_all(schema, output_dir, library)
        except Exception as e:
            print(f"Warning: background export failed for {schema.schema_id}: {e}")

    # ── routes ────────────────────────────────────────────────────────────────

    def _setup_routes(self):

        # ── Main page ──────────────────────────────────────────────────────

        @self.app.route('/')
        def index():
            # Serve built Vite app from static/dist
            dist_dir = os.path.join(os.path.dirname(__file__), 'static', 'dist')
            if os.path.exists(dist_dir):
                return send_from_directory(dist_dir, 'index.html')
            # Fallback to template for development
            return render_template('index.html')

        @self.app.route('/assets/<path:filename>')
        def serve_assets(filename):
            """Serve Vite built assets"""
            dist_dir = os.path.join(os.path.dirname(__file__), 'static', 'dist', 'assets')
            return send_from_directory(dist_dir, filename)

        # ── Sessions ───────────────────────────────────────────────────────

        @self.app.route('/api/session', methods=['POST'])
        def create_session():
            data = request.get_json() or {}
            session_id = self.backend.create_session(
                data.get('client_type', 'web'),
                user_info=data.get('user_info', {})
            )
            return self._ok({"session_id": session_id}, 201)

        @self.app.route('/api/session/<session_id>', methods=['GET'])
        def get_session(session_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            return self._ok(s.get_session_info())

        @self.app.route('/api/session/<session_id>', methods=['DELETE'])
        def delete_session(session_id):
            if self.backend.remove_session(session_id):
                return self._ok({"message": "Session deleted"})
            return self._err("Session not found", 404)

        @self.app.route('/api/session/<session_id>/libraries', methods=['PUT'])
        def set_session_libraries(session_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            data = request.get_json() or {}
            if 'schema_library' in data:
                s.active_schema_library = data['schema_library'] or None
            if 'brick_library' in data:
                s.active_brick_library = data['brick_library'] or None
            return self._ok(s.get_session_info())

        # ── Health ─────────────────────────────────────────────────────────

        @self.app.route('/api/health', methods=['GET'])
        def health():
            return self._ok({"timestamp": datetime.now().isoformat(), "version": "2.0.0"})

        # ── Libraries ──────────────────────────────────────────────────────

        @self.app.route('/api/libraries', methods=['GET'])
        def get_libraries():
            s = self._get_session(request.args.get('session_id', ''))
            if not s:
                # fall back to first available session
                s = self.backend.get_session_for_client_type('web')
            if not s:
                return self._err("No session available", 400)
            return self._ok({
                "schema_libraries": s.schema_core.get_libraries(),
                "brick_libraries": s.brick_integration.get_brick_libraries(),
            })

        @self.app.route('/api/session/<session_id>/schema-libraries', methods=['GET'])
        def get_schema_libraries(session_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            return self._ok(s.schema_core.get_libraries())

        @self.app.route('/api/session/<session_id>/brick-libraries', methods=['GET'])
        def get_brick_libraries(session_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            return self._ok(s.brick_integration.get_brick_libraries())

        # ── Bricks ─────────────────────────────────────────────────────────

        @self.app.route('/api/session/<session_id>/bricks', methods=['GET'])
        def get_bricks(session_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._blib(s)
            search = request.args.get('search')
            if search:
                bricks = s.brick_integration.search_bricks(search, library)
            else:
                bricks = s.brick_integration.get_available_bricks(library)
            return self._ok([b.to_dict() for b in bricks])

        @self.app.route('/api/session/<session_id>/bricks/node-shapes', methods=['GET'])
        def get_node_shapes(session_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._blib(s)
            bricks = s.brick_integration.get_node_shape_bricks(library)
            return self._ok([b.to_dict() for b in bricks])

        @self.app.route('/api/session/<session_id>/bricks/property-shapes', methods=['GET'])
        def get_property_shapes(session_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._blib(s)
            bricks = s.brick_integration.get_property_shape_bricks(library)
            return self._ok([b.to_dict() for b in bricks])

        @self.app.route('/api/session/<session_id>/bricks/<brick_id>', methods=['GET'])
        def get_brick(session_id, brick_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._blib(s)
            brick = s.brick_integration.get_brick_by_id(brick_id, library)
            if not brick:
                return self._err("Brick not found", 404)
            return self._ok(brick.to_dict())

        # ── Schemas ────────────────────────────────────────────────────────

        @self.app.route('/api/session/<session_id>/schemas', methods=['GET'])
        def get_schemas(session_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schemas = s.schema_core.get_all_schemas(library)
            return self._ok([self._serialize_schema(sc) for sc in schemas])

        @self.app.route('/api/session/<session_id>/schemas', methods=['POST'])
        def create_schema(session_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            data = request.get_json() or {}
            schema = s.schema_core.create_schema(
                name=data.get('name', ''),
                description=data.get('description', ''),
                root_brick_id=data.get('root_brick_id', '')
            )
            s.current_schema = schema
            s._emit_event('schema_created', schema.to_dict())
            return self._ok(self._serialize_schema(schema), 201)

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>', methods=['GET'])
        def get_schema(session_id, schema_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            s.current_schema = schema
            s._emit_event('schema_loaded', schema.to_dict())
            return self._ok(self._serialize_schema(schema))

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>', methods=['PUT'])
        def update_schema(session_id, schema_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            data = request.get_json() or {}
            if 'name' in data:
                schema.name = data['name']
            if 'description' in data:
                schema.description = data['description']
            if 'root_brick_id' in data:
                schema.root_brick_id = data['root_brick_id']
            if 'component_brick_ids' in data:
                schema.component_brick_ids = data['component_brick_ids']
            schema.update_timestamp()
            s._emit_event('schema_updated', schema.to_dict())
            if s.schema_core.save_schema(schema, library):
                s._emit_event('schema_saved', schema.to_dict())
                self._export_all(s, schema, library)
                return self._ok(self._serialize_schema(schema))
            return self._err("Failed to save schema", 500)

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>', methods=['DELETE'])
        def delete_schema(session_id, schema_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            if s.schema_core.delete_schema(schema_id, library):
                s._emit_event('schema_deleted', {'schema_id': schema_id})
                return self._ok({"message": "Schema deleted"})
            return self._err("Failed to delete schema", 500)

        # ── Schema validation & export ─────────────────────────────────────

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/validate', methods=['POST'])
        def validate_schema(session_id, schema_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            issues = []
            if not schema.name.strip():
                issues.append("Schema name is required")
            if not schema.root_brick_id:
                issues.append("Root brick is required")
            if schema.root_brick_id:
                root_brick = s.brick_integration.get_brick_by_id(schema.root_brick_id, library)
                if not root_brick:
                    issues.append("Root brick not found")
                elif root_brick.object_type != "NodeShape":
                    issues.append("Root brick must be a NodeShape")
            for brick_id in schema.component_brick_ids:
                if not s.brick_integration.get_brick_by_id(brick_id, library):
                    issues.append(f"Component brick not found: {brick_id}")
            if schema.flow_config:
                flow_issues = s.flow_engine.validate_flow(schema.flow_config.flow_id)
                issues.extend([f"Flow: {i}" for i in flow_issues])
            return self._ok({"valid": len(issues) == 0, "issues": issues})

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/export/shacl', methods=['GET'])
        def export_shacl(session_id, schema_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            try:
                from schema_app_v2.core.shacl_export import SHACLExporter
                exporter = SHACLExporter(s.brick_integration)
                content = exporter.export_schema(schema, library)
                lib_path = os.path.join(s.schema_core.repository_path, library or s.schema_core.active_library)
                os.makedirs(lib_path, exist_ok=True)
                ttl_path = os.path.join(lib_path, f"{schema_id}.ttl")
                with open(ttl_path, 'w') as f:
                    f.write(content)
                return content, 200, {
                    'Content-Type': 'text/turtle',
                    'Content-Disposition': f'attachment; filename="{schema.name}.ttl"'
                }
            except Exception as e:
                return self._err(f"Export failed: {e}", 500)

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/export/dash-form', methods=['GET'])
        def export_dash_form(session_id, schema_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            try:
                from schema_app_v2.core.shacl_export import SHACLExporter
                exporter = SHACLExporter(s.brick_integration)
                lib_path = os.path.join(s.schema_core.repository_path, library or s.schema_core.active_library)
                exporter.export_all(schema, lib_path, library)
                turtle = exporter.export_schema(schema, library)
                html = exporter.build_form_html(schema, turtle)
                return html, 200, {
                    'Content-Type': 'text/html',
                    'Content-Disposition': f'attachment; filename="{schema.name}_form.html"'
                }
            except Exception as e:
                return self._err(f"Form generation failed: {e}", 500)

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/shapes', methods=['GET'])
        def get_shapes(session_id, schema_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            try:
                from schema_app_v2.core.shacl_export import SHACLExporter
                exporter = SHACLExporter(s.brick_integration)
                turtle = exporter.export_schema(schema, library)
                return turtle, 200, {
                    'Content-Type': 'text/turtle',
                    'Access-Control-Allow-Origin': '*',
                }
            except Exception as e:
                return self._err(f"Shapes export failed: {e}", 500)

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/preview/form', methods=['GET'])
        def preview_form(session_id, schema_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            shapes_url = f"/api/session/{session_id}/schemas/{schema_id}/shapes"
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{schema.name} — Form Preview</title>
  <script src="https://cdn.jsdelivr.net/npm/@ulb-darmstadt/shacl-form/dist/bundle.js" type="module"></script>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 860px; margin: 40px auto; padding: 0 20px; }}
    h1 {{ font-size: 1.4rem; color: #333; border-bottom: 2px solid #007bff; padding-bottom: 8px; }}
    p.desc {{ color: #666; font-size: 0.9rem; margin-bottom: 24px; }}
    .actions {{ margin-top: 20px; display: flex; gap: 10px; }}
    button {{ padding: 9px 18px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }}
    .btn-submit {{ background: #007bff; color: white; }}
    .btn-reset  {{ background: #6c757d; color: white; }}
  </style>
</head>
<body>
  <h1>{schema.name}</h1>
  {f'<p class="desc">{schema.description}</p>' if schema.description else ''}
  <shacl-form id="shacl-form"
    data-shapes-url="{shapes_url}"
    data-collapse="open">
  </shacl-form>
  <div class="actions">
    <button class="btn-submit" onclick="submitForm()">Review &amp; Submit</button>
    <button class="btn-reset" onclick="document.getElementById('shacl-form').reset()">Reset</button>
  </div>
  <pre id="output" style="display:none; background:#f4f4f4; padding:16px; border-radius:4px; font-size:12px; margin-top:20px; white-space:pre-wrap;"></pre>
  <script type="module">
    const form = document.getElementById('shacl-form');
    form.addEventListener('change', async (e) => {{
      const valid = await form.validate(true);
      document.querySelector('.btn-submit').style.opacity = valid ? '1' : '0.6';
    }});
    window.submitForm = async () => {{
      const valid = await form.validate(false);
      if (!valid) return;
      const turtle = form.serialize();
      const out = document.getElementById('output');
      out.textContent = turtle;
      out.style.display = 'block';
      out.scrollIntoView({{behavior: 'smooth'}});
    }};
  </script>
</body>
</html>"""
            return html, 200, {'Content-Type': 'text/html'}

        # ── Components ─────────────────────────────────────────────────────

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/components', methods=['POST'])
        def add_component(session_id, schema_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            data = request.get_json() or {}
            brick_id = data.get('brick_id')
            if not brick_id:
                return self._err("brick_id is required")
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            if brick_id in schema.component_brick_ids:
                return self._err("Component already exists")
            schema.component_brick_ids.append(brick_id)
            schema.update_timestamp()
            s._emit_event('component_added', {'brick_id': brick_id})
            s.schema_core.save_schema(schema, library)
            return self._ok({"message": "Component added"})

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/components/<brick_id>', methods=['DELETE'])
        def remove_component(session_id, schema_id, brick_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            if brick_id not in schema.component_brick_ids:
                return self._err("Component not found", 404)
            schema.component_brick_ids.remove(brick_id)
            schema.update_timestamp()
            s._emit_event('component_removed', {'brick_id': brick_id})
            s.schema_core.save_schema(schema, library)
            return self._ok({"message": "Component removed"})

        # ── Schema refs ────────────────────────────────────────────────────

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/refs', methods=['GET'])
        def get_schema_refs(session_id, schema_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            return self._ok(schema.schema_refs)

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/refs', methods=['POST'])
        def add_schema_ref(session_id, schema_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            data = request.get_json() or {}
            ref_schema_id = data.get('schema_id')
            attach_to = data.get('attach_to_brick_id')
            prop_path = data.get('property_path')
            if not ref_schema_id or not attach_to or not prop_path:
                return self._err("schema_id, attach_to_brick_id and property_path are required")
            ref = schema.add_schema_ref(
                schema_id=ref_schema_id,
                attach_to_brick_id=attach_to,
                property_path=prop_path,
                label=data.get('label', '')
            )
            s.schema_core.save_schema(schema, library)
            s._emit_event('schema_ref_added', {'schema_id': schema_id, 'ref': ref})
            return self._ok(ref, 201)

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/refs/<ref_schema_id>', methods=['DELETE'])
        def remove_schema_ref(session_id, schema_id, ref_schema_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            attach_to = request.args.get('attach_to_brick_id', '')
            schema.remove_schema_ref(ref_schema_id, attach_to)
            s.schema_core.save_schema(schema, library)
            s._emit_event('schema_ref_removed', {'schema_id': schema_id, 'ref_schema_id': ref_schema_id})
            return self._ok({"message": "Schema ref removed"})

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/components/<brick_id>/refs', methods=['GET'])
        def get_refs_for_brick(session_id, schema_id, brick_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            return self._ok(schema.get_schema_refs_for_brick(brick_id))

        # ── Tree ───────────────────────────────────────────────────────────

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/tree', methods=['GET'])
        def get_schema_tree(session_id, schema_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            return self._ok({
                "tree": schema.get_ui_tree(),
                "roots": schema.get_ui_root_components(),
            })

        # ── Groups ─────────────────────────────────────────────────────────

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/groups', methods=['GET'])
        def get_groups(session_id, schema_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            return self._ok(schema.get_groups_by_sequence())

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/groups', methods=['POST'])
        def create_group(session_id, schema_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            data = request.get_json() or {}
            group_id = data.get('group_id')
            if not group_id:
                return self._err("group_id is required")
            if schema.create_group(group_id, data.get('label', group_id),
                                   data.get('description', ''), data.get('sequence', 0)):
                s.schema_core.save_schema(schema, library)
                s._emit_event('group_created', {'schema_id': schema_id, 'group_id': group_id})
                return self._ok({'id': group_id, **schema.groups[group_id]})
            return self._err("Group already exists")

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/groups/<group_id>', methods=['DELETE'])
        def delete_group(session_id, schema_id, group_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            if schema.delete_group(group_id):
                s.schema_core.save_schema(schema, library)
                s._emit_event('group_deleted', {'schema_id': schema_id, 'group_id': group_id})
                return self._ok({"message": "Group deleted"})
            return self._err("Group not found", 404)

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/components/<brick_id>/group', methods=['PUT'])
        def add_to_group(session_id, schema_id, brick_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            data = request.get_json() or {}
            group_id = data.get('group_id')
            if not group_id:
                return self._err("group_id is required")
            if schema.add_component_to_group(brick_id, group_id):
                s.schema_core.save_schema(schema, library)
                return self._ok({"message": "Added to group"})
            return self._err("Group not found", 404)

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/components/<brick_id>/group', methods=['DELETE'])
        def remove_from_group(session_id, schema_id, brick_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            if schema.remove_component_from_group(brick_id):
                s.schema_core.save_schema(schema, library)
                return self._ok({"message": "Removed from group"})
            return self._err("Failed to remove from group", 500)

        # ── UI Metadata ────────────────────────────────────────────────────

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/components/<brick_id>/ui-metadata', methods=['GET'])
        def get_ui_metadata(session_id, schema_id, brick_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            if brick_id not in schema.component_brick_ids:
                return self._err("Component not found", 404)
            meta = schema.get_component_ui_metadata(brick_id)
            if not meta:
                schema.initialize_component_ui_metadata(brick_id)
                meta = schema.get_component_ui_metadata(brick_id)
            return self._ok(meta.to_dict())

        @self.app.route('/api/session/<session_id>/schemas/<schema_id>/components/<brick_id>/ui-metadata', methods=['PUT'])
        def update_ui_metadata(session_id, schema_id, brick_id):
            s = self._get_session(session_id)
            if not s:
                return self._err("Session not found", 404)
            library = self._slib(s)
            schema = s.schema_core.load_schema(schema_id, library)
            if not schema:
                return self._err("Schema not found", 404)
            if brick_id not in schema.component_brick_ids:
                return self._err("Component not found", 404)
            data = request.get_json() or {}
            from schema_app_v2.core.schema_core import UIMetadata
            meta = UIMetadata(
                sequence=data.get('sequence', 0),
                group_id=data.get('group_id'),
                parent_id=data.get('parent_id'),
                label=data.get('label', ''),
                help_text=data.get('help_text', ''),
                is_collapsible=data.get('is_collapsible', True),
                is_visible=data.get('is_visible', True)
            )
            schema.set_component_ui_metadata(brick_id, meta)
            s.schema_core.save_schema(schema, library)
            s._emit_event('ui_metadata_updated', {'schema_id': schema_id, 'brick_id': brick_id})
            return self._ok(meta.to_dict())

        # ── Sessions list ──────────────────────────────────────────────────

        @self.app.route('/api/sessions', methods=['GET'])
        def get_sessions():
            return self._ok(self.backend.get_all_sessions())

        @self.app.route('/api/sessions/stats', methods=['GET'])
        def get_session_stats():
            return self._ok(self.backend.get_session_stats())

    # ── error handlers ────────────────────────────────────────────────────────

    def _setup_error_handlers(self):

        @self.app.errorhandler(HTTPException)
        def handle_http(e):
            return jsonify({"status": "error", "message": str(e.description), "code": e.code}), e.code

        @self.app.errorhandler(Exception)
        def handle_exc(e):
            return jsonify({"status": "error", "message": str(e), "code": 500}), 500

    # ── run ───────────────────────────────────────────────────────────────────

    def run(self, debug: bool = False):
        print(f"Starting Schema App v2 Web API on http://{self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=debug)


def create_app(schema_repository_path: str = None,
               brick_repository_path: str = None,
               host: str = 'localhost', port: int = 5000):
    """Factory — kept for backward-compat with main.py --web"""
    backend = MultiTenantBackend(schema_repository_path, brick_repository_path)
    api = SchemaWebAPI(backend, host=host, port=port)
    return api.app


if __name__ == "__main__":
    backend = MultiTenantBackend()
    api = SchemaWebAPI(backend)
    api.run(debug=True)
