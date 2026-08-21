"""
Discovery script - NOT a code-modifying patch.

Checks whether ItemDefinition(...) calls in GeneratedItemCatalog.kt and
MetalTierItemCatalog.kt explicitly write "stats = ItemStats(...)" or
omit the stats parameter entirely (relying on the class default).
This determines whether the upcoming stats-generation patch can do a
simple text replace, or needs to insert a new parameter.

Also counts total ItemDefinition( occurrences for a sanity check against
the 49 + 98 = 147 weapon/armor items found earlier (total will be higher
since this counts ALL categories, not just WEAPON/ARMOR).

Writes one new file: repo_stats_param_check.txt
"""

import os
import re

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_stats_param_check.txt"

lines_out = []
lines_out.append("=" * 70)
lines_out.append("stats parameter presence check")
lines_out.append("=" * 70)

for filename in ["GeneratedItemCatalog.kt", "MetalTierItemCatalog.kt"]:
    path = os.path.join(BASE, filename)
    if not os.path.isfile(path):
        lines_out.append(f"{filename}: NOT FOUND")
        continue
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    total_itemdefs = len(re.findall(r"ItemDefinition\(", content))
    explicit_stats = len(re.findall(r"stats\s*=\s*ItemStats\(", content))
    explicit_stats_empty = len(re.findall(r"stats\s*=\s*ItemStats\(\s*\)", content))

    lines_out.append(f"\n{filename}:")
    lines_out.append(f"  total ItemDefinition( calls: {total_itemdefs}")
    lines_out.append(f"  calls with explicit 'stats = ItemStats(...)': {explicit_stats}")
    lines_out.append(f"  of those, empty 'stats = ItemStats()': {explicit_stats_empty}")

    # show 3 sample full ItemDefinition blocks so we can see exact formatting
    lines_out.append("  --- 3 sample full blocks ---")
    sample_matches = list(re.finditer(r"ItemDefinition\([^)]*(?:\([^)]*\)[^)]*)*\)", content))[:3]
    for sm in sample_matches:
        lines_out.append("  >>> " + sm.group(0).replace("\n", "\n      "))
        lines_out.append("")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
