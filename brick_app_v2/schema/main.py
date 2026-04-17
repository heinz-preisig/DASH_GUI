#!/usr/bin/env python3
"""
Step 2: Schema Constructor Main Entry Point
Command-line interface for schema construction system
"""

import sys
import argparse
from PyQt6.QtWidgets import QApplication

def run_gui(repository_path: str = "schema_repositories"):
    """Run the schema constructor GUI"""
    from .gui.schema_gui import SchemaGUI
    
    app = QApplication(sys.argv)
    gui = SchemaGUI(repository_path)
    gui.show()
    return app.exec()

def run_example():
    """Run the schema construction example"""
    from .examples.schema_construction_example import main as example_main
    return example_main()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Step 2: Schema Constructor")
    parser.add_argument("--gui", action="store_true", help="Launch GUI")
    parser.add_argument("--example", action="store_true", help="Run example")
    parser.add_argument("--repository", type=str, default="schema_repositories", 
                       help="Repository path")
    
    args = parser.parse_args()
    
    if args.gui:
        return run_gui(args.repository)
    elif args.example:
        return run_example()
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
