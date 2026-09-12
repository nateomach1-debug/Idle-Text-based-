import pathlib

offline_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/OfflineIdleMechanicsSystem.kt")
gvm_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")
leaderboard_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/LeaderboardsScreen.kt")

offline_text = offline_path.read_text()
gvm_text = gvm_path.read_text()
leaderboard_text = leaderboard_path.read_text()

errors = []

# ============================================================
# 1. OfflineEfficiencyCurve: 12h full, 12h @ 50%, then 0% (was 12h full, 72h @ 50%, then 25% floor)
# ============================================================
offline_old = """    private val fullRateWindow: Duration = Duration.ofHours(12)
    private val reducedRateWindow: Duration = Duration.ofHours(72)
    private const val FULL_RATE_PERCENT = 100.0
    private const val REDUCED_RATE_PERCENT = 50.0
    private const val FLOOR_RATE_PERCENT = 25.0"""

offline_new = """    private val fullRateWindow: Duration = Duration.ofHours(12)
    private val reducedRateWindow: Duration = Duration.ofHours(24)
    private const val FULL_RATE_PERCENT = 100.0
    private const val REDUCED_RATE_PERCENT = 50.0
    private const val FLOOR_RATE_PERCENT = 0.0"""

count = offline_text.count(offline_old)
if count == 1:
    offline_text = offline_text.replace(offline_old, offline_new)
elif offline_text.count(offline_new) == 1:
    pass  # already applied
else:
    errors.append(f"OfflineIdleMechanicsSystem.kt curve constants: expected 1 match, found {count}")

# ============================================================
# 2. Market order cap: 2 open buy + 2 open sell (per side)
# ============================================================
gvm_old = """    fun placeBuyOrder(itemId: String, quantity: Int, pricePerUnit: Long) {
        val characterId = _currentCharacterId.value ?: return
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseMarketRepository.placeBuyOrder(supabaseCharacterId, itemId, quantity, pricePerUnit)
            result.onFailure { _marketActionError.value = it.message ?: it.toString() }
            result.onSuccess { order ->
                _marketActionError.value = null
                val filled = order.originalQuantity - order.remainingQuantity
                if (filled > 0) {
                    inventoryService.inventoryFor(characterId).addItem(itemId, filled)
                    refreshInventory()
                }
                refreshCurrency()
                refreshMarketListings()
                refreshMyOrders()
            }
        }
    }

    fun placeSellOrder(itemId: String, quantity: Int, pricePerUnit: Long) {
        val characterId = _currentCharacterId.value ?: return
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        val realInventory = inventoryService.inventoryFor(characterId)
        if (realInventory.quantityOf(itemId) < quantity) return

        realInventory.removeItem(itemId, quantity)
        refreshInventory()

        viewModelScope.launch {
            val result = SupabaseMarketRepository.placeSellOrder(supabaseCharacterId, itemId, quantity, pricePerUnit)
            result.onFailure {
                _marketActionError.value = it.message ?: it.toString()
                realInventory.addItem(itemId, quantity)
                refreshInventory()
            }
            result.onSuccess {
                _marketActionError.value = null
                refreshCurrency()
                refreshMarketListings()
                refreshMyOrders()
            }
        }
    }"""

