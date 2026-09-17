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
import androidx.compose.runtime.Composable
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
    val monsterNames: List<String>
)

@Composable
fun ZoneSelectScreen(
    zones: List<ZoneSummary>,
    playerLevel: Int,
    onZoneSelected: (String) -> Unit,
    onOpenLoadout: () -> Unit,
    modifier: Modifier = Modifier
) {
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

        LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            items(zones) { zone ->
                ZoneCard(
                    zone = zone,
                    isUnlocked = playerLevel >= zone.levelRequirement,
                    onClick = { if (playerLevel >= zone.levelRequirement) onZoneSelected(zone.zoneId) }
                )
            }
        }
    }
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
        Column(modifier = Modifier.alpha(contentAlpha)) {
            Text(
                text = zone.name,
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = zone.monsterNames.joinToString(", "),
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
