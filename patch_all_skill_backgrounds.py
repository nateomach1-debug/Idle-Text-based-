import pathlib

path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")
text = path.read_text()

edits = []  # list of (label, old, new)

# 1. Import
edits.append((
    "import BackHandler",
    "import androidx.activity.compose.setContent",
    "import androidx.activity.compose.setContent\nimport androidx.activity.compose.BackHandler",
))

# 2. Top-level Home BackHandler
edits.append((
    "top-level Home BackHandler",
    "    var currentDestination by rememberSaveable { mutableStateOf(AppDestination.HOME) }",
    "    var currentDestination by rememberSaveable { mutableStateOf(AppDestination.HOME) }\n\n"
    "    BackHandler(enabled = currentDestination != AppDestination.HOME) {\n"
    "        currentDestination = AppDestination.HOME\n"
    "    }",
))

# 3. Skills: Detail -> List
edits.append((
    "Skills BackHandler",
    """                            AppDestination.SKILLS -> when (val screen = skillsScreenState) {
                                is SkillsScreenState.List -> SkillsScreen(
                                    allSkills = allSkills,
                                    onSkillSelected = { selectedSkillId ->
                                        if (selectedSkillId in COMBAT_TRAINING_SKILL_IDS) {
                                            when (val result = gameViewModel.setTrainingSkill(SkillType.valueOf(selectedSkillId))) {
                                                is ServiceResult.Failure -> Toast.makeText(context, result.reason, Toast.LENGTH_SHORT).show()
                                                is ServiceResult.Success -> {
                                                    currentDestination = AppDestination.COMBAT
                                                    combatScreenState = CombatScreenState.ZoneSelect
                                                }
                                            }
                                        } else {
                                            skillsScreenState = SkillsScreenState.Detail(selectedSkillId)
                                        }
                                    },
                                    listState = skillsListScrollState,
                                    gridState = skillsGridScrollState
                                )
                                is SkillsScreenState.Detail -> allSkills[screen.skillId]?.let {
                                    Box(modifier = Modifier.fillMaxSize()) {
                                        when (screen.skillId) {
                                            "SMITHING" -> SmithingScreen(
                                                buildSmithingState(
                                                    it,
                                                    inventoryQuantities,
                                                    hasCapeEquipped = equippedItemsForSkills[EquipSlot.CAPE] == "smithing_cape"
                                                ),
                                                { skillsScreenState = SkillsScreenState.List },
                                                { itemId -> gameViewModel.startCraftingAction(itemId) }
                                            )
                                            in RECIPE_BASED_SKILL_LABELS -> SkillDetailScreen(
                                                buildSkillDetailState(
                                                    screen.skillId,
                                                    it,
                                                    inventoryQuantities,
                                                    hasCapeEquipped = equippedItemsForSkills[EquipSlot.CAPE] == screen.skillId.lowercase() + "_cape"
                                                ),
                                                { skillsScreenState = SkillsScreenState.List },
                                                { itemId -> gameViewModel.startCraftingAction(itemId) },
                                                startButtonLabel = RECIPE_BASED_SKILL_LABELS.getValue(screen.skillId),
                                                activeQueue = activeQueue
                                            )
                                            else -> SkillDetailScreen(
                                                buildSkillDetailState(
                                                    screen.skillId,
                                                    it,
                                                    inventoryQuantities,
                                                    hasCapeEquipped = equippedItemsForSkills[EquipSlot.CAPE] == screen.skillId.lowercase() + "_cape"
                                                ),
                                                { skillsScreenState = SkillsScreenState.List },
                                                { actionId -> gameViewModel.startSkillAction(SkillType.valueOf(screen.skillId), actionId) },
                                                activeQueue = activeQueue
                                            )
                                        }
                                    }
                                }
                            }""",
    """                            AppDestination.SKILLS -> {
                                BackHandler(enabled = skillsScreenState is SkillsScreenState.Detail) {
                                    skillsScreenState = SkillsScreenState.List
                                }
                                when (val screen = skillsScreenState) {
                                is SkillsScreenState.List -> SkillsScreen(
                                    allSkills = allSkills,
                                    onSkillSelected = { selectedSkillId ->
                                        if (selectedSkillId in COMBAT_TRAINING_SKILL_IDS) {
                                            when (val result = gameViewModel.setTrainingSkill(SkillType.valueOf(selectedSkillId))) {
                                                is ServiceResult.Failure -> Toast.makeText(context, result.reason, Toast.LENGTH_SHORT).show()
                                                is ServiceResult.Success -> {
                                                    currentDestination = AppDestination.COMBAT
                                                    combatScreenState = CombatScreenState.ZoneSelect
                                                }
                                            }
                                        } else {
                                            skillsScreenState = SkillsScreenState.Detail(selectedSkillId)
                                        }
                                    },
                                    listState = skillsListScrollState,
                                    gridState = skillsGridScrollState
                                )
                                is SkillsScreenState.Detail -> allSkills[screen.skillId]?.let {
                                    Box(modifier = Modifier.fillMaxSize()) {
                                        when (screen.skillId) {
                                            "SMITHING" -> SmithingScreen(
                                                buildSmithingState(
                                                    it,
                                                    inventoryQuantities,
                                                    hasCapeEquipped = equippedItemsForSkills[EquipSlot.CAPE] == "smithing_cape"
                                                ),
                                                { skillsScreenState = SkillsScreenState.List },
                                                { itemId -> gameViewModel.startCraftingAction(itemId) }
                                            )
                                            in RECIPE_BASED_SKILL_LABELS -> SkillDetailScreen(
                                                buildSkillDetailState(
                                                    screen.skillId,
                                                    it,
                                                    inventoryQuantities,
                                                    hasCapeEquipped = equippedItemsForSkills[EquipSlot.CAPE] == screen.skillId.lowercase() + "_cape"
                                                ),
                                                { skillsScreenState = SkillsScreenState.List },
                                                { itemId -> gameViewModel.startCraftingAction(itemId) },
                                                startButtonLabel = RECIPE_BASED_SKILL_LABELS.getValue(screen.skillId),
                                                activeQueue = activeQueue
                                            )
                                            else -> SkillDetailScreen(
                                                buildSkillDetailState(
                                                    screen.skillId,
                                                    it,
                                                    inventoryQuantities,
                                                    hasCapeEquipped = equippedItemsForSkills[EquipSlot.CAPE] == screen.skillId.lowercase() + "_cape"
                                                ),
                                                { skillsScreenState = SkillsScreenState.List },
                                                { actionId -> gameViewModel.startSkillAction(SkillType.valueOf(screen.skillId), actionId) },
                                                activeQueue = activeQueue
                                            )
                                        }
                                    }
                                }
                            }
                            }""",
))

