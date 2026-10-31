
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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
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
import com.yourname.idlerpg.ActionCatalog
import com.yourname.idlerpg.InventorySlotShop
import com.yourname.idlerpg.ItemCatalog
import com.yourname.idlerpg.Recipe
import com.yourname.idlerpg.RecipeCatalog
import com.yourname.idlerpg.ServiceResult
import com.yourname.idlerpg.SkillType
import com.yourname.idlerpg.ZoneCatalog
import com.yourname.idlerpg.ConsumableType

enum class InventoryViewMode { LIST, GRID }

enum class InventoryCategory {
    WEAPON, ARMOR, ACCESSORY, TOOL, AMMO, MATERIAL, CONSUMABLE
}

enum class InventorySortMode(val label: String) {
    RECENT_DESC("Most Recent"),
    RECENT_ASC("Oldest First"),
    ALPHA_ASC("A to Z"),
    ALPHA_DESC("Z to A")
}

data class InventoryItemSummary(
    val itemId: String,
    val displayName: String,
    val category: InventoryCategory,
    val quantity: Int,
    val isEquippable: Boolean,
    val isConsumable: Boolean,
    val npcValuePerUnit: Long,
    val statsDescription: String? = null,
    val isBuryable: Boolean = false,
    val lastAcquiredAtMillis: Long = 0L
)

private const val PREFS_NAME = "idlerpg_prefs"
private const val KEY_INVENTORY_VIEW_MODE = "inventory_view_mode"
private const val KEY_INVENTORY_SORT_MODE = "inventory_sort_mode"

private fun loadSavedInventoryViewMode(context: Context): InventoryViewMode {
    val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    val saved = prefs.getString(KEY_INVENTORY_VIEW_MODE, InventoryViewMode.LIST.name)
    return runCatching {
        InventoryViewMode.valueOf(saved ?: InventoryViewMode.LIST.name)
    }.getOrDefault(InventoryViewMode.LIST)
}

private fun saveInventoryViewMode(context: Context, mode: InventoryViewMode) {
    context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        .edit()
        .putString(KEY_INVENTORY_VIEW_MODE, mode.name)
        .apply()
}

private fun loadSavedInventorySortMode(context: Context): InventorySortMode {
    val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    val saved = prefs.getString(KEY_INVENTORY_SORT_MODE, InventorySortMode.RECENT_DESC.name)
    return runCatching {
        InventorySortMode.valueOf(saved ?: InventorySortMode.RECENT_DESC.name)
    }.getOrDefault(InventorySortMode.RECENT_DESC)
}

private fun saveInventorySortMode(context: Context, mode: InventorySortMode) {
    context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        .edit()
        .putString(KEY_INVENTORY_SORT_MODE, mode.name)
        .apply()
}

