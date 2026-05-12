#!/usr/bin/env python3
"""
Schema App v2 Web Launcher
Run from the workspace root so shared_libraries imports resolve correctly.
"""

import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

parser = argparse.ArgumentParser(description='Schema App v2 Web Launcher')
parser.add_argument('--port', type=int, default=5000, help='Port (default: 5000)')
parser.add_argument('--host', type=str, default='localhost', help='Host to bind (default: localhost, use 0.0.0.0 for Docker)')
parser.add_argument('--debug', action='store_true', help='Enable Flask debug mode')
args = parser.parse_args()

print('Starting Schema App v2 Web Interface...')
print(f'  URL : http://{args.host}:{args.port}')
print(f'  Debug: {args.debug}')

from schema_app_v2.interfaces.web.flask_app import SchemaWebAPI
from schema_app_v2.core.multi_tenant_backend import MultiTenantBackend

backend = MultiTenantBackend()
web_api = SchemaWebAPI(backend, host=args.host, port=args.port)
web_api.run(debug=args.debug)
