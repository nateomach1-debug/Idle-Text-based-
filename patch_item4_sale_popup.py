import os, re

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"

def find_file(name):
    for dirpath, _, files in os.walk(ROOT):
        if name in files:
            return os.path.join(dirpath, name)
    raise SystemExit(f"!!! FILE NOT FOUND: {name} !!!")

def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def guarded_replace(path, old, new, expected_count=1):
    content = read(path)
    count = content.count(old)
    if count != expected_count:
        raise SystemExit(
            f"!!! ABORTING: expected {expected_count} occurrence(s) of anchor in {path}, found {count} !!!\n"
            f"--- anchor was ---\n{old}\n--- end anchor ---"
        )
    content = content.replace(old, new)
    write(path, content)
    print(f"patched {path} (replaced {count} occurrence(s))")

def guarded_regex_replace(path, pattern, expected_count, repl_fn):
    content = read(path)
    matches = list(pattern.finditer(content))
    if len(matches) != expected_count:
        raise SystemExit(
            f"!!! ABORTING: expected {expected_count} regex match(es) in {path}, found {len(matches)} !!!\n"
            f"--- pattern was --- \n{pattern.pattern}"
        )
    content = pattern.sub(repl_fn, content)
    write(path, content)
    print(f"patched {path} (regex-replaced {len(matches)} occurrence(s))")

# ---------------------------------------------------------------------------
# 1. OfflineIdleMechanicsSystem.kt - LastSaleCheckExport + tracking
# ---------------------------------------------------------------------------
offline_idle_path = find_file("OfflineIdleMechanicsSystem.kt")

lastseen_export_old = "data class LastSeenExport(val characterId: String, val lastSeenAt: String)"
lastseen_export_new = """data class LastSeenExport(val characterId: String, val lastSeenAt: String)

data class LastSaleCheckExport(val characterId: String, val lastSaleCheckAt: String)"""
guarded_replace(offline_idle_path, lastseen_export_old, lastseen_export_new)

map_field_old = "    private val lastSeenAt: MutableMap<String, Instant> = mutableMapOf()"
map_field_new = """    private val lastSeenAt: MutableMap<String, Instant> = mutableMapOf()
    private val lastSaleCheckAt: MutableMap<String, Instant> = mutableMapOf()"""
guarded_replace(offline_idle_path, map_field_old, map_field_new)

record_old = """    fun recordLastSeen(characterId: String, now: Instant = Instant.now()) {
        lastSeenAt[characterId] = now
    }"""
record_new = """    fun recordLastSeen(characterId: String, now: Instant = Instant.now()) {
        lastSeenAt[characterId] = now
    }

    fun recordSaleCheck(characterId: String, now: Instant = Instant.now()) {
        lastSaleCheckAt[characterId] = now
    }

    fun lastSaleCheckFor(characterId: String): Instant? = lastSaleCheckAt[characterId]"""
guarded_replace(offline_idle_path, record_old, record_new)

export_old = """    fun exportLastSeen(): List<LastSeenExport> =
        lastSeenAt.map { (characterId, instant) -> LastSeenExport(characterId, instant.toString()) }"""
export_new = """    fun exportLastSeen(): List<LastSeenExport> =
        lastSeenAt.map { (characterId, instant) -> LastSeenExport(characterId, instant.toString()) }

    fun exportLastSaleCheck(): List<LastSaleCheckExport> =
        lastSaleCheckAt.map { (characterId, instant) -> LastSaleCheckExport(characterId, instant.toString()) }"""
guarded_replace(offline_idle_path, export_old, export_new)

restore_old = """    fun restoreLastSeen(export: LastSeenExport) {
        lastSeenAt[export.characterId] = Instant.parse(export.lastSeenAt)
    }
}"""
restore_new = """    fun restoreLastSeen(export: LastSeenExport) {
        lastSeenAt[export.characterId] = Instant.parse(export.lastSeenAt)
    }

    fun restoreLastSaleCheck(export: LastSaleCheckExport) {
        lastSaleCheckAt[export.characterId] = Instant.parse(export.lastSaleCheckAt)
    }
}"""
guarded_replace(offline_idle_path, restore_old, restore_new)

# ---------------------------------------------------------------------------
# 2. GameStateRepository.kt - save() signature, JSON write, JSON read, SavedGameState
# ---------------------------------------------------------------------------
repo_path = find_file("GameStateRepository.kt")

