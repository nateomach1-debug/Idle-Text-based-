GVM = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"


def patch(old, new):
    with open(GVM, "r", encoding="utf-8") as f:
        content = f.read()
    count = content.count(old)
    assert count == 1, f"expected exactly 1 match, found {count} for:\n{old!r}"
    content = content.replace(old, new)
    with open(GVM, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: patched ({len(old)} -> {len(new)} chars)")


# 1. refreshCurrency - straight swap, no inventory usage
patch(
    """    fun refreshCurrency() {
        val accountId = _currentAccountId.value ?: return
        val account = accountService.accountById(accountId) ?: return
        val characterId = _currentCharacterId.value ?: return
        viewModelScope.launch {
            val gold = SupabaseMarketRepository.currencyBalance(characterId).getOrNull() ?: 0L
            _currency.value = gold to account.premiumCurrency
        }
    }""",
    """    fun refreshCurrency() {
        val accountId = _currentAccountId.value ?: return
        val account = accountService.accountById(accountId) ?: return
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val gold = SupabaseMarketRepository.currencyBalance(characterId).getOrNull() ?: 0L
            _currency.value = gold to account.premiumCurrency
        }
    }""",
)

# 2. refreshMyOrders - straight swap, no inventory usage
patch(
    """    fun refreshMyOrders() {
        val characterId = _currentCharacterId.value ?: return
        viewModelScope.launch {
            val orders = SupabaseMarketRepository.myOrders(characterId).getOrNull()?.map { it.toDomain() } ?: emptyList()""",
    """    fun refreshMyOrders() {
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val orders = SupabaseMarketRepository.myOrders(characterId).getOrNull()?.map { it.toDomain() } ?: emptyList()""",
)

# 3. placeBuyOrder - needs BOTH ids: local for inventory, supabase for the RPC call
patch(
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
                }""",
    """    fun placeBuyOrder(itemId: String, quantity: Int, pricePerUnit: Long) {
        val characterId = _currentCharacterId.value ?: return
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseMarketRepository.placeBuyOrder(supabaseCharacterId, itemId, quantity, pricePerUnit)
            result.onFailure { _marketActionError.value = it.message ?: it.toString() }
            result.onSuccess { order ->
                _marketActionError.value = null
                val filled = order.originalQuantity - order.remainingQuantity
                if (filled > 0) {
                    inventoryService.inventoryFor(characterId).addItem(itemId, filled)
                    refreshInventory()
                }""",
)

# 4. placeSellOrder - needs BOTH ids
patch(
    """    fun placeSellOrder(itemId: String, quantity: Int, pricePerUnit: Long) {
        val characterId = _currentCharacterId.value ?: return
        val realInventory = inventoryService.inventoryFor(characterId)
        if (realInventory.quantityOf(itemId) < quantity) return

        realInventory.removeItem(itemId, quantity)
        refreshInventory()

        viewModelScope.launch {
            val result = SupabaseMarketRepository.placeSellOrder(characterId, itemId, quantity, pricePerUnit)""",
    """    fun placeSellOrder(itemId: String, quantity: Int, pricePerUnit: Long) {
        val characterId = _currentCharacterId.value ?: return
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        val realInventory = inventoryService.inventoryFor(characterId)
        if (realInventory.quantityOf(itemId) < quantity) return

        realInventory.removeItem(itemId, quantity)
        refreshInventory()

        viewModelScope.launch {
            val result = SupabaseMarketRepository.placeSellOrder(supabaseCharacterId, itemId, quantity, pricePerUnit)""",
)

# 5. sellItemToVendor - needs BOTH ids (corrected: includes the removeItem/refreshInventory lines)
patch(
    """    fun sellItemToVendor(itemId: String, quantity: Int) {
        val characterId = _currentCharacterId.value ?: return
        val realInventory = inventoryService.inventoryFor(characterId)
        if (realInventory.quantityOf(itemId) < quantity) return
        val payoutPerUnit = ((ItemCatalog.baseValueFor(itemId) * 40.0) / 100.0).toLong()

        realInventory.removeItem(itemId, quantity)
        refreshInventory()

        viewModelScope.launch {
            val result = SupabaseMarketRepository.sellToVendor(characterId, itemId, quantity, payoutPerUnit)""",
    """    fun sellItemToVendor(itemId: String, quantity: Int) {
        val characterId = _currentCharacterId.value ?: return
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        val realInventory = inventoryService.inventoryFor(characterId)
        if (realInventory.quantityOf(itemId) < quantity) return
        val payoutPerUnit = ((ItemCatalog.baseValueFor(itemId) * 40.0) / 100.0).toLong()

        realInventory.removeItem(itemId, quantity)
        refreshInventory()

        viewModelScope.launch {
            val result = SupabaseMarketRepository.sellToVendor(supabaseCharacterId, itemId, quantity, payoutPerUnit)""",
)

print("\nAll character-id patches applied successfully.")