# 4. Combat: InZone/Loadout -> ZoneSelect (leaves zone server-side if InZone)
edits.append((
    "Combat BackHandler",
    """                            AppDestination.COMBAT -> when (combatScreenState) {
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
                                    onAutoFleeChanged = { gameViewModel.setAutoFleeThreshold(it) },
                                    selectedPrayerId = loadoutSettings.selectedPrayerId,
                                    prayerOptions = gameViewModel.prayerOptions,
                                    prayerLevel = allSkills["PRAYER"]?.level ?: 1,
                                    onPrayerSelected = { gameViewModel.selectPrayer(it) }
                                )
                            }""",
    """                            AppDestination.COMBAT -> {
                                BackHandler(enabled = combatScreenState != CombatScreenState.ZoneSelect) {
                                    if (combatScreenState == CombatScreenState.InZone) {
                                        gameViewModel.leaveCombatZone()
                                    }
                                    combatScreenState = CombatScreenState.ZoneSelect
                                }
                                when (combatScreenState) {
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
                                    onAutoFleeChanged = { gameViewModel.setAutoFleeThreshold(it) },
                                    selectedPrayerId = loadoutSettings.selectedPrayerId,
                                    prayerOptions = gameViewModel.prayerOptions,
                                    prayerLevel = allSkills["PRAYER"]?.level ?: 1,
                                    onPrayerSelected = { gameViewModel.selectPrayer(it) }
                                )
                            }
                            }""",
))

