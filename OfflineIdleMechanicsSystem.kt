import java.time.Duration
import java.time.Instant
import java.util.UUID

// =========================================================
// QUEUE TYPES
// (Only one of these can be active per character at a time.)
// =========================================================

enum class QueueType { SKILLING, CRAFTING, OFFLINE_COMBAT }

sealed class ActiveQueue {
    abstract val characterId: String
    abstract val startedAt: Instant
    abstract val type: QueueType

    /** Gathering/production skills with no quantity cap -- runs until manually stopped. */
    data class SkillingQueue(
        override val characterId: String,
        val skillId: String,
        val itemId: String,
        val secondsPerAction: Long,
        override val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.SKILLING
    }

    /** Either a fixed target quantity, or indefinite (runs until materials run out). */
    data class CraftingQueue(
        override val characterId: String,
        val itemId: String,
        val secondsPerAction: Long,
        val targetQuantity: Int?, // null means indefinite -- stop condition is material depletion
        var quantityCompleted: Int = 0,
        override val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.CRAFTING
        fun isTargetReached(): Boolean = targetQuantity != null && quantityCompleted >= targetQuantity
    }

    /** Opt-in only; mutually exclusive with any skilling/crafting queue. */
    data class OfflineCombatQueue(
        override val characterId: String,
        val zoneId: String,
        override val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.OFFLINE_COMBAT
    }
}

// =========================================================
// MATERIAL AVAILABILITY (minimal stand-in until Items/Inventory exists)
// =========================================================

/** Given a character's inventory, can they still afford one more craft of this item? */
fun interface MaterialAvailabilityCheck {
    fun hasMaterialsFor(characterId: String, itemId: String): Boolean
}

// =========================================================
// EFFICIENCY TAPER (3-step: full -> reduced -> floor)
// =========================================================

object OfflineEfficiencyCurve {
    // Tuning-level placeholders -- structure (3 steps) is what's locked in.
    private val fullRateWindow: Duration = Duration.ofHours(12)
    private val reducedRateWindow: Duration = Duration.ofHours(72) // cumulative, i.e. up to 72h total
    private const val FULL_RATE_PERCENT = 100.0
    private const val REDUCED_RATE_PERCENT = 50.0
    private const val FLOOR_RATE_PERCENT = 25.0

    /** What efficiency % applies at this point in an offline session (elapsed since going offline). */
    fun efficiencyAt(elapsed: Duration): Double {
        return when {
            elapsed <= fullRateWindow -> FULL_RATE_PERCENT
            elapsed <= reducedRateWindow -> REDUCED_RATE_PERCENT
            else -> FLOOR_RATE_PERCENT
        }
    }

