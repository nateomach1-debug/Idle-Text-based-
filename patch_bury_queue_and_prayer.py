# PART A: OfflineIdleMechanicsSystem.kt - new BuryQueue queue type
path = "app/src/main/kotlin/com/yourname/idlerpg/OfflineIdleMechanicsSystem.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor_queuetype = "enum class QueueType { SKILLING, CRAFTING, OFFLINE_COMBAT }"
count = content.count(anchor_queuetype)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(anchor_queuetype, "enum class QueueType { SKILLING, CRAFTING, OFFLINE_COMBAT, BURYING }", 1)

anchor_activequeue_combat = '''    data class OfflineCombatQueue(
        override val characterId: String,
        val zoneId: String,
        val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.OFFLINE_COMBAT
    }
}'''
count = content.count(anchor_activequeue_combat)
assert count == 1, f"Expected 1 match, found {count}."
replacement_activequeue_combat = '''    data class OfflineCombatQueue(
        override val characterId: String,
        val zoneId: String,
        val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.OFFLINE_COMBAT
    }

    data class BuryQueue(
        override val characterId: String,
        val itemId: String,
        val targetQuantity: Int,
        var quantityCompleted: Int = 0,
        val secondsPerAction: Int,
        val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.BURYING
        fun isTargetReached(): Boolean = quantityCompleted >= targetQuantity
    }
}'''
content = content.replace(anchor_activequeue_combat, replacement_activequeue_combat, 1)

anchor_start_combat_queue_end = '''    fun exportOfflineCombatQueues(): List<OfflineCombatQueueExport> ='''
count = content.count(anchor_start_combat_queue_end)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(
    anchor_start_combat_queue_end,
    '''    fun startBuryQueue(characterId: String, itemId: String, targetQuantity: Int, secondsPerAction: Int): ServiceResult<ActiveQueue> {
        if (activeQueues.containsKey(characterId)) {
            return ServiceResult.Failure("Character already has an active queue. Stop it before starting a new one.")
        }
        if (targetQuantity <= 0) {
            return ServiceResult.Failure("Target quantity must be positive.")
        }
        val queue = ActiveQueue.BuryQueue(characterId, itemId, targetQuantity, secondsPerAction = secondsPerAction)
        activeQueues[characterId] = queue
        return ServiceResult.Success(queue)
    }

    fun exportOfflineCombatQueues(): List<OfflineCombatQueueExport> =''',
    1
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part A (OfflineIdleMechanicsSystem.kt) applied cleanly.")

# PART B: ItemsEquipmentSystem.kt - selectedPrayerId storage + persistence
path = "app/src/main/kotlin/com/yourname/idlerpg/ItemsEquipmentSystem.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor_inv_fields = '''    var selectedFoodId: String? = null,
    var selectedPotionId: String? = null,
    var potionTimerRemainingSeconds: Int = 0,
    var autoHealThresholdPercent: Int = 30,
    var autoFleeThresholdPercent: Int = 10
) {'''
count = content.count(anchor_inv_fields)
assert count == 1, f"Expected 1 match, found {count}."
replacement_inv_fields = '''    var selectedFoodId: String? = null,
    var selectedPotionId: String? = null,
    var potionTimerRemainingSeconds: Int = 0,
    var autoHealThresholdPercent: Int = 30,
    var autoFleeThresholdPercent: Int = 10,
    var selectedPrayerId: String? = null
) {'''
content = content.replace(anchor_inv_fields, replacement_inv_fields, 1)

anchor_select_potion_fn = '''    fun selectPotion(itemId: String?): ServiceResult<Unit> {
        if (itemId != null) {
            val definition = ItemCatalog.find(itemId) ?: return ServiceResult.Failure("Unknown item.")
            if (definition.consumableType != ConsumableType.POTION) return ServiceResult.Failure("Not a potion item.")
        }
        selectedPotionId = itemId
        potionTimerRemainingSeconds = 0
        return ServiceResult.Success(Unit)
    }'''
count = content.count(anchor_select_potion_fn)
assert count == 1, f"Expected 1 match, found {count}."
replacement_select_potion_fn = anchor_select_potion_fn + '''

    fun selectPrayer(prayerId: String?): ServiceResult<Unit> {
        if (prayerId != null && PrayerCatalog.none { it.id == prayerId }) {
            return ServiceResult.Failure("Unknown prayer.")
        }
        selectedPrayerId = prayerId
        return ServiceResult.Success(Unit)
    }'''
content = content.replace(anchor_select_potion_fn, replacement_select_potion_fn, 1)

anchor_export_class = '''data class LoadoutSettingsExport(
    val characterId: String,
    val selectedFoodId: String?,
    val selectedPotionId: String?,
    val potionTimerRemainingSeconds: Int,
    val autoHealThresholdPercent: Int,
    val autoFleeThresholdPercent: Int
)'''
count = content.count(anchor_export_class)
assert count == 1, f"Expected 1 match, found {count}."
replacement_export_class = '''data class LoadoutSettingsExport(
    val characterId: String,
    val selectedFoodId: String?,
    val selectedPotionId: String?,
    val potionTimerRemainingSeconds: Int,
    val autoHealThresholdPercent: Int,
    val autoFleeThresholdPercent: Int,
    val selectedPrayerId: String? = null
)'''
content = content.replace(anchor_export_class, replacement_export_class, 1)

anchor_export_fn = '''    fun exportAllLoadoutSettings(): List<LoadoutSettingsExport> = inventories.map { (characterId, inv) ->
        LoadoutSettingsExport(
            characterId, inv.selectedFoodId, inv.selectedPotionId, inv.potionTimerRemainingSeconds,
            inv.autoHealThresholdPercent, inv.autoFleeThresholdPercent
        )
    }

    fun restoreLoadoutSettings(export: LoadoutSettingsExport) {
        val inv = inventoryFor(export.characterId)
        inv.selectedFoodId = export.selectedFoodId
        inv.selectedPotionId = export.selectedPotionId
        inv.potionTimerRemainingSeconds = export.potionTimerRemainingSeconds
        inv.autoHealThresholdPercent = export.autoHealThresholdPercent
        inv.autoFleeThresholdPercent = export.autoFleeThresholdPercent
    }'''
count = content.count(anchor_export_fn)
assert count == 1, f"Expected 1 match, found {count}."
replacement_export_fn = '''    fun exportAllLoadoutSettings(): List<LoadoutSettingsExport> = inventories.map { (characterId, inv) ->
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
content = content.replace(anchor_export_fn, replacement_export_fn, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part B (ItemsEquipmentSystem.kt) applied cleanly.")
