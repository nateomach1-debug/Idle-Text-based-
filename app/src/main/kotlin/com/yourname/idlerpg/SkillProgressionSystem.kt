package com.yourname.idlerpg

import java.time.Duration
import java.time.Instant
import kotlin.math.floor
import kotlin.math.pow

enum class SkillGroup { GATHERING, PRODUCTION, COMBAT }

enum class SkillType(val groups: Set<SkillGroup>) {
    MINING(setOf(SkillGroup.GATHERING)),
    WOODCUTTING(setOf(SkillGroup.GATHERING)),
    FISHING(setOf(SkillGroup.GATHERING)),
    FARMING(setOf(SkillGroup.GATHERING)),
    THIEVING(setOf(SkillGroup.GATHERING)),
    SMITHING(setOf(SkillGroup.PRODUCTION)),
    COOKING(setOf(SkillGroup.PRODUCTION)),
    CRAFTING(setOf(SkillGroup.PRODUCTION)),
    FLETCHING(setOf(SkillGroup.PRODUCTION)),
    ALCHEMY(setOf(SkillGroup.PRODUCTION)),
    MAGIC(setOf(SkillGroup.PRODUCTION, SkillGroup.COMBAT)),
    ATTACK(setOf(SkillGroup.COMBAT)),
    STRENGTH(setOf(SkillGroup.COMBAT)),
    DEFENSE(setOf(SkillGroup.COMBAT)),
    PRAYER(setOf(SkillGroup.COMBAT)),
    ARCHERY(setOf(SkillGroup.COMBAT))
}

data class Skill(val type: SkillType, var xp: Long = 0)

class SkillBook {
    private val skills: MutableMap<SkillType, Skill> = SkillType.values()
        .associateWith { Skill(it) }
        .toMutableMap()

    fun get(type: SkillType): Skill = skills.getValue(type)
    fun all(): List<Skill> = skills.values.toList()
    fun inGroup(group: SkillGroup): List<Skill> = skills.values.filter { group in it.type.groups }
}

object LevelCurve {
    private const val BASE = 100.0
    private const val EXPONENT = 2.1
    const val SOFT_CAP_LEVEL = 99

    fun xpRequiredForLevel(level: Int): Long {
        if (level <= 1) return 0
        return floor(BASE * (level - 1).toDouble().pow(EXPONENT)).toLong()
    }

    fun levelForXp(xp: Long): Int {
        var level = 1
        while (xpRequiredForLevel(level + 1) <= xp) { level++ }
        return level
    }

    fun xpToNextLevel(xp: Long): Long {
        val currentLevel = levelForXp(xp)
        return xpRequiredForLevel(currentLevel + 1) - xp
    }
}

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
    data class MaterialSaveChance(val scope: EffectScope, val percent: Double) : Effect()
    data class CraftSuccessBoost(val scope: EffectScope, val percent: Double) : Effect()
}

object EffectStacker {
    private fun appliesTo(scope: EffectScope, skill: SkillType): Boolean = when (scope) {
        is EffectScope.SingleSkill -> scope.skill == skill
        is EffectScope.Group -> scope.group in skill.groups
    }

    fun totalXpBoostPercent(effects: List<Effect>, skill: SkillType): Double =
        effects.filterIsInstance<Effect.XpBoost>().filter { appliesTo(it.scope, skill) }.sumOf { it.percent }

    fun totalDropRateBoostPercent(effects: List<Effect>, skill: SkillType): Double =
        effects.filterIsInstance<Effect.DropRateBoost>().filter { appliesTo(it.scope, skill) }.sumOf { it.percent }

    fun totalCostDiscountPercent(effects: List<Effect>, skill: SkillType): Double =
        effects.filterIsInstance<Effect.CostDiscount>().filter { appliesTo(it.scope, skill) }.sumOf { it.percent }

    fun totalTimerReductionPercent(effects: List<Effect>, skill: SkillType): Double =
        effects.filterIsInstance<Effect.TimerReduction>().filter { appliesTo(it.scope, skill) }.sumOf { it.percent }

    fun totalMaterialSaveChancePercent(effects: List<Effect>, skill: SkillType): Double =
        effects.filterIsInstance<Effect.MaterialSaveChance>().filter { appliesTo(it.scope, skill) }.sumOf { it.percent }

    fun totalCraftSuccessBoostPercent(effects: List<Effect>, skill: SkillType): Double =
        effects.filterIsInstance<Effect.CraftSuccessBoost>().filter { appliesTo(it.scope, skill) }.sumOf { it.percent }

