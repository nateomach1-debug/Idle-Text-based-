#!/usr/bin/env python3
"""
Market persistence, part 2: GameStateRepository.kt

Extends save()/load()/SavedGameState with marketAccounts, marketOrders,
and marketPriceHistory, mirroring the existing JSON serialization pattern
used for accounts/characters/skills/etc. exactly. A PlayerEconomyAccount's
escrow inventory (Map<String, Int>) is stored as a nested JSON object.

Run from repo root:
    python3 apply_market_persistence_repository.py
"""
import sys
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/GameStateRepository.kt")


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

    if "marketAccounts" in text:
        fail("marketAccounts already present -- patch may already be applied")

    # 1. save() signature
    text = replace_once(
        text,
        (
            "        inventoryItems: List<InventorySlotExport>,\n"
            "        equippedSlots: List<EquippedSlotExport>\n"
            "    ) {\n"
        ),
        (
            "        inventoryItems: List<InventorySlotExport>,\n"
            "        equippedSlots: List<EquippedSlotExport>,\n"
            "        marketAccounts: List<PlayerEconomyAccountExport>,\n"
            "        marketOrders: List<MarketOrderExport>,\n"
            "        marketPriceHistory: List<PriceHistoryExport>\n"
            "    ) {\n"
        ),
        "save() signature",
    )

    # 2. save() body: serialize the three new lists before writing the file
    text = replace_once(
        text,
        (
            "        root.put(\"equippedSlots\", equippedArray)\n"
            "\n"
            "        saveFile.writeText(root.toString())\n"
        ),
        (
            "        root.put(\"equippedSlots\", equippedArray)\n"
            "\n"
            "        val marketAccountsArray = JSONArray()\n"
            "        marketAccounts.forEach { acc ->\n"
            "            val obj = JSONObject()\n"
            "            obj.put(\"characterId\", acc.characterId)\n"
            "            obj.put(\"accountId\", acc.accountId)\n"
            "            obj.put(\"isMainCharacter\", acc.isMainCharacter)\n"
            "            obj.put(\"currencyBalance\", acc.currencyBalance)\n"
            "            val inventoryObj = JSONObject()\n"
            "            acc.inventory.forEach { (itemId, qty) -> inventoryObj.put(itemId, qty) }\n"
            "            obj.put(\"inventory\", inventoryObj)\n"
            "            marketAccountsArray.put(obj)\n"
            "        }\n"
            "        root.put(\"marketAccounts\", marketAccountsArray)\n"
            "\n"
            "        val marketOrdersArray = JSONArray()\n"
            "        marketOrders.forEach { order ->\n"
            "            val obj = JSONObject()\n"
            "            obj.put(\"id\", order.id)\n"
            "            obj.put(\"characterId\", order.characterId)\n"
            "            obj.put(\"itemId\", order.itemId)\n"
            "            obj.put(\"side\", order.side)\n"
            "            obj.put(\"pricePerUnit\", order.pricePerUnit)\n"
            "            obj.put(\"originalQuantity\", order.originalQuantity)\n"
            "            obj.put(\"remainingQuantity\", order.remainingQuantity)\n"
            "            obj.put(\"status\", order.status)\n"
            "            obj.put(\"createdAt\", order.createdAt)\n"
            "            marketOrdersArray.put(obj)\n"
            "        }\n"
            "        root.put(\"marketOrders\", marketOrdersArray)\n"
            "\n"
            "        val marketPriceHistoryArray = JSONArray()\n"
            "        marketPriceHistory.forEach { entry ->\n"
            "            val obj = JSONObject()\n"
            "            obj.put(\"itemId\", entry.itemId)\n"
            "            obj.put(\"pricePerUnit\", entry.pricePerUnit)\n"
            "            obj.put(\"quantity\", entry.quantity)\n"
            "            obj.put(\"executedAt\", entry.executedAt)\n"
            "            marketPriceHistoryArray.put(obj)\n"
            "        }\n"
            "        root.put(\"marketPriceHistory\", marketPriceHistoryArray)\n"
            "\n"
            "        saveFile.writeText(root.toString())\n"
        ),
        "save() body serialization",
    )

    # 3. load(): parse the three new lists before returning SavedGameState
    text = replace_once(
        text,
        (
            "        return SavedGameState(accounts, characters, skills, skillingQueues, craftingQueues, lastSeen, inventoryItems, equippedSlots)\n"
            "    }\n"
            "}\n"
        ),
        (
            "        val marketAccounts = mutableListOf<PlayerEconomyAccountExport>()\n"
            "        val marketAccountsArray = root.optJSONArray(\"marketAccounts\") ?: JSONArray()\n"
            "        for (i in 0 until marketAccountsArray.length()) {\n"
            "            val obj = marketAccountsArray.getJSONObject(i)\n"
            "            val inventoryObj = obj.optJSONObject(\"inventory\") ?: JSONObject()\n"
            "            val inventory = mutableMapOf<String, Int>()\n"
            "            inventoryObj.keys().forEach { key -> inventory[key] = inventoryObj.getInt(key) }\n"
            "            marketAccounts.add(\n"
            "                PlayerEconomyAccountExport(\n"
            "                    characterId = obj.getString(\"characterId\"),\n"
            "                    accountId = obj.getString(\"accountId\"),\n"
            "                    isMainCharacter = obj.getBoolean(\"isMainCharacter\"),\n"
            "                    currencyBalance = obj.getLong(\"currencyBalance\"),\n"
            "                    inventory = inventory\n"
            "                )\n"
            "            )\n"
            "        }\n"
            "\n"
            "        val marketOrders = mutableListOf<MarketOrderExport>()\n"
            "        val marketOrdersArray = root.optJSONArray(\"marketOrders\") ?: JSONArray()\n"
            "        for (i in 0 until marketOrdersArray.length()) {\n"
            "            val obj = marketOrdersArray.getJSONObject(i)\n"
            "            marketOrders.add(\n"
            "                MarketOrderExport(\n"
            "                    id = obj.getString(\"id\"),\n"
            "                    characterId = obj.getString(\"characterId\"),\n"
            "                    itemId = obj.getString(\"itemId\"),\n"
            "                    side = obj.getString(\"side\"),\n"
            "                    pricePerUnit = obj.getLong(\"pricePerUnit\"),\n"
            "                    originalQuantity = obj.getInt(\"originalQuantity\"),\n"
            "                    remainingQuantity = obj.getInt(\"remainingQuantity\"),\n"
            "                    status = obj.getString(\"status\"),\n"
            "                    createdAt = obj.getString(\"createdAt\")\n"
            "                )\n"
            "            )\n"
            "        }\n"
            "\n"
            "        val marketPriceHistory = mutableListOf<PriceHistoryExport>()\n"
            "        val marketPriceHistoryArray = root.optJSONArray(\"marketPriceHistory\") ?: JSONArray()\n"
            "        for (i in 0 until marketPriceHistoryArray.length()) {\n"
            "            val obj = marketPriceHistoryArray.getJSONObject(i)\n"
            "            marketPriceHistory.add(\n"
            "                PriceHistoryExport(\n"
            "                    itemId = obj.getString(\"itemId\"),\n"
            "                    pricePerUnit = obj.getLong(\"pricePerUnit\"),\n"
            "                    quantity = obj.getInt(\"quantity\"),\n"
            "                    executedAt = obj.getString(\"executedAt\")\n"
            "                )\n"
            "            )\n"
            "        }\n"
            "\n"
            "        return SavedGameState(\n"
            "            accounts, characters, skills, skillingQueues, craftingQueues, lastSeen, inventoryItems, equippedSlots,\n"
            "            marketAccounts, marketOrders, marketPriceHistory\n"
            "        )\n"
            "    }\n"
            "}\n"
        ),
        "load() body parsing + return",
    )

    # 4. SavedGameState data class: add the three new fields
    text = replace_once(
        text,
        (
            "    val inventoryItems: List<InventorySlotExport>,\n"
            "    val equippedSlots: List<EquippedSlotExport>\n"
            ")\n"
        ),
        (
            "    val inventoryItems: List<InventorySlotExport>,\n"
            "    val equippedSlots: List<EquippedSlotExport>,\n"
            "    val marketAccounts: List<PlayerEconomyAccountExport>,\n"
            "    val marketOrders: List<MarketOrderExport>,\n"
            "    val marketPriceHistory: List<PriceHistoryExport>\n"
            ")\n"
        ),
        "SavedGameState data class",
    )

    if text == original:
        fail("no changes were made -- aborting")

    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
