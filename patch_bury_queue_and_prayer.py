import re

PATH = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

def apply(old, new, label):
    global content
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"FAILED [{label}]: expected 1 match, found {count}")
    content = content.replace(old, new, 1)

# 1. Tick loop: track real elapsed time instead of assuming 1s per iteration
apply(
"""    init {
        viewModelScope.launch(Dispatchers.Default) {
            while (true) {
                delay(1000L)
                tickSkilling()
            tickCrafting()
            tickBurying()
            tickConsumables()
            tickCombat()
            }
        }
    }""",
"""    init {
        viewModelScope.launch(Dispatchers.Default) {
            var lastTickMillis = System.currentTimeMillis()
            while (true) {
                delay(1000L)
                val now = System.currentTimeMillis()
                val elapsedSeconds = ((now - lastTickMillis) / 1000L).coerceAtLeast(1L)
                lastTickMillis += elapsedSeconds * 1000L
                tickSkilling(elapsedSeconds)
                tickCrafting(elapsedSeconds)
                tickBurying(elapsedSeconds)
                tickConsumables(elapsedSeconds)
                tickCombat(elapsedSeconds)
            }
        }
    }""",
    "tick loop"
)

# 2. tickSkilling: elapsed-time-correct progress
apply(
"""    private fun tickSkilling() {
        val characterId = _currentCharacterId.value ?: return
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.SkillingQueue ?: return

        skillActionProgressSeconds += 1
        if (skillActionProgressSeconds < queue.secondsPerAction) return""",
"""    private fun tickSkilling(elapsedSeconds: Long) {
        val characterId = _currentCharacterId.value ?: return
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.SkillingQueue ?: return

        skillActionProgressSeconds += elapsedSeconds
        if (skillActionProgressSeconds < queue.secondsPerAction) return""",
    "tickSkilling"
)

# 3. tickCrafting: elapsed-time-correct progress
apply(
"""    private fun tickCrafting() {
        val characterId = _currentCharacterId.value ?: return
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.CraftingQueue ?: return

        craftActionProgressSeconds += 1
        if (craftActionProgressSeconds < queue.secondsPerAction) return""",
"""    private fun tickCrafting(elapsedSeconds: Long) {
        val characterId = _currentCharacterId.value ?: return
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.CraftingQueue ?: return

        craftActionProgressSeconds += elapsedSeconds
        if (craftActionProgressSeconds < queue.secondsPerAction) return""",
    "tickCrafting"
)

# 4. tickBurying: elapsed-time-correct progress
apply(
"""    private fun tickBurying() {
        val characterId = _currentCharacterId.value ?: return
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.BuryQueue ?: return

        buryActionProgressSeconds += 1
        if (buryActionProgressSeconds < queue.secondsPerAction) return""",
"""    private fun tickBurying(elapsedSeconds: Long) {
        val characterId = _currentCharacterId.value ?: return
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.BuryQueue ?: return

        buryActionProgressSeconds += elapsedSeconds
        if (buryActionProgressSeconds < queue.secondsPerAction) return""",
    "tickBurying"
)

