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
