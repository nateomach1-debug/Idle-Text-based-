import pathlib

path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")
text = path.read_text()

old = """                                    MarketScreen(
                                        currentTab = marketTab,
                                        onTabSelected = { marketTab = it },
                                        listings = marketListingsUi,
                                        showingBuyOrders = showingBuyOrders,
                                        onToggleBrowseMode = { showingBuyOrders = !showingBuyOrders },
                                        onItemSelected = { selectedMarketItemId = it },
                                        myBuyOrders = myBuyOrdersUi,
                                        mySellOrders = mySellOrdersUi,
                                        onCancelOrder = { orderId -> gameViewModel.cancelMarketOrder(orderId) } 
                                        vendorSellableItems = inventoryItems,
                                        onPlaceBuyOrder = { itemId, quantity, price ->
                                            gameViewModel.placeBuyOrder(itemId, quantity, price),
                                        onPlaceSellOrder = { itemId, quantity, price ->
                                            gameViewModel.placeSellOrder(itemId, quantity, price),
                                        onSellToVendor = { sellItemId, quantity ->
                                            gameViewModel.sellItemToVendor(sellItemId, quantity),
                                        vendorBuyableItems = gameViewModel.vendorBuyableItems(),
                                        onBuyFromVendor = { buyItemId, quantity ->
                                            gameViewModel.buyItemFromVendor(buyItemId, quantity)
                                        }
                                    )"""

new = """                                    MarketScreen(
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
                                        onPlaceBuyOrder = { itemId, quantity, price ->
                                            gameViewModel.placeBuyOrder(itemId, quantity, price)
                                        },
                                        onPlaceSellOrder = { itemId, quantity, price ->
                                            gameViewModel.placeSellOrder(itemId, quantity, price)
                                        },
                                        onSellToVendor = { sellItemId, quantity ->
                                            gameViewModel.sellItemToVendor(sellItemId, quantity)
                                        },
                                        vendorBuyableItems = gameViewModel.vendorBuyableItems(),
                                        onBuyFromVendor = { buyItemId, quantity ->
                                            gameViewModel.buyItemFromVendor(buyItemId, quantity)
                                        }
                                    )"""

count = text.count(old)
if count == 0:
    raise SystemExit(
        "PATCH FAILED: expected corrupted MarketScreen(...) block not found in "
        "MainActivity.kt - it may already be fixed, or differ from what was expected. "
        "No changes made."
    )
elif count > 1:
    raise SystemExit(
        f"PATCH FAILED: block matched {count} times (expected exactly 1) - "
        "refusing to guess which one. No changes made."
    )

text = text.replace(old, new)
path.write_text(text)
print("Patched MainActivity.kt: fixed dropped braces/commas in the MarketScreen(...) call.")
