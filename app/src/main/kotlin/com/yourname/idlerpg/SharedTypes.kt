package com.yourname.idlerpg

import java.util.UUID

// --- Generic System Wrapper Types ---

sealed class ServiceResult<out T> {
    data class Success<out T>(val data: T) : ServiceResult<T>()
    data class Error(val message: String, val cause: Throwable? = null) : ServiceResult<Nothing>()
}

// --- Core Game Loop Enums & Data Classes ---

enum class SkillType {
    WOODCUTTING,
    MINING,
    ATTACK,
    DEFENSE
}

data class SkillState(
    val level: Int = 1,
    val currentXp: Long = 0L,
    val xpToNextLevel: Long = 100L
)

data class Enemy(
    val id: String,
    val name: String,
    val maxHp: Int,
    var currentHp: Int,
    val attackPower: Int,
    val xpReward: Long,
    val goldReward: Long
)

data class PlayerStats(
    var hp: Int = 100,
    var maxHp: Int = 100,
    var attackPower: Int = 10,
    var gold: Long = 0L,
    var activeSkill: SkillType? = null,
    var activeEnemy: Enemy? = null
)

data class PlayerGameState(
    val characterId: String = UUID.randomUUID().toString(),
    val stats: PlayerStats = PlayerStats(),
    val skills: MutableMap<SkillType, SkillState> = SkillType.values().associateWith { SkillState() }.toMutableMap(),
    val inventory: MutableMap<String, Int> = mutableMapOf(),
    var lastSavedTimestamp: Long = System.currentTimeMillis()
)
