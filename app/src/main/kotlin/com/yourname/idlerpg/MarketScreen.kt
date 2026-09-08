package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp

// =========================================================
// MARKET SCREENS
// Three separate screens (Browse, My Orders, Sell to Vendor),
// navigated via top buttons. Cosmetic-only price warning on
// order placement -- no backend validation tied to it.
// =========================================================

enum class MarketTab { BROWSE, MY_ORDERS, SELL_TO_VENDOR, BUY_FROM_VENDOR }

data class VendorBuyableItem(
    val itemId: String,
    val displayName: String,
    val pricePerUnit: Long
)

object VendorBuyCatalog {
    val items = listOf(
        VendorBuyableItem("flour", "Flour", 2L),
        VendorBuyableItem("vial_of_water", "Vial of Water", 2L),
        VendorBuyableItem("mining_cape", "Mining Cape", 10000L),
        VendorBuyableItem("woodcutting_cape", "Woodcutting Cape", 10000L),
        VendorBuyableItem("fishing_cape", "Fishing Cape", 10000L),
        VendorBuyableItem("farming_cape", "Farming Cape", 10000L),
        VendorBuyableItem("thieving_cape", "Thieving Cape", 10000L),
        VendorBuyableItem("smithing_cape", "Smithing Cape", 10000L),
        VendorBuyableItem("cooking_cape", "Cooking Cape", 10000L),
        VendorBuyableItem("crafting_cape", "Crafting Cape", 10000L),
        VendorBuyableItem("fletching_cape", "Fletching Cape", 10000L),
        VendorBuyableItem("alchemy_cape", "Alchemy Cape", 10000L),
        VendorBuyableItem("magic_cape", "Magic Cape", 10000L),
        VendorBuyableItem("attack_cape", "Attack Cape", 10000L),
        VendorBuyableItem("strength_cape", "Strength Cape", 10000L),
        VendorBuyableItem("defense_cape", "Defense Cape", 10000L),
        VendorBuyableItem("prayer_cape", "Prayer Cape", 10000L),
        VendorBuyableItem("archery_cape", "Archery Cape", 10000L)
    )
}

data class MarketListingSummary(
    val itemId: String,
    val displayName: String,
    val bestBuyPrice: Long?,   // highest current buy order, null if none
    val bestBuyQuantity: Int?, // total quantity available at bestBuyPrice
    val bestSellPrice: Long?,  // lowest current sell order, null if none
    val bestSellQuantity: Int? // total quantity available at bestSellPrice
)

data class MarketOrderSummary(
    val orderId: String,
    val itemId: String,
    val displayName: String,
    val pricePerUnit: Long,
    val remainingQuantity: Int
)

data class PriceHistoryRow(val pricePerUnit: Long, val quantity: Int, val timeAgo: String)

data class ItemOrderBookDetail(
    val itemId: String,
    val displayName: String,
    val bestBuyPrice: Long?,
    val bestSellPrice: Long?,
    val recentTrades: List<PriceHistoryRow>
)

@Composable
fun MarketScreen(
    currentTab: MarketTab,
    onTabSelected: (MarketTab) -> Unit,
    // Browse
    listings: List<MarketListingSummary>,
    showingBuyOrders: Boolean,
    onToggleBrowseMode: () -> Unit,
    onItemSelected: (String) -> Unit,
    // My Orders
    myBuyOrders: List<MarketOrderSummary>,
    mySellOrders: List<MarketOrderSummary>,
    onCancelOrder: (String) -> Unit,
    // Sell to Vendor
    vendorSellableItems: List<InventoryItemSummary>,
    onSellToVendor: (String, Int) -> Unit,
    // Buy from Vendor
    vendorBuyableItems: List<VendorBuyableItem>,
    onBuyFromVendor: (String, Int) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier.fillMaxSize().padding(20.dp)) {
        Text(text = "Market", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(12.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            MarketTabButton(
                label = "Browse",
                isSelected = currentTab == MarketTab.BROWSE,
                modifier = Modifier.weight(1f)
            ) { onTabSelected(MarketTab.BROWSE) }
            MarketTabButton(
                label = "Orders",
                isSelected = currentTab == MarketTab.MY_ORDERS,
                modifier = Modifier.weight(1f)
            ) { onTabSelected(MarketTab.MY_ORDERS) }
            MarketTabButton(
                label = "Vendor",
                isSelected = currentTab == MarketTab.SELL_TO_VENDOR,
                modifier = Modifier.weight(1f)
            ) { onTabSelected(MarketTab.SELL_TO_VENDOR) }
            MarketTabButton(
                label = "Buy",
                isSelected = currentTab == MarketTab.BUY_FROM_VENDOR,
                modifier = Modifier.weight(1f)
            ) { onTabSelected(MarketTab.BUY_FROM_VENDOR) }
        }

        Spacer(modifier = Modifier.height(16.dp))

        when (currentTab) {
            MarketTab.BROWSE -> BrowseTab(listings, showingBuyOrders, onToggleBrowseMode, onItemSelected)
            MarketTab.MY_ORDERS -> MyOrdersTab(myBuyOrders, mySellOrders, onCancelOrder)
            MarketTab.SELL_TO_VENDOR -> SellToVendorTab(vendorSellableItems, onSellToVendor)
            MarketTab.BUY_FROM_VENDOR -> BuyFromVendorTab(vendorBuyableItems, onBuyFromVendor)
        }
    }
}

