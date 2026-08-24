"""
Discovery script - NOT a code-modifying patch.

Finds the MarketScreen(...) call site in MainActivity.kt, including
onPlaceBuyOrder/onPlaceSellOrder/onCancelOrder/onSellToVendor callback
wiring, so the suspend-conversion patch can be written against exact
current text.

Writes one new file: repo_market_screen_callsite.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_market_screen_callsite.txt"

path = os.path.join(BASE, "MainActivity.kt")
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

lines_out = []
lines_out.append("=" * 70)
lines_out.append(f"MainActivity.kt (total lines: {len(lines)}) - MarketScreen callsite")
lines_out.append("=" * 70)

for i, line in enumerate(lines):
    if "MarketScreen(" in line:
        start = max(0, i - 3)
        end = min(len(lines), i + 60)
        lines_out.append(f"\n--- around line {i+1} ---")
        for j in range(start, end):
            lines_out.append(f"{j+1}: {lines[j].rstrip()}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
