import java.time.Duration
import java.time.Instant
import java.util.UUID

// =========================================================
// ITEM STATS & MINIMAL ITEM DEFINITION
// (Self-contained stand-in consistent with the Items & Equipment
//  module -- extended here with the real-money-purchasable flag
//  needed for the guardrail. Would be merged into one shared
//  ItemDefinition once all modules are combined into one project.)
// =========================================================

enum class ItemCategory { WEAPON, ARMOR, ACCESSORY, MATERIAL, CONSUMABLE, COSMETIC }

data class ItemStats(
    val attackBonus: Int = 0,
    val strengthBonus: Int = 0,
    val defenseBonus: Int = 0,
    val accuracyBonus: Int = 0,
    val maxHitBonus: Int = 0
) {
    fun isAllZero(): Boolean =
        attackBonus == 0 && strengthBonus == 0 && defenseBonus == 0 && accuracyBonus == 0 && maxHitBonus == 0
}

data class ItemDefinition(
    val id: String,
    val name: String,
    val category: ItemCategory,
    val isTradeable: Boolean,
    val isStackable: Boolean,
    val isRealMoneyPurchasable: Boolean = false,
    val stats: ItemStats = ItemStats()
)

// =========================================================
// ACTIVE GUARDRAIL
// (Rejects at creation time -- not just a design guideline.)
// =========================================================

sealed class ServiceResult<out T> {
    data class Success<T>(val value: T) : ServiceResult<T>()
    data class Failure(val reason: String) : ServiceResult<Nothing>()
}

object ItemMonetizationGuardrail {
    /**
     * Any COSMETIC item, or any item flagged as real-money-purchasable,
     * MUST have all-zero stats. This is checked actively, not just assumed.
     */
    fun validate(item: ItemDefinition): ServiceResult<ItemDefinition> {
        val mustBeStatless = item.category == ItemCategory.COSMETIC || item.isRealMoneyPurchasable
        if (mustBeStatless && !item.stats.isAllZero()) {
            return ServiceResult.Failure(
                "Rejected: '" + item.name + "' is cosmetic and/or real-money-purchasable but has non-zero stats. " +
                "This is not permitted under the anti-pay-to-win guardrail."
            )
        }
        return ServiceResult.Success(item)
    }
}

// =========================================================
// COSMETIC CATALOG
// =========================================================

class CosmeticCatalog {
    private val cosmetics: MutableMap<String, ItemDefinition> = mutableMapOf()

    /** All cosmetic creation MUST go through this -- guardrail-checked, never bypassable. */
    fun registerCosmetic(
        id: String,
        name: String,
        isTradeable: Boolean, // true if directly purchased, false if event-earned
        isRealMoneyPurchasable: Boolean
    ): ServiceResult<ItemDefinition> {
        val item = ItemDefinition(
            id = id,
            name = name,
            category = ItemCategory.COSMETIC,
            isTradeable = isTradeable,
            isStackable = false,
            isRealMoneyPurchasable = isRealMoneyPurchasable,
            stats = ItemStats() // always zero -- cosmetics never carry stats by construction
        )
        val validation = ItemMonetizationGuardrail.validate(item)
        if (validation is ServiceResult.Failure) return validation

        cosmetics[id] = item
        return ServiceResult.Success(item)
    }

    fun find(id: String): ItemDefinition? = cosmetics[id]
    fun all(): List<ItemDefinition> = cosmetics.values.toList()
}

// =========================================================
// SUBSCRIPTION TOKEN (tradeable item, redeemable for subscription time)
// =========================================================

object SubscriptionTokenCatalog {
    val tokenItem = ItemDefinition(
        id = "subscription_token",
        name = "Membership Token",
        category = ItemCategory.CONSUMABLE, // consumed/redeemed on use
        isTradeable = true, // purchased with premium currency, then freely tradeable on the market
        isStackable = true,
        isRealMoneyPurchasable = false, // the TOKEN itself is bought with premium currency, not directly with real money
        stats = ItemStats() // guaranteed statless -- QoL only, never power
    )

    private const val DAYS_GRANTED_PER_TOKEN = 30
    fun daysGrantedPerToken(): Int = DAYS_GRANTED_PER_TOKEN
}

// =========================================================
// SUBSCRIPTION STATE & BENEFITS
// =========================================================

data class SubscriptionBenefits(
    val inventorySlotBonus: Int = 20,
    val cosmeticLoadoutSlotBonus: Int = 3,
    val extendedFullRateWindow: Duration = Duration.ofHours(36) // vs. base 12h for non-subscribers
)

class SubscriptionState(
    var activeUntil: Instant? = null
) {
    fun isActive(now: Instant = Instant.now()): Boolean {
        val until = activeUntil ?: return false
        return now.isBefore(until)
    }
}

