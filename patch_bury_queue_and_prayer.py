def apply(content, old, new, label):
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"FAILED [{label}]: expected 1 match, found {count}")
    return content.replace(old, new, 1)

# ---------- SupabaseGuildRepository.kt ----------
SGR_PATH = "app/src/main/kotlin/com/yourname/idlerpg/SupabaseGuildRepository.kt"
with open(SGR_PATH, "r", encoding="utf-8") as f:
    sgr = f.read()

sgr = apply(sgr,
"""private data class GuildRow(
    val id: String,
    val name: String,
    val tier: Int,
    @SerialName("last_failed_vote_at") val lastFailedVoteAt: String? = null,
    @SerialName("guild_level") val guildLevel: Int = 1
)""",
"""private data class GuildRow(
    val id: String,
    val name: String,
    val tier: Int,
    @SerialName("last_failed_vote_at") val lastFailedVoteAt: String? = null,
    @SerialName("guild_level") val guildLevel: Int = 1,
    @SerialName("guild_xp") val guildXp: Long = 0
)""",
    "GuildRow: add guildXp"
)

sgr = apply(sgr,
"""            return GuildHomeState(
                guildName = guild.name,
                activeEvent = activeEvent,
                activeVote = activeVote,
                tier = guild.tier,
                guildLevel = guild.guildLevel,
                activeBonusPercent = 0.0,  // Phase 2 adds active bonus tracking
                members = members,
                quests = emptyList(),  // no backend concept for this yet - not fabricating fake data
                viewerRole = viewerRole
            )""",
"""            return GuildHomeState(
                guildName = guild.name,
                activeEvent = activeEvent,
                activeVote = activeVote,
                tier = guild.tier,
                guildLevel = guild.guildLevel,
                guildXp = guild.guildXp,
                activeBonusPercent = 0.0,  // Phase 2 adds active bonus tracking
                members = members,
                quests = emptyList(),  // no backend concept for this yet - not fabricating fake data
                viewerRole = viewerRole
            )""",
    "fetchGuildHome: pass guildXp through"
)

sgr = apply(sgr,
"""    suspend fun startGuildEvent(
        guildId: String,
        actingCharacterId: String,
        displayName: String,
        itemId: String,
        skillName: String,
        requiredQuantity: Int,
        guildCoinRewardPerMilestone: Long
    ): Result<String> = runCatching {
        client.postgrest.rpc("start_guild_event", buildJsonObject {
            put("p_guild_id", guildId)
            put("p_acting_character_id", actingCharacterId)
            put("p_display_name", displayName)
            put("p_item_id", itemId)
            put("p_skill_name", skillName)
            put("p_required_quantity", requiredQuantity)
            put("p_guild_coin_reward_per_milestone", guildCoinRewardPerMilestone)
        }).decodeAs<String>()
    }""",
"""    suspend fun startGuildEvent(
        guildId: String,
        actingCharacterId: String,
        displayName: String,
        itemId: String,
        skillName: String,
        requiredQuantity: Int,
        guildCoinRewardPerMilestone: Long,
        guildXpRewardPerMilestone: Long
    ): Result<String> = runCatching {
        client.postgrest.rpc("start_guild_event", buildJsonObject {
            put("p_guild_id", guildId)
            put("p_acting_character_id", actingCharacterId)
            put("p_display_name", displayName)
            put("p_item_id", itemId)
            put("p_skill_name", skillName)
            put("p_required_quantity", requiredQuantity)
            put("p_guild_coin_reward_per_milestone", guildCoinRewardPerMilestone)
            put("p_guild_xp_reward_per_milestone", guildXpRewardPerMilestone)
        }).decodeAs<String>()
    }""",
    "startGuildEvent: add guildXpRewardPerMilestone param"
)

with open(SGR_PATH, "w", encoding="utf-8") as f:
    f.write(sgr)

# ---------- GuildHomeScreen.kt ----------
GHS_PATH = "app/src/main/kotlin/com/yourname/idlerpg/GuildHomeScreen.kt"
with open(GHS_PATH, "r", encoding="utf-8") as f:
    ghs = f.read()

