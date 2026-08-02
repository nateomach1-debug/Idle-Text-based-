package com.yourname.idlerpg

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.ui.unit.dp
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import com.yourname.idlerpg.data.GameViewModel
import com.yourname.idlerpg.ui.components.RecoveryBar
import com.yourname.idlerpg.ui.components.ChatBanner
import com.yourname.idlerpg.ui.components.ChatChannelUi
import com.yourname.idlerpg.ui.components.ChatMessageUi
import com.yourname.idlerpg.ui.components.DmConversationSummary
import com.yourname.idlerpg.ui.components.ChatMessageAction
import com.yourname.idlerpg.ui.navigation.AppDestination
import com.yourname.idlerpg.ui.navigation.SideRail
import com.yourname.idlerpg.ui.screens.*
import com.yourname.idlerpg.ui.theme.IdleRpgTheme
import java.time.Instant

class MainActivity : ComponentActivity() {
    private val gameViewModel: GameViewModel by viewModels()
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            IdleRpgTheme {
                AppRoot(gameViewModel)
            }
        }
    }
override fun onPause() {
        super.onPause()
        gameViewModel.saveGame()
    }
}



private fun effectSummaryText(effect: Effect): String = when (effect) {
    is Effect.AccessUnlock -> effect.description
    is Effect.XpBoost -> "+" + effect.percent + "% XP"
    is Effect.DropRateBoost -> "+" + effect.percent + "% drop rate"
    is Effect.CostDiscount -> "-" + effect.percent + "% cost"
    is Effect.FlatStatBonus -> "+" + effect.amount + " " + effect.statName
    is Effect.TimerReduction -> "-" + effect.percent + "% action time"
}

private val RECIPE_BASED_SKILL_LABELS: Map<String, String> = mapOf(
    "CRAFTING" to "Select Recipe",
    "COOKING" to "Select Dish",
    "FLETCHING" to "Select Item",
    "ALCHEMY" to "Select Potion"
)

private fun buildSkillDetailState(skillId: String, summary: SkillSummary): SkillDetailState {
    val skillType = SkillType.valueOf(skillId)

    val earned = UnlockTable.unlocksEarnedAt(skillType, summary.level).map { unlock ->
        SkillUnlockSummary(
            description = unlock.grantedEffects.joinToString(", ") { effectSummaryText(it) },
            levelRequired = unlock.levelRequired
        )
    }

    val next = UnlockTable.allUnlocksFor(skillType)
        .filter { it.levelRequired > summary.level }
        .minByOrNull { it.levelRequired }
        ?.let { unlock ->
            SkillUnlockSummary(
                description = unlock.grantedEffects.joinToString(", ") { effectSummaryText(it) },
                levelRequired = unlock.levelRequired
            )
        }

    val actions = if (skillId in RECIPE_BASED_SKILL_LABELS) {
        RecipeCatalog.recipes
            .filter { it.skillRequired == skillId && it.levelRequired <= summary.level }
            .map { SkillActionSummary(it.outputItemId, ItemCatalog.find(it.outputItemId)?.name ?: it.outputItemId, it.levelRequired) }
            .sortedBy { it.levelRequired }
    } else {
        ActionCatalog.allFor(skillType)
            .filter { it.levelRequired <= summary.level }
            .map { SkillActionSummary(it.itemId, it.displayName, it.levelRequired) }
    }

    return SkillDetailState(
        skillId = summary.skillId, displayName = summary.displayName, level = summary.level,
        currentXp = summary.currentXp, xpToNextLevel = summary.xpToNextLevel,
        earnedUnlocks = earned,
        nextUnlock = next,
        availableActions = actions
    )
}

private val SMITHING_METALS = listOf(
    Triple("bronze", "Bronze", "bronze_bar"),
    Triple("iron", "Iron", "iron_bar"),
    Triple("steel", "Steel", "steel_bar"),
    Triple("mithril", "Mithril", "mithril_bar"),
    Triple("adamant", "Adamant", "adamantite_bar"),
    Triple("rune", "Rune", "runite_bar"),
    Triple("orichalcum", "Orichalcum", "orichalcum_bar"),
    Triple("celestial", "Celestial", "celestial_alloy_bar")
)

