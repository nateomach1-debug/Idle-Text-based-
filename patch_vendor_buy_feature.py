MARKET_SCREEN = "app/src/main/kotlin/com/yourname/idlerpg/MarketScreen.kt"
MAIN_ACTIVITY = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
GAME_VIEW_MODEL = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
SUPABASE_MARKET_REPO = "app/src/main/kotlin/com/yourname/idlerpg/SupabaseMarketRepository.kt"


def patch_market_screen():
    with open(MARKET_SCREEN, "r", encoding="utf-8") as fh:
        content = fh.read()
    before = content.count("{") - content.count("}")

    # 1. Enum + new VendorBuyableItem/VendorBuyCatalog
    old1 = 'enum class MarketTab { BROWSE, MY_ORDERS, SELL_TO_VENDOR }\n\ndata class MarketListingSummary('
    assert content.count(old1) == 1, f"1a: expected 1, found {content.count(old1)}"
    new1 = '''enum class MarketTab { BROWSE, MY_ORDERS, SELL_TO_VENDOR, BUY_FROM_VENDOR }

data class VendorBuyableItem(
    val itemId: String,
    val displayName: String,
    val pricePerUnit: Long
)

object VendorBuyCatalog {
    val items = listOf(
        VendorBuyableItem("flour", "Flour", 2L),
        VendorBuyableItem("vial_of_water", "Vial of Water", 2L)
    )
}

data class MarketListingSummary('''
    content = content.replace(old1, new1)

    # 2. MarketScreen composable signature - new params
    old2 = '''    // Sell to Vendor
    vendorSellableItems: List<InventoryItemSummary>,
    onSellToVendor: (String, Int) -> Unit,
    modifier: Modifier = Modifier
) {'''
    assert content.count(old2) == 1, f"2: expected 1, found {content.count(old2)}"
    new2 = '''    // Sell to Vendor
    vendorSellableItems: List<InventoryItemSummary>,
    onSellToVendor: (String, Int) -> Unit,
    // Buy from Vendor
    vendorBuyableItems: List<VendorBuyableItem>,
    onBuyFromVendor: (String, Int) -> Unit,
    modifier: Modifier = Modifier
) {'''
    content = content.replace(old2, new2)

    # 3. New tab button
    old3 = '''            MarketTabButton(
                label = "Vendor",
                isSelected = currentTab == MarketTab.SELL_TO_VENDOR,
                modifier = Modifier.weight(1f)
            ) { onTabSelected(MarketTab.SELL_TO_VENDOR) }
        }'''
    assert content.count(old3) == 1, f"3: expected 1, found {content.count(old3)}"
    new3 = '''            MarketTabButton(
                label = "Vendor",
                isSelected = currentTab == MarketTab.SELL_TO_VENDOR,
                modifier = Modifier.weight(1f)
            ) { onTabSelected(MarketTab.SELL_TO_VENDOR) }
            MarketTabButton(
                label = "Buy",
                isSelected = currentTab == MarketTab.BUY_FROM_VENDOR,
                modifier = Modifier.weight(1f)
            ) { onTabSelected(MarketTab.BUY_FROM_VENDOR) }
        }'''
    content = content.replace(old3, new3)

    # 4. New when() branch
    old4 = '''        when (currentTab) {
            MarketTab.BROWSE -> BrowseTab(listings, showingBuyOrders, onToggleBrowseMode, onItemSelected)
            MarketTab.MY_ORDERS -> MyOrdersTab(myBuyOrders, mySellOrders, onCancelOrder)
            MarketTab.SELL_TO_VENDOR -> SellToVendorTab(vendorSellableItems, onSellToVendor)
        }'''
    assert content.count(old4) == 1, f"4: expected 1, found {content.count(old4)}"
    new4 = '''        when (currentTab) {
            MarketTab.BROWSE -> BrowseTab(listings, showingBuyOrders, onToggleBrowseMode, onItemSelected)
            MarketTab.MY_ORDERS -> MyOrdersTab(myBuyOrders, mySellOrders, onCancelOrder)
            MarketTab.SELL_TO_VENDOR -> SellToVendorTab(vendorSellableItems, onSellToVendor)
            MarketTab.BUY_FROM_VENDOR -> BuyFromVendorTab(vendorBuyableItems, onBuyFromVendor)
        }'''
    content = content.replace(old4, new4)

    # 5. New composables (inserted just before the Sell to Vendor section)
    old5 = '''// ---------------- Sell to Vendor ----------------

@Composable
private fun SellToVendorTab(items: List<InventoryItemSummary>, onSell: (String, Int) -> Unit) {'''
    assert content.count(old5) == 1, f"5: expected 1, found {content.count(old5)}"
    new5 = '''// ---------------- Buy from Vendor ----------------

@Composable
private fun BuyFromVendorTab(items: List<VendorBuyableItem>, onBuy: (String, Int) -> Unit) {
    LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        items(items) { item ->
            VendorBuyItemRow(item, onBuy)
        }
    }
}

@Composable
private fun VendorBuyItemRow(item: VendorBuyableItem, onBuy: (String, Int) -> Unit) {
    var quantityText by remember(item.itemId) { mutableStateOf("1") }
    val enteredQuantity = quantityText.toIntOrNull()
    val isValidQuantity = enteredQuantity != null && enteredQuantity > 0

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(14.dp)
    ) {
        Text(
            text = item.displayName,
            style = MaterialTheme.typography.titleMedium,
            maxLines = 1,
            softWrap = false,
            overflow = TextOverflow.Ellipsis
        )
        Text(
            text = item.pricePerUnit.toString() + " gold each (unlimited stock)",
            style = MaterialTheme.typography.labelSmall,
            maxLines = 1,
            softWrap = false,
            overflow = TextOverflow.Ellipsis
        )
        Spacer(modifier = Modifier.height(10.dp))
        Row(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
                value = quantityText,
                onValueChange = { new -> if (new.length <= 6 && new.all { it.isDigit() }) quantityText = new },
                modifier = Modifier.width(56.dp),
                singleLine = true,
                textStyle = MaterialTheme.typography.bodyMedium,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
            )
            Button(
                onClick = { enteredQuantity?.let { onBuy(item.itemId, it) } },
                enabled = isValidQuantity
            ) {
                Text("Buy")
            }
        }
    }
}

// ---------------- Sell to Vendor ----------------

@Composable
private fun SellToVendorTab(items: List<InventoryItemSummary>, onSell: (String, Int) -> Unit) {'''
    content = content.replace(old5, new5)

    after = content.count("{") - content.count("}")
    assert before == after, f"brace balance changed: {before} -> {after}"

    with open(MARKET_SCREEN, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Patched {MARKET_SCREEN} (brace balance unchanged: {before})")


def patch_main_activity():
    with open(MAIN_ACTIVITY, "r", encoding="utf-8") as fh:
        content = fh.read()
    before = content.count("{") - content.count("}")

    old = '''                                    MarketScreen(
                                        currentTab = marketTab,
                                        onTabSelected = { marketTab = it },
                                        listings = marketListingsUi,
                                        showingBuyOrders = showingBuyOrders,
                                        onToggleBrowseMode = { showingBuyOrders = !showingBuyOrders },
                                        onItemSelected = { selectedMarketItemId = it },
                                        myBuyOrders = myBuyOrdersUi,
                                        mySellOrders = mySellOrdersUi,
                                        onCancelOrder = { orderId -> gameViewModel.cancelMarketOrder(orderId) },
                                        vendorSellableItems = inventoryItems,
                                        onSellToVendor = { sellItemId, quantity ->
                                            gameViewModel.sellItemToVendor(sellItemId, quantity)
                                        }
                                    )'''
    assert content.count(old) == 1, f"expected 1, found {content.count(old)}"
    new = '''                                    MarketScreen(
                                        currentTab = marketTab,
                                        onTabSelected = { marketTab = it },
                                        listings = marketListingsUi,
                                        showingBuyOrders = showingBuyOrders,
                                        onToggleBrowseMode = { showingBuyOrders = !showingBuyOrders },
                                        onItemSelected = { selectedMarketItemId = it },
                                        myBuyOrders = myBuyOrdersUi,
                                        mySellOrders = mySellOrdersUi,
                                        onCancelOrder = { orderId -> gameViewModel.cancelMarketOrder(orderId) },
                                        vendorSellableItems = inventoryItems,
                                        onSellToVendor = { sellItemId, quantity ->
                                            gameViewModel.sellItemToVendor(sellItemId, quantity)
                                        },
                                        vendorBuyableItems = VendorBuyCatalog.items,
                                        onBuyFromVendor = { buyItemId, quantity ->
                                            gameViewModel.buyItemFromVendor(buyItemId, quantity)
                                        }
                                    )'''
    content = content.replace(old, new)

    after = content.count("{") - content.count("}")
    assert before == after, f"brace balance changed: {before} -> {after}"

    with open(MAIN_ACTIVITY, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Patched {MAIN_ACTIVITY} (brace balance unchanged: {before})")


def patch_game_view_model():
    with open(GAME_VIEW_MODEL, "r", encoding="utf-8") as fh:
        content = fh.read()
    before = content.count("{") - content.count("}")

    old = '''        viewModelScope.launch {
            val result = SupabaseMarketRepository.sellToVendor(supabaseCharacterId, itemId, quantity, payoutPerUnit)
            result.onFailure {
                _marketActionError.value = it.message ?: it.toString()
                realInventory.addItem(itemId, quantity)
                refreshInventory()
            }
            result.onSuccess {
                _marketActionError.value = null
                refreshCurrency()
            }
        }
    }
}'''
    assert content.count(old) == 1, f"expected 1, found {content.count(old)}"
    new = '''        viewModelScope.launch {
            val result = SupabaseMarketRepository.sellToVendor(supabaseCharacterId, itemId, quantity, payoutPerUnit)
            result.onFailure {
                _marketActionError.value = it.message ?: it.toString()
                realInventory.addItem(itemId, quantity)
                refreshInventory()
            }
            result.onSuccess {
                _marketActionError.value = null
                refreshCurrency()
            }
        }
    }

    fun buyItemFromVendor(itemId: String, quantity: Int) {
        val characterId = _currentCharacterId.value ?: return
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        val realInventory = inventoryService.inventoryFor(characterId)
        val pricePerUnit = VendorBuyCatalog.items.find { it.itemId == itemId }?.pricePerUnit ?: return
        if (quantity <= 0) return

        realInventory.addItem(itemId, quantity)
        refreshInventory()

        viewModelScope.launch {
            val result = SupabaseMarketRepository.buyFromVendor(supabaseCharacterId, itemId, quantity, pricePerUnit)
            result.onFailure {
                _marketActionError.value = it.message ?: it.toString()
                realInventory.removeItem(itemId, quantity)
                refreshInventory()
            }
            result.onSuccess {
                _marketActionError.value = null
                refreshCurrency()
            }
        }
    }
}'''
    content = content.replace(old, new)

    after = content.count("{") - content.count("}")
    assert before == after, f"brace balance changed: {before} -> {after}"

    with open(GAME_VIEW_MODEL, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Patched {GAME_VIEW_MODEL} (brace balance unchanged: {before})")


def patch_supabase_market_repository():
    with open(SUPABASE_MARKET_REPO, "r", encoding="utf-8") as fh:
        content = fh.read()
    before = content.count("{") - content.count("}")

    old = '''    suspend fun myOrders(characterId: String): Result<List<MarketOrderRow>> = runCatching {
        client.postgrest.rpc("market_my_orders", buildJsonObject {
            put("p_character_id", characterId)
        }).decodeList<MarketOrderRow>()
    }
}'''
    assert content.count(old) == 1, f"expected 1, found {content.count(old)}"
    new = '''    suspend fun myOrders(characterId: String): Result<List<MarketOrderRow>> = runCatching {
        client.postgrest.rpc("market_my_orders", buildJsonObject {
            put("p_character_id", characterId)
        }).decodeList<MarketOrderRow>()
    }

    suspend fun buyFromVendor(characterId: String, itemId: String, quantity: Int, pricePerUnit: Long): Result<Long> = runCatching {
        client.postgrest.rpc("market_buy_from_vendor", buildJsonObject {
            put("p_character_id", characterId)
            put("p_item_id", itemId)
            put("p_quantity", quantity)
            put("p_price_per_unit", pricePerUnit)
        }).decodeAs<Long>()
    }
}'''
    content = content.replace(old, new)

    after = content.count("{") - content.count("}")
    assert before == after, f"brace balance changed: {before} -> {after}"

    with open(SUPABASE_MARKET_REPO, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Patched {SUPABASE_MARKET_REPO} (brace balance unchanged: {before})")


if __name__ == "__main__":
    patch_market_screen()
    patch_main_activity()
    patch_game_view_model()
    patch_supabase_market_repository()
    print("Done.")
