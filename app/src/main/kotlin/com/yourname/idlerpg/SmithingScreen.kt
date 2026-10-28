package com.yourname.idlerpg

import com.yourname.idlerpg.ui.theme.overrideColor

import com.yourname.idlerpg.ui.screens.MissingIngredientSummary
import com.yourname.idlerpg.ui.screens.MissingIngredientsDialog
import com.yourname.idlerpg.ui.screens.SkillUnlockSummary
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Info
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp

// =========================================================
// SMITHING SCREEN DATA MODELS
// =========================================================

data class SmithingMaterialOption(val materialId: String, val displayName: String)

data class SmithingIngredientSummary(val itemId: String, val displayName: String, val quantity: Int)

data class SmithingRecipeSummary(
    val itemId: String,
    val displayName: String,
    val levelRequired: Int,
    val ingredients: List<SmithingIngredientSummary>,
    val requiredIngredients: List<MissingIngredientSummary> = emptyList()
)


data class SmithingMaterialCatalogEntry(
    val material: SmithingMaterialOption,
    val bar: SmithingRecipeSummary?,
    val gear: List<SmithingRecipeSummary>
)

data class SmithingState(
    val displayName: String,
    val level: Int,
    val currentXp: Long,
    val xpToNextLevel: Long,
    val materials: List<SmithingMaterialCatalogEntry>,
    val earnedUnlocks: List<SkillUnlockSummary> = emptyList(),
    val nextUnlock: SkillUnlockSummary? = null
)

// =========================================================
// SMITHING SCREEN
// =========================================================

@Composable
fun SmithingScreen(
    state: SmithingState,
    onBack: () -> Unit,
    onStartAction: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    var materialDropdownExpanded by remember { mutableStateOf(false) }
    var selectedMaterialId by remember { mutableStateOf<String?>(null) }
    var showAdvanced by remember { mutableStateOf(false) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(20.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) {
                Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "Back", tint = MaterialTheme.colorScheme.onSurface)
            }
            Spacer(modifier = Modifier.width(4.dp))
            Text(text = state.displayName, style = MaterialTheme.typography.headlineMedium)
        }

        Spacer(modifier = Modifier.height(20.dp))
        Text(text = "Level " + state.level, style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        SmithingXpBar(state.currentXp, state.xpToNextLevel)

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

        Box {
            Button(
                onClick = { materialDropdownExpanded = true },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(text = "Select Material")
            }
            DropdownMenu(
                expanded = materialDropdownExpanded,
                onDismissRequest = { materialDropdownExpanded = false }
            ) {
                state.materials.forEach { entry ->
                    DropdownMenuItem(
                        text = { Text(text = entry.material.displayName) },
                        onClick = {
                            materialDropdownExpanded = false
                            selectedMaterialId = entry.material.materialId
                        }
                    )
                }
            }
        }

        if (state.earnedUnlocks.isNotEmpty()) {
            Spacer(modifier = Modifier.height(24.dp))
            Text(text = "Unlocks earned", style = MaterialTheme.typography.titleMedium)
            Spacer(modifier = Modifier.height(8.dp))
            state.earnedUnlocks.forEach { unlock ->
                Text(
                    text = "\u2022 " + unlock.description + " (Lv. " + unlock.levelRequired + ")",
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(vertical = 2.dp)
                )
            }
        }
    }

    val selectedEntry = state.materials.find { it.material.materialId == selectedMaterialId }
    if (selectedEntry != null) {
        SmithingMaterialPickerDialog(
            entry = selectedEntry,
            playerLevel = state.level,
            onItemSelected = { itemId ->
                selectedMaterialId = null
                onStartAction(itemId)
            },
            onDismiss = { selectedMaterialId = null }
        )
    }
}

