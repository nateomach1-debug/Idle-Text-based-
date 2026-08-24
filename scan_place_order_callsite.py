"""
Discovery script - NOT a code-modifying patch.

Finds every placeBuyOrder(/placeSellOrder( call site anywhere in
MainActivity.kt (likely in a separate order-placement dialog gated by
selectedMarketItemId, not inside the main MarketScreen(...) call).

Writes one new file: repo_place_order_callsite.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_place_order_callsite.txt"

path = os.path.join(BASE, "MainActivity.kt")
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

lines_out = []
lines_out.append("=" * 70)
lines_out.append("MainActivity.kt - placeBuyOrder/placeSellOrder/selectedMarketItemId references")
lines_out.append("=" * 70)

for i, line in enumerate(lines):
    if "placeBuyOrder" in line or "placeSellOrder" in line or "selectedMarketItemId" in line:
        start = max(0, i - 5)
        end = min(len(lines), i + 20)
        lines_out.append(f"\n--- around line {i+1} ---")
        for j in range(start, end):
            lines_out.append(f"{j+1}: {lines[j].rstrip()}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
