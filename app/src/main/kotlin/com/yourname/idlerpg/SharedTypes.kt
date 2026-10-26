package com.yourname.idlerpg

sealed class ServiceResult<out T> {
    data class Success<T>(val value: T) : ServiceResult<T>()
    data class Failure(val reason: String) : ServiceResult<Nothing>()
}

enum class CombatStyle { MELEE, RANGED, MAGIC }

enum class EquipmentSlot { WEAPON, ARMOR, ACCESSORY, TOOL }

enum class ItemCategory { WEAPON, ARMOR, ACCESSORY, MATERIAL, CONSUMABLE, COSMETIC }
enum class Rarity { COMMON, UNCOMMON, RARE, EPIC, LEGENDARY }
enum class EquipSlot { WEAPON, HELMET, CHESTPLATE, GLOVES, BOOTS, NECKLACE, RING_1, RING_2, TOOL, LEGS, SHIELD, CAPE, AMMO }

object SlotLockMapping {
    fun lockCategoryFor(slot: EquipSlot): EquipmentSlot = when (slot) {
        EquipSlot.WEAPON, EquipSlot.AMMO -> EquipmentSlot.WEAPON
        EquipSlot.HELMET, EquipSlot.CHESTPLATE, EquipSlot.GLOVES, EquipSlot.BOOTS,
        EquipSlot.LEGS, EquipSlot.SHIELD, EquipSlot.CAPE -> EquipmentSlot.ARMOR
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

enum class ConsumableType { FOOD, POTION }

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
    val elementalType: DamageType? = null,
    val levelRequired: Int = 1,
    val skillRequired: String? = null,
    val stats: ItemStats = ItemStats(),
    val consumableType: ConsumableType? = null,
    val healAmount: Int? = null,
    val buffDurationSeconds: Int? = null
)

object ItemCatalog {
    val items = mutableListOf(
        ItemDefinition(
            id = "iron_sword_common", name = "Iron Sword", category = ItemCategory.WEAPON,
            rarity = Rarity.COMMON, isTradeable = true, isStackable = false,
            equipSlot = EquipSlot.WEAPON, combatStyle = CombatStyle.MELEE,
            levelRequired = 10, skillRequired = "ATTACK",
            stats = ItemStats(attackBonus = 5, accuracyBonus = 10, maxHitBonus = 6)
        ),
        ItemDefinition(
            id = "iron_sword_rare", name = "Iron Sword", category = ItemCategory.WEAPON,
            rarity = Rarity.RARE, isTradeable = true, isStackable = false,
            equipSlot = EquipSlot.WEAPON, combatStyle = CombatStyle.MELEE,
            levelRequired = 10, skillRequired = "ATTACK",
            stats = ItemStats(attackBonus = 9, accuracyBonus = 16, maxHitBonus = 10)
        ),
        ItemDefinition(
            id = "leather_boots_common", name = "Leather Boots", category = ItemCategory.ARMOR,
            rarity = Rarity.COMMON, isTradeable = true, isStackable = false,
            equipSlot = EquipSlot.BOOTS, levelRequired = 1,
            stats = ItemStats(defenseBonus = 3)
        ),
        ItemDefinition(
            id = "minor_healing_potion", name = "Minor Healing Potion", category = ItemCategory.CONSUMABLE,
            isTradeable = true, isStackable = true,
            consumableType = ConsumableType.POTION, healAmount = 20
        ),
        ItemDefinition(
            id = "smiths_hammer", name = "Smith's Hammer", category = ItemCategory.WEAPON,
            rarity = Rarity.UNCOMMON, isTradeable = false, isStackable = false,
            equipSlot = EquipSlot.WEAPON, combatStyle = CombatStyle.MELEE, levelRequired = 1,
            stats = ItemStats(attackBonus = 2, maxHitBonus = 2)
        ),
        ItemDefinition(
            id = "mining_cape", name = "Mining Cape", category = ItemCategory.ARMOR,
            rarity = Rarity.LEGENDARY, isTradeable = false, isStackable = false,
            equipSlot = EquipSlot.CAPE, levelRequired = 99, skillRequired = "MINING"
        ),
        ItemDefinition(
            id = "woodcutting_cape", name = "Woodcutting Cape", category = ItemCategory.ARMOR,
            rarity = Rarity.LEGENDARY, isTradeable = false, isStackable = false,
            equipSlot = EquipSlot.CAPE, levelRequired = 99, skillRequired = "WOODCUTTING"
        ),
        ItemDefinition(
            id = "fishing_cape", name = "Fishing Cape", category = ItemCategory.ARMOR,
            rarity = Rarity.LEGENDARY, isTradeable = false, isStackable = false,
            equipSlot = EquipSlot.CAPE, levelRequired = 99, skillRequired = "FISHING"
        ),
        ItemDefinition(
            id = "farming_cape", name = "Farming Cape", category = ItemCategory.ARMOR,
            rarity = Rarity.LEGENDARY, isTradeable = false, isStackable = false,
            equipSlot = EquipSlot.CAPE, levelRequired = 99, skillRequired = "FARMING"
        ),
        ItemDefinition(
            id = "thieving_cape", name = "Thieving Cape", category = ItemCategory.ARMOR,
            rarity = Rarity.LEGENDARY, isTradeable = false, isStackable = false,
            equipSlot = EquipSlot.CAPE, levelRequired = 99, skillRequired = "THIEVING"
        ),
        ItemDefinition(
            id = "smithing_cape", name = "Smithing Cape", category = ItemCategory.ARMOR,
            rarity = Rarity.LEGENDARY, isTradeable = false, isStackable = false,
            equipSlot = EquipSlot.CAPE, levelRequired = 99, skillRequired = "SMITHING"
        ),
        ItemDefinition(
            id = "cooking_cape", name = "Cooking Cape", category = ItemCategory.ARMOR,
            rarity = Rarity.LEGENDARY, isTradeable = false, isStackable = false,
            equipSlot = EquipSlot.CAPE, levelRequired = 99, skillRequired = "COOKING"
        ),
        ItemDefinition(
            id = "crafting_cape", name = "Crafting Cape", category = ItemCategory.ARMOR,
            rarity = Rarity.LEGENDARY, isTradeable = false, isStackable = false,
            equipSlot = EquipSlot.CAPE, levelRequired = 99, skillRequired = "CRAFTING"
        ),
        ItemDefinition(
            id = "fletching_cape", name = "Fletching Cape", category = ItemCategory.ARMOR,
            rarity = Rarity.LEGENDARY, isTradeable = false, isStackable = false,
            equipSlot = EquipSlot.CAPE, levelRequired = 99, skillRequired = "FLETCHING"
        ),
        ItemDefinition(
            id = "alchemy_cape", name = "Alchemy Cape", category = ItemCategory.ARMOR,
            rarity = Rarity.LEGENDARY, isTradeable = false, isStackable = false,
            equipSlot = EquipSlot.CAPE, levelRequired = 99, skillRequired = "ALCHEMY"
        ),
        ItemDefinition(
            id = "magic_cape", name = "Magic Cape", category = ItemCategory.ARMOR,
            rarity = Rarity.LEGENDARY, isTradeable = false, isStackable = false,
            equipSlot = EquipSlot.CAPE, levelRequired = 99, skillRequired = "MAGIC"
        ),
        ItemDefinition(
            id = "attack_cape", name = "Attack Cape", category = ItemCategory.ARMOR,
            rarity = Rarity.LEGENDARY, isTradeable = false, isStackable = false,
            equipSlot = EquipSlot.CAPE, levelRequired = 99, skillRequired = "ATTACK"
        ),
        ItemDefinition(
            id = "strength_cape", name = "Strength Cape", category = ItemCategory.ARMOR,
            rarity = Rarity.LEGENDARY, isTradeable = false, isStackable = false,
            equipSlot = EquipSlot.CAPE, levelRequired = 99, skillRequired = "STRENGTH"
        ),
        ItemDefinition(
            id = "defense_cape", name = "Defense Cape", category = ItemCategory.ARMOR,
            rarity = Rarity.LEGENDARY, isTradeable = false, isStackable = false,
            equipSlot = EquipSlot.CAPE, levelRequired = 99, skillRequired = "DEFENSE"
        ),
        ItemDefinition(
            id = "prayer_cape", name = "Prayer Cape", category = ItemCategory.ARMOR,
            rarity = Rarity.LEGENDARY, isTradeable = false, isStackable = false,
            equipSlot = EquipSlot.CAPE, levelRequired = 99, skillRequired = "PRAYER"
        ),
        ItemDefinition(
            id = "archery_cape", name = "Archery Cape", category = ItemCategory.ARMOR,
            rarity = Rarity.LEGENDARY, isTradeable = false, isStackable = false,
            equipSlot = EquipSlot.CAPE, levelRequired = 99, skillRequired = "ARCHERY"
        ),
        ItemDefinition(
            id = "premium_membership_token",
            name = "Premium Membership Token",
            category = ItemCategory.CONSUMABLE,
            rarity = Rarity.EPIC,
            isTradeable = true,
            isStackable = true,
            consumableType = ConsumableType.POTION
        )
   ) + GeneratedItemCatalog.definitions + MetalTierItemCatalog.definitions

    fun find(itemId: String): ItemDefinition? = items.find { it.id == itemId }
    fun findByNameAndRarity(name: String, rarity: Rarity): ItemDefinition? =
        items.find { it.name == name && it.rarity == rarity }

    fun baseValueFor(itemId: String): Long = GeneratedItemCatalog.values[itemId] ?: when (itemId) {
        "oak_log" -> 8L
        else -> 5L
    }
}
