import java.time.Instant
import java.util.UUID
import kotlin.random.Random

// =========================================================
// MARKET ITEM CATALOG
// (Minimal stand-in until the real Items module exists --
//  baseValue drives the NPC vendor's fixed-percentage payout.)
// =========================================================

data class MarketItem(
    val id: String,
    val name: String,
    val baseValue: Long // reference value used by the NPC vendor calculation
)

object ItemCatalog {
    val items = listOf(
        MarketItem("iron_ore", "Iron Ore", baseValue = 10),
        MarketItem("oak_log", "Oak Log", baseValue = 8),
        MarketItem("steel_bar", "Steel Bar", baseValue = 45)
    )

    fun find(itemId: String): MarketItem? = items.find { it.id == itemId }
}

// =========================================================
// PLAYER ECONOMY ACCOUNT
// (Minimal stand-in for currency + inventory until Account/Character
//  and Items modules are wired together with this one.)
// =========================================================

class PlayerEconomyAccount(
    val characterId: String,
    val accountId: String,
    var isMainCharacter: Boolean,
    var currencyBalance: Long,
    val inventory: MutableMap<String, Int> = mutableMapOf() // itemId -> quantity
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

/** Public-safe record -- what a price history graph would display to players. */
data class PriceHistoryEntry(
    val itemId: String,
    val pricePerUnit: Long,
    val quantity: Int,
    val executedAt: Instant
)

/**
 * Developer-only record. Full buyer/seller account linkage for
 * collusion/pattern detection. Never exposed through any player-facing method.
 */
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
// RESULT TYPE
// =========================================================

sealed class ServiceResult<out T> {
    data class Success<T>(val value: T) : ServiceResult<T>()
    data class Failure(val reason: String) : ServiceResult<Nothing>()
}

// =========================================================
// DEVELOPER-ONLY ECONOMY MONITORING
// (No player-facing methods anywhere in this class, by design.)
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

    // ---- Developer-only query methods ----

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
// =========================================================

class MarketService(private val monitoring: EconomyMonitoringService) {

    private val accounts: MutableMap<String, PlayerEconomyAccount> = mutableMapOf()
    private val buyOrders: MutableList<MarketOrder> = mutableListOf()
    private val sellOrders: MutableList<MarketOrder> = mutableListOf()
    private val priceHistory: MutableList<PriceHistoryEntry> = mutableListOf()

    private val taxRatePercent: Double = 10.0
    private val vendorPayoutPercent: Double = 40.0 // fixed % of baseValue

    fun registerAccount(account: PlayerEconomyAccount) {
        accounts[account.characterId] = account
    }

    fun accountFor(characterId: String): PlayerEconomyAccount? = accounts[characterId]

    private fun requireMainCharacter(characterId: String): ServiceResult<PlayerEconomyAccount>? {
        val account = accounts[characterId] ?: return ServiceResult.Failure("Character not registered.")
        if (!account.isMainCharacter) {
            return ServiceResult.Failure("Only the account's Main character can access the market.")
        }
        return null // null means "passed the check" -- caller continues
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

        // Escrow on placement: currency locked immediately.
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

        // Escrow on placement: item removed from inventory immediately.
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

    /**
     * Price-time priority: sell orders sorted cheapest-first, buy orders sorted
     * highest-price-first, ties broken by earliest createdAt. A match executes
     * whenever the best buy price >= the best sell price, at the RESTING
     * (already-in-book) order's price. Supports partial fills on both sides.
     */
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

            if (bestBuy.pricePerUnit < bestSell.pricePerUnit) break // no crossing price -- no trade possible

            // Whichever order was resting first sets the execution price.
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

        // Buyer already escrowed at THEIR order's price, which may be higher than
        // the execution price -- refund the difference if the buyer overpaid relative
        // to the actual matched price.
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

        val payout = ((item.baseValue * vendorPayoutPercent) / 100.0).toLong() * quantity
        account.currencyBalance += payout
        monitoring.recordVendorPayout(payout)

        return ServiceResult.Success(payout)
    }

    // ---------------- Public-safe queries ----------------

    fun priceHistoryFor(itemId: String): List<PriceHistoryEntry> = priceHistory.filter { it.itemId == itemId }

    fun openOrdersFor(characterId: String): List<MarketOrder> =
        (buyOrders + sellOrders).filter { it.characterId == characterId && it.status != OrderStatus.CANCELLED }
}

// =========================================================
// DEMO
// =========================================================

fun main() {
    val monitoring = EconomyMonitoringService()
    val market = MarketService(monitoring)

    val alice = PlayerEconomyAccount("alice-char", "alice-account", isMainCharacter = true, currencyBalance = 1000)
    val bob = PlayerEconomyAccount("bob-char", "bob-account", isMainCharacter = true, currencyBalance = 1000)
    bob.addItem("iron_ore", 50)

    val notMain = PlayerEconomyAccount("alice-alt-char", "alice-account", isMainCharacter = false, currencyBalance = 500)

    market.registerAccount(alice)
    market.registerAccount(bob)
    market.registerAccount(notMain)

    println("=== Non-main character attempts to place an order (should fail) ===")
    printResult(market.placeBuyOrder("alice-alt-char", "iron_ore", 5, 12))

    println("")
    println("=== Bob places a sell order: 30 Iron Ore @ 10 each ===")
    val sellOrderResult = market.placeSellOrder("bob-char", "iron_ore", 30, 10)
    printResult(sellOrderResult)
    println("Bob's inventory after escrow: " + bob.inventory)

    println("")
    println("=== Alice places a buy order: 20 Iron Ore @ 12 each (crosses Bob's price) ===")
    val buyOrderResult = market.placeBuyOrder("alice-char", "iron_ore", 20, 12)
    printResult(buyOrderResult)

    println("")
    println("=== Post-trade balances ===")
    println("Alice currency: " + alice.currencyBalance + " | inventory: " + alice.inventory)
    println("Bob currency: " + bob.currencyBalance + " | inventory: " + bob.inventory)

    println("")
    println("=== Bob's remaining sell order (should be partially filled, 10 left) ===")
    val bobOpenOrders = market.openOrdersFor("bob-char")
    bobOpenOrders.forEach { println("Order " + it.id + " status=" + it.status + " remaining=" + it.remainingQuantity) }

    println("")
    println("=== Cancelling Bob's remaining order ===")
    val bobRemainingOrder = bobOpenOrders.first { it.status == OrderStatus.PARTIALLY_FILLED }
    printResult(market.cancelOrder(bobRemainingOrder.id))
    println("Bob's inventory after cancellation refund: " + bob.inventory)

    println("")
    println("=== Alice sells 5 Iron Ore to the NPC vendor ===")
    printResult(market.sellToVendor("alice-char", "iron_ore", 5))
    println("Alice currency after vendor sale: " + alice.currencyBalance + " | inventory: " + alice.inventory)

    println("")
    println("=== Price history for Iron Ore ===")
    market.priceHistoryFor("iron_ore").forEach {
        println("- qty=" + it.quantity + " price=" + it.pricePerUnit + " at " + it.executedAt)
    }

    println("")
    println("=== Developer-only: economy health snapshot ===")
    println(monitoring.economyHealthSnapshot())

    println("")
    println("=== Developer-only: full trade log with account-level detail ===")
    monitoring.fullTradeLog().forEach {
        println("- " + it.quantity + "x " + it.itemId + " @ " + it.pricePerUnit +
            " | buyer=" + it.buyerCharacterId + "(" + it.buyerAccountId + ")" +
            " seller=" + it.sellerCharacterId + "(" + it.sellerAccountId + ")" +
            " tax=" + it.taxCollected)
    }
}

fun <T> printResult(result: ServiceResult<T>) {
    when (result) {
        is ServiceResult.Success -> println("[OK] " + result.value)
        is ServiceResult.Failure -> println("[FAIL] " + result.reason)
    }
}
