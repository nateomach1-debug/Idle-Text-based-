package com.yourname.idlerpg

import java.time.Instant
import java.util.UUID

// =========================================================
// PLAYER ECONOMY ACCOUNT
// =========================================================

class PlayerEconomyAccount(
    val characterId: String,
    val accountId: String,
    var isMainCharacter: Boolean,
    var currencyBalance: Long,
    val inventory: MutableMap<String, Int> = mutableMapOf()
) {
    fun addItem(itemId: String, qty: Int) {
        inventory[itemId] = (inventory[itemId] ?: 0) + qty
    }

    fun removeItem(itemId: String, qty: Int): Boolean {
        val current = inventory[itemId] ?: 0
        if (current < qty) return false
        inventory[itemId] = current - qty
        return true
    }
}

// =========================================================
// ORDERS
// =========================================================

enum class OrderSide { BUY, SELL }
enum class OrderStatus { OPEN, PARTIALLY_FILLED, FILLED, CANCELLED }

data class MarketOrder(
    val id: String = UUID.randomUUID().toString(),
    val characterId: String,
    val itemId: String,
    val side: OrderSide,
    val pricePerUnit: Long,
    val originalQuantity: Int,
    var remainingQuantity: Int,
    var status: OrderStatus = OrderStatus.OPEN,
    val createdAt: Instant = Instant.now()
)

// =========================================================
// TRADE RECORDS
// =========================================================

data class PriceHistoryEntry(
    val itemId: String,
    val pricePerUnit: Long,
    val quantity: Int,
    val executedAt: Instant
)

data class DevTradeRecord(
    val tradeId: String = UUID.randomUUID().toString(),
    val itemId: String,
    val pricePerUnit: Long,
    val quantity: Int,
    val buyerCharacterId: String,
    val buyerAccountId: String,
    val sellerCharacterId: String,
    val sellerAccountId: String,
    val taxCollected: Long,
    val executedAt: Instant = Instant.now()
)

// =========================================================
// DEVELOPER-ONLY ECONOMY MONITORING
// =========================================================

class EconomyMonitoringService {
    private val devTradeLog: MutableList<DevTradeRecord> = mutableListOf()
    private var totalTaxSunk: Long = 0
    private var totalVendorPayoutFaucet: Long = 0

    internal fun recordTrade(record: DevTradeRecord) {
        devTradeLog.add(record)
        totalTaxSunk += record.taxCollected
    }

    internal fun recordVendorPayout(amount: Long) {
        totalVendorPayoutFaucet += amount
    }

    fun allTradesForCharacter(characterId: String): List<DevTradeRecord> =
        devTradeLog.filter { it.buyerCharacterId == characterId || it.sellerCharacterId == characterId }

    fun tradesBetween(characterIdA: String, characterIdB: String): List<DevTradeRecord> =
        devTradeLog.filter {
            (it.buyerCharacterId == characterIdA && it.sellerCharacterId == characterIdB) ||
            (it.buyerCharacterId == characterIdB && it.sellerCharacterId == characterIdA)
        }

    fun economyHealthSnapshot(): String {
        return "Total tax sunk: " + totalTaxSunk + " | Total vendor payouts (faucet): " + totalVendorPayoutFaucet +
            " | Net economy effect: " + (totalVendorPayoutFaucet - totalTaxSunk)
    }

    fun fullTradeLog(): List<DevTradeRecord> = devTradeLog.toList()
}

// =========================================================
// MARKET SERVICE
// (ServiceResult now comes from SharedTypes.kt. Item validation
//  now uses the shared ItemCatalog instead of a separate MarketItem list.)
// =========================================================

class MarketService(private val monitoring: EconomyMonitoringService) {

    private val accounts: MutableMap<String, PlayerEconomyAccount> = mutableMapOf()
    private val buyOrders: MutableList<MarketOrder> = mutableListOf()
    private val sellOrders: MutableList<MarketOrder> = mutableListOf()
    private val priceHistory: MutableList<PriceHistoryEntry> = mutableListOf()

