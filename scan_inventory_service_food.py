"""
Discovery script - NOT a code-modifying patch.

Finds InventoryService's consumeSelectedFood/selectFood/healAmount
definitions, and any generic per-itemId remove/consume function, so the
item-11 patch can write a real "use this specific food item" function
in GameViewModel rather than reusing the "selected slot" auto-heal path.

Writes one new file: repo_inventory_service_food.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_inventory_service_food.txt"

lines_out = []
lines_out.append("=" * 70)
lines_out.append("Search across all .kt files for InventoryService / consumeSelectedFood / healAmount")
lines_out.append("=" * 70)

keywords = ["class InventoryService", "consumeSelectedFood", "fun selectFood",
            "healAmount", "class Inventory(", "fun removeItem", "fun consumeItem",
            "ConsumableType.FOOD", "consumableDefinitionFor"]

for fname in sorted(os.listdir(BASE)):
    if not fname.endswith(".kt"):
        continue
    fpath = os.path.join(BASE, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    matches = []
    for i, line in enumerate(lines):
        if any(k in line for k in keywords):
            matches.append((i, line))
    if matches:
        lines_out.append(f"\n--- {fname} ---")
        for i, line in matches:
            start = max(0, i - 1)
            end = min(len(lines), i + 6)
            lines_out.append(f"  [line {i+1}]")
            for j in range(start, end):
                lines_out.append(f"    {j+1}: {lines[j].rstrip()}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
