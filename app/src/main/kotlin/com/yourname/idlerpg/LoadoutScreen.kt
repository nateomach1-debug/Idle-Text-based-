package com.yourname.idlerpg.ui.screens

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
    val autoFleeThresholdPercent: Int
)

@Composable
fun LoadoutScreen(
    state: LoadoutState,
    onBack: () -> Unit,
    onFoodSelected: (String) -> Unit,
    onPotionSelected: (String) -> Unit,
    onAutoHealChanged: (Int) -> Unit,
    onAutoFleeChanged: (Int) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) {
                Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "Back")
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

        Text(text = "Food", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        if (state.availableFood.isEmpty()) {
            Text(text = "No food in inventory.", style = MaterialTheme.typography.bodyMedium)
        } else {
            state.availableFood.forEach { food ->
                ConsumableRow(
                    option = food,
                    isSelected = food.itemId == state.selectedFoodId,
                    onClick = { onFoodSelected(food.itemId) }
                )
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        Text(text = "Potion", style = MaterialTheme.typography.titleMedium)
        if (state.selectedPotionId != null && state.potionTimerRemainingSeconds > 0) {
            Text(
                text = "Refreshes in " + state.potionTimerRemainingSeconds + "s",
                style = MaterialTheme.typography.labelSmall
            )
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
