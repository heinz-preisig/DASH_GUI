#!/usr/bin/env python3
"""
Brick App v2 - Main Entry Point
Clean architecture with both GUI and web interfaces
"""

import sys
import argparse
from PyQt6.QtWidgets import QApplication


def run_gui():
    """Run the PyQt GUI interface"""
    app = QApplication(sys.argv)
    
    # Import and create main window
    from refactored_gui import BrickAppV2GUI
    window = BrickAppV2GUI()
    window.show()
    
    return app.exec()


def run_web(port: int = 5000, debug: bool = False):
    """Run the web interface"""
    try:
        from api.web_api import BrickWebAPI
        from core.multi_tenant_backend import MultiTenantBackend
        
        # Initialize backend with repository path
        backend = MultiTenantBackend(repository_path="shared_libraries")
        
        # Create and run web API
        web_api = BrickWebAPI(backend, host='localhost', port=port)
        print(f"Starting Brick App v2 Web Interface on http://localhost:{port}")
        web_api.run(debug=debug)
        
    except ImportError as e:
        print(f"Web dependencies not available: {e}")
        print("Install with: pip install flask flask-cors")
        return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Brick App v2 - SHACL Brick Generator")
    parser.add_argument("--gui", action="store_true", help="Launch PyQt GUI interface")
    parser.add_argument("--web", action="store_true", help="Launch web interface")
    parser.add_argument("--port", type=int, default=5000, help="Web interface port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    if args.web:
        return run_web(args.port, args.debug)
    elif args.gui:
        return run_gui()
    else:
        # Default to GUI
        print("Starting Brick App v2 GUI...")
        print("Using clean architecture with separated concerns")
        print("Ready for web migration with proper state management")
        return run_gui()


if __name__ == "__main__":
    sys.exit(main())