    fun allAccessUnlocks(effects: List<Effect>): List<Effect.AccessUnlock> = effects.filterIsInstance<Effect.AccessUnlock>()
    fun allFlatStatBonuses(effects: List<Effect>): List<Effect.FlatStatBonus> = effects.filterIsInstance<Effect.FlatStatBonus>()
}

data class SkillUnlock(val skill: SkillType, val levelRequired: Int, val grantedEffects: List<Effect>)

object UnlockTable {
    private val unlocks = listOf(
        SkillUnlock(SkillType.MINING, 10, listOf(Effect.AccessUnlock("Iron Ore node"))),
        SkillUnlock(SkillType.MINING, 25, listOf(
            Effect.AccessUnlock("Mithril Ore node"),
            Effect.CostDiscount(EffectScope.SingleSkill(SkillType.SMITHING), 10.0)
        )),
        SkillUnlock(SkillType.ATTACK, 30, listOf(
            Effect.FlatStatBonus("meleeAccuracy", 5),
            Effect.AccessUnlock("Warrior's Guild access")
        )),
        SkillUnlock(SkillType.MAGIC, 40, listOf(
            Effect.TimerReduction(EffectScope.Group(SkillGroup.PRODUCTION), 5.0),
            Effect.AccessUnlock("Teleportation spell")
        )),
        // ---- Mastery perks (level 50, one per skill) ----
        SkillUnlock(SkillType.ATTACK, 50, listOf(
            Effect.AccessUnlock("Combat Mastery: +5% hit chance (melee)"),
            Effect.XpBoost(EffectScope.SingleSkill(SkillType.ATTACK), 5.0)
        )),
        SkillUnlock(SkillType.STRENGTH, 50, listOf(
            Effect.AccessUnlock("Combat Mastery: +5% min/max hit damage (melee)"),
            Effect.XpBoost(EffectScope.SingleSkill(SkillType.STRENGTH), 5.0)
        )),
        SkillUnlock(SkillType.DEFENSE, 50, listOf(
            Effect.AccessUnlock("Combat Mastery: +5% incoming damage reduction"),
            Effect.XpBoost(EffectScope.SingleSkill(SkillType.DEFENSE), 5.0)
        )),
        SkillUnlock(SkillType.ARCHERY, 50, listOf(
            Effect.AccessUnlock("Combat Mastery: +5% hit chance (ranged)"),
            Effect.XpBoost(EffectScope.SingleSkill(SkillType.ARCHERY), 5.0)
        )),
        SkillUnlock(SkillType.MAGIC, 50, listOf(
            Effect.AccessUnlock("Combat Mastery: +5% hit chance (magic)"),
            Effect.XpBoost(EffectScope.SingleSkill(SkillType.MAGIC), 5.0)
        )),
        SkillUnlock(SkillType.PRAYER, 50, listOf(
            Effect.AccessUnlock("Combat Mastery: +5% reduced monster damage while a prayer is active"),
            Effect.XpBoost(EffectScope.SingleSkill(SkillType.PRAYER), 5.0)
        )),
        SkillUnlock(SkillType.MINING, 50, listOf(
            Effect.DropRateBoost(EffectScope.SingleSkill(SkillType.MINING), 10.0),
            Effect.XpBoost(EffectScope.SingleSkill(SkillType.MINING), 5.0)
        )),
        SkillUnlock(SkillType.WOODCUTTING, 50, listOf(
            Effect.DropRateBoost(EffectScope.SingleSkill(SkillType.WOODCUTTING), 10.0),
            Effect.XpBoost(EffectScope.SingleSkill(SkillType.WOODCUTTING), 5.0)
        )),
        SkillUnlock(SkillType.FISHING, 50, listOf(
            Effect.DropRateBoost(EffectScope.SingleSkill(SkillType.FISHING), 10.0),
            Effect.XpBoost(EffectScope.SingleSkill(SkillType.FISHING), 5.0)
        )),
        SkillUnlock(SkillType.FARMING, 50, listOf(
            Effect.DropRateBoost(EffectScope.SingleSkill(SkillType.FARMING), 10.0),
            Effect.XpBoost(EffectScope.SingleSkill(SkillType.FARMING), 5.0)
        )),
        SkillUnlock(SkillType.THIEVING, 50, listOf(
            Effect.DropRateBoost(EffectScope.SingleSkill(SkillType.THIEVING), 10.0),
            Effect.XpBoost(EffectScope.SingleSkill(SkillType.THIEVING), 5.0)
        )),
        SkillUnlock(SkillType.SMITHING, 50, listOf(
            Effect.MaterialSaveChance(EffectScope.SingleSkill(SkillType.SMITHING), 10.0),
            Effect.XpBoost(EffectScope.SingleSkill(SkillType.SMITHING), 5.0)
        )),
        SkillUnlock(SkillType.COOKING, 50, listOf(
            Effect.CraftSuccessBoost(EffectScope.SingleSkill(SkillType.COOKING), 10.0),
            Effect.XpBoost(EffectScope.SingleSkill(SkillType.COOKING), 5.0)
        )),
        SkillUnlock(SkillType.CRAFTING, 50, listOf(
            Effect.MaterialSaveChance(EffectScope.SingleSkill(SkillType.CRAFTING), 10.0),
            Effect.XpBoost(EffectScope.SingleSkill(SkillType.CRAFTING), 5.0)
        )),
        SkillUnlock(SkillType.FLETCHING, 50, listOf(
            Effect.MaterialSaveChance(EffectScope.SingleSkill(SkillType.FLETCHING), 10.0),
            Effect.XpBoost(EffectScope.SingleSkill(SkillType.FLETCHING), 5.0)
        )),
        SkillUnlock(SkillType.ALCHEMY, 50, listOf(
            Effect.MaterialSaveChance(EffectScope.SingleSkill(SkillType.ALCHEMY), 10.0),
            Effect.XpBoost(EffectScope.SingleSkill(SkillType.ALCHEMY), 5.0)
        ))
    )

