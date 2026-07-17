import java.time.Duration
import java.time.Instant
import kotlin.math.floor
import kotlin.math.pow

// =========================================================
// SKILL & GROUP DEFINITIONS
// =========================================================

enum class SkillGroup { GATHERING, PRODUCTION, COMBAT }

enum class SkillType(val group: SkillGroup) {
    MINING(SkillGroup.GATHERING),
    WOODCUTTING(SkillGroup.GATHERING),
    FISHING(SkillGroup.GATHERING),
    FARMING(SkillGroup.GATHERING),
    THIEVING(SkillGroup.GATHERING),

    SMITHING(SkillGroup.PRODUCTION),
    COOKING(SkillGroup.PRODUCTION),
    CRAFTING(SkillGroup.PRODUCTION),
    FLETCHING(SkillGroup.PRODUCTION),
    ALCHEMY(SkillGroup.PRODUCTION),

    ATTACK(SkillGroup.COMBAT),
    STRENGTH(SkillGroup.COMBAT),
    DEFENSE(SkillGroup.COMBAT),
    PRAYER(SkillGroup.COMBAT),
    MAGIC(SkillGroup.COMBAT)
}

data class Skill(
    val type: SkillType,
    var xp: Long = 0
)

class SkillBook {
    private val skills: MutableMap<SkillType, Skill> = SkillType.values()
        .associateWith { Skill(it) }
        .toMutableMap()

    fun get(type: SkillType): Skill = skills.getValue(type)

    fun all(): List<Skill> = skills.values.toList()

    fun inGroup(group: SkillGroup): List<Skill> = skills.values.filter { it.type.group == group }
}

// =========================================================
// XP CURVE
// =========================================================

/**
 * Level is always derived from XP, never stored. 99 is a SOFT cap --
 * a milestone marker for UI/unlock purposes only. The formula keeps
 * producing valid results indefinitely past 99; there is no hard ceiling.
 */
object LevelCurve {
    private const val BASE = 100.0
    private const val EXPONENT = 2.1
    const val SOFT_CAP_LEVEL = 99

    fun xpRequiredForLevel(level: Int): Long {
        if (level <= 1) return 0
        return floor(BASE * (level - 1).toDouble().pow(EXPONENT)).toLong()
    }

    /** No upper bound -- keeps climbing past the soft cap indefinitely. */
    fun levelForXp(xp: Long): Int {
        var level = 1
        while (xpRequiredForLevel(level + 1) <= xp) {
            level++
        }
        return level
    }

    fun xpToNextLevel(xp: Long): Long {
        val currentLevel = levelForXp(xp)
        return xpRequiredForLevel(currentLevel + 1) - xp
    }
}

// =========================================================
// SHARED EFFECT SYSTEM
// (Used by skill unlocks now; reused as-is by Potions and Items later --
//  anything that "grants effects" produces a List<Effect> in this same shape.)
// =========================================================

/**
 * A single effect target: either one specific skill, or an entire group
 * (e.g. "all Combat skills"). Kept generic so effects don't need separate
 * single-skill vs. group-skill variants.
 */
sealed class EffectScope {
    data class SingleSkill(val skill: SkillType) : EffectScope()
    data class Group(val group: SkillGroup) : EffectScope()
}

sealed class Effect {
    data class XpBoost(val scope: EffectScope, val percent: Double) : Effect()
    data class DropRateBoost(val scope: EffectScope, val percent: Double) : Effect()
    data class CostDiscount(val scope: EffectScope, val percent: Double) : Effect()
    data class AccessUnlock(val description: String) : Effect()
    data class FlatStatBonus(val statName: String, val amount: Int) : Effect()
    data class TimerReduction(val scope: EffectScope, val percent: Double) : Effect()
}

/**
 * Combines a list of active effects (from unlocks, potions, items --
 * doesn't matter which) into single additive totals per skill, for the
 * numeric effect types. AccessUnlock and FlatStatBonus aren't "stacked"
 * numerically -- they're collected as-is since they aren't percentages.
 */
