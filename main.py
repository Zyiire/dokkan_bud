import cv2
import time
from vision import DokkanVision


def start_watching():
    print("Initializing dokkan_bud tracking engine...")

    # Change "BlueStacks" to match the exact window keyword your emulator uses!
    vision = DokkanVision(window_title="BlueStacks").start()

    # Give the thread a moment to fetch its first frames
    time.sleep(1.5)

    print("dokkan_bud is now watching! Press 'q' in the preview window to stop.")

    # Crop bounding boxes for Slot 1, Slot 2, Slot 3
    # Format: (X, Y, Width, Height) mapped to the 608x1080 game frame
    slots = {
        "Slot 1": (70, 780, 110, 110),
        "Slot 2": (250, 780, 110, 110),
        "Slot 3": (430, 780, 110, 110),
    }

    try:
        while True:
            # 1. Latest isolated game frame from the vision thread
            frame = vision.read()

            if frame is None:
                print("Waiting for emulator window frames... Make sure it's not minimized.")
                time.sleep(1.0)
                continue

            # 2. Draw on a copy so the source frame stays clean
            display_frame = frame.copy()

            # 3. Green target boxes over the three character slots
            for slot_name, (x, y, w, h) in slots.items():
                cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(display_frame, slot_name, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # 4. Live preview window
            cv2.imshow("dokkan_bud - Live Perception Stream", display_frame)

            # 5. 'q' quits
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        print("Closing down tracking windows safely...")
        vision.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    start_watching()
