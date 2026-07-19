package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp

// =========================================================
// SKILL DETAIL SCREEN
// Simple view: level, XP bar, earned unlocks.
// Advanced view (toggle): exact XP numbers, XP-to-next-level,
// next unlock preview.
// Includes "Start" action to queue a gather/craft action for
// this skill directly from this screen.
// =========================================================

data class SkillUnlockSummary(val description: String, val levelRequired: Int)

data class SkillActionSummary(val actionId: String, val displayName: String, val levelRequired: Int)

data class SkillDetailState(
    val skillId: String,
    val displayName: String,
    val level: Int,
    val currentXp: Long,
    val xpToNextLevel: Long,
    val earnedUnlocks: List<SkillUnlockSummary>,
    val nextUnlock: SkillUnlockSummary?,       // null if none remaining
    val availableActions: List<SkillActionSummary>
)

@Composable
fun SkillDetailScreen(
    state: SkillDetailState,
    onBack: () -> Unit,
    onStartAction: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    var showAdvanced by remember { mutableStateOf(false) }
    var showActionPicker by remember { mutableStateOf(false) }

    Column(modifier = modifier.fillMaxSize().padding(20.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) {
                Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "Back")
            }
            Spacer(modifier = Modifier.width(4.dp))
            Text(text = state.displayName, style = MaterialTheme.typography.headlineMedium)
        }

        Spacer(modifier = Modifier.height(20.dp))

        Text(text = "Level " + state.level, style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        ThinProgressBarPublic(skillProgressFractionPublic(state.currentXp, state.xpToNextLevel))

        if (showAdvanced) {
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "XP: " + state.currentXp + "  |  " + state.xpToNextLevel + " to next level",
                style = MaterialTheme.typography.labelSmall
            )
            state.nextUnlock?.let {
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Next unlock at level " + it.levelRequired + ": " + it.description,
                    style = MaterialTheme.typography.labelSmall
                )
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        TextButton(onClick = { showAdvanced = !showAdvanced }) {
            Text(text = if (showAdvanced) "Hide details" else "Show details")
        }

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = { showActionPicker = true },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(text = "Start " + state.displayName)
        }

        Spacer(modifier = Modifier.height(24.dp))

        if (state.earnedUnlocks.isNotEmpty()) {
            Text(text = "Unlocks earned", style = MaterialTheme.typography.titleMedium)
            Spacer(modifier = Modifier.height(8.dp))
            state.earnedUnlocks.forEach { unlock ->
                Text(
                    text = "• " + unlock.description + " (Lv. " + unlock.levelRequired + ")",
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(vertical = 2.dp)
                )
            }
        }
    }

    if (showActionPicker) {
        ActionPickerSheet(
            actions = state.availableActions,
            onActionSelected = {
                showActionPicker = false
                onStartAction(it)
            },
            onDismiss = { showActionPicker = false }
        )
    }
}

@Composable
private fun ActionPickerSheet(
    actions: List<SkillActionSummary>,
    onActionSelected: (String) -> Unit,
    onDismiss: () -> Unit
) {
    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(modifier = Modifier.padding(20.dp)) {
            Text(text = "Choose an action", style = MaterialTheme.typography.titleMedium)
            Spacer(modifier = Modifier.height(12.dp))

            if (actions.isEmpty()) {
                Text(text = "No actions available at your current level.", style = MaterialTheme.typography.bodyMedium)
            }

            LazyColumn {
                items(actions) { action ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(10.dp))
                            .clickable { onActionSelected(action.actionId) }
                            .padding(vertical = 12.dp, horizontal = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(text = action.displayName, style = MaterialTheme.typography.bodyMedium)
                        Text(text = "Lv. " + action.levelRequired, style = MaterialTheme.typography.labelSmall)
                    }
                }
            }
        }
    }
}

@Composable
private fun ThinProgressBarPublic(fraction: Float) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(6.dp)
            .clip(RoundedCornerShape(3.dp))
            .background(MaterialTheme.colorScheme.background)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth(fraction)
                .fillMaxHeight()
                .clip(RoundedCornerShape(3.dp))
                .background(MaterialTheme.colorScheme.primary)
        )
    }
}

private fun skillProgressFractionPublic(currentXp: Long, xpToNextLevel: Long): Float {
    val total = currentXp + xpToNextLevel
    if (total <= 0) return 0f
    return (currentXp.toFloat() / total.toFloat()).coerceIn(0f, 1f)
}
