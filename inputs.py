class DeviceController:
    """Sends taps/drags to the emulator window. Stub until input backend is chosen."""

    def __init__(self, dry_run=True):
        self.dry_run = dry_run

    def tap(self, x, y):
        if self.dry_run:
            print(f"[dry-run] tap ({x}, {y})")

    def drag(self, x1, y1, x2, y2, duration=0.3):
        if self.dry_run:
            print(f"[dry-run] drag ({x1}, {y1}) -> ({x2}, {y2}) over {duration}s")
