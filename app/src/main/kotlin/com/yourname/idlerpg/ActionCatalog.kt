package com.yourname.idlerpg

// =========================================================
// ACTION CATALOG
// Defines what a character earns per completed skilling action:
// how much XP, and how long the action takes. Keyed by skill +
// item (e.g. MINING + iron_ore).
// =========================================================

data class SkillActionDefinition(
    val skillType: SkillType,
    val itemId: String,
    val displayName: String,
    val xpPerAction: Long,
    val secondsPerAction: Long,
    val levelRequired: Int = 1
)

object ActionCatalog {
    private val actions = listOf(
        SkillActionDefinition(SkillType.MINING, "copper_ore", "Mine Copper Ore", xpPerAction = 8, secondsPerAction = 3),
        SkillActionDefinition(SkillType.MINING, "iron_ore", "Mine Iron Ore", xpPerAction = 15, secondsPerAction = 4, levelRequired = 10),
        SkillActionDefinition(SkillType.MINING, "mithril_ore", "Mine Mithril Ore", xpPerAction = 35, secondsPerAction = 6, levelRequired = 25),

        SkillActionDefinition(SkillType.WOODCUTTING, "oak_log", "Chop Oak Log", xpPerAction = 10, secondsPerAction = 3),

        SkillActionDefinition(SkillType.FISHING, "trout", "Fish Trout", xpPerAction = 10, secondsPerAction = 4),

        SkillActionDefinition(SkillType.SMITHING, "steel_bar", "Smelt Steel Bar", xpPerAction = 20, secondsPerAction = 5),

        SkillActionDefinition(SkillType.COOKING, "cooked_trout", "Cook Trout", xpPerAction = 12, secondsPerAction = 3)
    )

    fun find(skillType: SkillType, itemId: String): SkillActionDefinition? =
        actions.find { it.skillType == skillType && it.itemId == itemId }

    fun allFor(skillType: SkillType): List<SkillActionDefinition> =
        actions.filter { it.skillType == skillType }
}
