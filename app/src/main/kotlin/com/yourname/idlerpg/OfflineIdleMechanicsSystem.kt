package com.yourname.idlerpg

import java.time.Duration
import java.time.Instant

// =========================================================
// QUEUE TYPES
// =========================================================

enum class QueueType { SKILLING, CRAFTING, OFFLINE_COMBAT, BURYING }

sealed class ActiveQueue {
    abstract val characterId: String
    abstract val startedAt: Instant
    abstract val type: QueueType

    data class SkillingQueue(
        override val characterId: String,
        val skillId: String,
        val itemId: String,
        val secondsPerAction: Long,
        override val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.SKILLING
    }

    data class CraftingQueue(
        override val characterId: String,
        val itemId: String,
        val secondsPerAction: Long,
        val targetQuantity: Int?,
        var quantityCompleted: Int = 0,
        override val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.CRAFTING
        fun isTargetReached(): Boolean = targetQuantity != null && quantityCompleted >= targetQuantity
    }

    data class OfflineCombatQueue(
        override val characterId: String,
        val zoneId: String,
        override val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.OFFLINE_COMBAT
    }

    data class BuryQueue(
        override val characterId: String,
        val itemId: String,
        val targetQuantity: Int,
        var quantityCompleted: Int = 0,
        val secondsPerAction: Long,
        override val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.BURYING
        fun isTargetReached(): Boolean = quantityCompleted >= targetQuantity
    }
}

// =========================================================
// MATERIAL AVAILABILITY
// =========================================================

fun interface MaterialAvailabilityCheck {
    fun hasMaterialsFor(characterId: String, itemId: String): Boolean
}

// =========================================================
// EFFICIENCY TAPER
// =========================================================

object OfflineEfficiencyCurve {
    private const val FULL_RATE_PERCENT = 100.0
    private const val REDUCED_RATE_PERCENT = 50.0
    private const val FLOOR_RATE_PERCENT = 0.0

    fun efficiencyAt(
        elapsed: Duration,
        premiumMembershipActive: Boolean = false
    ): Double {
        val fullRateWindow =
            Duration.ofHours(if (premiumMembershipActive) 24 else 12)
        val reducedRateWindow =
            Duration.ofHours(if (premiumMembershipActive) 48 else 24)

        return when {
            elapsed <= fullRateWindow -> FULL_RATE_PERCENT
            elapsed <= reducedRateWindow -> REDUCED_RATE_PERCENT
            else -> FLOOR_RATE_PERCENT
        }
    }

    fun effectiveElapsed(
        elapsed: Duration,
        premiumMembershipActive: Boolean = false
    ): Duration {
        val fullRateWindow =
            Duration.ofHours(if (premiumMembershipActive) 24 else 12)
        val reducedRateWindow =
            Duration.ofHours(if (premiumMembershipActive) 48 else 24)

        if (elapsed <= fullRateWindow) return elapsed

        val fullMillis = fullRateWindow.toMillis()
        val reducedEndMillis =
            minOf(elapsed.toMillis(), reducedRateWindow.toMillis())

        val reducedMillis =
            (reducedEndMillis - fullMillis).coerceAtLeast(0)

        val floorMillis =
            (elapsed.toMillis() - reducedRateWindow.toMillis())
                .coerceAtLeast(0)

        val effectiveMillis =
            (fullMillis * (FULL_RATE_PERCENT / 100.0)) +
            (reducedMillis * (REDUCED_RATE_PERCENT / 100.0)) +
            (floorMillis * (FLOOR_RATE_PERCENT / 100.0))

        return Duration.ofMillis(effectiveMillis.toLong())
    }
}

// =========================================================
// ANTI-CHEAT SANITY CHECK
// =========================================================

data class OfflineFlagRecord(
    val characterId: String,
    val claimedElapsed: Duration,
    val cappedElapsed: Duration,
    val flaggedAt: Instant = Instant.now()
)

object OfflineSanityCheck {
    val maxPlausibleElapsed: Duration = Duration.ofDays(30)

    fun validate(characterId: String, claimedElapsed: Duration): Pair<Duration, OfflineFlagRecord?> {
        if (claimedElapsed <= maxPlausibleElapsed) return claimedElapsed to null

        val flag = OfflineFlagRecord(
            characterId = characterId,
            claimedElapsed = claimedElapsed,
            cappedElapsed = maxPlausibleElapsed
        )
        return maxPlausibleElapsed to flag
    }
}

// =========================================================
// RESULT TYPES
// (ServiceResult now comes from SharedTypes.kt.)
// =========================================================

data class OfflineResolution(
    val characterId: String,
    val queueType: QueueType,
    val claimedElapsed: Duration,
    val cappedElapsed: Duration,
    val effectiveElapsed: Duration,
    val actionsCompleted: Int,
    val wasFlagged: Boolean,
    val queueExhausted: Boolean
)

data class SkillingQueueExport(
    val characterId: String,
    val skillId: String,
    val itemId: String,
    val secondsPerAction: Long,
    val startedAt: String
)

