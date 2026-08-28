package com.yourname.idlerpg

import io.github.jan.supabase.postgrest.postgrest
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put

@Serializable
data class MarketOrderRpcResult(
    val id: String,
    val originalQuantity: Int,
    val remainingQuantity: Int,
    val status: String
)

@Serializable
data class MarketCancelRpcResult(
    val id: String,
    val side: String,
    val itemId: String,
    val remainingQuantityBeforeCancel: Int
)

@Serializable
data class MarketListingRow(
    val itemId: String,
    val bestBuyPrice: Long? = null,
    val bestBuyQuantity: Int? = null,
    val bestSellPrice: Long? = null,
    val bestSellQuantity: Int? = null
)

@Serializable
data class MarketOrderRow(
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

@Serializable
data class MarketSaleRow(
    val itemId: String,
    val quantity: Int,
    val pricePerUnit: Long,
    val taxCollected: Long,
    val executedAt: String
)

object SupabaseMarketRepository {
    private val client get() = SupabaseClientProvider.client

    suspend fun placeBuyOrder(characterId: String, itemId: String, quantity: Int, pricePerUnit: Long): Result<MarketOrderRpcResult> = runCatching {
        client.postgrest.rpc("market_place_buy_order", buildJsonObject {
            put("p_character_id", characterId)
            put("p_item_id", itemId)
            put("p_quantity", quantity)
            put("p_price_per_unit", pricePerUnit)
        }).decodeAs<MarketOrderRpcResult>()
    }

    suspend fun placeSellOrder(characterId: String, itemId: String, quantity: Int, pricePerUnit: Long): Result<MarketOrderRpcResult> = runCatching {
        client.postgrest.rpc("market_place_sell_order", buildJsonObject {
            put("p_character_id", characterId)
            put("p_item_id", itemId)
            put("p_quantity", quantity)
            put("p_price_per_unit", pricePerUnit)
        }).decodeAs<MarketOrderRpcResult>()
    }

    suspend fun cancelOrder(orderId: String): Result<MarketCancelRpcResult> = runCatching {
        client.postgrest.rpc("market_cancel_order", buildJsonObject {
            put("p_order_id", orderId)
        }).decodeAs<MarketCancelRpcResult>()
    }

    suspend fun sellToVendor(characterId: String, itemId: String, quantity: Int, payoutPerUnit: Long): Result<Long> = runCatching {
        client.postgrest.rpc("market_sell_to_vendor", buildJsonObject {
            put("p_character_id", characterId)
            put("p_item_id", itemId)
            put("p_quantity", quantity)
            put("p_payout_per_unit", payoutPerUnit)
        }).decodeAs<Long>()
    }

    suspend fun grantCombatCoins(characterId: String, amount: Long): Result<Long> = runCatching {
        client.postgrest.rpc("combat_grant_coins", buildJsonObject {
            put("p_character_id", characterId)
            put("p_amount", amount)
        }).decodeAs<Long>()
    }

    suspend fun myRecentSales(characterId: String, since: String): Result<List<MarketSaleRow>> = runCatching {
        client.postgrest.rpc("market_my_recent_sales", buildJsonObject {
            put("p_character_id", characterId)
            put("p_since", since)
        }).decodeList<MarketSaleRow>()
    }

    suspend fun currencyBalance(characterId: String): Result<Long> = runCatching {
        client.postgrest.rpc("market_currency_balance", buildJsonObject {
            put("p_character_id", characterId)
        }).decodeAs<Long>()
    }

    suspend fun listings(): Result<List<MarketListingRow>> = runCatching {
        client.postgrest.rpc("market_listings").decodeList<MarketListingRow>()
    }

    suspend fun myOrders(characterId: String): Result<List<MarketOrderRow>> = runCatching {
        client.postgrest.rpc("market_my_orders", buildJsonObject {
            put("p_character_id", characterId)
        }).decodeList<MarketOrderRow>()
    }

    suspend fun buyFromVendor(characterId: String, itemId: String, quantity: Int, pricePerUnit: Long): Result<Long> = runCatching {
        client.postgrest.rpc("market_buy_from_vendor", buildJsonObject {
            put("p_character_id", characterId)
            put("p_item_id", itemId)
            put("p_quantity", quantity)
            put("p_price_per_unit", pricePerUnit)
        }).decodeAs<Long>()
    }
}
