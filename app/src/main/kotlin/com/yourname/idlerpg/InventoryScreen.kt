package com.yourname.idlerpg.ui.screens

import com.yourname.idlerpg.InventorySlotShop
import com.yourname.idlerpg.ServiceResult

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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.ui.unit.dp
import com.yourname.idlerpg.ActionCatalog
import com.yourname.idlerpg.ItemCatalog
import com.yourname.idlerpg.Recipe
import com.yourname.idlerpg.RecipeCatalog
import com.yourname.idlerpg.SkillType
import com.yourname.idlerpg.ZoneCatalog

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
    val isBuryable: Boolean = false,
    val lastAcquiredAtMillis: Long = 0L
)

enum class InventorySortMode(val label: String) {
    RECENT_DESC("Most Recent"),
    RECENT_ASC("Oldest First"),
    ALPHA_ASC("A to Z"),
    ALPHA_DESC("Z to A")
}

private const val KEY_INVENTORY_SORT_MODE = "inventory_sort_mode"

private fun loadSavedInventorySortMode(context: Context): InventorySortMode {
    val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    val saved = prefs.getString(KEY_INVENTORY_SORT_MODE, InventorySortMode.RECENT_DESC.name)
    return runCatching { InventorySortMode.valueOf(saved ?: InventorySortMode.RECENT_DESC.name) }
        .getOrDefault(InventorySortMode.RECENT_DESC)
}

private fun saveInventorySortMode(context: Context, mode: InventorySortMode) {
    val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    prefs.edit().putString(KEY_INVENTORY_SORT_MODE, mode.name).apply()
}

private fun sortedInventoryItems(items: List<InventoryItemSummary>, mode: InventorySortMode): List<InventoryItemSummary> = when (mode) {
    InventorySortMode.RECENT_DESC -> items.sortedByDescending { it.lastAcquiredAtMillis }
    InventorySortMode.RECENT_ASC -> items.sortedBy { it.lastAcquiredAtMillis }
    InventorySortMode.ALPHA_ASC -> items.sortedBy { it.displayName.lowercase() }
    InventorySortMode.ALPHA_DESC -> items.sortedByDescending { it.displayName.lowercase() }
}

