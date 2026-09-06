import threading
import time
import cv2
import mss
import numpy as np
import pygetwindow as gw

class DokkaVision:
    def __init__(self, window_title="BlueStacks App Player"):
        self.sct = mss.mss()
        self.window_title = window_title
        self.latest_frame = None
        self.stopped = False
        self.lock = threading.Lock()
        self.monitor = {"top": 0, "left": 0, "width": 450, "height": 800}

        self._update_monitor_bounds()

    def _update_monitor_bounds(self):
        """Locates the emulator window and updates the monitor bounds."""
        try:
            windows = gw.getWindowsWithTitle(self.window_title)
            if windows:
                win = windows[0]
            #filters mini states
                if win.width > 100 and win.height > 100:
                    self.monitor = {"top": win.top, "left": win.left, "width": win.width,"height": win.height}
        except Exception:
            pass

    def start(self):
        threading.Thread(target=self._capture_loop, daemon=True).start()
        return self

    def _capture_loop(self):
        loop_count = 0
        while not self.stopped:
            # re-verify window loco bounderies every 60 frames
            if loop_count % 60 == 0:
                self._update_window_bounds()

            try:
                img = np.array(self.sct.grab(self.monitor))
                bgr_frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                with self.lock:
                    self.latest_frame = bgr_frame
            except Exception:
                pass

            loop_count += 1
            time.sleep(0.016)

    def read(self):
        with self.lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None

    def stop(self):
        self.stopped = True