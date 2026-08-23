"""
Discovery script - NOT a code-modifying patch.

Finds every GameViewModel.kt call site touching marketService
(registerAccount, placeBuyOrder, placeSellOrder, sellToVendor,
currencyBalance reads, refreshCurrency, etc.) to understand how the
market's internal account bookkeeping connects to the real
InventoryService/currency systems the rest of the game uses.

Writes one new file: repo_market_wiring.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_market_wiring.txt"

path = os.path.join(BASE, "GameViewModel.kt")
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

lines_out = []
lines_out.append("=" * 70)
lines_out.append("GameViewModel.kt - all marketService / refreshCurrency / currencyBalance references")
lines_out.append("=" * 70)

keywords = ["marketService", "refreshCurrency", "currencyBalance", "PlayerEconomyAccount"]

matched = set()
for i, line in enumerate(lines):
    if any(k in line for k in keywords):
        matched.add(i)

for i in sorted(matched):
    start = max(0, i - 2)
    end = min(len(lines), i + 6)
    lines_out.append(f"\n--- around line {i+1} ---")
    for j in range(start, end):
        marker = ">> " if j == i else "   "
        lines_out.append(f"{marker}{j+1}: {lines[j].rstrip()}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
