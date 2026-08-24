import re

GVM = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
MA = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"


def patch(path, old, new):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    count = content.count(old)
    assert count == 1, f"[{path}] expected exactly 1 match, found {count} for:\n{old!r}"
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: patched {path} ({len(old)} -> {len(new)} chars)")


# --- GameViewModel.kt ---

# 1. Add marketActionError StateFlow declaration, mirroring chatActionError
patch(
    GVM,
    """    private val _chatActionError = MutableStateFlow<String?>(null)
    val chatActionError: StateFlow<String?> = _chatActionError.asStateFlow()
""",
    """    private val _chatActionError = MutableStateFlow<String?>(null)
    val chatActionError: StateFlow<String?> = _chatActionError.asStateFlow()

    private val _marketActionError = MutableStateFlow<String?>(null)
    val marketActionError: StateFlow<String?> = _marketActionError.asStateFlow()
""",
)

# 2. placeBuyOrder - add onFailure (currently has none) and clear on success
patch(
    GVM,
    """    fun placeBuyOrder(itemId: String, quantity: Int, pricePerUnit: Long) {
        val characterId = _currentCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseMarketRepository.placeBuyOrder(characterId, itemId, quantity, pricePerUnit)
            result.onSuccess { order ->
                val filled = order.originalQuantity - order.remainingQuantity
                if (filled > 0) {
                    inventoryService.inventoryFor(characterId).addItem(itemId, filled)
                    refreshInventory()
                }
                refreshCurrency()
                refreshMarketListings()
                refreshMyOrders()
            }
        }
    }""",
    """    fun placeBuyOrder(itemId: String, quantity: Int, pricePerUnit: Long) {
        val characterId = _currentCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseMarketRepository.placeBuyOrder(characterId, itemId, quantity, pricePerUnit)
            result.onFailure { _marketActionError.value = it.message ?: it.toString() }
            result.onSuccess { order ->
                _marketActionError.value = null
                val filled = order.originalQuantity - order.remainingQuantity
                if (filled > 0) {
                    inventoryService.inventoryFor(characterId).addItem(itemId, filled)
                    refreshInventory()
                }
                refreshCurrency()
                refreshMarketListings()
                refreshMyOrders()
            }
        }
    }""",
)

# 3. placeSellOrder - set error on failure, clear on success
patch(
    GVM,
    """        viewModelScope.launch {
            val result = SupabaseMarketRepository.placeSellOrder(characterId, itemId, quantity, pricePerUnit)
            result.onFailure {
                realInventory.addItem(itemId, quantity)
                refreshInventory()
            }
            result.onSuccess {
                refreshCurrency()
                refreshMarketListings()
                refreshMyOrders()
            }
        }
    }""",
    """        viewModelScope.launch {
            val result = SupabaseMarketRepository.placeSellOrder(characterId, itemId, quantity, pricePerUnit)
            result.onFailure {
                _marketActionError.value = it.message ?: it.toString()
                realInventory.addItem(itemId, quantity)
                refreshInventory()
            }
            result.onSuccess {
                _marketActionError.value = null
                refreshCurrency()
                refreshMarketListings()
                refreshMyOrders()
            }
        }
    }""",
)

# 4. cancelMarketOrder - add onFailure and clear on success
patch(
    GVM,
    """    fun cancelMarketOrder(orderId: String) {
        val characterId = _currentCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseMarketRepository.cancelOrder(orderId)
            result.onSuccess { cancelled ->
                if (cancelled.side == "SELL" && cancelled.remainingQuantityBeforeCancel > 0) {
                    inventoryService.inventoryFor(characterId).addItem(cancelled.itemId, cancelled.remainingQuantityBeforeCancel)
                    refreshInventory()
                }
                refreshCurrency()
                refreshMarketListings()
                refreshMyOrders()
            }
        }
    }""",
    """    fun cancelMarketOrder(orderId: String) {
        val characterId = _currentCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseMarketRepository.cancelOrder(orderId)
            result.onFailure { _marketActionError.value = it.message ?: it.toString() }
            result.onSuccess { cancelled ->
                _marketActionError.value = null
                if (cancelled.side == "SELL" && cancelled.remainingQuantityBeforeCancel > 0) {
                    inventoryService.inventoryFor(characterId).addItem(cancelled.itemId, cancelled.remainingQuantityBeforeCancel)
                    refreshInventory()
                }
                refreshCurrency()
                refreshMarketListings()
                refreshMyOrders()
            }
        }
    }""",
)

# 5. sellItemToVendor - set error on failure, clear on success
patch(
    GVM,
    """        viewModelScope.launch {
            val result = SupabaseMarketRepository.sellToVendor(characterId, itemId, quantity, payoutPerUnit)
            result.onFailure {
                realInventory.addItem(itemId, quantity)
                refreshInventory()
            }
            result.onSuccess {
                refreshCurrency()
            }
        }
    }""",
    """        viewModelScope.launch {
            val result = SupabaseMarketRepository.sellToVendor(characterId, itemId, quantity, payoutPerUnit)
            result.onFailure {
                _marketActionError.value = it.message ?: it.toString()
                realInventory.addItem(itemId, quantity)
                refreshInventory()
            }
            result.onSuccess {
                _marketActionError.value = null
                refreshCurrency()
            }
        }
    }""",
)

# --- MainActivity.kt ---

# 6. Collect the new StateFlow alongside the other debug flows
patch(
    MA,
    """                                val debugChatError by gameViewModel.chatActionError.collectAsState()
                                var showDebugDialog by remember { mutableStateOf(false) }
                                LaunchedEffect(debugAuthError, debugCharSyncError) {
                                    if (debugAuthError != null || debugCharSyncError != null || debugChatError != null) {
                                        showDebugDialog = true
                                    }
                                }""",
    """                                val debugChatError by gameViewModel.chatActionError.collectAsState()
                                val debugMarketError by gameViewModel.marketActionError.collectAsState()
                                var showDebugDialog by remember { mutableStateOf(false) }
                                LaunchedEffect(debugAuthError, debugCharSyncError, debugMarketError) {
                                    if (debugAuthError != null || debugCharSyncError != null || debugChatError != null || debugMarketError != null) {
                                        showDebugDialog = true
                                    }
                                }""",
)

# 7. Show the market error in the debug dialog body
patch(
    MA,
    """                                                debugChatError?.let { androidx.compose.material3.Text("Chat error: $it") }
                                            }""",
    """                                                debugChatError?.let { androidx.compose.material3.Text("Chat error: $it") }
                                                debugMarketError?.let { androidx.compose.material3.Text("Market error: $it") }
                                            }""",
)

print("\nAll market error-surfacing patches applied successfully.")
