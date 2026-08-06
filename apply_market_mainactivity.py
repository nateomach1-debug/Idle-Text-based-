#!/usr/bin/env python3
"""
Market buy/sell wiring, part 3: MainActivity.kt

- Adds a formatTimeAgo() helper (java.time.Duration import) for the order
  book's recent-trades list.
- Removes demoMarketListings()/demoOrderBook()/demoMyBuyOrders()/
  demoMySellOrders() -- no longer used.
- Replaces the AppDestination.MARKET block: MarketScreen and
  OrderBookScreen now get real data from GameViewModel's
  marketListings/myBuyOrders/mySellOrders StateFlows and
  marketService.priceHistoryFor(), mapped into the UI-layer summary types.
  onPlaceOrder/onCancelOrder/onSellToVendor call the new GameViewModel
  wrapper functions instead of being no-ops.

Run from repo root, AFTER apply_market_backend.py and
apply_market_viewmodel.py:
    python3 apply_market_mainactivity.py
Then rebuild:
    ./gradlew assembleDebug --console=plain --no-daemon --no-configuration-cache
"""
import sys
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")


def fail(msg):
    print(f"FAILED: {msg}")
    sys.exit(1)


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        fail(f"expected exactly 1 occurrence of [{label}], found {count}")
    return text.replace(old, new, 1)


