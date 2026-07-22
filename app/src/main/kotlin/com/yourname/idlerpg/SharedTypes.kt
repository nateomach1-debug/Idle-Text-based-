package com.yourname.idlerpg

import java.time.Instant

// =========================================================
// SHARED RESULT TYPE
// =========================================================

sealed class ServiceResult<out T> {
    data class Success<T>(val value: T) : ServiceResult<T>()
    data class Failure(val reason: String) : ServiceResult<Nothing>()
}

// =========================================================
// SHARED COMBAT STYLE
// =========================================================

enum class CombatStyle { MELEE, RANGED, MAGIC }

// =========================================================
// SHARED EQUIPMENT LOCK CATEGORY
// =========================================================

enum class EquipmentSlot { WEAPON, ARMOR, ACCESSORY, TOOL }

// =========================================================
// SHARED ITEM DEFINITION
// =========================================================

enum class ItemCategory { WEAPON, ARMOR, ACCESSORY, MATERIAL, CONSUMABLE, COSMETIC }
enum class Rarity { COMMON, UNCOMMON, RARE, EPIC, LEGENDARY }
enum class EquipSlot { WEAPON, HELMET, CHESTPLATE, GLOVES, BOOTS, NECKLACE, RING_1, RING_2, TOOL }

object SlotLockMapping {
    fun lockCategoryFor(slot: EquipSlot): EquipmentSlot = when (slot) {
        EquipSlot.WEAPON -> EquipmentSlot.WEAPON
        EquipSlot.HELMET, EquipSlot.CHESTPLATE, EquipSlot.GLOVES, EquipSlot.BOOTS -> EquipmentSlot.ARMOR
        EquipSlot.NECKLACE, EquipSlot.RING_1, EquipSlot.RING_2 -> EquipmentSlot.ACCESSORY
        EquipSlot.TOOL -> EquipmentSlot.TOOL
    }
}

data class ItemStats(
    val attackBonus: Int = 0,
    val strengthBonus: Int = 0,
    val defenseBonus: Int = 0,
    val accuracyBonus: Int = 0,
    val maxHitBonus: Int = 0
) {
    fun isAllZero(): Boolean =
        attackBonus == 0 && strengthBonus == 0 && defenseBonus == 0 && accuracyBonus == 0 && maxHitBonus == 0
}

data class ItemDefinition(
    val id: String,
    val name: String,
    val category: ItemCategory,
    val rarity: Rarity = Rarity.COMMON,
    val isTradeable: Boolean,
    val isStackable: Boolean,
    val isRealMoneyPurchasable: Boolean = false,
    val equipSlot: EquipSlot? = null,
    val combatStyle: CombatStyle? = null,
    val levelRequired: Int = 1,
    val skillRequired: String? = null,
    val stats: ItemStats = ItemStats()
)

// =========================================================
// SHARED ITEM CATALOG
// =========================================================

object ItemCatalog {
    val items = mutableListOf(
        ItemDefinition(
            id = "iron_sword_common",
            name = "Iron Sword",
            category = ItemCategory.WEAPON,
            rarity = Rarity.COMMON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            levelRequired = 10,
            skillRequired = "ATTACK",
            stats = ItemStats(attackBonus = 5, accuracyBonus = 10, maxHitBonus = 6)
        ),
        ItemDefinition(
            id = "iron_sword_rare",
            name = "Iron Sword",
            category = ItemCategory.WEAPON,
            rarity = Rarity.RARE,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            levelRequired = 10,
            skillRequired = "ATTACK",
            stats = ItemStats(attackBonus = 9, accuracyBonus = 16, maxHitBonus = 10)
        ),
        ItemDefinition(
            id = "leather_boots_common",
            name = "Leather Boots",
            category = ItemCategory.ARMOR,
            rarity = Rarity.COMMON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.BOOTS,
            levelRequired = 1,
            stats = ItemStats(defenseBonus = 3)
        ),
        ItemDefinition(
            id = "iron_ore",
            name = "Iron Ore",
            category = ItemCategory.MATERIAL,
            isTradeable = true,
            isStackable = true
        ),
        ItemDefinition(
            id = "steel_bar",
            name = "Steel Bar",
            category = ItemCategory.MATERIAL,
            isTradeable = true,
            isStackable = true
        ),
        ItemDefinition(
            id = "minor_healing_potion",
            name = "Minor Healing Potion",
            category = ItemCategory.CONSUMABLE,
            isTradeable = true,
            isStackable = true
        ),
        ItemDefinition(
            id = "smiths_hammer",
            name = "Smith's Hammer",
            category = ItemCategory.WEAPON,
            rarity = Rarity.UNCOMMON,
            isTradeable = false,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            levelRequired = 1,
            stats = ItemStats(attackBonus = 2, maxHitBonus = 2)
        )
    )

    fun find(itemId: String): ItemDefinition? = items.find { it.id == itemId }
    fun findByNameAndRarity(name: String, rarity: Rarity): ItemDefinition? =
        items.find { it.name == name && it.rarity == rarity }

    fun baseValueFor(itemId: String): Long = when (itemId) {
        "iron_ore" -> 10L
        "oak_log" -> 8L
        "steel_bar" -> 45L
        else -> 5L
    }
}

// =========================================================
// GAME STATE & COMBAT TYPES
// =========================================================

enum class SkillType {
    WOODCUTTING,
    MINING,
    FISHING,
    COMBAT,
    ATTACK
}

data class SkillState(
    var level: Int = 1,
    var currentXp: Long = 0L,
    var xpToNextLevel: Long = 100L
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
    val characterId: String = java.util.UUID.randomUUID().toString(),
    val stats: PlayerStats = PlayerStats(),
    val skills: MutableMap<SkillType, SkillState> = SkillType.entries.associateWith { SkillState() }.toMutableMap(),
    val inventory: MutableMap<String, Int> = mutableMapOf(),
    var lastSavedTimestamp: Long = System.currentTimeMillis()
)

// =========================================================
// REPOSITORY EXPORT TYPES
// =========================================================

data class CharacterExport(
    val id: String,
    val accountId: String,
    val displayName: String,
    val avatarId: String? = null,
    val createdAt: String = Instant.now().toString(),
    val displayNameLastChangedAt: String? = null,
    val isMainCharacter: Boolean = false,
    val gameState: PlayerGameState = PlayerGameState()
)

data class AccountExport(
    val id: String,
    val email: String,
    val username: String,
    val passwordHash: String,
    val createdAt: String = Instant.now().toString(),
    val lastLoginAt: String = Instant.now().toString(),
    val ageBracket: String = "UNKNOWN",
    val region: String = "UNKNOWN",
    val isBanned: Boolean = false,
    val banReason: String? = null,
    val mutedUntil: String? = null,
    val subscriptionTier: String = "FREE",
    val softCurrency: Long = 0L,
    val premiumCurrency: Long = 0L,
    val characters: List<CharacterExport> = emptyList()
)
