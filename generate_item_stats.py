"""
Items 6+9: equipment/weapon stats audit -> generation.

Finding: every WEAPON/ARMOR ItemDefinition in GeneratedItemCatalog.kt and
MetalTierItemCatalog.kt currently omits the `stats` parameter entirely,
relying on ItemStats()'s all-zero default. This script inserts a real
`stats = ItemStats(...)` into each one, computed from a level-based
formula so tier-to-tier scaling is smooth and consistent by construction.

Formula:
  Level L for each item is looked up from RecipeCatalog's levelRequired
  in ItemsEquipmentSystem.kt (scanned live, not hardcoded) - this keeps
  combat-stat progression in lockstep with the existing crafting-level
  progression.

  WEAPONS (category=WEAPON, equipSlot != None):
    base_atk = 3 + 0.7*L      base_acc = 5 + 1.1*L
    base_hit = 2 + 0.75*L     base_str = 1 + 0.35*L
    Each multiplied by a per-subtype profile (dagger=fast/accurate/light,
    warhammer/2h=slow/inaccurate/heavy, etc). defenseBonus stays 0.

  ARMOR (category=ARMOR, equipSlot != None):
    base_def = 2 + 0.6*L, multiplied by a per-slot profile (chestplate
    weighted highest, gloves/boots lowest). Everything else stays 0.

  Items with equipSlot == None (bundle/set containers, not directly
  equippable) are skipped entirely - no stats inserted.

Safety: this is data generation via regex, not per-item hand-verified
asserts (147 items makes that impractical) - so it includes strong
sanity checks: every WEAPON/ARMOR block with a real equipSlot MUST have
a level found via the recipe scan, or the whole run aborts with a clear
error listing exactly which item(s) failed lookup, making NO file
changes. A full per-item log is also written for review.

Writes: modifies GeneratedItemCatalog.kt and MetalTierItemCatalog.kt.
Also writes stats_generation_log.txt (full log of every item + its
computed stats, for review) - NOT committed as source, just a log.
"""

import os
import re

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
LOG_PATH = "stats_generation_log.txt"

TIER_PREFIXES = [
    "bronze_", "iron_", "steel_", "mithril_",
    "adamant_", "rune_", "orichalcum_", "celestial_",
]

WEAPON_PROFILES = {
    # subtype: (atk_mult, acc_mult, hit_mult, str_mult)
    "dagger": (1.0, 1.2, 0.7, 0.3),
    "sword": (1.0, 1.0, 1.0, 0.5),
    "mace": (0.9, 0.9, 1.1, 0.8),
    "warhammer": (0.7, 0.7, 1.6, 1.3),
    "battleaxe": (0.8, 0.8, 1.4, 1.1),
    "claws": (1.1, 1.3, 0.6, 0.2),
    "2h_sword": (0.75, 0.8, 1.5, 1.2),
    "halberd": (0.85, 0.85, 1.3, 0.9),
    "throwing_knives": (1.0, 1.2, 0.6, 0.1),
}
DEFAULT_WEAPON_PROFILE = (1.0, 1.0, 1.0, 0.5)
BOW_PROFILE = (1.0, 1.1, 0.9, 0.0)
BATTLESTAFF_PROFILE = (1.0, 1.0, 1.0, 0.0)

ARMOR_SLOT_MULT = {
    "CHESTPLATE": 1.4,
    "LEGS": 1.1,
    "HELMET": 0.8,
    "SHIELD": 1.0,
    "GLOVES": 0.4,
    "BOOTS": 0.4,
}
DEFAULT_ARMOR_MULT = 1.0


def strip_tier(item_id):
    for p in TIER_PREFIXES:
        if item_id.startswith(p):
            return item_id[len(p):]
    return item_id


def weapon_profile_for(item_id):
    subtype = strip_tier(item_id)
    if subtype in WEAPON_PROFILES:
        return WEAPON_PROFILES[subtype]
    if "bow" in item_id:
        return BOW_PROFILE
    if "battlestaff" in item_id:
        return BATTLESTAFF_PROFILE
    if "throwing_knives" in item_id:
        return WEAPON_PROFILES["throwing_knives"]
    return DEFAULT_WEAPON_PROFILE


def compute_weapon_stats(level):
    return {
        "base_atk": 3 + 0.7 * level,
        "base_acc": 5 + 1.1 * level,
        "base_hit": 2 + 0.75 * level,
        "base_str": 1 + 0.35 * level,
    }


def compute_armor_def(level):
    return 2 + 0.6 * level


# -----------------------------------------------------------------
# Step 1: build item_id -> levelRequired lookup from recipes
# -----------------------------------------------------------------
recipe_path = os.path.join(BASE, "ItemsEquipmentSystem.kt")
with open(recipe_path, "r", encoding="utf-8") as f:
    recipe_content = f.read()

