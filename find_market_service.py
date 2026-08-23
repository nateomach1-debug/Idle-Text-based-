"""
Discovery script - NOT a code-modifying patch.

Finds MarketService.kt (or wherever market/order logic lives) in full,
plus the Order/MarketAccount/PriceHistory data class definitions, to
understand how buy/sell orders currently work locally before designing
a Supabase-backed shared order book.

Writes one new file: repo_market_service_full.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_market_service_full.txt"

lines_out = []

candidates = ["MarketService.kt", "MarketSystem.kt", "TradingSystem.kt"]
found_file = None
for c in candidates:
    if os.path.isfile(os.path.join(BASE, c)):
        found_file = c
        break

if found_file:
    path = os.path.join(BASE, found_file)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    lines_out.append("=" * 70)
    lines_out.append(f"{found_file} (total lines: {len(content.splitlines())})")
    lines_out.append("=" * 70)
    lines_out.append(content)
else:
    lines_out.append("No MarketService/MarketSystem/TradingSystem.kt found by direct name.")
    lines_out.append("Searching all files for 'class MarketService' or 'MarketOrder' instead...")
    for fname in sorted(os.listdir(BASE)):
        if not fname.endswith(".kt"):
            continue
        fpath = os.path.join(BASE, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        if "MarketService" in content or "MarketOrder" in content or "class Market" in content:
            lines_out.append(f"\nFound relevant content in: {fname} (total lines: {len(content.splitlines())})")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
