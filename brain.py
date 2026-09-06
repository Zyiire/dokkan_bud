from itertools import permutations
from database import CHARACTER_DB

def calculate_rotation_score(slot_combination):
    """
    Calculate a score for the given slot combination based on character attributes
    """
    score = 0
    char_data = [CHARACTER_DB.get(cid, {}) for cid in slot_combination]

    #1. Eval. link synch between neighbor
    # Slot 1 links with slot 2 slot 2 links with both 1 & 3
    if char_data[0] and char_data[1]:
        shared_1_2 = set(char_data[0].get("links", [])).intersection(set(char_data[1].get("links", [])))
        score += len(shared_1_2) *15 #15 points per macthing link

    if char_data[1] and char_data[2]:
        shared_2_3 = set(char_data[1].get("links", [])).intersection(set(char_data[2].get("links", [])))
        score += len(shared_2_3) *10

    #2. defensive placement 
    # penalty if a fragile unit is set into slot 1 when their kit dictates otherwise
    if char_data[0] and not char_data[0].get("slot_1_viable", False):
        score -= 100
    if char_data[0] and char_data[0].get("guard_active", False):
        score += 50 # this is to favor tanks

    return score

def get_optimal_movement(current_rotation):
    all_options + list(permutations(current_rotation))
    best_option = all_options[0]
    best_score = -9999

    for option in all_options:
        current_score = calculate_rotation_score(option)
        if current_score > best_score:
            best_score = current_score
            best_option = option

    return best_option, best_score

