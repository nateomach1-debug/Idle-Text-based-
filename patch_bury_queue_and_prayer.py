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
"""        val removal = inventoryService.inventoryFor(localCharacterId).removeItem(event.itemId, quantity)
        if (removal is ServiceResult.Failure) {
            _guildActionError.value = removal.message
            return
        }""",
"""        val removal = inventoryService.inventoryFor(localCharacterId).removeItem(event.itemId, quantity)
        if (removal is ServiceResult.Failure) {
            _guildActionError.value = removal.reason
            return
        }""",
    "fix: ServiceResult.Failure uses .reason not .message"
)

with open(GVM_PATH, "w", encoding="utf-8") as f:
    f.write(gvm)

# ---------- MainActivity.kt ----------
MA_PATH = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(MA_PATH, "r", encoding="utf-8") as f:
    ma = f.read()

ma = apply(ma,
"""private fun demoGuildState(): GuildHomeState = GuildHomeState(
    guildName = "Iron Wolves",
    activeEvent = GuildEventSummary("Beast Hunt", progressCurrent = 78, progressTarget = 120),
    activeVote = null,
    tier = 2,
    activeBonusPercent = 5.0,
    members = demoGuildMembers(),
    quests = listOf(
        GuildQuestSummary("Weekly Contribution", "Donate items toward this week's guild goal.")
    ),
    viewerRole = GuildMemberRole.LEADER
)""",
"""private fun demoGuildState(): GuildHomeState = GuildHomeState(
    guildName = "Iron Wolves",
    activeEvent = GuildEventSummary(
        id = "demo-event",
        name = "Beast Hunt",
        itemId = "wolf_pelt",
        skillName = "THIEVING",
        progressCurrent = 78,
        progressTarget = 120,
        milestonesPaid = 2
    ),
    activeVote = null,
    tier = 2,
    guildLevel = 3,
    guildXp = 1200L,
    activeBonusPercent = 5.0,
    members = demoGuildMembers(),
    quests = listOf(
        GuildQuestSummary("Weekly Contribution", "Donate items toward this week's guild goal.")
    ),
    viewerRole = GuildMemberRole.LEADER
)""",
    "fix: demoGuildState needs new GuildEventSummary/GuildHomeState fields"
)

with open(MA_PATH, "w", encoding="utf-8") as f:
    f.write(ma)

print("Both fixes applied.")