@Composable
private fun MarketTabButton(
    label: String,
    isSelected: Boolean,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    val tabPadding = PaddingValues(horizontal = 4.dp, vertical = 8.dp)
    if (isSelected) {
        Button(onClick = onClick, modifier = modifier, contentPadding = tabPadding) {
            Text(
                text = label,
                style = MaterialTheme.typography.labelMedium,
                maxLines = 1,
                softWrap = false,
                overflow = TextOverflow.Ellipsis
            )
        }
    } else {
        OutlinedButton(onClick = onClick, modifier = modifier, contentPadding = tabPadding) {
            Text(
                text = label,
                style = MaterialTheme.typography.labelMedium,
                maxLines = 1,
                softWrap = false,
                overflow = TextOverflow.Ellipsis
            )
        }
    }
}

// ---------------- Browse ----------------

@Composable
private fun BrowseTab(
    listings: List<MarketListingSummary>,
    showingBuyOrders: Boolean,
    onToggleMode: () -> Unit,
    onItemSelected: (String) -> Unit
) {
    Column {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = if (showingBuyOrders) "Wanted (Buy Orders)" else "For Sale",
                style = MaterialTheme.typography.titleMedium
            )
            TextButton(onClick = onToggleMode) {
                Text(text = if (showingBuyOrders) "Show For Sale" else "Show Wanted")
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(listings) { listing ->
                ListingRow(listing, onClick = { onItemSelected(listing.itemId) })
            }
        }
    }
}

@Composable
private fun ListingRow(listing: MarketListingSummary, onClick: () -> Unit) {
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
        Text(text = listing.displayName, style = MaterialTheme.typography.titleMedium)
        Column(horizontalAlignment = Alignment.End) {
            Text(text = "Buy: " + (listing.bestBuyPrice?.let { "$it (x${listing.bestBuyQuantity ?: 0})" } ?: "—"), style = MaterialTheme.typography.labelSmall)
            Text(text = "Sell: " + (listing.bestSellPrice?.let { "$it (x${listing.bestSellQuantity ?: 0})" } ?: "—"), style = MaterialTheme.typography.labelSmall)
        }
    }
}

// ---------------- My Orders ----------------

@Composable
private fun MyOrdersTab(
    buyOrders: List<MarketOrderSummary>,
    sellOrders: List<MarketOrderSummary>,
    onCancel: (String) -> Unit
) {
    LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        item { Text(text = "Buy Orders", style = MaterialTheme.typography.titleMedium) }
        if (buyOrders.isEmpty()) {
            item { Text(text = "No open buy orders.", style = MaterialTheme.typography.bodyMedium) }
        }
        items(buyOrders) { order -> OrderRow(order, onCancel) }

        item { Spacer(modifier = Modifier.height(12.dp)); Text(text = "Sell Orders", style = MaterialTheme.typography.titleMedium) }
        if (sellOrders.isEmpty()) {
            item { Text(text = "No open sell orders.", style = MaterialTheme.typography.bodyMedium) }
        }
        items(sellOrders) { order -> OrderRow(order, onCancel) }
    }
}

