import re

path = "app/src/main/kotlin/com/yourname/idlerpg/data/GameViewModel.kt"
with open(path, "r") as f:
    content = f.read()

# --- 1. Add Random import ---
old_imports = "import kotlinx.coroutines.launch\nimport java.time.Instant\n"
new_imports = "import kotlinx.coroutines.launch\nimport java.time.Instant\nimport kotlin.random.Random\n"
assert content.count(old_imports) == 1, "import anchor not found or not unique"
content = content.replace(old_imports, new_imports, 1)

# --- 2. Insert the new combat block right after `val combatService = CombatService()`. ---
anchor2 = "    val combatService = CombatService()\n"
assert content.count(anchor2) == 1, "combatService anchor not found or not unique"

combat_block = anchor2 + '''
    // =========================================================
    // COMBAT
    // =========================================================

    private val _trainingSkill = MutableStateFlow(SkillType.ATTACK)
    val trainingSkill: StateFlow<SkillType> = _trainingSkill.asStateFlow()

    private val _trainingSkillLevel = MutableStateFlow(1)
    val trainingSkillLevel: StateFlow<Int> = _trainingSkillLevel.asStateFlow()

    private val _combatViewData = MutableStateFlow<CombatViewData?>(null)
    val combatViewData: StateFlow<CombatViewData?> = _combatViewData.asStateFlow()

    private val _combatHp = MutableStateFlow<Pair<Int, Int>?>(null)
    val combatHp: StateFlow<Pair<Int, Int>?> = _combatHp.asStateFlow()

    private var lastHitChancePercent: Double? = null
    private var lastDamageDealt: Int? = null
    private val combatLogFor: MutableMap<String, MutableList<CombatLogEntry>> = mutableMapOf()

    val zoneSummaries: List<ZoneSummary>
        get() = ZoneCatalog.zones.map { zone ->
            ZoneSummary(
                zoneId = zone.id,
                name = zone.name,
                levelRequirement = zone.levelRequirement,
                monsterNames = zone.monsters.map { it.name }
            )
        }

    val allowedTrainingSkills: List<SkillType>
        get() {
            val characterId = _currentCharacterId.value ?: return listOf(SkillType.DEFENSE)
            val style = equippedWeapon(characterId)?.style ?: CombatStyle.MELEE
            return CombatSkillRules.allowedTrainingSkills(style)
        }

    // Placeholder max-HP formula until a dedicated stat exists: base 100 + 5 per Defense level above 1.
    // Same "reasonable placeholder, tune later" approach used for food/potion heal amounts.
    private fun maxHpFor(characterId: String): Int {
        val defenseLevel = LevelCurve.levelForXp(progressionService.skillBookFor(characterId).get(SkillType.DEFENSE).xp)
        return 100 + (defenseLevel - 1) * 5
    }

    private fun equippedWeapon(characterId: String): Weapon? {
        val itemId = _equippedItems.value[EquipSlot.WEAPON] ?: return null
        val def = ItemCatalog.items.find { it.id == itemId } ?: return null
        val style = def.combatStyle ?: return null
        return Weapon(
            name = def.name,
            style = style,
            attackSpeedSeconds = 2.4,
            baseAccuracy = 5 + def.stats.accuracyBonus,
            baseMaxHit = 1 + def.stats.maxHitBonus
        )
    }

    private fun skillLevel(characterId: String, skillType: SkillType): Int =
        LevelCurve.levelForXp(progressionService.skillBookFor(characterId).get(skillType).xp)

    fun setTrainingSkill(skillType: SkillType) {
        _trainingSkill.value = skillType
        val characterId = _currentCharacterId.value
        _trainingSkillLevel.value = characterId?.let { skillLevel(it, skillType) } ?: 1
    }

    private fun refreshCombatHp() {
        val characterId = _currentCharacterId.value ?: return
        val state = combatService.stateFor(characterId, maxHpFor(characterId))
        _combatHp.value = state.currentHp to state.maxHp
    }

    fun enterCombatZone(zoneId: String): ServiceResult<CombatSession> {
        val characterId = _currentCharacterId.value ?: return ServiceResult.Failure("No character selected.")
        combatService.stateFor(characterId, maxHpFor(characterId))
        val result = combatService.enterZone(characterId, zoneId, skillLevel(characterId, _trainingSkill.value))
        if (result is ServiceResult.Success) {
            combatLogFor.getOrPut(characterId) { mutableListOf() }.apply {
                clear()
                add(CombatLogEntry("Entered " + result.value.zone.name + "."))
            }
            refreshCombatView()
        }
        return result
    }

    fun leaveCombatZone() {
        val characterId = _currentCharacterId.value ?: return
        combatService.leaveZone(characterId)
        _combatViewData.value = null
    }

    private fun refreshCombatView() {
        val characterId = _currentCharacterId.value ?: return
        val state = combatService.stateFor(characterId, maxHpFor(characterId))
        _combatHp.value = state.currentHp to state.maxHp
        val session = state.session
        if (session == null) {
            _combatViewData.value = null
            return
        }
        val log = combatLogFor.getOrPut(characterId) { mutableListOf() }
        _combatViewData.value = CombatViewData(
            zoneName = session.zone.name,
            viewState = if (session.state == SessionState.IN_COMBAT) CombatViewState.IN_COMBAT else CombatViewState.SEARCHING,
            searchEndsAt = session.searchEndsAt,
            monsterName = session.currentMonster?.name,
            monsterCurrentHp = session.currentMonster?.let { session.currentMonsterHealth },
            monsterMaxHp = session.currentMonster?.maxHealth,
            playerCurrentHp = state.currentHp,
            playerMaxHp = state.maxHp,
            lastHitChancePercent = lastHitChancePercent,
            lastDamageDealt = lastDamageDealt,
            combatLog = log
        )
    }

    private fun tickCombat() {
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
                    loot.value.forEach { entry -> inventoryService.inventoryFor(characterId).addItem(entry.itemId, entry.minQty) }
                    refreshInventory()
                }
            }

            // Monsters don't have a dedicated offensive stat yet, so their counter-attack uses a flat
            // hit chance with damage scaled off defenseRating as a stand-in. Placeholder, same spirit
            // as the maxHp formula above - safe to retune once real monster balance is worked out.
            val monster = session.currentMonster
            if (monster != null && Random.nextDouble(0.0, 100.0) < 40.0) {
                val dmg = Random.nextInt(1, (monster.defenseRating / 3).coerceAtLeast(1) + 1)
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
    }
'''
content = content.replace(anchor2, combat_block, 1)

