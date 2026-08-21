"""
Discovery script - NOT a code-modifying patch.

Extracts every WEAPON and ARMOR ItemDefinition from GeneratedItemCatalog.kt
and MetalTierItemCatalog.kt (id, name, equipSlot, combatStyle,
skillRequired), plus every Recipe's (outputItemId -> levelRequired) from
ItemsEquipmentSystem.kt, so the tier/level progression used by the stat
formula lines up with what's already established via crafting.

Writes one new file: repo_weapon_armor_and_levels.txt
"""

import os
import re

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_weapon_armor_and_levels.txt"

lines_out = []
lines_out.append("=" * 70)
lines_out.append("WEAPON/ARMOR items from GeneratedItemCatalog.kt + MetalTierItemCatalog.kt")
lines_out.append("=" * 70)
lines_out.append("")

item_block_re = re.compile(
    r"ItemDefinition\(\s*"
    r'id\s*=\s*"([^"]+)"\s*,\s*'
    r'name\s*=\s*"([^"]+)"\s*,\s*'
    r"category\s*=\s*ItemCategory\.(\w+)"
    r"(.*?)\)",
    re.DOTALL,
)

for filename in ["GeneratedItemCatalog.kt", "MetalTierItemCatalog.kt"]:
    path = os.path.join(BASE, filename)
    if not os.path.isfile(path):
        lines_out.append(f"{filename}: NOT FOUND")
        continue
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    lines_out.append(f"--- {filename} ---")
    count = 0
    for m in item_block_re.finditer(content):
        item_id, name, category, rest = m.groups()
        if category not in ("WEAPON", "ARMOR"):
            continue
        equip = re.search(r"equipSlot\s*=\s*EquipSlot\.(\w+)", rest)
        style = re.search(r"combatStyle\s*=\s*CombatStyle\.(\w+)", rest)
        skill = re.search(r'skillRequired\s*=\s*"([^"]+)"', rest)
        lines_out.append(
            f"  id={item_id!r} name={name!r} category={category} "
            f"equipSlot={equip.group(1) if equip else None} "
            f"combatStyle={style.group(1) if style else None} "
            f"skillRequired={skill.group(1) if skill else None}"
        )
        count += 1
    lines_out.append(f"  ({count} weapon/armor items found)")
    lines_out.append("")

lines_out.append("=" * 70)
lines_out.append("Recipe levelRequired for weapon/armor-looking output items")
lines_out.append("(from ItemsEquipmentSystem.kt RecipeCatalog)")
lines_out.append("=" * 70)
lines_out.append("")

recipe_re = re.compile(
    r'outputItemId\s*=\s*"([^"]+)".*?levelRequired\s*=\s*(\d+)',
    re.DOTALL,
)

path = os.path.join(BASE, "ItemsEquipmentSystem.kt")
if os.path.isfile(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    # split on "Recipe(" to avoid regex spanning multiple recipes
    blocks = content.split("Recipe(")
    for block in blocks[1:]:
        m_id = re.search(r'outputItemId\s*=\s*"([^"]+)"', block)
        m_lvl = re.search(r"levelRequired\s*=\s*(\d+)", block)
        if m_id and m_lvl:
            lines_out.append(f"  {m_id.group(1)}: level {m_lvl.group(1)}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
