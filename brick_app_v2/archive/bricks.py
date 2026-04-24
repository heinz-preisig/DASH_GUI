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
    parser.add_argument("--repository", default=None, help="Repository path (uses shared libraries if None)")
    
    args = parser.parse_args()
    
    if args.gui:
        # Run GUI using v2 architecture
        from brick_app_v2 import run_gui
        sys.exit(run_gui(args.repository))
    elif args.test:
        # Run tests using v2 architecture
        print("Running v2 tests...")
        try:
            from schema_app_v2.core.brick_integration import BrickIntegration
            from schema_app_v2.core.schema_core import SchemaCore
            bi = BrickIntegration()
            sc = SchemaCore()
            print(f'Bricks: {len(bi.get_available_bricks())}')
            print(f'Schemas: {len(sc.get_all_schemas())}')
            print("V2 tests completed successfully!")
            sys.exit(0)
        except Exception as e:
            print(f"V2 test failed: {e}")
            sys.exit(1)
    else:
        # Default: show help
        parser.print_help()
        print("\nExamples:")
        print("  python main.py --gui                    # Run GUI")
        print("  python main.py --test                   # Run tests")
        print("  python main.py --gui --repository ./my_libs  # Use custom repository")

if __name__ == "__main__":
    main()
