package com.yourname.idlerpg.ui.screens

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.GridItemSpan
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.GridView
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.ViewList
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp

// =========================================================
// INVENTORY SCREEN
// List/Grid toggle (persistent), grouped by category, tap any
// item to open its quick-action popup. Equipment lives on a
// separate screen reached via button. Loadout also reachable
// via button, same pattern as Combat.
// =========================================================

enum class InventoryViewMode { LIST, GRID }

private const val PREFS_NAME = "idlerpg_prefs"
private const val KEY_INVENTORY_VIEW_MODE = "inventory_view_mode"

private fun loadSavedInventoryViewMode(context: Context): InventoryViewMode {
    val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    val saved = prefs.getString(KEY_INVENTORY_VIEW_MODE, InventoryViewMode.LIST.name)
    return runCatching { InventoryViewMode.valueOf(saved ?: InventoryViewMode.LIST.name) }
        .getOrDefault(InventoryViewMode.LIST)
}

private fun saveInventoryViewMode(context: Context, mode: InventoryViewMode) {
    val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    prefs.edit().putString(KEY_INVENTORY_VIEW_MODE, mode.name).apply()
}

enum class InventoryCategory { WEAPON, ARMOR, ACCESSORY, TOOL, MATERIAL, CONSUMABLE }

data class InventoryItemSummary(
    val itemId: String,
    val displayName: String,
    val category: InventoryCategory,
    val quantity: Int,
    val isEquippable: Boolean,
    val isConsumable: Boolean,
    val npcValuePerUnit: Long,
    val statsDescription: String? = null, // e.g. "ATK +5, ACC +10" -- only for equippable items
    val isBuryable: Boolean = false
)

