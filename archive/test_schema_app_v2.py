#!/usr/bin/env python3
"""
Test Script for Schema App v2
Validates all functionality and provides user-friendly feedback
"""

import sys
import os

# Add schema_app_v2 to path
sys.path.insert(0, os.path.abspath('schema_app_v2'))

def test_core_functionality():
    """Test core schema functionality"""
    print("🧪 Testing Core Functionality...")
    
    try:
        from schema_app_v2.core.schema_core import SchemaCore
        schema_core = SchemaCore('test_schemas')
        schema = schema_core.create_schema('Test Schema', 'A test schema for validation')
        print(f"✅ Schema creation: {schema.name}")
        
        # Test saving
        if schema_core.save_schema():
            print("✅ Schema saving: Success")
        else:
            print("❌ Schema saving: Failed")
            
    except Exception as e:
        print(f"❌ Core functionality failed: {e}")
        return False
    
    return True

def test_helper_functionality():
    """Test user-friendly helper functionality"""
    print("\n🧪 Testing Helper Functionality...")
    
    try:
        from schema_app_v2.core.schema_helper import SchemaHelper
        helper = SchemaHelper()
        
        # Test templates
        templates = helper.get_all_templates()
        print(f"✅ Templates loaded: {len(templates)} available")
        
        # Test explanations
        explanation = helper.get_explanation('schema')
        if explanation:
            print("✅ Schema explanation available")
        
        # Test tips
        tip = helper.get_random_tip()
        print(f"✅ Random tip: {tip[:50]}...")
        
    except Exception as e:
        print(f"❌ Helper functionality failed: {e}")
        return False
    
    return True

def test_brick_integration():
    """Test brick integration functionality"""
    print("\n🧪 Testing Brick Integration...")
    
    try:
        from schema_app_v2.core.brick_integration import BrickIntegration
        brick_integration = BrickIntegration('../brick_app_v2/brick_repositories_v2')
        
        # Test library access
        libraries = brick_integration.get_brick_libraries()
        print(f"✅ Brick libraries: {libraries}")
        
        # Test brick access
        bricks = brick_integration.get_available_bricks()
        print(f"✅ Available bricks: {len(bricks)} found")
        
    except Exception as e:
        print(f"❌ Brick integration failed: {e}")
        return False
    
    return True

def test_shacl_export():
    """Test SHACL export functionality"""
    print("\n🧪 Testing SHACL Export...")
    
    try:
        from schema_app_v2.core.shacl_export import SHACLExporter
        from schema_app_v2.core.schema_core import SchemaCore
        from schema_app_v2.core.brick_integration import BrickIntegration
        
        # Create test schema
        schema_core = SchemaCore('test_schemas')
        schema = schema_core.create_schema('Export Test', 'Test schema for export')
        
        # Test export
        brick_integration = BrickIntegration('../brick_app_v2/brick_repositories_v2')
        exporter = SHACLExporter(brick_integration)
        
        shacl_content = exporter.export_schema(schema)
        if shacl_content:
            print("✅ SHACL export: Success")
            print(f"   Generated {len(shacl_content)} characters of SHACL")
        else:
            print("❌ SHACL export: Empty result")
            
    except Exception as e:
        print(f"❌ SHACL export failed: {e}")
        return False
    
    return True

def test_flow_engine():
    """Test flow engine functionality"""
    print("\n🧪 Testing Flow Engine...")
    
    try:
        from schema_app_v2.core.flow_engine import FlowEngine, FlowType
        flow_engine = FlowEngine()
        
        # Create test flow
        flow = flow_engine.create_flow("Test Flow", FlowType.SEQUENTIAL, "Test flow")
        print(f"✅ Flow creation: {flow.name}")
        
        # Test validation
        issues = flow_engine.validate_flow(flow.flow_id)
        if issues:
            print(f"⚠️  Flow validation issues: {len(issues)}")
        else:
            print("✅ Flow validation: No issues")
            
    except Exception as e:
        print(f"❌ Flow engine failed: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Schema App v2 - System Test")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Core Functionality", test_core_functionality),
        ("Helper Functionality", test_helper_functionality),
        ("Brick Integration", test_brick_integration),
        ("SHACL Export", test_shacl_export),
        ("Flow Engine", test_flow_engine)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Schema App v2 is ready for use!")
        print("\n📋 To run the GUI:")
        print("   python3 run_schema_app_v2.py")
        print("\n🌐 To run the web interface:")
        print("   python3 run_schema_app_v2.py --web")
        print("\n💡 For help getting started:")
        print("   Use Help → Help Guide in the GUI")
        print("   Check the Templates tab for common use cases")
        print("   Read the Concepts Explained tab to learn terminology")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