sig_old = """        lastSeen: List<LastSeenExport>,
        inventoryItems: List<InventorySlotExport>,"""
sig_new = """        lastSeen: List<LastSeenExport>,
        lastSaleCheck: List<LastSaleCheckExport>,
        inventoryItems: List<InventorySlotExport>,"""
guarded_replace(repo_path, sig_old, sig_new)

write_old = """        val lastSeenArray = JSONArray()
        lastSeen.forEach { entry ->
            val obj = JSONObject()
            obj.put("characterId", entry.characterId)
            obj.put("lastSeenAt", entry.lastSeenAt)
            lastSeenArray.put(obj)
        }
        root.put("lastSeen", lastSeenArray)"""
write_new = """        val lastSeenArray = JSONArray()
        lastSeen.forEach { entry ->
            val obj = JSONObject()
            obj.put("characterId", entry.characterId)
            obj.put("lastSeenAt", entry.lastSeenAt)
            lastSeenArray.put(obj)
        }
        root.put("lastSeen", lastSeenArray)

        val lastSaleCheckArray = JSONArray()
        lastSaleCheck.forEach { entry ->
            val obj = JSONObject()
            obj.put("characterId", entry.characterId)
            obj.put("lastSaleCheckAt", entry.lastSaleCheckAt)
            lastSaleCheckArray.put(obj)
        }
        root.put("lastSaleCheck", lastSaleCheckArray)"""
guarded_replace(repo_path, write_old, write_new)

read_old = """        val lastSeen = mutableListOf<LastSeenExport>()
        val lastSeenArray = root.optJSONArray("lastSeen") ?: JSONArray()
        for (i in 0 until lastSeenArray.length()) {
            val obj = lastSeenArray.getJSONObject(i)
            lastSeen.add(LastSeenExport(characterId = obj.getString("characterId"), lastSeenAt = obj.getString("lastSeenAt")))
        }"""
read_new = """        val lastSeen = mutableListOf<LastSeenExport>()
        val lastSeenArray = root.optJSONArray("lastSeen") ?: JSONArray()
        for (i in 0 until lastSeenArray.length()) {
            val obj = lastSeenArray.getJSONObject(i)
            lastSeen.add(LastSeenExport(characterId = obj.getString("characterId"), lastSeenAt = obj.getString("lastSeenAt")))
        }

        val lastSaleCheck = mutableListOf<LastSaleCheckExport>()
        val lastSaleCheckArray = root.optJSONArray("lastSaleCheck") ?: JSONArray()
        for (i in 0 until lastSaleCheckArray.length()) {
            val obj = lastSaleCheckArray.getJSONObject(i)
            lastSaleCheck.add(LastSaleCheckExport(characterId = obj.getString("characterId"), lastSaleCheckAt = obj.getString("lastSaleCheckAt")))
        }"""
guarded_replace(repo_path, read_old, read_new)

return_old = """        return SavedGameState(
            accounts, characters, skills, skillingQueues, craftingQueues, lastSeen, inventoryItems, equippedSlots,
            loadoutSettings, marketAccounts, marketOrders, marketPriceHistory
        )"""
return_new = """        return SavedGameState(
            accounts, characters, skills, skillingQueues, craftingQueues, lastSeen, lastSaleCheck, inventoryItems, equippedSlots,
            loadoutSettings, marketAccounts, marketOrders, marketPriceHistory
        )"""
guarded_replace(repo_path, return_old, return_new)

class_old = """data class SavedGameState(
    val accounts: List<AccountExport>,
    val characters: List<CharacterExport>,
    val skills: List<SkillExport>,
    val skillingQueues: List<SkillingQueueExport>,
    val craftingQueues: List<CraftingQueueExport>,
    val lastSeen: List<LastSeenExport>,
    val inventoryItems: List<InventorySlotExport>,"""
class_new = """data class SavedGameState(
    val accounts: List<AccountExport>,
    val characters: List<CharacterExport>,
    val skills: List<SkillExport>,
    val skillingQueues: List<SkillingQueueExport>,
    val craftingQueues: List<CraftingQueueExport>,
    val lastSeen: List<LastSeenExport>,
    val lastSaleCheck: List<LastSaleCheckExport>,
    val inventoryItems: List<InventorySlotExport>,"""
