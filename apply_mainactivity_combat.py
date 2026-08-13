path = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(path, "r") as f:
    content = f.read()

# --- 1. Remove demoZones() - replaced by gameViewModel.zoneSummaries. ---
old_demo_zones = '''private fun demoZones(): List<ZoneSummary> = listOf(
    ZoneSummary("goblin_camp", "Goblin Camp", 1, listOf("Goblin Grunt")),
    ZoneSummary("shadow_ruins", "Shadow Ruins", 20, listOf("Wraith")),
    ZoneSummary("frost_peak", "Frost Peak", 40, listOf("Ice Troll", "Frost Wolf"))
)

'''
assert content.count(old_demo_zones) == 1, "demoZones block not found or not unique"
content = content.replace(old_demo_zones, "", 1)

# --- 2. zones/trainingSkill/trainingSkillLevel now come from GameViewModel. ---
old_zones_line = "    val zones = remember { demoZones() }\n"
new_zones_line = (
    "    val zones = gameViewModel.zoneSummaries\n"
    "    val trainingSkill by gameViewModel.trainingSkill.collectAsState()\n"
    "    val trainingSkillLevel by gameViewModel.trainingSkillLevel.collectAsState()\n"
)
assert content.count(old_zones_line) == 1, "zones line not found or not unique"
content = content.replace(old_zones_line, new_zones_line, 1)

# --- 3. homeState HP now comes from combatHp instead of hardcoded null. ---
old_homestate = '''    val activeQueue by gameViewModel.activeQueueInfo.collectAsState()
    val currency by gameViewModel.currency.collectAsState()
    val homeState = HomeScreenState(
        activeQueue = activeQueue,
        softCurrency = currency.first,
        premiumCurrency = currency.second,
        currentHp = null,
        maxHp = null,
        isRecovering = false,
        unreadNotificationCount = 2
    )'''
new_homestate = '''    val activeQueue by gameViewModel.activeQueueInfo.collectAsState()
    val currency by gameViewModel.currency.collectAsState()
    val combatHp by gameViewModel.combatHp.collectAsState()
    val homeState = HomeScreenState(
        activeQueue = activeQueue,
        softCurrency = currency.first,
        premiumCurrency = currency.second,
        currentHp = combatHp?.first,
        maxHp = combatHp?.second,
        isRecovering = false,
        unreadNotificationCount = 2
    )'''
assert content.count(old_homestate) == 1, "homeState block not found or not unique"
content = content.replace(old_homestate, new_homestate, 1)

# --- 4. combatViewData now comes straight from GameViewModel instead of hand-built demo data. ---
old_combatviewdata = '''    var combatViewState by remember { mutableStateOf(CombatViewState.SEARCHING) }
    val demoCombatLog = remember {
        mutableStateListOf(CombatLogEntry("You entered Goblin Camp."), CombatLogEntry("Searching for an enemy..."))
    }

    val combatViewData = CombatViewData(
        zoneName = "Goblin Camp", viewState = combatViewState,
        searchEndsAt = if (combatViewState == CombatViewState.SEARCHING) Instant.now().plusSeconds(7) else null,
        monsterName = if (combatViewState == CombatViewState.IN_COMBAT) "Goblin Grunt" else null,
        monsterCurrentHp = if (combatViewState == CombatViewState.IN_COMBAT) 15 else null,
        monsterMaxHp = if (combatViewState == CombatViewState.IN_COMBAT) 25 else null,
        playerCurrentHp = 80, playerMaxHp = 100,
        lastHitChancePercent = if (combatViewState == CombatViewState.IN_COMBAT) 62.5 else null,
        lastDamageDealt = if (combatViewState == CombatViewState.IN_COMBAT) 4 else null,
        combatLog = demoCombatLog
    )'''
new_combatviewdata = "    val combatViewData by gameViewModel.combatViewData.collectAsState()"
assert content.count(old_combatviewdata) == 1, "combatViewData block not found or not unique"
content = content.replace(old_combatviewdata, new_combatviewdata, 1)

