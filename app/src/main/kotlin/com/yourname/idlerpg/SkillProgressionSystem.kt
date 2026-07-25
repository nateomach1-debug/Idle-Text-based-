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
        ))
    )

    fun unlocksEarnedAt(skill: SkillType, level: Int): List<SkillUnlock> =
        unlocks.filter { it.skill == skill && it.levelRequired <= level }

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
EOF
echo "SkillProgressionSystem Part 1 written"
