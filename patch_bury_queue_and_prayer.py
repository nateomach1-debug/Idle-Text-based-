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
    @SerialName("last_failed_vote_at") val lastFailedVoteAt: String? = null
)""",
"""private data class GuildRow(
    val id: String,
    val name: String,
    val tier: Int,
    @SerialName("last_failed_vote_at") val lastFailedVoteAt: String? = null,
    @SerialName("guild_level") val guildLevel: Int = 1
)""",
    "GuildRow: add guildLevel"
)

sgr = apply(sgr,
"""            return GuildHomeState(
                guildName = guild.name,
                activeEvent = activeEvent,
                activeVote = activeVote,
                tier = guild.tier,
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
                activeBonusPercent = 0.0,  // Phase 2 adds active bonus tracking
                members = members,
                quests = emptyList(),  // no backend concept for this yet - not fabricating fake data
                viewerRole = viewerRole
            )""",
    "fetchGuildHome: pass guildLevel through"
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
    val activeBonusPercent: Double,
    val members: List<GuildMemberSummary>,
    val quests: List<GuildQuestSummary>,
    val viewerRole: GuildMemberRole
)""",
    "GuildHomeState: add guildLevel"
)

with open(GHS_PATH, "w", encoding="utf-8") as f:
    f.write(ghs)

# ---------- GameViewModel.kt ----------
GVM_PATH = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(GVM_PATH, "r", encoding="utf-8") as f:
    gvm = f.read()

gvm = apply(gvm,
"""    // Picks a random skill, then a random item tagged to that skill. Retries
    // with a different skill (up to a small cap) if the chosen skill happens
    // to have zero eligible items in the catalog, rather than ever throwing.
    private fun pickRandomGuildEventResource(): ItemDefinition? {
        val skills = SkillType.entries.toList()
        repeat(20) {
            val skill = skills.random()
            val candidates = ItemCatalog.items.filter { it.skillRequired == skill.name }
            if (candidates.isNotEmpty()) return candidates.random()
        }
        return null
    }""",
"""    // Caps event items to a level appropriate for the guild's current level,
    // so a level-1 guild never gets asked to contribute a level-90 item. This
    // cap should rise as the planned guild-leveling feature ships - for now,
    // with all guilds still at guild_level 1, it effectively caps events to
    // low-level items across the board. Tunable curve, first pass.
    private fun maxEventItemLevelFor(guildLevel: Int): Int = (guildLevel * 10).coerceAtLeast(10)

    // Picks a random skill, then a random item tagged to that skill at or
    // below maxItemLevel. Retries with a different skill (up to a small cap)
    // if the chosen skill happens to have zero eligible items at that level,
    // rather than ever throwing.
    private fun pickRandomGuildEventResource(maxItemLevel: Int): ItemDefinition? {
        val skills = SkillType.entries.toList()
        repeat(20) {
            val skill = skills.random()
            val candidates = ItemCatalog.items.filter { it.skillRequired == skill.name && it.levelRequired <= maxItemLevel }
            if (candidates.isNotEmpty()) return candidates.random()
        }
        return null
    }""",
    "pickRandomGuildEventResource: add level cap"
)

gvm = apply(gvm,
"""        val memberCount = (_guildHomeState.value?.members?.size ?: 1).coerceAtLeast(1)
        val item = pickRandomGuildEventResource() ?: run {
            _guildActionError.value = "No eligible items found for an event right now."
            return
        }""",
"""        val memberCount = (_guildHomeState.value?.members?.size ?: 1).coerceAtLeast(1)
        val guildLevel = _guildHomeState.value?.guildLevel ?: 1
        val item = pickRandomGuildEventResource(maxEventItemLevelFor(guildLevel)) ?: run {
            _guildActionError.value = "No eligible items found for an event right now."
            return
        }""",
    "startGuildEvent: pass guild-level-based item cap"
)

with open(GVM_PATH, "w", encoding="utf-8") as f:
    f.write(gvm)

print("All edits applied successfully.")