private fun recipeToSmithingSummary(recipe: Recipe): SmithingRecipeSummary {
    val displayName = ItemCatalog.find(recipe.outputItemId)?.name ?: recipe.outputItemId
    val ingredients = recipe.ingredients.map { ing ->
        val ingName = ItemCatalog.find(ing.itemId)?.name ?: ing.itemId
        SmithingIngredientSummary(ing.itemId, ingName, ing.quantity)
    }
    return SmithingRecipeSummary(recipe.outputItemId, displayName, recipe.levelRequired, ingredients)
}

private fun buildSmithingState(summary: SkillSummary): SmithingState {
    val materials = SMITHING_METALS.map { (materialId, displayName, barItemId) ->
        val barRecipe = RecipeCatalog.forOutput(barItemId)?.let { recipeToSmithingSummary(it) }
        val gearRecipes = RecipeCatalog.recipes
            .filter { it.skillRequired == "SMITHING" && it.ingredients.any { ing -> ing.itemId == barItemId } }
            .map { recipeToSmithingSummary(it) }
            .sortedBy { it.levelRequired }
        SmithingMaterialCatalogEntry(
            material = SmithingMaterialOption(materialId, displayName),
            bar = barRecipe,
            gear = gearRecipes
        )
    }
    return SmithingState(
        displayName = summary.displayName,
        level = summary.level,
        currentXp = summary.currentXp,
        xpToNextLevel = summary.xpToNextLevel,
        materials = materials
    )
}

private fun demoZones(): List<ZoneSummary> = listOf(
    ZoneSummary("goblin_camp", "Goblin Camp", 1, listOf("Goblin Grunt")),
    ZoneSummary("shadow_ruins", "Shadow Ruins", 20, listOf("Wraith")),
    ZoneSummary("frost_peak", "Frost Peak", 40, listOf("Ice Troll", "Frost Wolf"))
)

private fun demoWeapons(style: CombatStyleOption): List<WeaponOption> = when (style) {
    CombatStyleOption.MELEE -> listOf(
        WeaponOption("bronze_sword", "Bronze Sword", CombatStyleOption.MELEE),
        WeaponOption("iron_sword_common", "Iron Sword", CombatStyleOption.MELEE)
    )
    CombatStyleOption.RANGED -> listOf(WeaponOption("shortbow", "Shortbow", CombatStyleOption.RANGED))
    CombatStyleOption.MAGIC -> listOf(WeaponOption("spark_bolt", "Spark Bolt Staff", CombatStyleOption.MAGIC))
}

private fun mapItemCategory(category: ItemCategory): InventoryCategory = when (category) {
    ItemCategory.WEAPON -> InventoryCategory.WEAPON
    ItemCategory.ARMOR -> InventoryCategory.ARMOR
    ItemCategory.ACCESSORY -> InventoryCategory.ACCESSORY
    ItemCategory.MATERIAL -> InventoryCategory.MATERIAL
    ItemCategory.CONSUMABLE -> InventoryCategory.CONSUMABLE
    ItemCategory.COSMETIC -> InventoryCategory.MATERIAL
}

private fun buildInventoryItemSummaries(entries: List<InventorySlotEntry>): List<InventoryItemSummary> {
    return entries.map { entry ->
        val definition = ItemCatalog.find(entry.itemId)
        if (definition != null) {
            val statsText = if (!definition.stats.isAllZero()) {
                listOfNotNull(
                    definition.stats.attackBonus.takeIf { it != 0 }?.let { "ATK +" + it },
                    definition.stats.accuracyBonus.takeIf { it != 0 }?.let { "ACC +" + it },
                    definition.stats.maxHitBonus.takeIf { it != 0 }?.let { "Max Hit +" + it },
                    definition.stats.defenseBonus.takeIf { it != 0 }?.let { "DEF +" + it },
                    definition.stats.strengthBonus.takeIf { it != 0 }?.let { "STR +" + it }
                ).joinToString(", ")
            } else null

            InventoryItemSummary(
                itemId = entry.itemId,
                displayName = definition.name,
                category = mapItemCategory(definition.category),
                quantity = entry.quantity,
                isEquippable = definition.equipSlot != null,
                isConsumable = definition.category == ItemCategory.CONSUMABLE,
                npcValuePerUnit = ItemCatalog.baseValueFor(entry.itemId),
                statsDescription = statsText
            )
        } else {
            // Not yet defined in ItemCatalog (e.g. some gathered materials) -- graceful fallback.
            InventoryItemSummary(
                itemId = entry.itemId,
                displayName = entry.itemId.split("_").joinToString(" ") { it.replaceFirstChar { c -> c.uppercase() } },
                category = InventoryCategory.MATERIAL,
                quantity = entry.quantity,
                isEquippable = false,
                isConsumable = false,
                npcValuePerUnit = ItemCatalog.baseValueFor(entry.itemId)
            )
        }
    }
}