# --- 3. tickConsumables gains a refreshCombatHp() call at the end (HP visible on Home even without an active session). ---
old_tick_consumables = '''    private fun tickConsumables() {
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
    }'''
new_tick_consumables = old_tick_consumables.replace(
    "        refreshInventory()\n    }",
    "        refreshInventory()\n        refreshCombatHp()\n    }",
    1
)
assert content.count(old_tick_consumables) == 1, "tickConsumables block not found or not unique"
content = content.replace(old_tick_consumables, new_tick_consumables, 1)

# --- 4. Hook tickCombat() into the existing per-second loop, right after tickConsumables(). ---
old_loop = '''                tickSkilling()
            tickCrafting()
            tickConsumables()
            }'''
new_loop = '''                tickSkilling()
            tickCrafting()
            tickConsumables()
            tickCombat()
            }'''
assert content.count(old_loop) == 1, "per-second loop block not found or not unique"
content = content.replace(old_loop, new_loop, 1)

# --- 5. refreshSkills() also refreshes trainingSkillLevel, since combat XP changes it just like any other skill. ---
old_refresh_skills = '''    fun refreshSkills() {
        val characterId = _currentCharacterId.value ?: return
        val book = progressionService.skillBookFor(characterId)
        _skills.value = book.all().associate { skill ->
            val level = LevelCurve.levelForXp(skill.xp)
            val xpAtLevelStart = LevelCurve.xpRequiredForLevel(level)
            val xpAtNextLevel = LevelCurve.xpRequiredForLevel(level + 1)
            val displayName = skill.type.name.lowercase().replaceFirstChar { it.uppercase() }
            skill.type.name to SkillSummary(
                skillId = skill.type.name,
                displayName = displayName,
                level = level,
                currentXp = skill.xp - xpAtLevelStart,
                xpToNextLevel = xpAtNextLevel - skill.xp
            )
        }
    }'''
new_refresh_skills = old_refresh_skills.replace(
    "        }\n    }",
    "        }\n        _trainingSkillLevel.value = _skills.value[_trainingSkill.value.name]?.level ?: 1\n    }",
    1
)
assert content.count(old_refresh_skills) == 1, "refreshSkills block not found or not unique"
content = content.replace(old_refresh_skills, new_refresh_skills, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: GameViewModel.kt patched (combat driving logic added, tick loop hooked, refreshSkills extended).")
