#!/usr/bin/env python3
"""
Market persistence, part 1: EconomyMarketSystem.kt

Root cause of "gold resets / sell orders vanish on restart": MarketService's
entire state (PlayerEconomyAccount balances, open buy/sell orders, price
history) lives purely in memory -- it was never wired into
GameStateRepository's save/load cycle the way skills/inventory/queues are.

Adds export/import types + methods, mirroring the existing pattern
(SkillExport, InventorySlotExport, etc.):
  - PlayerEconomyAccountExport / exportAccounts() / restoreAccount()
  - MarketOrderExport / exportOrders() / restoreOrder()
  - PriceHistoryExport / exportPriceHistory() / restorePriceHistoryEntry()

Run from repo root, AFTER apply_market_backend.py (this appends right
after allListings()):
    python3 apply_market_persistence_backend.py
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

    if "PlayerEconomyAccountExport" in text:
        fail("PlayerEconomyAccountExport already present -- patch may already be applied")

    old = (
        "            MarketPriceSummary(itemId, bestBuy, bestSell)\n"
        "        }\n"
        "    }\n"
        "}\n"
        "\n"
        "data class MarketPriceSummary(val itemId: String, val bestBuyPrice: Long?, val bestSellPrice: Long?)\n"
    )
    new = (
        "            MarketPriceSummary(itemId, bestBuy, bestSell)\n"
        "        }\n"
        "    }\n"
        "\n"
        "    // ---------------- Persistence ----------------\n"
        "\n"
        "    fun exportAccounts(): List<PlayerEconomyAccountExport> = accounts.values.map {\n"
        "        PlayerEconomyAccountExport(\n"
        "            characterId = it.characterId,\n"
        "            accountId = it.accountId,\n"
        "            isMainCharacter = it.isMainCharacter,\n"
        "            currencyBalance = it.currencyBalance,\n"
        "            inventory = it.inventory.toMap()\n"
        "        )\n"
        "    }\n"
        "\n"
        "    fun restoreAccount(export: PlayerEconomyAccountExport) {\n"
        "        accounts[export.characterId] = PlayerEconomyAccount(\n"
        "            characterId = export.characterId,\n"
        "            accountId = export.accountId,\n"
        "            isMainCharacter = export.isMainCharacter,\n"
        "            currencyBalance = export.currencyBalance,\n"
        "            inventory = export.inventory.toMutableMap()\n"
        "        )\n"
        "    }\n"
        "\n"
        "    fun exportOrders(): List<MarketOrderExport> = (buyOrders + sellOrders).map {\n"
        "        MarketOrderExport(\n"
        "            id = it.id,\n"
        "            characterId = it.characterId,\n"
        "            itemId = it.itemId,\n"
        "            side = it.side.name,\n"
        "            pricePerUnit = it.pricePerUnit,\n"
        "            originalQuantity = it.originalQuantity,\n"
        "            remainingQuantity = it.remainingQuantity,\n"
        "            status = it.status.name,\n"
        "            createdAt = it.createdAt.toString()\n"
        "        )\n"
        "    }\n"
        "\n"
        "    fun restoreOrder(export: MarketOrderExport) {\n"
        "        val order = MarketOrder(\n"
        "            id = export.id,\n"
        "            characterId = export.characterId,\n"
        "            itemId = export.itemId,\n"
        "            side = OrderSide.valueOf(export.side),\n"
        "            pricePerUnit = export.pricePerUnit,\n"
        "            originalQuantity = export.originalQuantity,\n"
        "            remainingQuantity = export.remainingQuantity,\n"
        "            status = OrderStatus.valueOf(export.status),\n"
        "            createdAt = Instant.parse(export.createdAt)\n"
        "        )\n"
        "        if (order.side == OrderSide.BUY) buyOrders.add(order) else sellOrders.add(order)\n"
        "    }\n"
        "\n"
        "    fun exportPriceHistory(): List<PriceHistoryExport> = priceHistory.map {\n"
        "        PriceHistoryExport(\n"
        "            itemId = it.itemId,\n"
        "            pricePerUnit = it.pricePerUnit,\n"
        "            quantity = it.quantity,\n"
        "            executedAt = it.executedAt.toString()\n"
        "        )\n"
        "    }\n"
        "\n"
        "    fun restorePriceHistoryEntry(export: PriceHistoryExport) {\n"
        "        priceHistory.add(\n"
        "            PriceHistoryEntry(\n"
        "                itemId = export.itemId,\n"
        "                pricePerUnit = export.pricePerUnit,\n"
        "                quantity = export.quantity,\n"
        "                executedAt = Instant.parse(export.executedAt)\n"
        "            )\n"
        "        )\n"
        "    }\n"
        "}\n"
        "\n"
        "data class MarketPriceSummary(val itemId: String, val bestBuyPrice: Long?, val bestSellPrice: Long?)\n"
        "\n"
        "data class PlayerEconomyAccountExport(\n"
        "    val characterId: String,\n"
        "    val accountId: String,\n"
        "    val isMainCharacter: Boolean,\n"
        "    val currencyBalance: Long,\n"
        "    val inventory: Map<String, Int>\n"
        ")\n"
        "\n"
        "data class MarketOrderExport(\n"
        "    val id: String,\n"
        "    val characterId: String,\n"
        "    val itemId: String,\n"
        "    val side: String,\n"
        "    val pricePerUnit: Long,\n"
        "    val originalQuantity: Int,\n"
        "    val remainingQuantity: Int,\n"
        "    val status: String,\n"
        "    val createdAt: String\n"
        ")\n"
        "\n"
        "data class PriceHistoryExport(\n"
        "    val itemId: String,\n"
        "    val pricePerUnit: Long,\n"
        "    val quantity: Int,\n"
        "    val executedAt: String\n"
        ")\n"
    )

    count = text.count(old)
    if count != 1:
        fail(f"expected exactly 1 occurrence of the target block, found {count}")

    text = text.replace(old, new, 1)
    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
