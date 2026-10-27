package com.yourname.idlerpg.ui.screens

import com.yourname.idlerpg.ui.theme.overrideColor

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
import com.yourname.idlerpg.data.ActiveQueueInfo

// =========================================================
// SKILL DETAIL SCREEN
// Simple view: level, XP bar, earned unlocks.
// Advanced view (toggle): exact XP numbers, XP-to-next-level,
// next unlock preview.
// Includes "Start" action to queue a gather/craft action for
// this skill directly from this screen.
// =========================================================

data class SkillUnlockSummary(val description: String, val levelRequired: Int)

data class MissingIngredientSummary(val displayName: String, val required: Int, val have: Int)

data class SkillActionSummary(
    val actionId: String,
    val displayName: String,
    val levelRequired: Int,
    val requiredIngredients: List<MissingIngredientSummary> = emptyList(),
    val isLocked: Boolean = false
)


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
    modifier: Modifier = Modifier,
    startButtonLabel: String = "Start " + state.displayName,
    activeQueue: ActiveQueueInfo? = null,
    onStartCraftingAction: ((String, Int?) -> Unit)? = null,
    maxCraftableQuantity: (String) -> Int = { 0 }
) {
    var showAdvanced by remember { mutableStateOf(false) }
    var showActionPicker by remember { mutableStateOf(false) }
    var pendingCraftItemId by remember { mutableStateOf<String?>(null) }
    var selectedCraftQuantity by remember { mutableStateOf(1) }
    var customCraftQuantity by remember { mutableStateOf("1") }
    
    Column(modifier = modifier.fillMaxSize().padding(20.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) {
                Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "Back", tint = MaterialTheme.colorScheme.onSurface)
            }
            Spacer(modifier = Modifier.width(4.dp))
            Text(text = state.displayName, style = MaterialTheme.typography.headlineMedium)
        }

        activeQueue?.let {
            Spacer(modifier = Modifier.height(8.dp))
            CycleCountdown(queue = it)
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
            Text(text = startButtonLabel)
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
            onActionSelected = { itemId ->
                showActionPicker = false

                if (onStartCraftingAction != null) {
                    pendingCraftItemId = itemId
                    selectedCraftQuantity = 1
                    customCraftQuantity = "1"
                } else {
                    onStartAction(itemId)
                }
            },
            onDismiss = { showActionPicker = false }
        )
    }

    val craftItemId = pendingCraftItemId
    if (craftItemId != null && onStartCraftingAction != null) {
        val maxQuantity = maxCraftableQuantity(craftItemId)
        val customQuantity = customCraftQuantity.toIntOrNull() ?: 0
        val selectedQuantity = when (selectedCraftQuantity) {
            -1 -> customQuantity
            -2 -> maxQuantity
            else -> selectedCraftQuantity
        }

        AlertDialog(
            onDismissRequest = { pendingCraftItemId = null },
            title = { Text("Choose quantity") },
            text = {
                Column(
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text("Maximum craftable: $maxQuantity")

                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        listOf(1, 5, 10).forEach { quantity ->
                            TextButton(
                                enabled = maxQuantity >= quantity,
                                onClick = {
                                    selectedCraftQuantity = quantity
                                }
                            ) {
                                Text(
                                    text = if (selectedCraftQuantity == quantity) {
                                        "[$quantity]"
                                    } else {
                                        quantity.toString()
                                    }
                                )
                            }
                        }
                    }

                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        TextButton(
                            enabled = maxQuantity > 0,
                            onClick = { selectedCraftQuantity = -1 }
                        ) {
                            Text(
                                if (selectedCraftQuantity == -1) {
                                    "[Custom]"
                                } else {
                                    "Custom"
                                }
                            )
                        }

                        TextButton(
                            enabled = maxQuantity > 0,
                            onClick = { selectedCraftQuantity = -2 }
                        ) {
                            Text(
                                if (selectedCraftQuantity == -2) {
                                    "[Craft All]"
                                } else {
                                    "Craft All"
                                }
                            )
                        }
                    }

                    if (selectedCraftQuantity == -1) {
                        OutlinedTextField(
                            value = customCraftQuantity,
                            onValueChange = { value ->
                                if (value.all { it.isDigit() }) {
                                    customCraftQuantity = value
                                }
                            },
                            label = { Text("Custom quantity") },
                            singleLine = true
                        )
                    }

                    if (maxQuantity == 0) {
                        Text(
                            "You don't have enough materials to craft this recipe.",
                            color = MaterialTheme.colorScheme.error
                        )
                    } else if (selectedQuantity > maxQuantity) {
                        Text(
                            "Quantity will be limited to $maxQuantity.",
                            color = MaterialTheme.colorScheme.error
                        )
                    }
                }
            },
            confirmButton = {
                Button(
                    enabled = maxQuantity > 0 &&
                        selectedQuantity in 1..maxQuantity,
                    onClick = {
                        onStartCraftingAction(
                            craftItemId,
                            selectedQuantity
                        )
                        pendingCraftItemId = null
                    }
                ) {
                    Text("Start crafting")
                }
            },
            dismissButton = {
                TextButton(
                    onClick = { pendingCraftItemId = null }
                ) {
                    Text("Cancel")
                }
            }
        )
    }
}

