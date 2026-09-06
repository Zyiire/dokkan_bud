"""Character database for dokkan_bud.

Loads every character from data/characters.json (796 UR/LR units, sourced from
the open-source MNprojects/DokkanAPI dataset, itself scraped from the Dokkan
Wiki) and derives the tactical flags brain.py scores on.

Hand-tuned entries in MANUAL_OVERRIDES win over anything derived from text, so
you can correct a unit the heuristics get wrong, or add units newer than the
dataset (it stops around May 2023).
"""
import json
import os
import re

_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "characters.json")


def _slug(text):
    """'Prepared for Battle' -> 'prepared_for_battle'."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _pct(match):
    return int(match.group(1)) / 100.0 if match else 0.0


# Rough word -> probability map Dokkan uses in passive text
_CHANCE_WORDS = {
    "rare chance": 0.10, "chance": 0.30, "medium chance": 0.50,
    "high chance": 0.70, "great chance": 0.90,
}


def _derive_flags(card):
    """Turn a raw card dict into the fields brain.py scores on."""
    passive = (card.get("passive") or "").lower()

    # Dodge: explicit % if present, otherwise map the chance wording
    dodge = 0.0
    m = re.search(r"(\d+)%\s+chance\s+of\s+evad", passive)
    if m:
        dodge = _pct(m)
    elif "evad" in passive:
        for phrase, p in sorted(_CHANCE_WORDS.items(), key=lambda kv: -len(kv[0])):
            if phrase in passive:
                dodge = p
                break
        else:
            dodge = 0.30

    # Damage reduction: "reduces damage received by 30%" / "damage reduction rate +40%"
    dr = 0.0
    m = re.search(r"(?:reduces? damage received by|damage reduction rate \+?)\s*(\d+)%", passive)
    if m:
        dr = _pct(m)

    guard = "guard" in passive and "disables" not in passive.split("guard")[0][-30:]
    counter = "counter" in passive

    # Slot 1 takes the most hits. A unit is slot-1 viable if it has any defensive
    # mechanic, or is a tanky LR with high DEF for its rarity.
    max_def = card.get("rainbowDefence") or card.get("maxDefence") or 0
    slot_1_viable = bool(guard or dodge >= 0.5 or dr >= 0.2 or counter or max_def >= 10000)

    return {
        "id": card.get("id"),
        "name": card.get("name", ""),
        "title": card.get("title", ""),
        "rarity": card.get("rarity", ""),
        "class": card.get("class", ""),
        "type": card.get("type", ""),
        "links": [_slug(l) for l in card.get("links", [])],
        "categories": card.get("categories", []),
        "passive_text": card.get("passive") or "",
        "leader_text": card.get("leaderSkill") or "",
        "image_url": card.get("imageURL", ""),
        "atk": card.get("rainbowAttack") or card.get("maxLevelAttack") or 0,
        "def": max_def,
        "hp": card.get("rainbowHP") or card.get("maxLevelHP") or 0,
        "slot_1_viable": slot_1_viable,
        "guard_active": guard,
        "dodge_chance": dodge,
        "damage_reduction": dr,
        "counter": counter,
        "transforms": bool(card.get("transformations")),
        "needs_rainbow_ki": False,
    }


def _make_key(card):
    """Stable id like 'lr_goku_ultra_instinct_sign_11982'."""
    return f"{card.get('rarity', 'ur').lower()}_{_slug(card.get('name', ''))}_{card.get('id', '')}"


# Hand-curated units. Keys here are the short ids used by your face templates.
MANUAL_OVERRIDES = {
    "lr_beast_gohan": {
        "name": "Super Saiyan Gohan (Beast)",
        "links": ["super_saiyan", "fierce_battle", "legendary_power", "prepared_for_battle"],
        "slot_1_viable": True,
        "guard_active": True,
        "damage_reduction": 0.20,
        "dodge_chance": 0.0,
        "counter": False,
        "needs_rainbow_ki": False,
    },
    "lr_mui_goku": {
        "name": "Ultra Instinct Goku",
        "links": ["tournament_of_power", "prepared_for_battle", "fierce_battle", "legendary_power"],
        "slot_1_viable": True,
        "guard_active": False,
        "dodge_chance": 0.77,
        "damage_reduction": 0.0,
        "counter": False,
        "needs_rainbow_ki": False,
    },
}


def load_character_db(path=_DATA_PATH):
    db = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for card in json.load(f):
                db[_make_key(card)] = _derive_flags(card)
    db.update(MANUAL_OVERRIDES)
    return db


CHARACTER_DB = load_character_db()

# Secondary index so you can look a unit up by its in-game name
NAME_INDEX = {}
for _k, _v in CHARACTER_DB.items():
    NAME_INDEX.setdefault(_v["name"].lower(), _k)


def find(name_fragment):
    """Search by name substring. Returns list of (key, name, rarity)."""
    q = name_fragment.lower()
    return [(k, v["name"], v.get("rarity", "")) for k, v in CHARACTER_DB.items() if q in v["name"].lower()]


if __name__ == "__main__":
    print(f"{len(CHARACTER_DB)} characters loaded")
    for k, name, r in find("Ultra Instinct")[:5]:
        c = CHARACTER_DB[k]
        print(f"  {k}: {r} {name} | dodge={c['dodge_chance']} guard={c['guard_active']} dr={c['damage_reduction']} slot1={c['slot_1_viable']}")
