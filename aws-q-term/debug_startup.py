#!/usr/bin/env python3
"""
Debug startup issues
"""

print("Testing PIL imports...")
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
    print("✓ PIL with ImageTk available")
except ImportError:
    try:
        from PIL import Image
        PIL_AVAILABLE = False
        print("⚠ PIL available but ImageTk missing")
    except ImportError:
        PIL_AVAILABLE = False
        print("⚠ PIL not available")

print(f"PIL_AVAILABLE = {PIL_AVAILABLE}")

print("\nTesting tkinter...")
try:
    import tkinter as tk
    print("✓ tkinter available")
    
    # Test creating a window
    root = tk.Tk()
    root.withdraw()
    print("✓ tkinter window created")
    
    # Test the load_hal_image method in isolation
    print("\nTesting load_hal_image logic...")
    
    import os
    image_path = os.path.join(os.path.dirname(__file__), "assets", "Hal_9000_Panel.svg.png")
    print(f"Looking for image at: {image_path}")
    print(f"Image exists: {os.path.exists(image_path)}")
    
    if PIL_AVAILABLE and os.path.exists(image_path):
        try:
            pil_image = Image.open(image_path)
            print(f"✓ Image loaded: {pil_image.size}")
            
            # Test resize
            target_height = 600
            aspect_ratio = pil_image.width / pil_image.height
            target_width = int(target_height * aspect_ratio)
            pil_image = pil_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            print(f"✓ Image resized to: {pil_image.size}")
            
            # Test ImageTk
            tk_image = ImageTk.PhotoImage(pil_image)
            print("✓ ImageTk.PhotoImage created")
            
        except Exception as e:
            print(f"✗ Image processing failed: {e}")
            import traceback
            traceback.print_exc()
    
    root.destroy()
    print("✓ Test completed successfully")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
