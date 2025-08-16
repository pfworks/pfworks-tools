#!/usr/bin/env python3
"""
Simple startup test for HAL GUI to catch initialization errors
"""

import sys
import os

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    try:
        import tkinter as tk
        print("✓ tkinter available")
    except ImportError as e:
        print(f"✗ tkinter not available: {e}")
        return False
    
    try:
        # Test PIL imports (should handle gracefully)
        from PIL import Image, ImageTk
        print("✓ PIL with ImageTk available")
    except ImportError:
        try:
            from PIL import Image
            print("⚠ PIL available but ImageTk missing")
        except ImportError:
            print("⚠ PIL not available (will use animated eye)")
    
    return True

def test_hal_class():
    """Test HAL class initialization"""
    print("\nTesting HAL class initialization...")
    
    try:
        # Import the HAL class
        sys.path.insert(0, os.path.dirname(__file__))
        from hal_gui import HALInterface
        print("✓ HALInterface class imported successfully")
        
        # Create a test root window
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Try to create HAL instance
        hal = HALInterface(root)
        print("✓ HALInterface initialized successfully")
        
        # Clean up
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ HALInterface initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_methods():
    """Test key methods exist"""
    print("\nTesting method availability...")
    
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from hal_gui import HALInterface
        
        # Check if key methods exist
        methods_to_check = [
            'load_hal_image',
            'get_terminal_font', 
            'get_theme_colors',
            'toggle_color_theme',
            'set_mode',
            'handle_tab_completion'
        ]
        
        for method_name in methods_to_check:
            if hasattr(HALInterface, method_name):
                print(f"✓ {method_name} method exists")
            else:
                print(f"✗ {method_name} method missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Method check failed: {e}")
        return False

def main():
    """Run all tests"""
    print("HAL 9000 Interface - Startup Test")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Imports
    if test_imports():
        tests_passed += 1
    
    # Test 2: Class initialization
    if test_hal_class():
        tests_passed += 1
    
    # Test 3: Method availability
    if test_methods():
        tests_passed += 1
    
    print(f"\nTest Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! HAL GUI should start correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
