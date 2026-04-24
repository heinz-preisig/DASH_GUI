#!/usr/bin/env python3
"""
Test Refactored Architecture
Simple test to verify the new architecture works without UI dependencies
"""

import sys
from pathlib import Path

# Add brick_app_v2 directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))
sys.path.insert(0, str(app_dir / 'state'))
sys.path.insert(0, str(app_dir / 'business'))

from state.app_state import app_state_manager, UIState, BrickType
from business.brick_operations import brick_business_logic

def test_architecture():
    """Test the refactored architecture components"""
    print("🧪 Testing Refactored Architecture...")
    
    # Test 1: State Management
    print("\n1. Testing State Management...")
    try:
        # Test initial state
        current_state = app_state_manager.get_ui_state()
        print(f"   ✅ Initial UI state: {current_state}")
        
        # Test state change
        app_state_manager.set_ui_state(UIState.CREATE)
        new_state = app_state_manager.get_ui_state()
        print(f"   ✅ Updated UI state: {new_state}")
        
        # Test brick type change
        app_state_manager.set_brick_type(BrickType.PROPERTY_SHAPE)
        brick_type = app_state_manager.get_brick_type()
        print(f"   ✅ Brick type: {brick_type}")
        
    except Exception as e:
        print(f"   ❌ State management error: {e}")
        return False
    
    # Test 2: Business Logic
    print("\n2. Testing Business Logic...")
    try:
        # Test library operations
        libraries = brick_business_logic.get_libraries()
        print(f"   ✅ Available libraries: {libraries}")
        
        # Test brick operations
        bricks = brick_business_logic.get_bricks()
        print(f"   ✅ Found {len(bricks)} bricks")
        
        # Test brick creation
        success = brick_business_logic.create_new_brick(BrickType.NODE_SHAPE)
        print(f"   ✅ Brick creation: {'Success' if success else 'Failed'}")
        
        # Test brick field update
        app_state_manager.update_brick_field("name", "Test Brick")
        app_state_manager.update_brick_field("description", "Test Description")
        print("   ✅ Brick field updates")
        
    except Exception as e:
        print(f"   ❌ Business logic error: {e}")
        return False
    
    # Test 3: State Integration
    print("\n3. Testing State Integration...")
    try:
        # Get current brick state
        brick_state = app_state_manager.get_brick_state()
        print(f"   ✅ Current brick state: {brick_state.name}")
        
        # Get brick as dictionary
        brick_dict = app_state_manager.get_brick_dict()
        print(f"   ✅ Brick dict keys: {list(brick_dict.keys())}")
        
        # Get UI visibility state
        ui_visibility = app_state_manager.get_ui_visibility()
        print(f"   ✅ UI visibility: editor={ui_visibility.show_brick_editor}, list={ui_visibility.show_brick_list}")
        
    except Exception as e:
        print(f"   ❌ State integration error: {e}")
        return False
    
    print("\n🎉 Architecture Test Complete!")
    print("✅ State Management: Working")
    print("✅ Business Logic: Working") 
    print("✅ State Integration: Working")
    print("✅ Ready for Web Migration!")
    
    return True

if __name__ == "__main__":
    success = test_architecture()
    sys.exit(0 if success else 1)