@Composable
fun InventoryScreen(
    items: List<InventoryItemSummary>,
    onOpenEquipment: () -> Unit,
    onOpenLoadout: () -> Unit,
    onUseItem: (String) -> Unit,
    onSellOnMarket: (String) -> Unit,
    onEquipItem: (String) -> Unit,
    onBuryItem: (String) -> Unit,
    canEquip: (InventoryItemSummary) -> Pair<Boolean, String?>, // (canEquip, lockReasonIfNot)
    canBury: (InventoryItemSummary) -> Pair<Boolean, String?>, // (canBury, lockReasonIfNot)
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    var viewMode by remember { mutableStateOf(loadSavedInventoryViewMode(context)) }
    var selectedItem by remember { mutableStateOf<InventoryItemSummary?>(null) }

    val grouped = remember(items) {
        InventoryCategory.values().mapNotNull { category ->
            val categoryItems = items.filter { it.category == category }
            if (categoryItems.isEmpty()) null else category to categoryItems
        }
    }

    Column(modifier = modifier.fillMaxSize().padding(20.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(text = "Inventory", style = MaterialTheme.typography.headlineMedium)
            Row {
                IconButton(onClick = {
                    viewMode = InventoryViewMode.LIST
                    saveInventoryViewMode(context, InventoryViewMode.LIST)
                }) {
                    Icon(
                        imageVector = Icons.Filled.ViewList,
                        contentDescription = "List view",
                        tint = if (viewMode == InventoryViewMode.LIST) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface
                    )
                }
                IconButton(onClick = {
                    viewMode = InventoryViewMode.GRID
                    saveInventoryViewMode(context, InventoryViewMode.GRID)
                }) {
                    Icon(
                        imageVector = Icons.Filled.GridView,
                        contentDescription = "Grid view",
                        tint = if (viewMode == InventoryViewMode.GRID) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedButton(onClick = onOpenEquipment, modifier = Modifier.weight(1f)) {
                Text(text = "Equipment", maxLines = 1, softWrap = false, overflow = TextOverflow.Ellipsis)
            }
            OutlinedButton(onClick = onOpenLoadout, modifier = Modifier.weight(1f)) {
                Text(text = "Loadout", maxLines = 1, softWrap = false, overflow = TextOverflow.Ellipsis)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        when (viewMode) {
            InventoryViewMode.LIST -> InventoryListView(grouped) { selectedItem = it }
            InventoryViewMode.GRID -> InventoryGridView(grouped) { selectedItem = it }
        }
    }

    selectedItem?.let { item ->
        ItemActionSheet(
            item = item,
            canEquip = canEquip(item),
            canBury = canBury(item),
            onUse = { onUseItem(item.itemId); selectedItem = null },
            onSell = { onSellOnMarket(item.itemId); selectedItem = null },
            onEquip = { onEquipItem(item.itemId); selectedItem = null },
            onBury = { onBuryItem(item.itemId); selectedItem = null },
            onDismiss = { selectedItem = null }
        )
    }
}

@Composable
private fun InventoryListView(
    grouped: List<Pair<InventoryCategory, List<InventoryItemSummary>>>,
    onItemSelected: (InventoryItemSummary) -> Unit
) {
    LazyColumn(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        grouped.forEach { (category, categoryItems) ->
            item { CategoryHeader(category.name) }
            items(categoryItems) { invItem ->
                ItemListRow(invItem, onClick = { onItemSelected(invItem) })
            }
        }
    }
}

@Composable
private fun InventoryGridView(
    grouped: List<Pair<InventoryCategory, List<InventoryItemSummary>>>,
    onItemSelected: (InventoryItemSummary) -> Unit
) {
    LazyVerticalGrid(
        columns = GridCells.Fixed(3),
        verticalArrangement = Arrangement.spacedBy(10.dp),
        horizontalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        grouped.forEach { (category, categoryItems) ->
            item(span = { GridItemSpan(maxLineSpan) }) { CategoryHeader(category.name) }
            items(categoryItems) { invItem ->
                ItemGridTile(invItem, onClick = { onItemSelected(invItem) })
            }
        }
    }
}

@Composable
private fun CategoryHeader(title: String) {
    Text(
        text = title,
        style = MaterialTheme.typography.labelSmall,
        modifier = Modifier.padding(top = 12.dp, bottom = 4.dp)
    )
}

@Composable
private fun ItemListRow(item: InventoryItemSummary, onClick: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .clickable { onClick() }
            .padding(14.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(text = item.displayName, style = MaterialTheme.typography.titleMedium)
        Text(text = "x" + item.quantity, style = MaterialTheme.typography.labelSmall)
    }
}

@Composable
private fun ItemGridTile(item: InventoryItemSummary, onClick: () -> Unit) {
    Column(
        modifier = Modifier
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .clickable { onClick() }
            .padding(12.dp)
            .fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = item.displayName, style = MaterialTheme.typography.labelSmall)
        Spacer(modifier = Modifier.height(4.dp))
        Text(text = "x" + item.quantity, style = MaterialTheme.typography.titleMedium)
    }
}

@Composable
private fun ItemActionSheet(
    item: InventoryItemSummary,
    canEquip: Pair<Boolean, String?>,
    canBury: Pair<Boolean, String?>,
    onUse: () -> Unit,
    onSell: () -> Unit,
    onEquip: () -> Unit,
    onBury: () -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(text = item.displayName, style = MaterialTheme.typography.headlineMedium) },
        text = {
            Column {
                Text(text = "Quantity: " + item.quantity, style = MaterialTheme.typography.bodyMedium)

                val stackValue = item.npcValuePerUnit * item.quantity
                Text(
                    text = "NPC value: " + item.npcValuePerUnit + " each (" + stackValue + " for full stack)",
                    style = MaterialTheme.typography.bodyMedium
                )

                item.statsDescription?.let {
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(text = "Stats: " + it, style = MaterialTheme.typography.bodyMedium)
                }

                Spacer(modifier = Modifier.height(16.dp))

                if (item.isConsumable) {
                    Button(onClick = onUse, modifier = Modifier.fillMaxWidth()) {
                        Text(text = "Use")
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                }

                if (item.isEquippable) {
                    val (canEquipNow, lockReason) = canEquip
                    Button(
                        onClick = onEquip,
                        enabled = canEquipNow,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(text = "Equip")
                    }
                    if (!canEquipNow && lockReason != null) {
                        Spacer(modifier = Modifier.height(4.dp))
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = Icons.Filled.Lock,
                                contentDescription = "Locked",
                                tint = MaterialTheme.colorScheme.error,
                                modifier = Modifier.size(14.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(text = lockReason, style = MaterialTheme.typography.labelSmall)
                        }
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                }

                if (item.isBuryable) {
                    val (canBuryNow, buryLockReason) = canBury
                    Button(
                        onClick = onBury,
                        enabled = canBuryNow,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(text = "Bury")
                    }
                    if (!canBuryNow && buryLockReason != null) {
                        Spacer(modifier = Modifier.height(4.dp))
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = Icons.Filled.Lock,
                                contentDescription = "Locked",
                                tint = MaterialTheme.colorScheme.error,
                                modifier = Modifier.size(14.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(text = buryLockReason, style = MaterialTheme.typography.labelSmall)
                        }
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                }

                OutlinedButton(onClick = onSell, modifier = Modifier.fillMaxWidth()) {
                    Text(text = "Sell on Market")
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text(text = "Close")
            }
        }
    )
}
