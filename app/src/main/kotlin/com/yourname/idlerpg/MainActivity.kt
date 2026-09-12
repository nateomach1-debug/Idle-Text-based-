package com.yourname.idlerpg

import android.widget.Toast

import com.yourname.idlerpg.ui.components.ReportMessageDialog

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.compose.BackHandler
import androidx.activity.viewModels
import androidx.compose.foundation.layout.Box
import androidx.compose.ui.graphics.Color
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.Density
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalConfiguration
import android.content.res.Configuration
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
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
import com.yourname.idlerpg.ui.theme.skillPatternBackground
import com.yourname.idlerpg.ui.theme.appPatternBackground
import androidx.compose.foundation.background
import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.lazy.grid.LazyGridState
import androidx.compose.foundation.lazy.grid.rememberLazyGridState
import java.time.Duration
import kotlinx.coroutines.launch
import java.time.Instant

// Shrinks all dp-based sizing (padding, spacers, icons, fonts) proportionally
// in landscape, unchanged in portrait. Adjust the two multipliers here to
// retune density app-wide from one place.
@Composable
private fun adaptiveDensity(): Density {
    val configuration = LocalConfiguration.current
    val baseDensity = LocalDensity.current
    return if (configuration.orientation == Configuration.ORIENTATION_LANDSCAPE) {
        Density(density = baseDensity.density * 0.78f, fontScale = baseDensity.fontScale * 0.9f)
    } else {
        baseDensity
    }
}

// Skills tab rows that route directly into training-location selection
// (Combat's zone-select) instead of the generic skill-detail screen.
// Prayer is deliberately excluded.
private val COMBAT_TRAINING_SKILL_IDS = setOf("ATTACK", "STRENGTH", "DEFENSE", "MAGIC", "ARCHERY")

