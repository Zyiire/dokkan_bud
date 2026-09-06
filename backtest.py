"""Offline backtest: runs the perception -> brain pipeline on synthetic frames.

No emulator needed. Builds fake face templates, stamps them onto a blank frame at
the slot coordinates perception.py expects, and checks that the detected rotation
and the chosen optimal movement are what we'd expect.
"""
import numpy as np
import cv2

from perception import identify_active_rotation
from brain import get_optimal_movement, calculate_rotation_score
from database import CHARACTER_DB

SLOT_REGIONS = [(100, 600, 80, 80), (200, 600, 80, 80), (300, 600, 80, 80)]


def make_templates(seed=0):
    """One distinct 80x80 noise 'face' per character in the DB."""
    rng = np.random.default_rng(seed)
    return {cid: rng.integers(0, 255, (80, 80, 3), dtype=np.uint8) for cid in CHARACTER_DB}


def make_frame(templates, layout):
    """Blank 450x800 frame with the given character ids stamped into slots 1-3."""
    frame = np.zeros((800, 450, 3), dtype=np.uint8)
    for (x, y, w, h), cid in zip(SLOT_REGIONS, layout):
        if cid in templates:
            frame[y:y + h, x:x + w] = templates[cid]
    return frame


def run_case(name, layout, templates, expect_detect, expect_best):
    frame = make_frame(templates, layout)
    detected = identify_active_rotation(frame, templates)
    best, score = get_optimal_movement(detected)
    ok = detected == expect_detect and list(best) == expect_best
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    print(f"       layout   : {layout}")
    print(f"       detected : {detected}")
    print(f"       best     : {list(best)}  score={score}")
    return ok


def main():
    templates = make_templates()
    gohan, goku = "lr_beast_gohan", "lr_mui_goku"
    results = []

    # Case 1: both known units present, Gohan already leading. Gohan has guard so
    # he should stay in slot 1 (guard bonus +50 beats nothing else).
    results.append(run_case(
        "gohan lead, goku slot 2, empty slot 3",
        [gohan, goku, "unknown"], templates,
        expect_detect=[gohan, goku, "unknown"],
        expect_best=[gohan, goku, "unknown"],
    ))

    # Case 2: Goku leading. Optimizer should swap Gohan into slot 1 for the guard bonus.
    results.append(run_case(
        "goku lead -> should promote gohan to slot 1",
        [goku, gohan, "unknown"], templates,
        expect_detect=[goku, gohan, "unknown"],
        expect_best=[gohan, goku, "unknown"],
    ))

    # Case 3: nothing recognisable on screen. Every permutation scores 0.
    results.append(run_case(
        "empty field",
        ["unknown", "unknown", "unknown"], templates,
        expect_detect=["unknown", "unknown", "unknown"],
        expect_best=["unknown", "unknown", "unknown"],
    ))

    # Direct scorer sanity check: 3 shared links * 15 + guard 50 + 20% DR 20 = 115
    s = calculate_rotation_score((gohan, goku, "unknown"))
    ok = s == 115
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] scorer: gohan/goku/unknown = {s} (expected 115)")

    # Database sanity: full dataset loaded, overrides present
    ok = len(CHARACTER_DB) > 700 and gohan in CHARACTER_DB and goku in CHARACTER_DB
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] database: {len(CHARACTER_DB)} characters loaded, overrides present")

    passed = sum(results)
    print(f"\n{passed}/{len(results)} checks passed")
    raise SystemExit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
