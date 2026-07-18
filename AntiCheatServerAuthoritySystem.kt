import java.time.Duration
import java.time.Instant
import java.util.UUID

// =========================================================
// UNIFIED FLAG REGISTRY
// (Single shared destination for suspicious-activity flags from
//  ANY module -- anti-cheat rate limiting, Economy's collusion
//  tagging, Offline's sanity-check cap, anything else later.)
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

    // ---------------- Dev-only queries ----------------

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

/**
 * Pulls the legitimate minimum interval from whatever the relevant module
 * already defines -- never a separate hardcoded number disconnected from
 * the actual game data. In the combined project, these would call directly
 * into Combat System's Weapon/Spell speed and the Items module's Recipe.
 */
object MinimumIntervalResolver {
    // Stand-ins mirroring the real lookups until all modules are combined --
    // same shape as what Combat/Items already define.
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
// =========================================================

class ActionTimingState(
    var lastActionAt: Instant? = null,
    var violationsSinceLastFlag: Int = 0
)

data class ActionResolution(
    val group: ActionGroup,
    val actionKey: String,
    val requestedAt: Instant,
    val correctedAt: Instant,      // what the action is actually timed/credited as
    val wasCorrected: Boolean,
    val flagRaisedThisTime: Boolean
)

class RateLimitService(private val flagRegistry: FlagRegistry) {
    // key: characterId + group -> timing state
    private val states: MutableMap<String, ActionTimingState> = mutableMapOf()
    private val flagSuppressionWindow = 20

    private fun key(characterId: String, group: ActionGroup) = characterId + ":" + group.name

    /**
     * Call every time an action of this type is attempted. Returns the
     * CORRECTED timestamp the action should actually be credited against --
     * never a rejection, always clamped to the legitimate minimum interval.
     *
     * Flagging behavior: flags immediately on the FIRST violation in a streak,
     * then stays quiet for the next 20 violations before flagging again.
     * Any legitimately-paced action resets the suppression window entirely.
     */
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
                // Clamp: the action is credited as if it happened at the earliest legitimate moment.
                correctedAt = lastAction.plus(minInterval)
                wasCorrected = true

                if (state.violationsSinceLastFlag == 0) {
                    // In extreme spam scenarios, the corrected/throttled timeline can advance
                    // faster than the attacker's own requested timeline, which would otherwise
                    // log a confusing negative interval. Clamp for display and call it out plainly.
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
                    state.violationsSinceLastFlag = 0 // next violation after this will flag again
                }
            } else {
                state.violationsSinceLastFlag = 0 // legitimate timing resets the suppression window
            }
        }

        state.lastActionAt = correctedAt
        return ActionResolution(group, actionKey, requestedAt, correctedAt, wasCorrected, flagRaisedThisTime)
    }
}

// =========================================================
// RESULT TYPE
// =========================================================

sealed class ServiceResult<out T> {
    data class Success<T>(val value: T) : ServiceResult<T>()
    data class Failure(val reason: String) : ServiceResult<Nothing>()
}

// =========================================================
// DEMO
// =========================================================

fun main() {
    val flagRegistry = FlagRegistry()
    val rateLimiter = RateLimitService(flagRegistry)
    val characterId = "lyra-character-id"

    println("=== Legitimate-speed combat actions (respecting the 2.4s minimum) ===")
    var t = Instant.now()
    repeat(3) { i ->
        val resolution = rateLimiter.resolveAction(characterId, ActionGroup.COMBAT, "bronze_sword", t)
        println("Action " + (i + 1) + ": corrected=" + resolution.wasCorrected + " flagged=" + resolution.flagRaisedThisTime)
        t = t.plusMillis(2400)
    }

    println("")
    println("=== Simulating a bot: 25 rapid-fire combat actions, far faster than the 2.4s minimum ===")
    var fastTime = t
    var flaggedCount = 0
    repeat(25) { i ->
        val resolution = rateLimiter.resolveAction(characterId, ActionGroup.COMBAT, "bronze_sword", fastTime)
        if (resolution.flagRaisedThisTime) {
            flaggedCount++
            println("Violation flagged at loop index " + (i + 1))
        }
        fastTime = fastTime.plusMillis(100) // way faster than legitimate
    }
    println("Total flags raised during this burst: " + flaggedCount + " (expected 2 -- one on the first violation, one 20 violations later)")

    println("")
    println("=== Checking the corrected timestamp actually reflects the legitimate pace, not the spammed pace ===")
    val firstFastAction = rateLimiter.resolveAction(characterId, ActionGroup.COMBAT, "bronze_sword", fastTime)
    println("Requested at: " + firstFastAction.requestedAt)
    println("Corrected/credited at: " + firstFastAction.correctedAt + " (should be later than requested)")

    println("")
    println("=== Crafting and Gathering pull their own independent minimums, unaffected by Combat's violation streak ===")
    val craftResolution = rateLimiter.resolveAction(characterId, ActionGroup.CRAFTING, "steel_bar")
    val gatherResolution = rateLimiter.resolveAction(characterId, ActionGroup.GATHERING, "iron_ore")
    println("First Crafting action: corrected=" + craftResolution.wasCorrected + " (should be false -- no prior action to compare against yet)")
    println("First Gathering action: corrected=" + gatherResolution.wasCorrected + " (should be false)")

    println("")
    println("=== Dev-only: reviewing pending flags across ALL sources (unified registry) ===")
    flagRegistry.raise("bob", FlagSource.ECONOMY_COLLUSION, "Suspicious repeated below-market trades with the same account.")
    flagRegistry.raise("carol", FlagSource.OFFLINE_TIME_ANOMALY, "Claimed 90 days offline, capped to 30.")
    flagRegistry.pending().forEach {
        println("- [" + it.source + "] " + it.characterId + ": " + it.details)
    }

    println("")
    println("=== Resolving one flag ===")
    val someFlag = flagRegistry.pending().first()
    printResult(flagRegistry.resolve(someFlag.id, actionTaken = true))
    println("Remaining pending flags: " + flagRegistry.pending().size)
}

fun <T> printResult(result: ServiceResult<T>) {
    when (result) {
        is ServiceResult.Success -> println("[OK] " + result.value)
        is ServiceResult.Failure -> println("[FAIL] " + result.reason)
    }
}
