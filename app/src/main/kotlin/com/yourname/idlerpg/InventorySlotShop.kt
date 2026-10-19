package com.yourname.idlerpg

object InventorySlotShop {
    const val COIN_PACK_SLOTS = 5
    const val GEM_PACK_SLOTS = 25

    // Price of each successive pack, in order. Edit these to rebalance.
    val COIN_PACK_PRICES = listOf(
        50_000L, 75_000L, 100_000L, 150_000L, 200_000L,
        300_000L, 400_000L, 600_000L, 800_000L, 1_000_000L
    )
    val GEM_PACK_PRICES = listOf(
        100L, 150L, 200L, 250L, 300L, 400L, 500L, 600L
    )

    val COIN_SLOTS_TOTAL: Int get() = COIN_PACK_PRICES.size * COIN_PACK_SLOTS
    val GEM_SLOTS_TOTAL: Int get() = GEM_PACK_PRICES.size * GEM_PACK_SLOTS

    fun nextCoinPackPrice(packsBought: Int): Long? = COIN_PACK_PRICES.getOrNull(packsBought)
    fun nextGemPackPrice(packsBought: Int): Long? = GEM_PACK_PRICES.getOrNull(packsBought)
}
