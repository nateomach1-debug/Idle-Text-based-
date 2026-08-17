package com.yourname.idlerpg.ui.navigation

import androidx.compose.animation.animateContentSize
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp

// =========================================================
// COLLAPSIBLE SIDE RAIL
// Collapsed by default: icon-only strip. Tapping the toggle
// expands to show icon + label for all 7 destinations.
// Badge dots overlay on icons that have pending notifications,
// visible in BOTH collapsed and expanded states.
// =========================================================

private fun iconFor(destination: AppDestination): ImageVector = when (destination) {
    AppDestination.HOME -> Icons.Filled.Person
    AppDestination.SKILLS -> Icons.Filled.Star
    AppDestination.COMBAT -> Icons.Filled.Shield
    AppDestination.INVENTORY -> Icons.Filled.Inventory2
    AppDestination.MARKET -> Icons.Filled.Storefront
    AppDestination.GUILD -> Icons.Filled.Flag
    AppDestination.CHAT -> Icons.Filled.ChatBubble
    AppDestination.MODERATION -> Icons.Filled.AdminPanelSettings
}

@Composable
fun SideRail(
    currentDestination: AppDestination,
    onDestinationSelected: (AppDestination) -> Unit,
    badgedDestinations: Set<AppDestination> = emptySet(),
    destinations: List<AppDestination> = AppDestination.values().toList(),
    modifier: Modifier = Modifier
) {
    var expanded by remember { mutableStateOf(false) }

    Column(
        modifier = modifier
            .fillMaxHeight()
            .animateContentSize()
            .width(if (expanded) 140.dp else 64.dp)
            .padding(vertical = 12.dp),
        horizontalAlignment = Alignment.Start
    ) {
        // Toggle handle
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 8.dp, vertical = 8.dp)
                .clip(RoundedCornerShape(8.dp))
                .clickable { expanded = !expanded },
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = if (expanded) Icons.Filled.ChevronLeft else Icons.Filled.ChevronRight,
                contentDescription = if (expanded) "Collapse navigation" else "Expand navigation",
                tint = MaterialTheme.colorScheme.onSurface
            )
        }

        Spacer(modifier = Modifier.height(8.dp))

        destinations.forEach { destination ->
            RailItem(
                destination = destination,
                isSelected = destination == currentDestination,
                isExpanded = expanded,
                hasBadge = destination in badgedDestinations,
                onClick = { onDestinationSelected(destination) }
            )
        }
    }
}

@Composable
private fun RailItem(
    destination: AppDestination,
    isSelected: Boolean,
    isExpanded: Boolean,
    hasBadge: Boolean,
    onClick: () -> Unit
) {
    val backgroundColor = if (isSelected) MaterialTheme.colorScheme.primary.copy(alpha = 0.15f) else MaterialTheme.colorScheme.surface
    val contentColor = if (isSelected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 8.dp, vertical = 4.dp)
            .clip(RoundedCornerShape(10.dp))
            .background(backgroundColor)
            .clickable { onClick() }
            .padding(vertical = 12.dp, horizontal = 12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box {
            Icon(
                imageVector = iconFor(destination),
                contentDescription = destination.label,
                tint = contentColor
            )
            if (hasBadge) {
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .align(Alignment.TopEnd)
                        .clip(RoundedCornerShape(4.dp))
                        .background(MaterialTheme.colorScheme.error)
                )
            }
        }

        if (isExpanded) {
            Spacer(modifier = Modifier.width(12.dp))
            Text(
                text = destination.label,
                style = MaterialTheme.typography.bodyMedium,
                color = contentColor
            )
        }
    }
}
