package com.yourname.idlerpg

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
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



private fun demoDetailFor(skillId: String, summary: SkillSummary): SkillDetailState {
    return SkillDetailState(
        skillId = summary.skillId, displayName = summary.displayName, level = summary.level,
        currentXp = summary.currentXp, xpToNextLevel = summary.xpToNextLevel,
        earnedUnlocks = listOf(
            SkillUnlockSummary("Basic access unlocked", 1),
            SkillUnlockSummary("Improved yield", 10)
        ).filter { it.levelRequired <= summary.level },
        nextUnlock = SkillUnlockSummary("Advanced technique", summary.level + 5),
        availableActions = listOf(
            SkillActionSummary("action_basic", "Basic " + summary.displayName + " Action", 1),
            SkillActionSummary("action_advanced", "Advanced " + summary.displayName + " Action", 15)
        ).filter { it.levelRequired <= summary.level }
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

private fun demoInventoryItems(): List<InventoryItemSummary> = listOf(
    InventoryItemSummary("iron_sword_common", "Iron Sword", InventoryCategory.WEAPON, 1, true, false, 25, "ATK +5, ACC +10, Max Hit +6"),
    InventoryItemSummary("leather_boots_common", "Leather Boots", InventoryCategory.ARMOR, 1, true, false, 8, "DEF +3"),
    InventoryItemSummary("pickaxe_bronze", "Bronze Pickaxe", InventoryCategory.TOOL, 1, true, false, 12, "Mining Tool"),
    InventoryItemSummary("iron_ore", "Iron Ore", InventoryCategory.MATERIAL, 47, false, false, 4),
    InventoryItemSummary("steel_bar", "Steel Bar", InventoryCategory.MATERIAL, 12, false, false, 18),
    InventoryItemSummary("minor_healing_potion", "Minor Healing Potion", InventoryCategory.CONSUMABLE, 6, false, true, 5)
)

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
    var flowState by remember { mutableStateOf<AppFlowState>(AppFlowState.Login) }
    var isCreatingAccount by remember { mutableStateOf(false) }
    var loginError by remember { mutableStateOf<String?>(null) }
    var currentAccountId by remember { mutableStateOf<String?>(null) }
val currentCharacterId by gameViewModel.currentCharacterId.collectAsState()
    LaunchedEffect(Unit) {
        gameViewModel.loadGame()
        val autoAccount = gameViewModel.tryAutoLogin()
        if (autoAccount != null) {
            currentAccountId = autoAccount.id
            val chars = gameViewModel.accountService.charactersFor(autoAccount.id)
            flowState = if (chars.isEmpty()) AppFlowState.CharacterCreate else AppFlowState.CharacterSelect
        }
    }

    var currentDestination by remember { mutableStateOf(AppDestination.HOME) }
    var skillsScreenState by remember { mutableStateOf<SkillsScreenState>(SkillsScreenState.List) }
    var combatScreenState by remember { mutableStateOf<CombatScreenState>(CombatScreenState.ZoneSelect) }
    var inventoryScreenState by remember { mutableStateOf<InventoryScreenState>(InventoryScreenState.Items) }

    val allSkills by gameViewModel.skills.collectAsState()
    val zones = remember { demoZones() }
    val inventoryItems = remember { demoInventoryItems() }
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
                EquipSlotUi.BOOTS, EquipSlotUi.NECKLACE, EquipSlotUi.RING_1, EquipSlotUi.RING_2
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
                            currentAccountId = result.value.id
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
                            currentAccountId = result.value.id
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
                                    SkillDetailScreen(demoDetailFor(screen.skillId, it), { skillsScreenState = SkillsScreenState.List }, { })
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