    private val taxRatePercent: Double = 10.0
    private val vendorPayoutPercent: Double = 40.0

    fun registerAccount(account: PlayerEconomyAccount) {
        accounts[account.characterId] = account
    }

    fun accountFor(characterId: String): PlayerEconomyAccount? = accounts[characterId]

    private fun requireMainCharacter(characterId: String): ServiceResult<PlayerEconomyAccount>? {
        val account = accounts[characterId] ?: return ServiceResult.Failure("Character not registered.")
        if (!account.isMainCharacter) {
            return ServiceResult.Failure("Only the account's Main character can access the market.")
        }
        return null
    }

    // ---------------- Placing orders ----------------

    fun placeBuyOrder(characterId: String, itemId: String, quantity: Int, pricePerUnit: Long): ServiceResult<MarketOrder> {
        requireMainCharacter(characterId)?.let { return it as ServiceResult.Failure }
        val account = accounts.getValue(characterId)

        if (quantity <= 0) return ServiceResult.Failure("Quantity must be positive.")
        if (pricePerUnit <= 0) return ServiceResult.Failure("Price must be positive.")
        if (ItemCatalog.find(itemId) == null) return ServiceResult.Failure("Unknown item.")

        val totalCost = pricePerUnit * quantity
        if (account.currencyBalance < totalCost) {
            return ServiceResult.Failure("Insufficient currency to escrow this order.")
        }

        account.currencyBalance -= totalCost

        val order = MarketOrder(
            characterId = characterId,
            itemId = itemId,
            side = OrderSide.BUY,
            pricePerUnit = pricePerUnit,
            originalQuantity = quantity,
            remainingQuantity = quantity
        )
        buyOrders.add(order)
        matchOrders(itemId)
        return ServiceResult.Success(order)
    }

    fun placeSellOrder(characterId: String, itemId: String, quantity: Int, pricePerUnit: Long): ServiceResult<MarketOrder> {
        requireMainCharacter(characterId)?.let { return it as ServiceResult.Failure }
        val account = accounts.getValue(characterId)

        if (quantity <= 0) return ServiceResult.Failure("Quantity must be positive.")
        if (pricePerUnit <= 0) return ServiceResult.Failure("Price must be positive.")
        if (ItemCatalog.find(itemId) == null) return ServiceResult.Failure("Unknown item.")

        if (!account.removeItem(itemId, quantity)) {
            return ServiceResult.Failure("Insufficient item quantity to escrow this order.")
        }

        val order = MarketOrder(
            characterId = characterId,
            itemId = itemId,
            side = OrderSide.SELL,
            pricePerUnit = pricePerUnit,
            originalQuantity = quantity,
            remainingQuantity = quantity
        )
        sellOrders.add(order)
        matchOrders(itemId)
        return ServiceResult.Success(order)
    }

    // ---------------- Matching engine ----------------

    private fun matchOrders(itemId: String) {
        var matchFound = true
        while (matchFound) {
            matchFound = false

            val bestBuy = buyOrders
                .filter { it.itemId == itemId && it.remainingQuantity > 0 }
                .sortedWith(compareByDescending<MarketOrder> { it.pricePerUnit }.thenBy { it.createdAt })
                .firstOrNull() ?: break

            val bestSell = sellOrders
                .filter { it.itemId == itemId && it.remainingQuantity > 0 }
                .sortedWith(compareBy<MarketOrder> { it.pricePerUnit }.thenBy { it.createdAt })
                .firstOrNull() ?: break

            if (bestBuy.pricePerUnit < bestSell.pricePerUnit) break

            val executionPrice = if (bestSell.createdAt.isBefore(bestBuy.createdAt)) bestSell.pricePerUnit else bestBuy.pricePerUnit
            val tradedQuantity = minOf(bestBuy.remainingQuantity, bestSell.remainingQuantity)

            executeTrade(bestBuy, bestSell, executionPrice, tradedQuantity)
            matchFound = true
        }
    }

