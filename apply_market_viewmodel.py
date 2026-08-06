#!/usr/bin/env python3
"""
Market buy/sell wiring, part 2: GameViewModel.kt

- New marketService/economyMonitoring instances.
- New StateFlows: marketListings, myBuyOrders, mySellOrders.
- selectCharacter() now registers a PlayerEconomyAccount (starting Gold = 0,
  isMainCharacter looked up from the real Character record) the first time
  a character is selected, and does an initial market refresh.
- refreshCurrency() now sources Gold from marketService's
  PlayerEconomyAccount.currencyBalance instead of the currently-inert
  Account.softCurrency (Gems still come from Account.premiumCurrency).
- New wrapper functions: placeBuyOrder, placeSellOrder, cancelMarketOrder,
  sellItemToVendor. Each syncs PlayerEconomyAccount's internal escrow
  ledger against the real InventoryService, so items actually move in/out
  of the player's real bag rather than a disconnected shadow inventory.

Run from repo root, AFTER apply_market_backend.py (this file uses
MarketPriceSummary and allListings(), defined there):
    python3 apply_market_viewmodel.py
"""
import sys
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")


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

    if "marketService" in text:
        fail("marketService already present -- patch may already be applied")

    # 1. New services + StateFlows, right after _equippedItems/equippedItems
    text = replace_once(
        text,
        (
            "    private val _equippedItems = MutableStateFlow<Map<EquipSlot, String>>(emptyMap())\n"
            "    val equippedItems: StateFlow<Map<EquipSlot, String>> = _equippedItems.asStateFlow()\n"
        ),
        (
            "    private val _equippedItems = MutableStateFlow<Map<EquipSlot, String>>(emptyMap())\n"
            "    val equippedItems: StateFlow<Map<EquipSlot, String>> = _equippedItems.asStateFlow()\n"
            "\n"
            "    val economyMonitoring = EconomyMonitoringService()\n"
            "    val marketService = MarketService(economyMonitoring)\n"
            "\n"
            "    private val _marketListings = MutableStateFlow<List<MarketPriceSummary>>(emptyList())\n"
            "    val marketListings: StateFlow<List<MarketPriceSummary>> = _marketListings.asStateFlow()\n"
            "\n"
            "    private val _myBuyOrders = MutableStateFlow<List<MarketOrder>>(emptyList())\n"
            "    val myBuyOrders: StateFlow<List<MarketOrder>> = _myBuyOrders.asStateFlow()\n"
            "\n"
            "    private val _mySellOrders = MutableStateFlow<List<MarketOrder>>(emptyList())\n"
            "    val mySellOrders: StateFlow<List<MarketOrder>> = _mySellOrders.asStateFlow()\n"
        ),
        "market service + StateFlow declarations",
    )

    # 2. selectCharacter(): register the market account + initial refresh
    text = replace_once(
        text,
        (
            "        offlineIdleService.recordLastSeen(characterId)\n"
            "        skillActionProgressSeconds = 0\n"
            "        craftActionProgressSeconds = 0\n"
            "        refreshSkills()\n"
            "        refreshInventory()\n"
            "        refreshActiveQueue()\n"
            "    }\n"
        ),
        (
            "        offlineIdleService.recordLastSeen(characterId)\n"
            "        skillActionProgressSeconds = 0\n"
            "        craftActionProgressSeconds = 0\n"
            "        refreshSkills()\n"
            "        refreshInventory()\n"
            "        refreshActiveQueue()\n"
            "\n"
            "        if (marketService.accountFor(characterId) == null) {\n"
            "            val character = accountService.charactersFor(_currentAccountId.value ?: \"\")\n"
            "                .find { it.id == characterId }\n"
            "            marketService.registerAccount(\n"
            "                PlayerEconomyAccount(\n"
            "                    characterId = characterId,\n"
            "                    accountId = _currentAccountId.value ?: \"\",\n"
            "                    isMainCharacter = character?.isMainCharacter ?: true,\n"
            "                    currencyBalance = 0L\n"
            "                )\n"
            "            )\n"
            "        }\n"
            "        refreshCurrency()\n"
            "        refreshMarketListings()\n"
            "        refreshMyOrders()\n"
            "    }\n"
        ),
        "selectCharacter() market account registration",
    )

    # 3. refreshCurrency(): source Gold from PlayerEconomyAccount instead of Account.softCurrency
    text = replace_once(
        text,
        (
            "    fun refreshCurrency() {\n"
            "        val accountId = _currentAccountId.value ?: return\n"
            "        val account = accountService.accountById(accountId) ?: return\n"
            "        _currency.value = account.softCurrency to account.premiumCurrency\n"
            "    }\n"
            "}\n"
        ),
        (
            "    fun refreshCurrency() {\n"
            "        val accountId = _currentAccountId.value ?: return\n"
            "        val account = accountService.accountById(accountId) ?: return\n"
            "        val characterId = _currentCharacterId.value\n"
            "        val gold = characterId?.let { marketService.accountFor(it)?.currencyBalance } ?: 0L\n"
            "        _currency.value = gold to account.premiumCurrency\n"
            "    }\n"
            "\n"
            "    // =========================================================\n"
            "    // MARKET\n"
            "    // =========================================================\n"
            "\n"
            "    fun refreshMarketListings() {\n"
            "        _marketListings.value = marketService.allListings()\n"
            "    }\n"
            "\n"
            "    fun refreshMyOrders() {\n"
            "        val characterId = _currentCharacterId.value ?: return\n"
            "        val open = marketService.openOrdersFor(characterId)\n"
            "        _myBuyOrders.value = open.filter { it.side == OrderSide.BUY }\n"
            "        _mySellOrders.value = open.filter { it.side == OrderSide.SELL }\n"
            "    }\n"
            "\n"
            "    fun placeBuyOrder(itemId: String, quantity: Int, pricePerUnit: Long): ServiceResult<MarketOrder> {\n"
            "        val characterId = _currentCharacterId.value ?: return ServiceResult.Failure(\"No character selected.\")\n"
            "        val account = marketService.accountFor(characterId)\n"
            "            ?: return ServiceResult.Failure(\"Market account not registered.\")\n"
            "        val before = account.inventory[itemId] ?: 0\n"
            "\n"
            "        val result = marketService.placeBuyOrder(characterId, itemId, quantity, pricePerUnit)\n"
            "        if (result is ServiceResult.Success) {\n"
            "            val after = account.inventory[itemId] ?: 0\n"
            "            val filled = after - before\n"
            "            if (filled > 0) {\n"
            "                inventoryService.inventoryFor(characterId).addItem(itemId, filled)\n"
            "                account.removeItem(itemId, filled)\n"
            "                refreshInventory()\n"
            "            }\n"
            "            refreshCurrency()\n"
            "            refreshMarketListings()\n"
            "            refreshMyOrders()\n"
            "        }\n"
            "        return result\n"
            "    }\n"
            "\n"
            "    fun placeSellOrder(itemId: String, quantity: Int, pricePerUnit: Long): ServiceResult<MarketOrder> {\n"
            "        val characterId = _currentCharacterId.value ?: return ServiceResult.Failure(\"No character selected.\")\n"
            "        val account = marketService.accountFor(characterId)\n"
            "            ?: return ServiceResult.Failure(\"Market account not registered.\")\n"
            "        val realInventory = inventoryService.inventoryFor(characterId)\n"
            "\n"
            "        if (realInventory.quantityOf(itemId) < quantity) {\n"
            "            return ServiceResult.Failure(\"Insufficient item quantity to escrow this order.\")\n"
            "        }\n"
            "        realInventory.removeItem(itemId, quantity)\n"
            "        account.addItem(itemId, quantity)\n"
            "\n"
            "        val result = marketService.placeSellOrder(characterId, itemId, quantity, pricePerUnit)\n"
            "        if (result is ServiceResult.Failure) {\n"
            "            realInventory.addItem(itemId, quantity)\n"
            "            account.removeItem(itemId, quantity)\n"
            "        } else {\n"
            "            refreshCurrency()\n"
            "            refreshMarketListings()\n"
            "            refreshMyOrders()\n"
            "        }\n"
            "        refreshInventory()\n"
            "        return result\n"
            "    }\n"
            "\n"
            "    fun cancelMarketOrder(orderId: String): ServiceResult<MarketOrder> {\n"
            "        val characterId = _currentCharacterId.value ?: return ServiceResult.Failure(\"No character selected.\")\n"
            "        val account = marketService.accountFor(characterId)\n"
            "            ?: return ServiceResult.Failure(\"Market account not registered.\")\n"
            "        val before = account.inventory.toMap()\n"
            "\n"
            "        val result = marketService.cancelOrder(orderId)\n"
            "        if (result is ServiceResult.Success) {\n"
            "            for ((itemId, afterQty) in account.inventory.toMap()) {\n"
            "                val delta = afterQty - (before[itemId] ?: 0)\n"
            "                if (delta > 0) {\n"
            "                    inventoryService.inventoryFor(characterId).addItem(itemId, delta)\n"
            "                    account.removeItem(itemId, delta)\n"
            "                }\n"
            "            }\n"
            "            refreshInventory()\n"
            "            refreshCurrency()\n"
            "            refreshMarketListings()\n"
            "            refreshMyOrders()\n"
            "        }\n"
            "        return result\n"
            "    }\n"
            "\n"
            "    fun sellItemToVendor(itemId: String, quantity: Int): ServiceResult<Long> {\n"
            "        val characterId = _currentCharacterId.value ?: return ServiceResult.Failure(\"No character selected.\")\n"
            "        val account = marketService.accountFor(characterId)\n"
            "            ?: return ServiceResult.Failure(\"Market account not registered.\")\n"
            "        val realInventory = inventoryService.inventoryFor(characterId)\n"
            "\n"
            "        if (realInventory.quantityOf(itemId) < quantity) {\n"
            "            return ServiceResult.Failure(\"Insufficient item quantity to sell.\")\n"
            "        }\n"
            "        realInventory.removeItem(itemId, quantity)\n"
            "        account.addItem(itemId, quantity)\n"
            "\n"
            "        val result = marketService.sellToVendor(characterId, itemId, quantity)\n"
            "        if (result is ServiceResult.Failure) {\n"
            "            realInventory.addItem(itemId, quantity)\n"
            "            account.removeItem(itemId, quantity)\n"
            "        } else {\n"
            "            refreshCurrency()\n"
            "        }\n"
            "        refreshInventory()\n"
            "        return result\n"
            "    }\n"
            "}\n"
        ),
        "refreshCurrency() + market wrapper functions",
    )

    if text == original:
        fail("no changes were made -- aborting")

    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