@OptIn(androidx.compose.material3.ExperimentalMaterial3Api::class)
@Composable
private fun ActionPickerSheet(
    actions: List<SkillActionSummary>,
    onActionSelected: (String) -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(text = "Choose an action", style = MaterialTheme.typography.titleMedium) },
        text = {
            Column {
                if (actions.isEmpty()) {
                    Text(text = "No actions available at your current level.", style = MaterialTheme.typography.bodyMedium)
                }

                LazyColumn(modifier = Modifier.heightIn(max = 300.dp)) {
                    items(actions) { action ->
                        ActionRow(action = action, onActionSelected = onActionSelected)
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text(text = "Cancel")
            }
        }
    )
}

@Composable
private fun ActionRow(
    action: SkillActionSummary,
    onActionSelected: (String) -> Unit
) {
    var showDetails by remember { mutableStateOf(false) }

    val hasMaterials = action.requiredIngredients.all {
        it.have >= it.required
    }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .clickable { showDetails = true }
            .padding(vertical = 12.dp, horizontal = 8.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = (if (action.isLocked) "🔒 " else "") +
                    action.displayName,
                style = MaterialTheme.typography.bodyMedium,
                color = if (action.isLocked) {
                    MaterialTheme.colorScheme.onSurfaceVariant
                } else {
                    MaterialTheme.colorScheme.onSurface
                },
                modifier = Modifier.weight(1f)
            )

            Text(
                text = "Lv. ${action.levelRequired}",
                style = MaterialTheme.typography.labelSmall
            )
        }

        Spacer(Modifier.height(4.dp))

        Text(
            text = if (action.requiredIngredients.isEmpty()) {
                "Materials: None required"
            } else {
                "Requires: " + action.requiredIngredients.joinToString(", ") {
                    "${it.displayName} ×${it.required}"
                }
            },
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        if (action.isLocked) {
            Text(
                text = "Requires level ${action.levelRequired}",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.error
            )
        } else if (!hasMaterials) {
            Text(
                text = "Missing required materials",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.error
            )
        }
    }

    if (showDetails) {
        AlertDialog(
            onDismissRequest = { showDetails = false },
            title = {
                Text(action.displayName)
            },
            text = {
                Column(
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text("Required skill level: ${action.levelRequired}")

                    if (action.isLocked) {
                        Text(
                            "Your current level is too low to start this action.",
                            color = MaterialTheme.colorScheme.error
                        )
                    }

                    HorizontalDivider()

                    Text(
                        "Required items",
                        style = MaterialTheme.typography.titleSmall
                    )

                    if (action.requiredIngredients.isEmpty()) {
                        Text("No inventory items are required.")
                    } else {
                        action.requiredIngredients.forEach { ingredient ->
                            Text(
                                "${ingredient.displayName}: " +
                                    "have ${ingredient.have} / " +
                                    "need ${ingredient.required}",
                                color = if (ingredient.have >= ingredient.required) {
                                    MaterialTheme.colorScheme.onSurface
                                } else {
                                    MaterialTheme.colorScheme.error
                                }
                            )
                        }
                    }
                }
            },
            confirmButton = {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    TextButton(
                        onClick = { showDetails = false }
                    ) {
                        Text("Close")
                    }

                    Button(
                        enabled = !action.isLocked && hasMaterials,
                        onClick = {
                            showDetails = false
                            onActionSelected(action.actionId)
                        }
                    ) {
                        Text("Start")
                    }
                }
            }
        )
    }
}

@Composable
fun MissingIngredientsDialog(
    itemName: String,
    missing: List<MissingIngredientSummary>,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(text = "Missing materials", style = MaterialTheme.typography.titleMedium) },
        text = {
            Column {
                Text(
                    text = "You need the following to craft " + itemName + ":",
                    style = MaterialTheme.typography.bodyMedium
                )
                Spacer(modifier = Modifier.height(8.dp))
                missing.forEach {
                    Text(
                        text = "\u2022 " + it.displayName + ": have " + it.have + " / need " + it.required,
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text(text = "OK")
            }
        }
    )
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