# 5. tickConsumables: elapsed-time-correct potion timer
apply(
"""    private fun tickConsumables() {
        val characterId = _currentCharacterId.value ?: return
        val inventory = inventoryService.inventoryFor(characterId)
        val combatState = combatService.stateFor(characterId)

        if (combatState.maxHp > 0) {
            val hpPercent = (combatState.currentHp * 100) / combatState.maxHp
            if (hpPercent <= inventory.autoHealThresholdPercent) {
                inventory.consumeSelectedFood()?.let { food ->
                    combatService.healCharacter(characterId, food.healAmount ?: 0)
                }
            }
        }

        if (inventory.selectedPotionId != null) {
            if (inventory.potionTimerRemainingSeconds > 0) {
                inventory.potionTimerRemainingSeconds -= 1
            }
            if (inventory.potionTimerRemainingSeconds <= 0) {
                inventory.consumeSelectedPotion()?.let { potion ->
                    inventory.potionTimerRemainingSeconds = potion.buffDurationSeconds ?: 0
                }
            }
        }

        refreshInventory()
        refreshCombatHp()
    }""",
"""    private fun tickConsumables(elapsedSeconds: Long) {
        val characterId = _currentCharacterId.value ?: return
        val inventory = inventoryService.inventoryFor(characterId)
        val combatState = combatService.stateFor(characterId)

        if (combatState.maxHp > 0) {
            val hpPercent = (combatState.currentHp * 100) / combatState.maxHp
            if (hpPercent <= inventory.autoHealThresholdPercent) {
                inventory.consumeSelectedFood()?.let { food ->
                    combatService.healCharacter(characterId, food.healAmount ?: 0)
                }
            }
        }

        if (inventory.selectedPotionId != null) {
            if (inventory.potionTimerRemainingSeconds > 0) {
                inventory.potionTimerRemainingSeconds = (inventory.potionTimerRemainingSeconds - elapsedSeconds.toInt()).coerceAtLeast(0)
            }
            if (inventory.potionTimerRemainingSeconds <= 0) {
                inventory.consumeSelectedPotion()?.let { potion ->
                    inventory.potionTimerRemainingSeconds = potion.buffDurationSeconds ?: 0
                }
            }
        }

        refreshInventory()
        refreshCombatHp()
    }""",
    "tickConsumables"
)