data class CraftingQueueExport(
    val characterId: String,
    val itemId: String,
    val secondsPerAction: Long,
    val targetQuantity: Int?,
    val quantityCompleted: Int,
    val startedAt: String
)

data class LastSeenExport(val characterId: String, val lastSeenAt: String)

data class LastSaleCheckExport(val characterId: String, val lastSaleCheckAt: String)

data class OfflineCombatQueueExport(val characterId: String, val zoneId: String, val startedAt: String)

data class BuryQueueExport(val characterId: String, val itemId: String, val targetQuantity: Int, val quantityCompleted: Int, val secondsPerAction: Long, val startedAt: String)

// =========================================================
// OFFLINE/IDLE SERVICE
// =========================================================

class OfflineIdleService(private val materialCheck: MaterialAvailabilityCheck) {

    private val activeQueues: MutableMap<String, ActiveQueue> = mutableMapOf()
    private val lastSeenAt: MutableMap<String, Instant> = mutableMapOf()
    private val lastSaleCheckAt: MutableMap<String, Instant> = mutableMapOf()
    private val flaggedAccounts: MutableList<OfflineFlagRecord> = mutableListOf()

    fun startSkillingQueue(characterId: String, skillId: String, itemId: String, secondsPerAction: Long): ServiceResult<ActiveQueue> {
        if (activeQueues.containsKey(characterId)) {
            return ServiceResult.Failure("Character already has an active queue. Stop it before starting a new one.")
        }
        val queue = ActiveQueue.SkillingQueue(characterId, skillId, itemId, secondsPerAction)
        activeQueues[characterId] = queue
        return ServiceResult.Success(queue)
    }

    fun startCraftingQueue(
        characterId: String,
        itemId: String,
        secondsPerAction: Long,
        targetQuantity: Int?
    ): ServiceResult<ActiveQueue> {
        if (activeQueues.containsKey(characterId)) {
            return ServiceResult.Failure("Character already has an active queue. Stop it before starting a new one.")
        }
        if (targetQuantity != null && targetQuantity <= 0) {
            return ServiceResult.Failure("Target quantity must be positive if specified.")
        }
        val queue = ActiveQueue.CraftingQueue(characterId, itemId, secondsPerAction, targetQuantity)
        activeQueues[characterId] = queue
        return ServiceResult.Success(queue)
    }

    fun optIntoOfflineCombat(characterId: String, zoneId: String): ServiceResult<ActiveQueue> {
        if (activeQueues.containsKey(characterId)) {
            return ServiceResult.Failure("Character already has an active queue. Stop it before opting into offline combat.")
        }
        val queue = ActiveQueue.OfflineCombatQueue(characterId, zoneId)
        activeQueues[characterId] = queue
        return ServiceResult.Success(queue)
    }

    fun stopQueue(characterId: String): ServiceResult<Unit> {
        if (!activeQueues.containsKey(characterId)) return ServiceResult.Failure("No active queue to stop.")
        activeQueues.remove(characterId)
        return ServiceResult.Success(Unit)
    }

    fun activeQueueFor(characterId: String): ActiveQueue? = activeQueues[characterId]

    fun recordLastSeen(characterId: String, now: Instant = Instant.now()) {
        lastSeenAt[characterId] = now
    }

    fun recordSaleCheck(characterId: String, now: Instant = Instant.now()) {
        lastSaleCheckAt[characterId] = now
    }

    fun lastSaleCheckFor(characterId: String): Instant? = lastSaleCheckAt[characterId]

    fun lastSeenFor(characterId: String): Instant? = lastSeenAt[characterId]
    
    fun recordSaleCheckAt(characterId: String, serverTimestamp: String) {
        lastSaleCheckAt[characterId] = java.time.OffsetDateTime.parse(serverTimestamp).toInstant()
    }

    fun resolveOfflineProgress(characterId: String, now: Instant = Instant.now(), premiumMembershipActive: Boolean = false ): ServiceResult<OfflineResolution> {
        val queue = activeQueues[characterId] ?: return ServiceResult.Failure("No active queue to resolve.")
        val lastSeen = lastSeenAt[characterId] ?: return ServiceResult.Failure("No last-seen timestamp recorded.")

        val claimedElapsed = Duration.between(lastSeen, now)
        if (claimedElapsed.isNegative) return ServiceResult.Failure("Invalid elapsed time (negative duration).")

        val (cappedElapsed, flag) = OfflineSanityCheck.validate(characterId, claimedElapsed)
        if (flag != null) flaggedAccounts.add(flag)

        val combatPenaltyMultiplier = if (queue.type == QueueType.OFFLINE_COMBAT) 0.8 else 1.0
        val effectiveElapsed = OfflineEfficiencyCurve.effectiveElapsed(cappedElapsed, premiumMembershipActive)
        val penalizedEffectiveMillis = (effectiveElapsed.toMillis() * combatPenaltyMultiplier).toLong()
        val finalEffectiveElapsed = Duration.ofMillis(penalizedEffectiveMillis)

        var actionsCompleted = 0
        var queueExhausted = false

        when (queue) {
            is ActiveQueue.SkillingQueue -> {
                actionsCompleted =
                    (finalEffectiveElapsed.seconds / queue.secondsPerAction).toInt()
            }
            
is ActiveQueue.CraftingQueue -> {
    var possibleActions =
        (finalEffectiveElapsed.seconds / queue.secondsPerAction).toInt()

    if (queue.targetQuantity != null) {
        val remaining = (queue.targetQuantity - queue.quantityCompleted)
            .coerceAtLeast(0)
        possibleActions = possibleActions.coerceAtMost(remaining)
    }

    // Report the potential attempts only.
    // GameViewModel will perform the crafts and record actual attempts.
    actionsCompleted = possibleActions
}

            is ActiveQueue.OfflineCombatQueue -> {
    actionsCompleted = 0
}

is ActiveQueue.BuryQueue -> {
    val possibleActions =
        (finalEffectiveElapsed.seconds / queue.secondsPerAction).toInt()

    val remaining =
        (queue.targetQuantity - queue.quantityCompleted).coerceAtLeast(0)

    // Report potential actions only. GameViewModel updates completed
    // progress after checking and consuming the available bones.
    actionsCompleted = possibleActions.coerceAtMost(remaining)
}
            }
        }

