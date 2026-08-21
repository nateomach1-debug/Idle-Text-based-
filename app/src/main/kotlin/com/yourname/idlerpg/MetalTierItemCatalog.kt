package com.yourname.idlerpg

// =========================================================
// METAL TIER ITEM CATALOG
// 105 items generated to fill out full metal x weapon-class
// coverage (Option A: dynamic metal selection at craft time).
// Merge these into ItemCatalog alongside GeneratedItemCatalog.definitions --
// see instructions in the handoff message for the exact merge point.
// =========================================================

object MetalTierItemCatalog {
    val definitions: List<ItemDefinition> = listOf(
        ItemDefinition(
            id = "bronze_arrowheads",
            name = "Bronze Arrowheads",
            category = ItemCategory.MATERIAL,
            isTradeable = true,
            isStackable = true,
        ),
        ItemDefinition(
            id = "bronze_throwing_knives",
            name = "Bronze Throwing Knives",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.RANGED,
            stats = ItemStats(attackBonus = 9, strengthBonus = 0, accuracyBonus = 17, maxHitBonus = 5)
        ),
        ItemDefinition(
            id = "bronze_chainmail_body",
            name = "Bronze Chainmail Body",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.CHESTPLATE,
            stats = ItemStats(defenseBonus = 10)
        ),
        ItemDefinition(
            id = "bronze_full_helm",
            name = "Bronze Full Helm",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.HELMET,
            stats = ItemStats(defenseBonus = 6)
        ),
        ItemDefinition(
            id = "bronze_platelegs",
            name = "Bronze Platelegs",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.LEGS,
            stats = ItemStats(defenseBonus = 9)
        ),
        ItemDefinition(
            id = "bronze_kiteshield",
            name = "Bronze Kiteshield",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.SHIELD,
            stats = ItemStats(defenseBonus = 9)
        ),
        ItemDefinition(
            id = "bronze_battleaxe",
            name = "Bronze Battleaxe",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 9, strengthBonus = 6, accuracyBonus = 15, maxHitBonus = 15)
        ),
        ItemDefinition(
            id = "bronze_claws",
            name = "Bronze Claws",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 13, strengthBonus = 1, accuracyBonus = 24, maxHitBonus = 7)
        ),
        ItemDefinition(
            id = "bronze_2h_sword",
            name = "Bronze Two-Handed Sword",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 9, strengthBonus = 7, accuracyBonus = 15, maxHitBonus = 18)
        ),
        ItemDefinition(
            id = "bronze_platebody",
            name = "Bronze Platebody",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.CHESTPLATE,
            stats = ItemStats(defenseBonus = 15)
        ),
        ItemDefinition(
            id = "bronze_halberd",
            name = "Bronze Halberd",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 11, strengthBonus = 5, accuracyBonus = 17, maxHitBonus = 16)
        ),
        ItemDefinition(
            id = "iron_dagger",
            name = "Iron Dagger",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 14, strengthBonus = 2, accuracyBonus = 26, maxHitBonus = 9)
        ),
        ItemDefinition(
            id = "iron_sword",
            name = "Iron Sword",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 14, strengthBonus = 3, accuracyBonus = 23, maxHitBonus = 14)
        ),
        ItemDefinition(
            id = "iron_mace",
            name = "Iron Mace",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 13, strengthBonus = 6, accuracyBonus = 21, maxHitBonus = 16)
        ),
        ItemDefinition(
            id = "iron_arrowheads",
            name = "Iron Arrowheads",
            category = ItemCategory.MATERIAL,
            isTradeable = true,
            isStackable = true,
        ),
        ItemDefinition(
            id = "iron_warhammer",
            name = "Iron Warhammer",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 11, strengthBonus = 9, accuracyBonus = 17, maxHitBonus = 25)
        ),
        ItemDefinition(
            id = "iron_throwing_knives",
            name = "Iron Throwing Knives",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.RANGED,
            stats = ItemStats(attackBonus = 16, strengthBonus = 1, accuracyBonus = 30, maxHitBonus = 9)
        ),
        ItemDefinition(
            id = "iron_platelegs",
            name = "Iron Platelegs",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.LEGS,
            stats = ItemStats(defenseBonus = 15)
        ),
        ItemDefinition(
            id = "iron_kiteshield",
            name = "Iron Kiteshield",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.SHIELD,
            stats = ItemStats(defenseBonus = 15)
        ),
        ItemDefinition(
            id = "iron_battleaxe",
            name = "Iron Battleaxe",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 15, strengthBonus = 10, accuracyBonus = 23, maxHitBonus = 26)
        ),
        ItemDefinition(
            id = "iron_claws",
            name = "Iron Claws",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 20, strengthBonus = 2, accuracyBonus = 38, maxHitBonus = 11)
        ),
        ItemDefinition(
            id = "iron_2h_sword",
            name = "Iron Two-Handed Sword",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 14, strengthBonus = 11, accuracyBonus = 24, maxHitBonus = 29)
        ),
        ItemDefinition(
            id = "iron_platebody",
            name = "Iron Platebody",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.CHESTPLATE,
            stats = ItemStats(defenseBonus = 23)
        ),
        ItemDefinition(
            id = "iron_halberd",
            name = "Iron Halberd",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 17, strengthBonus = 8, accuracyBonus = 27, maxHitBonus = 26)
        ),
        ItemDefinition(
            id = "steel_dagger",
            name = "Steel Dagger",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 28, strengthBonus = 4, accuracyBonus = 52, maxHitBonus = 20)
        ),
        ItemDefinition(
            id = "steel_sword",
            name = "Steel Sword",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 28, strengthBonus = 7, accuracyBonus = 45, maxHitBonus = 29)
        ),
        ItemDefinition(
            id = "steel_mace",
            name = "Steel Mace",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 26, strengthBonus = 11, accuracyBonus = 41, maxHitBonus = 33)
        ),
        ItemDefinition(
            id = "steel_arrowheads",
            name = "Steel Arrowheads",
            category = ItemCategory.MATERIAL,
            isTradeable = true,
            isStackable = true,
        ),
        ItemDefinition(
            id = "steel_warhammer",
            name = "Steel Warhammer",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 21, strengthBonus = 19, accuracyBonus = 33, maxHitBonus = 49)
        ),
        ItemDefinition(
            id = "steel_throwing_knives",
            name = "Steel Throwing Knives",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.RANGED,
            stats = ItemStats(attackBonus = 30, strengthBonus = 1, accuracyBonus = 56, maxHitBonus = 18)
        ),
        ItemDefinition(
            id = "steel_chainmail_body",
            name = "Steel Chainmail Body",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.CHESTPLATE,
            stats = ItemStats(defenseBonus = 36)
        ),
        ItemDefinition(
            id = "steel_full_helm",
            name = "Steel Full Helm",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.HELMET,
            stats = ItemStats(defenseBonus = 20)
        ),
        ItemDefinition(
            id = "steel_battleaxe",
            name = "Steel Battleaxe",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 26, strengthBonus = 17, accuracyBonus = 41, maxHitBonus = 47)
        ),
        ItemDefinition(
            id = "steel_claws",
            name = "Steel Claws",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 36, strengthBonus = 3, accuracyBonus = 67, maxHitBonus = 20)
        ),
        ItemDefinition(
            id = "steel_2h_sword",
            name = "Steel Two-Handed Sword",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 25, strengthBonus = 19, accuracyBonus = 42, maxHitBonus = 51)
        ),
        ItemDefinition(
            id = "steel_halberd",
            name = "Steel Halberd",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 29, strengthBonus = 15, accuracyBonus = 45, maxHitBonus = 46)
        ),
        ItemDefinition(
            id = "mithril_dagger",
            name = "Mithril Dagger",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 38, strengthBonus = 6, accuracyBonus = 72, maxHitBonus = 28)
        ),
        ItemDefinition(
            id = "mithril_sword",
            name = "Mithril Sword",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 39, strengthBonus = 9, accuracyBonus = 61, maxHitBonus = 40)
        ),
        ItemDefinition(
            id = "mithril_mace",
            name = "Mithril Mace",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 35, strengthBonus = 15, accuracyBonus = 56, maxHitBonus = 45)
        ),
        ItemDefinition(
            id = "mithril_warhammer",
            name = "Mithril Warhammer",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 28, strengthBonus = 25, accuracyBonus = 44, maxHitBonus = 67)
        ),
        ItemDefinition(
            id = "mithril_throwing_knives",
            name = "Mithril Throwing Knives",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.RANGED,
            stats = ItemStats(attackBonus = 40, strengthBonus = 2, accuracyBonus = 76, maxHitBonus = 25)
        ),
        ItemDefinition(
            id = "mithril_chainmail_body",
            name = "Mithril Chainmail Body",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.CHESTPLATE,
            stats = ItemStats(defenseBonus = 48)
        ),
        ItemDefinition(
            id = "mithril_full_helm",
            name = "Mithril Full Helm",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.HELMET,
            stats = ItemStats(defenseBonus = 28)
        ),
        ItemDefinition(
            id = "mithril_platelegs",
            name = "Mithril Platelegs",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.LEGS,
            stats = ItemStats(defenseBonus = 38)
        ),
        ItemDefinition(
            id = "mithril_kiteshield",
            name = "Mithril Kiteshield",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.SHIELD,
            stats = ItemStats(defenseBonus = 36)
        ),
        ItemDefinition(
            id = "mithril_claws",
            name = "Mithril Claws",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 47, strengthBonus = 4, accuracyBonus = 88, maxHitBonus = 27)
        ),
        ItemDefinition(
            id = "mithril_platebody",
            name = "Mithril Platebody",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.CHESTPLATE,
            stats = ItemStats(defenseBonus = 52)
        ),
        ItemDefinition(
            id = "mithril_halberd",
            name = "Mithril Halberd",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 38, strengthBonus = 19, accuracyBonus = 59, maxHitBonus = 60)
        ),
        ItemDefinition(
            id = "adamant_dagger",
            name = "Adamant Dagger",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 45, strengthBonus = 7, accuracyBonus = 85, maxHitBonus = 33)
        ),
        ItemDefinition(
            id = "adamant_sword",
            name = "Adamant Sword",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 46, strengthBonus = 11, accuracyBonus = 72, maxHitBonus = 48)
        ),
        ItemDefinition(
            id = "adamant_mace",
            name = "Adamant Mace",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 42, strengthBonus = 18, accuracyBonus = 66, maxHitBonus = 53)
        ),
        ItemDefinition(
            id = "adamant_arrowheads",
            name = "Adamant Arrowheads",
            category = ItemCategory.MATERIAL,
            isTradeable = true,
            isStackable = true,
        ),
        ItemDefinition(
            id = "adamant_warhammer",
            name = "Adamant Warhammer",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 33, strengthBonus = 30, accuracyBonus = 52, maxHitBonus = 79)
        ),
        ItemDefinition(
            id = "adamant_chainmail_body",
            name = "Adamant Chainmail Body",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.CHESTPLATE,
            stats = ItemStats(defenseBonus = 57)
        ),
        ItemDefinition(
            id = "adamant_full_helm",
            name = "Adamant Full Helm",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.HELMET,
            stats = ItemStats(defenseBonus = 32)
        ),
        ItemDefinition(
            id = "adamant_platelegs",
            name = "Adamant Platelegs",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.LEGS,
            stats = ItemStats(defenseBonus = 45)
        ),
        ItemDefinition(
            id = "adamant_kiteshield",
            name = "Adamant Kiteshield",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.SHIELD,
            stats = ItemStats(defenseBonus = 42)
        ),
        ItemDefinition(
            id = "adamant_battleaxe",
            name = "Adamant Battleaxe",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 40, strengthBonus = 27, accuracyBonus = 63, maxHitBonus = 73)
        ),
        ItemDefinition(
            id = "adamant_claws",
            name = "Adamant Claws",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 55, strengthBonus = 5, accuracyBonus = 102, maxHitBonus = 31)
        ),
        ItemDefinition(
            id = "adamant_2h_sword",
            name = "Adamant Two-Handed Sword",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 38, strengthBonus = 30, accuracyBonus = 64, maxHitBonus = 80)
        ),
        ItemDefinition(
            id = "adamant_platebody",
            name = "Adamant Platebody",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.CHESTPLATE,
            stats = ItemStats(defenseBonus = 61)
        ),
        ItemDefinition(
            id = "adamant_halberd",
            name = "Adamant Halberd",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 44, strengthBonus = 23, accuracyBonus = 69, maxHitBonus = 70)
        ),
        ItemDefinition(
            id = "rune_dagger",
            name = "Rune Dagger",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 52, strengthBonus = 8, accuracyBonus = 98, maxHitBonus = 38)
        ),
        ItemDefinition(
            id = "rune_sword",
            name = "Rune Sword",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 53, strengthBonus = 13, accuracyBonus = 83, maxHitBonus = 55)
        ),
        ItemDefinition(
            id = "rune_mace",
            name = "Rune Mace",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 48, strengthBonus = 21, accuracyBonus = 76, maxHitBonus = 62)
        ),
        ItemDefinition(
            id = "rune_arrowheads",
            name = "Rune Arrowheads",
            category = ItemCategory.MATERIAL,
            isTradeable = true,
            isStackable = true,
        ),
        ItemDefinition(
            id = "rune_warhammer",
            name = "Rune Warhammer",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 38, strengthBonus = 35, accuracyBonus = 60, maxHitBonus = 91)
        ),
        ItemDefinition(
            id = "rune_throwing_knives",
            name = "Rune Throwing Knives",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.RANGED,
            stats = ItemStats(attackBonus = 54, strengthBonus = 3, accuracyBonus = 102, maxHitBonus = 34)
        ),
        ItemDefinition(
            id = "rune_chainmail_body",
            name = "Rune Chainmail Body",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.CHESTPLATE,
            stats = ItemStats(defenseBonus = 65)
        ),
        ItemDefinition(
            id = "rune_full_helm",
            name = "Rune Full Helm",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.HELMET,
            stats = ItemStats(defenseBonus = 37)
        ),
        ItemDefinition(
            id = "rune_platelegs",
            name = "Rune Platelegs",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.LEGS,
            stats = ItemStats(defenseBonus = 52)
        ),
        ItemDefinition(
            id = "rune_kiteshield",
            name = "Rune Kiteshield",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.SHIELD,
            stats = ItemStats(defenseBonus = 48)
        ),
        ItemDefinition(
            id = "rune_battleaxe",
            name = "Rune Battleaxe",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 46, strengthBonus = 31, accuracyBonus = 72, maxHitBonus = 84)
        ),
        ItemDefinition(
            id = "rune_2h_sword",
            name = "Rune Two-Handed Sword",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 43, strengthBonus = 34, accuracyBonus = 73, maxHitBonus = 91)
        ),
        ItemDefinition(
            id = "rune_platebody",
            name = "Rune Platebody",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.CHESTPLATE,
            stats = ItemStats(defenseBonus = 69)
        ),
        ItemDefinition(
            id = "orichalcum_dagger",
            name = "Orichalcum Dagger",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 59, strengthBonus = 9, accuracyBonus = 112, maxHitBonus = 43)
        ),
        ItemDefinition(
            id = "orichalcum_sword",
            name = "Orichalcum Sword",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 60, strengthBonus = 15, accuracyBonus = 94, maxHitBonus = 63)
        ),
        ItemDefinition(
            id = "orichalcum_mace",
            name = "Orichalcum Mace",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 54, strengthBonus = 24, accuracyBonus = 86, maxHitBonus = 70)
        ),
        ItemDefinition(
            id = "orichalcum_arrowheads",
            name = "Orichalcum Arrowheads",
            category = ItemCategory.MATERIAL,
            isTradeable = true,
            isStackable = true,
        ),
        ItemDefinition(
            id = "orichalcum_warhammer",
            name = "Orichalcum Warhammer",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 43, strengthBonus = 39, accuracyBonus = 67, maxHitBonus = 103)
        ),
        ItemDefinition(
            id = "orichalcum_throwing_knives",
            name = "Orichalcum Throwing Knives",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.RANGED,
            stats = ItemStats(attackBonus = 61, strengthBonus = 3, accuracyBonus = 116, maxHitBonus = 39)
        ),
        ItemDefinition(
            id = "orichalcum_chainmail_body",
            name = "Orichalcum Chainmail Body",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.CHESTPLATE,
            stats = ItemStats(defenseBonus = 73)
        ),
        ItemDefinition(
            id = "orichalcum_full_helm",
            name = "Orichalcum Full Helm",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.HELMET,
            stats = ItemStats(defenseBonus = 42)
        ),
        ItemDefinition(
            id = "orichalcum_platelegs",
            name = "Orichalcum Platelegs",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.LEGS,
            stats = ItemStats(defenseBonus = 58)
        ),
        ItemDefinition(
            id = "orichalcum_kiteshield",
            name = "Orichalcum Kiteshield",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.SHIELD,
            stats = ItemStats(defenseBonus = 54)
        ),
        ItemDefinition(
            id = "orichalcum_battleaxe",
            name = "Orichalcum Battleaxe",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 51, strengthBonus = 35, accuracyBonus = 81, maxHitBonus = 94)
        ),
        ItemDefinition(
            id = "orichalcum_claws",
            name = "Orichalcum Claws",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 70, strengthBonus = 6, accuracyBonus = 131, maxHitBonus = 40)
        ),
        ItemDefinition(
            id = "orichalcum_2h_sword",
            name = "Orichalcum Two-Handed Sword",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 48, strengthBonus = 38, accuracyBonus = 81, maxHitBonus = 102)
        ),
        ItemDefinition(
            id = "orichalcum_platebody",
            name = "Orichalcum Platebody",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.CHESTPLATE,
            stats = ItemStats(defenseBonus = 78)
        ),
        ItemDefinition(
            id = "orichalcum_halberd",
            name = "Orichalcum Halberd",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 56, strengthBonus = 29, accuracyBonus = 87, maxHitBonus = 89)
        ),
        ItemDefinition(
            id = "celestial_dagger",
            name = "Celestial Dagger",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 66, strengthBonus = 10, accuracyBonus = 125, maxHitBonus = 49)
        ),
        ItemDefinition(
            id = "celestial_sword",
            name = "Celestial Sword",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 67, strengthBonus = 16, accuracyBonus = 105, maxHitBonus = 70)
        ),
        ItemDefinition(
            id = "celestial_mace",
            name = "Celestial Mace",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 61, strengthBonus = 27, accuracyBonus = 96, maxHitBonus = 78)
        ),
        ItemDefinition(
            id = "celestial_arrowheads",
            name = "Celestial Arrowheads",
            category = ItemCategory.MATERIAL,
            isTradeable = true,
            isStackable = true,
        ),
        ItemDefinition(
            id = "celestial_warhammer",
            name = "Celestial Warhammer",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 48, strengthBonus = 44, accuracyBonus = 75, maxHitBonus = 115)
        ),
        ItemDefinition(
            id = "celestial_throwing_knives",
            name = "Celestial Throwing Knives",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.RANGED,
            stats = ItemStats(attackBonus = 68, strengthBonus = 3, accuracyBonus = 129, maxHitBonus = 43)
        ),
        ItemDefinition(
            id = "celestial_chainmail_body",
            name = "Celestial Chainmail Body",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.CHESTPLATE,
            stats = ItemStats(defenseBonus = 82)
        ),
        ItemDefinition(
            id = "celestial_full_helm",
            name = "Celestial Full Helm",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.HELMET,
            stats = ItemStats(defenseBonus = 47)
        ),
        ItemDefinition(
            id = "celestial_platelegs",
            name = "Celestial Platelegs",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.LEGS,
            stats = ItemStats(defenseBonus = 65)
        ),
        ItemDefinition(
            id = "celestial_kiteshield",
            name = "Celestial Kiteshield",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.SHIELD,
            stats = ItemStats(defenseBonus = 60)
        ),
        ItemDefinition(
            id = "celestial_battleaxe",
            name = "Celestial Battleaxe",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 57, strengthBonus = 38, accuracyBonus = 89, maxHitBonus = 105)
        ),
        ItemDefinition(
            id = "celestial_claws",
            name = "Celestial Claws",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 78, strengthBonus = 7, accuracyBonus = 145, maxHitBonus = 45)
        ),
        ItemDefinition(
            id = "celestial_2h_sword",
            name = "Celestial Two-Handed Sword",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 54, strengthBonus = 42, accuracyBonus = 90, maxHitBonus = 113)
        ),
        ItemDefinition(
            id = "celestial_platebody",
            name = "Celestial Platebody",
            category = ItemCategory.ARMOR,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.CHESTPLATE,
            stats = ItemStats(defenseBonus = 86)
        ),
        ItemDefinition(
            id = "celestial_halberd",
            name = "Celestial Halberd",
            category = ItemCategory.WEAPON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            stats = ItemStats(attackBonus = 61, strengthBonus = 32, accuracyBonus = 97, maxHitBonus = 99)
        ),
    )
}