# 6. tickCombat: elapsed-time-correct AND now actually gated by attackSpeedSeconds (Option B)
apply(
"""    private fun tickCombat() {
        val characterId = _currentCharacterId.value ?: return
        val state = combatService.stateFor(characterId, maxHpFor(characterId))

        if (state.recovery.isRecovering()) {
            refreshCombatHp()
            return
        }
        if (combatService.resolveRecoveryIfReady(characterId) is ServiceResult.Success) {
            refreshCombatHp()
        }

        val session = state.session ?: return

        if (session.state == SessionState.SEARCHING) {
            val result = combatService.resolveSearchIfReady(characterId)
            if (result is ServiceResult.Success) {
                combatLogFor.getOrPut(characterId) { mutableListOf() }
                    .add(CombatLogEntry(result.value.name + " appears!"))
            }
            refreshCombatView()
            return
        }

        if (session.state != SessionState.IN_COMBAT) return

        val weapon = equippedWeapon(characterId)
        val trainingSkill = _trainingSkill.value
        val accuracy: Int
        val maxHit: Int
        when (weapon?.style) {
            CombatStyle.MAGIC -> {
                val magicLevel = skillLevel(characterId, SkillType.MAGIC)
                accuracy = magicLevel * 2 + weapon.baseAccuracy
                maxHit = (magicLevel / 3) + weapon.baseMaxHit
            }
            CombatStyle.RANGED -> {
                val archeryLevel = skillLevel(characterId, SkillType.ARCHERY)
                accuracy = archeryLevel * 2 + weapon.baseAccuracy
                maxHit = (archeryLevel / 3) + weapon.baseMaxHit
            }
            else -> {
                val attackLevel = skillLevel(characterId, SkillType.ATTACK)
                val strengthLevel = skillLevel(characterId, SkillType.STRENGTH)
                accuracy = attackLevel * 2 + (weapon?.baseAccuracy ?: 5)
                maxHit = (strengthLevel / 3) + (weapon?.baseMaxHit ?: 1)
            }
        }

        val loadout = CombatLoadout(
            style = weapon?.style ?: CombatStyle.MELEE,
            trainingSkill = trainingSkill,
            selectedPrayerId = inventoryService.inventoryFor(characterId).selectedPrayerId,
            equippedWeapon = weapon,
            equippedSpell = null,
            autoHealThresholdPercent = inventoryService.inventoryFor(characterId).autoHealThresholdPercent,
            autoFleeThresholdPercent = inventoryService.inventoryFor(characterId).autoFleeThresholdPercent
        )

        val result = combatService.resolveAttack(characterId, loadout, accuracy, maxHit)
        val log = combatLogFor.getOrPut(characterId) { mutableListOf() }

        if (result is ServiceResult.Success) {
            val attack = result.value
            val monsterDefense = session.currentMonster?.defenseRating ?: 1
            lastHitChancePercent = (accuracy.toDouble() / (accuracy + monsterDefense)) * 100.0
            lastDamageDealt = attack.damageDealt

            if (attack.didHit) {
                log.add(CombatLogEntry("You hit for " + attack.damageDealt + "."))
                val xpGrant = progressionService.grantXp(characterId, trainingSkill, (attack.damageDealt * 4 + 5).toLong())
                if (xpGrant is ServiceResult.Success) refreshSkills()
            } else {
                log.add(CombatLogEntry("You missed."))
            }

            if (attack.monsterDefeated) {
                val defeatedName = session.currentMonster?.name ?: "the enemy"
                log.add(CombatLogEntry("Defeated " + defeatedName + "!"))
                val loot = combatService.collectLoot(characterId)
                if (loot is ServiceResult.Success && loot.value.isNotEmpty()) {
                    loot.value.forEach { entry ->
                        inventoryService.inventoryFor(characterId).addItem(entry.itemId, entry.minQty)
                        sessionDropsFor.getOrPut(characterId) { mutableMapOf() }.merge(entry.itemId, entry.minQty, Int::plus)
                    }
                    refreshInventory()
                }
                val coinsEarned = combatService.collectCoins(characterId)
                if (coinsEarned > 0) {
                    log.add(CombatLogEntry("Found " + coinsEarned + " coins."))
                    grantCombatCoins(characterId, coinsEarned)
                }
            }

            // Monsters don't have a dedicated offensive stat yet, so their counter-attack uses a flat
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
            }

            val freshState = combatService.stateFor(characterId, maxHpFor(characterId))
            if (freshState.currentHp <= 0) {
                log.add(CombatLogEntry("You were defeated and are recovering."))
            } else if (freshState.maxHp > 0 &&
                (freshState.currentHp * 100 / freshState.maxHp) <= inventoryService.inventoryFor(characterId).autoFleeThresholdPercent
            ) {
                combatService.leaveZone(characterId)
                log.add(CombatLogEntry("Fled to safety."))
            }
        }
        refreshCombatView()
    }""",
"""    private var combatActionProgressSeconds: Double = 0.0

    private fun tickCombat(elapsedSeconds: Long) {
        val characterId = _currentCharacterId.value ?: return
        val state = combatService.stateFor(characterId, maxHpFor(characterId))

        if (state.recovery.isRecovering()) {
            refreshCombatHp()
            return
        }
        if (combatService.resolveRecoveryIfReady(characterId) is ServiceResult.Success) {
            refreshCombatHp()
        }

        val session = state.session ?: return

        if (session.state == SessionState.SEARCHING) {
            val result = combatService.resolveSearchIfReady(characterId)
            if (result is ServiceResult.Success) {
                combatLogFor.getOrPut(characterId) { mutableListOf() }
                    .add(CombatLogEntry(result.value.name + " appears!"))
            }
            refreshCombatView()
            return
        }

        if (session.state != SessionState.IN_COMBAT) return

        val weapon = equippedWeapon(characterId)
        val trainingSkill = _trainingSkill.value
        val accuracy: Int
        val maxHit: Int
        val attackSpeedSeconds: Double
        when (weapon?.style) {
            CombatStyle.MAGIC -> {
                val magicLevel = skillLevel(characterId, SkillType.MAGIC)
                accuracy = magicLevel * 2 + weapon.baseAccuracy
                maxHit = (magicLevel / 3) + weapon.baseMaxHit
                attackSpeedSeconds = weapon.attackSpeedSeconds
            }
            CombatStyle.RANGED -> {
                val archeryLevel = skillLevel(characterId, SkillType.ARCHERY)
                accuracy = archeryLevel * 2 + weapon.baseAccuracy
                maxHit = (archeryLevel / 3) + weapon.baseMaxHit
                attackSpeedSeconds = weapon.attackSpeedSeconds
            }
            else -> {
                val attackLevel = skillLevel(characterId, SkillType.ATTACK)
                val strengthLevel = skillLevel(characterId, SkillType.STRENGTH)
                accuracy = attackLevel * 2 + (weapon?.baseAccuracy ?: 5)
                maxHit = (strengthLevel / 3) + (weapon?.baseMaxHit ?: 1)
                attackSpeedSeconds = weapon?.attackSpeedSeconds ?: 2.4
            }
        }

        combatActionProgressSeconds += elapsedSeconds
        if (combatActionProgressSeconds < attackSpeedSeconds) {
            refreshCombatView()
            return
        }

        val log = combatLogFor.getOrPut(characterId) { mutableListOf() }

        while (combatActionProgressSeconds >= attackSpeedSeconds) {
            combatActionProgressSeconds -= attackSpeedSeconds

            val loadout = CombatLoadout(
                style = weapon?.style ?: CombatStyle.MELEE,
                trainingSkill = trainingSkill,
                selectedPrayerId = inventoryService.inventoryFor(characterId).selectedPrayerId,
                equippedWeapon = weapon,
                equippedSpell = null,
                autoHealThresholdPercent = inventoryService.inventoryFor(characterId).autoHealThresholdPercent,
                autoFleeThresholdPercent = inventoryService.inventoryFor(characterId).autoFleeThresholdPercent
            )

            val result = combatService.resolveAttack(characterId, loadout, accuracy, maxHit)

            if (result is ServiceResult.Success) {
                val attack = result.value
                val monsterDefense = session.currentMonster?.defenseRating ?: 1
                lastHitChancePercent = (accuracy.toDouble() / (accuracy + monsterDefense)) * 100.0
                lastDamageDealt = attack.damageDealt

                if (attack.didHit) {
                    log.add(CombatLogEntry("You hit for " + attack.damageDealt + "."))
                    val xpGrant = progressionService.grantXp(characterId, trainingSkill, (attack.damageDealt * 4 + 5).toLong())
                    if (xpGrant is ServiceResult.Success) refreshSkills()
                } else {
                    log.add(CombatLogEntry("You missed."))
                }

                if (attack.monsterDefeated) {
                    val defeatedName = session.currentMonster?.name ?: "the enemy"
                    log.add(CombatLogEntry("Defeated " + defeatedName + "!"))
                    val loot = combatService.collectLoot(characterId)
                    if (loot is ServiceResult.Success && loot.value.isNotEmpty()) {
                        loot.value.forEach { entry ->
                            inventoryService.inventoryFor(characterId).addItem(entry.itemId, entry.minQty)
                            sessionDropsFor.getOrPut(characterId) { mutableMapOf() }.merge(entry.itemId, entry.minQty, Int::plus)
                        }
                        refreshInventory()
                    }
                    val coinsEarned = combatService.collectCoins(characterId)
                    if (coinsEarned > 0) {
                        log.add(CombatLogEntry("Found " + coinsEarned + " coins."))
                        grantCombatCoins(characterId, coinsEarned)
                    }
                }

                // Monsters don't have a dedicated offensive stat yet, so their counter-attack uses a flat
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
                }

                val freshState = combatService.stateFor(characterId, maxHpFor(characterId))
                if (freshState.currentHp <= 0) {
                    log.add(CombatLogEntry("You were defeated and are recovering."))
                    combatActionProgressSeconds = 0.0
                    break
                } else if (freshState.maxHp > 0 &&
                    (freshState.currentHp * 100 / freshState.maxHp) <= inventoryService.inventoryFor(characterId).autoFleeThresholdPercent
                ) {
                    combatService.leaveZone(characterId)
                    log.add(CombatLogEntry("Fled to safety."))
                    combatActionProgressSeconds = 0.0
                    break
                }
            }

            val postAttackSession = combatService.stateFor(characterId, maxHpFor(characterId)).session
            if (postAttackSession == null || postAttackSession.state != SessionState.IN_COMBAT) break
        }

        refreshCombatView()
    }""",
    "tickCombat"
)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("All 6 edits applied successfully.")
