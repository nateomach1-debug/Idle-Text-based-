# PART O (1/4): OfflineIdleMechanicsSystem.kt - BuryQueue export/restore, matching
# every other queue type. This was the missing piece causing bury queues to vanish
# on a real app close (in-memory only, never persisted to disk).
path = "app/src/main/kotlin/com/yourname/idlerpg/OfflineIdleMechanicsSystem.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor_export_class = 'data class OfflineCombatQueueExport(val characterId: String, val zoneId: String, val startedAt: String)'
count = content.count(anchor_export_class)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(
    anchor_export_class,
    anchor_export_class + '\n\ndata class BuryQueueExport(val characterId: String, val itemId: String, val targetQuantity: Int, val quantityCompleted: Int, val secondsPerAction: Long, val startedAt: String)',
    1
)

anchor_export_fn = '''    fun exportOfflineCombatQueues(): List<OfflineCombatQueueExport> =
        activeQueues.values.filterIsInstance<ActiveQueue.OfflineCombatQueue>().map {
            OfflineCombatQueueExport(it.characterId, it.zoneId, it.startedAt.toString())
        }'''
count = content.count(anchor_export_fn)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(
    anchor_export_fn,
    anchor_export_fn + '''

    fun exportBuryQueues(): List<BuryQueueExport> =
        activeQueues.values.filterIsInstance<ActiveQueue.BuryQueue>().map {
            BuryQueueExport(it.characterId, it.itemId, it.targetQuantity, it.quantityCompleted, it.secondsPerAction, it.startedAt.toString())
        }''',
    1
)