class SubscriptionService {
    private val states: MutableMap<String, SubscriptionState> = mutableMapOf()
    val benefits = SubscriptionBenefits()

    private fun stateFor(characterId: String) = states.getOrPut(characterId) { SubscriptionState() }

    fun isSubscribed(characterId: String, now: Instant = Instant.now()): Boolean = stateFor(characterId).isActive(now)

    /** Redeeming a token consumes it from inventory (handled by caller) and extends subscription time. */
    fun redeemToken(characterId: String, now: Instant = Instant.now()): ServiceResult<Instant> {
        val state = stateFor(characterId)
        val currentExpiry = if (state.isActive(now)) state.activeUntil!! else now
        val newExpiry = currentExpiry.plus(Duration.ofDays(SubscriptionTokenCatalog.daysGrantedPerToken().toLong()))
        state.activeUntil = newExpiry
        return ServiceResult.Success(newExpiry)
    }

    fun activeUntil(characterId: String): Instant? = stateFor(characterId).activeUntil
}

// =========================================================
// OFFLINE EFFICIENCY CURVE, SUBSCRIPTION-AWARE
// (Extends the taper model from Offline/Idle -- subscribers get a
//  longer 100% window, compressing the 50% middle tier, but the
//  floor transition point stays FIXED at the same total elapsed
//  time for every player, subscribed or not.)
// =========================================================

object SubscriptionAwareEfficiencyCurve {
    private val baseFullRateWindow: Duration = Duration.ofHours(12)     // non-subscriber 100% window
    private val floorTransitionPoint: Duration = Duration.ofHours(72)   // FIXED for everyone -- when 25% floor kicks in
    private const val FULL_RATE_PERCENT = 100.0
    private const val REDUCED_RATE_PERCENT = 50.0
    private const val FLOOR_RATE_PERCENT = 25.0

    fun efficiencyAt(elapsed: Duration, isSubscriber: Boolean, subscriberFullRateWindow: Duration): Double {
        val fullRateWindow = if (isSubscriber) subscriberFullRateWindow else baseFullRateWindow
        return when {
            elapsed <= fullRateWindow -> FULL_RATE_PERCENT
            elapsed <= floorTransitionPoint -> REDUCED_RATE_PERCENT
            else -> FLOOR_RATE_PERCENT
        }
    }

    fun effectiveElapsed(elapsed: Duration, isSubscriber: Boolean, subscriberFullRateWindow: Duration): Duration {
        val fullRateWindow = if (isSubscriber) subscriberFullRateWindow else baseFullRateWindow

        if (elapsed <= fullRateWindow) return elapsed

        val fullMillis = fullRateWindow.toMillis()
        val reducedEndMillis = minOf(elapsed.toMillis(), floorTransitionPoint.toMillis())
        val reducedMillis = (reducedEndMillis - fullMillis).coerceAtLeast(0)
        val floorMillis = (elapsed.toMillis() - floorTransitionPoint.toMillis()).coerceAtLeast(0)

        val effectiveMillis =
            (fullMillis * (FULL_RATE_PERCENT / 100.0)) +
            (reducedMillis * (REDUCED_RATE_PERCENT / 100.0)) +
            (floorMillis * (FLOOR_RATE_PERCENT / 100.0))

        return Duration.ofMillis(effectiveMillis.toLong())
    }
}

// =========================================================
// PREMIUM CURRENCY BUNDLES (real money purchase)
// =========================================================

data class CurrencyBundle(
    val id: String,
    val realMoneyPriceUsd: Double,
    val premiumCurrencyGranted: Long,
    val bonusPercent: Double = 0.0 // larger bundles typically grant a bonus on top
)

object CurrencyBundleCatalog {
    val bundles = listOf(
        CurrencyBundle(id = "bundle_small", realMoneyPriceUsd = 4.99, premiumCurrencyGranted = 500),
        CurrencyBundle(id = "bundle_medium", realMoneyPriceUsd = 9.99, premiumCurrencyGranted = 1100, bonusPercent = 10.0),
        CurrencyBundle(id = "bundle_large", realMoneyPriceUsd = 24.99, premiumCurrencyGranted = 3000, bonusPercent = 20.0)
    )

    fun find(bundleId: String): CurrencyBundle? = bundles.find { it.id == bundleId }
}

class CurrencyPurchaseService {
    private val premiumBalances: MutableMap<String, Long> = mutableMapOf()

    fun balanceFor(characterId: String): Long = premiumBalances[characterId] ?: 0

    fun purchaseBundle(characterId: String, bundleId: String): ServiceResult<Long> {
        val bundle = CurrencyBundleCatalog.find(bundleId) ?: return ServiceResult.Failure("Unknown bundle.")
        // Real payment processing would happen here via whatever payment integration exists --
        // this module only tracks the resulting balance once a purchase is confirmed.
        val newBalance = balanceFor(characterId) + bundle.premiumCurrencyGranted
        premiumBalances[characterId] = newBalance
        return ServiceResult.Success(newBalance)
    }

