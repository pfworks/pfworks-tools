#!/usr/bin/env python3
"""
Simple PIL and HAL image test
"""

import os
import sys

print("=== PIL and HAL Image Test ===")
print()

# Test 1: Basic imports
print("1. Testing basic imports...")
try:
    import tkinter as tk
    print("✓ tkinter available")
except ImportError as e:
    print(f"✗ tkinter not available: {e}")
    sys.exit(1)

# Test 2: PIL imports
print("\n2. Testing PIL imports...")
try:
    from PIL import Image
    print("✓ PIL.Image available")
    PIL_IMAGE = True
except ImportError as e:
    print(f"✗ PIL.Image not available: {e}")
    PIL_IMAGE = False

try:
    from PIL import ImageTk
    print("✓ PIL.ImageTk available")
    PIL_IMAGETK = True
except ImportError as e:
    print(f"✗ PIL.ImageTk not available: {e}")
    PIL_IMAGETK = False

# Test 3: HAL image file
print("\n3. Testing HAL image file...")
image_paths = [
    "assets/Hal_9000_Panel.svg.png",
    "Hal_9000_Panel.svg.png",
    "/home/rory/Q-projects/hal/assets/Hal_9000_Panel.svg.png"
]

hal_image_found = False
for path in image_paths:
    if os.path.exists(path):
        print(f"✓ HAL image found at: {path}")
        print(f"  File size: {os.path.getsize(path)} bytes")
        hal_image_found = True
        
        # Try to load it if PIL is available
        if PIL_IMAGE and PIL_IMAGETK:
            try:
                pil_image = Image.open(path)
                print(f"  Image format: {pil_image.format}")
                print(f"  Image size: {pil_image.size}")
                print(f"  Image mode: {pil_image.mode}")
                
                # Try to create ImageTk
                resized = pil_image.resize((80, 80), Image.Resampling.LANCZOS)
                tk_image = ImageTk.PhotoImage(resized)
                print("✓ Successfully created ImageTk object")
                
            except Exception as e:
                print(f"✗ Error loading image: {e}")
        break

if not hal_image_found:
    print("✗ HAL image not found in any expected location")

# Test 4: Simple tkinter window with results
print("\n4. Creating test window...")

def create_test_window():
    root = tk.Tk()
    root.title("HAL PIL Test Results")
    root.geometry("600x400")
    root.configure(bg='#000000')
    
    # Results display
    text_widget = tk.Text(root, bg='#000000', fg='#00FF00', 
                         font=('Courier New', 10))
    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    results = f"""HAL PIL Test Results:

PIL.Image available: {PIL_IMAGE}
PIL.ImageTk available: {PIL_IMAGETK}
HAL image found: {hal_image_found}

Recommendations:
"""
    
    if not PIL_IMAGE:
        results += "\n• Install PIL: sudo apt-get install python3-pil"
    if not PIL_IMAGETK:
        results += "\n• Install ImageTk: sudo apt-get install python3-pil.imagetk"
    if not hal_image_found:
        results += "\n• HAL image missing - will use animated eye fallback"
    
    if PIL_IMAGE and PIL_IMAGETK and hal_image_found:
        results += "\n✓ Everything looks good for HAL image display!"
    else:
        results += "\n• HAL will work with animated red eye fallback"
    
    results += "\n\nClose this window and run HAL interface."
    
    text_widget.insert(tk.END, results)
    text_widget.config(state=tk.DISABLED)
    
    root.mainloop()

if __name__ == "__main__":
    create_test_window()