def main():
    if not TARGET.exists():
        fail(f"{TARGET} not found -- run this from the repo root")

    text = TARGET.read_text()
    original = text

    if "formatTimeAgo" in text:
        fail("formatTimeAgo already present -- patch may already be applied")

    # 1. Duration import
    text = replace_once(
        text,
        "import java.time.Instant\n",
        "import java.time.Duration\nimport java.time.Instant\n",
        "import block",
    )

    # 2. Replace the four demo market functions with formatTimeAgo()
    text = replace_once(
        text,
        (
            "private fun demoMarketListings(): List<MarketListingSummary> = listOf(\n"
            "    MarketListingSummary(\"iron_ore\", \"Iron Ore\", bestBuyPrice = 9, bestSellPrice = 11),\n"
            "    MarketListingSummary(\"steel_bar\", \"Steel Bar\", bestBuyPrice = 40, bestSellPrice = 48),\n"
            "    MarketListingSummary(\"minor_healing_potion\", \"Minor Healing Potion\", bestBuyPrice = 4, bestSellPrice = 6)\n"
            ")\n"
            "\n"
            "private fun demoOrderBook(itemId: String): ItemOrderBookDetail {\n"
            "    val listing = demoMarketListings().find { it.itemId == itemId }\n"
            "    return ItemOrderBookDetail(\n"
            "        itemId = itemId,\n"
            "        displayName = listing?.displayName ?: itemId,\n"
            "        bestBuyPrice = listing?.bestBuyPrice,\n"
            "        bestSellPrice = listing?.bestSellPrice,\n"
            "        recentTrades = listOf(\n"
            "            PriceHistoryRow(11, 20, \"5m ago\"),\n"
            "            PriceHistoryRow(10, 15, \"22m ago\"),\n"
            "            PriceHistoryRow(12, 5, \"1h ago\")\n"
            "        )\n"
            "    )\n"
            "}\n"
            "\n"
            "private fun demoMyBuyOrders(): List<MarketOrderSummary> = listOf(\n"
            "    MarketOrderSummary(\"order1\", \"iron_ore\", \"Iron Ore\", 9, 30)\n"
            ")\n"
            "\n"
            "private fun demoMySellOrders(): List<MarketOrderSummary> = listOf(\n"
            "    MarketOrderSummary(\"order2\", \"steel_bar\", \"Steel Bar\", 48, 8)\n"
            ")\n"
        ),
        (
            "private fun formatTimeAgo(instant: Instant): String {\n"
            "    val seconds = Duration.between(instant, Instant.now()).seconds.coerceAtLeast(0)\n"
            "    return when {\n"
            "        seconds < 60 -> seconds.toString() + \"s ago\"\n"
            "        seconds < 3600 -> (seconds / 60).toString() + \"m ago\"\n"
            "        seconds < 86400 -> (seconds / 3600).toString() + \"h ago\"\n"
            "        else -> (seconds / 86400).toString() + \"d ago\"\n"
            "    }\n"
            "}\n"
        ),
        "demo market functions -> formatTimeAgo",
    )

    # 3. Replace the AppDestination.MARKET block with real data wiring
    text = replace_once(
        text,
        (
            "                            AppDestination.MARKET -> {\n"
            "                                val itemId = selectedMarketItemId\n"
            "                                if (itemId != null) {\n"
            "                                    OrderBookScreen(\n"
            "                                        detail = demoOrderBook(itemId),\n"
            "                                        prefilledQuantity = prefilledSellQuantity,\n"
            "                                        onBack = { selectedMarketItemId = null; prefilledSellQuantity = null },\n"
            "                                        onPlaceOrder = { _, _, _ -> selectedMarketItemId = null; prefilledSellQuantity = null }\n"
            "                                    )\n"
            "                                } else {\n"
            "                                    MarketScreen(\n"
            "                                        currentTab = marketTab,\n"
            "                                        onTabSelected = { marketTab = it },\n"
            "                                        listings = demoMarketListings(),\n"
            "                                        showingBuyOrders = showingBuyOrders,\n"
            "                                        onToggleBrowseMode = { showingBuyOrders = !showingBuyOrders },\n"
            "                                        onItemSelected = { selectedMarketItemId = it },\n"
            "                                        myBuyOrders = demoMyBuyOrders(),\n"
            "                                        mySellOrders = demoMySellOrders(),\n"
            "                                        onCancelOrder = { },\n"
            "                                        vendorSellableItems = inventoryItems,\n"
            "                                        onSellToVendor = { _, _ -> }\n"
            "                                    )\n"
            "                                }\n"
            "                            }\n"
        ),
        (
            "                            AppDestination.MARKET -> {\n"
            "                                val marketPriceSummaries by gameViewModel.marketListings.collectAsState()\n"
            "                                val myBuyOrdersRaw by gameViewModel.myBuyOrders.collectAsState()\n"
            "                                val mySellOrdersRaw by gameViewModel.mySellOrders.collectAsState()\n"
            "                                val marketListingsUi = remember(marketPriceSummaries) {\n"
            "                                    marketPriceSummaries.map {\n"
            "                                        MarketListingSummary(\n"
            "                                            itemId = it.itemId,\n"
            "                                            displayName = ItemCatalog.find(it.itemId)?.name ?: it.itemId,\n"
            "                                            bestBuyPrice = it.bestBuyPrice,\n"
            "                                            bestSellPrice = it.bestSellPrice\n"
            "                                        )\n"
            "                                    }\n"
            "                                }\n"
            "                                val myBuyOrdersUi = remember(myBuyOrdersRaw) {\n"
            "                                    myBuyOrdersRaw.map {\n"
            "                                        MarketOrderSummary(\n"
            "                                            orderId = it.id,\n"
            "                                            itemId = it.itemId,\n"
            "                                            displayName = ItemCatalog.find(it.itemId)?.name ?: it.itemId,\n"
            "                                            pricePerUnit = it.pricePerUnit,\n"
            "                                            remainingQuantity = it.remainingQuantity\n"
            "                                        )\n"
            "                                    }\n"
            "                                }\n"
            "                                val mySellOrdersUi = remember(mySellOrdersRaw) {\n"
            "                                    mySellOrdersRaw.map {\n"
            "                                        MarketOrderSummary(\n"
            "                                            orderId = it.id,\n"
            "                                            itemId = it.itemId,\n"
            "                                            displayName = ItemCatalog.find(it.itemId)?.name ?: it.itemId,\n"
            "                                            pricePerUnit = it.pricePerUnit,\n"
            "                                            remainingQuantity = it.remainingQuantity\n"
            "                                        )\n"
            "                                    }\n"
            "                                }\n"
            "\n"
            "                                val itemId = selectedMarketItemId\n"
            "                                if (itemId != null) {\n"
            "                                    val orderBookDetail = remember(itemId, marketPriceSummaries) {\n"
            "                                        val summary = marketPriceSummaries.find { it.itemId == itemId }\n"
            "                                        ItemOrderBookDetail(\n"
            "                                            itemId = itemId,\n"
            "                                            displayName = ItemCatalog.find(itemId)?.name ?: itemId,\n"
            "                                            bestBuyPrice = summary?.bestBuyPrice,\n"
            "                                            bestSellPrice = summary?.bestSellPrice,\n"
            "                                            recentTrades = gameViewModel.marketService.priceHistoryFor(itemId)\n"
            "                                                .sortedByDescending { it.executedAt }\n"
            "                                                .take(10)\n"
            "                                                .map { PriceHistoryRow(it.pricePerUnit, it.quantity, formatTimeAgo(it.executedAt)) }\n"
            "                                        )\n"
            "                                    }\n"
            "                                    OrderBookScreen(\n"
            "                                        detail = orderBookDetail,\n"
            "                                        prefilledQuantity = prefilledSellQuantity,\n"
            "                                        onBack = { selectedMarketItemId = null; prefilledSellQuantity = null },\n"
            "                                        onPlaceOrder = { side, qty, price ->\n"
            "                                            if (side == OrderSideUi.BUY) {\n"
            "                                                gameViewModel.placeBuyOrder(itemId, qty, price)\n"
            "                                            } else {\n"
            "                                                gameViewModel.placeSellOrder(itemId, qty, price)\n"
            "                                            }\n"
            "                                            selectedMarketItemId = null\n"
            "                                            prefilledSellQuantity = null\n"
            "                                        }\n"
            "                                    )\n"
            "                                } else {\n"
            "                                    MarketScreen(\n"
            "                                        currentTab = marketTab,\n"
            "                                        onTabSelected = { marketTab = it },\n"
            "                                        listings = marketListingsUi,\n"
            "                                        showingBuyOrders = showingBuyOrders,\n"
            "                                        onToggleBrowseMode = { showingBuyOrders = !showingBuyOrders },\n"
            "                                        onItemSelected = { selectedMarketItemId = it },\n"
            "                                        myBuyOrders = myBuyOrdersUi,\n"
            "                                        mySellOrders = mySellOrdersUi,\n"
            "                                        onCancelOrder = { orderId -> gameViewModel.cancelMarketOrder(orderId) },\n"
            "                                        vendorSellableItems = inventoryItems,\n"
            "                                        onSellToVendor = { sellItemId, quantity ->\n"
            "                                            gameViewModel.sellItemToVendor(sellItemId, quantity)\n"
            "                                        }\n"
            "                                    )\n"
            "                                }\n"
            "                            }\n"
        ),
        "AppDestination.MARKET block",
    )

    if text == original:
        fail("no changes were made -- aborting")

    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")
    print("Run: git diff", TARGET, "to verify before rebuilding.")


if __name__ == "__main__":
    main()