guarded_replace(repo_path, class_old, class_new)

# ---------------------------------------------------------------------------
# 3. GameViewModel.kt - saveGame() call, 3 restore call sites, popup queue, checkForRecentSales
# ---------------------------------------------------------------------------
game_vm_path = find_file("GameViewModel.kt")

save_call_old = """            offlineIdleService.exportLastSeen(),
            inventoryService.exportAllItems(),"""
save_call_new = """            offlineIdleService.exportLastSeen(),
            offlineIdleService.exportLastSaleCheck(),
            inventoryService.exportAllItems(),"""
guarded_replace(game_vm_path, save_call_old, save_call_new)

# restore site #1 (loadGame(), "saved." variant, single occurrence)
saved_restore_old = "        saved.lastSeen.forEach { offlineIdleService.restoreLastSeen(it) }"
saved_restore_new = """        saved.lastSeen.forEach { offlineIdleService.restoreLastSeen(it) }
        saved.lastSaleCheck.forEach { offlineIdleService.restoreLastSaleCheck(it) }"""
guarded_replace(game_vm_path, saved_restore_old, saved_restore_new)

# restore sites #2 and #3 ("recovered." variant, two occurrences at different indentation
# levels - use regex with a captured indent so both come out correctly indented)
recovered_pattern = re.compile(
    r"^([ \t]*)recovered\.lastSeen\.forEach \{ offlineIdleService\.restoreLastSeen\(it\) \}$",
    re.MULTILINE
)
def recovered_repl(m):
    indent = m.group(1)
    return (f"{indent}recovered.lastSeen.forEach {{ offlineIdleService.restoreLastSeen(it) }}\n"
            f"{indent}recovered.lastSaleCheck.forEach {{ offlineIdleService.restoreLastSaleCheck(it) }}")
guarded_regex_replace(game_vm_path, recovered_pattern, 2, recovered_repl)

# SaleNotification data class, right after OfflineSummary
offline_summary_old = """data class OfflineSummary(
    val awaySeconds: Long,
    val skillActionName: String,
    val itemName: String,
    val quantity: Int,
    val xpEarned: Long
)"""
offline_summary_new = """data class OfflineSummary(
    val awaySeconds: Long,
    val skillActionName: String,
    val itemName: String,
    val quantity: Int,
    val xpEarned: Long
)

data class SaleNotification(
    val itemName: String,
    val quantity: Int,
    val netProceeds: Long
)"""
guarded_replace(game_vm_path, offline_summary_old, offline_summary_new)

# pendingSaleNotifications StateFlow, right after offlineSummary StateFlow
flow_old = """    private val _offlineSummary = MutableStateFlow<OfflineSummary?>(null)
    val offlineSummary: StateFlow<OfflineSummary?> = _offlineSummary.asStateFlow()"""
flow_new = """    private val _offlineSummary = MutableStateFlow<OfflineSummary?>(null)
    val offlineSummary: StateFlow<OfflineSummary?> = _offlineSummary.asStateFlow()

    private val _pendingSaleNotifications = MutableStateFlow<List<SaleNotification>>(emptyList())
    val pendingSaleNotifications: StateFlow<List<SaleNotification>> = _pendingSaleNotifications.asStateFlow()"""
guarded_replace(game_vm_path, flow_old, flow_new)

# dismissSaleNotification() + checkForRecentSales(), right after clearOfflineSummary()
clear_old = """    fun clearOfflineSummary() {
        _offlineSummary.value = null
    }"""