level_lookup = {}
for block in recipe_content.split("Recipe(")[1:]:
    m_id = re.search(r'outputItemId\s*=\s*"([^"]+)"', block)
    m_lvl = re.search(r"levelRequired\s*=\s*(\d+)", block)
    if m_id and m_lvl:
        level_lookup[m_id.group(1)] = int(m_lvl.group(1))

assert len(level_lookup) > 50, f"Recipe level lookup suspiciously small ({len(level_lookup)}) - aborting."

# -----------------------------------------------------------------
# Step 2: process both catalog files
# -----------------------------------------------------------------
item_block_re = re.compile(r"ItemDefinition\([^)]*\)")

log_lines = []
missing_levels = []
skipped_no_slot = []
patched_count = 0

for filename in ["GeneratedItemCatalog.kt", "MetalTierItemCatalog.kt"]:
    path = os.path.join(BASE, filename)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    def process_block(m):
        global patched_count
        block = m.group(0)
        id_m = re.search(r'id\s*=\s*"([^"]+)"', block)
        cat_m = re.search(r"category\s*=\s*ItemCategory\.(\w+)", block)
        slot_m = re.search(r"equipSlot\s*=\s*EquipSlot\.(\w+)", block)

        if not id_m or not cat_m:
            return block
        item_id = id_m.group(1)
        category = cat_m.group(1)

        if category not in ("WEAPON", "ARMOR"):
            return block

        if not slot_m:
            skipped_no_slot.append(item_id)
            return block

        equip_slot = slot_m.group(1)
        level = level_lookup.get(item_id)
        if level is None:
            missing_levels.append(item_id)
            return block  # leave unmodified; reported at the end, run aborts before writing

        if category == "WEAPON":
            atk_m, acc_m, hit_m, str_m = weapon_profile_for(item_id)
            base = compute_weapon_stats(level)
            attack = max(1, round(base["base_atk"] * atk_m))
            accuracy = max(1, round(base["base_acc"] * acc_m))
            max_hit = max(1, round(base["base_hit"] * hit_m))
            strength = max(0, round(base["base_str"] * str_m))
            stats_str = (
                f"stats = ItemStats(attackBonus = {attack}, strengthBonus = {strength}, "
                f"accuracyBonus = {accuracy}, maxHitBonus = {max_hit})"
            )
            log_lines.append(
                f"{item_id} (WEAPON, L{level}, subtype={strip_tier(item_id)}): "
                f"atk={attack} str={strength} acc={accuracy} hit={max_hit}"
            )
        else:  # ARMOR
            slot_mult = ARMOR_SLOT_MULT.get(equip_slot, DEFAULT_ARMOR_MULT)
            defense = max(1, round(compute_armor_def(level) * slot_mult))
            stats_str = f"stats = ItemStats(defenseBonus = {defense})"
            log_lines.append(f"{item_id} (ARMOR, L{level}, slot={equip_slot}): def={defense}")

        patched_count += 1
        # insert stats param before the closing paren, matching trailing-comma style
        inner = block[len("ItemDefinition("):-1].rstrip()
        if inner.endswith(","):
            new_block = f"ItemDefinition({inner}\n            {stats_str}\n        )"
        else:
            new_block = f"ItemDefinition({inner},\n            {stats_str}\n        )"
        return new_block

    new_content = item_block_re.sub(process_block, content)

    # Only write if no missing levels found (checked after processing all files - see below)
    content_by_file = new_content
    with open(path + ".pending", "w", encoding="utf-8") as f:
        f.write(content_by_file)

# -----------------------------------------------------------------
# Step 3: abort if any lookups failed, otherwise commit the .pending files
# -----------------------------------------------------------------
if missing_levels:
    for fname in ["GeneratedItemCatalog.kt", "MetalTierItemCatalog.kt"]:
        pending = os.path.join(BASE, fname + ".pending")
        if os.path.exists(pending):
            os.remove(pending)
    raise AssertionError(
        f"Aborting - {len(missing_levels)} item(s) had no recipe levelRequired found, "
        f"no files were modified: {missing_levels}"
    )

for fname in ["GeneratedItemCatalog.kt", "MetalTierItemCatalog.kt"]:
    pending = os.path.join(BASE, fname + ".pending")
    real = os.path.join(BASE, fname)
    os.replace(pending, real)

log_lines.append("")
log_lines.append(f"TOTAL PATCHED: {patched_count}")
log_lines.append(f"SKIPPED (equipSlot=None, not equippable): {skipped_no_slot}")

with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

print(f"Patched {patched_count} items. Skipped {len(skipped_no_slot)} (no equipSlot). Log: {LOG_PATH}")
