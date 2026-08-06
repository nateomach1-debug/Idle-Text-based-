#!/usr/bin/env python3
"""
Market buy/sell wiring, part 1: EconomyMarketSystem.kt

Adds a new public read-only query, allListings(), that aggregates the
current best buy/sell price per item across all open orders. This is the
one new piece of surface area MarketService needs -- everything else
(placeBuyOrder, placeSellOrder, cancelOrder, sellToVendor, openOrdersFor,
priceHistoryFor) already exists and is untouched by this patch.

Returns MarketPriceSummary (itemId + prices only) rather than the UI-layer
MarketListingSummary, to keep this backend file free of ui.screens
imports -- GameViewModel/MainActivity map it to MarketListingSummary
(adding the display name via ItemCatalog).

Run from repo root:
    python3 apply_market_backend.py
"""
import sys
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/EconomyMarketSystem.kt")


def fail(msg):
    print(f"FAILED: {msg}")
    sys.exit(1)


def main():
    if not TARGET.exists():
        fail(f"{TARGET} not found -- run this from the repo root")

    text = TARGET.read_text()

    if "MarketPriceSummary" in text:
        fail("MarketPriceSummary already present -- patch may already be applied")

    old = (
        "    // ---------------- Public-safe queries ----------------\n"
        "\n"
        "    fun priceHistoryFor(itemId: String): List<PriceHistoryEntry> = priceHistory.filter { it.itemId == itemId }\n"
        "\n"
        "    fun openOrdersFor(characterId: String): List<MarketOrder> =\n"
        "        (buyOrders + sellOrders).filter { it.characterId == characterId && it.status != OrderStatus.CANCELLED }\n"
        "}\n"
    )
    new = (
        "    // ---------------- Public-safe queries ----------------\n"
        "\n"
        "    fun priceHistoryFor(itemId: String): List<PriceHistoryEntry> = priceHistory.filter { it.itemId == itemId }\n"
        "\n"
        "    fun openOrdersFor(characterId: String): List<MarketOrder> =\n"
        "        (buyOrders + sellOrders).filter { it.characterId == characterId && it.status != OrderStatus.CANCELLED }\n"
        "\n"
        "    fun allListings(): List<MarketPriceSummary> {\n"
        "        val itemIds = (buyOrders + sellOrders)\n"
        "            .filter { it.remainingQuantity > 0 }\n"
        "            .map { it.itemId }\n"
        "            .distinct()\n"
        "        return itemIds.map { itemId ->\n"
        "            val bestBuy = buyOrders\n"
        "                .filter { it.itemId == itemId && it.remainingQuantity > 0 }\n"
        "                .maxOfOrNull { it.pricePerUnit }\n"
        "            val bestSell = sellOrders\n"
        "                .filter { it.itemId == itemId && it.remainingQuantity > 0 }\n"
        "                .minOfOrNull { it.pricePerUnit }\n"
        "            MarketPriceSummary(itemId, bestBuy, bestSell)\n"
        "        }\n"
        "    }\n"
        "}\n"
        "\n"
        "data class MarketPriceSummary(val itemId: String, val bestBuyPrice: Long?, val bestSellPrice: Long?)\n"
    )

    count = text.count(old)
    if count != 1:
        fail(f"expected exactly 1 occurrence of the target block, found {count}")

    text = text.replace(old, new, 1)
    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