@Composable
private fun SmithingXpBar(currentXp: Long, xpToNextLevel: Long) {
    val total = currentXp + xpToNextLevel
    val fraction = if (total > 0) (currentXp.toFloat() / total.toFloat()).coerceIn(0f, 1f) else 0f
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(6.dp)
            .clip(RoundedCornerShape(3.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant)
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

// =========================================================
// MATERIAL PICKER DIALOG -- Bars / Gear toggle
// =========================================================

@Composable
private fun SmithingMaterialPickerDialog(
    entry: SmithingMaterialCatalogEntry,
    playerLevel: Int,
    onItemSelected: (String) -> Unit,
    onDismiss: () -> Unit
) {
    var showingBars by remember { mutableStateOf(false) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(text = entry.material.displayName, style = MaterialTheme.typography.titleMedium) },
        text = {
            Column {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Button(
                        onClick = { showingBars = false },
                        modifier = Modifier.weight(1f),
                        colors = if (!showingBars) {
                            ButtonDefaults.buttonColors()
                        } else {
                            ButtonDefaults.buttonColors(
                                containerColor = MaterialTheme.colorScheme.surfaceVariant,
                                contentColor = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    ) {
                        Text(text = "Gear")
                    }
                    Button(
                        onClick = { showingBars = true },
                        modifier = Modifier.weight(1f),
                        colors = if (showingBars) {
                            ButtonDefaults.buttonColors()
                        } else {
                            ButtonDefaults.buttonColors(
                                containerColor = MaterialTheme.colorScheme.surfaceVariant,
                                contentColor = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    ) {
                        Text(text = "Bars")
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))

                if (showingBars) {
                    val bar = entry.bar
                    if (bar == null) {
                        Text(
                            text = "No bar recipe for this material.",
                            style = MaterialTheme.typography.bodyMedium
                        )
                    } else {
                        LazyColumn(modifier = Modifier.heightIn(max = 320.dp)) {
                            item {
                                SmithingRecipeRow(
                                    recipe = bar,
                                    playerLevel = playerLevel,
                                    onClick = { onItemSelected(bar.itemId) }
                                )
                            }
                        }
                    }
                } else {
                    if (entry.gear.isEmpty()) {
                        Text(
                            text = "No gear recipes for this material.",
                            style = MaterialTheme.typography.bodyMedium
                        )
                    } else {
                        LazyColumn(modifier = Modifier.heightIn(max = 320.dp)) {
                            items(entry.gear) { recipe ->
                                SmithingRecipeRow(
                                    recipe = recipe,
                                    playerLevel = playerLevel,
                                    onClick = { onItemSelected(recipe.itemId) }
                                )
                            }
                        }
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) { Text(text = "Cancel") }
        }
    )
}

@Composable
private fun SmithingRecipeRow(
    recipe: SmithingRecipeSummary,
    playerLevel: Int,
    onClick: () -> Unit
) {
    var showDetails by remember { mutableStateOf(false) }

    val levelOk = playerLevel >= recipe.levelRequired
    val ingredientsOk = recipe.requiredIngredients.all {
        it.have >= it.required
    }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .padding(vertical = 8.dp, horizontal = 8.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clickable(
                    enabled = levelOk && ingredientsOk
                ) {
                    onClick()
                },
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = (if (!levelOk) "🔒 " else "") + recipe.displayName,
                style = MaterialTheme.typography.bodyMedium,
                color = overrideColor(
                    if (levelOk && ingredientsOk) {
                        MaterialTheme.colorScheme.onSurface
                    } else {
                        MaterialTheme.colorScheme.onSurface.copy(alpha = 0.65f)
                    }
                ),
                modifier = Modifier.weight(1f)
            )

            Text(
                text = "Lv. ${recipe.levelRequired}",
                style = MaterialTheme.typography.labelSmall
            )

            IconButton(
                onClick = { showDetails = true },
                modifier = Modifier.size(32.dp)
            ) {
                Icon(
                    imageVector = Icons.Filled.Info,
                    contentDescription =
                        "View ${recipe.displayName} requirements",
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }

    if (showDetails) {
        AlertDialog(
            onDismissRequest = { showDetails = false },
            title = { Text(recipe.displayName) },
            text = {
                Column(
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        "Required Smithing level: ${recipe.levelRequired}"
                    )

                    if (!levelOk) {
                        Text(
                            "Your current level is too low to start this recipe.",
                            color = MaterialTheme.colorScheme.error
                        )
                    }

                    HorizontalDivider()

                    Text(
                        "Required items",
                        style = MaterialTheme.typography.titleSmall
                    )

                    if (recipe.requiredIngredients.isEmpty()) {
                        Text("No inventory items are required.")
                    } else {
                        recipe.requiredIngredients.forEach { ingredient ->
                            Text(
                                "${ingredient.displayName}: have " +
                                    "${ingredient.have} / need ${ingredient.required}",
                                color = if (
                                    ingredient.have >= ingredient.required
                                ) {
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
                        enabled = levelOk && ingredientsOk,
                        onClick = {
                            showDetails = false
                            onClick()
                        }
                    ) {
                        Text("Start")
                    }
                }
            }
        )
    }
}