    private fun executeTrade(buyOrder: MarketOrder, sellOrder: MarketOrder, pricePerUnit: Long, quantity: Int) {
        val buyerAccount = accounts.getValue(buyOrder.characterId)
        val sellerAccount = accounts.getValue(sellOrder.characterId)

        val grossAmount = pricePerUnit * quantity
        val tax = ((grossAmount * taxRatePercent) / 100.0).toLong()
        val sellerProceeds = grossAmount - tax

        val buyerEscrowedAtOriginalPrice = buyOrder.pricePerUnit * quantity
        val refundToBuyer = buyerEscrowedAtOriginalPrice - grossAmount
        if (refundToBuyer > 0) {
            buyerAccount.currencyBalance += refundToBuyer
        }

        sellerAccount.currencyBalance += sellerProceeds
        buyerAccount.addItem(buyOrder.itemId, quantity)

        buyOrder.remainingQuantity -= quantity
        sellOrder.remainingQuantity -= quantity
        buyOrder.status = if (buyOrder.remainingQuantity == 0) OrderStatus.FILLED else OrderStatus.PARTIALLY_FILLED
        sellOrder.status = if (sellOrder.remainingQuantity == 0) OrderStatus.FILLED else OrderStatus.PARTIALLY_FILLED

        priceHistory.add(PriceHistoryEntry(buyOrder.itemId, pricePerUnit, quantity, Instant.now()))

        monitoring.recordTrade(
            DevTradeRecord(
                itemId = buyOrder.itemId,
                pricePerUnit = pricePerUnit,
                quantity = quantity,
                buyerCharacterId = buyerAccount.characterId,
                buyerAccountId = buyerAccount.accountId,
                sellerCharacterId = sellerAccount.characterId,
                sellerAccountId = sellerAccount.accountId,
                taxCollected = tax
            )
        )
    }

    // ---------------- Cancellation ----------------

    fun cancelOrder(orderId: String): ServiceResult<MarketOrder> {
        val order = (buyOrders + sellOrders).find { it.id == orderId }
            ?: return ServiceResult.Failure("Order not found.")

        if (order.status == OrderStatus.FILLED || order.status == OrderStatus.CANCELLED) {
            return ServiceResult.Failure("Order is already " + order.status.name.lowercase() + " and cannot be cancelled.")
        }

        val account = accounts.getValue(order.characterId)
        if (order.side == OrderSide.BUY) {
            val refund = order.pricePerUnit * order.remainingQuantity
            account.currencyBalance += refund
        } else {
            account.addItem(order.itemId, order.remainingQuantity)
        }

        order.remainingQuantity = 0
        order.status = OrderStatus.CANCELLED
        return ServiceResult.Success(order)
    }

    // ---------------- NPC vendor fallback ----------------

    fun sellToVendor(characterId: String, itemId: String, quantity: Int): ServiceResult<Long> {
        requireMainCharacter(characterId)?.let { return it as ServiceResult.Failure }
        val account = accounts.getValue(characterId)
        val item = ItemCatalog.find(itemId) ?: return ServiceResult.Failure("Unknown item.")

        if (quantity <= 0) return ServiceResult.Failure("Quantity must be positive.")
        if (!account.removeItem(itemId, quantity)) {
            return ServiceResult.Failure("Insufficient item quantity to sell.")
        }

        val baseValue = ItemCatalog.baseValueFor(item.id)
        val payout = ((baseValue * vendorPayoutPercent) / 100.0).toLong() * quantity
        account.currencyBalance += payout
        monitoring.recordVendorPayout(payout)

        return ServiceResult.Success(payout)
    }

    // ---------------- Public-safe queries ----------------

    fun priceHistoryFor(itemId: String): List<PriceHistoryEntry> = priceHistory.filter { it.itemId == itemId }