gvm_new = """    private val MAX_OPEN_ORDERS_PER_SIDE = 2

    fun placeBuyOrder(itemId: String, quantity: Int, pricePerUnit: Long) {
        val characterId = _currentCharacterId.value ?: return
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        if (_myBuyOrders.value.count { it.remainingQuantity > 0 } >= MAX_OPEN_ORDERS_PER_SIDE) {
            _marketActionError.value = "You can only have $MAX_OPEN_ORDERS_PER_SIDE open buy orders at a time."
            return
        }
        viewModelScope.launch {
            val result = SupabaseMarketRepository.placeBuyOrder(supabaseCharacterId, itemId, quantity, pricePerUnit)
            result.onFailure { _marketActionError.value = it.message ?: it.toString() }
            result.onSuccess { order ->
                _marketActionError.value = null
                val filled = order.originalQuantity - order.remainingQuantity
                if (filled > 0) {
                    inventoryService.inventoryFor(characterId).addItem(itemId, filled)
                    refreshInventory()
                }
                refreshCurrency()
                refreshMarketListings()
                refreshMyOrders()
            }
        }
    }

    fun placeSellOrder(itemId: String, quantity: Int, pricePerUnit: Long) {
        val characterId = _currentCharacterId.value ?: return
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        if (_mySellOrders.value.count { it.remainingQuantity > 0 } >= MAX_OPEN_ORDERS_PER_SIDE) {
            _marketActionError.value = "You can only have $MAX_OPEN_ORDERS_PER_SIDE open sell orders at a time."
            return
        }
        val realInventory = inventoryService.inventoryFor(characterId)
        if (realInventory.quantityOf(itemId) < quantity) return

        realInventory.removeItem(itemId, quantity)
        refreshInventory()

        viewModelScope.launch {
            val result = SupabaseMarketRepository.placeSellOrder(supabaseCharacterId, itemId, quantity, pricePerUnit)
            result.onFailure {
                _marketActionError.value = it.message ?: it.toString()
                realInventory.addItem(itemId, quantity)
                refreshInventory()
            }
            result.onSuccess {
                _marketActionError.value = null
                refreshCurrency()
                refreshMarketListings()
                refreshMyOrders()
            }
        }
    }"""

count_old = gvm_text.count(gvm_old)
count_new = gvm_text.count(gvm_new)
if count_new == 1:
    pass  # already applied
elif count_old == 1:
    gvm_text = gvm_text.replace(gvm_old, gvm_new)
else:
    errors.append(f"GameViewModel.kt placeBuyOrder/placeSellOrder: expected old or new form exactly once, found old={count_old} new={count_new}")

# ============================================================
# 3. Leaderboards: scale 1st/2nd/3rd place name text size
# ============================================================
lb_old = """                items(rows) { row ->
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(text = "#" + row.rank + "  " + row.name, style = MaterialTheme.typography.bodyLarge)
                        Text(text = row.valueLabel, style = MaterialTheme.typography.bodyMedium)
                    }
                    HorizontalDivider()
                }"""

lb_new = """                items(rows) { row ->
                    val nameStyle = when (row.rank) {
                        1 -> MaterialTheme.typography.headlineSmall
                        2 -> MaterialTheme.typography.titleLarge
                        3 -> MaterialTheme.typography.titleMedium
                        else -> MaterialTheme.typography.bodyLarge
                    }
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(text = "#" + row.rank + "  " + row.name, style = nameStyle)
                        Text(text = row.valueLabel, style = MaterialTheme.typography.bodyMedium)
                    }
                    HorizontalDivider()
                }"""

count_old = leaderboard_text.count(lb_old)
count_new = leaderboard_text.count(lb_new)
if count_new == 1:
    pass  # already applied
elif count_old == 1:
    leaderboard_text = leaderboard_text.replace(lb_old, lb_new)
else:
    errors.append(f"LeaderboardsScreen.kt row rendering: expected old or new form exactly once, found old={count_old} new={count_new}")

if errors:
    raise SystemExit(
        "PATCH FAILED: one or more expected blocks did not match exactly once. "
        "No changes made to any file.\n" + "\n".join(f"  - {e}" for e in errors)
    )

offline_path.write_text(offline_text)
gvm_path.write_text(gvm_text)
leaderboard_path.write_text(leaderboard_text)

print("Patched OfflineIdleMechanicsSystem.kt: offline progress is now 12h full rate, 12h at 50%, then 0% (capped at 24h total).")
print("Patched GameViewModel.kt: market orders capped at 2 open buy + 2 open sell (MAX_OPEN_ORDERS_PER_SIDE).")
print("Patched LeaderboardsScreen.kt: 1st/2nd/3rd place names now scale down in size (headlineSmall/titleLarge/titleMedium), rest unchanged.")
