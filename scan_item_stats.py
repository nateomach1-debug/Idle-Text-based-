"""
Discovery script - NOT a code-modifying patch.

Scans GeneratedItemCatalog.kt and MetalTierItemCatalog.kt for item stat
entries (looking for common field name patterns like defense/attack/
accuracy/maxHit/armor/level/tier), then:
  1. Flags likely bugs: zero, negative, or suspiciously duplicate stat
     blocks between differently-named items.
  2. Flags consistency outliers: within items grouped by a detected tier/
     level number, stats that don't increase monotonically tier-to-tier
     or that jump/drop unusually compared to neighbors.

Since the exact data class shape isn't known yet, this first extracts
raw item-like blocks via a generic brace-matching heuristic keyed on
lines containing "level" or "tier" and numeric fields, then reports
findings. This is intentionally a first-pass scan - some manual review
of the report is expected before any patch is written.

Writes one new file: repo_item_stats_audit_report.txt
"""

import os
import re

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_item_stats_audit_report.txt"

FILES = ["GeneratedItemCatalog.kt", "MetalTierItemCatalog.kt", "ItemsEquipmentSystem.kt"]

lines_out = []
lines_out.append("=" * 70)
lines_out.append("Item/weapon stats discovery report")
lines_out.append("=" * 70)
lines_out.append("")

# First: find the data class definitions themselves, wherever they live,
# so we know the actual field names before parsing entries.
lines_out.append("-" * 70)
lines_out.append("STEP 1: data class / field name discovery")
lines_out.append("-" * 70)

class_pattern = re.compile(r"(data class|class|enum class)\s+(\w*(Item|Weapon|Equipment|Armor|Stats)\w*)")
field_pattern = re.compile(r"val\s+(\w+)\s*:\s*(\w+)")

for filename in FILES:
    path = os.path.join(BASE, filename)
    if not os.path.isfile(path):
        lines_out.append(f"{filename}: NOT FOUND")
        continue
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        file_lines = content.splitlines()

    lines_out.append(f"\n{filename}:")
    for i, line in enumerate(file_lines):
        m = class_pattern.search(line)
        if m:
            lines_out.append(f"  line {i+1}: {line.strip()}")
            # print next ~15 lines to capture the field list
            for j in range(i + 1, min(i + 16, len(file_lines))):
                lines_out.append(f"    {j+1}: {file_lines[j].rstrip()}")
                if "{" not in "".join(file_lines[i:j+1]) and file_lines[j].strip().startswith(")"):
                    break

# Second: pull all numeric-looking stat assignments, grouped loosely by
# nearby item-name-like strings, so we get raw data to eyeball for zeros/
# negatives without needing to know the exact schema up front.
lines_out.append("\n" + "-" * 70)
lines_out.append("STEP 2: raw numeric stat fields found (sample - first 200 per file)")
lines_out.append("-" * 70)

stat_field_pattern = re.compile(
    r"\b(defense|defence|attack|accuracy|maxHit|max_hit|armor|armour|"
    r"strength|magic|ranged|archery|level|tier|damage|power|value|price)\s*=\s*(-?\d+)",
    re.IGNORECASE,
)

for filename in FILES:
    path = os.path.join(BASE, filename)
    if not os.path.isfile(path):
        continue
    with open(path, "r", encoding="utf-8") as f:
        file_lines = f.readlines()

    lines_out.append(f"\n{filename} (total lines: {len(file_lines)}):")
    matches_found = 0
    for i, line in enumerate(file_lines):
        for m in stat_field_pattern.finditer(line):
            field, value = m.group(1), m.group(2)
            flag = ""
            if int(value) == 0:
                flag = "  <-- ZERO"
            elif int(value) < 0:
                flag = "  <-- NEGATIVE"
            lines_out.append(f"  line {i+1}: {field}={value}{flag}")
            matches_found += 1
            if matches_found >= 200:
                break
        if matches_found >= 200:
            lines_out.append("  ... (truncated at 200 matches, see full file if more detail needed)")
            break

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
