"""
Discovery script - NOT a code-modifying patch.

Extracts the ItemDefinition data class definition (and any related
enums: ItemCategory, EquipSlot, CombatStyle) from SharedTypes.kt to see
the exact stat field names and their defaults.

Writes one new file: repo_itemdefinition_schema.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(BASE, "SharedTypes.kt")
OUTPUT_PATH = "repo_itemdefinition_schema.txt"

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

lines_out = []
lines_out.append("=" * 70)
lines_out.append("SharedTypes.kt - ItemDefinition and related type definitions")
lines_out.append(f"(total lines: {len(lines)})")
lines_out.append("=" * 70)
lines_out.append("")

keywords = ["ItemDefinition", "ItemCategory", "EquipSlot", "CombatStyle", "ItemCatalog"]

i = 0
while i < len(lines):
    line = lines[i]
    if any(k in line for k in keywords) and ("class" in line or "object" in line or "enum" in line):
        lines_out.append(f"--- starting line {i+1} ---")
        # print until we hit a closing brace/paren at column 0 or low indent, up to 60 lines
        depth = 0
        started = False
        count = 0
        j = i
        while j < len(lines) and count < 60:
            l = lines[j]
            lines_out.append(f"{j+1}: {l.rstrip()}")
            depth += l.count("(") + l.count("{")
            depth -= l.count(")") + l.count("}")
            if "(" in l or "{" in l:
                started = True
            if started and depth <= 0:
                break
            j += 1
            count += 1
        lines_out.append("")
        i = j
    i += 1

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