object EffectStacker {

    private fun appliesTo(scope: EffectScope, skill: SkillType): Boolean = when (scope) {
        is EffectScope.SingleSkill -> scope.skill == skill
        is EffectScope.Group -> scope.group == skill.group
    }

    fun totalXpBoostPercent(effects: List<Effect>, skill: SkillType): Double =
        effects.filterIsInstance<Effect.XpBoost>()
            .filter { appliesTo(it.scope, skill) }
            .sumOf { it.percent }

    fun totalDropRateBoostPercent(effects: List<Effect>, skill: SkillType): Double =
        effects.filterIsInstance<Effect.DropRateBoost>()
            .filter { appliesTo(it.scope, skill) }
            .sumOf { it.percent }

    fun totalCostDiscountPercent(effects: List<Effect>, skill: SkillType): Double =
        effects.filterIsInstance<Effect.CostDiscount>()
            .filter { appliesTo(it.scope, skill) }
            .sumOf { it.percent }

    fun totalTimerReductionPercent(effects: List<Effect>, skill: SkillType): Double =
        effects.filterIsInstance<Effect.TimerReduction>()
            .filter { appliesTo(it.scope, skill) }
            .sumOf { it.percent }

    fun allAccessUnlocks(effects: List<Effect>): List<Effect.AccessUnlock> =
        effects.filterIsInstance<Effect.AccessUnlock>()

    fun allFlatStatBonuses(effects: List<Effect>): List<Effect.FlatStatBonus> =
        effects.filterIsInstance<Effect.FlatStatBonus>()
}

// =========================================================
// SKILL UNLOCKS (single-skill-triggered, per confirmed design)
// =========================================================

data class SkillUnlock(
    val skill: SkillType,
    val levelRequired: Int,
    val grantedEffects: List<Effect>
)

object UnlockTable {
    private val unlocks = listOf(
        SkillUnlock(
            skill = SkillType.MINING,
            levelRequired = 10,
            grantedEffects = listOf(Effect.AccessUnlock("Iron Ore node"))
        ),
        SkillUnlock(
            skill = SkillType.MINING,
            levelRequired = 25,
            grantedEffects = listOf(
                Effect.AccessUnlock("Mithril Ore node"),
                Effect.CostDiscount(EffectScope.SingleSkill(SkillType.SMITHING), percent = 10.0)
            )
        ),
        SkillUnlock(
            skill = SkillType.ATTACK,
            levelRequired = 30,
            grantedEffects = listOf(
                Effect.FlatStatBonus("meleeAccuracy", amount = 5),
                Effect.AccessUnlock("Warrior's Guild access")
            )
        ),
        SkillUnlock(
            skill = SkillType.MAGIC,
            levelRequired = 40,
            grantedEffects = listOf(
                Effect.TimerReduction(EffectScope.Group(SkillGroup.PRODUCTION), percent = 5.0),
                Effect.AccessUnlock("Teleportation spell")
            )
        )
    )

    fun unlocksEarnedAt(skill: SkillType, level: Int): List<SkillUnlock> =
        unlocks.filter { it.skill == skill && it.levelRequired <= level }

    fun newlyEarnedUnlocks(skill: SkillType, levelBefore: Int, levelAfter: Int): List<SkillUnlock> =
        unlocks.filter { it.skill == skill && it.levelRequired in (levelBefore + 1)..levelAfter }

    /** All effects a character currently has active from every unlock they've earned, across all skills. */
    fun allActiveEffects(skillBook: SkillBook): List<Effect> =
        skillBook.all().flatMap { skill ->
            val level = LevelCurve.levelForXp(skill.xp)
            unlocksEarnedAt(skill.type, level).flatMap { it.grantedEffects }
        }
}

// =========================================================
// RESULT TYPES
// =========================================================

