package com.yourname.idlerpg

// =========================================================
// CHAT COSMETICS CATALOG - TITLES + BADGES
// Titles show as "[Title] " before a character's name in chat.
//   - Earned titles: "Master <Skill>" (reach level 99) and
//     "Master <Monster> Slayer" (defeat 10,000 of that monster).
//     One per skill / per monster in ZoneCatalog - new monsters
//     get their Slayer title automatically.
//   - Gem titles: extra titles bought with Gems.
// Badges are name-only visual effects layered over the viewer's
// normal text effect. ALL badges cost Gems.
// Ownership and equipped state live server-side (see the
// character_owned_cosmetics / character_cosmetics tables) so other
// players see them; this file only supplies display data and the
// earn rules the client checks before claiming an earned title.
// Gem prices here MUST match the chat_cosmetics seed rows in
// cosmetics_schema.sql - the server is the source of truth for
// what a purchase actually charges.
// =========================================================

enum class CosmeticKind { TITLE, BADGE }

enum class BadgeEffect {
    RAINBOW, GILDED, INFERNO, FROSTBITE, NEON_PULSE,
    AURORA, STORMCALL, BLOOD_MOON, TOXIC, VOID
}

data class ChatCosmetic(
    val id: String,
    val kind: CosmeticKind,
    val displayName: String,
    val gemCost: Long = 0L,
    val colorArgb: Long = 0xFFFFFFFFL,
    val badgeEffect: BadgeEffect? = null,
    val earnedSkill: SkillType? = null,
    val earnedMonsterId: String? = null
) {
    val isEarned: Boolean
        get() = earnedSkill != null || earnedMonsterId != null
}

object ChatCosmeticCatalog {
    const val MASTER_SKILL_LEVEL = 99
    const val SLAYER_KILLS_REQUIRED = 10000L

    private fun skillTitleColor(skill: SkillType): Long = when (skill) {
        SkillType.MINING -> 0xFFB0B4BCL
        SkillType.WOODCUTTING -> 0xFF7FB069L
        SkillType.FISHING -> 0xFF5DA9E9L
        SkillType.FARMING -> 0xFFD4B95EL
        SkillType.THIEVING -> 0xFFA678D6L
        SkillType.SMITHING -> 0xFFE8873AL
        SkillType.COOKING -> 0xFFE0674FL
        SkillType.CRAFTING -> 0xFFB18AD8L
        SkillType.FLETCHING -> 0xFF9BCB6BL
        SkillType.ALCHEMY -> 0xFF4FD1A5L
        SkillType.MAGIC -> 0xFF6EA8FFL
        SkillType.ATTACK -> 0xFFE05252L
        SkillType.STRENGTH -> 0xFFF08A3CL
        SkillType.DEFENSE -> 0xFF6FA3D9L
        SkillType.PRAYER -> 0xFFF3E9B5L
        SkillType.ARCHERY -> 0xFF8FCB5AL
    }

    // One "Master <Skill>" title per skill, earned at level 99.
    val skillTitles: List<ChatCosmetic> = SkillType.values().map { skill ->
        ChatCosmetic(
            id = "title_master_" + skill.name.lowercase(),
            kind = CosmeticKind.TITLE,
            displayName = "Master " + skill.name.lowercase().replaceFirstChar { it.uppercase() },
            colorArgb = skillTitleColor(skill),
            earnedSkill = skill
        )
    }

    // One "Master <Monster> Slayer" title per monster currently in ZoneCatalog.
    val slayerTitles: List<ChatCosmetic> by lazy {
        ZoneCatalog.zones.flatMap { it.monsters }.map { monster ->
            ChatCosmetic(
                id = "title_slayer_" + monster.id,
                kind = CosmeticKind.TITLE,
                displayName = "Master " + monster.name + " Slayer",
                colorArgb = 0xFFFF6B4AL,
                earnedMonsterId = monster.id
            )
        }
    }