# --- 5. canEquip / lockedEquipSlots now check combatViewData?.viewState instead of the removed combatViewState var. ---
old_canequip = '''    fun canEquip(item: InventoryItemSummary): Pair<Boolean, String?> {
        if (item.category == InventoryCategory.TOOL) return true to null
        val locked = combatViewState == CombatViewState.IN_COMBAT
        return if (locked) false to "Locked during combat" else true to null
    }

    val lockedEquipSlots = remember(combatViewState) {
        if (combatViewState == CombatViewState.IN_COMBAT) {'''
new_canequip = '''    fun canEquip(item: InventoryItemSummary): Pair<Boolean, String?> {
        if (item.category == InventoryCategory.TOOL) return true to null
        val locked = combatViewData?.viewState == CombatViewState.IN_COMBAT
        return if (locked) false to "Locked during combat" else true to null
    }

    val lockedEquipSlots = remember(combatViewData) {
        if (combatViewData?.viewState == CombatViewState.IN_COMBAT) {'''
assert content.count(old_canequip) == 1, "canEquip/lockedEquipSlots block not found or not unique"
content = content.replace(old_canequip, new_canequip, 1)

# --- 6. Combat tab routing: real enterCombatZone/leaveCombatZone calls, real trainingSkillLevel gating,
#         and the new training-skill picker passed through to LoadoutScreen. ---
old_combat_routing = '''                            AppDestination.COMBAT -> when (combatScreenState) {
                                CombatScreenState.ZoneSelect -> ZoneSelectScreen(
                                    zones = zones, playerLevel = 24,
                                    onZoneSelected = { combatScreenState = CombatScreenState.InZone; combatViewState = CombatViewState.SEARCHING },
                                    onOpenLoadout = { combatScreenState = CombatScreenState.Loadout }
                                )
                                CombatScreenState.InZone -> CombatViewScreen(data = combatViewData, onLeaveZone = { combatScreenState = CombatScreenState.ZoneSelect })
                                CombatScreenState.Loadout -> LoadoutScreen(
                                    state = LoadoutState(
                                        availableFoodOptions, loadoutSettings.selectedFoodId,
                                        availablePotionOptions, loadoutSettings.selectedPotionId,
                                        loadoutSettings.potionTimerRemainingSeconds,
                                        loadoutSettings.autoHealThresholdPercent, loadoutSettings.autoFleeThresholdPercent
                                    ),
                                    onBack = { combatScreenState = CombatScreenState.ZoneSelect },
                                    onFoodSelected = { gameViewModel.selectFood(it) },
                                    onPotionSelected = { gameViewModel.selectPotion(it) },
                                    onAutoHealChanged = { gameViewModel.setAutoHealThreshold(it) },
                                    onAutoFleeChanged = { gameViewModel.setAutoFleeThreshold(it) }
                                )
                            }'''
new_combat_routing = '''                            AppDestination.COMBAT -> when (combatScreenState) {
                                CombatScreenState.ZoneSelect -> ZoneSelectScreen(
                                    zones = zones, playerLevel = trainingSkillLevel,
                                    onZoneSelected = { zoneId ->
                                        val result = gameViewModel.enterCombatZone(zoneId)
                                        if (result is ServiceResult.Success) {
                                            combatScreenState = CombatScreenState.InZone
                                        }
                                    },
                                    onOpenLoadout = { combatScreenState = CombatScreenState.Loadout }
                                )
                                CombatScreenState.InZone -> {
                                    val currentCombatData = combatViewData
                                    if (currentCombatData != null) {
                                        CombatViewScreen(
                                            data = currentCombatData,
                                            onLeaveZone = {
                                                gameViewModel.leaveCombatZone()
                                                combatScreenState = CombatScreenState.ZoneSelect
                                            }
                                        )
                                    } else {
                                        combatScreenState = CombatScreenState.ZoneSelect
                                    }
                                }
                                CombatScreenState.Loadout -> LoadoutScreen(
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
                                )
                            }'''
assert content.count(old_combat_routing) == 1, "combat tab routing block not found or not unique"
content = content.replace(old_combat_routing, new_combat_routing, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: MainActivity.kt patched (real zones/combat view/HP wired in, all demo combat data removed).")