        if (queueExhausted) {
            activeQueues.remove(characterId)
        }

        return ServiceResult.Success(
            OfflineResolution(
                characterId = characterId,
                queueType = queue.type,
                claimedElapsed = claimedElapsed,
                cappedElapsed = cappedElapsed,
                effectiveElapsed = finalEffectiveElapsed,
                actionsCompleted = actionsCompleted,
                wasFlagged = flag != null,
                queueExhausted = queueExhausted
            )
        )
    }

    fun estimatedTimeUntilExhausted(characterId: String): Duration? {
        val queue = activeQueues[characterId] as? ActiveQueue.CraftingQueue ?: return null
        val target = queue.targetQuantity ?: return null
        val remaining = target - queue.quantityCompleted
        if (remaining <= 0) return Duration.ZERO
        return Duration.ofSeconds(remaining * queue.secondsPerAction)
    }

    fun allFlaggedAccounts(): List<OfflineFlagRecord> = flaggedAccounts.toList()

    fun exportSkillingQueues(): List<SkillingQueueExport> =
        activeQueues.values.filterIsInstance<ActiveQueue.SkillingQueue>().map {
            SkillingQueueExport(it.characterId, it.skillId, it.itemId, it.secondsPerAction, it.startedAt.toString())
        }

    fun exportCraftingQueues(): List<CraftingQueueExport> =
        activeQueues.values.filterIsInstance<ActiveQueue.CraftingQueue>().map {
            CraftingQueueExport(
                it.characterId,
                it.itemId,
                it.secondsPerAction,
                it.targetQuantity,
                it.quantityCompleted,
                it.startedAt.toString()
            )
        }

    fun exportLastSeen(): List<LastSeenExport> =
        lastSeenAt.map { (characterId, instant) -> LastSeenExport(characterId, instant.toString()) }

    fun exportLastSaleCheck(): List<LastSaleCheckExport> =
        lastSaleCheckAt.map { (characterId, instant) -> LastSaleCheckExport(characterId, instant.toString()) }

    fun startBuryQueue(characterId: String, itemId: String, targetQuantity: Int, secondsPerAction: Long): ServiceResult<ActiveQueue> {
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

    fun exportOfflineCombatQueues(): List<OfflineCombatQueueExport> =
        activeQueues.values.filterIsInstance<ActiveQueue.OfflineCombatQueue>().map {
            OfflineCombatQueueExport(it.characterId, it.zoneId, it.startedAt.toString())
        }

    fun exportBuryQueues(): List<BuryQueueExport> =
        activeQueues.values.filterIsInstance<ActiveQueue.BuryQueue>().map {
            BuryQueueExport(it.characterId, it.itemId, it.targetQuantity, it.quantityCompleted, it.secondsPerAction, it.startedAt.toString())
        }

    fun restoreSkillingQueue(export: SkillingQueueExport) {
        activeQueues[export.characterId] = ActiveQueue.SkillingQueue(
            characterId = export.characterId,
            skillId = export.skillId,
            itemId = export.itemId,
            secondsPerAction = export.secondsPerAction,
            startedAt = Instant.parse(export.startedAt)
        )
    }

    fun restoreCraftingQueue(export: CraftingQueueExport) {
        val queue = ActiveQueue.CraftingQueue(
            characterId = export.characterId,
            itemId = export.itemId,
            secondsPerAction = export.secondsPerAction,
            targetQuantity = export.targetQuantity,
            startedAt = Instant.parse(export.startedAt)
        )
        queue.quantityCompleted = export.quantityCompleted
        activeQueues[export.characterId] = queue
    }

    fun restoreLastSeen(export: LastSeenExport) {
        lastSeenAt[export.characterId] = Instant.parse(export.lastSeenAt)
    }

    fun restoreLastSaleCheck(export: LastSaleCheckExport) {
        lastSaleCheckAt[export.characterId] = Instant.parse(export.lastSaleCheckAt)
    }

    fun restoreOfflineCombatQueue(export: OfflineCombatQueueExport) {
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
}
