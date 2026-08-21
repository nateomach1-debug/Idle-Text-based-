"""
Discovery script - NOT a code-modifying patch.

Scans InventoryScreen.kt for the existing "Use" button/action, and
GameViewModel.kt for ConsumableType.FOOD handling and healCharacter,
to see how food-use currently works (likely combat-only) before writing
the item-11 patch (enable it outside combat too).

Writes one new file: repo_inventory_use_and_heal.txt
"""

import os
import re

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_inventory_use_and_heal.txt"

lines_out = []
lines_out.append("=" * 70)
lines_out.append("InventoryScreen.kt - lines mentioning Use/use/onUse/Consumable/Food")
lines_out.append("=" * 70)

path = os.path.join(BASE, "InventoryScreen.kt")
if os.path.isfile(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    lines_out.append(f"(total lines: {len(lines)})")
    keywords = ["Use", "use", "Consumable", "Food", "heal", "Heal"]
    for i, line in enumerate(lines):
        if any(k in line for k in keywords):
            lines_out.append(f"{i+1}: {line.rstrip()}")
else:
    lines_out.append("NOT FOUND")

lines_out.append("")
lines_out.append("=" * 70)
lines_out.append("GameViewModel.kt - lines mentioning healCharacter/ConsumableType/FOOD/useItem")
lines_out.append("=" * 70)

path = os.path.join(BASE, "GameViewModel.kt")
if os.path.isfile(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    lines_out.append(f"(total lines: {len(lines)})")
    keywords = ["healCharacter", "ConsumableType", "FOOD", "useItem", "consumeItem", "eatFood"]
    for i, line in enumerate(lines):
        if any(k in line for k in keywords):
            lines_out.append(f"{i+1}: {line.rstrip()}")
else:
    lines_out.append("NOT FOUND")

lines_out.append("")
lines_out.append("=" * 70)
lines_out.append("CombatSystem-ish files - search for healCharacter definition")
lines_out.append("=" * 70)

for fname in os.listdir(BASE):
    if fname.endswith(".kt"):
        fpath = os.path.join(BASE, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        if "fun healCharacter" in content:
            lines_out.append(f"Found 'fun healCharacter' in {fname}")
            idx = content.find("fun healCharacter")
            snippet = content[idx:idx+400]
            lines_out.append(snippet)
            lines_out.append("")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
