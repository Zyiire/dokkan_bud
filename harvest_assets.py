import cv2
import os
from vision import DokkanVision

def harvest_team_portraits():
    print("Initializing asset harvester for dokkan_bud...")
    vision = DokkanVision(window_title="BlueStacks").start() # Change title if needed
    
    # Give the engine a brief window to spin up threads and acquire a frame buffer
    import time
    time.sleep(2.0)
    
    frame = vision.read()
    if frame is None:
        print("❌ Error: Could not read game canvas frame. Is the emulator open and visible?")
        return

    # Normalized pixel coordinate arrays mapping the 3 combat wheel centers
    # Coordinates are calculated relative to our isolated 608x1080 game frame area
    slots = {
        "slot_1": (70, 780, 110, 110),   # (X, Y, Width, Height)
        "slot_2": (250, 780, 110, 110),
        "slot_3": (430, 780, 110, 110)
    }
    
    os.makedirs("character_assets", exist_ok=True)
    
    for slot_name, (x, y, w, h) in slots.items():
        portrait_crop = frame[y:y+h, x:x+w]
        filename = f"character_assets/raw_{slot_name}.png"
        cv2.imwrite(filename, portrait_crop)
        print(f"💾 Captured and saved target: {filename}")
        
    print("\n✅ Harvesting Complete! Check the 'character_assets' folder.")
    print("Rename the saved 'raw_slot_X.png' files to matching database IDs (e.g., 'beast_gohan.png')")

if __name__ == "__main__":
    harvest_team_portraits()