import pygetwindow as gw
import cv2
import mss
import numpy as np

"""Searches for your emulator window by title and returns its dimensions."""
def find_emulator_window(title_keyword):
    windows = gw.getWindowsWithTitle(title_keyword)
    if not windows:
       print(f"❌ Could not find any windows matching keyword: '{title_keyword}'")
       print("Available windows on your system:")
       for w in gw.getAllTitles():
           if w.strip():
                print(f" - {w}")
       return None

    win = windows[0]
    print(f"✅ Found window: '{win.title}'")
    print(f"📍 Location: Top-Left ({win.left}, {win.top}) | Size: {win.width}x{win.height}")

    return {
        "top": win.top,
        "left": win.left,
        "width": win.width,
        "height": win.height,
        "title": win.title
    }
if __name__ == "__main__":

    target_keyword = "BlueStacks"

    win_rect = find_emulator_window(target_keyword)

    if win_rect:
        with mss.mss() as sct:
            monitor = {"top": win_rect["top"], "left": win_rect["left"], "width": win_rect["width"], "height": win_rect["height"]}
            screenshot = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
            
            # Save visual reference to verify we aren't clipping borders
            cv2.imwrite("emulator_workspace.png", frame)
            print("💾 Saved image verification to 'emulator_workspace.png'. Open it to verify it shows the game cleanly!")