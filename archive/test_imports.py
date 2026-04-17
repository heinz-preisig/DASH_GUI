#!/usr/bin/env python3
"""
Quick test to verify package imports work correctly
"""

def test_imports():
    """Test that all package imports work"""
    try:
        print("Testing package imports...")
        
        # Test main package import
        from shacl_brick_app import create_brick_system
        print("  Main package import: OK")
        
        # Test backend import
        from shacl_brick_app.core.brick_backend import BrickBackendAPI
        print("  Backend import: OK")
        
        # Test generator import
        from shacl_brick_app.core.brick_generator import BrickLibrary
        print("  Generator import: OK")
        
        # Test GUI import
        from shacl_brick_app.gui.brick_gui import BrickGUI
        print("  GUI import: OK")
        
        # Test test import
        from shacl_brick_app.tests.test_brick_generator import test_brick_generator
        print("  Test import: OK")
        
        print("\nAll imports successful!")
        return True
        
    except Exception as e:
        print(f"Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\nPackage imports are working correctly!")
    else:
        print("\nThere are still import issues to fix.")