clear_new = """    fun clearOfflineSummary() {
        _offlineSummary.value = null
    }

    fun dismissSaleNotification() {
        _pendingSaleNotifications.value = _pendingSaleNotifications.value.drop(1)
    }

    private fun checkForRecentSales(characterId: String) {
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
guarded_replace(game_vm_path, clear_old, clear_new)

# wire the check into the existing recordLastSeen call site
record_call_old = """        offlineIdleService.recordLastSeen(characterId)
        skillActionProgressSeconds = 0"""
record_call_new = """        offlineIdleService.recordLastSeen(characterId)
        checkForRecentSales(characterId)
        skillActionProgressSeconds = 0"""
guarded_replace(game_vm_path, record_call_old, record_call_new)

# ---------------------------------------------------------------------------
# 4. SupabaseMarketRepository.kt - MarketSaleRow + myRecentSales RPC wrapper
# ---------------------------------------------------------------------------
market_repo_path = find_file("SupabaseMarketRepository.kt")

row_old = """@Serializable
data class MarketOrderRow(
    val id: String,
    val characterId: String,
    val itemId: String,
    val side: String,
    val pricePerUnit: Long,
    val originalQuantity: Int,
    val remainingQuantity: Int,
    val status: String,
    val createdAt: String
)"""
row_new = """@Serializable
data class MarketOrderRow(
    val id: String,
    val characterId: String,
    val itemId: String,
    val side: String,
    val pricePerUnit: Long,
    val originalQuantity: Int,
    val remainingQuantity: Int,
    val status: String,
    val createdAt: String
)

@Serializable
data class MarketSaleRow(
    val itemId: String,
    val quantity: Int,
    val pricePerUnit: Long,
    val taxCollected: Long,
    val executedAt: String
)"""
guarded_replace(market_repo_path, row_old, row_new)

grant_coins_old = """    suspend fun grantCombatCoins(characterId: String, amount: Long): Result<Long> = runCatching {
        client.postgrest.rpc("combat_grant_coins", buildJsonObject {
            put("p_character_id", characterId)
            put("p_amount", amount)
        }).decodeAs<Long>()
    }"""
grant_coins_new = """    suspend fun grantCombatCoins(characterId: String, amount: Long): Result<Long> = runCatching {
        client.postgrest.rpc("combat_grant_coins", buildJsonObject {
            put("p_character_id", characterId)
            put("p_amount", amount)
        }).decodeAs<Long>()
    }

    suspend fun myRecentSales(characterId: String, since: String): Result<List<MarketSaleRow>> = runCatching {
        client.postgrest.rpc("market_my_recent_sales", buildJsonObject {
            put("p_character_id", characterId)
            put("p_since", since)
        }).decodeList<MarketSaleRow>()
    }"""
guarded_replace(market_repo_path, grant_coins_old, grant_coins_new)

# ---------------------------------------------------------------------------
# 5. MainActivity.kt - popup UI, right after the offlineSummary AlertDialog
# ---------------------------------------------------------------------------
main_activity_path = find_file("MainActivity.kt")

dialog_old = """    val offlineSummary by gameViewModel.offlineSummary.collectAsState()
    offlineSummary?.let { summary ->
        androidx.compose.material3.AlertDialog(
            onDismissRequest = { gameViewModel.clearOfflineSummary() },
            title = { androidx.compose.material3.Text("Welcome back!") },
            text = {
                val minutes = summary.awaySeconds / 60
                val awayText = if (minutes < 1) "under a minute" else minutes.toString() + " minute(s)"
                androidx.compose.material3.Text(
                    "You were away for " + awayText + ".\\n\\n" +
                    "While gone, you were " + summary.skillActionName + ":\\n" +
                    "+" + summary.xpEarned + " XP\\n" +
                    "Gathered " + summary.quantity + "x " + summary.itemName
                )
            },
            confirmButton = {
                androidx.compose.material3.TextButton(onClick = { gameViewModel.clearOfflineSummary() }) {
                    androidx.compose.material3.Text("Nice!")
                }
            }
        )
    }"""
dialog_new = dialog_old + """

    val pendingSaleNotifications by gameViewModel.pendingSaleNotifications.collectAsState()
    pendingSaleNotifications.firstOrNull()?.let { sale ->
        androidx.compose.material3.AlertDialog(
            onDismissRequest = { gameViewModel.dismissSaleNotification() },
            title = { androidx.compose.material3.Text("Item Sold!") },
            text = {
                androidx.compose.material3.Text(
                    "Sold " + sale.quantity + "x " + sale.itemName + "\\n" +
                    "You received " + sale.netProceeds + " coins (after tax)."
                )
            },
            confirmButton = {
                androidx.compose.material3.TextButton(onClick = { gameViewModel.dismissSaleNotification() }) {
                    androidx.compose.material3.Text("Nice!")
                }
            }
        )
    }"""
guarded_replace(main_activity_path, dialog_old, dialog_new)

print("ALL PATCHES APPLIED SUCCESSFULLY")
