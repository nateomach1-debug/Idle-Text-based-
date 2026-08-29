package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp

// =========================================================
// ORDER BOOK / PLACE ORDER SCREEN
// Simple view: best buy + best sell price shown separately.
// Advanced view: recent trade list (price history).
// Cosmetic-only warning if entered price is far from best price
// -- purely advisory, does not block submission.
// =========================================================

enum class OrderSideUi { BUY, SELL }

@Composable
fun OrderBookScreen(
    detail: ItemOrderBookDetail,
    prefilledQuantity: Int? = null, // set when arriving from "Sell on Market" in Inventory
    onBack: () -> Unit,
    onPlaceOrder: (OrderSideUi, Int, Long) -> Unit,
    modifier: Modifier = Modifier
) {
    var showAdvanced by remember { mutableStateOf(false) }
    var side by remember { mutableStateOf(if (prefilledQuantity != null) OrderSideUi.SELL else OrderSideUi.BUY) }
    var quantityText by remember { mutableStateOf(prefilledQuantity?.toString() ?: "") }
    var priceText by remember { mutableStateOf("") }

    val referencePrice = if (side == OrderSideUi.BUY) detail.bestSellPrice else detail.bestBuyPrice
    val enteredPrice = priceText.toLongOrNull()
    val priceIsFarOff = referencePrice != null && enteredPrice != null &&
        (enteredPrice < referencePrice / 2 || enteredPrice > referencePrice * 2)

    Column(modifier = modifier.fillMaxSize().padding(20.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) {
                Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "Back", tint = MaterialTheme.colorScheme.onSurface)
            }
            Spacer(modifier = Modifier.width(4.dp))
            Text(text = detail.displayName, style = MaterialTheme.typography.headlineMedium)
        }

        Spacer(modifier = Modifier.height(16.dp))

        Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            PriceBlock("Best Buy", detail.bestBuyPrice)
            PriceBlock("Best Sell", detail.bestSellPrice)
        }

        Spacer(modifier = Modifier.height(8.dp))
        TextButton(onClick = { showAdvanced = !showAdvanced }) {
            Text(text = if (showAdvanced) "Hide price history" else "Show price history")
        }
        if (showAdvanced) {
            PriceHistoryList(detail.recentTrades)
        }

        Spacer(modifier = Modifier.height(24.dp))

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            SideToggle("Buy", side == OrderSideUi.BUY) { side = OrderSideUi.BUY }
            SideToggle("Sell", side == OrderSideUi.SELL) { side = OrderSideUi.SELL }
        }

        Spacer(modifier = Modifier.height(12.dp))

        OutlinedTextField(
            value = quantityText,
            onValueChange = { quantityText = it.filter { c -> c.isDigit() } },
            label = { Text("Quantity") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(8.dp))

        OutlinedTextField(
            value = priceText,
            onValueChange = { priceText = it.filter { c -> c.isDigit() } },
            label = { Text("Price per unit") },
            modifier = Modifier.fillMaxWidth()
        )

        if (priceIsFarOff) {
            Spacer(modifier = Modifier.height(6.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Filled.Warning,
                    contentDescription = "Warning",
                    tint = MaterialTheme.colorScheme.error,
                    modifier = Modifier.size(16.dp)
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = "This price is far from the current market rate.",
                    style = MaterialTheme.typography.labelSmall
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = {
                val qty = quantityText.toIntOrNull()
                val price = enteredPrice
                if (qty != null && qty > 0 && price != null && price > 0) {
                    onPlaceOrder(side, qty, price)
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(text = "Place " + (if (side == OrderSideUi.BUY) "Buy" else "Sell") + " Order")
        }
    }
}

@Composable
private fun PriceBlock(label: String, price: Long?) {
    Column {
        Text(text = label, style = MaterialTheme.typography.labelSmall)
        Text(text = price?.toString() ?: "—", style = MaterialTheme.typography.titleMedium)
    }
}

@Composable
private fun RowScope.SideToggle(label: String, isSelected: Boolean, onClick: () -> Unit) {
    if (isSelected) {
        Button(onClick = onClick, modifier = Modifier.weight(1f)) { Text(text = label) }
    } else {
        OutlinedButton(onClick = onClick, modifier = Modifier.weight(1f)) { Text(text = label) }
    }
}

@Composable
private fun PriceHistoryList(trades: List<PriceHistoryRow>) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(12.dp)
    ) {
        if (trades.isEmpty()) {
            Text(text = "No recent trades.", style = MaterialTheme.typography.bodyMedium)
        }
        LazyColumn(modifier = Modifier.heightIn(max = 180.dp)) {
            items(trades) { trade ->
                Row(
                    modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(text = trade.quantity.toString() + " @ " + trade.pricePerUnit, style = MaterialTheme.typography.labelSmall)
                    Text(text = trade.timeAgo, style = MaterialTheme.typography.labelSmall)
                }
            }
        }
    }
}
