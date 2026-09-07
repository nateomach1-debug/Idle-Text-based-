package com.yourname.idlerpg

// Unified UI-facing row that every leaderboard category maps into, so
// LeaderboardsScreen itself never needs per-category branching.
data class LeaderboardRow(
    val rank: Int,
    val name: String,
    val valueLabel: String
)

// All leaderboard categories shown in the category picker. The 16 skill
// entries deliberately match SkillType.name exactly, so category.name can
// be passed straight into fetch_skill_leaderboard without a lookup table.
enum class LeaderboardCategory(val label: String) {
    TOTAL_LEVEL("Total Level"),
    COMBAT_LEVEL("Combat Level"),
    GUILDS("Guilds"),
    MINING("Mining"),
    WOODCUTTING("Woodcutting"),
    FISHING("Fishing"),
    FARMING("Farming"),
    THIEVING("Thieving"),
    SMITHING("Smithing"),
    COOKING("Cooking"),
    CRAFTING("Crafting"),
    FLETCHING("Fletching"),
    ALCHEMY("Alchemy"),
    MAGIC("Magic"),
    ATTACK("Attack"),
    STRENGTH("Strength"),
    DEFENSE("Defense"),
    PRAYER("Prayer"),
    ARCHERY("Archery");

    val isSkillCategory: Boolean
        get() = this != TOTAL_LEVEL && this != COMBAT_LEVEL && this != GUILDS
}
