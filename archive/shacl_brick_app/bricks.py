#!/usr/bin/env python3
"""
Main entry point for SHACL Brick Generator
"""

import sys
import argparse

def main():
    """Main entry point with command line options"""
    parser = argparse.ArgumentParser(description="SHACL Brick Generator - Step 1")
    parser.add_argument("--gui", action="store_true", help="Run GUI interface")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--repository", default="brick_repositories", help="Repository path")
    
    args = parser.parse_args()
    
    if args.gui:
        # Run GUI
        from shacl_brick_app import run_gui
        sys.exit(run_gui(args.repository))
    elif args.test:
        # Run tests
        from shacl_brick_app.tests import test_brick_generator
        success = test_brick_generator()
        sys.exit(0 if success else 1)
    else:
        # Default: show help
        parser.print_help()
        print("\nExamples:")
        print("  python main.py --gui                    # Run GUI")
        print("  python main.py --test                   # Run tests")
        print("  python main.py --gui --repository ./my_libs  # Use custom repository")

if __name__ == "__main__":
    main()
