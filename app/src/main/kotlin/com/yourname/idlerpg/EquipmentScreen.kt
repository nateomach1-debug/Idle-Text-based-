package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp

// =========================================================
// EQUIPMENT SCREEN (the "paper doll")
// All 9 slots shown; locked slots show a lock icon, same
// visual language as Zone Select's locked zones.
// =========================================================

enum class EquipSlotUi { WEAPON, HELMET, CHESTPLATE, GLOVES, BOOTS, NECKLACE, RING_1, RING_2, TOOL, LEGS, SHIELD, CAPE, AMMO }

data class EquippedItemInfo(val itemId: String, val displayName: String)

data class EquipmentScreenState(
    val equipped: Map<EquipSlotUi, EquippedItemInfo?>,
    val lockedSlots: Set<EquipSlotUi> // slots currently locked (combat/recovery) -- TOOL never appears here
)

@Composable
fun EquipmentScreen(
    state: EquipmentScreenState,
    onBack: () -> Unit,
    onSlotTapped: (EquipSlotUi) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) {
                Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "Back")
            }
            Spacer(modifier = Modifier.width(4.dp))
            Text(text = "Equipment", style = MaterialTheme.typography.headlineMedium)
        }

        Spacer(modifier = Modifier.height(20.dp))

        EquipSlotUi.values().forEach { slot ->
            EquipmentSlotRow(
                slot = slot,
                equippedItem = state.equipped[slot],
                isLocked = slot in state.lockedSlots,
                onClick = { onSlotTapped(slot) }
            )
            Spacer(modifier = Modifier.height(8.dp))
        }
    }
}

@Composable
private fun EquipmentSlotRow(
    slot: EquipSlotUi,
    equippedItem: EquippedItemInfo?,
    isLocked: Boolean,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .clickable(onClick = onClick)
            .padding(14.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text(text = slot.name, style = MaterialTheme.typography.labelSmall)
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = equippedItem?.displayName ?: "Empty",
                style = MaterialTheme.typography.titleMedium
            )
        }

        if (isLocked) {
            Icon(
                imageVector = Icons.Filled.Lock,
                contentDescription = "Locked",
                tint = MaterialTheme.colorScheme.error,
                modifier = Modifier.size(18.dp)
            )
        }
    }
}