@Composable
fun InventoryScreen(
    items: List<InventoryItemSummary>,
    capacity: Int = 100,
    coinPacks: Int = 0,
    gemPacks: Int = 0,
    coinBalance: Long = 0L,
    gemBalance: Long = 0L,
    slotError: String? = null,
    onBuyCoinSlots: () -> Unit = {},
    onBuyGemSlots: () -> Unit = {},
    onClearSlotError: () -> Unit = {},
    onOpenEquipment: () -> Unit,
    onOpenLoadout: () -> Unit,
    onUseItem: (String) -> Unit,
    onSellOnMarket: (String) -> Unit,
    onEquipItem: (String) -> ServiceResult<Unit>,
    onBuryItem: (String, Int) -> Unit,
    canEquip: (InventoryItemSummary) -> Pair<Boolean, String?>, // (canEquip, lockReasonIfNot)
    canBury: (InventoryItemSummary) -> Pair<Boolean, String?>, // (canBury, lockReasonIfNot)
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    var viewMode by remember { mutableStateOf(loadSavedInventoryViewMode(context)) }
    var sortMode by remember { mutableStateOf(loadSavedInventorySortMode(context)) }
    var sortMenuExpanded by remember { mutableStateOf(false) }
    var showSlotShop by remember { mutableStateOf(false) }
    var selectedItem by remember { mutableStateOf<InventoryItemSummary?>(null) }
    var showItemInfo by remember { mutableStateOf(false) }
    var equipRequirementError by remember { mutableStateOf<String?>(null) }
    
    val grouped = remember(items, sortMode) {
        InventoryCategory.values().mapNotNull { category ->
            val categoryItems = sortedInventoryItems(items.filter { it.category == category }, sortMode)
            if (categoryItems.isEmpty()) null else category to categoryItems
        }
    }

    Column(modifier = modifier.fillMaxSize().padding(20.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(text = "Inventory", style = MaterialTheme.typography.headlineMedium)
                Text(text = "Slots: " + items.size + " / " + capacity, style = MaterialTheme.typography.bodyMedium)
                TextButton(onClick = { showSlotShop = true }) { Text(text = "Buy slots") }
                if (showSlotShop) {
                    androidx.compose.material3.AlertDialog(
                        onDismissRequest = { showSlotShop = false; onClearSlotError() },
                        title = { Text(text = "Buy inventory slots") },
                        text = {
                            Column {
                                val coinPrice = InventorySlotShop.nextCoinPackPrice(coinPacks)
                                val gemPrice = InventorySlotShop.nextGemPackPrice(gemPacks)
                                Text(text = "Coins: " + coinBalance + "   Gems: " + gemBalance)
                                Spacer(modifier = Modifier.height(12.dp))
                                Text(text = "Coin slots: " + (coinPacks * InventorySlotShop.COIN_PACK_SLOTS) + " / " + InventorySlotShop.COIN_SLOTS_TOTAL)
                                if (coinPrice != null) {
                                    androidx.compose.material3.Button(onClick = onBuyCoinSlots, enabled = coinBalance >= coinPrice) {
                                        Text(text = "Buy " + InventorySlotShop.COIN_PACK_SLOTS + " slots - " + coinPrice + " coins")
                                    }
                                }
                                Spacer(modifier = Modifier.height(12.dp))
                                Text(text = "Premium slots: " + (gemPacks * InventorySlotShop.GEM_PACK_SLOTS) + " / " + InventorySlotShop.GEM_SLOTS_TOTAL)
                                if (gemPrice != null) {
                                    androidx.compose.material3.Button(onClick = onBuyGemSlots, enabled = gemBalance >= gemPrice) {
                                        Text(text = "Buy " + InventorySlotShop.GEM_PACK_SLOTS + " slots - " + gemPrice + " gems")
                                    }
                                }
                                if (slotError != null) {
                                    Spacer(modifier = Modifier.height(8.dp))
                                    Text(text = slotError, color = MaterialTheme.colorScheme.error)
                                }
                            }
                        },
                        confirmButton = {
                            TextButton(onClick = { showSlotShop = false; onClearSlotError() }) { Text(text = "Close") }
                        }
                    )
                }
            }
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

        Box {
            TextButton(onClick = { sortMenuExpanded = true }) {
                Text(text = "Sort: " + sortMode.label)
            }
            DropdownMenu(expanded = sortMenuExpanded, onDismissRequest = { sortMenuExpanded = false }) {
                InventorySortMode.values().forEach { option ->
                    DropdownMenuItem(
                        text = { Text(text = option.label) },
                        onClick = {
                            sortMode = option
                            saveInventorySortMode(context, option)
                            sortMenuExpanded = false
                        }
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

        
    
    if (!showItemInfo) {
        selectedItem?.let { item ->
            ItemActionSheet(
                item = item,
                canEquip = canEquip(item),
                canBury = canBury(item),
                onUse = {
                    onUseItem(item.itemId)
                    selectedItem = null
                },
                onSell = {
                    onSellOnMarket(item.itemId)
                    selectedItem = null
                },
                onShowInfo = {
                    showItemInfo = true
                },
                onEquip = {
                    val result = onEquipItem(item.itemId)
                    selectedItem = null

                    if (
                        result is ServiceResult.Failure &&
                        result.reason.contains("level", ignoreCase = true)
                    ) {
                        equipRequirementError = result.reason
                    }
                },
                onBury = { qty ->
                    onBuryItem(item.itemId, qty)
                    selectedItem = null
                },
                onDismiss = {
                    selectedItem = null
                }
            )
        }
    }

    if (showItemInfo) {
        val infoItem = selectedItem

        if (infoItem != null) {
            val info = remember(infoItem.itemId) {
                buildItemInfoDetails(infoItem.itemId)
            }

            AlertDialog(
                onDismissRequest = {
                    showItemInfo = false
                },
                title = {
                    Text(text = "${infoItem.displayName}: Info & Sources")
                },
                text = {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .heightIn(max = 440.dp)
                            .verticalScroll(rememberScrollState()),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "RECIPES USING THIS ITEM",
                            style = MaterialTheme.typography.titleSmall
                        )

                        if (info.recipesUsing.isEmpty()) {
                            Text("This item is not listed as an ingredient in any recipe.")
                        } else {
                            info.recipesUsing.forEach { recipe ->
                                Text(
                                    text = "• ${itemInfoName(recipe.outputItemId)} " +
                                        "(uses ${recipe.ingredients.firstOrNull {
                                            it.itemId == infoItem.itemId
                                        }?.quantity ?: 0})"
                                )
                                Text(
                                    text = "  Makes ${recipe.outputQuantity}; " +
                                        "${recipe.skillRequired.lowercase().replaceFirstChar {
                                            it.uppercase()
                                        }} level ${recipe.levelRequired}",
                                    style = MaterialTheme.typography.bodySmall
                                )
                            }
                        }

                        HorizontalDivider()

                        Text(
                            text = "RECIPES PRODUCING THIS ITEM",
                            style = MaterialTheme.typography.titleSmall
                        )

                        if (info.recipesProducing.isEmpty()) {
                            Text("No recipe producing this item is listed.")
                        } else {
                            info.recipesProducing.forEach { recipe ->
                                Text(
                                    text = "• Makes ${recipe.outputQuantity} " +
                                        itemInfoName(recipe.outputItemId)
                                )

                                Text(
                                    text = recipe.ingredients.joinToString(
                                        separator = ", "
                                    ) { ingredient ->
                                        "${itemInfoName(ingredient.itemId)} × ${ingredient.quantity}"
                                    }
                                )

                                Text(
                                    text = "Requires ${recipe.skillRequired.lowercase().replaceFirstChar {
                                        it.uppercase()
                                    }} level ${recipe.levelRequired}",
                                    style = MaterialTheme.typography.bodySmall
                                )
                            }
                        }

                        HorizontalDivider()

                        Text(
                            text = "ACQUISITION SOURCES",
                            style = MaterialTheme.typography.titleSmall
                        )

                        if (info.sources.isEmpty()) {
                            Text(
                                "No source is currently listed in the skilling, " +
                                    "combat-drop, vendor, or crafting catalogs."
                            )
                        } else {
                            info.sources.forEach { source ->
                                Text(text = "• $source")
                            }
                        }
                    }
                },
                confirmButton = {
                    TextButton(
                        onClick = {
                            showItemInfo = false
                        }
                    ) {
                        Text(text = "Close")
                    }
                }
            )
        } else {
            AlertDialog(
                onDismissRequest = {
                    showItemInfo = false
                },
                title = {
                    Text(text = "Item Info & Sources")
                },
                text = {
                    Text(text = "No item is selected.")
                },
                confirmButton = {
                    TextButton(
                        onClick = {
                            showItemInfo = false
                        }
                    ) {
                        Text(text = "Close")
                    }
                }
            )
        }
    }
                    equipRequirementError = result.reason
                }
            },
            onBury = { qty ->
                onBuryItem(item.itemId, qty)
                selectedItem = null
            },
            onDismiss = {
                selectedItem = null
            }
        )
    }

    if (showItemInfo) {
        AlertDialog(
            onDismissRequest = { showItemInfo = false },
            title = {
                Text(text = "Item Info & Sources")
            },
            text = {
                Text(
                    text = selectedItem?.displayName
                        ?: "No item selected"
                )
            },
            confirmButton = {
                TextButton(
                    onClick = { showItemInfo = false }
                ) {
                    Text(text = "Close")
                }
            }
        )
    }

    equipRequirementError?.let { errorMessage ->
        AlertDialog(
            onDismissRequest = { equipRequirementError = null },
            title = {
                Text(text = "Level Requirement Not Met")
            },
            text = {
                Text(text = errorMessage)
            },
            confirmButton = {
                TextButton(
                    onClick = { equipRequirementError = null }
                ) {
                    Text(text = "OK")
                }
            }
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
            item(span = { GridItemSpan(maxLineSpan) }) {
                CategoryHeader(category.name)
            }
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
private fun ItemListRow(
    item: InventoryItemSummary,
    onClick: () -> Unit
) {
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
private fun ItemGridTile(
    item: InventoryItemSummary,
    onClick: () -> Unit
) {
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
    onShowInfo: () -> Unit,
    onEquip: () -> Unit,
    onBury: (Int) -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text(
                text = item.displayName,
                style = MaterialTheme.typography.headlineMedium
            )
        },
        text = {
            Column {
                Text(
                    text = "Quantity: " + item.quantity,
                    style = MaterialTheme.typography.bodyMedium
                )

                val stackValue = item.npcValuePerUnit * item.quantity
                Text(
                    text = "NPC value: " + item.npcValuePerUnit +
                        " each (" + stackValue + " for full stack)",
                    style = MaterialTheme.typography.bodyMedium
                )

                item.statsDescription?.let {
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Stats: " + it,
                        style = MaterialTheme.typography.bodyMedium
                    )
                }

                Spacer(modifier = Modifier.height(8.dp))

                OutlinedButton(
                    onClick = onShowInfo,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(text = "Info & Sources")
                }

                Spacer(modifier = Modifier.height(16.dp))

                if (item.isConsumable) {
                    Button(
                        onClick = onUse,
                        modifier = Modifier.fillMaxWidth()
                    ) {
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
                            Text(
                                text = lockReason,
                                style = MaterialTheme.typography.labelSmall
                            )
                        }
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                }

                if (item.isBuryable) {
                    val (canBuryNow, buryLockReason) = canBury
                    var buryQuantity by remember(item.itemId) {
                        mutableStateOf(1)
                    }

                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        IconButton(
                            onClick = {
                                if (buryQuantity > 1) buryQuantity -= 1
                            },
                            enabled = canBuryNow
                        ) {
                            Text(text = "-", style = MaterialTheme.typography.titleLarge)
                        }

                        OutlinedTextField(
                            value = buryQuantity.toString(),
                            onValueChange = { newValue ->
                                val digitsOnly = newValue.filter { it.isDigit() }
                                buryQuantity = when {
                                    digitsOnly.isEmpty() -> 1
                                    else -> (digitsOnly.toIntOrNull() ?: 1)
                                        .coerceIn(1, item.quantity)
                                }
                            },
                            singleLine = true,
                            enabled = canBuryNow,
                            modifier = Modifier.width(90.dp)
                        )

                        IconButton(
                            onClick = {
                                if (buryQuantity < item.quantity) buryQuantity += 1
                            },
                            enabled = canBuryNow
                        ) {
                            Text(text = "+", style = MaterialTheme.typography.titleLarge)
                        }

                        TextButton(
                            onClick = { buryQuantity = item.quantity },
                            enabled = canBuryNow
                        ) {
                            Text(text = "Max")
                        }
                    }

                    Spacer(modifier = Modifier.height(4.dp))

                    Button(
                        onClick = { onBury(buryQuantity) },
                        enabled = canBuryNow,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(text = "Bury " + buryQuantity)
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
                            Text(
                                text = buryLockReason,
                                style = MaterialTheme.typography.labelSmall
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))
                }

                OutlinedButton(
                    onClick = onSell,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(text = "Sell on Market")
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text(text = "Close")

                
private data class ItemInfoDetails(
    val recipesUsing: List<Recipe>,
    val recipesProducing: List<Recipe>,
    val sources: List<String>
)

private fun itemInfoName(itemId: String): String {
    return ItemCatalog.find(itemId)?.name
        ?: itemId
            .split('_')
            .joinToString(" ") { word ->
                word.replaceFirstChar { it.uppercase() }
            }
}

private fun buildItemInfoDetails(itemId: String): ItemInfoDetails {
    val recipesUsing = RecipeCatalog.recipes.filter { recipe ->
        recipe.ingredients.any { ingredient ->
            ingredient.itemId == itemId
        }
    }

    val recipesProducing = RecipeCatalog.recipes.filter { recipe ->
        recipe.outputItemId == itemId
    }

    val sources = linkedSetOf<String>()

    // Skilling actions that directly produce this item.
    SkillType.values().forEach { skill ->
        ActionCatalog.allFor(skill)
            .filter { action -> action.itemId == itemId }
            .forEach { action ->
                sources.add(
                    "Skilling — ${action.displayName} " +
                        "(${skill.name.lowercase().replaceFirstChar {
                            it.uppercase()
                        }}, level ${action.levelRequired})"
                )
            }
    }

    // Crafting recipes that create the item.
    recipesProducing.forEach { recipe ->
        sources.add(
            "Crafting — ${recipe.skillRequired.lowercase().replaceFirstChar {
                it.uppercase()
            }} level ${recipe.levelRequired}; produces ${recipe.outputQuantity}"
        )
    }

    // Items sold by the in-game vendor.
    VendorBuyCatalog.items
        .filter { it.itemId == itemId }
        .forEach { vendorItem ->
            sources.add(
                "Vendor — ${vendorItem.displayName}, " +
                    "${vendorItem.pricePerUnit} coins each"
            )
        }

    // Items obtained from monster loot tables.
    ZoneCatalog.zones.forEach { zone ->
        zone.monsters.forEach { monster ->
            (monster.mainLootTable + monster.rareLootTable)
                .filter { loot -> loot.itemId == itemId }
                .forEach { loot ->
                    sources.add(
                        "Combat — ${monster.name} in ${zone.name}: " +
                            "${loot.dropChancePercent}% chance, " +
                            "${loot.minQty}–${loot.maxQty} per drop"
                    )
                }

            // Bones are granted separately from each monster's loot table.
            val guaranteedBoneType = when {
                monster.levelRequirement >= 60 -> "dragon_bones"
                monster.levelRequirement >= 20 -> "big_bones"
                monster.levelRequirement >= 15 -> "gem_bones"
                else -> "bone"
            }

            if (itemId == guaranteedBoneType) {
                sources.add(
                    "Combat — ${monster.name} in ${zone.name}: " +
                        "1 guaranteed bone per kill"
                )
            }

            // Each kill has a 15% chance of granting one randomly selected
            // elemental essence from the four essence types.
            if (
                itemId in setOf(
                    "fire_essence",
                    "earth_essence",
                    "water_essence",
                    "wind_essence"
                )
            ) {
                sources.add(
                    "Combat — any monster: approximately 3.75% chance " +
                        "per kill for this specific elemental essence"
                )
            }
        }
    }

    // A tradeable item may also be acquired from another player.
    val itemDefinition = ItemCatalog.find(itemId)
    if (itemDefinition?.isTradeable == true) {
        sources.add("Player market — can be purchased from another player")
    }

    return ItemInfoDetails(
        recipesUsing = recipesUsing,
        recipesProducing = recipesProducing,
        sources = sources.toList()
    )
}
            }
        }
    )
}