private fun demoEquipped(): Map<EquipSlotUi, EquippedItemInfo?> = mapOf(
    EquipSlotUi.WEAPON to EquippedItemInfo("bronze_sword", "Bronze Sword"),
    EquipSlotUi.HELMET to null,
    EquipSlotUi.CHESTPLATE to null,
    EquipSlotUi.GLOVES to null,
    EquipSlotUi.BOOTS to EquippedItemInfo("leather_boots_common", "Leather Boots"),
    EquipSlotUi.NECKLACE to null,
    EquipSlotUi.RING_1 to null,
    EquipSlotUi.RING_2 to null,
    EquipSlotUi.TOOL to EquippedItemInfo("pickaxe_bronze", "Bronze Pickaxe")
)

private fun demoMarketListings(): List<MarketListingSummary> = listOf(
    MarketListingSummary("iron_ore", "Iron Ore", bestBuyPrice = 9, bestSellPrice = 11),
    MarketListingSummary("steel_bar", "Steel Bar", bestBuyPrice = 40, bestSellPrice = 48),
    MarketListingSummary("minor_healing_potion", "Minor Healing Potion", bestBuyPrice = 4, bestSellPrice = 6)
)

private fun demoOrderBook(itemId: String): ItemOrderBookDetail {
    val listing = demoMarketListings().find { it.itemId == itemId }
    return ItemOrderBookDetail(
        itemId = itemId,
        displayName = listing?.displayName ?: itemId,
        bestBuyPrice = listing?.bestBuyPrice,
        bestSellPrice = listing?.bestSellPrice,
        recentTrades = listOf(
            PriceHistoryRow(11, 20, "5m ago"),
            PriceHistoryRow(10, 15, "22m ago"),
            PriceHistoryRow(12, 5, "1h ago")
        )
    )
}

private fun demoMyBuyOrders(): List<MarketOrderSummary> = listOf(
    MarketOrderSummary("order1", "iron_ore", "Iron Ore", 9, 30)
)

private fun demoMySellOrders(): List<MarketOrderSummary> = listOf(
    MarketOrderSummary("order2", "steel_bar", "Steel Bar", 48, 8)
)

private fun demoGuildMembers(): List<GuildMemberSummary> = listOf(
    GuildMemberSummary("char1", "Lyra", GuildMemberRole.LEADER),
    GuildMemberSummary("char2", "Bram", GuildMemberRole.OFFICER),
    GuildMemberSummary("char3", "Sable", GuildMemberRole.MEMBER),
    GuildMemberSummary("char4", "Quinn", GuildMemberRole.MEMBER)
)

private fun demoGuildState(): GuildHomeState = GuildHomeState(
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
)

private fun demoLeaderboard(): List<GuildLeaderboardEntry> = listOf(
    GuildLeaderboardEntry("Lyra", 15200),
    GuildLeaderboardEntry("Bram", 9800),
    GuildLeaderboardEntry("Sable", 6100),
    GuildLeaderboardEntry("Quinn", 4200)
)

private fun demoChatMessages(): List<ChatMessageUi> = listOf(
    ChatMessageUi("m1", "Bram", "anyone selling steel bars?", ChatChannelUi.GLOBAL),
    ChatMessageUi("m2", "Sable", "check the market, saw some at 48 each", ChatChannelUi.GLOBAL),
    ChatMessageUi("m3", "Quinn", "gl on the hunt everyone", ChatChannelUi.GLOBAL)
)

private fun demoDmConversations(): List<DmConversationSummary> = listOf(
    DmConversationSummary("char2", "Bram", "hey, got a minute?"),
    DmConversationSummary("char3", "Sable", "thanks for the help earlier!")
)

private sealed class AppFlowState {
    object Login : AppFlowState()
    object CharacterSelect : AppFlowState()
    object CharacterCreate : AppFlowState()
    object InGame : AppFlowState()
}