data class XpGrantResult(
    val skillType: SkillType,
    val xpGained: Long,
    val newTotalXp: Long,
    val levelBefore: Int,
    val levelAfter: Int
) {
    val didLevelUp: Boolean get() = levelAfter > levelBefore
    val levelsGained: Int get() = levelAfter - levelBefore
}

sealed class ServiceResult<out T> {
    data class Success<T>(val value: T) : ServiceResult<T>()
    data class Failure(val reason: String) : ServiceResult<Nothing>()
}

// =========================================================
// RESET COOLDOWN TRACKING (per character)
// =========================================================

class CharacterResetState {
    var lastSingleSkillResetAt: Instant? = null // shared across ALL skills for this character
    var lastFullCharacterResetAt: Instant? = null
}

// =========================================================
// SERVICE LAYER
// =========================================================

class ProgressionService {
    private val skillBooks: MutableMap<String, SkillBook> = mutableMapOf()
    private val resetStates: MutableMap<String, CharacterResetState> = mutableMapOf()

    private val singleSkillResetCooldown: Duration = Duration.ofHours(24)
    private val fullCharacterResetCooldown: Duration = Duration.ofDays(30)

    fun skillBookFor(characterId: String): SkillBook =
        skillBooks.getOrPut(characterId) { SkillBook() }

    private fun resetStateFor(characterId: String): CharacterResetState =
        resetStates.getOrPut(characterId) { CharacterResetState() }

    fun grantXp(
        characterId: String,
        skillType: SkillType,
        baseXp: Long,
        extraEffects: List<Effect> = emptyList() // e.g. an active potion buff, passed in by whatever calls this
    ): ServiceResult<XpGrantResult> {
        if (baseXp < 0) {
            return ServiceResult.Failure("XP amount cannot be negative.")
        }

        val book = skillBookFor(characterId)
        val skill = book.get(skillType)
        val levelBefore = LevelCurve.levelForXp(skill.xp)

        val activeEffects = UnlockTable.allActiveEffects(book) + extraEffects
        val boostPercent = EffectStacker.totalXpBoostPercent(activeEffects, skillType)
        val multiplier = 1.0 + (boostPercent / 100.0)

        val xpGained = floor(baseXp * multiplier).toLong()
        skill.xp += xpGained
        val levelAfter = LevelCurve.levelForXp(skill.xp)

        return ServiceResult.Success(
            XpGrantResult(
                skillType = skillType,
                xpGained = xpGained,
                newTotalXp = skill.xp,
                levelBefore = levelBefore,
                levelAfter = levelAfter
            )
        )
    }

    fun resetSkill(characterId: String, skillType: SkillType, now: Instant = Instant.now()): ServiceResult<Skill> {
        val state = resetStateFor(characterId)
        val lastReset = state.lastSingleSkillResetAt
        if (lastReset != null) {
            val elapsed = Duration.between(lastReset, now)
            if (elapsed < singleSkillResetCooldown) {
                val hoursRemaining = (singleSkillResetCooldown - elapsed).toHours() + 1
                return ServiceResult.Failure(
                    "Skill reset is on cooldown. Try again in " + hoursRemaining + " hour(s)."
                )
            }
        }

        val skill = skillBookFor(characterId).get(skillType)
        skill.xp = 0
        state.lastSingleSkillResetAt = now
        return ServiceResult.Success(skill)
    }

    fun resetCharacter(characterId: String, now: Instant = Instant.now()): ServiceResult<SkillBook> {
        val state = resetStateFor(characterId)
        val lastReset = state.lastFullCharacterResetAt
        if (lastReset != null) {
            val elapsed = Duration.between(lastReset, now)
            if (elapsed < fullCharacterResetCooldown) {
                val daysRemaining = (fullCharacterResetCooldown - elapsed).toDays() + 1
                return ServiceResult.Failure(
                    "Full character reset is on cooldown. Try again in " + daysRemaining + " day(s)."
                )
            }
        }

        val book = skillBookFor(characterId)
        book.all().forEach { it.xp = 0 }
        state.lastFullCharacterResetAt = now
        return ServiceResult.Success(book)
    }
}