    fun openOrdersFor(characterId: String): List<MarketOrder> =
        (buyOrders + sellOrders).filter { it.characterId == characterId && it.status != OrderStatus.CANCELLED }

    fun allListings(): List<MarketPriceSummary> {
        val itemIds = (buyOrders + sellOrders)
            .filter { it.remainingQuantity > 0 }
            .map { it.itemId }
            .distinct()
        return itemIds.map { itemId ->
            val bestBuy = buyOrders
                .filter { it.itemId == itemId && it.remainingQuantity > 0 }
                .maxOfOrNull { it.pricePerUnit }
            val bestSell = sellOrders
                .filter { it.itemId == itemId && it.remainingQuantity > 0 }
                .minOfOrNull { it.pricePerUnit }
            MarketPriceSummary(itemId, bestBuy, bestSell)
        }
    }

    // ---------------- Persistence ----------------

    fun exportAccounts(): List<PlayerEconomyAccountExport> = accounts.values.map {
        PlayerEconomyAccountExport(
            characterId = it.characterId,
            accountId = it.accountId,
            isMainCharacter = it.isMainCharacter,
            currencyBalance = it.currencyBalance,
            inventory = it.inventory.toMap()
        )
    }

    fun restoreAccount(export: PlayerEconomyAccountExport) {
        accounts[export.characterId] = PlayerEconomyAccount(
            characterId = export.characterId,
            accountId = export.accountId,
            isMainCharacter = export.isMainCharacter,
            currencyBalance = export.currencyBalance,
            inventory = export.inventory.toMutableMap()
        )
    }

    fun exportOrders(): List<MarketOrderExport> = (buyOrders + sellOrders).map {
        MarketOrderExport(
            id = it.id,
            characterId = it.characterId,
            itemId = it.itemId,
            side = it.side.name,
            pricePerUnit = it.pricePerUnit,
            originalQuantity = it.originalQuantity,
            remainingQuantity = it.remainingQuantity,
            status = it.status.name,
            createdAt = it.createdAt.toString()
        )
    }

    fun restoreOrder(export: MarketOrderExport) {
        val order = MarketOrder(
            id = export.id,
            characterId = export.characterId,
            itemId = export.itemId,
            side = OrderSide.valueOf(export.side),
            pricePerUnit = export.pricePerUnit,
            originalQuantity = export.originalQuantity,
            remainingQuantity = export.remainingQuantity,
            status = OrderStatus.valueOf(export.status),
            createdAt = Instant.parse(export.createdAt)
        )
        if (order.side == OrderSide.BUY) buyOrders.add(order) else sellOrders.add(order)
    }

    fun exportPriceHistory(): List<PriceHistoryExport> = priceHistory.map {
        PriceHistoryExport(
            itemId = it.itemId,
            pricePerUnit = it.pricePerUnit,
            quantity = it.quantity,
            executedAt = it.executedAt.toString()
        )
    }

    fun restorePriceHistoryEntry(export: PriceHistoryExport) {
        priceHistory.add(
            PriceHistoryEntry(
                itemId = export.itemId,
                pricePerUnit = export.pricePerUnit,
                quantity = export.quantity,
                executedAt = Instant.parse(export.executedAt)
            )
        )
    }
}

data class MarketPriceSummary(val itemId: String, val bestBuyPrice: Long?, val bestSellPrice: Long?)

data class PlayerEconomyAccountExport(
    val characterId: String,
    val accountId: String,
    val isMainCharacter: Boolean,
    val currencyBalance: Long,
    val inventory: Map<String, Int>
)

data class MarketOrderExport(
    val id: String,
    val characterId: String,
    val itemId: String,
    val side: String,
    val pricePerUnit: Long,
    val originalQuantity: Int,
    val remainingQuantity: Int,
    val status: String,
    val createdAt: String
)

data class PriceHistoryExport(
    val itemId: String,
    val pricePerUnit: Long,
    val quantity: Int,
    val executedAt: String
)