private sealed class SkillsScreenState {
    object List : SkillsScreenState()
    data class Detail(val skillId: String) : SkillsScreenState()
}

private sealed class CombatScreenState {
    object ZoneSelect : CombatScreenState()
    object InZone : CombatScreenState()
    object Loadout : CombatScreenState()
}

private sealed class InventoryScreenState {
    object Items : InventoryScreenState()
    object Equipment : InventoryScreenState()
    object Loadout : InventoryScreenState()
}

@Composable
fun AppRoot(gameViewModel: GameViewModel) {
    val currentAccountId by gameViewModel.currentAccountId.collectAsState()
    val currentCharacterId by gameViewModel.currentCharacterId.collectAsState()
    var isCreatingAccount by remember { mutableStateOf(false) }
    var loginError by remember { mutableStateOf<String?>(null) }
    var flowState by remember {
        val accountIdSnapshot = currentAccountId
        mutableStateOf(
            when {
                currentCharacterId != null -> AppFlowState.InGame
                accountIdSnapshot != null -> {
                    val chars = gameViewModel.accountService.charactersFor(accountIdSnapshot)
                    if (chars.isEmpty()) AppFlowState.CharacterCreate else AppFlowState.CharacterSelect
                }
                else -> AppFlowState.Login
            }
        )
    }
    LaunchedEffect(Unit) {
        gameViewModel.loadGame()
        if (flowState == AppFlowState.Login) {
            val autoAccount = gameViewModel.tryAutoLogin()
            if (autoAccount != null) {
                val chars = gameViewModel.accountService.charactersFor(autoAccount.id)
                flowState = if (chars.isEmpty()) AppFlowState.CharacterCreate else AppFlowState.CharacterSelect
            }
        }
    }

    val offlineSummary by gameViewModel.offlineSummary.collectAsState()
    offlineSummary?.let { summary ->
        androidx.compose.material3.AlertDialog(
            onDismissRequest = { gameViewModel.clearOfflineSummary() },
            title = { androidx.compose.material3.Text("Welcome back!") },
            text = {
                val minutes = summary.awaySeconds / 60
                val awayText = if (minutes < 1) "under a minute" else minutes.toString() + " minute(s)"
                androidx.compose.material3.Text(
                    "You were away for " + awayText + ".\n\n" +
                    "While gone, you were " + summary.skillActionName + ":\n" +
                    "+" + summary.xpEarned + " XP\n" +
                    "Gathered " + summary.quantity + "x " + summary.itemName
                )
            },
            confirmButton = {
                androidx.compose.material3.TextButton(onClick = { gameViewModel.clearOfflineSummary() }) {
                    androidx.compose.material3.Text("Nice!")
                }
            }
        )
    }

    var currentDestination by remember { mutableStateOf(AppDestination.HOME) }
    var skillsScreenState by remember { mutableStateOf<SkillsScreenState>(SkillsScreenState.List) }
    var combatScreenState by remember { mutableStateOf<CombatScreenState>(CombatScreenState.ZoneSelect) }
    var inventoryScreenState by remember { mutableStateOf<InventoryScreenState>(InventoryScreenState.Items) }

    val allSkills by gameViewModel.skills.collectAsState()
    val zones = remember { demoZones() }
    val inventoryItemEntries by gameViewModel.inventoryItems.collectAsState()
    val inventoryItems = remember(inventoryItemEntries) { buildInventoryItemSummaries(inventoryItemEntries) }
    val equipped = remember { demoEquipped() }

    val homeState = remember {
        HomeScreenState("Mining Iron Ore", Instant.now().plusSeconds(90), 1250, 40, 80, 100, false, 3, 2)
    }

    val recoveringUntil = remember { mutableStateOf<Instant?>(null) }

    var loadoutStyle by remember { mutableStateOf(CombatStyleOption.MELEE) }
    var loadoutWeaponId by remember { mutableStateOf<String?>("bronze_sword") }
    var autoHeal by remember { mutableStateOf(30) }
    var autoFlee by remember { mutableStateOf(10) }

    var combatViewState by remember { mutableStateOf(CombatViewState.SEARCHING) }
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
    )

    fun canEquip(item: InventoryItemSummary): Pair<Boolean, String?> {
        if (item.category == InventoryCategory.TOOL) return true to null
        val locked = combatViewState == CombatViewState.IN_COMBAT
        return if (locked) false to "Locked during combat" else true to null
    }

    val lockedEquipSlots = remember(combatViewState) {
        if (combatViewState == CombatViewState.IN_COMBAT) {
            setOf(
                EquipSlotUi.WEAPON, EquipSlotUi.HELMET, EquipSlotUi.CHESTPLATE, EquipSlotUi.GLOVES,
                EquipSlotUi.BOOTS, EquipSlotUi.NECKLACE, EquipSlotUi.RING_1, EquipSlotUi.RING_2,
                EquipSlotUi.LEGS, EquipSlotUi.SHIELD, EquipSlotUi.CAPE, EquipSlotUi.AMMO
            )
        } else emptySet()
    }

    var marketTab by remember { mutableStateOf(MarketTab.BROWSE) }
    var showingBuyOrders by remember { mutableStateOf(false) }
    var selectedMarketItemId by remember { mutableStateOf<String?>(null) }
    var prefilledSellQuantity by remember { mutableStateOf<Int?>(null) }

    var leaderboardShowingDaily by remember { mutableStateOf(false) }
    var selectedGuildMember by remember { mutableStateOf<GuildMemberSummary?>(null) }

    var selectedChatChannel by remember { mutableStateOf(ChatChannelUi.GLOBAL) }
    var selectedDmCharacterId by remember { mutableStateOf<String?>(null) }
    var chatMessageInput by remember { mutableStateOf("") }
    val chatMessages = remember { mutableStateListOf(*demoChatMessages().toTypedArray()) }

    when (flowState) {
        AppFlowState.Login -> {
            LoginScreen(
                isCreatingAccount = isCreatingAccount,
                onToggleMode = { isCreatingAccount = !isCreatingAccount; loginError = null },
                errorMessage = loginError,
                onLogin = { email, password ->
                    val result = gameViewModel.login(email, password)
                    when (result) {
                        is ServiceResult.Success -> {
                            val chars = gameViewModel.accountService.charactersFor(result.value.id)
                            flowState = if (chars.isEmpty()) AppFlowState.CharacterCreate else AppFlowState.CharacterSelect
                            loginError = null
                        }
                        is ServiceResult.Failure -> loginError = result.reason
                    }
                },
                onCreateAccount = { email, username, password ->
                    val result = gameViewModel.createAccount(email, username, password)
                    when (result) {
                        is ServiceResult.Success -> {
                            gameViewModel.saveGame()
                            loginError = null
                            flowState = AppFlowState.CharacterCreate
                        }
                        is ServiceResult.Failure -> loginError = result.reason
                    }
                }
            )
        }

        AppFlowState.CharacterCreate -> {
            CharacterCreateScreen(
                errorMessage = loginError,
                onCreate = { displayName, avatarId ->
                    val accountId = currentAccountId
                    if (accountId != null) {
                        val result = gameViewModel.accountService.createCharacter(accountId, displayName, avatarId)
                        when (result) {
                            is ServiceResult.Success -> {
    gameViewModel.accountService.setMainCharacter(result.value.id)
    gameViewModel.selectCharacter(result.value.id)
    gameViewModel.saveGame()
    loginError = null
    flowState = AppFlowState.InGame
}
                            is ServiceResult.Failure -> loginError = result.reason
                        }
                    }
                }
            )
        }

        AppFlowState.CharacterSelect -> {
            val accountId = currentAccountId
            if (accountId != null) {
                val chars = gameViewModel.accountService.charactersFor(accountId).map {
                    CharacterSummaryUi(it.id, it.displayName, it.avatarId)
                }
                CharacterSelectScreen(
                    characters = chars,
                    onCharacterSelected = {
    gameViewModel.selectCharacter(it)
    flowState = AppFlowState.InGame
},
                    onCreateNew = { flowState = AppFlowState.CharacterCreate }
                )
            }
        }

        AppFlowState.InGame -> {
            Surface(modifier = Modifier.fillMaxSize()) {
                Column(modifier = Modifier.fillMaxSize()) {
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 4.dp),
                        horizontalArrangement = androidx.compose.foundation.layout.Arrangement.End
                    ) {
                        androidx.compose.material3.TextButton(onClick = {
                            gameViewModel.logout()
                            flowState = AppFlowState.Login
                        }) {
                            androidx.compose.material3.Text("Log Out")
                        }
                    }
                    RecoveryBar(recoveringUntil = recoveringUntil.value)

                    Row(modifier = Modifier.fillMaxSize().weight(1f)) {
                        SideRail(
                            currentDestination = currentDestination,
                            onDestinationSelected = {
                                currentDestination = it
                                skillsScreenState = SkillsScreenState.List
                                combatScreenState = CombatScreenState.ZoneSelect
                                inventoryScreenState = InventoryScreenState.Items
                                marketTab = MarketTab.BROWSE
                                selectedMarketItemId = null
                            },
                            badgedDestinations = setOf(AppDestination.CHAT, AppDestination.GUILD)
                        )

                        when (currentDestination) {
                            AppDestination.HOME -> HomeScreen(state = homeState, onCollectLoot = { })

                            AppDestination.SKILLS -> when (val screen = skillsScreenState) {
                                is SkillsScreenState.List -> SkillsScreen(
                                    allSkills = allSkills,
                                    onSkillSelected = { skillsScreenState = SkillsScreenState.Detail(it) }
                                )
                                is SkillsScreenState.Detail -> allSkills[screen.skillId]?.let {
                                    when (screen.skillId) {
                                        "SMITHING" -> SmithingScreen(
                                            buildSmithingState(it),
                                            { skillsScreenState = SkillsScreenState.List },
                                            { itemId -> gameViewModel.startCraftingAction(itemId) }
                                        )
                                        in RECIPE_BASED_SKILL_LABELS -> SkillDetailScreen(
                                            buildSkillDetailState(screen.skillId, it),
                                            { skillsScreenState = SkillsScreenState.List },
                                            { itemId -> gameViewModel.startCraftingAction(itemId) },
                                            startButtonLabel = RECIPE_BASED_SKILL_LABELS.getValue(screen.skillId)
                                        )
                                        else -> SkillDetailScreen(
                                            buildSkillDetailState(screen.skillId, it),
                                            { skillsScreenState = SkillsScreenState.List },
                                            { actionId -> gameViewModel.startSkillAction(SkillType.valueOf(screen.skillId), actionId) }
                                        )
                                    }
                                }
                            }

                            AppDestination.COMBAT -> when (combatScreenState) {
                                CombatScreenState.ZoneSelect -> ZoneSelectScreen(
                                    zones = zones, playerLevel = 24,
                                    onZoneSelected = { combatScreenState = CombatScreenState.InZone; combatViewState = CombatViewState.SEARCHING },
                                    onOpenLoadout = { combatScreenState = CombatScreenState.Loadout }
                                )
                                CombatScreenState.InZone -> CombatViewScreen(data = combatViewData, onLeaveZone = { combatScreenState = CombatScreenState.ZoneSelect })
                                CombatScreenState.Loadout -> LoadoutScreen(
                                    state = LoadoutState(
                                        loadoutStyle, demoWeapons(loadoutStyle), loadoutWeaponId, autoHeal, autoFlee,
                                        combatViewState == CombatViewState.IN_COMBAT, "Locked during combat"
                                    ),
                                    onBack = { combatScreenState = CombatScreenState.ZoneSelect },
                                    onStyleSelected = { loadoutStyle = it; loadoutWeaponId = demoWeapons(it).firstOrNull()?.itemId },
                                    onWeaponSelected = { loadoutWeaponId = it },
                                    onAutoHealChanged = { autoHeal = it },
                                    onAutoFleeChanged = { autoFlee = it }
                                )
                            }

                            AppDestination.INVENTORY -> when (inventoryScreenState) {
                                InventoryScreenState.Items -> InventoryScreen(
                                    items = inventoryItems,
                                    onOpenEquipment = { inventoryScreenState = InventoryScreenState.Equipment },
                                    onOpenLoadout = { inventoryScreenState = InventoryScreenState.Loadout },
                                    onUseItem = { },
                                    onSellOnMarket = { itemId ->
                                        val item = inventoryItems.find { it.itemId == itemId }
                                        selectedMarketItemId = itemId
                                        prefilledSellQuantity = item?.quantity
                                        currentDestination = AppDestination.MARKET
                                    },
                                    onEquipItem = { },
                                    canEquip = ::canEquip
                                )
                                InventoryScreenState.Equipment -> EquipmentScreen(
                                    state = EquipmentScreenState(equipped, lockedEquipSlots),
                                    onBack = { inventoryScreenState = InventoryScreenState.Items },
                                    onSlotTapped = { }
                                )
                                InventoryScreenState.Loadout -> LoadoutScreen(
                                    state = LoadoutState(
                                        loadoutStyle, demoWeapons(loadoutStyle), loadoutWeaponId, autoHeal, autoFlee,
                                        combatViewState == CombatViewState.IN_COMBAT, "Locked during combat"
                                    ),
                                    onBack = { inventoryScreenState = InventoryScreenState.Items },
                                    onStyleSelected = { loadoutStyle = it; loadoutWeaponId = demoWeapons(it).firstOrNull()?.itemId },
                                    onWeaponSelected = { loadoutWeaponId = it },
                                    onAutoHealChanged = { autoHeal = it },
                                    onAutoFleeChanged = { autoFlee = it }
                                )
                            }

                            AppDestination.MARKET -> {
                                val itemId = selectedMarketItemId
                                if (itemId != null) {
                                    OrderBookScreen(
                                        detail = demoOrderBook(itemId),
                                        prefilledQuantity = prefilledSellQuantity,
                                        onBack = { selectedMarketItemId = null; prefilledSellQuantity = null },
                                        onPlaceOrder = { _, _, _ -> selectedMarketItemId = null; prefilledSellQuantity = null }
                                    )
                                } else {
                                    MarketScreen(
                                        currentTab = marketTab,
                                        onTabSelected = { marketTab = it },
                                        listings = demoMarketListings(),
                                        showingBuyOrders = showingBuyOrders,
                                        onToggleBrowseMode = { showingBuyOrders = !showingBuyOrders },
                                        onItemSelected = { selectedMarketItemId = it },
                                        myBuyOrders = demoMyBuyOrders(),
                                        mySellOrders = demoMySellOrders(),
                                        onCancelOrder = { },
                                        vendorSellableItems = inventoryItems,
                                        onSellToVendor = { _, _ -> }
                                    )
                                }
                            }

                            AppDestination.GUILD -> {
                                GuildHomeScreen(
                                    state = demoGuildState(),
                                    leaderboardEntries = demoLeaderboard(),
                                    leaderboardShowingDaily = leaderboardShowingDaily,
                                    onToggleLeaderboardPeriod = { leaderboardShowingDaily = !leaderboardShowingDaily },
                                    onMemberTapped = { selectedGuildMember = it },
                                    onContributeToEvent = { },
                                    onCastVote = { }
                                )

                                selectedGuildMember?.let { member ->
                                    MemberActionPopup(
                                        member = member,
                                        viewerRole = GuildMemberRole.LEADER,
                                        onDismiss = { selectedGuildMember = null },
                                        onKick = { selectedGuildMember = null },
                                        onPromote = { selectedGuildMember = null },
                                        onDemote = { selectedGuildMember = null },
                                        onInitiateVote = { selectedGuildMember = null }
                                    )
                                }
                            }

                            else -> androidx.compose.material3.Text(
                                text = currentDestination.label + " screen coming soon",
                                modifier = Modifier.fillMaxSize()
                            )
                        }
                    }

                    ChatBanner(
                        selectedChannel = selectedChatChannel,
                        onChannelSelected = {
                            selectedChatChannel = it
                            if (it != ChatChannelUi.DMS) selectedDmCharacterId = null
                        },
                        messages = chatMessages.filter { it.channel == selectedChatChannel },
                        dmConversations = demoDmConversations(),
                        selectedDmCharacterId = selectedDmCharacterId,
                        onDmSelected = { selectedDmCharacterId = it },
                        hasUnread = true,
                        messageInput = chatMessageInput,
                        onMessageInputChanged = { chatMessageInput = it },
                        onSendMessage = {
                            if (chatMessageInput.isNotBlank()) {
                                chatMessages.add(ChatMessageUi("m" + (chatMessages.size + 1), "You", chatMessageInput, selectedChatChannel))
                                chatMessageInput = ""
                            }
                        },
                        onMessageAction = { _, _ -> }
                    )
                }
            }
        }
    }
}
