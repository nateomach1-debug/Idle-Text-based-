"""
Discovery script - NOT a code-modifying patch.

Previous keyword-based scan found zero matches, meaning the actual
field/structure naming differs from what was guessed. This just dumps
raw samples (first 120 lines, plus a middle slice) of each file so we
can see the real structure before writing a targeted scan.

Writes one new file: repo_item_catalog_raw_samples.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_item_catalog_raw_samples.txt"

FILES = ["GeneratedItemCatalog.kt", "MetalTierItemCatalog.kt", "ItemsEquipmentSystem.kt"]

lines_out = []

for filename in FILES:
    path = os.path.join(BASE, filename)
    lines_out.append("=" * 70)
    lines_out.append(filename)
    lines_out.append("=" * 70)
    if not os.path.isfile(path):
        lines_out.append("NOT FOUND")
        continue
    with open(path, "r", encoding="utf-8") as f:
        file_lines = f.readlines()

    total = len(file_lines)
    lines_out.append(f"(total lines: {total})")
    lines_out.append("")
    lines_out.append("--- first 120 lines ---")
    for i, line in enumerate(file_lines[:120]):
        lines_out.append(f"{i+1}: {line.rstrip()}")

    if total > 300:
        mid = total // 2
        lines_out.append("")
        lines_out.append(f"--- middle 60 lines (around line {mid}) ---")
        for i in range(max(0, mid - 30), min(total, mid + 30)):
            lines_out.append(f"{i+1}: {file_lines[i].rstrip()}")

    lines_out.append("")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
