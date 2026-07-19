package com.yourname.idlerpg

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import com.yourname.idlerpg.ui.components.RecoveryBar
import com.yourname.idlerpg.ui.navigation.AppDestination
import com.yourname.idlerpg.ui.navigation.SideRail
import com.yourname.idlerpg.ui.screens.*
import com.yourname.idlerpg.ui.theme.IdleRpgTheme
import java.time.Instant

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            IdleRpgTheme {
                AppRoot()
            }
        }
    }
}

// =========================================================
// PLACEHOLDER DEMO DATA
// =========================================================

private fun demoSkills(): Map<String, SkillSummary> {
    val raw = listOf(
        Triple("MINING", "Mining", 24), Triple("SMITHING", "Smithing", 18),
        Triple("FISHING", "Fishing", 30), Triple("COOKING", "Cooking", 22),
        Triple("WOODCUTTING", "Woodcutting", 15), Triple("FLETCHING", "Fletching", 9),
        Triple("FARMING", "Farming", 12), Triple("ALCHEMY", "Alchemy", 7),
        Triple("THIEVING", "Thieving", 20), Triple("CRAFTING", "Crafting", 16),
        Triple("ATTACK", "Attack", 28), Triple("STRENGTH", "Strength", 26),
        Triple("DEFENSE", "Defense", 25), Triple("ARCHERY", "Archery", 19),
        Triple("PRAYER", "Prayer", 11), Triple("MAGIC", "Magic", 14)
    )
    return raw.associate { (id, name, level) ->
        val currentXp = (level * 120L)
        val xpToNext = ((level + 1) * 130L) - currentXp
        id to SkillSummary(id, name, level, currentXp, xpToNext.coerceAtLeast(50L))
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

// =========================================================
// APP ROOT
// =========================================================

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
fun AppRoot() {
    var currentDestination by remember { mutableStateOf(AppDestination.HOME) }
    var skillsScreenState by remember { mutableStateOf<SkillsScreenState>(SkillsScreenState.List) }
    var combatScreenState by remember { mutableStateOf<CombatScreenState>(CombatScreenState.ZoneSelect) }
    var inventoryScreenState by remember { mutableStateOf<InventoryScreenState>(InventoryScreenState.Items) }

    val allSkills = remember { demoSkills() }
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

    // Equipment lock check -- mirrors CombatService.canChangeEquipment logic for the demo.
    // TOOL is never locked; WEAPON/ARMOR/ACCESSORY locked during IN_COMBAT.
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

    Surface(modifier = Modifier.fillMaxSize()) {
        Column(modifier = Modifier.fillMaxSize()) {
            RecoveryBar(recoveringUntil = recoveringUntil.value)

            Row(modifier = Modifier.fillMaxSize()) {
                SideRail(
                    currentDestination = currentDestination,
                    onDestinationSelected = {
                        currentDestination = it
                        skillsScreenState = SkillsScreenState.List
                        combatScreenState = CombatScreenState.ZoneSelect
                        inventoryScreenState = InventoryScreenState.Items
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
                        CombatScreenState.InZone -> CombatViewScreen(
    data = combatViewData,
    onLeaveZone = { combatScreenState = CombatScreenState.ZoneSelect }
)
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
                            onSellOnMarket = { },
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

                    else -> androidx.compose.material3.Text(
                        text = currentDestination.label + " screen coming soon",
                        modifier = Modifier.fillMaxSize()
                    )
                }
            }
        }
    }
}
