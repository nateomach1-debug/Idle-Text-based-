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
        Triple("MINING", "Mining", 24),
        Triple("SMITHING", "Smithing", 18),
        Triple("FISHING", "Fishing", 30),
        Triple("COOKING", "Cooking", 22),
        Triple("WOODCUTTING", "Woodcutting", 15),
        Triple("FLETCHING", "Fletching", 9),
        Triple("FARMING", "Farming", 12),
        Triple("ALCHEMY", "Alchemy", 7),
        Triple("THIEVING", "Thieving", 20),
        Triple("CRAFTING", "Crafting", 16),
        Triple("ATTACK", "Attack", 28),
        Triple("STRENGTH", "Strength", 26),
        Triple("DEFENSE", "Defense", 25),
        Triple("ARCHERY", "Archery", 19),
        Triple("PRAYER", "Prayer", 11),
        Triple("MAGIC", "Magic", 14)
    )

    return raw.associate { (id, name, level) ->
        val currentXp = (level * 120L)
        val xpToNext = ((level + 1) * 130L) - currentXp
        id to SkillSummary(
            skillId = id,
            displayName = name,
            level = level,
            currentXp = currentXp,
            xpToNextLevel = xpToNext.coerceAtLeast(50L)
        )
    }
}

private fun demoDetailFor(skillId: String, summary: SkillSummary): SkillDetailState {
    return SkillDetailState(
        skillId = summary.skillId,
        displayName = summary.displayName,
        level = summary.level,
        currentXp = summary.currentXp,
        xpToNextLevel = summary.xpToNextLevel,
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

private fun demoZones(): List<ZoneSummary> {
    return listOf(
        ZoneSummary("goblin_camp", "Goblin Camp", levelRequirement = 1, monsterNames = listOf("Goblin Grunt")),
        ZoneSummary("shadow_ruins", "Shadow Ruins", levelRequirement = 20, monsterNames = listOf("Wraith")),
        ZoneSummary("frost_peak", "Frost Peak", levelRequirement = 40, monsterNames = listOf("Ice Troll", "Frost Wolf"))
    )
}

private fun demoWeapons(style: CombatStyleOption): List<WeaponOption> {
    return when (style) {
        CombatStyleOption.MELEE -> listOf(
            WeaponOption("bronze_sword", "Bronze Sword", CombatStyleOption.MELEE),
            WeaponOption("iron_sword_common", "Iron Sword", CombatStyleOption.MELEE)
        )
        CombatStyleOption.RANGED -> listOf(
            WeaponOption("shortbow", "Shortbow", CombatStyleOption.RANGED)
        )
        CombatStyleOption.MAGIC -> listOf(
            WeaponOption("spark_bolt", "Spark Bolt Staff", CombatStyleOption.MAGIC)
        )
    }
}

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

@Composable
fun AppRoot() {
    var currentDestination by remember { mutableStateOf(AppDestination.HOME) }
    var skillsScreenState by remember { mutableStateOf<SkillsScreenState>(SkillsScreenState.List) }
    var combatScreenState by remember { mutableStateOf<CombatScreenState>(CombatScreenState.ZoneSelect) }

    val allSkills = remember { demoSkills() }
    val zones = remember { demoZones() }

    val homeState = remember {
        HomeScreenState(
            queueLabel = "Mining Iron Ore",
            queueEndsAt = Instant.now().plusSeconds(90),
            softCurrency = 1250,
            premiumCurrency = 40,
            currentHp = 80,
            maxHp = 100,
            isRecovering = false,
            pendingLootCount = 3,
            unreadNotificationCount = 2
        )
    }

    // Set to a future Instant (e.g. Instant.now().plusSeconds(600)) to test the recovery bar.
    val recoveringUntil = remember { mutableStateOf<Instant?>(null) }

    // Loadout state, shared across Combat and (later) Inventory.
    var loadoutStyle by remember { mutableStateOf(CombatStyleOption.MELEE) }
    var loadoutWeaponId by remember { mutableStateOf<String?>("bronze_sword") }
    var autoHeal by remember { mutableStateOf(30) }
    var autoFlee by remember { mutableStateOf(10) }

    // Toggle between SEARCHING and IN_COMBAT to test both simple views. In real wiring,
    // this comes from CombatService's session state instead of a manual toggle.
    var combatViewState by remember { mutableStateOf(CombatViewState.SEARCHING) }
    val demoCombatLog = remember {
        mutableStateListOf(
            CombatLogEntry("You entered Goblin Camp."),
            CombatLogEntry("Searching for an enemy...")
        )
    }

    val combatViewData = CombatViewData(
        zoneName = "Goblin Camp",
        viewState = combatViewState,
        searchEndsAt = if (combatViewState == CombatViewState.SEARCHING) Instant.now().plusSeconds(7) else null,
        monsterName = if (combatViewState == CombatViewState.IN_COMBAT) "Goblin Grunt" else null,
        monsterCurrentHp = if (combatViewState == CombatViewState.IN_COMBAT) 15 else null,
        monsterMaxHp = if (combatViewState == CombatViewState.IN_COMBAT) 25 else null,
        playerCurrentHp = 80,
        playerMaxHp = 100,
        lastHitChancePercent = if (combatViewState == CombatViewState.IN_COMBAT) 62.5 else null,
        lastDamageDealt = if (combatViewState == CombatViewState.IN_COMBAT) 4 else null,
        combatLog = demoCombatLog
    )

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
                    },
                    badgedDestinations = setOf(AppDestination.CHAT, AppDestination.GUILD)
                )

                when (currentDestination) {
                    AppDestination.HOME -> HomeScreen(
                        state = homeState,
                        onCollectLoot = { /* wire to CombatService.collectLoot later */ }
                    )

                    AppDestination.SKILLS -> {
                        when (val screen = skillsScreenState) {
                            is SkillsScreenState.List -> SkillsScreen(
                                allSkills = allSkills,
                                onSkillSelected = { skillsScreenState = SkillsScreenState.Detail(it) }
                            )
                            is SkillsScreenState.Detail -> {
                                val summary = allSkills[screen.skillId]
                                if (summary != null) {
                                    SkillDetailScreen(
                                        state = demoDetailFor(screen.skillId, summary),
                                        onBack = { skillsScreenState = SkillsScreenState.List },
                                        onStartAction = { /* wire to OfflineIdleService.startSkillingQueue later */ }
                                    )
                                }
                            }
                        }
                    }

                    AppDestination.COMBAT -> {
                        when (combatScreenState) {
                            CombatScreenState.ZoneSelect -> ZoneSelectScreen(
                                zones = zones,
                                playerLevel = 24, // demo player level -- matches Mining level for now
                                onZoneSelected = {
                                    combatScreenState = CombatScreenState.InZone
                                    combatViewState = CombatViewState.SEARCHING
                                },
                                onOpenLoadout = { combatScreenState = CombatScreenState.Loadout }
                            )

                            CombatScreenState.InZone -> CombatViewScreen(
                                data = combatViewData,
                                onLeaveZone = { combatScreenState = CombatScreenState.ZoneSelect }
                            )

                            CombatScreenState.Loadout -> LoadoutScreen(
                                state = LoadoutState(
                                    selectedStyle = loadoutStyle,
                                    availableWeapons = demoWeapons(loadoutStyle),
                                    selectedWeaponId = loadoutWeaponId,
                                    autoHealThresholdPercent = autoHeal,
                                    autoFleeThresholdPercent = autoFlee,
                                    isLocked = combatViewState == CombatViewState.IN_COMBAT,
                                    lockReason = "Locked during combat"
                                ),
                                onBack = { combatScreenState = CombatScreenState.ZoneSelect },
                                onStyleSelected = {
                                    loadoutStyle = it
                                    loadoutWeaponId = demoWeapons(it).firstOrNull()?.itemId
                                },
                                onWeaponSelected = { loadoutWeaponId = it },
                                onAutoHealChanged = { autoHeal = it },
                                onAutoFleeChanged = { autoFlee = it }
                            )
                        }
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
