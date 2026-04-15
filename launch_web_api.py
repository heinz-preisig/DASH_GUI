#!/usr/bin/env python3
"""
Launch Web API for SHACL Brick Generator
Starts REST API server for browser-enabled frontend
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shacl_brick_app.core.multi_tenant_backend import MultiTenantBackend
from shacl_brick_app.api.web_api import create_web_api


def main():
    """Launch web API server"""
    print("Starting SHACL Brick Generator Web API...")
    
    # Initialize multi-tenant backend
    backend = MultiTenantBackend()
    
    # Create web API
    api = create_web_api(backend, host='localhost', port=5000)
    
    try:
        # Start the API server
        api.run(debug=True)
    except KeyboardInterrupt:
        print("\nShutting down web API...")
        backend.shutdown()
        print("Web API stopped gracefully")


if __name__ == "__main__":
    main()