private fun sortedInventoryItems(
    items: List<InventoryItemSummary>,
    mode: InventorySortMode
): List<InventoryItemSummary> = when (mode) {
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
    canEquip: (InventoryItemSummary) -> Pair<Boolean, String?>,
    canBury: (InventoryItemSummary) -> Pair<Boolean, String?>,
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
            val categoryItems = sortedInventoryItems(
                items.filter { it.category == category },
                sortMode
            )
            if (categoryItems.isEmpty()) null else category to categoryItems
        }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(20.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text("Inventory", style = MaterialTheme.typography.headlineMedium)
                Text(
                    "Slots: ${items.size} / $capacity",
                    style = MaterialTheme.typography.bodyMedium
                )
                TextButton(onClick = { showSlotShop = true }) {
                    Text("Buy slots")
                }
            }

            Row {
                IconButton(
                    onClick = {
                        viewMode = InventoryViewMode.LIST
                        saveInventoryViewMode(context, viewMode)
                    }
                ) {
                    Icon(
                        Icons.Filled.ViewList,
                        contentDescription = "List view",
                        tint = if (viewMode == InventoryViewMode.LIST)
                            MaterialTheme.colorScheme.primary
                        else MaterialTheme.colorScheme.onSurface
                    )
                }
                IconButton(
                    onClick = {
                        viewMode = InventoryViewMode.GRID
                        saveInventoryViewMode(context, viewMode)
                    }
                ) {
                    Icon(
                        Icons.Filled.GridView,
                        contentDescription = "Grid view",
                        tint = if (viewMode == InventoryViewMode.GRID)
                            MaterialTheme.colorScheme.primary
                        else MaterialTheme.colorScheme.onSurface
                    )
                }
            }
        }

        Box {
            TextButton(onClick = { sortMenuExpanded = true }) {
                Text("Sort: ${sortMode.label}")
            }
            DropdownMenu(
                expanded = sortMenuExpanded,
                onDismissRequest = { sortMenuExpanded = false }
            ) {
                InventorySortMode.values().forEach { option ->
                    DropdownMenuItem(
                        text = { Text(option.label) },
                        onClick = {
                            sortMode = option
                            saveInventorySortMode(context, option)
                            sortMenuExpanded = false
                        }
                    )
                }
            }
        }

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedButton(
                onClick = onOpenEquipment,
                modifier = Modifier.weight(1f)
            ) {
                Text("Equipment", maxLines = 1, softWrap = false,
                    overflow = TextOverflow.Ellipsis)
            }
            OutlinedButton(
                onClick = onOpenLoadout,
                modifier = Modifier.weight(1f)
            ) {
                Text("Loadout", maxLines = 1, softWrap = false,
                    overflow = TextOverflow.Ellipsis)
            }
        }

        Spacer(Modifier.height(12.dp))

        when (viewMode) {
            InventoryViewMode.LIST ->
                InventoryListView(grouped) { selectedItem = it }
            InventoryViewMode.GRID ->
                InventoryGridView(grouped) { selectedItem = it }
        }
    }

    if (showSlotShop) {
        AlertDialog(
            onDismissRequest = {
                showSlotShop = false
                onClearSlotError()
            },
            title = { Text("Buy inventory slots") },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Coins: $coinBalance   Gems: $gemBalance")

                    val coinPrice = InventorySlotShop.nextCoinPackPrice(coinPacks)
                    val gemPrice = InventorySlotShop.nextGemPackPrice(gemPacks)

                    Text(
                        "Coin slots: ${coinPacks * InventorySlotShop.COIN_PACK_SLOTS} / " +
                            InventorySlotShop.COIN_SLOTS_TOTAL
                    )
                    if (coinPrice != null) {
                        Button(
                            onClick = onBuyCoinSlots,
                            enabled = coinBalance >= coinPrice,
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(
                                "Buy ${InventorySlotShop.COIN_PACK_SLOTS} slots - " +
                                    "$coinPrice coins"
                            )
                        }
                    } else {
                        Text("All coin slot packs purchased.")
                    }

                    Text(
                        "Premium slots: ${gemPacks * InventorySlotShop.GEM_PACK_SLOTS} / " +
                            InventorySlotShop.GEM_SLOTS_TOTAL
                    )
                    if (gemPrice != null) {
                        Button(
                            onClick = onBuyGemSlots,
                            enabled = gemBalance >= gemPrice,
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(
                                "Buy ${InventorySlotShop.GEM_PACK_SLOTS} slots - " +
                                    "$gemPrice gems"
                            )
                        }
                    } else {
                        Text("All premium slot packs purchased.")
                    }

                    if (slotError != null) {
                        Text(slotError, color = MaterialTheme.colorScheme.error)
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = {
                    showSlotShop = false
                    onClearSlotError()
                }) {
                    Text("Close")
                }
            }
        )
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
                onShowInfo = { showItemInfo = true },
                onEquip = {
                    val result = onEquipItem(item.itemId)
                    selectedItem = null
                    if (result is ServiceResult.Failure &&
                        result.reason.contains("level", ignoreCase = true)
                    ) {
                        equipRequirementError = result.reason
                    }
                },
                onBury = { quantity ->
                    onBuryItem(item.itemId, quantity)
                    selectedItem = null
                },
                onDismiss = { selectedItem = null }
            )
        }
    }

    if (showItemInfo) {
        selectedItem?.let { item ->
            val info = remember(item.itemId) {
                buildItemInfoDetails(item.itemId)
            }

            AlertDialog(
                onDismissRequest = { showItemInfo = false },
                title = { Text("${item.displayName}: Info & Sources") },
                text = {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .heightIn(max = 440.dp)
                            .verticalScroll(rememberScrollState()),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        if (info.effects.isNotEmpty()) {
                            Text(
                                "EFFECTS",
                                style = MaterialTheme.typography.titleSmall
                            )

                            info.effects.forEach { effect ->
                                Text("• $effect")
                            }

                            HorizontalDivider()
                        }

                        Text(
                            "RECIPES USING THIS ITEM",
                            style = MaterialTheme.typography.titleSmall
                        )

                        if (info.recipesUsing.isEmpty()) {
                            Text("This item is not listed as an ingredient in any recipe.")
                        } else {
                            info.recipesUsing.forEach { recipe ->
                                val usedQuantity = recipe.ingredients
                                    .filter { it.itemId == item.itemId }
                                    .sumOf { it.quantity }

                                Text("• ${itemInfoName(recipe.outputItemId)}")
                                Text(
                                    "Uses $usedQuantity; makes ${recipe.outputQuantity}. " +
                                        "${formatSkillName(recipe.skillRequired)} level " +
                                        "${recipe.levelRequired}",
                                    style = MaterialTheme.typography.bodySmall
                                )
                            }
                        }

                        HorizontalDivider()

                        Text(
                            "RECIPES PRODUCING THIS ITEM",
                            style = MaterialTheme.typography.titleSmall
                        )

                        if (info.recipesProducing.isEmpty()) {
                            Text("No recipe producing this item is listed.")
                        } else {
                            info.recipesProducing.forEach { recipe ->
                                Text(
                                    "• Makes ${recipe.outputQuantity} " +
                                        itemInfoName(recipe.outputItemId)
                                )
                                Text(
                                    recipe.ingredients.joinToString(", ") { ingredient ->
                                        "${itemInfoName(ingredient.itemId)} × ${ingredient.quantity}"
                                    }
                                )
                                Text(
                                    "Requires ${formatSkillName(recipe.skillRequired)} " +
                                        "level ${recipe.levelRequired}",
                                    style = MaterialTheme.typography.bodySmall
                                )
                            }
                        }

                        HorizontalDivider()

                        Text(
                            "ACQUISITION SOURCES",
                            style = MaterialTheme.typography.titleSmall
                        )

                        if (info.sources.isEmpty()) {
                            Text(
                                "No source is currently listed in the skilling, combat, " +
                                    "vendor, or crafting catalogs."
                            )
                        } else {
                            info.sources.forEach { source ->
                                Text("• $source")
                            }
                        }
                    }
                },
                confirmButton = {
                    TextButton(onClick = { showItemInfo = false }) {
                        Text("Close")
                    }
                }
            )
        } ?: run {
            AlertDialog(
                onDismissRequest = { showItemInfo = false },
                title = { Text("Item Info & Sources") },
                text = { Text("No item is selected.") },
                confirmButton = {
                    TextButton(onClick = { showItemInfo = false }) {
                        Text("Close")
                    }
                }
            )
        }
    }

    equipRequirementError?.let { message ->
        AlertDialog(
            onDismissRequest = { equipRequirementError = null },
            title = { Text("Level Requirement Not Met") },
            text = { Text(message) },
            confirmButton = {
                TextButton(onClick = { equipRequirementError = null }) {
                    Text("OK")
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
            items(categoryItems) { item ->
                ItemListRow(item) { onItemSelected(item) }
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
            items(categoryItems) { item ->
                ItemGridTile(item) { onItemSelected(item) }
            }
        }
    }
}

@Composable
private fun CategoryHeader(title: String) {
    Text(
        title,
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
            .clickable(onClick = onClick)
            .padding(14.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(item.displayName, style = MaterialTheme.typography.titleMedium)
        Text("x${item.quantity}", style = MaterialTheme.typography.labelSmall)
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
            .clickable(onClick = onClick)
            .padding(12.dp)
            .fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(item.displayName, style = MaterialTheme.typography.labelSmall)
        Spacer(Modifier.height(4.dp))
        Text("x${item.quantity}", style = MaterialTheme.typography.titleMedium)
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
            Text(item.displayName, style = MaterialTheme.typography.headlineMedium)
        },
        text = {
            Column {
                Text("Quantity: ${item.quantity}")
                Text(
                    "NPC value: ${item.npcValuePerUnit} each " +
                        "(${item.npcValuePerUnit * item.quantity} for full stack)"
                )

                item.statsDescription?.let {
                    Spacer(Modifier.height(8.dp))
                    Text("Stats: $it")
                }

                Spacer(Modifier.height(8.dp))

                OutlinedButton(
                    onClick = onShowInfo,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Info & Sources")
                }

                Spacer(Modifier.height(8.dp))

                if (item.isConsumable) {
                    Button(
                        onClick = onUse,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Use")
                    }
                    Spacer(Modifier.height(8.dp))
                }

                if (item.isEquippable) {
                    val (canEquipNow, lockReason) = canEquip
                    Button(
                        onClick = onEquip,
                        enabled = canEquipNow,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Equip")
                    }

                    if (!canEquipNow && lockReason != null) {
                        LockReason(lockReason)
                    }
                    Spacer(Modifier.height(8.dp))
                }

                if (item.isBuryable) {
                    val (canBuryNow, lockReason) = canBury
                    var buryQuantity by remember(item.itemId) {
                        mutableIntStateOf(1)
                    }

                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        IconButton(
                            onClick = { buryQuantity = (buryQuantity - 1).coerceAtLeast(1) },
                            enabled = canBuryNow
                        ) {
                            Text("−")
                        }

                        OutlinedTextField(
                            value = buryQuantity.toString(),
                            onValueChange = { value ->
                                buryQuantity = (value.toIntOrNull() ?: 1)
                                    .coerceIn(1, item.quantity)
                            },
                            singleLine = true,
                            enabled = canBuryNow,
                            modifier = Modifier.width(76.dp)
                        )

                        IconButton(
                            onClick = {
                                buryQuantity = (buryQuantity + 1).coerceAtMost(item.quantity)
                            },
                            enabled = canBuryNow
                        ) {
                            Text("+")
                        }

                        TextButton(
                            onClick = { buryQuantity = item.quantity },
                            enabled = canBuryNow
                        ) {
                            Text("Max")
                        }
                    }

                    Button(
                        onClick = { onBury(buryQuantity) },
                        enabled = canBuryNow,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Bury $buryQuantity")
                    }

                    if (!canBuryNow && lockReason != null) {
                        LockReason(lockReason)
                    }
                    Spacer(Modifier.height(8.dp))
                }

                OutlinedButton(
                    onClick = onSell,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Sell on Market")
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text("Close")
            }
        }
    )
}

@Composable
private fun LockReason(reason: String) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Icon(
            imageVector = Icons.Filled.Lock,
            contentDescription = "Locked",
            tint = MaterialTheme.colorScheme.error,
            modifier = Modifier.size(14.dp)
        )
        Spacer(Modifier.width(4.dp))
        Text(reason, style = MaterialTheme.typography.labelSmall)
    }
}

