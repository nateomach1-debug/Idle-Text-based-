package com.yourname.idlerpg

import kotlin.random.Random

// =========================================================
// ITEM CATEGORY, RARITY, EQUIP SLOTS, ITEM DEFINITION, and
// ITEM CATALOG now all come from SharedTypes.kt -- no longer
// defined here. CombatStyle and EquipmentSlot also come from
// SharedTypes.kt.
// =========================================================

// =========================================================
// RECIPE CATALOG
// =========================================================

data class RecipeIngredient(val itemId: String, val quantity: Int)

data class Recipe(
    val outputItemId: String,
    val outputQuantity: Int,
    val ingredients: List<RecipeIngredient>,
    val skillRequired: String,
    val levelRequired: Int
)

object RecipeCatalog {
    val recipes = listOf(
        Recipe(
            outputItemId = "bronze_dagger",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("bronze_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 5
        ),
        Recipe(
            outputItemId = "bronze_sword",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("bronze_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 6
        ),
        Recipe(
            outputItemId = "bronze_mace",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("bronze_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 7
        ),
        Recipe(
            outputItemId = "bronze_arrowheads",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("bronze_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 7
        ),
        Recipe(
            outputItemId = "bronze_warhammer",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("bronze_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 8
        ),
        Recipe(
            outputItemId = "bronze_throwing_knives",
            outputQuantity = 5,
            ingredients = listOf(RecipeIngredient("bronze_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 8
        ),
        Recipe(
            outputItemId = "bronze_chainmail_body",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("bronze_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 9
        ),
        Recipe(
            outputItemId = "bronze_full_helm",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("bronze_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 9
        ),
        Recipe(
            outputItemId = "bronze_platelegs",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("bronze_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 10
        ),
        Recipe(
            outputItemId = "bronze_kiteshield",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("bronze_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 11
        ),
        Recipe(
            outputItemId = "bronze_battleaxe",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("bronze_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 12
        ),
        Recipe(
            outputItemId = "bronze_claws",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("bronze_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 12
        ),
        Recipe(
            outputItemId = "bronze_2h_sword",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("bronze_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 13
        ),
        Recipe(
            outputItemId = "bronze_platebody",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("bronze_bar", 5)),
            skillRequired = "SMITHING",
            levelRequired = 14
        ),
        Recipe(
            outputItemId = "bronze_halberd",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("bronze_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 14
        ),
        Recipe(
            outputItemId = "iron_dagger",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("iron_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 15
        ),
        Recipe(
            outputItemId = "iron_sword",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("iron_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 16
        ),
        Recipe(
            outputItemId = "iron_mace",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("iron_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 17
        ),
        Recipe(
            outputItemId = "iron_arrowheads",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("iron_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 17
        ),
        Recipe(
            outputItemId = "iron_warhammer",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("iron_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 18
        ),
        Recipe(
            outputItemId = "iron_throwing_knives",
            outputQuantity = 5,
            ingredients = listOf(RecipeIngredient("iron_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 18
        ),
        Recipe(
            outputItemId = "iron_chainmail_body",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("iron_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 19
        ),
        Recipe(
            outputItemId = "iron_full_helm",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("iron_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 19
        ),
        Recipe(
            outputItemId = "iron_platelegs",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("iron_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 20
        ),
        Recipe(
            outputItemId = "iron_kiteshield",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("iron_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 21
        ),
        Recipe(
            outputItemId = "iron_battleaxe",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("iron_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 22
        ),
        Recipe(
            outputItemId = "iron_claws",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("iron_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 22
        ),
        Recipe(
            outputItemId = "iron_2h_sword",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("iron_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 23
        ),
        Recipe(
            outputItemId = "iron_platebody",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("iron_bar", 5)),
            skillRequired = "SMITHING",
            levelRequired = 24
        ),
        Recipe(
            outputItemId = "iron_halberd",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("iron_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 24
        ),
        Recipe(
            outputItemId = "steel_dagger",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("steel_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 35
        ),
        Recipe(
            outputItemId = "steel_sword",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("steel_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 36
        ),
        Recipe(
            outputItemId = "steel_mace",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("steel_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 37
        ),
        Recipe(
            outputItemId = "steel_arrowheads",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("steel_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 37
        ),
        Recipe(
            outputItemId = "steel_warhammer",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("steel_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 38
        ),
        Recipe(
            outputItemId = "steel_throwing_knives",
            outputQuantity = 5,
            ingredients = listOf(RecipeIngredient("steel_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 38
        ),
        Recipe(
            outputItemId = "steel_chainmail_body",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("steel_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 39
        ),
        Recipe(
            outputItemId = "steel_full_helm",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("steel_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 39
        ),
        Recipe(
            outputItemId = "steel_platelegs",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("steel_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 40
        ),
        Recipe(
            outputItemId = "steel_kiteshield",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("steel_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 41
        ),
        Recipe(
            outputItemId = "steel_battleaxe",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("steel_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 42
        ),
        Recipe(
            outputItemId = "steel_claws",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("steel_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 42
        ),
        Recipe(
            outputItemId = "steel_2h_sword",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("steel_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 43
        ),
        Recipe(
            outputItemId = "steel_platebody",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("steel_bar", 5)),
            skillRequired = "SMITHING",
            levelRequired = 44
        ),
        Recipe(
            outputItemId = "steel_halberd",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("steel_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 44
        ),
        Recipe(
            outputItemId = "mithril_dagger",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("mithril_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 50
        ),
        Recipe(
            outputItemId = "mithril_sword",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("mithril_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 51
        ),
        Recipe(
            outputItemId = "mithril_mace",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("mithril_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 52
        ),
        Recipe(
            outputItemId = "mithril_arrowheads",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("mithril_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 52
        ),
        Recipe(
            outputItemId = "mithril_warhammer",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("mithril_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 53
        ),
        Recipe(
            outputItemId = "mithril_throwing_knives",
            outputQuantity = 5,
            ingredients = listOf(RecipeIngredient("mithril_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 53
        ),
        Recipe(
            outputItemId = "mithril_chainmail_body",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("mithril_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 54
        ),
        Recipe(
            outputItemId = "mithril_full_helm",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("mithril_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 54
        ),
        Recipe(
            outputItemId = "mithril_platelegs",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("mithril_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 55
        ),
        Recipe(
            outputItemId = "mithril_kiteshield",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("mithril_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 56
        ),
        Recipe(
            outputItemId = "mithril_battleaxe",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("mithril_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 57
        ),
        Recipe(
            outputItemId = "mithril_claws",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("mithril_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 57
        ),
        Recipe(
            outputItemId = "mithril_2h_sword",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("mithril_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 58
        ),
        Recipe(
            outputItemId = "mithril_platebody",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("mithril_bar", 5)),
            skillRequired = "SMITHING",
            levelRequired = 59
        ),
        Recipe(
            outputItemId = "mithril_halberd",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("mithril_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 59
        ),
        Recipe(
            outputItemId = "adamant_dagger",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("adamantite_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 60
        ),
        Recipe(
            outputItemId = "adamant_sword",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("adamantite_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 61
        ),
        Recipe(
            outputItemId = "adamant_mace",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("adamantite_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 62
        ),
        Recipe(
            outputItemId = "adamant_arrowheads",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("adamantite_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 62
        ),
        Recipe(
            outputItemId = "adamant_warhammer",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("adamantite_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 63
        ),
        Recipe(
            outputItemId = "adamant_throwing_knives",
            outputQuantity = 5,
            ingredients = listOf(RecipeIngredient("adamantite_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 63
        ),
        Recipe(
            outputItemId = "adamant_chainmail_body",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("adamantite_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 64
        ),
        Recipe(
            outputItemId = "adamant_full_helm",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("adamantite_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 64
        ),
        Recipe(
            outputItemId = "adamant_platelegs",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("adamantite_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 65
        ),
        Recipe(
            outputItemId = "adamant_kiteshield",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("adamantite_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 66
        ),
        Recipe(
            outputItemId = "adamant_battleaxe",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("adamantite_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 67
        ),
        Recipe(
            outputItemId = "adamant_claws",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("adamantite_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 67
        ),
        Recipe(
            outputItemId = "adamant_2h_sword",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("adamantite_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 68
        ),
        Recipe(
            outputItemId = "adamant_platebody",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("adamantite_bar", 5)),
            skillRequired = "SMITHING",
            levelRequired = 69
        ),
        Recipe(
            outputItemId = "adamant_halberd",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("adamantite_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 69
        ),
        Recipe(
            outputItemId = "rune_dagger",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("runite_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 70
        ),
        Recipe(
            outputItemId = "rune_sword",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("runite_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 71
        ),
        Recipe(
            outputItemId = "rune_mace",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("runite_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 72
        ),
        Recipe(
            outputItemId = "rune_arrowheads",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("runite_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 72
        ),
        Recipe(
            outputItemId = "rune_warhammer",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("runite_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 73
        ),
        Recipe(
            outputItemId = "rune_throwing_knives",
            outputQuantity = 5,
            ingredients = listOf(RecipeIngredient("runite_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 73
        ),
        Recipe(
            outputItemId = "rune_chainmail_body",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("runite_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 74
        ),
        Recipe(
            outputItemId = "rune_full_helm",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("runite_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 74
        ),
        Recipe(
            outputItemId = "rune_platelegs",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("runite_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 75
        ),
        Recipe(
            outputItemId = "rune_kiteshield",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("runite_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 76
        ),
        Recipe(
            outputItemId = "rune_battleaxe",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("runite_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 77
        ),
        Recipe(
            outputItemId = "rune_claws",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("runite_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 77
        ),
        Recipe(
            outputItemId = "rune_2h_sword",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("runite_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 78
        ),
        Recipe(
            outputItemId = "rune_platebody",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("runite_bar", 5)),
            skillRequired = "SMITHING",
            levelRequired = 79
        ),
        Recipe(
            outputItemId = "rune_halberd",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("runite_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 79
        ),
        Recipe(
            outputItemId = "orichalcum_dagger",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("orichalcum_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 80
        ),
        Recipe(
            outputItemId = "orichalcum_sword",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("orichalcum_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 81
        ),
        Recipe(
            outputItemId = "orichalcum_mace",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("orichalcum_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 82
        ),
        Recipe(
            outputItemId = "orichalcum_arrowheads",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("orichalcum_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 82
        ),
        Recipe(
            outputItemId = "orichalcum_warhammer",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("orichalcum_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 83
        ),
        Recipe(
            outputItemId = "orichalcum_throwing_knives",
            outputQuantity = 5,
            ingredients = listOf(RecipeIngredient("orichalcum_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 83
        ),
        Recipe(
            outputItemId = "orichalcum_chainmail_body",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("orichalcum_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 84
        ),
        Recipe(
            outputItemId = "orichalcum_full_helm",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("orichalcum_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 84
        ),
        Recipe(
            outputItemId = "orichalcum_platelegs",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("orichalcum_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 85
        ),
        Recipe(
            outputItemId = "orichalcum_kiteshield",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("orichalcum_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 86
        ),
        Recipe(
            outputItemId = "orichalcum_battleaxe",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("orichalcum_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 87
        ),
        Recipe(
            outputItemId = "orichalcum_claws",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("orichalcum_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 87
        ),
        Recipe(
            outputItemId = "orichalcum_2h_sword",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("orichalcum_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 88
        ),
        Recipe(
            outputItemId = "orichalcum_platebody",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("orichalcum_bar", 5)),
            skillRequired = "SMITHING",
            levelRequired = 89
        ),
        Recipe(
            outputItemId = "orichalcum_halberd",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("orichalcum_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 89
        ),
        Recipe(
            outputItemId = "celestial_dagger",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("celestial_alloy_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 90
        ),
        Recipe(
            outputItemId = "celestial_sword",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("celestial_alloy_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 91
        ),
        Recipe(
            outputItemId = "celestial_mace",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("celestial_alloy_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 92
        ),
        Recipe(
            outputItemId = "celestial_arrowheads",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("celestial_alloy_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 92
        ),
        Recipe(
            outputItemId = "celestial_warhammer",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("celestial_alloy_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 93
        ),
        Recipe(
            outputItemId = "celestial_throwing_knives",
            outputQuantity = 5,
            ingredients = listOf(RecipeIngredient("celestial_alloy_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 93
        ),
        Recipe(
            outputItemId = "celestial_chainmail_body",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("celestial_alloy_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 94
        ),
        Recipe(
            outputItemId = "celestial_full_helm",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("celestial_alloy_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 94
        ),
        Recipe(
            outputItemId = "celestial_platelegs",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("celestial_alloy_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 95
        ),
        Recipe(
            outputItemId = "celestial_kiteshield",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("celestial_alloy_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 96
        ),
        Recipe(
            outputItemId = "celestial_battleaxe",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("celestial_alloy_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 97
        ),
        Recipe(
            outputItemId = "celestial_claws",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("celestial_alloy_bar", 2)),
            skillRequired = "SMITHING",
            levelRequired = 97
        ),
        Recipe(
            outputItemId = "celestial_2h_sword",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("celestial_alloy_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 98
        ),
        Recipe(
            outputItemId = "celestial_platebody",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("celestial_alloy_bar", 5)),
            skillRequired = "SMITHING",
            levelRequired = 99
        ),
        Recipe(
            outputItemId = "celestial_halberd",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("celestial_alloy_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 99
        ),
        Recipe(
            outputItemId = "full_plate_armor_set",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("adamantite_bar", 8)),
            skillRequired = "SMITHING",
            levelRequired = 65
        ),
        Recipe(
            outputItemId = "orichalcum_ceremonial_armor",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("orichalcum_bar", 6)),
            skillRequired = "SMITHING",
            levelRequired = 80
        ),
        Recipe(
            outputItemId = "masterwork_weapon",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("celestial_alloy_bar", 5)),
            skillRequired = "SMITHING",
            levelRequired = 85
        ),
        Recipe(
            outputItemId = "legendary_blade",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("celestial_alloy_bar", 8)),
            skillRequired = "SMITHING",
            levelRequired = 90
        ),
        Recipe(
            outputItemId = "copper_bar",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("copper_ore", 1)),
            skillRequired = "SMITHING",
            levelRequired = 1
        ),
        Recipe(
            outputItemId = "tin_bar",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("tin_ore", 1)),
            skillRequired = "SMITHING",
            levelRequired = 1
        ),
        Recipe(
            outputItemId = "bronze_bar",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("copper_ore", 1), RecipeIngredient("tin_ore", 1)),
            skillRequired = "SMITHING",
            levelRequired = 1
        ),
        Recipe(
            outputItemId = "iron_bar",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("iron_ore", 1)),
            skillRequired = "SMITHING",
            levelRequired = 15
        ),
        Recipe(
            outputItemId = "silver_bar",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("silver_ore", 1)),
            skillRequired = "SMITHING",
            levelRequired = 30
        ),
        Recipe(
            outputItemId = "steel_bar",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("iron_ore", 1), RecipeIngredient("coal", 1)),
            skillRequired = "SMITHING",
            levelRequired = 35
        ),
        Recipe(
            outputItemId = "gold_bar",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("gold_ore", 1)),
            skillRequired = "SMITHING",
            levelRequired = 40
        ),
        Recipe(
            outputItemId = "mithril_bar",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("mithril_ore", 1), RecipeIngredient("coal", 2)),
            skillRequired = "SMITHING",
            levelRequired = 50
        ),
        Recipe(
            outputItemId = "adamantite_bar",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("adamantite_ore", 1), RecipeIngredient("coal", 3)),
            skillRequired = "SMITHING",
            levelRequired = 60
        ),
        Recipe(
            outputItemId = "runite_bar",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("runite_ore", 1), RecipeIngredient("coal", 4)),
            skillRequired = "SMITHING",
            levelRequired = 70
        ),
        Recipe(
            outputItemId = "orichalcum_bar",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("orichalcum_ore", 1), RecipeIngredient("coal", 5)),
            skillRequired = "SMITHING",
            levelRequired = 80
        ),
        Recipe(
            outputItemId = "celestial_alloy_bar",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("celestial_silver", 1), RecipeIngredient("coal", 6)),
            skillRequired = "SMITHING",
            levelRequired = 90
        ),
        Recipe(
            outputItemId = "iron_nails",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("copper_bar", 1)),
            skillRequired = "SMITHING",
            levelRequired = 1
        ),
        Recipe(
            outputItemId = "cooked_shrimp",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_shrimp", 1)),
            skillRequired = "COOKING",
            levelRequired = 1
        ),
        Recipe(
            outputItemId = "cooked_anchovies",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_anchovies", 1)),
            skillRequired = "COOKING",
            levelRequired = 1
        ),
        Recipe(
            outputItemId = "cooked_sardine",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_sardine", 1)),
            skillRequired = "COOKING",
            levelRequired = 5
        ),
        Recipe(
            outputItemId = "cooked_chicken",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_chicken", 1)),
            skillRequired = "COOKING",
            levelRequired = 8
        ),
        Recipe(
            outputItemId = "cooked_herring",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_herring", 1)),
            skillRequired = "COOKING",
            levelRequired = 10
        ),
        Recipe(
            outputItemId = "cooked_beef",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_beef", 1)),
            skillRequired = "COOKING",
            levelRequired = 12
        ),
        Recipe(
            outputItemId = "cooked_crayfish",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_crayfish", 1)),
            skillRequired = "COOKING",
            levelRequired = 15
        ),
        Recipe(
            outputItemId = "cooked_trout",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_trout", 1)),
            skillRequired = "COOKING",
            levelRequired = 20
        ),
        Recipe(
            outputItemId = "cooked_salmon",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_salmon", 1)),
            skillRequired = "COOKING",
            levelRequired = 25
        ),
        Recipe(
            outputItemId = "cooked_tuna",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_tuna", 1)),
            skillRequired = "COOKING",
            levelRequired = 30
        ),
        Recipe(
            outputItemId = "cooked_mackerel",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_mackerel", 1)),
            skillRequired = "COOKING",
            levelRequired = 35
        ),
        Recipe(
            outputItemId = "cooked_swordfish",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_swordfish", 1)),
            skillRequired = "COOKING",
            levelRequired = 40
        ),
        Recipe(
            outputItemId = "cooked_lobster",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_lobster", 1)),
            skillRequired = "COOKING",
            levelRequired = 45
        ),
        Recipe(
            outputItemId = "cooked_crab",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_crab", 1)),
            skillRequired = "COOKING",
            levelRequired = 50
        ),
        Recipe(
            outputItemId = "cooked_shark",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_shark", 1)),
            skillRequired = "COOKING",
            levelRequired = 55
        ),
        Recipe(
            outputItemId = "cooked_monkfish",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_monkfish", 1)),
            skillRequired = "COOKING",
            levelRequired = 60
        ),
        Recipe(
            outputItemId = "cooked_manta_ray",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_manta_ray", 1)),
            skillRequired = "COOKING",
            levelRequired = 65
        ),
        Recipe(
            outputItemId = "cooked_eel",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_eel", 1)),
            skillRequired = "COOKING",
            levelRequired = 70
        ),
        Recipe(
            outputItemId = "cooked_deep_sea_cod",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_deep_sea_cod", 1)),
            skillRequired = "COOKING",
            levelRequired = 75
        ),
        Recipe(
            outputItemId = "cooked_anglerfish",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("raw_anglerfish", 1)),
            skillRequired = "COOKING",
            levelRequired = 80
        ),
        Recipe(
            outputItemId = "bread_dough",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("flour", 2), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "COOKING",
            levelRequired = 28
        ),
        Recipe(
            outputItemId = "bread",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("bread_dough", 1)),
            skillRequired = "COOKING",
            levelRequired = 28
        ),
        Recipe(
            outputItemId = "meat_pie",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("pie_shell", 1), RecipeIngredient("cooked_beef", 1)),
            skillRequired = "COOKING",
            levelRequired = 34
        ),
        Recipe(
            outputItemId = "apple_pie",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("pie_shell", 1), RecipeIngredient("apple", 1)),
            skillRequired = "COOKING",
            levelRequired = 36
        ),
        Recipe(
            outputItemId = "lemon_pie",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("pie_shell", 1), RecipeIngredient("lemon", 1)),
            skillRequired = "COOKING",
            levelRequired = 41
        ),
        Recipe(
            outputItemId = "pumpkin_pie",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("pie_shell", 1), RecipeIngredient("pumpkin", 1)),
            skillRequired = "COOKING",
            levelRequired = 48
        ),
        Recipe(
            outputItemId = "cake",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("cake_mix", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "COOKING",
            levelRequired = 42
        ),
        Recipe(
            outputItemId = "stew",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("potato", 1), RecipeIngredient("cooked_beef", 1)),
            skillRequired = "COOKING",
            levelRequired = 58
        ),
        Recipe(
            outputItemId = "gourmet_feast",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("cooked_shark", 1), RecipeIngredient("cooked_monkfish", 1), RecipeIngredient("cake", 1)),
            skillRequired = "COOKING",
            levelRequired = 85
        ),
        Recipe(
            outputItemId = "leviathan_steak",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("leviathan_spawn", 1)),
            skillRequired = "COOKING",
            levelRequired = 90
        ),
        Recipe(
            outputItemId = "ambrosia_banquet",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("cooked_anglerfish", 1), RecipeIngredient("gourmet_feast", 1), RecipeIngredient("celestial_herb", 1)),
            skillRequired = "COOKING",
            levelRequired = 99
        ),
        Recipe(
            outputItemId = "shortbow_u",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("logs", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 1
        ),
        Recipe(
            outputItemId = "shortbow",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("shortbow_u", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 5
        ),
        Recipe(
            outputItemId = "longbow_u",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("logs", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 10
        ),
        Recipe(
            outputItemId = "longbow",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("longbow_u", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 15
        ),
        Recipe(
            outputItemId = "oak_shortbow",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("oak_logs", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 20
        ),
        Recipe(
            outputItemId = "oak_longbow",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("oak_logs", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 25
        ),
        Recipe(
            outputItemId = "willow_shortbow",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("willow_logs", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 30
        ),
        Recipe(
            outputItemId = "willow_longbow",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("willow_logs", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 35
        ),
        Recipe(
            outputItemId = "composite_bow",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("teak_logs", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 40
        ),
        Recipe(
            outputItemId = "maple_longbow",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("maple_logs", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 45
        ),
        Recipe(
            outputItemId = "crossbow_frame",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("mahogany_logs", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 50
        ),
        Recipe(
            outputItemId = "crossbow",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("crossbow_frame", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 50
        ),
        Recipe(
            outputItemId = "yew_shortbow",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("yew_logs", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 55
        ),
        Recipe(
            outputItemId = "yew_longbow",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("yew_logs", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 60
        ),
        Recipe(
            outputItemId = "ironwood_composite_bow",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("ironwood_logs", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 65
        ),
        Recipe(
            outputItemId = "magic_shortbow",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("magic_logs", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 70
        ),
        Recipe(
            outputItemId = "magic_longbow",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("magic_logs", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 75
        ),
        Recipe(
            outputItemId = "elder_bow",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("elder_logs", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 80
        ),
        Recipe(
            outputItemId = "spirit_bow",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("spirit_logs", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 90
        ),
        Recipe(
            outputItemId = "ancient_ironbark_bow",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("ancient_ironbark_logs", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 99
        ),
        Recipe(
            outputItemId = "arrow_shafts",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("logs", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 1
        ),
        Recipe(
            outputItemId = "bronze_arrows",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("arrow_shafts", 15), RecipeIngredient("feathers", 15), RecipeIngredient("bronze_arrowheads", 15)),
            skillRequired = "FLETCHING",
            levelRequired = 5
        ),
        Recipe(
            outputItemId = "iron_arrows",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("arrow_shafts", 15), RecipeIngredient("feathers", 15), RecipeIngredient("iron_arrowheads", 15)),
            skillRequired = "FLETCHING",
            levelRequired = 15
        ),
        Recipe(
            outputItemId = "bolt_frame",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("iron_bar", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 20
        ),
        Recipe(
            outputItemId = "bolts",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("bolt_frame", 15), RecipeIngredient("feathers", 15)),
            skillRequired = "FLETCHING",
            levelRequired = 20
        ),
        Recipe(
            outputItemId = "steel_arrows",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("arrow_shafts", 15), RecipeIngredient("feathers", 15), RecipeIngredient("steel_arrowheads", 15)),
            skillRequired = "FLETCHING",
            levelRequired = 25
        ),
        Recipe(
            outputItemId = "mithril_arrows",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("arrow_shafts", 15), RecipeIngredient("feathers", 15), RecipeIngredient("mithril_arrowheads", 15)),
            skillRequired = "FLETCHING",
            levelRequired = 35
        ),
        Recipe(
            outputItemId = "adamant_arrows",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("arrow_shafts", 15), RecipeIngredient("feathers", 15), RecipeIngredient("adamant_arrowheads", 15)),
            skillRequired = "FLETCHING",
            levelRequired = 45
        ),
        Recipe(
            outputItemId = "rune_arrows",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("arrow_shafts", 15), RecipeIngredient("feathers", 15), RecipeIngredient("rune_arrowheads", 15)),
            skillRequired = "FLETCHING",
            levelRequired = 55
        ),
        Recipe(
            outputItemId = "barbed_bolts",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("bolt_frame", 15), RecipeIngredient("feathers", 15)),
            skillRequired = "FLETCHING",
            levelRequired = 60
        ),
        Recipe(
            outputItemId = "broad_arrows",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("arrow_shafts", 15), RecipeIngredient("feathers", 15), RecipeIngredient("rune_arrowheads", 15)),
            skillRequired = "FLETCHING",
            levelRequired = 70
        ),
        Recipe(
            outputItemId = "dragon_arrows",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("arrow_shafts", 15), RecipeIngredient("feathers", 15), RecipeIngredient("orichalcum_arrowheads", 15)),
            skillRequired = "FLETCHING",
            levelRequired = 80
        ),
        Recipe(
            outputItemId = "enchanted_bolts",
            outputQuantity = 15,
            ingredients = listOf(RecipeIngredient("bolt_frame", 15), RecipeIngredient("feathers", 15), RecipeIngredient("celestial_herb", 1)),
            skillRequired = "FLETCHING",
            levelRequired = 90
        ),
        Recipe(
            outputItemId = "attack_potion",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("guam_leaf", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 1
        ),
        Recipe(
            outputItemId = "antipoison",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("marrentill", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 3
        ),
        Recipe(
            outputItemId = "strength_potion",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("tarromin", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 5
        ),
        Recipe(
            outputItemId = "defense_potion",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("harralander", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 10
        ),
        Recipe(
            outputItemId = "restore_potion",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("harralander", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 12
        ),
        Recipe(
            outputItemId = "energy_potion",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("harralander", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 15
        ),
        Recipe(
            outputItemId = "combat_potion",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("harralander", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 20
        ),
        Recipe(
            outputItemId = "prayer_potion",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("ranarr_weed", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 22
        ),
        Recipe(
            outputItemId = "super_attack_potion",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("irit_leaf", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 30
        ),
        Recipe(
            outputItemId = "super_strength_potion",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("kwuarm", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 34
        ),
        Recipe(
            outputItemId = "super_defense_potion",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("avantoe", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 38
        ),
        Recipe(
            outputItemId = "ranging_potion",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("avantoe", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 40
        ),
        Recipe(
            outputItemId = "magic_potion",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("toadflax", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 45
        ),
        Recipe(
            outputItemId = "super_restore_potion",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("snapdragon", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 48
        ),
        Recipe(
            outputItemId = "antidote_plus",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("toadflax", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 55
        ),
        Recipe(
            outputItemId = "brew_of_vigor",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("torstol", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 60
        ),
        Recipe(
            outputItemId = "antifire_potion",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("snapdragon", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 65
        ),
        Recipe(
            outputItemId = "extreme_attack_potion",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("torstol", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 72
        ),
        Recipe(
            outputItemId = "extreme_strength_potion",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("torstol", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 78
        ),
        Recipe(
            outputItemId = "overload_potion",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("torstol", 1), RecipeIngredient("celestial_herb", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 85
        ),
        Recipe(
            outputItemId = "divine_potion",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("celestial_herb", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 92
        ),
        Recipe(
            outputItemId = "elixir_of_the_ancients",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("celestial_herb", 2), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "ALCHEMY",
            levelRequired = 99
        ),
        Recipe(
            outputItemId = "leather",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("cowhide", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 1
        ),
        Recipe(
            outputItemId = "leather_gloves",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("leather", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 1
        ),
        Recipe(
            outputItemId = "leather_boots",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("leather", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 5
        ),
        Recipe(
            outputItemId = "leather_cowl",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("leather", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 7
        ),
        Recipe(
            outputItemId = "leather_vambraces",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("leather", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 9
        ),
        Recipe(
            outputItemId = "leather_body",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("leather", 3)),
            skillRequired = "CRAFTING",
            levelRequired = 14
        ),
        Recipe(
            outputItemId = "leather_chaps",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("leather", 2)),
            skillRequired = "CRAFTING",
            levelRequired = 18
        ),
        Recipe(
            outputItemId = "studded_body",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("leather_body", 1), RecipeIngredient("iron_bar", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 22
        ),
        Recipe(
            outputItemId = "studded_chaps",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("leather_chaps", 1), RecipeIngredient("iron_bar", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 32
        ),
        Recipe(
            outputItemId = "hardleather_body",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("leather", 4)),
            skillRequired = "CRAFTING",
            levelRequired = 38
        ),
        Recipe(
            outputItemId = "snakeskin_armor",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("snake_hide", 3)),
            skillRequired = "CRAFTING",
            levelRequired = 45
        ),
        Recipe(
            outputItemId = "green_dhide_vambraces",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("green_dragonhide", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 55
        ),
        Recipe(
            outputItemId = "blue_dhide_body",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("blue_dragonhide", 3)),
            skillRequired = "CRAFTING",
            levelRequired = 60
        ),
        Recipe(
            outputItemId = "blue_dhide_chaps",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("blue_dragonhide", 2)),
            skillRequired = "CRAFTING",
            levelRequired = 65
        ),
        Recipe(
            outputItemId = "opal",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("uncut_opal", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 1
        ),
        Recipe(
            outputItemId = "jade",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("uncut_jade", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 5
        ),
        Recipe(
            outputItemId = "red_topaz",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("uncut_red_topaz", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 10
        ),
        Recipe(
            outputItemId = "sapphire",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("uncut_sapphire", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 20
        ),
        Recipe(
            outputItemId = "emerald",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("uncut_emerald", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 27
        ),
        Recipe(
            outputItemId = "ruby",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("uncut_ruby", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 34
        ),
        Recipe(
            outputItemId = "diamond",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("uncut_diamond", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 43
        ),
        Recipe(
            outputItemId = "dragonstone",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("uncut_dragonstone", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 55
        ),
        Recipe(
            outputItemId = "onyx",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("uncut_onyx", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 67
        ),
        Recipe(
            outputItemId = "zenyte",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("uncut_zenyte", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 80
        ),
        Recipe(
            outputItemId = "celestial_crystal",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("uncut_celestial_crystal", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 90
        ),
        Recipe(
            outputItemId = "gold_ring",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("gold_bar", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 5
        ),
        Recipe(
            outputItemId = "gold_necklace",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("gold_bar", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 8
        ),
        Recipe(
            outputItemId = "sapphire_ring",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("gold_ring", 1), RecipeIngredient("sapphire", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 15
        ),
        Recipe(
            outputItemId = "amulet_u",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("gold_bar", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 20
        ),
        Recipe(
            outputItemId = "emerald_amulet",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("amulet_u", 1), RecipeIngredient("emerald", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 27
        ),
        Recipe(
            outputItemId = "bowstring",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("flax", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 30
        ),
        Recipe(
            outputItemId = "ruby_ring",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("gold_ring", 1), RecipeIngredient("ruby", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 35
        ),
        Recipe(
            outputItemId = "diamond_necklace",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("gold_necklace", 1), RecipeIngredient("diamond", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 40
        ),
        Recipe(
            outputItemId = "glass_vial",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("sandstone", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 46
        ),
        Recipe(
            outputItemId = "battlestaff",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("volcanic_rock", 1), RecipeIngredient("celestial_silver", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 50
        ),
        Recipe(
            outputItemId = "dragonstone_amulet",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("amulet_u", 1), RecipeIngredient("dragonstone", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 56
        ),
        Recipe(
            outputItemId = "basket",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("bamboo", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 63
        ),
        Recipe(
            outputItemId = "onyx_ring",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("gold_ring", 1), RecipeIngredient("onyx", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 70
        ),
        Recipe(
            outputItemId = "zenyte_amulet",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("amulet_u", 1), RecipeIngredient("zenyte", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 75
        ),
        Recipe(
            outputItemId = "enchanted_circlet",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("gold_bar", 1), RecipeIngredient("dragonstone", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 80
        ),
        Recipe(
            outputItemId = "celestial_diadem",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("amulet_u", 1), RecipeIngredient("celestial_crystal", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 90
        ),
        Recipe(
            outputItemId = "cake_mix",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("flour", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "COOKING",
            levelRequired = 1
        ),
        Recipe(
            outputItemId = "pie_shell",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("flour", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "COOKING",
            levelRequired = 1
        )
    )

    fun forOutput(itemId: String): Recipe? = recipes.find { it.outputItemId == itemId }
}

// =========================================================
// CRAFTING SUCCESS CALCULATION
// =========================================================

object CraftingSuccessCalculator {
    private const val BASE_SUCCESS_PERCENT = 80.0
    private const val PERCENT_PER_LEVEL_ABOVE = 1.0

    fun successChancePercent(playerSkillLevel: Int, recipe: Recipe): Double {
        val levelsAbove = (playerSkillLevel - recipe.levelRequired).coerceAtLeast(0)
        val chance = BASE_SUCCESS_PERCENT + (levelsAbove * PERCENT_PER_LEVEL_ABOVE)
        return chance.coerceAtMost(100.0)
    }

    fun rollSuccess(playerSkillLevel: Int, recipe: Recipe): Boolean {
        val chance = successChancePercent(playerSkillLevel, recipe)
        return Random.nextDouble(0.0, 100.0) < chance
    }
}

// =========================================================
// CRAFTING TIER CURVE
// Decoupled from ActionCatalog on purpose -- Recipe.levelRequired is
// the sole source of truth for crafting XP/time, reusing the same
// tier ladder ActionCatalog already uses elsewhere in the game.
// =========================================================

object CraftingTierCurve {
    private val tierLevels = intArrayOf(1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 99)
    private val tierXp = intArrayOf(10, 19, 30, 41, 52, 63, 74, 85, 96, 107, 118, 129, 140, 151, 162, 173, 184, 195, 206, 226)
    private val tierSeconds = longArrayOf(3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6)

    private fun tierIndexFor(level: Int): Int {
        var index = 0
        for (i in tierLevels.indices) {
            if (level >= tierLevels[i]) index = i else break
        }
        return index
    }

    fun xpFor(level: Int): Int = tierXp[tierIndexFor(level)]
    fun secondsFor(level: Int): Long = tierSeconds[tierIndexFor(level)]
}

// =========================================================
// INVENTORY
// (ServiceResult now comes from SharedTypes.kt.)
// =========================================================

data class InventorySlotEntry(val itemId: String, val quantity: Int, val lastAcquiredAtMillis: Long = System.currentTimeMillis())

class Inventory(
    var maxSlots: Int = 100,
    private val entries: MutableMap<String, InventorySlotEntry> = mutableMapOf(),
    private val equipped: MutableMap<EquipSlot, String> = mutableMapOf(),
    var selectedFoodId: String? = null,
    var selectedPotionId: String? = null,
    var potionTimerRemainingSeconds: Int = 0,
    var autoHealThresholdPercent: Int = 30,
    var autoFleeThresholdPercent: Int = 10,
    var selectedPrayerId: String? = null,
    var trainingSkillId: String? = null
) {
    fun usedSlots(): Int = entries.size

    fun addItem(itemId: String, quantity: Int): ServiceResult<Unit> {
        val definition = ItemCatalog.find(itemId) ?: return ServiceResult.Failure("Unknown item.")
        if (quantity <= 0) return ServiceResult.Failure("Quantity must be positive.")

        val existing = entries[itemId]
        if (existing != null) {
            // Restocking an existing stack counts as "acquired now" too, so
            // "most recent" sorting reflects the last time you got more of
            // something, not just when you first ever picked it up.
            entries[itemId] = existing.copy(quantity = existing.quantity + quantity, lastAcquiredAtMillis = System.currentTimeMillis())
            return ServiceResult.Success(Unit)
        }

        if (usedSlots() >= maxSlots) return ServiceResult.Failure("Inventory is full.")
        entries[itemId] = InventorySlotEntry(itemId, quantity)
        return ServiceResult.Success(Unit)
    }

    fun removeItem(itemId: String, quantity: Int): ServiceResult<Unit> {
        val entry = entries[itemId] ?: return ServiceResult.Failure("Item not in inventory.")
        if (entry.quantity < quantity) return ServiceResult.Failure("Not enough quantity to remove.")

        val newQuantity = entry.quantity - quantity
        if (newQuantity <= 0) {
            entries.remove(itemId)
        } else {
            entries[itemId] = entry.copy(quantity = newQuantity)
        }
        return ServiceResult.Success(Unit)
    }

    fun quantityOf(itemId: String): Int = entries[itemId]?.quantity ?: 0

    fun expandCapacity(additionalSlots: Int) {
        maxSlots += additionalSlots
    }

    // ---------------- Equipping ----------------

    fun equippedItemIn(slot: EquipSlot): String? = equipped[slot]

    fun equip(itemId: String, playerLevel: Int, playerSkillLevels: Map<String, Int>, canChangeSlot: (EquipmentSlot) -> Boolean): ServiceResult<Unit> {
        val definition = ItemCatalog.find(itemId) ?: return ServiceResult.Failure("Unknown item.")
        val slot = definition.equipSlot ?: return ServiceResult.Failure("This item cannot be equipped.")

        val lockCategory = SlotLockMapping.lockCategoryFor(slot)
        if (!canChangeSlot(lockCategory)) {
            return ServiceResult.Failure("Cannot change " + lockCategory.name + " slot right now.")
        }
        if (quantityOf(itemId) <= 0) return ServiceResult.Failure("Item not in inventory.")
        if (playerLevel < definition.levelRequired) {
            return ServiceResult.Failure("Requires level " + definition.levelRequired + ".")
        }
        definition.skillRequired?.let { skillId ->
            val playerSkillLevel = playerSkillLevels[skillId] ?: 0
            if (playerSkillLevel < definition.levelRequired) {
                return ServiceResult.Failure("Requires " + skillId + " level " + definition.levelRequired + ".")
            }
        }

        equipped[slot]?.let { previousItemId ->
            addItem(previousItemId, 1)
        }

        removeItem(itemId, 1)
        equipped[slot] = itemId
        return ServiceResult.Success(Unit)
    }

    fun unequip(slot: EquipSlot, canChangeSlot: (EquipmentSlot) -> Boolean): ServiceResult<Unit> {
        val lockCategory = SlotLockMapping.lockCategoryFor(slot)
        if (!canChangeSlot(lockCategory)) {
            return ServiceResult.Failure("Cannot change " + lockCategory.name + " slot right now.")
        }
        val itemId = equipped[slot] ?: return ServiceResult.Failure("Nothing equipped in that slot.")

        addItem(itemId, 1)
        equipped.remove(slot)
        return ServiceResult.Success(Unit)
    }

    fun allEquipped(): Map<EquipSlot, String> = equipped.toMap()

    fun allItems(): List<InventorySlotEntry> = entries.values.toList()

    fun restoreItem(itemId: String, quantity: Int, lastAcquiredAtMillis: Long = System.currentTimeMillis()) {
        entries[itemId] = InventorySlotEntry(itemId, quantity, lastAcquiredAtMillis)
    }

    fun restoreEquipped(slot: EquipSlot, itemId: String) {
        equipped[slot] = itemId
    }

    // ---------------- Food / Potion selection ----------------

    fun selectFood(itemId: String?): ServiceResult<Unit> {
        if (itemId != null) {
            val definition = ItemCatalog.find(itemId) ?: return ServiceResult.Failure("Unknown item.")
            if (definition.consumableType != ConsumableType.FOOD) return ServiceResult.Failure("Not a food item.")
        }
        selectedFoodId = itemId
        return ServiceResult.Success(Unit)
    }

    fun selectPotion(itemId: String?): ServiceResult<Unit> {
        if (itemId != null) {
            val definition = ItemCatalog.find(itemId) ?: return ServiceResult.Failure("Unknown item.")
            if (definition.consumableType != ConsumableType.POTION) return ServiceResult.Failure("Not a potion item.")
        }
        selectedPotionId = itemId
        potionTimerRemainingSeconds = 0
        return ServiceResult.Success(Unit)
    }

    fun selectPrayer(prayerId: String?): ServiceResult<Unit> {
        if (prayerId != null && PrayerCatalog.none { it.id == prayerId }) {
            return ServiceResult.Failure("Unknown prayer.")
        }
        selectedPrayerId = prayerId
        return ServiceResult.Success(Unit)
    }

    fun consumeSelectedFood(): ItemDefinition? {
        val foodId = selectedFoodId ?: return null
        val definition = ItemCatalog.find(foodId) ?: return null
        if (quantityOf(foodId) <= 0) return null
        removeItem(foodId, 1)
        return definition
    }

    fun consumeSelectedPotion(): ItemDefinition? {
        val potionId = selectedPotionId ?: return null
        val definition = ItemCatalog.find(potionId) ?: return null
        if (quantityOf(potionId) <= 0) return null
        removeItem(potionId, 1)
        return definition
    }
}

// =========================================================
// CRAFTING SERVICE
// =========================================================

class CraftingResult(val succeeded: Boolean, val itemId: String, val quantityProduced: Int)

class CraftingService {
    fun craftOnce(inventory: Inventory, itemId: String, playerSkillLevel: Int): ServiceResult<CraftingResult> {
        val recipe = RecipeCatalog.forOutput(itemId) ?: return ServiceResult.Failure("No recipe for this item.")
        if (playerSkillLevel < recipe.levelRequired) {
            return ServiceResult.Failure("Requires " + recipe.skillRequired + " level " + recipe.levelRequired + ".")
        }

        for (ingredient in recipe.ingredients) {
            if (inventory.quantityOf(ingredient.itemId) < ingredient.quantity) {
                return ServiceResult.Failure("Missing materials: " + ingredient.itemId)
            }
        }

        for (ingredient in recipe.ingredients) {
            inventory.removeItem(ingredient.itemId, ingredient.quantity)
        }

        val succeeded = CraftingSuccessCalculator.rollSuccess(playerSkillLevel, recipe)
        if (succeeded) {
            inventory.addItem(recipe.outputItemId, recipe.outputQuantity)
        }
        // Materials are consumed even on failure, per your confirmed design decision.

        return ServiceResult.Success(CraftingResult(succeeded, itemId, if (succeeded) recipe.outputQuantity else 0))
    }
}

// =========================================================
// INVENTORY SERVICE
// =========================================================

data class InventorySlotExport(val characterId: String, val itemId: String, val quantity: Int, val lastAcquiredAtMillis: Long = System.currentTimeMillis())
data class EquippedSlotExport(val characterId: String, val slot: String, val itemId: String)
data class LoadoutSettingsExport(
    val characterId: String,
    val selectedFoodId: String?,
    val selectedPotionId: String?,
    val potionTimerRemainingSeconds: Int,
    val autoHealThresholdPercent: Int,
    val autoFleeThresholdPercent: Int,
    val selectedPrayerId: String? = null,
    val trainingSkillId: String? = null
)

class InventoryService {
    private val inventories: MutableMap<String, Inventory> = mutableMapOf()

    fun inventoryFor(characterId: String): Inventory =
        inventories.getOrPut(characterId) { Inventory() }

    fun exportAllItems(): List<InventorySlotExport> = inventories.flatMap { (characterId, inv) ->
        inv.allItems().map { InventorySlotExport(characterId, it.itemId, it.quantity, it.lastAcquiredAtMillis) }
    }

    fun exportAllEquipped(): List<EquippedSlotExport> = inventories.flatMap { (characterId, inv) ->
        inv.allEquipped().map { (slot, itemId) -> EquippedSlotExport(characterId, slot.name, itemId) }
    }

    fun restoreItem(export: InventorySlotExport) {
        inventoryFor(export.characterId).restoreItem(export.itemId, export.quantity, export.lastAcquiredAtMillis)
    }

    fun restoreEquipped(export: EquippedSlotExport) {
        inventoryFor(export.characterId).restoreEquipped(EquipSlot.valueOf(export.slot), export.itemId)
    }

    fun exportAllLoadoutSettings(): List<LoadoutSettingsExport> = inventories.map { (characterId, inv) ->
        LoadoutSettingsExport(
            characterId, inv.selectedFoodId, inv.selectedPotionId, inv.potionTimerRemainingSeconds,
            inv.autoHealThresholdPercent, inv.autoFleeThresholdPercent, inv.selectedPrayerId, inv.trainingSkillId
        )
    }

    fun restoreLoadoutSettings(export: LoadoutSettingsExport) {
        val inv = inventoryFor(export.characterId)
        inv.selectedFoodId = export.selectedFoodId
        inv.selectedPotionId = export.selectedPotionId
        inv.potionTimerRemainingSeconds = export.potionTimerRemainingSeconds
        inv.autoHealThresholdPercent = export.autoHealThresholdPercent
        inv.autoFleeThresholdPercent = export.autoFleeThresholdPercent
        inv.selectedPrayerId = export.selectedPrayerId
        inv.trainingSkillId = export.trainingSkillId
    }
}
