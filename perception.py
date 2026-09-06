import cv2

def identify_active_rotation(frame, character_templates):
    """
    Crops out the three player wheels and matches them against face assets.
    Returns: list of 3 strings matching character IDs (e.g., ['lr_beast_gohan', ...])
    """
    detected_slots = ["unknown", "unknown", "unknown"]
    # Coordinates mapping out Slot 1, Slot 2, Slot 3 wheels (normalized to your resolution)
    slot_regions = [(100, 600, 80, 80), (200, 600, 80, 80), (300, 600, 80, 80)]
    
    for idx, (x, y, w, h) in enumerate(slot_regions):
        crop = frame[y:y+h, x:x+w]
        best_val = 0.0
        best_id = "unknown"
        
        for char_id, template in character_templates.items():
            res = cv2.matchTemplate(crop, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            if max_val > 0.85 and max_val > best_val:  # Confidence boundary threshold
                best_val = max_val
                best_id = char_id
        detected_slots[idx] = best_id
    return detected_slots