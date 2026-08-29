package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.background
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
import kotlinx.coroutines.delay
import java.time.Duration
import java.time.Instant

// =========================================================
// COMBAT VIEW SCREEN
// Two live states: SEARCHING (timer only) and IN_COMBAT
// (monster + player HP). Advanced toggle adds hit chance,
// exact damage, and a scrolling combat log in either state.
// =========================================================

enum class CombatViewState { SEARCHING, IN_COMBAT }

data class CombatLogEntry(
    val text: String,
    val timestamp: Instant = Instant.now()
)

data class SessionDropEntry(
    val itemName: String,
    val quantity: Int
)

data class CombatViewData(
    val zoneName: String,
    val viewState: CombatViewState,
    val searchEndsAt: Instant?,          // set only when SEARCHING
    val monsterName: String?,            // set only when IN_COMBAT
    val monsterCurrentHp: Int?,
    val monsterMaxHp: Int?,
    val playerCurrentHp: Int,
    val playerMaxHp: Int,
    val lastHitChancePercent: Double?,   // advanced view only
    val lastDamageDealt: Int?,           // advanced view only
    val combatLog: List<CombatLogEntry>,
    val sessionDrops: List<SessionDropEntry>
)

@Composable
fun CombatViewScreen(
    data: CombatViewData,
    onLeaveZone: () -> Unit,
    modifier: Modifier = Modifier
) {
    var showAdvanced by remember { mutableStateOf(false) }

    Column(modifier = modifier.fillMaxSize().padding(20.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onLeaveZone) {
                Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "Leave zone", tint = MaterialTheme.colorScheme.onSurface)
            }
            Spacer(modifier = Modifier.width(4.dp))
            Text(text = data.zoneName, style = MaterialTheme.typography.headlineMedium)
        }

        Spacer(modifier = Modifier.height(20.dp))

        when (data.viewState) {
            CombatViewState.SEARCHING -> SearchingView(data.searchEndsAt)
            CombatViewState.IN_COMBAT -> InCombatView(data)
        }

        Spacer(modifier = Modifier.height(16.dp))
        SessionDropsPanel(data.sessionDrops)

        Spacer(modifier = Modifier.height(16.dp))

        TextButton(onClick = { showAdvanced = !showAdvanced }) {
            Text(text = if (showAdvanced) "Hide details" else "Show details")
        }

        if (showAdvanced) {
            Spacer(modifier = Modifier.height(8.dp))
            AdvancedDetails(data)
        }
    }
}

@Composable
private fun SearchingView(searchEndsAt: Instant?) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(20.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = "Searching for an enemy...", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        if (searchEndsAt != null) {
            LiveCountdownText(searchEndsAt)
        }
    }
}

@Composable
private fun InCombatView(data: CombatViewData) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(20.dp)
    ) {
        Text(text = data.monsterName ?: "Unknown", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(6.dp))
        HpBarRow(
            label = "Enemy",
            current = data.monsterCurrentHp ?: 0,
            max = data.monsterMaxHp ?: 1,
            color = MaterialTheme.colorScheme.error
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(text = "You", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(6.dp))
        HpBarRow(
            label = "HP",
            current = data.playerCurrentHp,
            max = data.playerMaxHp,
            color = MaterialTheme.colorScheme.primary
        )
    }
}

@Composable
private fun SessionDropsPanel(drops: List<SessionDropEntry>) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(16.dp)
    ) {
        Text(text = "Drops This Session", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(6.dp))
        if (drops.isEmpty()) {
            Text(text = "No items yet.", style = MaterialTheme.typography.labelSmall)
        } else {
            drops.forEach { drop ->
                Text(
                    text = drop.itemName + " x" + drop.quantity,
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(vertical = 2.dp)
                )
            }
        }
    }
}

@Composable
private fun HpBarRow(label: String, current: Int, max: Int, color: androidx.compose.ui.graphics.Color) {
    val fraction = (current.toFloat() / max.toFloat()).coerceIn(0f, 1f)

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(10.dp)
            .clip(RoundedCornerShape(5.dp))
            .background(MaterialTheme.colorScheme.background)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth(fraction)
                .fillMaxHeight()
                .clip(RoundedCornerShape(5.dp))
                .background(color)
        )
    }
    Spacer(modifier = Modifier.height(2.dp))
    Text(text = "$current / $max", style = MaterialTheme.typography.labelSmall)
}

@Composable
private fun AdvancedDetails(data: CombatViewData) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(16.dp)
    ) {
        data.lastHitChancePercent?.let {
            Text(text = "Hit chance: " + String.format("%.1f", it) + "%", style = MaterialTheme.typography.labelSmall)
        }
        data.lastDamageDealt?.let {
            Text(text = "Last hit: " + it + " damage", style = MaterialTheme.typography.labelSmall)
        }

        Spacer(modifier = Modifier.height(12.dp))
        Text(text = "Combat Log", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(6.dp))

        LazyColumn(modifier = Modifier.heightIn(max = 200.dp)) {
            items(data.combatLog.reversed()) { entry ->
                Text(
                    text = entry.text,
                    style = MaterialTheme.typography.labelSmall,
                    modifier = Modifier.padding(vertical = 2.dp)
                )
            }
        }
    }
}

@Composable
private fun LiveCountdownText(endsAt: Instant) {
    var remaining by remember(endsAt) { mutableStateOf(Duration.between(Instant.now(), endsAt)) }

    LaunchedEffect(endsAt) {
        while (true) {
            remaining = Duration.between(Instant.now(), endsAt)
            if (remaining.isNegative || remaining.isZero) break
            delay(1000)
        }
    }

    val text = if (remaining.isNegative || remaining.isZero) {
        "Encounter starting..."
    } else {
        remaining.seconds.toString() + "s remaining"
    }

    Text(text = text, style = MaterialTheme.typography.bodyMedium)
}
