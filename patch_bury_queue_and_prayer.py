def apply(content, old, new, label):
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"FAILED [{label}]: expected 1 match, found {count}")
    return content.replace(old, new, 1)

# ---------- GameViewModel.kt ----------
GVM_PATH = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(GVM_PATH, "r", encoding="utf-8") as f:
    gvm = f.read()

gvm = apply(gvm,
"""    private fun eventPerMemberQuantityFor(rarity: Rarity): Int = when (rarity) {
        Rarity.COMMON -> 40
        Rarity.UNCOMMON -> 25
        Rarity.RARE -> 15
        Rarity.EPIC -> 8
        Rarity.LEGENDARY -> 3
    }""",
"""    // x10 from the original first-pass numbers, per explicit user request.
    private fun eventPerMemberQuantityFor(rarity: Rarity): Int = when (rarity) {
        Rarity.COMMON -> 400
        Rarity.UNCOMMON -> 250
        Rarity.RARE -> 150
        Rarity.EPIC -> 80
        Rarity.LEGENDARY -> 30
    }""",
    "eventPerMemberQuantityFor: x10"
)

gvm = apply(gvm,
"""    private fun eventGuildXpRewardPerMilestoneFor(rarity: Rarity): Long = when (rarity) {
        Rarity.COMMON -> 25L
        Rarity.UNCOMMON -> 50L
        Rarity.RARE -> 100L
        Rarity.EPIC -> 200L
        Rarity.LEGENDARY -> 400L
    }""",
"""    // x5 from the original first-pass numbers, per explicit user request.
    private fun eventGuildXpRewardPerMilestoneFor(rarity: Rarity): Long = when (rarity) {
        Rarity.COMMON -> 125L
        Rarity.UNCOMMON -> 250L
        Rarity.RARE -> 500L
        Rarity.EPIC -> 1000L
        Rarity.LEGENDARY -> 2000L
    }""",
    "eventGuildXpRewardPerMilestoneFor: x5"
)

with open(GVM_PATH, "w", encoding="utf-8") as f:
    f.write(gvm)

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
    @SerialName("guild_level") val guildLevel: Int = 1,
    @SerialName("guild_xp") val guildXp: Long = 0
)""",
"""private data class GuildRow(
    val id: String,
    val name: String,
    val tier: Int,
    @SerialName("last_failed_vote_at") val lastFailedVoteAt: String? = null,
    @SerialName("guild_level") val guildLevel: Int = 1,
    @SerialName("guild_xp") val guildXp: Long = 0,
    @SerialName("guild_coins") val guildCoins: Long = 0
)""",
    "GuildRow: add guildCoins"
)

sgr = apply(sgr,
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
"""            return GuildHomeState(
                guildName = guild.name,
                activeEvent = activeEvent,
                activeVote = activeVote,
                tier = guild.tier,
                guildLevel = guild.guildLevel,
                guildXp = guild.guildXp,
                guildCoins = guild.guildCoins,
                activeBonusPercent = 0.0,  // Phase 2 adds active bonus tracking
                members = members,
                quests = emptyList(),  // no backend concept for this yet - not fabricating fake data
                viewerRole = viewerRole
            )""",
    "fetchGuildHome: pass guildCoins through"
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
    val guildXp: Long,
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
    val guildCoins: Long,
    val activeBonusPercent: Double,
    val members: List<GuildMemberSummary>,
    val quests: List<GuildQuestSummary>,
    val viewerRole: GuildMemberRole
)""",
    "GuildHomeState: add guildCoins"
)

ghs = apply(ghs,
"""        GuildLevelCard(state.guildLevel, state.guildXp, xpRequiredForNextLevel)""",
"""        GuildLevelCard(state.guildLevel, state.guildXp, xpRequiredForNextLevel, state.guildCoins)""",
    "pass guildCoins to GuildLevelCard call site"
)

ghs = apply(ghs,
"""@Composable
private fun GuildLevelCard(level: Int, xp: Long, xpRequiredForNextLevel: Long) {
    val fraction = if (xpRequiredForNextLevel > 0) (xp.toFloat() / xpRequiredForNextLevel.toFloat()).coerceIn(0f, 1f) else 0f
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(14.dp)
    ) {
        Text(text = "Guild Level " + level, style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(6.dp))
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(8.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(MaterialTheme.colorScheme.background)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(fraction)
                    .fillMaxHeight()
                    .clip(RoundedCornerShape(4.dp))
                    .background(MaterialTheme.colorScheme.primary)
            )
        }
        Spacer(modifier = Modifier.height(4.dp))
        Text(text = "%,d / %,d XP".format(xp, xpRequiredForNextLevel), style = MaterialTheme.typography.labelSmall)
    }
}""",
"""@Composable
private fun GuildLevelCard(level: Int, xp: Long, xpRequiredForNextLevel: Long, guildCoins: Long) {
    val fraction = if (xpRequiredForNextLevel > 0) (xp.toFloat() / xpRequiredForNextLevel.toFloat()).coerceIn(0f, 1f) else 0f
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(14.dp)
    ) {
        Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
            Text(text = "Guild Level " + level, style = MaterialTheme.typography.titleMedium)
            Text(text = "%,d Guild Coins".format(guildCoins), style = MaterialTheme.typography.titleMedium)
        }
        Spacer(modifier = Modifier.height(6.dp))
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(8.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(MaterialTheme.colorScheme.background)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(fraction)
                    .fillMaxHeight()
                    .clip(RoundedCornerShape(4.dp))
                    .background(MaterialTheme.colorScheme.primary)
            )
        }
        Spacer(modifier = Modifier.height(4.dp))
        Text(text = "%,d / %,d XP".format(xp, xpRequiredForNextLevel), style = MaterialTheme.typography.labelSmall)
    }
}""",
    "GuildLevelCard: display guild coins"
)

with open(GHS_PATH, "w", encoding="utf-8") as f:
    f.write(ghs)

print("All edits applied successfully.")