private data class ItemInfoDetails(
    val recipesUsing: List<Recipe>,
    val recipesProducing: List<Recipe>,
    val effects: List<String>,
    val sources: List<String>
)

private fun itemInfoName(itemId: String): String {
    return ItemCatalog.find(itemId)?.name
        ?: itemId.split('_').joinToString(" ") { word ->
            word.replaceFirstChar { it.uppercase() }
        }
}

private fun formatSkillName(skill: String): String {
    return skill.lowercase().replaceFirstChar { it.uppercase() }
}

private fun buildConsumableEffects(itemId: String): List<String> {
    val definition = ItemCatalog.find(itemId) ?: return emptyList()

    return when (definition.consumableType) {
        ConsumableType.FOOD -> {
            listOf(
                "Restores ${definition.healAmount ?: 0} HP"
            )
        }

        ConsumableType.POTION -> {
            PotionEffectCatalog.effectsFor(itemId)
        }

        null -> emptyList()
    }
}


private fun buildItemInfoDetails(itemId: String): ItemInfoDetails {
    val recipesUsing = RecipeCatalog.recipes.filter { recipe ->
        recipe.ingredients.any { it.itemId == itemId }
    }

    val recipesProducing = RecipeCatalog.recipes.filter { recipe ->
        recipe.outputItemId == itemId
    }

    val effects = buildConsumableEffects(itemId)

    val sources = linkedSetOf<String>()

    // Items directly gathered or obtained through skilling actions.
    // Crafted items are already covered by their recipe source below.
    if (recipesProducing.isEmpty()) {
        SkillType.values().forEach { skill ->
            ActionCatalog.allFor(skill)
                .filter { it.itemId == itemId }
                .forEach { action ->
                    sources.add(
                        "Skilling — ${action.displayName} " +
                            "(${formatSkillName(skill.name)}, level ${action.levelRequired})"
                    )
                }
        }
    }

    // Recipes that create this item.
    recipesProducing.forEach { recipe ->
        sources.add(
            "Crafting — ${formatSkillName(recipe.skillRequired)} level " +
                "${recipe.levelRequired}; produces ${recipe.outputQuantity}"
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

    // Monster loot tables and the guaranteed bone drop.
    ZoneCatalog.zones.forEach { zone ->
        zone.monsters.forEach { monster ->
            (monster.mainLootTable + monster.rareLootTable)
                .filter { it.itemId == itemId }
                .forEach { loot ->
                    sources.add(
                        "Combat — ${monster.name} (${zone.name}): " +
                            "${loot.dropChancePercent}% drop chance, " +
                            "${loot.minQty}–${loot.maxQty} per drop"
                    )
                }

            val boneType = when {
                monster.levelRequirement >= 60 -> "dragon_bones"
                monster.levelRequirement >= 20 -> "big_bones"
                monster.levelRequirement >= 15 -> "gem_bones"
                else -> "bone"
            }

            if (itemId == boneType) {
                sources.add(
                    "Combat — ${monster.name} (${zone.name}): " +
                        "1 guaranteed ${itemInfoName(boneType)} per kill"
                )
            }
        }
    }

    // Combat grants one random elemental essence on a 15% roll.
    val essenceTypes = setOf(
        "fire_essence",
        "earth_essence",
        "water_essence",
        "wind_essence"
    )
    if (itemId in essenceTypes) {
        sources.add(
            "Combat — any monster: 15% chance to receive one random elemental " +
                "essence (approximately 3.75% for this type if all four are equally likely)"
        )
    }

    return ItemInfoDetails(
        recipesUsing = recipesUsing,
        recipesProducing = recipesProducing,
        effects = effects,
        sources = sources.toList()
    )
}
