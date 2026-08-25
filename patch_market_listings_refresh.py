MA = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"

with open(MA, "r", encoding="utf-8") as f:
    content = f.read()

old = """                            AppDestination.MARKET -> {
                                val marketPriceSummaries by gameViewModel.marketListings.collectAsState()
                                val myBuyOrdersRaw by gameViewModel.myBuyOrders.collectAsState()
                                val mySellOrdersRaw by gameViewModel.mySellOrders.collectAsState()"""

new = """                            AppDestination.MARKET -> {
                                LaunchedEffect(Unit) {
                                    gameViewModel.refreshMarketListings()
                                    gameViewModel.refreshMyOrders()
                                }
                                val marketPriceSummaries by gameViewModel.marketListings.collectAsState()
                                val myBuyOrdersRaw by gameViewModel.myBuyOrders.collectAsState()
                                val mySellOrdersRaw by gameViewModel.mySellOrders.collectAsState()"""

count = content.count(old)
assert count == 1, f"expected exactly 1 match, found {count}"
content = content.replace(old, new)

with open(MA, "w", encoding="utf-8") as f:
    f.write(content)

print(f"OK: patched MainActivity.kt ({len(old)} -> {len(new)} chars)")
