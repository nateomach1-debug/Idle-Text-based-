import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"

def find_file(name):
    for dirpath, _, files in os.walk(ROOT):
        if name in files:
            return os.path.join(dirpath, name)
    raise SystemExit(f"!!! FILE NOT FOUND: {name} !!!")

def guarded_replace(path, old, new, expected_count=1):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    count = content.count(old)
    if count != expected_count:
        raise SystemExit(
            f"!!! ABORTING: expected {expected_count} occurrence(s) of anchor in {path}, found {count} !!!\n"
            f"--- anchor was ---\n{old}\n--- end anchor ---"
        )
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"patched {path} (replaced {count} occurrence(s))")

# ---------------------------------------------------------------------------
# 1. OfflineIdleMechanicsSystem.kt - add recordSaleCheckAt(characterId, serverTimestamp)
# ---------------------------------------------------------------------------
offline_idle_path = find_file("OfflineIdleMechanicsSystem.kt")

anchor_old = """    fun lastSaleCheckFor(characterId: String): Instant? = lastSaleCheckAt[characterId]"""
anchor_new = """    fun lastSaleCheckFor(characterId: String): Instant? = lastSaleCheckAt[characterId]

    fun recordSaleCheckAt(characterId: String, serverTimestamp: String) {
        lastSaleCheckAt[characterId] = java.time.OffsetDateTime.parse(serverTimestamp).toInstant()
    }"""
guarded_replace(offline_idle_path, anchor_old, anchor_new)

# ---------------------------------------------------------------------------
# 2. GameViewModel.kt - fix checkForRecentSales() to use server timestamps + onFailure
# ---------------------------------------------------------------------------
game_vm_path = find_file("GameViewModel.kt")

old_fn = """    private fun checkForRecentSales(characterId: String) {
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        val since = offlineIdleService.lastSaleCheckFor(characterId)?.toString()
            ?: Instant.now().minusSeconds(86400).toString()
        offlineIdleService.recordSaleCheck(characterId)
        viewModelScope.launch {
            val result = SupabaseMarketRepository.myRecentSales(supabaseCharacterId, since)
            result.onSuccess { rows ->
                if (rows.isNotEmpty()) {
                    val notifications = rows.map { row ->
                        val netProceeds = (row.pricePerUnit * row.quantity) - row.taxCollected
                        SaleNotification(
                            itemName = ItemCatalog.find(row.itemId)?.name ?: formatItemName(row.itemId),
                            quantity = row.quantity,
                            netProceeds = netProceeds
                        )
                    }
                    _pendingSaleNotifications.value = _pendingSaleNotifications.value + notifications
                }
            }
        }
    }"""
new_fn = """    private fun checkForRecentSales(characterId: String) {
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        val since = offlineIdleService.lastSaleCheckFor(characterId)?.toString()
            ?: Instant.now().minusSeconds(86400).toString()
        viewModelScope.launch {
            val result = SupabaseMarketRepository.myRecentSales(supabaseCharacterId, since)
            result.onFailure {
                _marketActionError.value = it.message ?: it.toString()
            }
            result.onSuccess { rows ->
                if (rows.isNotEmpty()) {
                    val notifications = rows.map { row ->
                        val netProceeds = (row.pricePerUnit * row.quantity) - row.taxCollected
                        SaleNotification(
                            itemName = ItemCatalog.find(row.itemId)?.name ?: formatItemName(row.itemId),
                            quantity = row.quantity,
                            netProceeds = netProceeds
                        )
                    }
                    _pendingSaleNotifications.value = _pendingSaleNotifications.value + notifications
                    // Use the server's own latest executed_at as the new checkpoint,
                    // never the device clock - avoids any client/server clock-skew risk.
                    val latestServerTimestamp = rows.maxOf { it.executedAt }
                    offlineIdleService.recordSaleCheckAt(characterId, latestServerTimestamp)
                }
            }
        }
    }"""
guarded_replace(game_vm_path, old_fn, new_fn)

print("ALL PATCHES APPLIED SUCCESSFULLY")