    // Titles bought with Gems.
    val gemTitles: List<ChatCosmetic> = listOf(
        ChatCosmetic(id = "title_wanderer", kind = CosmeticKind.TITLE, displayName = "Wanderer", gemCost = 100L, colorArgb = 0xFFB8C4D0L),
        ChatCosmetic(id = "title_adventurer", kind = CosmeticKind.TITLE, displayName = "Adventurer", gemCost = 100L, colorArgb = 0xFF9ED08AL),
        ChatCosmetic(id = "title_ranger", kind = CosmeticKind.TITLE, displayName = "Ranger", gemCost = 200L, colorArgb = 0xFF6FCF97L),
        ChatCosmetic(id = "title_ironclad", kind = CosmeticKind.TITLE, displayName = "Ironclad", gemCost = 250L, colorArgb = 0xFFAEB6BFL),
        ChatCosmetic(id = "title_sage", kind = CosmeticKind.TITLE, displayName = "Sage", gemCost = 250L, colorArgb = 0xFF8AB4F8L),
        ChatCosmetic(id = "title_champion", kind = CosmeticKind.TITLE, displayName = "Champion", gemCost = 300L, colorArgb = 0xFFF2C94CL),
        ChatCosmetic(id = "title_shadowwalker", kind = CosmeticKind.TITLE, displayName = "Shadowwalker", gemCost = 300L, colorArgb = 0xFFB388FFL),
        ChatCosmetic(id = "title_dreadnought", kind = CosmeticKind.TITLE, displayName = "Dreadnought", gemCost = 350L, colorArgb = 0xFFE57373L),
        ChatCosmetic(id = "title_stormbringer", kind = CosmeticKind.TITLE, displayName = "Stormbringer", gemCost = 350L, colorArgb = 0xFF64B5F6L),
        ChatCosmetic(id = "title_legend", kind = CosmeticKind.TITLE, displayName = "Legend", gemCost = 500L, colorArgb = 0xFFFFD54FL),
        ChatCosmetic(id = "title_grand_champion", kind = CosmeticKind.TITLE, displayName = "Grand Champion", gemCost = 800L, colorArgb = 0xFFFFA726L),
        ChatCosmetic(id = "title_sovereign", kind = CosmeticKind.TITLE, displayName = "Sovereign", gemCost = 1000L, colorArgb = 0xFFFF80ABL)
    )

    // Name effects. Every badge costs Gems.
    val badges: List<ChatCosmetic> = listOf(
        ChatCosmetic(id = "badge_neon_pulse", kind = CosmeticKind.BADGE, displayName = "Neon Pulse", gemCost = 200L, colorArgb = 0xFF00F5FFL, badgeEffect = BadgeEffect.NEON_PULSE),
        ChatCosmetic(id = "badge_toxic", kind = CosmeticKind.BADGE, displayName = "Toxic", gemCost = 200L, colorArgb = 0xFF7CFF3AL, badgeEffect = BadgeEffect.TOXIC),
        ChatCosmetic(id = "badge_frostbite", kind = CosmeticKind.BADGE, displayName = "Frostbite", gemCost = 300L, colorArgb = 0xFF9BE7FFL, badgeEffect = BadgeEffect.FROSTBITE),
        ChatCosmetic(id = "badge_gilded", kind = CosmeticKind.BADGE, displayName = "Gilded", gemCost = 300L, colorArgb = 0xFFFFD54FL, badgeEffect = BadgeEffect.GILDED),
        ChatCosmetic(id = "badge_inferno", kind = CosmeticKind.BADGE, displayName = "Inferno", gemCost = 350L, colorArgb = 0xFFFF7A1AL, badgeEffect = BadgeEffect.INFERNO),
        ChatCosmetic(id = "badge_blood_moon", kind = CosmeticKind.BADGE, displayName = "Blood Moon", gemCost = 350L, colorArgb = 0xFFE01B1BL, badgeEffect = BadgeEffect.BLOOD_MOON),
        ChatCosmetic(id = "badge_void", kind = CosmeticKind.BADGE, displayName = "Void", gemCost = 400L, colorArgb = 0xFFB14CFFL, badgeEffect = BadgeEffect.VOID),
        ChatCosmetic(id = "badge_aurora", kind = CosmeticKind.BADGE, displayName = "Aurora", gemCost = 450L, colorArgb = 0xFF00FFA3L, badgeEffect = BadgeEffect.AURORA),
        ChatCosmetic(id = "badge_stormcall", kind = CosmeticKind.BADGE, displayName = "Stormcall", gemCost = 450L, colorArgb = 0xFF8EA8FFL, badgeEffect = BadgeEffect.STORMCALL),
        ChatCosmetic(id = "badge_rainbow", kind = CosmeticKind.BADGE, displayName = "Rainbow", gemCost = 500L, colorArgb = 0xFFFF4D4DL, badgeEffect = BadgeEffect.RAINBOW)
    )

    val earnedTitles: List<ChatCosmetic>
        get() = skillTitles + slayerTitles

    val allTitles: List<ChatCosmetic>
        get() = earnedTitles + gemTitles

    private val byId: Map<String, ChatCosmetic> by lazy {
        (skillTitles + slayerTitles + gemTitles + badges).associateBy { it.id }
    }

    fun find(id: String): ChatCosmetic? = byId[id]

    fun monsterName(monsterId: String): String =
        ZoneCatalog.zones.flatMap { it.monsters }.find { it.id == monsterId }?.name ?: monsterId
}
