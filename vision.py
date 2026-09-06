import threading
import time
import cv2
import mss
import numpy as np
import pygetwindow as gw


class DokkanVision:
    """Background screen-capture thread for the emulator window.

    Grabs the emulator window rect with mss, then slices out the centred
    vertical game canvas (default 608 px wide) to drop the black pillarboxes.
    """

    def __init__(self, window_title="BlueStacks App Player", canvas_width=608):
        self.window_title = window_title
        self.canvas_width = canvas_width
        self.latest_frame = None
        self.stopped = False
        self.lock = threading.Lock()
        self.monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
        self._thread = None

        self._update_monitor_bounds()

    def _update_monitor_bounds(self):
        """Locate the emulator window and update the capture rect."""
        try:
            windows = gw.getWindowsWithTitle(self.window_title)
            if windows:
                win = windows[0]
                # Ignore minimised / collapsed states
                if win.width > 100 and win.height > 100:
                    self.monitor = {
                        "top": win.top,
                        "left": win.left,
                        "width": win.width,
                        "height": win.height,
                    }
        except Exception:
            pass

    def start(self):
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        return self

    def _capture_loop(self):
        # mss must be created on the thread that uses it (Windows GDI handles are per-thread)
        with mss.mss() as sct:
            loop_count = 0
            while not self.stopped:
                # Re-verify window position every 60 frames
                if loop_count % 60 == 0:
                    self._update_monitor_bounds()

                try:
                    # 1. Grab the emulator window from the OS buffer
                    img = np.array(sct.grab(self.monitor))
                    full_frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                    # 2. Slice out the centred vertical game canvas (discard black pillars).
                    #    Computed from the real frame width so it works whether mss returned
                    #    a full 1920x1080 screen or just the window rect.
                    h, w = full_frame.shape[:2]
                    if w > self.canvas_width:
                        left = (w - self.canvas_width) // 2
                        game_canvas = full_frame[0:h, left:left + self.canvas_width]
                    else:
                        game_canvas = full_frame

                    with self.lock:
                        self.latest_frame = game_canvas
                except Exception as e:
                    print(f"[vision] capture error: {type(e).__name__}: {e}")

                loop_count += 1
                time.sleep(0.016)

    def read(self):
        """Return a copy of the newest game-canvas frame, or None if nothing captured yet."""
        with self.lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None

    def stop(self):
        self.stopped = True
        if self._thread is not None:
            self._thread.join(timeout=1.0)
