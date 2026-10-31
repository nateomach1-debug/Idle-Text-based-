package com.yourname.idlerpg.ui.screens

import com.yourname.idlerpg.ui.theme.overrideColor

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.yourname.idlerpg.SkillType
import com.yourname.idlerpg.PrayerDefinition
import com.yourname.idlerpg.PotionEffectCatalog

// =========================================================
// LOADOUT SCREEN
// Auto-heal/flee thresholds, plus Food/Potion selection.
// Accessible from both Combat and Inventory via a push button
// (per spec). Combat Style/Weapon sections were dropped since
// they're meaningless until real combat is wired up.
// =========================================================

data class ConsumableOption(val itemId: String, val displayName: String, val quantity: Int)

data class LoadoutState(
    val availableFood: List<ConsumableOption>,
    val selectedFoodId: String?,
    val availablePotions: List<ConsumableOption>,
    val selectedPotionId: String?,
    val potionTimerRemainingSeconds: Int,
    val autoHealThresholdPercent: Int,
    val autoFleeThresholdPercent: Int,
    val isSkilling: Boolean = false
)

@Composable
fun LoadoutScreen(
    state: LoadoutState,
    onBack: () -> Unit,
    onFoodSelected: (String?) -> Unit,
    onPotionSelected: (String) -> Unit,
    onAutoHealChanged: (Int) -> Unit,
    onAutoFleeChanged: (Int) -> Unit,
    trainingSkill: SkillType? = null,
    allowedTrainingSkills: List<SkillType> = emptyList(),
    onTrainingSkillSelected: (SkillType) -> Unit = {},
    selectedPrayerId: String? = null,
    prayerOptions: List<PrayerDefinition> = emptyList(),
    prayerLevel: Int = 1,
    onPrayerSelected: (String) -> Unit = {},
    modifier: Modifier = Modifier
) {    
    val selectedPotionInfo = state.selectedPotionId?.let {
        PotionEffectCatalog.effectsFor(it)
    } ?: emptyList()

    val selectedPotionEffects = selectedPotionInfo.filterNot {
        it.startsWith("Duration:")
    }

    val selectedPotionHasTimedEffect = selectedPotionInfo.any {
        it.startsWith("Duration:")
    }

    val selectedPotionName = state.selectedPotionId?.let { selectedId ->
        state.availablePotions.firstOrNull {
            it.itemId == selectedId
        }?.displayName ?: selectedId.split("_").joinToString(" ") { word ->
            word.replaceFirstChar { it.uppercase() }
        }
    } ?: "Potion"

    val potionTimeText = "%d:%02d".format(
        state.potionTimerRemainingSeconds / 60,
        state.potionTimerRemainingSeconds % 60
    )
    Column(modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) {
                Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "Back", tint = MaterialTheme.colorScheme.onSurface)
            }
            Spacer(modifier = Modifier.width(4.dp))
            Text(text = "Loadout", style = MaterialTheme.typography.headlineMedium)
        }

        Spacer(modifier = Modifier.height(20.dp))

        Text(text = "Auto-Heal Threshold: " + state.autoHealThresholdPercent + "%", style = MaterialTheme.typography.titleMedium)
        Slider(
            value = state.autoHealThresholdPercent.toFloat(),
            onValueChange = { onAutoHealChanged(it.toInt()) },
            valueRange = 0f..100f
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(text = "Auto-Flee Threshold: " + state.autoFleeThresholdPercent + "%", style = MaterialTheme.typography.titleMedium)
        Slider(
            value = state.autoFleeThresholdPercent.toFloat(),
            onValueChange = { onAutoFleeChanged(it.toInt()) },
            valueRange = 0f..100f
        )

        Spacer(modifier = Modifier.height(24.dp))

        if (trainingSkill != null && allowedTrainingSkills.isNotEmpty()) {
            Text(text = "Training", style = MaterialTheme.typography.titleMedium)
            Spacer(modifier = Modifier.height(8.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                allowedTrainingSkills.forEach { skill ->
                    val selected = skill == trainingSkill
                    val background = if (selected) {
                        MaterialTheme.colorScheme.primary.copy(alpha = 0.2f)
                    } else {
                        MaterialTheme.colorScheme.surfaceVariant
                    }
                    Text(
                        text = skill.name.lowercase().replaceFirstChar { it.uppercase() },
                        style = MaterialTheme.typography.bodyMedium,
                        modifier = Modifier
                            .clip(RoundedCornerShape(10.dp))
                            .background(background)
                            .clickable { onTrainingSkillSelected(skill) }
                            .padding(horizontal = 12.dp, vertical = 8.dp)
                    )
                }
            }
            Spacer(modifier = Modifier.height(24.dp))
        }

        Text(text = "Food", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        if (state.availableFood.isEmpty()) {
            Text(text = "No food in inventory.", style = MaterialTheme.typography.bodyMedium)
        } else {
            state.availableFood.forEach { food ->
                ConsumableRow(
                    option = food,
                    isSelected = food.itemId == state.selectedFoodId,
                    onClick = { onFoodSelected(if (food.itemId == state.selectedFoodId) null else food.itemId) }
                )
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

                Text(text = "Potion", style = MaterialTheme.typography.titleMedium)

        Spacer(modifier = Modifier.height(8.dp))

        if (state.selectedPotionId == null) {
            Text(
                "No potion selected.",
                style = MaterialTheme.typography.bodyMedium
            )
        } else {
            val isActive = state.potionTimerRemainingSeconds > 0

            Surface(
                modifier = Modifier.fillMaxWidth(),
                color = if (isActive) {
                    MaterialTheme.colorScheme.primaryContainer
                } else {
                    MaterialTheme.colorScheme.surfaceVariant
                },
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(
                    modifier = Modifier.padding(12.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        if (isActive) "POTION ACTIVE" else "POTION NOT ACTIVE",
                        style = MaterialTheme.typography.titleSmall
                    )

                    Text(
                        selectedPotionName,
                        style = MaterialTheme.typography.titleMedium
                    )

                    selectedPotionEffects.forEach { effect ->
                        Text(
                            "• $effect",
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }

                    if (isActive) {
                        Text("Time remaining: $potionTimeText")

                        if (selectedPotionEffects.any {
                            it.contains("skilling", ignoreCase = true)
                        }) {
                            Text(
                                "Speed bonus applies while a skilling action is running.",
                                style = MaterialTheme.typography.bodySmall
                            )
                        }
                    } else if (selectedPotionHasTimedEffect) {
                        val hasCopies = state.availablePotions.any {
                            it.itemId == state.selectedPotionId && it.quantity > 0
                        }

                        Text(
                            if (hasCopies) {
                                "Selected — waiting for activation."
                            } else {
                                "No copies remain. The potion cannot activate."
                            },
                            style = MaterialTheme.typography.bodySmall
                        )
                    } else {
                        Text(
                            "This potion does not have an active timed effect.",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                }
            }
        }
        Spacer(modifier = Modifier.height(8.dp))
        if (state.availablePotions.isEmpty()) {
            Text(text = "No potions in inventory.", style = MaterialTheme.typography.bodyMedium)
        } else {
            state.availablePotions.forEach { potion ->
                ConsumableRow(
                    option = potion,
                    isSelected = potion.itemId == state.selectedPotionId,
                    onClick = { onPotionSelected(potion.itemId) }
                )
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        Text(text = "Prayer", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        Column {
            prayerOptions.forEach { prayer ->
                val selected = prayer.id == selectedPrayerId
                val locked = prayerLevel < prayer.levelRequired
                val background = if (selected) {
                    MaterialTheme.colorScheme.primary.copy(alpha = 0.2f)
                } else {
                    MaterialTheme.colorScheme.surfaceVariant
                }
                val textColor = if (locked) {
                    MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
                } else {
                    MaterialTheme.colorScheme.onSurface
                }
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp)
                        .clip(RoundedCornerShape(10.dp))
                        .background(background)
                        .clickable(enabled = !locked) { onPrayerSelected(prayer.id) }
                        .padding(12.dp)
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(text = prayer.displayName, style = MaterialTheme.typography.bodyMedium, color = overrideColor(textColor))
                        Text(text = prayer.description, style = MaterialTheme.typography.labelSmall, color = overrideColor(textColor))
                    }
                    if (locked) {
                        Text(text = "Lv " + prayer.levelRequired, style = MaterialTheme.typography.labelSmall, color = overrideColor(textColor))
                    }
                }
            }
        }
    }
}

@Composable
private fun ConsumableRow(option: ConsumableOption, isSelected: Boolean, onClick: () -> Unit) {
    val backgroundColor = if (isSelected) MaterialTheme.colorScheme.primary.copy(alpha = 0.15f) else MaterialTheme.colorScheme.surface

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp)
            .clip(RoundedCornerShape(10.dp))
            .background(backgroundColor)
            .clickable { onClick() }
            .padding(12.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = option.displayName,
            style = MaterialTheme.typography.bodyMedium,
            maxLines = 1,
            softWrap = false,
            overflow = TextOverflow.Ellipsis
        )
        Text(text = "x" + option.quantity, style = MaterialTheme.typography.labelSmall)
    }
}