    fun unlocksEarnedAt(skill: SkillType, level: Int): List<SkillUnlock> =
        unlocks.filter { it.skill == skill && it.levelRequired <= level }

    fun allUnlocksFor(skill: SkillType): List<SkillUnlock> =
        unlocks.filter { it.skill == skill }

    fun newlyEarnedUnlocks(skill: SkillType, levelBefore: Int, levelAfter: Int): List<SkillUnlock> =
        unlocks.filter { it.skill == skill && it.levelRequired in (levelBefore + 1)..levelAfter }

    fun allActiveEffects(skillBook: SkillBook): List<Effect> = skillBook.all().flatMap { skill ->
        val level = LevelCurve.levelForXp(skill.xp)
        unlocksEarnedAt(skill.type, level).flatMap { it.grantedEffects }
    }
}

data class XpGrantResult(
    val skillType: SkillType, val xpGained: Long, val newTotalXp: Long,
    val levelBefore: Int, val levelAfter: Int
) {
    val didLevelUp: Boolean get() = levelAfter > levelBefore
    val levelsGained: Int get() = levelAfter - levelBefore
}

class CharacterResetState {
    var lastSingleSkillResetAt: Instant? = null
    var lastFullCharacterResetAt: Instant? = null
}

data class SkillExport(val characterId: String, val skillId: String, val xp: Long)

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
        extraEffects: List<Effect> = emptyList()
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
            XpGrantResult(skillType, xpGained, skill.xp, levelBefore, levelAfter)
        )
    }

    fun resetSkill(characterId: String, skillType: SkillType, now: Instant = Instant.now()): ServiceResult<Skill> {
        val state = resetStateFor(characterId)
        val lastReset = state.lastSingleSkillResetAt
        if (lastReset != null) {
            val elapsed = Duration.between(lastReset, now)
            if (elapsed < singleSkillResetCooldown) {
                val hoursRemaining = (singleSkillResetCooldown - elapsed).toHours() + 1
                return ServiceResult.Failure("Skill reset is on cooldown. Try again in " + hoursRemaining + " hour(s).")
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
                return ServiceResult.Failure("Full character reset is on cooldown. Try again in " + daysRemaining + " day(s).")
            }
        }

        val book = skillBookFor(characterId)
        book.all().forEach { it.xp = 0 }
        state.lastFullCharacterResetAt = now
        return ServiceResult.Success(book)
    }

    fun exportAllSkills(): List<SkillExport> = skillBooks.flatMap { (characterId, book) ->
        book.all().map { skill -> SkillExport(characterId, skill.type.name, skill.xp) }
    }

    fun restoreSkill(export: SkillExport) {
        val book = skillBookFor(export.characterId)
        val skillType = SkillType.valueOf(export.skillId)
        book.get(skillType).xp = export.xp
    }
}