    fun spend(characterId: String, amount: Long): ServiceResult<Long> {
        val balance = balanceFor(characterId)
        if (balance < amount) return ServiceResult.Failure("Insufficient premium currency.")
        val newBalance = balance - amount
        premiumBalances[characterId] = newBalance
        return ServiceResult.Success(newBalance)
    }
}

// =========================================================
// DEMO
// =========================================================

fun main() {
    println("=== Attempting to register a valid cosmetic (zero stats) ===")
    val cosmetics = CosmeticCatalog()
    printResult(cosmetics.registerCosmetic("golden_cloak", "Golden Cloak", isTradeable = true, isRealMoneyPurchasable = true))

    println("")
    println("=== Attempting to register an event-earned cosmetic (non-tradeable) ===")
    printResult(cosmetics.registerCosmetic("winter_crown", "Winter Crown", isTradeable = false, isRealMoneyPurchasable = false))

    println("")
    println("=== Guardrail test: attempting to sneak stats onto a cosmetic (should be rejected) ===")
    val riggedCosmetic = ItemDefinition(
        id = "sus_amulet",
        name = "Suspiciously Powerful Amulet",
        category = ItemCategory.COSMETIC,
        isTradeable = true,
        isStackable = false,
        isRealMoneyPurchasable = true,
        stats = ItemStats(attackBonus = 50) // should never pass
    )
    printResult(ItemMonetizationGuardrail.validate(riggedCosmetic))

    println("")
    println("=== Guardrail test: a non-cosmetic real-money item with stats (should also be rejected) ===")
    val riggedPurchasable = ItemDefinition(
        id = "sus_sword",
        name = "Pay-to-Win Sword",
        category = ItemCategory.WEAPON,
        isTradeable = false,
        isStackable = false,
        isRealMoneyPurchasable = true,
        stats = ItemStats(attackBonus = 999)
    )
    printResult(ItemMonetizationGuardrail.validate(riggedPurchasable))

    println("")
    println("=== Purchasing a currency bundle, then buying a subscription token ===")
    val currencyService = CurrencyPurchaseService()
    printResult(currencyService.purchaseBundle("alice", "bundle_medium"))
    println("Alice's premium balance: " + currencyService.balanceFor("alice"))

    val tokenPrice = 300L
    printResult(currencyService.spend("alice", tokenPrice))
    println("Alice's premium balance after buying a token: " + currencyService.balanceFor("alice"))

    println("")
    println("=== Alice redeems the token for subscription time ===")
    val subscriptions = SubscriptionService()
    printResult(subscriptions.redeemToken("alice"))
    println("Alice is subscribed: " + subscriptions.isSubscribed("alice"))
    println("Subscription active until: " + subscriptions.activeUntil("alice"))

    println("")
    println("=== Redeeming a second token stacks additional time on top ===")
    printResult(subscriptions.redeemToken("alice"))
    println("New subscription end date: " + subscriptions.activeUntil("alice"))

    println("")
    println("=== Comparing offline efficiency: subscriber vs. non-subscriber at 20 hours elapsed ===")
    val elapsed20h = Duration.ofHours(20)
    val nonSubEfficiency = SubscriptionAwareEfficiencyCurve.efficiencyAt(elapsed20h, isSubscriber = false, subscriberFullRateWindow = subscriptions.benefits.extendedFullRateWindow)
    val subEfficiency = SubscriptionAwareEfficiencyCurve.efficiencyAt(elapsed20h, isSubscriber = true, subscriberFullRateWindow = subscriptions.benefits.extendedFullRateWindow)
    println("Non-subscriber efficiency at 20h: " + nonSubEfficiency + "%")
    println("Subscriber efficiency at 20h: " + subEfficiency + "%")

    println("")
    println("=== Confirming BOTH still hit the 25% floor at the same total elapsed time (80 hours) ===")
    val elapsed80h = Duration.ofHours(80)
    val nonSubFloor = SubscriptionAwareEfficiencyCurve.efficiencyAt(elapsed80h, isSubscriber = false, subscriberFullRateWindow = subscriptions.benefits.extendedFullRateWindow)
    val subFloor = SubscriptionAwareEfficiencyCurve.efficiencyAt(elapsed80h, isSubscriber = true, subscriberFullRateWindow = subscriptions.benefits.extendedFullRateWindow)
    println("Non-subscriber efficiency at 80h: " + nonSubFloor + "%")
    println("Subscriber efficiency at 80h: " + subFloor + "%")
}

fun <T> printResult(result: ServiceResult<T>) {
    when (result) {
        is ServiceResult.Success -> println("[OK] " + result.value)
        is ServiceResult.Failure -> println("[FAIL] " + result.reason)
    }
}
