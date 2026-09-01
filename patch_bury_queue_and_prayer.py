# PART A: OfflineIdleMechanicsSystem.kt - new BuryQueue queue type
path = "app/src/main/kotlin/com/yourname/idlerpg/OfflineIdleMechanicsSystem.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor_queuetype = "enum class QueueType { SKILLING, CRAFTING, OFFLINE_COMBAT }"
count = content.count(anchor_queuetype)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(anchor_queuetype, "enum class QueueType { SKILLING, CRAFTING, OFFLINE_COMBAT, BURYING }", 1)

anchor_activequeue_combat = '''    data class OfflineCombatQueue(
        override val characterId: String,
        val zoneId: String,
        override val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.OFFLINE_COMBAT
    }
}'''
count = content.count(anchor_activequeue_combat)
assert count == 1, f"Expected 1 match, found {count}."
replacement_activequeue_combat = '''    data class OfflineCombatQueue(
        override val characterId: String,
        val zoneId: String,
        val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.OFFLINE_COMBAT
    }

    data class BuryQueue(
        override val characterId: String,
        val itemId: String,
        val targetQuantity: Int,
        var quantityCompleted: Int = 0,
        val secondsPerAction: Int,
        val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.BURYING
        fun isTargetReached(): Boolean = quantityCompleted >= targetQuantity
    }
}'''
content = content.replace(anchor_activequeue_combat, replacement_activequeue_combat, 1)

