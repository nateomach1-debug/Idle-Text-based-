package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp

// =========================================================
// MARKET SCREENS
// Three separate screens (Browse, My Orders, Sell to Vendor),
// navigated via top buttons. Cosmetic-only price warning on
// order placement -- no backend validation tied to it.
// =========================================================

enum class MarketTab { BROWSE, MY_ORDERS, SELL_TO_VENDOR }

data class MarketListingSummary(
    val itemId: String,
    val displayName: String,
    val bestBuyPrice: Long?,   // highest current buy order, null if none
    val bestSellPrice: Long?   // lowest current sell order, null if none
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
        }

        Spacer(modifier = Modifier.height(16.dp))

        when (currentTab) {
            MarketTab.BROWSE -> BrowseTab(listings, showingBuyOrders, onToggleBrowseMode, onItemSelected)
            MarketTab.MY_ORDERS -> MyOrdersTab(myBuyOrders, mySellOrders, onCancelOrder)
            MarketTab.SELL_TO_VENDOR -> SellToVendorTab(vendorSellableItems, onSellToVendor)
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
    if (isSelected) {
        Button(onClick = onClick, modifier = modifier) {
            Text(text = label, style = MaterialTheme.typography.labelMedium)
        }
    } else {
        OutlinedButton(onClick = onClick, modifier = modifier) {
            Text(text = label, style = MaterialTheme.typography.labelMedium)
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
            Text(text = "Buy: " + (listing.bestBuyPrice?.toString() ?: "—"), style = MaterialTheme.typography.labelSmall)
            Text(text = "Sell: " + (listing.bestSellPrice?.toString() ?: "—"), style = MaterialTheme.typography.labelSmall)
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

// ---------------- Sell to Vendor ----------------

@Composable
private fun SellToVendorTab(items: List<InventoryItemSummary>, onSell: (String, Int) -> Unit) {
    LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        items(items) { item ->
            VendorItemRow(item, onSell)
        }
    }
}

@Composable
private fun VendorItemRow(item: InventoryItemSummary, onSell: (String, Int) -> Unit) {
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
            Text(text = item.displayName, style = MaterialTheme.typography.titleMedium)
            Text(
                text = "x" + item.quantity + " — " + item.npcValuePerUnit + " each",
                style = MaterialTheme.typography.labelSmall
            )
        }
        Button(onClick = { onSell(item.itemId, item.quantity) }) {
            Text(text = "Sell All")
        }
    }
}