anchor_restore_fn = '''    fun restoreOfflineCombatQueue(export: OfflineCombatQueueExport) {
        activeQueues[export.characterId] = ActiveQueue.OfflineCombatQueue(
            characterId = export.characterId,
            zoneId = export.zoneId,
            startedAt = Instant.parse(export.startedAt)
        )
    }
}'''
count = content.count(anchor_restore_fn)
assert count == 1, f"Expected 1 match, found {count}."
replacement_restore_fn = '''    fun restoreOfflineCombatQueue(export: OfflineCombatQueueExport) {
        activeQueues[export.characterId] = ActiveQueue.OfflineCombatQueue(
            characterId = export.characterId,
            zoneId = export.zoneId,
            startedAt = Instant.parse(export.startedAt)
        )
    }

    fun restoreBuryQueue(export: BuryQueueExport) {
        activeQueues[export.characterId] = ActiveQueue.BuryQueue(
            characterId = export.characterId,
            itemId = export.itemId,
            targetQuantity = export.targetQuantity,
            quantityCompleted = export.quantityCompleted,
            secondsPerAction = export.secondsPerAction,
            startedAt = Instant.parse(export.startedAt)
        )
    }
}'''
content = content.replace(anchor_restore_fn, replacement_restore_fn, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part O (1/4 - OfflineIdleMechanicsSystem.kt) applied cleanly.")

# PART O (2/4): GameStateRepository.kt - thread buryQueues through save()/load()/SavedGameState.
path = "app/src/main/kotlin/com/yourname/idlerpg/GameStateRepository.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor_sig = '''        combatSessions: List<CombatSessionExport> = emptyList(),
        offlineCombatQueues: List<OfflineCombatQueueExport> = emptyList()
    ) {'''
count = content.count(anchor_sig)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(
    anchor_sig,
    '''        combatSessions: List<CombatSessionExport> = emptyList(),
        offlineCombatQueues: List<OfflineCombatQueueExport> = emptyList(),
        buryQueues: List<BuryQueueExport> = emptyList()
    ) {''',
    1
)

anchor_save_tail = '''            obj.put("startedAt", q.startedAt)
            offlineCombatQueuesArray.put(obj)
        }
        root.put("offlineCombatQueues", offlineCombatQueuesArray)

        saveFile.writeText(root.toString())'''
count = content.count(anchor_save_tail)
assert count == 1, f"Expected 1 match, found {count}."
replacement_save_tail = '''            obj.put("startedAt", q.startedAt)
            offlineCombatQueuesArray.put(obj)
        }
        root.put("offlineCombatQueues", offlineCombatQueuesArray)

        val buryQueuesArray = JSONArray()
        buryQueues.forEach { q ->
            val obj = JSONObject()
            obj.put("characterId", q.characterId)
            obj.put("itemId", q.itemId)
            obj.put("targetQuantity", q.targetQuantity)
            obj.put("quantityCompleted", q.quantityCompleted)
            obj.put("secondsPerAction", q.secondsPerAction)
            obj.put("startedAt", q.startedAt)
            buryQueuesArray.put(obj)
        }
        root.put("buryQueues", buryQueuesArray)

        saveFile.writeText(root.toString())'''
content = content.replace(anchor_save_tail, replacement_save_tail, 1)

anchor_load_tail = '''        val offlineCombatQueues = mutableListOf<OfflineCombatQueueExport>()
        val offlineCombatQueuesArray = root.optJSONArray("offlineCombatQueues") ?: JSONArray()
        for (i in 0 until offlineCombatQueuesArray.length()) {
            val obj = offlineCombatQueuesArray.getJSONObject(i)
            offlineCombatQueues.add(
                OfflineCombatQueueExport(
                    characterId = obj.getString("characterId"),
                    zoneId = obj.getString("zoneId"),
                    startedAt = obj.getString("startedAt")
                )
            )
        }

        val inventoryItems = mutableListOf<InventorySlotExport>()'''
count = content.count(anchor_load_tail)
assert count == 1, f"Expected 1 match, found {count}."
replacement_load_tail = '''        val offlineCombatQueues = mutableListOf<OfflineCombatQueueExport>()
        val offlineCombatQueuesArray = root.optJSONArray("offlineCombatQueues") ?: JSONArray()
        for (i in 0 until offlineCombatQueuesArray.length()) {
            val obj = offlineCombatQueuesArray.getJSONObject(i)
            offlineCombatQueues.add(
                OfflineCombatQueueExport(
                    characterId = obj.getString("characterId"),
                    zoneId = obj.getString("zoneId"),
                    startedAt = obj.getString("startedAt")
                )
            )
        }

        val buryQueues = mutableListOf<BuryQueueExport>()
        val buryQueuesArray = root.optJSONArray("buryQueues") ?: JSONArray()
        for (i in 0 until buryQueuesArray.length()) {
            val obj = buryQueuesArray.getJSONObject(i)
            buryQueues.add(
                BuryQueueExport(
                    characterId = obj.getString("characterId"),
                    itemId = obj.getString("itemId"),
                    targetQuantity = obj.getInt("targetQuantity"),
                    quantityCompleted = obj.getInt("quantityCompleted"),
                    secondsPerAction = obj.getLong("secondsPerAction"),
                    startedAt = obj.getString("startedAt")
                )
            )
        }

        val inventoryItems = mutableListOf<InventorySlotExport>()'''
content = content.replace(anchor_load_tail, replacement_load_tail, 1)

anchor_return = '''        return SavedGameState(
            accounts, characters, skills, skillingQueues, craftingQueues, lastSeen, lastSaleCheck, inventoryItems, equippedSlots,
            loadoutSettings, marketAccounts, marketOrders, marketPriceHistory, combatSessions, offlineCombatQueues
        )'''
count = content.count(anchor_return)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(
    anchor_return,
    '''        return SavedGameState(
            accounts, characters, skills, skillingQueues, craftingQueues, lastSeen, lastSaleCheck, inventoryItems, equippedSlots,
            loadoutSettings, marketAccounts, marketOrders, marketPriceHistory, combatSessions, offlineCombatQueues, buryQueues
        )''',
    1
)

anchor_class = '''    val combatSessions: List<CombatSessionExport> = emptyList(),
    val offlineCombatQueues: List<OfflineCombatQueueExport> = emptyList()
)'''
count = content.count(anchor_class)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(
    anchor_class,
    '''    val combatSessions: List<CombatSessionExport> = emptyList(),
    val offlineCombatQueues: List<OfflineCombatQueueExport> = emptyList(),
    val buryQueues: List<BuryQueueExport> = emptyList()
)''',
    1
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part O (2/4 - GameStateRepository.kt) applied cleanly.")

# PART O (3/4): ItemsEquipmentSystem.kt - add trainingSkillId to Inventory (a
# natural per-character home for it) and to LoadoutSettingsExport/its export-restore.
path = "app/src/main/kotlin/com/yourname/idlerpg/ItemsEquipmentSystem.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor_inv_fields = '''    var autoFleeThresholdPercent: Int = 10,
    var selectedPrayerId: String? = null
) {'''
count = content.count(anchor_inv_fields)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(
    anchor_inv_fields,
    '''    var autoFleeThresholdPercent: Int = 10,
    var selectedPrayerId: String? = null,
    var trainingSkillId: String? = null
) {''',
    1
)

anchor_export_class = '''    val autoFleeThresholdPercent: Int,
    val selectedPrayerId: String? = null
)'''
count = content.count(anchor_export_class)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(
    anchor_export_class,
    '''    val autoFleeThresholdPercent: Int,
    val selectedPrayerId: String? = null,
    val trainingSkillId: String? = null
)''',
    1
)

anchor_export_restore_fns = '''    fun exportAllLoadoutSettings(): List<LoadoutSettingsExport> = inventories.map { (characterId, inv) ->
        LoadoutSettingsExport(
            characterId, inv.selectedFoodId, inv.selectedPotionId, inv.potionTimerRemainingSeconds,
            inv.autoHealThresholdPercent, inv.autoFleeThresholdPercent, inv.selectedPrayerId
        )
    }

    fun restoreLoadoutSettings(export: LoadoutSettingsExport) {
        val inv = inventoryFor(export.characterId)
        inv.selectedFoodId = export.selectedFoodId
        inv.selectedPotionId = export.selectedPotionId
        inv.potionTimerRemainingSeconds = export.potionTimerRemainingSeconds
        inv.autoHealThresholdPercent = export.autoHealThresholdPercent
        inv.autoFleeThresholdPercent = export.autoFleeThresholdPercent
        inv.selectedPrayerId = export.selectedPrayerId
    }'''
count = content.count(anchor_export_restore_fns)
assert count == 1, f"Expected 1 match, found {count}."
replacement_export_restore_fns = '''    fun exportAllLoadoutSettings(): List<LoadoutSettingsExport> = inventories.map { (characterId, inv) ->
        LoadoutSettingsExport(
            characterId, inv.selectedFoodId, inv.selectedPotionId, inv.potionTimerRemainingSeconds,
            inv.autoHealThresholdPercent, inv.autoFleeThresholdPercent, inv.selectedPrayerId, inv.trainingSkillId
        )
    }

    fun restoreLoadoutSettings(export: LoadoutSettingsExport) {
        val inv = inventoryFor(export.characterId)
        inv.selectedFoodId = export.selectedFoodId
        inv.selectedPotionId = export.selectedPotionId
        inv.potionTimerRemainingSeconds = export.potionTimerRemainingSeconds
        inv.autoHealThresholdPercent = export.autoHealThresholdPercent
        inv.autoFleeThresholdPercent = export.autoFleeThresholdPercent
        inv.selectedPrayerId = export.selectedPrayerId
        inv.trainingSkillId = export.trainingSkillId
    }'''
content = content.replace(anchor_export_restore_fns, replacement_export_restore_fns, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part O (3/4 - ItemsEquipmentSystem.kt) applied cleanly.")

# PART O (4/4): GameViewModel.kt - sync trainingSkillId into the current
# character's Inventory before saving, export/restore buryQueues at all three
# restore sites, and restore the training skill early in selectCharacter()
# (before resolveOfflineRewardsAndSync() runs later in the same flow - this is
# what actually fixes offline combat XP defaulting to Attack).
path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor_savegame = '''    fun saveGame() {
        repository.save(
            accountService.exportAllAccounts(),
            accountService.exportAllCharacters(),
            progressionService.exportAllSkills(),
            offlineIdleService.exportSkillingQueues(),
            offlineIdleService.exportCraftingQueues(),
            offlineIdleService.exportLastSeen(),
            offlineIdleService.exportLastSaleCheck(),
            inventoryService.exportAllItems(),
            inventoryService.exportAllEquipped(),
            inventoryService.exportAllLoadoutSettings(),
            marketService.exportAccounts(),
            marketService.exportOrders(),
            marketService.exportPriceHistory(),
            combatService.exportSessions(),
            offlineIdleService.exportOfflineCombatQueues()
        )'''
count = content.count(anchor_savegame)
assert count == 1, f"Expected 1 match, found {count}."
replacement_savegame = '''    fun saveGame() {
        _currentCharacterId.value?.let { characterId ->
            inventoryService.inventoryFor(characterId).trainingSkillId = _trainingSkill.value.name
        }
        repository.save(
            accountService.exportAllAccounts(),
            accountService.exportAllCharacters(),
            progressionService.exportAllSkills(),
            offlineIdleService.exportSkillingQueues(),
            offlineIdleService.exportCraftingQueues(),
            offlineIdleService.exportLastSeen(),
            offlineIdleService.exportLastSaleCheck(),
            inventoryService.exportAllItems(),
            inventoryService.exportAllEquipped(),
            inventoryService.exportAllLoadoutSettings(),
            marketService.exportAccounts(),
            marketService.exportOrders(),
            marketService.exportPriceHistory(),
            combatService.exportSessions(),
            offlineIdleService.exportOfflineCombatQueues(),
            offlineIdleService.exportBuryQueues()
        )'''
content = content.replace(anchor_savegame, replacement_savegame, 1)

anchor_loadgame_restore = '''        saved.combatSessions.forEach { combatService.restoreSession(it) }
        saved.offlineCombatQueues.forEach { offlineIdleService.restoreOfflineCombatQueue(it) }
    }
suspend fun login(email: String, password: String): ServiceResult<Account> {'''
count = content.count(anchor_loadgame_restore)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(
    anchor_loadgame_restore,
    '''        saved.combatSessions.forEach { combatService.restoreSession(it) }
        saved.offlineCombatQueues.forEach { offlineIdleService.restoreOfflineCombatQueue(it) }
        saved.buryQueues.forEach { offlineIdleService.restoreBuryQueue(it) }
    }
suspend fun login(email: String, password: String): ServiceResult<Account> {''',
    1
)

anchor_recovery_restore = '''    recovered.combatSessions.forEach { combatService.restoreSession(it) }
    recovered.offlineCombatQueues.forEach { offlineIdleService.restoreOfflineCombatQueue(it) }

    val recoveredAccountExport = recovered.accounts.firstOrNull { it.email.equals(email, ignoreCase = true) }'''
count = content.count(anchor_recovery_restore)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(
    anchor_recovery_restore,
    '''    recovered.combatSessions.forEach { combatService.restoreSession(it) }
    recovered.offlineCombatQueues.forEach { offlineIdleService.restoreOfflineCombatQueue(it) }
    recovered.buryQueues.forEach { offlineIdleService.restoreBuryQueue(it) }

    val recoveredAccountExport = recovered.accounts.firstOrNull { it.email.equals(email, ignoreCase = true) }''',
    1
)

anchor_mismatch_restore = '''                                recovered.combatSessions.forEach { combatService.restoreSession(it) }
                                recovered.offlineCombatQueues.forEach { offlineIdleService.restoreOfflineCombatQueue(it) }
                                _currentCharacterId.value = remoteLocalId'''
count = content.count(anchor_mismatch_restore)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(
    anchor_mismatch_restore,
    '''                                recovered.combatSessions.forEach { combatService.restoreSession(it) }
                                recovered.offlineCombatQueues.forEach { offlineIdleService.restoreOfflineCombatQueue(it) }
                                recovered.buryQueues.forEach { offlineIdleService.restoreBuryQueue(it) }
                                _currentCharacterId.value = remoteLocalId''',
    1
)

anchor_final = '''                // Only one of these ever fires per selection: whichever character id
                // turned out to be correct once the async cloud-recovery check above
                // finished. Previously an immediate, unconditional call fired outside
                // this coroutine entirely, racing this check - it would briefly show
                // an offline-progress popup built from the wrong (pre-recovery)
                // character before this corrected one silently replaced it.
                resolveOfflineRewardsAndSync(recoveredToRemoteId ?: characterId)'''
count = content.count(anchor_final)
assert count == 1, f"Expected 1 match, found {count}."
replacement_final = '''                val finalCharacterId = recoveredToRemoteId ?: characterId
                // Restore the persisted training skill for THIS character before
                // resolving offline rewards below - previously trainingSkill stayed
                // at its hardcoded ATTACK default every cold start (never restored
                // anywhere), so offline combat XP always landed on Attack regardless
                // of what the player had actually selected before closing the app.
                val restoredTrainingSkillId = inventoryService.inventoryFor(finalCharacterId).trainingSkillId
                val restoredTrainingSkill = restoredTrainingSkillId?.let {
                    runCatching { SkillType.valueOf(it) }.getOrNull()
                } ?: SkillType.ATTACK
                setTrainingSkill(restoredTrainingSkill)
                // Only one of these ever fires per selection: whichever character id
                // turned out to be correct once the async cloud-recovery check above
                // finished. Previously an immediate, unconditional call fired outside
                // this coroutine entirely, racing this check - it would briefly show
                // an offline-progress popup built from the wrong (pre-recovery)
                // character before this corrected one silently replaced it.
                resolveOfflineRewardsAndSync(finalCharacterId)'''
content = content.replace(anchor_final, replacement_final, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part O (4/4 - GameViewModel.kt) applied cleanly.")