ghs = apply(ghs,
"""data class GuildHomeState(
    val guildName: String,
    val activeEvent: GuildEventSummary?,
    val activeVote: GuildVoteSummary?,
    val tier: Int,
    val guildLevel: Int,
    val activeBonusPercent: Double,
    val members: List<GuildMemberSummary>,
    val quests: List<GuildQuestSummary>,
    val viewerRole: GuildMemberRole
)""",
"""data class GuildHomeState(
    val guildName: String,
    val activeEvent: GuildEventSummary?,
    val activeVote: GuildVoteSummary?,
    val tier: Int,
    val guildLevel: Int,
    val guildXp: Long,
    val activeBonusPercent: Double,
    val members: List<GuildMemberSummary>,
    val quests: List<GuildQuestSummary>,
    val viewerRole: GuildMemberRole
)""",
    "GuildHomeState: add guildXp"
)

with open(GHS_PATH, "w", encoding="utf-8") as f:
    f.write(ghs)

# ---------- GameViewModel.kt ----------
GVM_PATH = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(GVM_PATH, "r", encoding="utf-8") as f:
    gvm = f.read()

gvm = apply(gvm,
"""    private fun eventGuildCoinRewardPerMilestoneFor(rarity: Rarity): Long = when (rarity) {
        Rarity.COMMON -> 100L
        Rarity.UNCOMMON -> 200L
        Rarity.RARE -> 400L
        Rarity.EPIC -> 800L
        Rarity.LEGENDARY -> 1600L
    }""",
"""    private fun eventGuildCoinRewardPerMilestoneFor(rarity: Rarity): Long = when (rarity) {
        Rarity.COMMON -> 100L
        Rarity.UNCOMMON -> 200L
        Rarity.RARE -> 400L
        Rarity.EPIC -> 800L
        Rarity.LEGENDARY -> 1600L
    }

    private fun eventGuildXpRewardPerMilestoneFor(rarity: Rarity): Long = when (rarity) {
        Rarity.COMMON -> 25L
        Rarity.UNCOMMON -> 50L
        Rarity.RARE -> 100L
        Rarity.EPIC -> 200L
        Rarity.LEGENDARY -> 400L
    }

    // Must match the SQL curve in contribute_to_guild_event() - level L needs
    // 1000*L XP to advance to L+1. Exposed here so the UI can show a progress
    // bar without a network round trip.
    fun guildXpRequiredForLevel(level: Int): Long = 1000L * level""",
    "add eventGuildXpRewardPerMilestoneFor + guildXpRequiredForLevel"
)

gvm = apply(gvm,
"""        val requiredQuantity = eventPerMemberQuantityFor(item.rarity) * memberCount
        val rewardPerMilestone = eventGuildCoinRewardPerMilestoneFor(item.rarity)
        val displayName = item.name + " Drive"

        viewModelScope.launch {
            val result = SupabaseGuildRepository.startGuildEvent(
                guildId = guildId,
                actingCharacterId = actingCharacterId,
                displayName = displayName,
                itemId = item.id,
                skillName = item.skillRequired ?: "",
                requiredQuantity = requiredQuantity,
                guildCoinRewardPerMilestone = rewardPerMilestone
            )""",
"""        val requiredQuantity = eventPerMemberQuantityFor(item.rarity) * memberCount
        val rewardPerMilestone = eventGuildCoinRewardPerMilestoneFor(item.rarity)
        val xpRewardPerMilestone = eventGuildXpRewardPerMilestoneFor(item.rarity)
        val displayName = item.name + " Drive"

        viewModelScope.launch {
            val result = SupabaseGuildRepository.startGuildEvent(
                guildId = guildId,
                actingCharacterId = actingCharacterId,
                displayName = displayName,
                itemId = item.id,
                skillName = item.skillRequired ?: "",
                requiredQuantity = requiredQuantity,
                guildCoinRewardPerMilestone = rewardPerMilestone,
                guildXpRewardPerMilestone = xpRewardPerMilestone
            )""",
    "startGuildEvent: pass xpRewardPerMilestone"
)

with open(GVM_PATH, "w", encoding="utf-8") as f:
    f.write(gvm)

print("All edits applied successfully.")
