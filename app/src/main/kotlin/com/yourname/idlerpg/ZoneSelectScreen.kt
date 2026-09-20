package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material3.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp

// =========================================================
// ZONE SELECT SCREEN
// All zones visible; locked ones (above the player's level)
// shown greyed out with their requirement displayed instead
// of being hidden entirely.
// =========================================================

data class ZoneSummary(
    val zoneId: String,
    val name: String,
    val levelRequirement: Int,
    val monsterNames: List<String>,
    val monsters: List<ZoneMonsterSummary> = emptyList()
)

// One selectable monster in a zone. weaknessLabel is display text ("Fire", "Melee", ...).
data class ZoneMonsterSummary(
    val monsterId: String,
    val name: String,
    val level: Int,
    val weaknessLabel: String
)

@Composable
fun ZoneSelectScreen(
    zones: List<ZoneSummary>,
    playerLevel: Int,
    onZoneSelected: (zoneId: String, monsterId: String) -> Unit,
    onOpenLoadout: () -> Unit,
    modifier: Modifier = Modifier
) {
    var pickerZoneId by rememberSaveable { mutableStateOf<String?>(null) }

    Column(modifier = modifier.fillMaxSize().padding(20.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(text = "Combat", style = MaterialTheme.typography.headlineMedium)
            TextButton(onClick = onOpenLoadout) {
                Text(text = "Loadout")
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Tap a zone to choose a monster. Brackets show each monster's weakness.",
            style = MaterialTheme.typography.labelSmall,
            modifier = Modifier.alpha(0.7f)
        )
        Spacer(modifier = Modifier.height(10.dp))

        LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            items(zones) { zone ->
                ZoneCard(
                    zone = zone,
                    isUnlocked = playerLevel >= zone.levelRequirement,
                    onClick = { if (playerLevel >= zone.levelRequirement) pickerZoneId = zone.zoneId }
                )
            }
        }
    }

    val pickerZone = zones.find { it.zoneId == pickerZoneId }
    if (pickerZone != null) {
        MonsterPickerDialog(
            zone = pickerZone,
            onPick = { monsterId ->
                pickerZoneId = null
                onZoneSelected(pickerZone.zoneId, monsterId)
            },
            onDismiss = { pickerZoneId = null }
        )
    }
}

@Composable
private fun MonsterPickerDialog(
    zone: ZoneSummary,
    onPick: (String) -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(text = zone.name) },
        text = {
            Column(
                modifier = Modifier.verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = "Choose which monster to fight:",
                    style = MaterialTheme.typography.bodyMedium
                )
                zone.monsters.forEach { monster ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(10.dp))
                            .background(MaterialTheme.colorScheme.onSurface.copy(alpha = 0.08f))
                            .clickable { onPick(monster.monsterId) }
                            .padding(12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(text = monster.name, style = MaterialTheme.typography.titleSmall)
                            Text(text = "Lv. " + monster.level, style = MaterialTheme.typography.labelSmall)
                        }
                        Text(
                            text = "Weak: " + monster.weaknessLabel,
                            style = MaterialTheme.typography.labelMedium
                        )
                    }
                }
            }
        },
        confirmButton = {},
        dismissButton = {
            TextButton(onClick = onDismiss) { Text(text = "Cancel") }
        }
    )
}

@Composable
private fun ZoneCard(zone: ZoneSummary, isUnlocked: Boolean, onClick: () -> Unit) {
    val backgroundColor = if (isUnlocked) MaterialTheme.colorScheme.surface else MaterialTheme.colorScheme.surface.copy(alpha = 0.5f)
    val contentAlpha = if (isUnlocked) 1f else 0.5f

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(backgroundColor)
            .clickable(enabled = isUnlocked) { onClick() }
            .padding(16.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f).padding(end = 8.dp).alpha(contentAlpha)) {
            Text(
                text = zone.name,
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = if (zone.monsters.isNotEmpty()) {
                    zone.monsters.joinToString("  \u2022  ") { it.name + " (" + it.weaknessLabel + ")" }
                } else {
                    zone.monsterNames.joinToString(", ")
                },
                style = MaterialTheme.typography.labelSmall
            )
        }

        if (!isUnlocked) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Filled.Lock,
                    contentDescription = "Locked",
                    tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                    modifier = Modifier.size(16.dp)
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = "Lv. " + zone.levelRequirement,
                    style = MaterialTheme.typography.labelSmall
                )
            }
        }
    }
}
