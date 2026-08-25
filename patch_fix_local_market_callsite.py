EMS = "app/src/main/kotlin/com/yourname/idlerpg/EconomyMarketSystem.kt"

with open(EMS, "r", encoding="utf-8") as f:
    content = f.read()

old = """            val bestBuy = buyOrders
                .filter { it.itemId == itemId && it.remainingQuantity > 0 }
                .maxOfOrNull { it.pricePerUnit }
            val bestSell = sellOrders
                .filter { it.itemId == itemId && it.remainingQuantity > 0 }
                .minOfOrNull { it.pricePerUnit }
            MarketPriceSummary(itemId, bestBuy, bestSell)"""

new = """            val bestBuy = buyOrders
                .filter { it.itemId == itemId && it.remainingQuantity > 0 }
                .maxOfOrNull { it.pricePerUnit }
            val bestBuyQty = buyOrders
                .filter { it.itemId == itemId && it.remainingQuantity > 0 && it.pricePerUnit == bestBuy }
                .sumOf { it.remainingQuantity }
            val bestSell = sellOrders
                .filter { it.itemId == itemId && it.remainingQuantity > 0 }
                .minOfOrNull { it.pricePerUnit }
            val bestSellQty = sellOrders
                .filter { it.itemId == itemId && it.remainingQuantity > 0 && it.pricePerUnit == bestSell }
                .sumOf { it.remainingQuantity }
            MarketPriceSummary(itemId, bestBuy, if (bestBuy != null) bestBuyQty else null, bestSell, if (bestSell != null) bestSellQty else null)"""

count = content.count(old)
assert count == 1, f"expected exactly 1 match, found {count}"
content = content.replace(old, new)

with open(EMS, "w", encoding="utf-8") as f:
    f.write(content)

print(f"OK: patched EconomyMarketSystem.kt ({len(old)} -> {len(new)} chars)")
