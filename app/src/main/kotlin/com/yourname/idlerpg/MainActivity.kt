package com.yourname.idlerpg

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
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
// Stand-ins until real backend wiring replaces these. Levels
// are varied on purpose so the XP bars actually show something
// other than 0% across the list/grid/detail screens.
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
        // Rough placeholder XP math -- not the real curve, just enough
        // to populate a believable-looking progress bar per skill.
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

// =========================================================
// APP ROOT
// =========================================================

private sealed class ScreenState {
    object SkillsList : ScreenState()
    data class SkillDetail(val skillId: String) : ScreenState()
}

@Composable
fun AppRoot() {
    var currentDestination by remember { mutableStateOf(AppDestination.HOME) }
    var skillsScreenState by remember { mutableStateOf<ScreenState>(ScreenState.SkillsList) }

    val allSkills = remember { demoSkills() }

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

    Surface(modifier = Modifier.fillMaxSize()) {
        Row(modifier = Modifier.fillMaxSize()) {
            SideRail(
                currentDestination = currentDestination,
                onDestinationSelected = {
                    currentDestination = it
                    skillsScreenState = ScreenState.SkillsList // reset skill navigation when leaving the tab
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
                        is ScreenState.SkillsList -> SkillsScreen(
                            allSkills = allSkills,
                            onSkillSelected = { skillsScreenState = ScreenState.SkillDetail(it) }
                        )
                        is ScreenState.SkillDetail -> {
                            val summary = allSkills[screen.skillId]
                            if (summary != null) {
                                SkillDetailScreen(
                                    state = demoDetailFor(screen.skillId, summary),
                                    onBack = { skillsScreenState = ScreenState.SkillsList },
                                    onStartAction = { /* wire to OfflineIdleService.startSkillingQueue later */ }
                                )
                            }
                        }
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
