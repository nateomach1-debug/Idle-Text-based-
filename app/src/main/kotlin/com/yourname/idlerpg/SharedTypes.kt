package com.yourname.idlerpg

import java.util.UUID

// ==========================================
// 1. Generic Result & Service Wrapper Types
// ==========================================

sealed class ServiceResult<out T> {
    data class Success<out T>(val data: T) : ServiceResult<T>()
    data class Error(val message: String, val cause: Throwable? = null) : ServiceResult<Nothing>()
}

// Convenient aliases expected across system classes
typealias Failure = ServiceResult.Error

// ==========================================
// 2. Equipment, Items & Catalog Definitions
// ==========================================

enum class EquipSlot {
    HEAD,
    CHEST,
    LEGS,
    FEET,
    MAIN_HAND,
    OFF_HAND,
    RING,
    AMULET
}

enum class ItemCategory {
    WEAPON,
    ARMOR,
    CONSUMABLE,
    MATERIAL,
    CURRENCY
}

data class ItemStats(
    val attackBonus: Int = 0,
    val defenseBonus: Int = 0,
    val hpBonus: Int = 0
)

data class ItemDefinition(
    val id: String,
    val name: String,
    val description: String = "",
    val category: ItemCategory = ItemCategory.MATERIAL,
    val equipSlot: EquipSlot? = null,
    val stats: ItemStats = ItemStats(),
    val isStackable: Boolean = true,
    val levelRequired: Int = 1,
    val skillRequired: SkillType? = null
)

object ItemCatalog {
    val items = mutableMapOf<String, ItemDefinition>()
    fun getItem(id: String): ItemDefinition? = items[id]
}

object SlotLockMapping {
    val lockedSlots = mutableMapOf<EquipSlot, Boolean>()
}

// ==========================================
// 3. Core Game Loop, Player & Skill Types
// ==========================================

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