    /**
     * Computes an EFFECTIVE elapsed duration accounting for the taper -- i.e. how much
     * "full-rate-equivalent" time the offline session is worth, blending across steps
     * if the offline period spans multiple efficiency zones.
     */
    fun effectiveElapsed(elapsed: Duration): Duration {
        if (elapsed <= fullRateWindow) return elapsed

        val fullPortion = fullRateWindow
        val reducedPortionEnd = minOf(elapsed, reducedRateWindow)
        val reducedPortion = reducedPortionEnd - fullPortion.toMinutes().let { Duration.ofMinutes(0) } // placeholder, corrected below
        // Rebuilt cleanly using millis to avoid Duration subtraction ambiguity:
        val fullMillis = fullRateWindow.toMillis()
        val reducedEndMillis = minOf(elapsed.toMillis(), reducedRateWindow.toMillis())
        val reducedMillis = (reducedEndMillis - fullMillis).coerceAtLeast(0)
        val floorMillis = (elapsed.toMillis() - reducedRateWindow.toMillis()).coerceAtLeast(0)

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
    // A generous but finite ceiling -- anything beyond this is treated as implausible
    // (clock tampering, corrupted timestamp, etc.) rather than trusted at face value.
    val maxPlausibleElapsed: Duration = Duration.ofDays(30)

    /** Returns the (possibly capped) elapsed duration, plus a flag record if capping occurred. */
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
// =========================================================

sealed class ServiceResult<out T> {
    data class Success<T>(val value: T) : ServiceResult<T>()
    data class Failure(val reason: String) : ServiceResult<Nothing>()
}

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

// =========================================================
// OFFLINE/IDLE SERVICE
// =========================================================

class OfflineIdleService(private val materialCheck: MaterialAvailabilityCheck) {

    private val activeQueues: MutableMap<String, ActiveQueue> = mutableMapOf() // characterId -> their one active queue
    private val lastSeenAt: MutableMap<String, Instant> = mutableMapOf()
    private val flaggedAccounts: MutableList<OfflineFlagRecord> = mutableListOf() // dev-only, same pattern as Economy monitoring

    // ---------------- Starting a queue (enforces "one at a time") ----------------

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
        targetQuantity: Int? // null = indefinite, stops on material depletion
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

    // ---------------- Going offline / coming back ----------------

    fun recordLastSeen(characterId: String, now: Instant = Instant.now()) {
        lastSeenAt[characterId] = now
    }

    /**
     * Call on next login. Server-authoritative: elapsed time is derived ONLY from the
     * stored lastSeenAt timestamp and the current server time -- never a client-supplied value.
     */
    fun resolveOfflineProgress(characterId: String, now: Instant = Instant.now()): ServiceResult<OfflineResolution> {
        val queue = activeQueues[characterId] ?: return ServiceResult.Failure("No active queue to resolve.")
        val lastSeen = lastSeenAt[characterId] ?: return ServiceResult.Failure("No last-seen timestamp recorded.")

        val claimedElapsed = Duration.between(lastSeen, now)
        if (claimedElapsed.isNegative) return ServiceResult.Failure("Invalid elapsed time (negative duration).")

        val (cappedElapsed, flag) = OfflineSanityCheck.validate(characterId, claimedElapsed)
        if (flag != null) flaggedAccounts.add(flag)

        // Offline combat runs 20% slower than the base rate, on top of the normal taper.
        val combatPenaltyMultiplier = if (queue.type == QueueType.OFFLINE_COMBAT) 0.8 else 1.0
        val effectiveElapsed = OfflineEfficiencyCurve.effectiveElapsed(cappedElapsed)
        val penalizedEffectiveMillis = (effectiveElapsed.toMillis() * combatPenaltyMultiplier).toLong()
        val finalEffectiveElapsed = Duration.ofMillis(penalizedEffectiveMillis)

        var actionsCompleted = 0
        var queueExhausted = false

        when (queue) {
            is ActiveQueue.SkillingQueue -> {
                actionsCompleted = (finalEffectiveElapsed.seconds / queue.secondsPerAction).toInt()
                // Indefinite -- no stopping condition besides player action, so never "exhausted" here.
            }
            is ActiveQueue.CraftingQueue -> {
                var possibleActions = (finalEffectiveElapsed.seconds / queue.secondsPerAction).toInt()
                if (queue.targetQuantity != null) {
                    val remaining = queue.targetQuantity - queue.quantityCompleted
                    possibleActions = possibleActions.coerceAtMost(remaining)
                }
                // Material depletion check -- stop early if materials run out, whichever comes first.
                var completed = 0
                for (i in 0 until possibleActions) {
                    if (!materialCheck.hasMaterialsFor(characterId, queue.itemId)) {
                        queueExhausted = true
                        break
                    }
                    completed++
                }
                queue.quantityCompleted += completed
                actionsCompleted = completed
                if (queue.isTargetReached()) queueExhausted = true
            }
            is ActiveQueue.OfflineCombatQueue -> {
                // Actual combat resolution happens via CombatService; this just reports
                // how much effective time was available for it to consume.
                actionsCompleted = 0 // combat doesn't use a flat "actions" count the same way
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

    // ---------------- Queue exhaustion tracking (for a future notification system) ----------------

    /** Estimated time remaining until this queue naturally exhausts (crafting only -- others are indefinite). */
    fun estimatedTimeUntilExhausted(characterId: String): Duration? {
        val queue = activeQueues[characterId] as? ActiveQueue.CraftingQueue ?: return null
        val target = queue.targetQuantity ?: return null // indefinite crafting has no ETA by quantity
        val remaining = target - queue.quantityCompleted
        if (remaining <= 0) return Duration.ZERO
        return Duration.ofSeconds(remaining * queue.secondsPerAction)
    }

    // ---------------- Dev-only monitoring ----------------

    fun allFlaggedAccounts(): List<OfflineFlagRecord> = flaggedAccounts.toList()
}

// =========================================================
// DEMO
// =========================================================

fun main() {
    // Simple material stand-in: character has enough for 20 crafts, then runs dry.
    val materialCounter = mutableMapOf("lyra-character-id" to 20)
    val materialCheck = MaterialAvailabilityCheck { characterId, _ ->
        val remaining = materialCounter[characterId] ?: 0
        if (remaining > 0) {
            materialCounter[characterId] = remaining - 1
            true
        } else {
            false
        }
    }

    val service = OfflineIdleService(materialCheck)
    val characterId = "lyra-character-id"

    println("=== Starting a Mining queue (indefinite skilling) ===")
    printResult(service.startSkillingQueue(characterId, "MINING", "iron_ore", secondsPerAction = 5))

    println("")
    println("=== Attempting to start a second queue while one is active (should fail) ===")
    printResult(service.startCraftingQueue(characterId, "steel_bar", secondsPerAction = 10, targetQuantity = 5))

    println("")
    println("=== Recording last-seen, then resolving after a short simulated offline period (within full-rate window) ===")
    val shortAgo = Instant.now().minus(Duration.ofHours(2))
    service.recordLastSeen(characterId, shortAgo)
    printResult(service.resolveOfflineProgress(characterId))

    println("")
    println("=== Stopping the Mining queue, starting an indefinite Crafting queue (material-limited) ===")
    service.stopQueue(characterId)
    printResult(service.startCraftingQueue(characterId, "steel_bar", secondsPerAction = 5, targetQuantity = null))

    println("")
    println("=== Resolving offline crafting progress after a long simulated absence (spans all 3 taper steps) ===")
    val longAgo = Instant.now().minus(Duration.ofHours(80))
    service.recordLastSeen(characterId, longAgo)
    val craftResult = service.resolveOfflineProgress(characterId)
    printResult(craftResult)
    println("Materials remaining after crafting: " + materialCounter[characterId])

    println("")
    println("=== Attempting to opt into offline combat while a queue is still active (should fail, since exhaustion may not have cleared it) ===")
    printResult(service.optIntoOfflineCombat(characterId, "goblin_camp"))

    println("")
    println("=== Simulating an implausible elapsed time (clock tampering) ===")
    service.stopQueue(characterId)
    service.startSkillingQueue(characterId, "FISHING", "trout", secondsPerAction = 5)
    val implausiblyLongAgo = Instant.now().minus(Duration.ofDays(90))
    service.recordLastSeen(characterId, implausiblyLongAgo)
    val suspiciousResult = service.resolveOfflineProgress(characterId)
    printResult(suspiciousResult)

    println("")
    println("=== Dev-only: checking flagged accounts ===")
    service.allFlaggedAccounts().forEach {
        println("- " + it.characterId + " claimed " + it.claimedElapsed.toDays() + " days, capped to " + it.cappedElapsed.toDays() + " days")
    }
}

fun <T> printResult(result: ServiceResult<T>) {
    when (result) {
        is ServiceResult.Success -> println("[OK] " + result.value)
        is ServiceResult.Failure -> println("[FAIL] " + result.reason)
    }
}
