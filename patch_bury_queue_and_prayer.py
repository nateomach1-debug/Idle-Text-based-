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
"""    // Must match the SQL curve in contribute_to_guild_event() - level L needs
    // 1000*L XP to advance to L+1. Exposed here so the UI can show a progress
    // bar without a network round trip.
    fun guildXpRequiredForLevel(level: Int): Long = 1000L * level""",
"""    // Must match the SQL curve in contribute_to_guild_event() - level L needs
    // 1000*L XP to advance to L+1. Exposed here so the UI can show a progress
    // bar without a network round trip.
    fun guildXpRequiredForLevel(level: Int): Long = 1000L * level

    // Guild-exclusive perk: +0.5% XP per guild level, capped at +15% (reached
    // around guild level 30). Noticeable by the mid game, never mandatory.
    // Reuses the existing Effect.XpBoost mechanism (grantXp()'s extraEffects
    // param) rather than a separate bolt-on multiplier - nothing else in the
    // game currently produces an XpBoost effect, so this is genuinely
    // guild-exclusive. One effect per SkillGroup so it applies uniformly
    // across combat/gathering/production without double-counting (a skill
    // belongs to exactly one group).
    fun guildXpBonusPercent(): Double {
        val level = _guildHomeState.value?.guildLevel ?: return 0.0
        return (level * 0.5).coerceAtMost(15.0)
    }

    private fun guildXpBonusEffects(): List<Effect> {
        val percent = guildXpBonusPercent()
        if (percent <= 0.0) return emptyList()
        return SkillGroup.entries.map { group -> Effect.XpBoost(EffectScope.Group(group), percent) }
    }""",
    "add guildXpBonusPercent + guildXpBonusEffects"
)

gvm = apply(gvm,
"""progressionService.grantXp(characterId, trainingSkill, (attack.damageDealt * 4 + 5).toLong())""",
"""progressionService.grantXp(characterId, trainingSkill, (attack.damageDealt * 4 + 5).toLong(), guildXpBonusEffects())""",
    "grantXp call site 1 (combat)"
)

gvm = apply(gvm,
"""progressionService.grantXp(characterId, SkillType.PRAYER, boneInfo.xpAmount * effectiveAttempts)""",
"""progressionService.grantXp(characterId, SkillType.PRAYER, boneInfo.xpAmount * effectiveAttempts, guildXpBonusEffects())""",
    "grantXp call site 2 (bury/prayer)"
)

gvm = apply(gvm,
"""progressionService.grantXp(characterId, skillType, xpEarned)""",
"""progressionService.grantXp(characterId, skillType, xpEarned, guildXpBonusEffects())""",
    "grantXp call site 3"
)

gvm = apply(gvm,
"""progressionService.grantXp(characterId, SkillType.PRAYER, xpGranted)""",
"""progressionService.grantXp(characterId, SkillType.PRAYER, xpGranted, guildXpBonusEffects())""",
    "grantXp call site 4 (prayer)"
)

gvm = apply(gvm,
"""progressionService.grantXp(characterId, trainingSkill, outcome.value.xpEarned)""",
"""progressionService.grantXp(characterId, trainingSkill, outcome.value.xpEarned, guildXpBonusEffects())""",
    "grantXp call site 5"
)

gvm = apply(gvm,
"""progressionService.grantXp(characterId, skillType, action.xpPerAction * effectiveActions)""",
"""progressionService.grantXp(characterId, skillType, action.xpPerAction * effectiveActions, guildXpBonusEffects())""",
    "grantXp call site 6"
)

gvm = apply(gvm,
"""progressionService.grantXp(characterId, skillType, xpGranted)""",
"""progressionService.grantXp(characterId, skillType, xpGranted, guildXpBonusEffects())""",
    "grantXp call site 7"
)

with open(GVM_PATH, "w", encoding="utf-8") as f:
    f.write(gvm)

# ---------- SupabaseGuildRepository.kt ----------
SGR_PATH = "app/src/main/kotlin/com/yourname/idlerpg/SupabaseGuildRepository.kt"
with open(SGR_PATH, "r", encoding="utf-8") as f:
    sgr = f.read()

sgr = apply(sgr,
"""                guildCoins = guild.guildCoins,
                activeBonusPercent = 0.0,  // Phase 2 adds active bonus tracking""",
"""                guildCoins = guild.guildCoins,
                activeBonusPercent = (guild.guildLevel * 0.5).coerceAtMost(15.0),""",
    "fetchGuildHome: compute real activeBonusPercent"
)

with open(SGR_PATH, "w", encoding="utf-8") as f:
    f.write(sgr)

# ---------- GuildHomeScreen.kt ----------
GHS_PATH = "app/src/main/kotlin/com/yourname/idlerpg/GuildHomeScreen.kt"
with open(GHS_PATH, "r", encoding="utf-8") as f:
    ghs = f.read()

ghs = apply(ghs,
"""            TierBonusCard(state.tier, state.activeBonusPercent, modifier = Modifier.weight(1f))""",
"""            TierBonusCard(state.activeBonusPercent, modifier = Modifier.weight(1f))""",
    "TierBonusCard call site: drop redundant tier number"
)

ghs = apply(ghs,
"""private fun TierBonusCard(tier: Int, bonusPercent: Double, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(14.dp)
    ) {
        Text(text = "Tier " + tier, style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = if (bonusPercent > 0) "+" + bonusPercent + "% active bonus" else "No active bonus",
            style = MaterialTheme.typography.labelSmall
        )
    }
}""",
"""private fun TierBonusCard(bonusPercent: Double, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(14.dp)
    ) {
        Text(text = "Guild Bonus", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = if (bonusPercent > 0) "+%.1f%% XP from all sources".format(bonusPercent) else "No active bonus",
            style = MaterialTheme.typography.labelSmall
        )
    }
}""",
    "TierBonusCard: show bonus description instead of redundant level number"
)

with open(GHS_PATH, "w", encoding="utf-8") as f:
    f.write(ghs)

print("All edits applied successfully.")
