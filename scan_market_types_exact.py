"""
Discovery script - NOT a code-modifying patch.

Gets exact type definitions for MarketListing, MarketOrder, OrderSide
(wherever they live - likely SharedTypes.kt or EconomyMarketSystem.kt),
plus the _marketListings/_myBuyOrders/_mySellOrders/_currency StateFlow
declarations in GameViewModel.kt, to avoid type-mismatch build failures
in the market-sync rewiring patch.

Writes one new file: repo_market_types_exact.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_market_types_exact.txt"

lines_out = []

for filename in ["SharedTypes.kt", "EconomyMarketSystem.kt"]:
    path = os.path.join(BASE, filename)
    if not os.path.isfile(path):
        continue
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.splitlines()
    lines_out.append(f"\n{'=' * 70}\n{filename}\n{'=' * 70}")
    for i, line in enumerate(lines):
        if any(k in line for k in ["data class MarketListing", "data class MarketOrder", "enum class OrderSide", "enum class OrderStatus", "class PlayerEconomyAccount"]):
            for j in range(i, min(len(lines), i + 10)):
                lines_out.append(f"{j+1}: {lines[j]}")
            lines_out.append("")

path = os.path.join(BASE, "GameViewModel.kt")
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()
lines_out.append(f"\n{'=' * 70}\nGameViewModel.kt - market StateFlow declarations\n{'=' * 70}")
for i, line in enumerate(lines):
    if any(k in line for k in ["_marketListings", "_myBuyOrders", "_mySellOrders", "_currency ", "marketListings ", "myBuyOrders ", "mySellOrders ", "val currency "]):
        lines_out.append(f"{i+1}: {line.rstrip()}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
