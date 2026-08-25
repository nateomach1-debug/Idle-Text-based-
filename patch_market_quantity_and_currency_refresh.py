SMR = "app/src/main/kotlin/com/yourname/idlerpg/SupabaseMarketRepository.kt"
EMS = "app/src/main/kotlin/com/yourname/idlerpg/EconomyMarketSystem.kt"
GVM = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
MS = "app/src/main/kotlin/com/yourname/idlerpg/MarketScreen.kt"
MA = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"


def patch(path, old, new):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    count = content.count(old)
    assert count == 1, f"[{path}] expected exactly 1 match, found {count} for:\n{old!r}"
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: patched {path} ({len(old)} -> {len(new)} chars)")


# 1. SupabaseMarketRepository.kt - MarketListingRow gains quantity fields
patch(
    SMR,
    """@Serializable
data class MarketListingRow(
    val itemId: String,
    val bestBuyPrice: Long? = null,
    val bestSellPrice: Long? = null
)""",
    """@Serializable
data class MarketListingRow(
    val itemId: String,
    val bestBuyPrice: Long? = null,
    val bestBuyQuantity: Int? = null,
    val bestSellPrice: Long? = null,
    val bestSellQuantity: Int? = null
)""",
)

# 2. EconomyMarketSystem.kt - MarketPriceSummary gains quantity fields
patch(
    EMS,
    """data class MarketPriceSummary(val itemId: String, val bestBuyPrice: Long?, val bestSellPrice: Long?)""",
    """data class MarketPriceSummary(val itemId: String, val bestBuyPrice: Long?, val bestBuyQuantity: Int?, val bestSellPrice: Long?, val bestSellQuantity: Int?)""",
)

# 3. GameViewModel.kt - pass quantities through in refreshMarketListings, and refresh currency on Home entry doesn't live here (MainActivity), just the mapping fix
patch(
    GVM,
    """            _marketListings.value = listings.map { MarketPriceSummary(it.itemId, it.bestBuyPrice, it.bestSellPrice) }""",
    """            _marketListings.value = listings.map { MarketPriceSummary(it.itemId, it.bestBuyPrice, it.bestBuyQuantity, it.bestSellPrice, it.bestSellQuantity) }""",
)

# 4. MarketScreen.kt - MarketListingSummary gains quantity fields
patch(
    MS,
    """data class MarketListingSummary(
    val itemId: String,
    val displayName: String,
    val bestBuyPrice: Long?,   // highest current buy order, null if none
    val bestSellPrice: Long?   // lowest current sell order, null if none
)""",
    """data class MarketListingSummary(
    val itemId: String,
    val displayName: String,
    val bestBuyPrice: Long?,   // highest current buy order, null if none
    val bestBuyQuantity: Int?, // total quantity available at bestBuyPrice
    val bestSellPrice: Long?,  // lowest current sell order, null if none
    val bestSellQuantity: Int? // total quantity available at bestSellPrice
)""",
)

# 5. MarketScreen.kt - display quantity alongside price
patch(
    MS,
    """        Text(text = listing.displayName, style = MaterialTheme.typography.titleMedium)
        Column(horizontalAlignment = Alignment.End) {
            Text(text = "Buy: " + (listing.bestBuyPrice?.toString() ?: "—"), style = MaterialTheme.typography.labelSmall)
            Text(text = "Sell: " + (listing.bestSellPrice?.toString() ?: "—"), style = MaterialTheme.typography.labelSmall)
        }""",
    """        Text(text = listing.displayName, style = MaterialTheme.typography.titleMedium)
        Column(horizontalAlignment = Alignment.End) {
            Text(text = "Buy: " + (listing.bestBuyPrice?.let { "$it (x${listing.bestBuyQuantity ?: 0})" } ?: "—"), style = MaterialTheme.typography.labelSmall)
            Text(text = "Sell: " + (listing.bestSellPrice?.let { "$it (x${listing.bestSellQuantity ?: 0})" } ?: "—"), style = MaterialTheme.typography.labelSmall)
        }""",
)

# 6. MainActivity.kt - pass quantities through into MarketListingSummary
patch(
    MA,
    """                                val marketListingsUi = remember(marketPriceSummaries) {
                                    marketPriceSummaries.map {
                                        MarketListingSummary(
                                            itemId = it.itemId,
                                            displayName = ItemCatalog.find(it.itemId)?.name ?: it.itemId,
                                            bestBuyPrice = it.bestBuyPrice,
                                            bestSellPrice = it.bestSellPrice
                                        )
                                    }
                                }""",
    """                                val marketListingsUi = remember(marketPriceSummaries) {
                                    marketPriceSummaries.map {
                                        MarketListingSummary(
                                            itemId = it.itemId,
                                            displayName = ItemCatalog.find(it.itemId)?.name ?: it.itemId,
                                            bestBuyPrice = it.bestBuyPrice,
                                            bestBuyQuantity = it.bestBuyQuantity,
                                            bestSellPrice = it.bestSellPrice,
                                            bestSellQuantity = it.bestSellQuantity
                                        )
                                    }
                                }""",
)

# 7. MainActivity.kt - refresh currency on Home tab entry (fixes stale gold after async trade fills)
patch(
    MA,
    """                            AppDestination.HOME -> HomeScreen(state = homeState)""",
    """                            AppDestination.HOME -> {
                                LaunchedEffect(Unit) { gameViewModel.refreshCurrency() }
                                HomeScreen(state = homeState)
                            }""",
)

print("\nAll quantity-display and currency-refresh patches applied successfully.")
