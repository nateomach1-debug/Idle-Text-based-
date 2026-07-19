package com.yourname.idlerpg

import java.time.Duration
import java.time.Instant
import java.util.UUID

// =========================================================
// UNIFIED FLAG REGISTRY
// =========================================================

enum class FlagSource { RATE_LIMIT_VIOLATION, ECONOMY_COLLUSION, OFFLINE_TIME_ANOMALY, OTHER }
enum class FlagReviewStatus { PENDING, REVIEWED_ACTION_TAKEN, REVIEWED_NO_ACTION }

data class SuspicionFlag(
    val id: String = UUID.randomUUID().toString(),
    val characterId: String,
    val source: FlagSource,
    val details: String,
    val createdAt: Instant = Instant.now(),
    var status: FlagReviewStatus = FlagReviewStatus.PENDING
)

class FlagRegistry {
    private val flags: MutableList<SuspicionFlag> = mutableListOf()

    fun raise(characterId: String, source: FlagSource, details: String): SuspicionFlag {
        val flag = SuspicionFlag(characterId = characterId, source = source, details = details)
        flags.add(flag)
        return flag
    }

    fun pending(): List<SuspicionFlag> = flags.filter { it.status == FlagReviewStatus.PENDING }
    fun allForCharacter(characterId: String): List<SuspicionFlag> = flags.filter { it.characterId == characterId }
    fun allBySource(source: FlagSource): List<SuspicionFlag> = flags.filter { it.source == source }

    fun resolve(flagId: String, actionTaken: Boolean): ServiceResult<SuspicionFlag> {
        val flag = flags.find { it.id == flagId } ?: return ServiceResult.Failure("Flag not found.")
        flag.status = if (actionTaken) FlagReviewStatus.REVIEWED_ACTION_TAKEN else FlagReviewStatus.REVIEWED_NO_ACTION
        return ServiceResult.Success(flag)
    }
}

// =========================================================
// ACTION GROUPS & MINIMUM INTERVAL SOURCING
// =========================================================

enum class ActionGroup { COMBAT, CRAFTING, GATHERING }

object MinimumIntervalResolver {
    // These stand-ins can now be replaced with real lookups into
    // Combat System's Weapon/Spell speed and Items & Equipment's
    // Recipe.levelRequired-based timing, once wired together directly.
    private val combatSpeeds = mapOf(
        "bronze_sword" to 2.4,
        "spark_bolt" to 2.4,
        "flame_lance" to 2.8,
        "frost_spike" to 3.0
    )
    private val craftingSpeeds = mapOf(
        "steel_bar" to 5.0,
        "iron_sword_common" to 8.0
    )
    private val gatheringSpeeds = mapOf(
        "iron_ore" to 3.0,
        "oak_log" to 3.0,
        "trout" to 4.0
    )

    fun minimumIntervalSeconds(group: ActionGroup, actionKey: String): Double = when (group) {
        ActionGroup.COMBAT -> combatSpeeds[actionKey] ?: 2.4
        ActionGroup.CRAFTING -> craftingSpeeds[actionKey] ?: 5.0
        ActionGroup.GATHERING -> gatheringSpeeds[actionKey] ?: 3.0
    }
}

// =========================================================
// RATE LIMITER
// (ServiceResult now comes from SharedTypes.kt.)
// =========================================================

class ActionTimingState(
    var lastActionAt: Instant? = null,
    var violationsSinceLastFlag: Int = 0
)

data class ActionResolution(
    val group: ActionGroup,
    val actionKey: String,
    val requestedAt: Instant,
    val correctedAt: Instant,
    val wasCorrected: Boolean,
    val flagRaisedThisTime: Boolean
)

class RateLimitService(private val flagRegistry: FlagRegistry) {
    private val states: MutableMap<String, ActionTimingState> = mutableMapOf()
    private val flagSuppressionWindow = 20

    private fun key(characterId: String, group: ActionGroup) = characterId + ":" + group.name

    fun resolveAction(
        characterId: String,
        group: ActionGroup,
        actionKey: String,
        requestedAt: Instant = Instant.now()
    ): ActionResolution {
        val state = states.getOrPut(key(characterId, group)) { ActionTimingState() }
        val minInterval = Duration.ofMillis((MinimumIntervalResolver.minimumIntervalSeconds(group, actionKey) * 1000).toLong())

        val lastAction = state.lastActionAt
        var correctedAt = requestedAt
        var wasCorrected = false
        var flagRaisedThisTime = false

        if (lastAction != null) {
            val actualElapsed = Duration.between(lastAction, requestedAt)
            if (actualElapsed < minInterval) {
                correctedAt = lastAction.plus(minInterval)
                wasCorrected = true

                if (state.violationsSinceLastFlag == 0) {
                    val displayIntervalMillis = actualElapsed.toMillis().coerceAtLeast(0)
                    val extremeSpamNote = if (actualElapsed.isNegative) " [EXTREME SPAM: corrected timeline has outpaced request timeline]" else ""

                    flagRegistry.raise(
                        characterId = characterId,
                        source = FlagSource.RATE_LIMIT_VIOLATION,
                        details = group.name + "/" + actionKey +
                            ": violation detected (requested interval " + displayIntervalMillis +
                            "ms, minimum allowed " + minInterval.toMillis() + "ms)" + extremeSpamNote
                    )
                    flagRaisedThisTime = true
                }

                state.violationsSinceLastFlag += 1
                if (state.violationsSinceLastFlag >= flagSuppressionWindow) {
                    state.violationsSinceLastFlag = 0
                }
            } else {
                state.violationsSinceLastFlag = 0
            }
        }

        state.lastActionAt = correctedAt
        return ActionResolution(group, actionKey, requestedAt, correctedAt, wasCorrected, flagRaisedThisTime)
    }
}