class MainActivity : ComponentActivity() {
    private val gameViewModel: GameViewModel by viewModels()
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val textColorOverride by gameViewModel.textColorOverride.collectAsState()
            val textOutlineEnabled by gameViewModel.textOutlineEnabled.collectAsState()
            val textOutlineColor by gameViewModel.textOutlineColor.collectAsState()
            IdleRpgTheme(
                textColorOverride = textColorOverride,
                outlineEnabled = textOutlineEnabled,
                outlineColor = textOutlineColor
            ) {
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
    is Effect.MaterialSaveChance -> "+" + effect.percent + "% material save chance"
    is Effect.CraftSuccessBoost -> "+" + effect.percent + "% success chance"
}

// Cape's OWN individual contribution (mirrors capeBonusEffects() in
// GameViewModel.kt exactly - the level-50 perk already grants the base
// bonus + 5% XP, the cape grants this same amount again on top).
// Combat skills aren't Effect-driven (hardcoded in tickCombat), hence
private val COMBAT_CAPE_BONUS_TEXT: Map<SkillType, String> = mapOf(
    SkillType.ATTACK to "+5% hit chance (melee)",
    SkillType.STRENGTH to "+5% min/max hit damage (melee)",
    SkillType.DEFENSE to "+5% incoming damage reduction",
    SkillType.ARCHERY to "+5% hit chance (ranged)",
    SkillType.MAGIC to "+5% hit chance (magic)",
    SkillType.PRAYER to "+5% reduced monster damage while a prayer is active"
)

private fun capeBonusDescriptionFor(skillType: SkillType): String {
    val specific = COMBAT_CAPE_BONUS_TEXT[skillType] ?: when (skillType) {
        SkillType.MINING, SkillType.WOODCUTTING, SkillType.FISHING, SkillType.FARMING, SkillType.THIEVING -> "+10% drop rate"
        SkillType.SMITHING, SkillType.CRAFTING, SkillType.FLETCHING, SkillType.ALCHEMY -> "+10% material save chance"
        SkillType.COOKING -> "+10% success chance"
        else -> ""
    }
    return specific + ", +5% XP"
}

private val RECIPE_BASED_SKILL_LABELS: Map<String, String> = mapOf(
    "CRAFTING" to "Select Recipe",
    "COOKING" to "Select Dish",
    "FLETCHING" to "Select Item",
    "ALCHEMY" to "Select Potion"
)

private fun missingIngredientsFor(
    ingredients: List<RecipeIngredient>,
    inventoryQuantities: Map<String, Int>
): List<MissingIngredientSummary> {
    return ingredients.mapNotNull { ingredient ->
        val have = inventoryQuantities[ingredient.itemId] ?: 0
        if (have < ingredient.quantity) {
            MissingIngredientSummary(
                displayName = ItemCatalog.find(ingredient.itemId)?.name ?: ingredient.itemId,
                required = ingredient.quantity,
                have = have
            )
        } else {
            null
        }
    }
}

private fun buildSkillDetailState(
    skillId: String,
    summary: SkillSummary,
    inventoryQuantities: Map<String, Int>,
    hasCapeEquipped: Boolean = false
): SkillDetailState {
    val skillType = SkillType.valueOf(skillId)

    val earned = UnlockTable.unlocksEarnedAt(skillType, summary.level).map { unlock ->
        SkillUnlockSummary(
            description = unlock.grantedEffects.joinToString(", ") { effectSummaryText(it) },
            levelRequired = unlock.levelRequired
        )
    } + if (hasCapeEquipped) {
        listOf(SkillUnlockSummary(description = "Cape equipped: " + capeBonusDescriptionFor(skillType), levelRequired = 99))
    } else {
        emptyList()
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
            .filter { it.skillRequired == skillId }
            .map {
                SkillActionSummary(
                    actionId = it.outputItemId,
                    displayName = ItemCatalog.find(it.outputItemId)?.name ?: it.outputItemId,
                    levelRequired = it.levelRequired,
                    missingIngredients = if (it.levelRequired <= summary.level) missingIngredientsFor(it.ingredients, inventoryQuantities) else emptyList(),
                    isLocked = it.levelRequired > summary.level
                )
            }
            .sortedBy { it.levelRequired }
    } else {
        ActionCatalog.allFor(skillType)
            .filter { it.levelRequired <= summary.level }
            .map { action ->
                val requiredSeedId = if (skillId == "FARMING") FarmingSeedRequirements[action.itemId] else null
                val missing = if (requiredSeedId != null) {
                    missingIngredientsFor(listOf(RecipeIngredient(requiredSeedId, 1)), inventoryQuantities)
                } else {
                    emptyList()
                }
                SkillActionSummary(action.itemId, action.displayName, action.levelRequired, missing)
            }
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

private fun buildSmithingState(summary: SkillSummary, inventoryQuantities: Map<String, Int>, hasCapeEquipped: Boolean = false): SmithingState {
    val skillType = SkillType.SMITHING
    val earned = UnlockTable.unlocksEarnedAt(skillType, summary.level).map { unlock ->
        SkillUnlockSummary(
            description = unlock.grantedEffects.joinToString(", ") { effectSummaryText(it) },
            levelRequired = unlock.levelRequired
        )
    } + if (hasCapeEquipped) {
        listOf(SkillUnlockSummary(description = "Cape equipped: " + capeBonusDescriptionFor(skillType), levelRequired = 99))
    } else {
        emptyList()
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

    val materials = SMITHING_METALS.map { (materialId, displayName, barItemId) ->
        val barRecipe = RecipeCatalog.forOutput(barItemId)?.let {
            recipeToSmithingSummary(it).copy(
                missingIngredients = missingIngredientsFor(it.ingredients, inventoryQuantities)
            )
        }
        val gearRecipes = RecipeCatalog.recipes
            .filter { it.skillRequired == "SMITHING" && it.ingredients.any { ing -> ing.itemId == barItemId } }
            .map {
                recipeToSmithingSummary(it).copy(
                    missingIngredients = missingIngredientsFor(it.ingredients, inventoryQuantities)
                )
            }
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
        materials = materials,
        earnedUnlocks = earned,
        nextUnlock = next
    )
}

private fun mapItemCategory(category: ItemCategory): InventoryCategory = when (category) {
    ItemCategory.WEAPON -> InventoryCategory.WEAPON
    ItemCategory.ARMOR -> InventoryCategory.ARMOR
    ItemCategory.ACCESSORY -> InventoryCategory.ACCESSORY
    ItemCategory.MATERIAL -> InventoryCategory.MATERIAL
    ItemCategory.CONSUMABLE -> InventoryCategory.CONSUMABLE
    ItemCategory.COSMETIC -> InventoryCategory.MATERIAL
}

private fun buildInventoryItemSummaries(
    entries: List<InventorySlotEntry>,
    vendorPayoutFor: (String) -> Long
): List<InventoryItemSummary> {
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
                npcValuePerUnit = vendorPayoutFor(entry.itemId),
                statsDescription = statsText,
                isBuryable = PrayerBoneRequirements.containsKey(entry.itemId),
                lastAcquiredAtMillis = entry.lastAcquiredAtMillis
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
                npcValuePerUnit = vendorPayoutFor(entry.itemId),
                lastAcquiredAtMillis = entry.lastAcquiredAtMillis
            )
        }
    }
}


private fun formatTimeAgo(instant: Instant): String {
    val seconds = Duration.between(instant, Instant.now()).seconds.coerceAtLeast(0)
    return when {
        seconds < 60 -> seconds.toString() + "s ago"
        seconds < 3600 -> (seconds / 60).toString() + "m ago"
        seconds < 86400 -> (seconds / 3600).toString() + "h ago"
        else -> (seconds / 86400).toString() + "d ago"
    }
}

private fun demoGuildMembers(): List<GuildMemberSummary> = listOf(
    GuildMemberSummary("char1", "Lyra", GuildMemberRole.LEADER),
    GuildMemberSummary("char2", "Bram", GuildMemberRole.OFFICER),
    GuildMemberSummary("char3", "Sable", GuildMemberRole.MEMBER),
    GuildMemberSummary("char4", "Quinn", GuildMemberRole.MEMBER)
)

private fun demoGuildState(): GuildHomeState = GuildHomeState(
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
    guildCoins = 500L,
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
    ChatMessageUi("m1", "demo-bram", "Bram", "anyone selling steel bars?", ChatChannelUi.GLOBAL),
    ChatMessageUi("m2", "demo-sable", "Sable", "check the market, saw some at 48 each", ChatChannelUi.GLOBAL),
    ChatMessageUi("m3", "demo-quinn", "Quinn", "gl on the hunt everyone", ChatChannelUi.GLOBAL)
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
        } else if (flowState == AppFlowState.InGame) {
            gameViewModel.resumeCurrentCharacterIfNeeded()
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

    val pendingSaleNotifications by gameViewModel.pendingSaleNotifications.collectAsState()
    pendingSaleNotifications.firstOrNull()?.let { sale ->
        androidx.compose.material3.AlertDialog(
            onDismissRequest = { gameViewModel.dismissSaleNotification() },
            title = { androidx.compose.material3.Text("Item Sold!") },
            text = {
                androidx.compose.material3.Text(
                    "Sold " + sale.quantity + "x " + sale.itemName + "\n" +
                    "You received " + sale.netProceeds + " coins (after tax)."
                )
            },
            confirmButton = {
                androidx.compose.material3.TextButton(onClick = { gameViewModel.dismissSaleNotification() }) {
                    androidx.compose.material3.Text("Nice!")
                }
            }
        )
    }

    val actionStoppedNotifications by gameViewModel.actionStoppedNotifications.collectAsState()
    actionStoppedNotifications.firstOrNull()?.let { notice ->
        androidx.compose.material3.AlertDialog(
            onDismissRequest = { gameViewModel.dismissActionStoppedNotification() },
            title = { androidx.compose.material3.Text(if (notice.isCompletion) "Done!" else "Action Stopped") },
            text = {
                androidx.compose.material3.Text(
                    if (notice.isCompletion) {
                        notice.reason
                    } else {
                        "Ran out of materials for " + notice.itemName + ".\n" + notice.reason
                    }
                )
            },
            confirmButton = {
                androidx.compose.material3.TextButton(onClick = { gameViewModel.dismissActionStoppedNotification() }) {
                    androidx.compose.material3.Text("OK")
                }
            }
        )
    }

    val context = androidx.compose.ui.platform.LocalContext.current
    var currentDestination by rememberSaveable { mutableStateOf(AppDestination.HOME) }

    BackHandler(enabled = currentDestination != AppDestination.HOME) {
        currentDestination = AppDestination.HOME
    }
    var skillsScreenState by remember { mutableStateOf<SkillsScreenState>(SkillsScreenState.List) }
    var combatScreenState by remember { mutableStateOf<CombatScreenState>(CombatScreenState.ZoneSelect) }
    var inventoryScreenState by remember { mutableStateOf<InventoryScreenState>(InventoryScreenState.Items) }

    val allSkills by gameViewModel.skills.collectAsState()
    val zones = gameViewModel.zoneSummaries
    val trainingSkill by gameViewModel.trainingSkill.collectAsState()
    val trainingSkillLevel by gameViewModel.trainingSkillLevel.collectAsState()
    val inventoryItemEntries by gameViewModel.inventoryItems.collectAsState()
    val inventoryItems = remember(inventoryItemEntries) {
        buildInventoryItemSummaries(inventoryItemEntries, gameViewModel.marketService::vendorPayoutPerUnit)
    }
    val inventoryQuantities = remember(inventoryItemEntries) {
        inventoryItemEntries.associate { it.itemId to it.quantity }
    }
    val equippedBackend by gameViewModel.equippedItems.collectAsState()
    val equipped = remember(equippedBackend) {
        EquipSlotUi.values().associateWith { uiSlot ->
            equippedBackend[EquipSlot.valueOf(uiSlot.name)]?.let { itemId ->
                ItemCatalog.find(itemId)?.let { def -> EquippedItemInfo(itemId, def.name) }
            }
        }
    }
    val loadoutSettings by gameViewModel.loadoutSettings.collectAsState()
    val availableFoodOptions = remember(inventoryItemEntries) {
        inventoryItemEntries.mapNotNull { entry ->
            val definition = ItemCatalog.find(entry.itemId)
            if (definition?.consumableType == ConsumableType.FOOD) {
                ConsumableOption(entry.itemId, definition.name, entry.quantity)
            } else null
        }
    }
    val availablePotionOptions = remember(inventoryItemEntries) {
        inventoryItemEntries.mapNotNull { entry ->
            val definition = ItemCatalog.find(entry.itemId)
            if (definition?.consumableType == ConsumableType.POTION) {
                ConsumableOption(entry.itemId, definition.name, entry.quantity)
            } else null
        }
    }
    val skillsListScrollState = rememberLazyListState()
    val skillsGridScrollState = rememberLazyGridState()

    val activeQueue by gameViewModel.activeQueueInfo.collectAsState()
    val currency by gameViewModel.currency.collectAsState()
    val combatHp by gameViewModel.combatHp.collectAsState()
    val homeCombatViewData by gameViewModel.combatViewData.collectAsState()
    val homeState = HomeScreenState(
        activeQueue = activeQueue,
        activeCombat = homeCombatViewData,
        trainingSkillLabel = trainingSkill.name.lowercase().replaceFirstChar { it.uppercase() },
        softCurrency = currency.first,
        premiumCurrency = currency.second,
        currentHp = combatHp?.first,
        maxHp = combatHp?.second,
        isRecovering = false,
        unreadNotificationCount = 0
    )

    val recoveringUntil = remember { mutableStateOf<Instant?>(null) }

    var loadoutWeaponId by remember { mutableStateOf<String?>("bronze_sword") }
    var autoHeal by remember { mutableStateOf(30) }
    var autoFlee by remember { mutableStateOf(10) }

    val combatViewData by gameViewModel.combatViewData.collectAsState()

    // Survives rotation: if the ViewModel still has an active combat session
    // but the local UI state reset back to ZoneSelect (e.g. after an
    // orientation change recreated the Activity), snap back to InZone.
    LaunchedEffect(combatViewData) {
        if (combatViewData != null && combatScreenState == CombatScreenState.ZoneSelect) {
            combatScreenState = CombatScreenState.InZone
        }
    }

    fun canEquip(item: InventoryItemSummary): Pair<Boolean, String?> {
        if (item.category == InventoryCategory.TOOL) return true to null
        val locked = combatViewData?.viewState == CombatViewState.IN_COMBAT
        return if (locked) false to "Locked during combat" else true to null
    }

    fun canBury(item: InventoryItemSummary): Pair<Boolean, String?> {
        val boneInfo = PrayerBoneRequirements[item.itemId] ?: return false to null
        val prayerLevel = allSkills["PRAYER"]?.level ?: 1
        return if (prayerLevel < boneInfo.levelRequired) {
            false to ("Requires Prayer level " + boneInfo.levelRequired)
        } else {
            true to null
        }
    }

    val lockedEquipSlots = remember(combatViewData) {
        if (combatViewData?.viewState == CombatViewState.IN_COMBAT) {
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
            val loginCoroutineScope = rememberCoroutineScope()
            LoginScreen(
                isCreatingAccount = isCreatingAccount,
                onToggleMode = { isCreatingAccount = !isCreatingAccount; loginError = null },
                errorMessage = loginError,
                onLogin = { email, password ->
                    loginCoroutineScope.launch {
                        val result = gameViewModel.login(email, password)
                        when (result) {
                            is ServiceResult.Success -> {
                                val chars = gameViewModel.accountService.charactersFor(result.value.id)
                                flowState = if (chars.isEmpty()) AppFlowState.CharacterCreate else AppFlowState.CharacterSelect
                                loginError = null
                            }
                            is ServiceResult.Failure -> loginError = result.reason
                        }
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
            val activeSkillId = (skillsScreenState as? SkillsScreenState.Detail)?.skillId
            val screenBackgroundModifier = if (currentDestination == AppDestination.SKILLS && activeSkillId != null) {
                Modifier.fillMaxSize().skillPatternBackground(activeSkillId)
            } else {
                Modifier.fillMaxSize().appPatternBackground()
            }
            Surface(modifier = screenBackgroundModifier, color = Color.Transparent) {
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
                        val isModerator by gameViewModel.isModerator.collectAsState()
                        val equippedItemsForSkills by gameViewModel.equippedItems.collectAsState()
                        SideRail(
                            currentDestination = currentDestination,
                            destinations = AppDestination.values().filter { it != AppDestination.MODERATION || isModerator },
                            onDestinationSelected = {
                                currentDestination = it
                                skillsScreenState = SkillsScreenState.List
                                // combatScreenState intentionally NOT reset here - if a
                                // battle is still running in the background, navigating
                                // away and back should return to it, not zone-select.
                                inventoryScreenState = InventoryScreenState.Items
                                marketTab = MarketTab.BROWSE
                                selectedMarketItemId = null
                            },
                            badgedDestinations = setOf(AppDestination.GUILD)
                        )

                        CompositionLocalProvider(LocalDensity provides adaptiveDensity()) {
                        Box(modifier = Modifier.weight(1f)) {
                        when (currentDestination) {
                            AppDestination.HOME -> {
                                LaunchedEffect(Unit) { gameViewModel.refreshCurrency() }
                                HomeScreen(state = homeState)
                            }

                            AppDestination.SKILLS -> {
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
                            }

                            AppDestination.COMBAT -> {
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
                            }

                            AppDestination.INVENTORY -> {
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
                            }

                            AppDestination.MARKET -> {
                                LaunchedEffect(Unit) {
                                    gameViewModel.refreshMarketListings()
                                    gameViewModel.refreshMyOrders()
                                }
                                val marketPriceSummaries by gameViewModel.marketListings.collectAsState()
                                val myBuyOrdersRaw by gameViewModel.myBuyOrders.collectAsState()
                                val mySellOrdersRaw by gameViewModel.mySellOrders.collectAsState()
                                val marketListingsUi = remember(marketPriceSummaries) {
                                    marketPriceSummaries.map {
                                        MarketListingSummary(
                                            itemId = it.itemId,
                                            displayName = ItemCatalog.find(it.itemId)?.name ?: it.itemId,
                                            bestBuyPrice = it.bestBuyPrice,
                                            bestBuyQuantity = it.bestBuyQuantity,
                                            bestSellPrice = it.bestSellPrice,
                                            bestSellQuantity = it.bestSellQuantity
                                        )
                                    }
                                }
                                val myBuyOrdersUi = remember(myBuyOrdersRaw) {
                                    myBuyOrdersRaw.map {
                                        MarketOrderSummary(
                                            orderId = it.id,
                                            itemId = it.itemId,
                                            displayName = ItemCatalog.find(it.itemId)?.name ?: it.itemId,
                                            pricePerUnit = it.pricePerUnit,
                                            remainingQuantity = it.remainingQuantity
                                        )
                                    }
                                }
                                val mySellOrdersUi = remember(mySellOrdersRaw) {
                                    mySellOrdersRaw.map {
                                        MarketOrderSummary(
                                            orderId = it.id,
                                            itemId = it.itemId,
                                            displayName = ItemCatalog.find(it.itemId)?.name ?: it.itemId,
                                            pricePerUnit = it.pricePerUnit,
                                            remainingQuantity = it.remainingQuantity
                                        )
                                    }
                                }

                                val itemId = selectedMarketItemId

                                BackHandler(enabled = itemId != null) {
                                    selectedMarketItemId = null
                                    prefilledSellQuantity = null
                                }
                                BackHandler(enabled = itemId == null && marketTab != MarketTab.BROWSE) {
                                    marketTab = MarketTab.BROWSE
                                }

                                if (itemId != null) {
                                    val orderBookDetail = remember(itemId, marketPriceSummaries) {
                                        val summary = marketPriceSummaries.find { it.itemId == itemId }
                                        ItemOrderBookDetail(
                                            itemId = itemId,
                                            displayName = ItemCatalog.find(itemId)?.name ?: itemId,
                                            bestBuyPrice = summary?.bestBuyPrice,
                                            bestSellPrice = summary?.bestSellPrice,
                                            recentTrades = gameViewModel.marketService.priceHistoryFor(itemId)
                                                .sortedByDescending { it.executedAt }
                                                .take(10)
                                                .map { PriceHistoryRow(it.pricePerUnit, it.quantity, formatTimeAgo(it.executedAt)) }
                                        )
                                    }
                                    OrderBookScreen(
                                        detail = orderBookDetail,
                                        prefilledQuantity = prefilledSellQuantity,
                                        onBack = { selectedMarketItemId = null; prefilledSellQuantity = null },
                                        onPlaceOrder = { side, qty, price ->
                                            if (side == OrderSideUi.BUY) {
                                                gameViewModel.placeBuyOrder(itemId, qty, price)
                                            } else {
                                                gameViewModel.placeSellOrder(itemId, qty, price)
                                            }
                                            selectedMarketItemId = null
                                            prefilledSellQuantity = null
                                        }
                                    )
                                } else {
                                    MarketScreen(
                                        currentTab = marketTab,
                                        onTabSelected = { marketTab = it },
                                        listings = marketListingsUi,
                                        showingBuyOrders = showingBuyOrders,
                                        onToggleBrowseMode = { showingBuyOrders = !showingBuyOrders },
                                        onItemSelected = { selectedMarketItemId = it },
                                        myBuyOrders = myBuyOrdersUi,
                                        mySellOrders = mySellOrdersUi,
                                        onCancelOrder = { orderId -> gameViewModel.cancelMarketOrder(orderId) },
                                        vendorSellableItems = inventoryItems,
                                        onPlaceBuyOrder = { itemId, quantity, price ->
                                            gameViewModel.placeBuyOrder(itemId, quantity, price)
                                        },
                                        onPlaceSellOrder = { itemId, quantity, price ->
                                            gameViewModel.placeSellOrder(itemId, quantity, price)
                                        },
                                        onSellToVendor = { sellItemId, quantity ->
                                            gameViewModel.sellItemToVendor(sellItemId, quantity)
                                        },
                                        vendorBuyableItems = gameViewModel.vendorBuyableItems(),
                                        onBuyFromVendor = { buyItemId, quantity ->
                                            gameViewModel.buyItemFromVendor(buyItemId, quantity)
                                        }
                                    )
                                }
                            }

                            AppDestination.GUILD -> {
                                val currentGuildHomeState by gameViewModel.guildHomeState.collectAsState()
                                val currentGuildLeaderboard by gameViewModel.guildLeaderboard.collectAsState()
                                val currentBrowsableGuilds by gameViewModel.browsableGuilds.collectAsState()

                                LaunchedEffect(Unit) { gameViewModel.refreshGuildHome() }
                                LaunchedEffect(Unit) { gameViewModel.loadInitialChatState() }
                                LaunchedEffect(Unit) { gameViewModel.checkModeratorStatus() }
                                val debugAuthState by gameViewModel.supabaseAuthState.collectAsState()
                                val debugAuthError by gameViewModel.supabaseAuthError.collectAsState()
                                val debugSupabaseCharId by gameViewModel.currentSupabaseCharacterId.collectAsState()
                                val debugCharSyncError by gameViewModel.characterSyncError.collectAsState()
                                val debugChatError by gameViewModel.chatActionError.collectAsState()
                                val debugMarketError by gameViewModel.marketActionError.collectAsState()
                                var showDebugDialog by remember { mutableStateOf(false) }
                                LaunchedEffect(debugAuthError, debugCharSyncError, debugMarketError) {
                                    if (debugAuthError != null || debugCharSyncError != null || debugChatError != null || debugMarketError != null) {
                                        showDebugDialog = true
                                    }
                                }
                                if (showDebugDialog) {
                                    androidx.compose.material3.AlertDialog(
                                        onDismissRequest = { showDebugDialog = false },
                                        title = { androidx.compose.material3.Text("Debug: Supabase Sync") },
                                        text = {
                                            androidx.compose.foundation.layout.Column {
                                                androidx.compose.material3.Text("Auth: $debugAuthState")
                                                debugAuthError?.let { androidx.compose.material3.Text("Auth error: $it") }
                                                androidx.compose.material3.Text("Char id: ${debugSupabaseCharId ?: "none"}")
                                                debugCharSyncError?.let { androidx.compose.material3.Text("Char sync error: $it") }
                                                debugChatError?.let { androidx.compose.material3.Text("Chat error: $it") }
                                                debugMarketError?.let { androidx.compose.material3.Text("Market error: $it") }
                                            }
                                        },
                                        confirmButton = {
                                            androidx.compose.material3.TextButton(onClick = { showDebugDialog = false }) {
                                                androidx.compose.material3.Text("OK")
                                            }
                                        }
                                    )
                                }

                                val guildState = currentGuildHomeState
                                if (guildState == null) {
                                    GuildCreateJoinScreen(
                                        browsableGuilds = currentBrowsableGuilds,
                                        onCreateGuild = { name -> gameViewModel.createGuild(name) },
                                        onJoinGuild = { guildId -> gameViewModel.joinGuild(guildId) }
                                    )
                                } else {
                                    val guildActionErrorState by gameViewModel.guildActionError.collectAsState()
                                    val contributableQuantity = guildState.activeEvent?.let { gameViewModel.currentInventoryQuantityOf(it.itemId) } ?: 0
                                    GuildHomeScreen(
                                        state = guildState,
                                        leaderboardEntries = currentGuildLeaderboard,
                                        leaderboardShowingDaily = leaderboardShowingDaily,
                                        contributableQuantity = contributableQuantity,
                                        xpRequiredForNextLevel = gameViewModel.guildXpRequiredForLevel(guildState.guildLevel),
                                        actionError = guildActionErrorState,
                                        onToggleLeaderboardPeriod = { leaderboardShowingDaily = !leaderboardShowingDaily },
                                        onMemberTapped = { selectedGuildMember = it },
                                        onContributeToEvent = { qty -> gameViewModel.contributeToGuildEvent(qty) },
                                        onStartEvent = { gameViewModel.startGuildEvent() },
                                        onCastVote = { },
                                        onDismissError = { gameViewModel.clearGuildActionError() }
                                    )

                                    selectedGuildMember?.let { member ->
                                        MemberActionPopup(
                                            member = member,
                                            viewerRole = guildState.viewerRole,
                                            onDismiss = { selectedGuildMember = null },
                                            onKick = {
                                                gameViewModel.kickGuildMember(member.characterId)
                                                selectedGuildMember = null
                                            },
                                            onPromote = {
                                                when (member.role) {
                                                    GuildMemberRole.MEMBER -> gameViewModel.promoteGuildMemberToOfficer(member.characterId)
                                                    GuildMemberRole.OFFICER -> gameViewModel.promoteGuildMemberToLeader(member.characterId)
                                                    GuildMemberRole.LEADER -> {}
                                                }
                                                selectedGuildMember = null
                                            },
                                            onDemote = { selectedGuildMember = null },
                                            onInitiateVote = { selectedGuildMember = null }
                                        )
                                    }
                                }
                            }

                            AppDestination.MODERATION -> {
                                val moderation by gameViewModel.moderationState.collectAsState()
                                LaunchedEffect(Unit) { gameViewModel.refreshModeration() }
                                ModerationScreen(
                                    state = moderation,
                                    onResolveReport = { id, action -> gameViewModel.resolveReport(id, action) },
                                    onResolveAppeal = { id, grant, notes -> gameViewModel.resolveAppeal(id, grant, notes) },
                                    onMuteCharacter = { id, dur, reason -> gameViewModel.muteCharacterAsModerator(id, dur, reason) },
                                    onUnmuteCharacter = { id -> gameViewModel.unmuteCharacterAsModerator(id) }
                                )
                            }

                            AppDestination.LEADERBOARDS -> {
                                val leaderboardRows by gameViewModel.leaderboardRows.collectAsState()
                                val leaderboardLoading by gameViewModel.leaderboardLoading.collectAsState()
                                val selectedLeaderboardCategory by gameViewModel.selectedLeaderboardCategory.collectAsState()
                                LaunchedEffect(Unit) { gameViewModel.fetchLeaderboard(selectedLeaderboardCategory) }
                                LeaderboardsScreen(
                                    selectedCategory = selectedLeaderboardCategory,
                                    rows = leaderboardRows,
                                    isLoading = leaderboardLoading,
                                    onCategorySelected = { gameViewModel.fetchLeaderboard(it) }
                                )
                            }

                            AppDestination.SETTINGS -> {
                                val settingsTextColorOverride by gameViewModel.textColorOverride.collectAsState()
                                val settingsOutlineEnabled by gameViewModel.textOutlineEnabled.collectAsState()
                                val settingsOutlineColor by gameViewModel.textOutlineColor.collectAsState()
                                SettingsScreen(
                                    textColorOverride = settingsTextColorOverride,
                                    outlineEnabled = settingsOutlineEnabled,
                                    outlineColor = settingsOutlineColor,
                                    onTextColorChanged = { gameViewModel.setTextColorOverride(it) },
                                    onOutlineEnabledChanged = { gameViewModel.setTextOutlineEnabled(it) },
                                    onOutlineColorChanged = { gameViewModel.setTextOutlineColor(it) }
                                )
                            }

                            else -> androidx.compose.material3.Text(
                                text = currentDestination.label + " screen coming soon",
                                modifier = Modifier.fillMaxSize()
                            )
                        }
                        }
                        }
                    }

                    val chatMessagesFromVm by gameViewModel.chatMessages.collectAsState()
val selectedChatChannelFromVm by gameViewModel.selectedChatChannel.collectAsState()
val dmConversationsFromVm by gameViewModel.dmConversations.collectAsState()
val selectedDmCharacterIdFromVm by gameViewModel.selectedDmCharacterId.collectAsState()

var reportDialogMessage by remember { mutableStateOf<ChatMessageUi?>(null) }
                    reportDialogMessage?.let { targetMessage ->
                        ReportMessageDialog(
                            message = targetMessage,
                            onDismiss = { reportDialogMessage = null },
                            onSubmit = { category, reason ->
                                gameViewModel.reportChatMessage(targetMessage, category, reason)
                                reportDialogMessage = null
                            }
                        )
                    }

                    ChatBanner(
    selectedChannel = selectedChatChannelFromVm,
    onChannelSelected = { gameViewModel.selectChatChannel(it) },
    messages = chatMessagesFromVm,
    dmConversations = dmConversationsFromVm,
    selectedDmCharacterId = selectedDmCharacterIdFromVm,
    onDmSelected = { gameViewModel.selectDmConversation(it) },
    hasUnread = true,
    messageInput = chatMessageInput,
    onMessageInputChanged = { chatMessageInput = it },
    onSendMessage = {
        if (chatMessageInput.isNotBlank()) {
            gameViewModel.sendChatMessage(chatMessageInput)
                                chatMessageInput = ""
                            }
                        },
                        onMessageAction = { message, action ->
                            when (action) {
                                ChatMessageAction.REPORT -> reportDialogMessage = message
                                ChatMessageAction.BLOCK -> gameViewModel.blockCharacter(message.senderCharacterId)
                                ChatMessageAction.SELF_MUTE -> gameViewModel.selfMuteCharacter(message.senderCharacterId)
                                ChatMessageAction.MESSAGE_PLAYER -> {
                                    gameViewModel.selectChatChannel(ChatChannelUi.DMS)
                                    gameViewModel.selectDmConversation(message.senderCharacterId)
                                }
                            }
                        }
                    )
                }
            }
        }
    }
}