# 5. Inventory: Equipment/Loadout -> Items
edits.append((
    "Inventory BackHandler",
    """                            AppDestination.INVENTORY -> when (inventoryScreenState) {
                                InventoryScreenState.Items -> InventoryScreen(
                                    items = inventoryItems,
                                    onOpenEquipment = { inventoryScreenState = InventoryScreenState.Equipment },
                                    onOpenLoadout = { inventoryScreenState = InventoryScreenState.Loadout },
                                    onUseItem = { itemId -> gameViewModel.useInventoryItem(itemId) },
                                    onSellOnMarket = { itemId ->
                                        val item = inventoryItems.find { it.itemId == itemId }
                                        selectedMarketItemId = itemId
                                        prefilledSellQuantity = item?.quantity
                                        currentDestination = AppDestination.MARKET
                                    },
                                    onEquipItem = { itemId -> gameViewModel.equipItem(itemId) },
                                    onBuryItem = { itemId, qty -> gameViewModel.startBuryAction(itemId, qty) },
                                    canEquip = ::canEquip,
                                    canBury = ::canBury
                                )
                                InventoryScreenState.Equipment -> EquipmentScreen(
                                    state = EquipmentScreenState(equipped, lockedEquipSlots),
                                    onBack = { inventoryScreenState = InventoryScreenState.Items },
                                    onSlotTapped = { slot -> gameViewModel.unequipSlot(EquipSlot.valueOf(slot.name)) }
                                )
                                InventoryScreenState.Loadout -> LoadoutScreen(
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
                                )
                            }""",
    """                            AppDestination.INVENTORY -> {
                                BackHandler(enabled = inventoryScreenState != InventoryScreenState.Items) {
                                    inventoryScreenState = InventoryScreenState.Items
                                }
                                when (inventoryScreenState) {
                                InventoryScreenState.Items -> InventoryScreen(
                                    items = inventoryItems,
                                    onOpenEquipment = { inventoryScreenState = InventoryScreenState.Equipment },
                                    onOpenLoadout = { inventoryScreenState = InventoryScreenState.Loadout },
                                    onUseItem = { itemId -> gameViewModel.useInventoryItem(itemId) },
                                    onSellOnMarket = { itemId ->
                                        val item = inventoryItems.find { it.itemId == itemId }
                                        selectedMarketItemId = itemId
                                        prefilledSellQuantity = item?.quantity
                                        currentDestination = AppDestination.MARKET
                                    },
                                    onEquipItem = { itemId -> gameViewModel.equipItem(itemId) },
                                    onBuryItem = { itemId, qty -> gameViewModel.startBuryAction(itemId, qty) },
                                    canEquip = ::canEquip,
                                    canBury = ::canBury
                                )
                                InventoryScreenState.Equipment -> EquipmentScreen(
                                    state = EquipmentScreenState(equipped, lockedEquipSlots),
                                    onBack = { inventoryScreenState = InventoryScreenState.Items },
                                    onSlotTapped = { slot -> gameViewModel.unequipSlot(EquipSlot.valueOf(slot.name)) }
                                )
                                InventoryScreenState.Loadout -> LoadoutScreen(
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
                                )
                            }
                            }""",
))

# 6. Market: order-book detail -> Browse tab -> (falls through to Home via top-level handler)
edits.append((
    "Market BackHandler",
    "                                val itemId = selectedMarketItemId\n                                if (itemId != null) {",
    "                                val itemId = selectedMarketItemId\n\n"
    "                                BackHandler(enabled = itemId != null) {\n"
    "                                    selectedMarketItemId = null\n"
    "                                    prefilledSellQuantity = null\n"
    "                                }\n"
    "                                BackHandler(enabled = itemId == null && marketTab != MarketTab.BROWSE) {\n"
    "                                    marketTab = MarketTab.BROWSE\n"
    "                                }\n\n"
    "                                if (itemId != null) {",
))

errors = []
for label, old, new in edits:
    count = text.count(old)
    if count != 1:
        errors.append(f"  - {label}: expected 1 match, found {count}")

if errors:
    raise SystemExit(
        "PATCH FAILED: one or more expected blocks did not match exactly once. "
        "No changes made to the file.\n" + "\n".join(errors)
    )

for label, old, new in edits:
    text = text.replace(old, new)

path.write_text(text)
print(f"Patched MainActivity.kt: applied {len(edits)} back-navigation edits successfully.")
