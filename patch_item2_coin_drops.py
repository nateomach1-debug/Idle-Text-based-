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
# 1. CombatSystem.kt - CoinDropTable, pendingCoins field, rollLoot hook, collectCoins()
# ---------------------------------------------------------------------------
combat_system_path = find_file("CombatSystem.kt")

state_old = """class CharacterCombatState(
    var currentHp: Int,
    var maxHp: Int,
    val recovery: RecoveryStatus = RecoveryStatus(),
    var session: CombatSession? = null,
    val lootPool: MutableList<LootEntry> = mutableListOf()
)"""
state_new = """class CharacterCombatState(
    var currentHp: Int,
    var maxHp: Int,
    val recovery: RecoveryStatus = RecoveryStatus(),
    var session: CombatSession? = null,
    val lootPool: MutableList<LootEntry> = mutableListOf(),
    var pendingCoins: Long = 0L
)

object CoinDropTable {
    fun rollCoins(monsterLevel: Int): Long {
        val base = (monsterLevel * 3).coerceAtLeast(1)
        val variance = (base * 0.4).toInt().coerceAtLeast(1)
        val roll = base - (variance / 2) + Random.nextInt(variance + 1)
        return roll.toLong().coerceAtLeast(1L)
    }
}"""
guarded_replace(combat_system_path, state_old, state_new)

roll_loot_old = """    private fun rollLoot(state: CharacterCombatState, monster: Monster) {
        (monster.mainLootTable + monster.rareLootTable).forEach { entry ->
            if (Random.nextDouble(0.0, 100.0) < entry.dropChancePercent) {
                val qty = Random.nextInt(entry.minQty, entry.maxQty + 1)
                state.lootPool.add(entry.copy(minQty = qty, maxQty = qty))
            }
        }
    }

    fun collectLoot(characterId: String): ServiceResult<List<LootEntry>> {
        val state = stateFor(characterId)
        val collected = state.lootPool.toList()
        state.lootPool.clear()
        return ServiceResult.Success(collected)
    }"""
roll_loot_new = """    private fun rollLoot(state: CharacterCombatState, monster: Monster) {
        (monster.mainLootTable + monster.rareLootTable).forEach { entry ->
            if (Random.nextDouble(0.0, 100.0) < entry.dropChancePercent) {
                val qty = Random.nextInt(entry.minQty, entry.maxQty + 1)
                state.lootPool.add(entry.copy(minQty = qty, maxQty = qty))
            }
        }
        state.pendingCoins += CoinDropTable.rollCoins(monster.levelRequirement)
    }

    fun collectLoot(characterId: String): ServiceResult<List<LootEntry>> {
        val state = stateFor(characterId)
        val collected = state.lootPool.toList()
        state.lootPool.clear()
        return ServiceResult.Success(collected)
    }

    fun collectCoins(characterId: String): Long {
        val state = stateFor(characterId)
        val collected = state.pendingCoins
        state.pendingCoins = 0L
        return collected
    }"""
guarded_replace(combat_system_path, roll_loot_old, roll_loot_new)

# ---------------------------------------------------------------------------
# 2. GameViewModel.kt - collect coins right alongside loot on monster defeat
# ---------------------------------------------------------------------------
game_vm_path = find_file("GameViewModel.kt")

defeat_old = """               log.add(CombatLogEntry("Defeated " + defeatedName + "!"))
                val loot = combatService.collectLoot(characterId)
                if (loot is ServiceResult.Success && loot.value.isNotEmpty()) {
                    loot.value.forEach { entry -> inventoryService.inventoryFor(characterId).addItem(entry.itemId, entry.minQty) }
                    refreshInventory()
                }
            }"""
defeat_new = """               log.add(CombatLogEntry("Defeated " + defeatedName + "!"))
                val loot = combatService.collectLoot(characterId)
                if (loot is ServiceResult.Success && loot.value.isNotEmpty()) {
                    loot.value.forEach { entry -> inventoryService.inventoryFor(characterId).addItem(entry.itemId, entry.minQty) }
                    refreshInventory()
                }
                val coinsEarned = combatService.collectCoins(characterId)
                if (coinsEarned > 0) {
                    log.add(CombatLogEntry("Found " + coinsEarned + " coins."))
                    grantCombatCoins(characterId, coinsEarned)
                }
            }"""
guarded_replace(game_vm_path, defeat_old, defeat_new)

# Add the grantCombatCoins helper function right after refreshInventory()'s definition
refresh_inv_anchor = "fun refreshInventory("
with open(game_vm_path, "r", encoding="utf-8") as f:
    vm_content = f.read()
if vm_content.count(refresh_inv_anchor) < 1:
    raise SystemExit(f"!!! ABORTING: could not find anchor '{refresh_inv_anchor}' in {game_vm_path} !!!")

# Find the end of the refreshInventory() function body (first standalone closing brace
# at the same indentation as the function's own opening line) and insert after it.
start_idx = vm_content.index(refresh_inv_anchor)
brace_open_idx = vm_content.index("{", start_idx)
depth = 0
i = brace_open_idx
while i < len(vm_content):
    if vm_content[i] == "{":
        depth += 1
    elif vm_content[i] == "}":
        depth -= 1
        if depth == 0:
            break
    i += 1
if depth != 0:
    raise SystemExit("!!! ABORTING: could not find matching closing brace for refreshInventory() !!!")
insert_at = i + 1

grant_fn = """

    private fun grantCombatCoins(characterId: String, amount: Long) {
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseMarketRepository.grantCombatCoins(supabaseCharacterId, amount)
            result.onFailure {
                _marketActionError.value = it.message ?: it.toString()
            }
            result.onSuccess {
                _marketActionError.value = null
                refreshCurrency()
            }
        }
    }"""

vm_content = vm_content[:insert_at] + grant_fn + vm_content[insert_at:]
with open(game_vm_path, "w", encoding="utf-8") as f:
    f.write(vm_content)
print(f"patched {game_vm_path} (inserted grantCombatCoins() after refreshInventory())")

# ---------------------------------------------------------------------------
# 3. SupabaseMarketRepository.kt - grantCombatCoins RPC wrapper
# ---------------------------------------------------------------------------
market_repo_path = find_file("SupabaseMarketRepository.kt")

sell_wrapper_old = """    suspend fun sellToVendor(characterId: String, itemId: String, quantity: Int, payoutPerUnit: Long): Result<Long> = runCatching {
        client.postgrest.rpc("market_sell_to_vendor", buildJsonObject {
            put("p_character_id", characterId)
            put("p_item_id", itemId)
            put("p_quantity", quantity)
            put("p_payout_per_unit", payoutPerUnit)
        }).decodeAs<Long>()
    }"""
sell_wrapper_new = """    suspend fun sellToVendor(characterId: String, itemId: String, quantity: Int, payoutPerUnit: Long): Result<Long> = runCatching {
        client.postgrest.rpc("market_sell_to_vendor", buildJsonObject {
            put("p_character_id", characterId)
            put("p_item_id", itemId)
            put("p_quantity", quantity)
            put("p_payout_per_unit", payoutPerUnit)
        }).decodeAs<Long>()
    }

    suspend fun grantCombatCoins(characterId: String, amount: Long): Result<Long> = runCatching {
        client.postgrest.rpc("combat_grant_coins", buildJsonObject {
            put("p_character_id", characterId)
            put("p_amount", amount)
        }).decodeAs<Long>()
    }"""
guarded_replace(market_repo_path, sell_wrapper_old, sell_wrapper_new)

print("ALL PATCHES APPLIED SUCCESSFULLY")