// =========================================================
// DEMO
// =========================================================

fun main() {
    val progression = ProgressionService()
    val characterId = "lyra-character-id"

    println("=== Starting state ===")
    printSkillSummary(progression, characterId, SkillType.MINING)

    println("")
    println("=== Granting XP to reach Mining level 25 (unlocks a Smithing discount) ===")
    val bigGrant = progression.grantXp(characterId, SkillType.MINING, baseXp = 20000)
    printGrantResult(bigGrant)

    println("")
    println("=== Checking active effects across the whole skill book now ===")
    val book = progression.skillBookFor(characterId)
    val effects = UnlockTable.allActiveEffects(book)
    effects.forEach { println("- " + it) }

    println("")
    println("=== Granting Smithing XP -- should reflect no direct XP boost (discount != XP boost) ===")
    printGrantResult(progression.grantXp(characterId, SkillType.SMITHING, baseXp = 100))

    println("")
    println("=== Granting Mining XP again -- no further boost active, gain should equal base ===")
    printGrantResult(progression.grantXp(characterId, SkillType.MINING, baseXp = 100))

    println("")
    println("=== Attempting single-skill reset on Mining ===")
    printResetResult(progression.resetSkill(characterId, SkillType.MINING))

    println("")
    println("=== Attempting single-skill reset on a DIFFERENT skill immediately after (should fail: shared cooldown) ===")
    printResetResult(progression.resetSkill(characterId, SkillType.FISHING))

    println("")
    println("=== Attempting single-skill reset again after simulating 25 hours ===")
    val future25h = Instant.now().plus(Duration.ofHours(25))
    printResetResult(progression.resetSkill(characterId, SkillType.FISHING, now = future25h))

    println("")
    println("=== Attempting full character reset (should succeed, independent cooldown) ===")
    when (val result = progression.resetCharacter(characterId)) {
        is ServiceResult.Success -> println("[OK] Character fully reset. Mining XP now: " + result.value.get(SkillType.MINING).xp)
        is ServiceResult.Failure -> println("[FAIL] " + result.reason)
    }

    println("")
    println("=== Attempting full character reset again immediately (should fail: 30-day cooldown) ===")
    when (val result = progression.resetCharacter(characterId)) {
        is ServiceResult.Success -> println("[OK] Character fully reset.")
        is ServiceResult.Failure -> println("[FAIL] " + result.reason)
    }
}

fun printSkillSummary(progression: ProgressionService, characterId: String, skillType: SkillType) {
    val skill = progression.skillBookFor(characterId).get(skillType)
    val level = LevelCurve.levelForXp(skill.xp)
    val toNext = LevelCurve.xpToNextLevel(skill.xp)
    println(skillType.name + " -> Level " + level + ", XP " + skill.xp + ", XP to next level: " + toNext)
}

fun printGrantResult(result: ServiceResult<XpGrantResult>) {
    when (result) {
        is ServiceResult.Success -> {
            val r = result.value
            var line = "[OK] Granted " + r.xpGained + " XP to " + r.skillType.name + " (total: " + r.newTotalXp + ")"
            if (r.didLevelUp) {
                line += " -- LEVEL UP! " + r.levelBefore + " -> " + r.levelAfter + " (+" + r.levelsGained + ")"
            }
            println(line)
        }
        is ServiceResult.Failure -> println("[FAIL] " + result.reason)
    }
}

fun printResetResult(result: ServiceResult<Skill>) {
    when (result) {
        is ServiceResult.Success -> println("[OK] Reset " + result.value.type.name + " to 0 XP.")
        is ServiceResult.Failure -> println("[FAIL] " + result.reason)
    }
}