@Composable
private fun OrderRow(order: MarketOrderSummary, onCancel: (String) -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(14.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text(text = order.displayName, style = MaterialTheme.typography.titleMedium)
            Text(
                text = order.remainingQuantity.toString() + " remaining @ " + order.pricePerUnit,
                style = MaterialTheme.typography.labelSmall
            )
        }
        TextButton(onClick = { onCancel(order.orderId) }) {
            Text(text = "Cancel")
        }
    }
}

// ---------------- Buy from Vendor ----------------

@Composable
private fun BuyFromVendorTab(items: List<VendorBuyableItem>, onBuy: (String, Int) -> Unit) {
    LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        if (items.isEmpty()) {
            item { Text(text = "The vendor has nothing for sale right now.", style = MaterialTheme.typography.bodyMedium) }
        }
        items(items) { item ->
            VendorBuyItemRow(item, onBuy)
        }
    }
}

@Composable
private fun VendorBuyItemRow(item: VendorBuyableItem, onBuy: (String, Int) -> Unit) {
    var quantityText by remember(item.itemId) { mutableStateOf("1") }
    val enteredQuantity = quantityText.toIntOrNull()
    val isValidQuantity = enteredQuantity != null && enteredQuantity > 0

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(14.dp)
    ) {
        Text(
            text = item.displayName,
            style = MaterialTheme.typography.titleMedium,
            maxLines = 1,
            softWrap = false,
            overflow = TextOverflow.Ellipsis
        )
        Text(
            text = item.pricePerUnit.toString() + " gold each (unlimited stock)",
            style = MaterialTheme.typography.labelSmall,
            maxLines = 1,
            softWrap = false,
            overflow = TextOverflow.Ellipsis
        )
        Spacer(modifier = Modifier.height(10.dp))
        Row(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
                value = quantityText,
                onValueChange = { new -> if (new.length <= 6 && new.all { it.isDigit() }) quantityText = new },
                modifier = Modifier.width(56.dp),
                singleLine = true,
                textStyle = MaterialTheme.typography.bodyMedium,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
            )
            Button(
                onClick = { enteredQuantity?.let { onBuy(item.itemId, it) } },
                enabled = isValidQuantity
            ) {
                Text("Buy")
            }
        }
    }
}

// ---------------- Sell to Vendor ----------------

@Composable
private fun SellToVendorTab(items: List<InventoryItemSummary>, onSell: (String, Int) -> Unit) {
    LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        if (items.isEmpty()) {
            item { Text(text = "You have nothing sellable right now.", style = MaterialTheme.typography.bodyMedium) }
        }
        items(items) { item ->
            VendorItemRow(item, onSell)
        }
    }
}

@Composable
private fun VendorItemRow(item: InventoryItemSummary, onSell: (String, Int) -> Unit) {
    var quantityText by remember(item.itemId, item.quantity) { mutableStateOf(item.quantity.toString()) }
    val enteredQuantity = quantityText.toIntOrNull()
    val isValidQuantity = enteredQuantity != null && enteredQuantity in 1..item.quantity

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(14.dp)
    ) {
        Text(
            text = item.displayName,
            style = MaterialTheme.typography.titleMedium,
            maxLines = 1,
            softWrap = false,
            overflow = TextOverflow.Ellipsis
        )
        Text(
            text = "x" + item.quantity + " — " + item.npcValuePerUnit + " each",
            style = MaterialTheme.typography.labelSmall,
            maxLines = 1,
            softWrap = false,
            overflow = TextOverflow.Ellipsis
        )
        Spacer(modifier = Modifier.height(10.dp))
        Row(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
                value = quantityText,
                onValueChange = { new -> if (new.length <= 6 && new.all { it.isDigit() }) quantityText = new },
                modifier = Modifier.width(56.dp),
                singleLine = true,
                textStyle = MaterialTheme.typography.bodyMedium,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
            )
            Button(
                onClick = { enteredQuantity?.let { onSell(item.itemId, it) } },
                enabled = isValidQuantity,
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp)
            ) {
                Text(text = "Sell", maxLines = 1, softWrap = false, overflow = TextOverflow.Ellipsis)
            }
        }
    }
}
