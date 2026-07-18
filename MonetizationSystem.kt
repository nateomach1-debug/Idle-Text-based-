import java.time.Duration
import java.time.Instant

// =========================================================
// ITEM STATS, ITEM CATEGORY, and ITEM DEFINITION now all come
// from SharedTypes.kt -- the minimal stand-in versions that
// used to live here have been removed.
// =========================================================

// =========================================================
// ACTIVE GUARDRAIL
// (ServiceResult now comes from SharedTypes.kt.)
// =========================================================

object ItemMonetizationGuardrail {
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

    fun registerCosmetic(
        id: String,
        name: String,
        isTradeable: Boolean,
        isRealMoneyPurchasable: Boolean
    ): ServiceResult<ItemDefinition> {
        val item = ItemDefinition(
            id = id,
            name = name,
            category = ItemCategory.COSMETIC,
            isTradeable = isTradeable,
            isStackable = false,
            isRealMoneyPurchasable = isRealMoneyPurchasable,
            stats = ItemStats()
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
// SUBSCRIPTION TOKEN
// =========================================================

object SubscriptionTokenCatalog {
    val tokenItem = ItemDefinition(
        id = "subscription_token",
        name = "Membership Token",
        category = ItemCategory.CONSUMABLE,
        isTradeable = true,
        isStackable = true,
        isRealMoneyPurchasable = false,
        stats = ItemStats()
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
    val extendedFullRateWindow: Duration = Duration.ofHours(36)
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
// =========================================================

object SubscriptionAwareEfficiencyCurve {
    private val baseFullRateWindow: Duration = Duration.ofHours(12)
    private val floorTransitionPoint: Duration = Duration.ofHours(72)
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
// PREMIUM CURRENCY BUNDLES
// =========================================================

data class CurrencyBundle(
    val id: String,
    val realMoneyPriceUsd: Double,
    val premiumCurrencyGranted: Long,
    val bonusPercent: Double = 0.0
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