anchor_start_combat_queue_end = '''    fun exportOfflineCombatQueues(): List<OfflineCombatQueueExport> ='''
count = content.count(anchor_start_combat_queue_end)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(
    anchor_start_combat_queue_end,
    '''    fun startBuryQueue(characterId: String, itemId: String, targetQuantity: Int, secondsPerAction: Int): ServiceResult<ActiveQueue> {
        if (activeQueues.containsKey(characterId)) {
            return ServiceResult.Failure("Character already has an active queue. Stop it before starting a new one.")
        }
        if (targetQuantity <= 0) {
            return ServiceResult.Failure("Target quantity must be positive.")
        }
        val queue = ActiveQueue.BuryQueue(characterId, itemId, targetQuantity, secondsPerAction = secondsPerAction)
        activeQueues[characterId] = queue
        return ServiceResult.Success(queue)
    }

    fun exportOfflineCombatQueues(): List<OfflineCombatQueueExport> =''',
    1
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part A (OfflineIdleMechanicsSystem.kt) applied cleanly.")

# PART B: ItemsEquipmentSystem.kt - selectedPrayerId storage + persistence
path = "app/src/main/kotlin/com/yourname/idlerpg/ItemsEquipmentSystem.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor_inv_fields = '''    var selectedFoodId: String? = null,
    var selectedPotionId: String? = null,
    var potionTimerRemainingSeconds: Int = 0,
    var autoHealThresholdPercent: Int = 30,
    var autoFleeThresholdPercent: Int = 10
) {'''
count = content.count(anchor_inv_fields)
assert count == 1, f"Expected 1 match, found {count}."
replacement_inv_fields = '''    var selectedFoodId: String? = null,
    var selectedPotionId: String? = null,
    var potionTimerRemainingSeconds: Int = 0,
    var autoHealThresholdPercent: Int = 30,
    var autoFleeThresholdPercent: Int = 10,
    var selectedPrayerId: String? = null
) {'''
content = content.replace(anchor_inv_fields, replacement_inv_fields, 1)

anchor_select_potion_fn = '''    fun selectPotion(itemId: String?): ServiceResult<Unit> {
        if (itemId != null) {
            val definition = ItemCatalog.find(itemId) ?: return ServiceResult.Failure("Unknown item.")
            if (definition.consumableType != ConsumableType.POTION) return ServiceResult.Failure("Not a potion item.")
        }
        selectedPotionId = itemId
        potionTimerRemainingSeconds = 0
        return ServiceResult.Success(Unit)
    }'''
count = content.count(anchor_select_potion_fn)
assert count == 1, f"Expected 1 match, found {count}."
replacement_select_potion_fn = anchor_select_potion_fn + '''

    fun selectPrayer(prayerId: String?): ServiceResult<Unit> {
        if (prayerId != null && PrayerCatalog.none { it.id == prayerId }) {
            return ServiceResult.Failure("Unknown prayer.")
        }
        selectedPrayerId = prayerId
        return ServiceResult.Success(Unit)
    }'''
content = content.replace(anchor_select_potion_fn, replacement_select_potion_fn, 1)

anchor_export_class = '''data class LoadoutSettingsExport(
    val characterId: String,
    val selectedFoodId: String?,
    val selectedPotionId: String?,
    val potionTimerRemainingSeconds: Int,
    val autoHealThresholdPercent: Int,
    val autoFleeThresholdPercent: Int
)'''
count = content.count(anchor_export_class)
assert count == 1, f"Expected 1 match, found {count}."
replacement_export_class = '''data class LoadoutSettingsExport(
    val characterId: String,
    val selectedFoodId: String?,
    val selectedPotionId: String?,
    val potionTimerRemainingSeconds: Int,
    val autoHealThresholdPercent: Int,
    val autoFleeThresholdPercent: Int,
    val selectedPrayerId: String? = null
)'''
content = content.replace(anchor_export_class, replacement_export_class, 1)

anchor_export_fn = '''    fun exportAllLoadoutSettings(): List<LoadoutSettingsExport> = inventories.map { (characterId, inv) ->
        LoadoutSettingsExport(
            characterId, inv.selectedFoodId, inv.selectedPotionId, inv.potionTimerRemainingSeconds,
            inv.autoHealThresholdPercent, inv.autoFleeThresholdPercent
        )
    }

    fun restoreLoadoutSettings(export: LoadoutSettingsExport) {
        val inv = inventoryFor(export.characterId)
        inv.selectedFoodId = export.selectedFoodId
        inv.selectedPotionId = export.selectedPotionId
        inv.potionTimerRemainingSeconds = export.potionTimerRemainingSeconds
        inv.autoHealThresholdPercent = export.autoHealThresholdPercent
        inv.autoFleeThresholdPercent = export.autoFleeThresholdPercent
    }'''
count = content.count(anchor_export_fn)
assert count == 1, f"Expected 1 match, found {count}."
replacement_export_fn = '''    fun exportAllLoadoutSettings(): List<LoadoutSettingsExport> = inventories.map { (characterId, inv) ->
        LoadoutSettingsExport(
            characterId, inv.selectedFoodId, inv.selectedPotionId, inv.potionTimerRemainingSeconds,
            inv.autoHealThresholdPercent, inv.autoFleeThresholdPercent, inv.selectedPrayerId
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
    }'''
content = content.replace(anchor_export_fn, replacement_export_fn, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part B (ItemsEquipmentSystem.kt) applied cleanly.")

# PART C: ActionCatalog.kt - Prayer catalog
path = "app/src/main/kotlin/com/yourname/idlerpg/ActionCatalog.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor_end = '''data class BoneBuryInfo(val levelRequired: Int, val xpAmount: Long)'''
count = content.count(anchor_end)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(
    anchor_end,
    '''data class PrayerDefinition(val id: String, val displayName: String, val levelRequired: Int, val description: String)

// Single-select toggle, no drain resource - selecting one deselects any other.
val PrayerCatalog: List<PrayerDefinition> = listOf(
    PrayerDefinition("clarity_of_thought", "Clarity of Thought", 1, "+10% combat accuracy"),
    PrayerDefinition("burst_of_strength", "Burst of Strength", 10, "+10% combat max hit"),
    PrayerDefinition("efficient_hands", "Efficient Hands", 15, "-15% time per skilling action"),
    PrayerDefinition("rock_skin", "Rock Skin", 20, "-20% damage taken from monsters"),
    PrayerDefinition("fortunes_favor", "Fortune's Favor", 30, "+15% to all loot drop chances")
)

data class BoneBuryInfo(val levelRequired: Int, val xpAmount: Long)''',
    1
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part C (ActionCatalog.kt) applied cleanly.")

# PART D (CORRECTED — replaces the Part D sent previously): CombatSystem.kt -
# drop-rate/accuracy/max-hit prayer effects + rollLoot/resolveOfflineCombat updates
path = "app/src/main/kotlin/com/yourname/idlerpg/CombatSystem.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor_loadout = '''data class CombatLoadout(
    val style: CombatStyle,
    val trainingSkill: SkillType,
    val equippedWeapon: Weapon?,
    val equippedSpell: Spell?,
    val autoHealThresholdPercent: Int,
    val autoFleeThresholdPercent: Int
)'''
count = content.count(anchor_loadout)
assert count == 1, f"Expected 1 match, found {count}."
replacement_loadout = '''data class CombatLoadout(
    val style: CombatStyle,
    val trainingSkill: SkillType,
    val equippedWeapon: Weapon?,
    val equippedSpell: Spell?,
    val autoHealThresholdPercent: Int,
    val autoFleeThresholdPercent: Int,
    val selectedPrayerId: String? = null
)'''
content = content.replace(anchor_loadout, replacement_loadout, 1)

anchor_resolveAttack = '''    fun resolveAttack(
        characterId: String,
        loadout: CombatLoadout,
        attackerAccuracy: Int,
        attackerMaxHit: Int
    ): ServiceResult<AttackResult> {
        val state = stateFor(characterId)
        val session = state.session ?: return ServiceResult.Failure("Not currently in a zone.")
        if (session.state != SessionState.IN_COMBAT) {
            return ServiceResult.Failure("Not currently in combat.")
        }
        val monster = session.currentMonster ?: return ServiceResult.Failure("No active target.")

        val hitChancePercent = (attackerAccuracy.toDouble() / (attackerAccuracy + monster.defenseRating)) * 100.0
        val didHit = Random.nextDouble(0.0, 100.0) < hitChancePercent

        if (!didHit) {
            return ServiceResult.Success(
                AttackResult(didHit = false, damageDealt = 0, monsterHpRemaining = session.currentMonsterHealth, monsterDefeated = false)
            )
        }

        val damage = Random.nextInt(0, attackerMaxHit + 1)
        session.currentMonsterHealth = (session.currentMonsterHealth - damage).coerceAtLeast(0)
        val defeated = session.currentMonsterHealth <= 0

        if (defeated) {
            rollLoot(state, monster)
            session.currentMonster = null
            startSearching(characterId)
        }

        return ServiceResult.Success(
            AttackResult(didHit = true, damageDealt = damage, monsterHpRemaining = session.currentMonsterHealth, monsterDefeated = defeated)
        )
    }

    private fun rollLoot(state: CharacterCombatState, monster: Monster) {
        (monster.mainLootTable + monster.rareLootTable).forEach { entry ->
            if (Random.nextDouble(0.0, 100.0) < entry.dropChancePercent) {
                val qty = Random.nextInt(entry.minQty, entry.maxQty + 1)
                state.lootPool.add(entry.copy(minQty = qty, maxQty = qty))
            }
        }
        // Every monster guarantees exactly 1 bone per kill, tiered by monster level.
        val boneType = when {
            monster.levelRequirement >= 60 -> "dragon_bones"
            monster.levelRequirement >= 20 -> "big_bones"
            monster.levelRequirement >= 15 -> "gem_bones"
            else -> "bone"
        }
        state.lootPool.add(LootEntry(boneType, 1, 1, 100.0))
        state.pendingCoins += CoinDropTable.rollCoins(monster.levelRequirement)
    }'''
count = content.count(anchor_resolveAttack)
assert count == 1, f"Expected 1 match, found {count}."
replacement_resolveAttack = '''    fun resolveAttack(
        characterId: String,
        loadout: CombatLoadout,
        attackerAccuracy: Int,
        attackerMaxHit: Int
    ): ServiceResult<AttackResult> {
        val state = stateFor(characterId)
        val session = state.session ?: return ServiceResult.Failure("Not currently in a zone.")
        if (session.state != SessionState.IN_COMBAT) {
            return ServiceResult.Failure("Not currently in combat.")
        }
        val monster = session.currentMonster ?: return ServiceResult.Failure("No active target.")

        // Prayer bonuses applied here (rather than at the caller) since this is the
        // one place both live and any future callers already thread the loadout through.
        val effectiveAccuracy = if (loadout.selectedPrayerId == "clarity_of_thought") (attackerAccuracy * 1.1).toInt() else attackerAccuracy
        val effectiveMaxHit = if (loadout.selectedPrayerId == "burst_of_strength") (attackerMaxHit * 1.1).toInt() else attackerMaxHit

        val hitChancePercent = (effectiveAccuracy.toDouble() / (effectiveAccuracy + monster.defenseRating)) * 100.0
        val didHit = Random.nextDouble(0.0, 100.0) < hitChancePercent

        if (!didHit) {
            return ServiceResult.Success(
                AttackResult(didHit = false, damageDealt = 0, monsterHpRemaining = session.currentMonsterHealth, monsterDefeated = false)
            )
        }

        val damage = Random.nextInt(0, effectiveMaxHit + 1)
        session.currentMonsterHealth = (session.currentMonsterHealth - damage).coerceAtLeast(0)
        val defeated = session.currentMonsterHealth <= 0

        if (defeated) {
            val dropRateMultiplier = if (loadout.selectedPrayerId == "fortunes_favor") 1.15 else 1.0
            rollLoot(state, monster, dropRateMultiplier)
            session.currentMonster = null
            startSearching(characterId)
        }

        return ServiceResult.Success(
            AttackResult(didHit = true, damageDealt = damage, monsterHpRemaining = session.currentMonsterHealth, monsterDefeated = defeated)
        )
    }

    private fun rollLoot(state: CharacterCombatState, monster: Monster, dropRateMultiplier: Double = 1.0) {
        (monster.mainLootTable + monster.rareLootTable).forEach { entry ->
            val effectiveChance = (entry.dropChancePercent * dropRateMultiplier).coerceAtMost(100.0)
            if (Random.nextDouble(0.0, 100.0) < effectiveChance) {
                val qty = Random.nextInt(entry.minQty, entry.maxQty + 1)
                state.lootPool.add(entry.copy(minQty = qty, maxQty = qty))
            }
        }
        // Every monster guarantees exactly 1 bone per kill, tiered by monster level.
        // Guaranteed - not affected by drop-rate prayers.
        val boneType = when {
            monster.levelRequirement >= 60 -> "dragon_bones"
            monster.levelRequirement >= 20 -> "big_bones"
            monster.levelRequirement >= 15 -> "gem_bones"
            else -> "bone"
        }
        state.lootPool.add(LootEntry(boneType, 1, 1, 100.0))
        state.pendingCoins += CoinDropTable.rollCoins(monster.levelRequirement)
    }'''
content = content.replace(anchor_resolveAttack, replacement_resolveAttack, 1)

anchor_resolveOffline = '''    fun resolveOfflineCombat(
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
    }'''
count = content.count(anchor_resolveOffline)
assert count == 1, f"Expected 1 match, found {count}."
replacement_resolveOffline = '''    fun resolveOfflineCombat(
        characterId: String,
        zoneId: String,
        elapsedSeconds: Long,
        attackerAccuracy: Int,
        attackerMaxHit: Int,
        dropRateMultiplier: Double = 1.0
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
            rollLoot(state, monster, dropRateMultiplier)
        }

        return ServiceResult.Success(OfflineCombatOutcome(estimatedKills = estimatedKills, xpEarned = xpEarned))
    }'''
content = content.replace(anchor_resolveOffline, replacement_resolveOffline, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part D (CombatSystem.kt, corrected) applied cleanly.")

# PART E: GameViewModel.kt - prayer storage/selection, prayer effects wired into
# combat/skilling/crafting, and the new bury queue (replaces the old instant buryBone()).
path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

# 1. LoadoutSettingsSnapshot + selectedPrayerId
anchor_snapshot = '''    data class LoadoutSettingsSnapshot(
        val selectedFoodId: String?,
        val selectedPotionId: String?,
        val potionTimerRemainingSeconds: Int,
        val autoHealThresholdPercent: Int,
        val autoFleeThresholdPercent: Int
    )

    private val _loadoutSettings = MutableStateFlow(LoadoutSettingsSnapshot(null, null, 0, 30, 10))
    val loadoutSettings: StateFlow<LoadoutSettingsSnapshot> = _loadoutSettings.asStateFlow()'''
count = content.count(anchor_snapshot)
assert count == 1, f"Expected 1 match, found {count}."
replacement_snapshot = '''    data class LoadoutSettingsSnapshot(
        val selectedFoodId: String?,
        val selectedPotionId: String?,
        val potionTimerRemainingSeconds: Int,
        val autoHealThresholdPercent: Int,
        val autoFleeThresholdPercent: Int,
        val selectedPrayerId: String? = null
    )

    private val _loadoutSettings = MutableStateFlow(LoadoutSettingsSnapshot(null, null, 0, 30, 10, null))
    val loadoutSettings: StateFlow<LoadoutSettingsSnapshot> = _loadoutSettings.asStateFlow()

    val prayerOptions: List<PrayerDefinition> get() = PrayerCatalog'''
content = content.replace(anchor_snapshot, replacement_snapshot, 1)

anchor_snapshot_refresh = '''        _loadoutSettings.value = LoadoutSettingsSnapshot(
            inv.selectedFoodId, inv.selectedPotionId, inv.potionTimerRemainingSeconds,
            inv.autoHealThresholdPercent, inv.autoFleeThresholdPercent
        )'''
count = content.count(anchor_snapshot_refresh)
assert count == 1, f"Expected 1 match, found {count}."
replacement_snapshot_refresh = '''        _loadoutSettings.value = LoadoutSettingsSnapshot(
            inv.selectedFoodId, inv.selectedPotionId, inv.potionTimerRemainingSeconds,
            inv.autoHealThresholdPercent, inv.autoFleeThresholdPercent, inv.selectedPrayerId
        )'''
content = content.replace(anchor_snapshot_refresh, replacement_snapshot_refresh, 1)

# 2. selectPrayer() - level-gated, unlike food/potion which have no level gate
anchor_select_potion_fn = '''    fun selectPotion(itemId: String?) {
        val characterId = _currentCharacterId.value ?: return
        inventoryService.inventoryFor(characterId).selectPotion(itemId)
        refreshInventory()
    }'''
count = content.count(anchor_select_potion_fn)
assert count == 1, f"Expected 1 match, found {count}."
replacement_select_potion_fn = anchor_select_potion_fn + '''

    fun selectPrayer(prayerId: String?) {
        val characterId = _currentCharacterId.value ?: return
        if (prayerId != null) {
            val prayer = PrayerCatalog.find { it.id == prayerId } ?: return
            if (skillLevel(characterId, SkillType.PRAYER) < prayer.levelRequired) return
        }
        inventoryService.inventoryFor(characterId).selectPrayer(prayerId)
        refreshInventory()
    }'''
content = content.replace(anchor_select_potion_fn, replacement_select_potion_fn, 1)

# 3. Thread selectedPrayerId into the CombatLoadout construction
anchor_loadout_construct = '''        val loadout = CombatLoadout(
            style = weapon?.style ?: CombatStyle.MELEE,
            trainingSkill = trainingSkill,'''
count = content.count(anchor_loadout_construct)
assert count == 1, f"Expected 1 match, found {count}."
replacement_loadout_construct = '''        val loadout = CombatLoadout(
            style = weapon?.style ?: CombatStyle.MELEE,
            trainingSkill = trainingSkill,
            selectedPrayerId = inventoryService.inventoryFor(characterId).selectedPrayerId,'''
content = content.replace(anchor_loadout_construct, replacement_loadout_construct, 1)

# 4. Rock Skin prayer reduces incoming monster damage
anchor_counterattack = '''            // Monsters don't have a dedicated offensive stat yet, so their counter-attack uses a flat
            // hit chance with damage scaled off defenseRating as a stand-in. Placeholder, same spirit
            // as the maxHp formula above - safe to retune once real monster balance is worked out.
            val monster = session.currentMonster
            if (monster != null && Random.nextDouble(0.0, 100.0) < 40.0) {
                val dmg = Random.nextInt(1, (monster.defenseRating / 3).coerceAtLeast(1) + 1)
                combatService.applyDamageToCharacter(characterId, dmg)
                log.add(CombatLogEntry(monster.name + " hits you for " + dmg + "."))
            }'''
count = content.count(anchor_counterattack)
assert count == 1, f"Expected 1 match, found {count}."
replacement_counterattack = '''            // Monsters don't have a dedicated offensive stat yet, so their counter-attack uses a flat
            // hit chance with damage scaled off defenseRating as a stand-in. Placeholder, same spirit
            // as the maxHp formula above - safe to retune once real monster balance is worked out.
            val monster = session.currentMonster
            if (monster != null && Random.nextDouble(0.0, 100.0) < 40.0) {
                val rawDmg = Random.nextInt(1, (monster.defenseRating / 3).coerceAtLeast(1) + 1)
                val dmg = if (inventoryService.inventoryFor(characterId).selectedPrayerId == "rock_skin") {
                    (rawDmg * 0.8).toInt().coerceAtLeast(1)
                } else {
                    rawDmg
                }
                combatService.applyDamageToCharacter(characterId, dmg)
                log.add(CombatLogEntry(monster.name + " hits you for " + dmg + "."))
            }'''
content = content.replace(anchor_counterattack, replacement_counterattack, 1)

# 5. Offline combat resolution gets the same accuracy/max-hit/drop-rate prayer bonuses
anchor_offline_combat = '''                    val outcome = combatService.resolveOfflineCombat(characterId, combatQueue.zoneId, elapsedSeconds, accuracy, maxHit)'''
count = content.count(anchor_offline_combat)
assert count == 1, f"Expected 1 match, found {count}."
replacement_offline_combat = '''                    val selectedPrayerId = inventoryService.inventoryFor(characterId).selectedPrayerId
                    val prayerAccuracy = if (selectedPrayerId == "clarity_of_thought") (accuracy * 1.1).toInt() else accuracy
                    val prayerMaxHit = if (selectedPrayerId == "burst_of_strength") (maxHit * 1.1).toInt() else maxHit
                    val prayerDropRateMultiplier = if (selectedPrayerId == "fortunes_favor") 1.15 else 1.0
                    val outcome = combatService.resolveOfflineCombat(characterId, combatQueue.zoneId, elapsedSeconds, prayerAccuracy, prayerMaxHit, prayerDropRateMultiplier)'''
content = content.replace(anchor_offline_combat, replacement_offline_combat, 1)

# 6. Efficient Hands prayer speeds up gathering-skill queues (start-time only, mirrors
#    how these queues already fix secondsPerAction for their whole duration)
anchor_start_skill = '''        offlineIdleService.startSkillingQueue(characterId, skillType.name, itemId, action.secondsPerAction)'''
count = content.count(anchor_start_skill)
assert count == 1, f"Expected 1 match, found {count}."
replacement_start_skill = '''        val effectiveSecondsPerAction = if (inventoryService.inventoryFor(characterId).selectedPrayerId == "efficient_hands") {
            (action.secondsPerAction * 0.85).toLong().coerceAtLeast(1L)
        } else {
            action.secondsPerAction
        }
        offlineIdleService.startSkillingQueue(characterId, skillType.name, itemId, effectiveSecondsPerAction)'''
content = content.replace(anchor_start_skill, replacement_start_skill, 1)

# 7. Same for the Crafting-queue skills (Smithing/Cooking/Crafting/Fletching)
anchor_start_crafting = '''        offlineIdleService.startCraftingQueue(
            characterId,
            itemId,
            CraftingTierCurve.secondsFor(recipe.levelRequired),
            targetQuantity
        )'''
count = content.count(anchor_start_crafting)
assert count == 1, f"Expected 1 match, found {count}."
replacement_start_crafting = '''        val baseCraftSeconds = CraftingTierCurve.secondsFor(recipe.levelRequired)
        val effectiveCraftSeconds = if (inventoryService.inventoryFor(characterId).selectedPrayerId == "efficient_hands") {
            (baseCraftSeconds * 0.85).toLong().coerceAtLeast(1L)
        } else {
            baseCraftSeconds
        }
        offlineIdleService.startCraftingQueue(
            characterId,
            itemId,
            effectiveCraftSeconds,
            targetQuantity
        )'''
content = content.replace(anchor_start_crafting, replacement_start_crafting, 1)

# 8. Replace the old instant buryBone() with a proper timed, quantity-targeted queue
#    (2 seconds per bone, also sped up by Efficient Hands), plus its own tick function.
anchor_buryBone = '''    fun buryBone(itemId: String) {
        val characterId = _currentCharacterId.value ?: return
        val boneInfo = PrayerBoneRequirements[itemId] ?: return
        val prayerLevel = skillLevel(characterId, SkillType.PRAYER)
        if (prayerLevel < boneInfo.levelRequired) return
        val inventory = inventoryService.inventoryFor(characterId)
        val removed = inventory.removeItem(itemId, 1)
        if (removed is ServiceResult.Success) {
            progressionService.grantXp(characterId, SkillType.PRAYER, boneInfo.xpAmount)
            refreshInventory()
            refreshSkills()
        }
    }'''
count = content.count(anchor_buryBone)
assert count == 1, f"Expected 1 match, found {count}."
replacement_buryBone = '''    private var buryActionProgressSeconds: Long = 0

    fun startBuryAction(itemId: String, quantity: Int) {
        val characterId = _currentCharacterId.value ?: return
        val boneInfo = PrayerBoneRequirements[itemId] ?: return
        val prayerLevel = skillLevel(characterId, SkillType.PRAYER)
        if (prayerLevel < boneInfo.levelRequired) return
        val inventory = inventoryService.inventoryFor(characterId)
        val available = inventory.quantityOf(itemId)
        if (available <= 0 || quantity <= 0) return
        val cappedQuantity = minOf(quantity, available)
        val baseSeconds = 2L
        val effectiveSeconds = if (inventory.selectedPrayerId == "efficient_hands") {
            (baseSeconds * 0.85).toLong().coerceAtLeast(1L)
        } else {
            baseSeconds
        }
        // Starting a bury queue stops any active combat session - only one
        // activity can run at a time.
        leaveCombatZone()
        offlineIdleService.stopQueue(characterId)
        offlineIdleService.startBuryQueue(characterId, itemId, cappedQuantity, effectiveSeconds)
        offlineIdleService.recordLastSeen(characterId)
        buryActionProgressSeconds = 0
        refreshActiveQueue()
    }

    fun stopBuryAction() {
        val characterId = _currentCharacterId.value ?: return
        offlineIdleService.stopQueue(characterId)
        buryActionProgressSeconds = 0
        refreshActiveQueue()
    }

    private fun tickBurying() {
        val characterId = _currentCharacterId.value ?: return
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.BuryQueue ?: return

        buryActionProgressSeconds += 1
        if (buryActionProgressSeconds < queue.secondsPerAction) return

        val attempts = (buryActionProgressSeconds / queue.secondsPerAction).toInt()
        buryActionProgressSeconds %= queue.secondsPerAction

        val remainingToTarget = queue.targetQuantity - queue.quantityCompleted
        val cappedAttempts = minOf(attempts, remainingToTarget)
        if (cappedAttempts <= 0) return

        val boneInfo = PrayerBoneRequirements[queue.itemId] ?: return
        val inventory = inventoryService.inventoryFor(characterId)
        val available = inventory.quantityOf(queue.itemId)
        val effectiveAttempts = minOf(cappedAttempts, available)

        if (effectiveAttempts > 0) {
            inventory.removeItem(queue.itemId, effectiveAttempts)
            progressionService.grantXp(characterId, SkillType.PRAYER, boneInfo.xpAmount * effectiveAttempts)
            queue.quantityCompleted += effectiveAttempts
            refreshInventory()
            refreshSkills()
        }

        if (queue.isTargetReached()) {
            offlineIdleService.stopQueue(characterId)
            buryActionProgressSeconds = 0
            refreshActiveQueue()
        } else if (effectiveAttempts < cappedAttempts) {
            // Ran out of bones mid-batch - stop instead of spinning uselessly.
            offlineIdleService.stopQueue(characterId)
            buryActionProgressSeconds = 0
            refreshActiveQueue()
            _actionStoppedNotifications.value = _actionStoppedNotifications.value + ActionStoppedNotice(
                itemName = formatItemName(queue.itemId),
                reason = "Ran out of " + formatItemName(queue.itemId) + "."
            )
        }
    }'''
content = content.replace(anchor_buryBone, replacement_buryBone, 1)

# 9. Wire tickBurying() into the main tick loop
anchor_tickloop = '''                delay(1000L)
                tickSkilling()
            tickCrafting()
            tickConsumables()
            tickCombat()
            }'''
count = content.count(anchor_tickloop)
assert count == 1, f"Expected 1 match, found {count}."
replacement_tickloop = '''                delay(1000L)
                tickSkilling()
            tickCrafting()
            tickBurying()
            tickConsumables()
            tickCombat()
            }'''
content = content.replace(anchor_tickloop, replacement_tickloop, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part E (GameViewModel.kt) applied cleanly.")

# PART F: InventoryScreen.kt - replace the single "Bury" button with a quantity
# stepper (1..item.quantity) and "Bury N" button, matching the requested per-bone timer feature.
path = "app/src/main/kotlin/com/yourname/idlerpg/InventoryScreen.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor_screen_sig = '''    onBuryItem: (String) -> Unit,'''
count = content.count(anchor_screen_sig)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(anchor_screen_sig, '    onBuryItem: (String, Int) -> Unit,', 1)

anchor_sheet_call_bury = '''            onBury = { onBuryItem(item.itemId); selectedItem = null },'''
count = content.count(anchor_sheet_call_bury)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(
    anchor_sheet_call_bury,
    '            onBury = { qty -> onBuryItem(item.itemId, qty); selectedItem = null },',
    1
)

anchor_sheet_sig_bury = '''    onBury: () -> Unit,'''
count = content.count(anchor_sheet_sig_bury)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(anchor_sheet_sig_bury, '    onBury: (Int) -> Unit,', 1)

anchor_bury_block = '''                if (item.isBuryable) {
                    val (canBuryNow, buryLockReason) = canBury
                    Button(
                        onClick = onBury,
                        enabled = canBuryNow,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(text = "Bury")
                    }
                    if (!canBuryNow && buryLockReason != null) {
                        Spacer(modifier = Modifier.height(4.dp))
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = Icons.Filled.Lock,
                                contentDescription = "Locked",
                                tint = MaterialTheme.colorScheme.error,
                                modifier = Modifier.size(14.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(text = buryLockReason, style = MaterialTheme.typography.labelSmall)
                        }
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                }'''
count = content.count(anchor_bury_block)
assert count == 1, f"Expected 1 match, found {count}."
replacement_bury_block = '''                if (item.isBuryable) {
                    val (canBuryNow, buryLockReason) = canBury
                    var buryQuantity by remember(item.itemId) { mutableStateOf(1) }
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        IconButton(
                            onClick = { if (buryQuantity > 1) buryQuantity -= 1 },
                            enabled = canBuryNow
                        ) {
                            Text(text = "-", style = MaterialTheme.typography.titleLarge)
                        }
                        Text(
                            text = buryQuantity.toString(),
                            style = MaterialTheme.typography.titleMedium,
                            modifier = Modifier.padding(horizontal = 8.dp)
                        )
                        IconButton(
                            onClick = { if (buryQuantity < item.quantity) buryQuantity += 1 },
                            enabled = canBuryNow
                        ) {
                            Text(text = "+", style = MaterialTheme.typography.titleLarge)
                        }
                    }
                    Spacer(modifier = Modifier.height(4.dp))
                    Button(
                        onClick = { onBury(buryQuantity) },
                        enabled = canBuryNow,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(text = "Bury " + buryQuantity)
                    }
                    if (!canBuryNow && buryLockReason != null) {
                        Spacer(modifier = Modifier.height(4.dp))
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = Icons.Filled.Lock,
                                contentDescription = "Locked",
                                tint = MaterialTheme.colorScheme.error,
                                modifier = Modifier.size(14.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(text = buryLockReason, style = MaterialTheme.typography.labelSmall)
                        }
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                }'''
content = content.replace(anchor_bury_block, replacement_bury_block, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part F (InventoryScreen.kt) applied cleanly.")

# PART G: LoadoutScreen.kt - Prayer picker section, mirroring the Training
# chip-row style, with locked/grayed-out prayers above the player's current level.
path = "app/src/main/kotlin/com/yourname/idlerpg/LoadoutScreen.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor_sig = '''fun LoadoutScreen(
    state: LoadoutState,
    onBack: () -> Unit,
    onFoodSelected: (String) -> Unit,
    onPotionSelected: (String) -> Unit,
    onAutoHealChanged: (Int) -> Unit,
    onAutoFleeChanged: (Int) -> Unit,
    trainingSkill: SkillType? = null,
    allowedTrainingSkills: List<SkillType> = emptyList(),
    onTrainingSkillSelected: (SkillType) -> Unit = {},
    modifier: Modifier = Modifier
) {'''
count = content.count(anchor_sig)
assert count == 1, f"Expected 1 match, found {count}."
replacement_sig = '''fun LoadoutScreen(
    state: LoadoutState,
    onBack: () -> Unit,
    onFoodSelected: (String) -> Unit,
    onPotionSelected: (String) -> Unit,
    onAutoHealChanged: (Int) -> Unit,
    onAutoFleeChanged: (Int) -> Unit,
    trainingSkill: SkillType? = null,
    allowedTrainingSkills: List<SkillType> = emptyList(),
    onTrainingSkillSelected: (SkillType) -> Unit = {},
    selectedPrayerId: String? = null,
    prayerOptions: List<PrayerDefinition> = emptyList(),
    prayerLevel: Int = 1,
    onPrayerSelected: (String) -> Unit = {},
    modifier: Modifier = Modifier
) {'''
content = content.replace(anchor_sig, replacement_sig, 1)

anchor_potion_end = '''        if (state.availablePotions.isEmpty()) {
            Text(text = "No potions in inventory.", style = MaterialTheme.typography.bodyMedium)
        } else {
            state.availablePotions.forEach { potion ->
                ConsumableRow(
                    option = potion,
                    isSelected = potion.itemId == state.selectedPotionId,
                    onClick = { onPotionSelected(potion.itemId) }
                )
            }
        }
    }
}'''
count = content.count(anchor_potion_end)
assert count == 1, f"Expected 1 match, found {count}."
replacement_potion_end = '''        if (state.availablePotions.isEmpty()) {
            Text(text = "No potions in inventory.", style = MaterialTheme.typography.bodyMedium)
        } else {
            state.availablePotions.forEach { potion ->
                ConsumableRow(
                    option = potion,
                    isSelected = potion.itemId == state.selectedPotionId,
                    onClick = { onPotionSelected(potion.itemId) }
                )
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        Text(text = "Prayer", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        Column {
            prayerOptions.forEach { prayer ->
                val selected = prayer.id == selectedPrayerId
                val locked = prayerLevel < prayer.levelRequired
                val background = if (selected) {
                    MaterialTheme.colorScheme.primary.copy(alpha = 0.2f)
                } else {
                    MaterialTheme.colorScheme.surfaceVariant
                }
                val textColor = if (locked) {
                    MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
                } else {
                    MaterialTheme.colorScheme.onSurface
                }
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp)
                        .clip(RoundedCornerShape(10.dp))
                        .background(background)
                        .clickable(enabled = !locked) { onPrayerSelected(prayer.id) }
                        .padding(12.dp)
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(text = prayer.displayName, style = MaterialTheme.typography.bodyMedium, color = textColor)
                        Text(text = prayer.description, style = MaterialTheme.typography.labelSmall, color = textColor)
                    }
                    if (locked) {
                        Text(text = "Lv " + prayer.levelRequired, style = MaterialTheme.typography.labelSmall, color = textColor)
                    }
                }
            }
        }
    }
}'''
content = content.replace(anchor_potion_end, replacement_potion_end, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part G (LoadoutScreen.kt) applied cleanly.")

# PART H: MainActivity.kt - wire Prayer params into both LoadoutScreen call
# sites, and fix onBuryItem's wiring to the new quantity-taking startBuryAction().
path = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor_combat_loadout = '''                                CombatScreenState.Loadout -> LoadoutScreen(
                                    state = LoadoutState(
                                        availableFoodOptions, loadoutSettings.selectedFoodId,
                                        availablePotionOptions, loadoutSettings.selectedPotionId,
                                        loadoutSettings.potionTimerRemainingSeconds,
                                        loadoutSettings.autoHealThresholdPercent, loadoutSettings.autoFleeThresholdPercent
                                    ),
                                    trainingSkill = trainingSkill,
                                    allowedTrainingSkills = gameViewModel.allowedTrainingSkills,
                                    onTrainingSkillSelected = { gameViewModel.setTrainingSkill(it) },
                                    onBack = { combatScreenState = CombatScreenState.ZoneSelect },
                                    onFoodSelected = { gameViewModel.selectFood(it) },
                                    onPotionSelected = { gameViewModel.selectPotion(it) },
                                    onAutoHealChanged = { gameViewModel.setAutoHealThreshold(it) },
                                    onAutoFleeChanged = { gameViewModel.setAutoFleeThreshold(it) }
                                )'''
count = content.count(anchor_combat_loadout)
assert count == 1, f"Expected 1 match, found {count}."
replacement_combat_loadout = '''                                CombatScreenState.Loadout -> LoadoutScreen(
                                    state = LoadoutState(
                                        availableFoodOptions, loadoutSettings.selectedFoodId,
                                        availablePotionOptions, loadoutSettings.selectedPotionId,
                                        loadoutSettings.potionTimerRemainingSeconds,
                                        loadoutSettings.autoHealThresholdPercent, loadoutSettings.autoFleeThresholdPercent
                                    ),
                                    trainingSkill = trainingSkill,
                                    allowedTrainingSkills = gameViewModel.allowedTrainingSkills,
                                    onTrainingSkillSelected = { gameViewModel.setTrainingSkill(it) },
                                    onBack = { combatScreenState = CombatScreenState.ZoneSelect },
                                    onFoodSelected = { gameViewModel.selectFood(it) },
                                    onPotionSelected = { gameViewModel.selectPotion(it) },
                                    onAutoHealChanged = { gameViewModel.setAutoHealThreshold(it) },
                                    onAutoFleeChanged = { gameViewModel.setAutoFleeThreshold(it) },
                                    selectedPrayerId = loadoutSettings.selectedPrayerId,
                                    prayerOptions = gameViewModel.prayerOptions,
                                    prayerLevel = allSkills["PRAYER"]?.level ?: 1,
                                    onPrayerSelected = { gameViewModel.selectPrayer(it) }
                                )'''
content = content.replace(anchor_combat_loadout, replacement_combat_loadout, 1)

anchor_inventory_loadout = '''                                InventoryScreenState.Loadout -> LoadoutScreen(
                                    state = LoadoutState(
                                        availableFoodOptions, loadoutSettings.selectedFoodId,
                                        availablePotionOptions, loadoutSettings.selectedPotionId,
                                        loadoutSettings.potionTimerRemainingSeconds,
                                        loadoutSettings.autoHealThresholdPercent, loadoutSettings.autoFleeThresholdPercent
                                    ),
                                    onBack = { inventoryScreenState = InventoryScreenState.Items },
                                    onFoodSelected = { gameViewModel.selectFood(it) },
                                    onPotionSelected = { gameViewModel.selectPotion(it) },
                                    onAutoHealChanged = { gameViewModel.setAutoHealThreshold(it) },
                                    onAutoFleeChanged = { gameViewModel.setAutoFleeThreshold(it) }
                                )'''
count = content.count(anchor_inventory_loadout)
assert count == 1, f"Expected 1 match, found {count}."
replacement_inventory_loadout = '''                                InventoryScreenState.Loadout -> LoadoutScreen(
                                    state = LoadoutState(
                                        availableFoodOptions, loadoutSettings.selectedFoodId,
                                        availablePotionOptions, loadoutSettings.selectedPotionId,
                                        loadoutSettings.potionTimerRemainingSeconds,
                                        loadoutSettings.autoHealThresholdPercent, loadoutSettings.autoFleeThresholdPercent
                                    ),
                                    onBack = { inventoryScreenState = InventoryScreenState.Items },
                                    onFoodSelected = { gameViewModel.selectFood(it) },
                                    onPotionSelected = { gameViewModel.selectPotion(it) },
                                    onAutoHealChanged = { gameViewModel.setAutoHealThreshold(it) },
                                    onAutoFleeChanged = { gameViewModel.setAutoFleeThreshold(it) },
                                    selectedPrayerId = loadoutSettings.selectedPrayerId,
                                    prayerOptions = gameViewModel.prayerOptions,
                                    prayerLevel = allSkills["PRAYER"]?.level ?: 1,
                                    onPrayerSelected = { gameViewModel.selectPrayer(it) }
                                )'''
content = content.replace(anchor_inventory_loadout, replacement_inventory_loadout, 1)

anchor_onburyitem = '''                                    onBuryItem = { itemId -> gameViewModel.buryBone(itemId) },'''
count = content.count(anchor_onburyitem)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(
    anchor_onburyitem,
    '                                    onBuryItem = { itemId, qty -> gameViewModel.startBuryAction(itemId, qty) },',
    1
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part H (MainActivity.kt) applied cleanly.")

# PART I: Fix Long/Int mismatch - BuryQueue.secondsPerAction and startBuryQueue()
# should be Long, matching SkillingQueue/CraftingQueue's existing convention.
path = "app/src/main/kotlin/com/yourname/idlerpg/OfflineIdleMechanicsSystem.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor_buryqueue_class = '''    data class BuryQueue(
        override val characterId: String,
        val itemId: String,
        val targetQuantity: Int,
        var quantityCompleted: Int = 0,
        val secondsPerAction: Int,
        val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.BURYING
        fun isTargetReached(): Boolean = quantityCompleted >= targetQuantity
    }
}'''
count = content.count(anchor_buryqueue_class)
assert count == 1, f"Expected 1 match, found {count}."
replacement_buryqueue_class = '''    data class BuryQueue(
        override val characterId: String,
        val itemId: String,
        val targetQuantity: Int,
        var quantityCompleted: Int = 0,
        val secondsPerAction: Long,
        override val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.BURYING
        fun isTargetReached(): Boolean = quantityCompleted >= targetQuantity
    }
}'''
count2 = content.count(replacement_buryqueue_class)
if count2 == 0:
    content = content.replace(anchor_buryqueue_class, replacement_buryqueue_class, 1)

anchor_startburyqueue = '''    fun startBuryQueue(characterId: String, itemId: String, targetQuantity: Int, secondsPerAction: Int): ServiceResult<ActiveQueue> {'''
count3 = content.count(anchor_startburyqueue)
if count3 == 1:
    content = content.replace(
        anchor_startburyqueue,
        '    fun startBuryQueue(characterId: String, itemId: String, targetQuantity: Int, secondsPerAction: Long): ServiceResult<ActiveQueue> {',
        1
    )

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part I (OfflineIdleMechanicsSystem.kt Long/Int fix) applied cleanly.")
