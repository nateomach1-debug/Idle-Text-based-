path = "app/src/main/kotlin/com/yourname/idlerpg/CombatSystem.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor1 = '''data class AttackResult(
    val didHit: Boolean,
    val damageDealt: Int,
    val monsterHpRemaining: Int,
    val monsterDefeated: Boolean
)'''
count1 = content.count(anchor1)
assert count1 == 1, f"Expected 1 match for anchor1, found {count1}."
replacement1 = anchor1 + '''

data class CombatSessionExport(
    val characterId: String,
    val currentHp: Int,
    val maxHp: Int,
    val recoveringUntil: String?,
    val zoneId: String?,
    val sessionState: String?,
    val searchEndsAt: String?,
    val currentMonsterId: String?,
    val currentMonsterHealth: Int
)

data class OfflineCombatOutcome(
    val estimatedKills: Int,
    val xpEarned: Long
)'''
content = content.replace(anchor1, replacement1, 1)

anchor2 = '''    fun resolveRecoveryIfReady(characterId: String, now: Instant = Instant.now()): ServiceResult<CharacterCombatState> {
        val state = stateFor(characterId)
        val until = state.recovery.recoveringUntil
            ?: return ServiceResult.Failure("Character is not recovering.")
        if (now.isBefore(until)) {
            return ServiceResult.Failure("Recovery still in progress.")
        }
        state.currentHp = (state.maxHp * 0.5).toInt()
        state.recovery.recoveringUntil = null
        return ServiceResult.Success(state)
    }
}'''
count2 = content.count(anchor2)
assert count2 == 1, f"Expected 1 match for anchor2, found {count2}."
replacement2 = '''    fun resolveRecoveryIfReady(characterId: String, now: Instant = Instant.now()): ServiceResult<CharacterCombatState> {
        val state = stateFor(characterId)
        val until = state.recovery.recoveringUntil
            ?: return ServiceResult.Failure("Character is not recovering.")
        if (now.isBefore(until)) {
            return ServiceResult.Failure("Recovery still in progress.")
        }
        state.currentHp = (state.maxHp * 0.5).toInt()
        state.recovery.recoveringUntil = null
        return ServiceResult.Success(state)
    }

    fun exportSessions(): List<CombatSessionExport> =
        states.map { (characterId, state) ->
            CombatSessionExport(
                characterId = characterId,
                currentHp = state.currentHp,
                maxHp = state.maxHp,
                recoveringUntil = state.recovery.recoveringUntil?.toString(),
                zoneId = state.session?.zone?.id,
                sessionState = state.session?.state?.name,
                searchEndsAt = state.session?.searchEndsAt?.toString(),
                currentMonsterId = state.session?.currentMonster?.id,
                currentMonsterHealth = state.session?.currentMonsterHealth ?: 0
            )
        }

    fun restoreSession(export: CombatSessionExport) {
        val state = stateFor(export.characterId, export.maxHp)
        state.currentHp = export.currentHp
        state.maxHp = export.maxHp
        state.recovery.recoveringUntil = export.recoveringUntil?.let { Instant.parse(it) }
        val zoneId = export.zoneId
        if (zoneId != null) {
            val zone = ZoneCatalog.zones.find { it.id == zoneId }
            if (zone != null) {
                val monster = export.currentMonsterId?.let { mId -> zone.monsters.find { it.id == mId } }
                state.session = CombatSession(
                    zone = zone,
                    state = export.sessionState?.let { SessionState.valueOf(it) } ?: SessionState.SEARCHING,
                    searchEndsAt = export.searchEndsAt?.let { Instant.parse(it) },
                    currentMonster = monster,
                    currentMonsterHealth = export.currentMonsterHealth
                )
            }
        }
    }

    // Stat-aware estimator for offline combat progress. Mirrors live combat's own
    // formulas rather than inventing new ones: hitChance uses the same
    // accuracy-vs-defense ratio, damage uses the same uniform 0..maxHit
    // distribution (averaged), and XP uses the same damagePerHit * 4 + 5 per-hit
    // formula, scaled by elapsed time assuming the same 1-attack-per-second
    // cadence as the live tick. Average monster stats are used since live combat
    // itself picks a random monster from the zone per encounter. Loot/coins are
    // rolled per estimated kill through the same rollLoot() used by live combat,
    // so they land in the same lootPool/pendingCoins for the caller to collect
    // via the existing collectLoot()/collectCoins().
    fun resolveOfflineCombat(
        characterId: String,
        zoneId: String,
        elapsedSeconds: Long,
        attackerAccuracy: Int,
        attackerMaxHit: Int
    ): ServiceResult<OfflineCombatOutcome> {
        val state = stateFor(characterId)
        val zone = ZoneCatalog.zones.find { it.id == zoneId }
            ?: return ServiceResult.Failure("Zone not found.")
        if (zone.monsters.isEmpty()) {
            return ServiceResult.Failure("Zone has no monsters.")
        }
        if (elapsedSeconds <= 0) {
            return ServiceResult.Success(OfflineCombatOutcome(estimatedKills = 0, xpEarned = 0L))
        }

        val avgMonsterHealth = zone.monsters.map { it.maxHealth }.average()
        val avgMonsterDefense = zone.monsters.map { it.defenseRating }.average()

        val hitChance = (attackerAccuracy.toDouble() / (attackerAccuracy + avgMonsterDefense)).coerceIn(0.0, 1.0)
        val avgDamagePerHit = attackerMaxHit / 2.0

        if (hitChance <= 0.0 || avgDamagePerHit <= 0.0) {
            return ServiceResult.Success(OfflineCombatOutcome(estimatedKills = 0, xpEarned = 0L))
        }

        // Matches the live per-hit XP formula (damageDealt * 4 + 5), scaled by
        // hit chance and elapsed time at one attack attempt per second.
        val xpPerSecond = hitChance * (avgDamagePerHit * 4 + 5)
        val xpEarned = (xpPerSecond * elapsedSeconds).toLong()

        // Average search window is Random.nextInt(3, 11) in startSearching(), i.e. 3..10 inclusive.
        val avgSearchSeconds = 6.5
        val avgHitsToKill = avgMonsterHealth / avgDamagePerHit
        val avgAttacksToKill = avgHitsToKill / hitChance
        val avgTimeToKillSeconds = avgSearchSeconds + avgAttacksToKill

        val estimatedKills = (elapsedSeconds / avgTimeToKillSeconds).toInt().coerceAtLeast(0)

        repeat(estimatedKills) {
            val monster = zone.monsters.random()
            rollLoot(state, monster)
        }

        return ServiceResult.Success(OfflineCombatOutcome(estimatedKills = estimatedKills, xpEarned = xpEarned))
    }
}'''
content = content.replace(anchor2, replacement2, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("patch_offline_combat_service.py applied cleanly.")
PYEOF
cat /home/claude/patch2.py
