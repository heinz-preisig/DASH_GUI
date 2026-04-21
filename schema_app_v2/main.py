#!/usr/bin/env python3
"""
Schema App v2 - Main Entry Point
Clean, modular schema construction system following brick_app_v2 architecture
"""

import sys
import argparse
from PyQt6.QtWidgets import QApplication



def run_gui(schema_repository: str = None, 
           brick_repository: str = None):
    """Run the PyQt GUI interface"""
    app = QApplication(sys.argv)
    
    # Create main window using clean architecture
    from .interfaces.qt.schema_gui_clean import CleanSchemaGUI
    window = CleanSchemaGUI(schema_repository, brick_repository)
    
    return app.exec()


def run_web(schema_repository: str = None, 
           brick_repository: str = None,
           port: int = 5000, debug: bool = False):
    """Run the web interface"""
    from schema_app_v2.interfaces.web.flask_app import create_app
    
    app = create_app(schema_repository, brick_repository)
    app.run(debug=debug, port=port)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Schema App v2 - Schema Constructor")
    parser.add_argument("--gui", action="store_true", help="Launch PyQt GUI interface")
    parser.add_argument("--web", action="store_true", help="Launch web interface")
    parser.add_argument("--schema-repo", type=str, default=None, 
                       help="Schema repository path (uses shared libraries if None)")
    parser.add_argument("--brick-repo", type=str, default=None, 
                       help="Brick repository path (uses shared libraries if None)")
    parser.add_argument("--port", type=int, default=5000, help="Web interface port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    if args.gui:
        return run_gui(args.schema_repo, args.brick_repo)
    elif args.web:
        return run_web(args.schema_repo, args.brick_repo, args.port, args.debug)
    else:
        # Default to GUI
        print("Starting Schema App v2 GUI...")
        return run_gui(args.schema_repo, args.brick_repo)


if __name__ == "__main__":
    sys.exit(main())
