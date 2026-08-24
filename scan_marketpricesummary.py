"""
Discovery script - NOT a code-modifying patch.

Finds the exact MarketPriceSummary data class definition (used by
_marketListings StateFlow) across all files.

Writes one new file: repo_marketpricesummary_exact.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_marketpricesummary_exact.txt"

lines_out = []

for fname in sorted(os.listdir(BASE)):
    if not fname.endswith(".kt"):
        continue
    fpath = os.path.join(BASE, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if "MarketPriceSummary" in line:
            start = max(0, i - 1)
            end = min(len(lines), i + 8)
            lines_out.append(f"\n--- {fname} around line {i+1} ---")
            for j in range(start, end):
                lines_out.append(f"{j+1}: {lines[j].rstrip()}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
