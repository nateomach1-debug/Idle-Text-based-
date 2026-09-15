import sys

BASE = "app/src/main/kotlin/com/yourname/idlerpg/"

def guarded_replace(path, old, new, label):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Check idempotency FIRST: for edits that append/extend rather than fully
    # replace, old_str can still be present (unchanged) inside an
    # already-patched file, since new_str = old_str + extra content. Checking
    # new_str first prevents re-applying (and duplicating) such edits.
    if new in text:
        print(f"SKIP (already applied): {label} ({path})")
        return True

    count = text.count(old)
    if count == 1:
        text = text.replace(old, new)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"OK: {label} ({path})")
        return True
    elif count == 0:
        print(f"FAIL (old_str not found, new_str not found either): {label} ({path})")
        return False
    else:
        print(f"FAIL (old_str matched {count} times, expected 1): {label} ({path})")
        return False


def check_braces(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    opens = text.count("{")
    closes = text.count("}")
    if opens != closes:
        print(f"WARNING: brace mismatch in {path}: {{ = {opens}, }} = {closes}")
        return False
    print(f"Brace check OK: {path} ({{ = {opens}, }} = {closes})")
    return True


results = []

# ---------------------------------------------------------
# 1. SupabaseModerationRepository.kt - add grantGems
# ---------------------------------------------------------
path = BASE + "SupabaseModerationRepository.kt"
old = '''    suspend fun unmuteCharacter(characterId: String): Result<Unit> = runCatching {
        client.postgrest.rpc("admin_unmute_character", buildJsonObject {
            put("p_character_id", characterId)
        })
    }
}'''
new = '''    suspend fun unmuteCharacter(characterId: String): Result<Unit> = runCatching {
        client.postgrest.rpc("admin_unmute_character", buildJsonObject {
            put("p_character_id", characterId)
        })
    }

    // ---------------------------------------------------------
    // PREMIUM CURRENCY (GEMS) - MODERATOR GRANT
    // ---------------------------------------------------------

    suspend fun grantGems(characterId: String, amount: Long, reason: String): Result<Long> = runCatching {
        client.postgrest.rpc("admin_grant_gems", buildJsonObject {
            put("p_character_id", characterId)
            put("p_amount", amount)
            put("p_reason", reason)
        }).decodeAs<Long>()
    }
}'''
results.append(guarded_replace(path, old, new, "add grantGems to SupabaseModerationRepository"))

# ---------------------------------------------------------
# 2. SupabaseMarketRepository.kt - add gemsBalance/spendGems/creditGems
# ---------------------------------------------------------
path = BASE + "SupabaseMarketRepository.kt"
old = '''    suspend fun currencyBalance(characterId: String): Result<Long> = runCatching {
        client.postgrest.rpc("market_currency_balance", buildJsonObject {
            put("p_character_id", characterId)
        }).decodeAs<Long>()
    }'''
new = '''    suspend fun currencyBalance(characterId: String): Result<Long> = runCatching {
        client.postgrest.rpc("market_currency_balance", buildJsonObject {
            put("p_character_id", characterId)
        }).decodeAs<Long>()
    }

    suspend fun gemsBalance(characterId: String): Result<Long> = runCatching {
        client.postgrest.rpc("gems_balance", buildJsonObject {
            put("p_character_id", characterId)
        }).decodeAs<Long>()
    }

    suspend fun spendGems(characterId: String, amount: Long): Result<Long> = runCatching {
        client.postgrest.rpc("spend_gems", buildJsonObject {
            put("p_character_id", characterId)
            put("p_amount", amount)
        }).decodeAs<Long>()
    }

    suspend fun creditGems(characterId: String, amount: Long): Result<Long> = runCatching {
        client.postgrest.rpc("credit_gems", buildJsonObject {
            put("p_character_id", characterId)
            put("p_amount", amount)
        }).decodeAs<Long>()
    }'''
results.append(guarded_replace(path, old, new, "add gemsBalance/spendGems/creditGems to SupabaseMarketRepository"))

# ---------------------------------------------------------
# 3a. GameViewModel.kt - refreshCurrency now reads gems from server
# ---------------------------------------------------------
path = BASE + "GameViewModel.kt"
old = '''    fun refreshCurrency() {
        val accountId = _currentAccountId.value ?: return
        val account = accountService.accountById(accountId) ?: return
        _unlockedPresets.value = account.unlockedPresets.toSet()
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val gold = SupabaseMarketRepository.currencyBalance(characterId).getOrNull() ?: 0L
            _currency.value = gold to account.premiumCurrency
        }
    }'''
new = '''    fun refreshCurrency() {
        val accountId = _currentAccountId.value ?: return
        val account = accountService.accountById(accountId) ?: return
        _unlockedPresets.value = account.unlockedPresets.toSet()
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val gold = SupabaseMarketRepository.currencyBalance(characterId).getOrNull() ?: 0L
            val gems = SupabaseMarketRepository.gemsBalance(characterId).getOrNull() ?: 0L
            _currency.value = gold to gems
        }
    }'''
results.append(guarded_replace(path, old, new, "refreshCurrency reads gems from server"))

# ---------------------------------------------------------
# 3b. GameViewModel.kt - creditPremiumCurrency + purchasePreset + grantTestGems -> grantGemsAsModerator
# ---------------------------------------------------------
old = '''    fun creditPremiumCurrency(bundleId: String) {
        val accountId = _currentAccountId.value ?: return
        val bundle = CurrencyBundleCatalog.find(bundleId) ?: return
        val result = accountService.addCurrency(accountId, bundle.premiumCurrencyGranted)
        if (result is ServiceResult.Failure) {
            _premiumActionError.value = result.reason
            return
        }
        _premiumActionError.value = null
        refreshCurrency()
        saveGame()
    }

    fun purchasePreset(presetId: String) {
        val accountId = _currentAccountId.value ?: return
        val result = accountService.purchasePreset(accountId, presetId)
        if (result is ServiceResult.Failure) {
            _premiumActionError.value = result.reason
            return
        }
        _premiumActionError.value = null
        refreshCurrency()
        saveGame()
    }

    // Moderator/testing tool only - credits the currently logged-in account
    // directly, bypassing Play Billing entirely. Does NOT target other
    // players' accounts (this app's Account/AccountService layer is local
    // per-device, not a live server-side directory).
    fun grantTestGems(amount: Long) {
        val accountId = _currentAccountId.value ?: return
        val result = accountService.addCurrency(accountId, amount)
        if (result is ServiceResult.Failure) {
            _premiumActionError.value = result.reason
            return
        }
        _premiumActionError.value = null
        refreshCurrency()
        saveGame()
    }'''
new = '''    fun creditPremiumCurrency(bundleId: String) {
        val bundle = CurrencyBundleCatalog.find(bundleId) ?: return
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseMarketRepository.creditGems(characterId, bundle.premiumCurrencyGranted)
            result.onFailure { _premiumActionError.value = it.message ?: it.toString() }
            result.onSuccess {
                _premiumActionError.value = null
                refreshCurrency()
                saveGame()
            }
        }
    }

    fun purchasePreset(presetId: String) {
        val accountId = _currentAccountId.value ?: return
        val characterId = _currentSupabaseCharacterId.value ?: return
        val account = accountService.accountById(accountId) ?: return
        if (presetId in account.unlockedPresets) {
            _premiumActionError.value = "Already unlocked."
            return
        }
        val preset = PremiumPresetCatalog.find(presetId) ?: return
        viewModelScope.launch {
            val spendResult = SupabaseMarketRepository.spendGems(characterId, preset.gemCost)
            spendResult.onFailure { _premiumActionError.value = it.message ?: it.toString() }
            spendResult.onSuccess {
                val result = accountService.unlockPreset(accountId, presetId)
                if (result is ServiceResult.Failure) {
                    _premiumActionError.value = result.reason
                    return@onSuccess
                }
                _premiumActionError.value = null
                refreshCurrency()
                saveGame()
            }
        }
    }

    // Moderator tool - grants Gems to ANY player by their Supabase character
    // id, via the server-authoritative admin_grant_gems RPC (SECURITY
    // DEFINER, independently re-checks caller_is_moderator() server-side,
    // same pattern as muteCharacterAsModerator/unmuteCharacterAsModerator
    // above). Replaces the old self-only grantTestGems, which only touched
    // the local logged-in account's in-memory Account.premiumCurrency and
    // never actually reached other players.
    fun grantGemsAsModerator(characterId: String, amount: Long, reason: String) {
        viewModelScope.launch {
            SupabaseModerationRepository.grantGems(characterId, amount, reason)
        }
    }'''
results.append(guarded_replace(path, old, new, "creditPremiumCurrency/purchasePreset server-side + grantGemsAsModerator"))

# ---------------------------------------------------------
# 4. ModerationScreen.kt - ManualGrantGemsSection targets any character
# ---------------------------------------------------------
path = BASE + "ModerationScreen.kt"
old = '''private fun ManualGrantGemsSection(
    onGrantGems: (Long) -> Unit
) {
    var amountText by remember { mutableStateOf("500") }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(12.dp)
    ) {
        Text(text = "Grant Gems (testing only - credits your own logged-in account)", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = amountText,
            onValueChange = { input -> if (input.all { it.isDigit() }) amountText = input },
            label = { Text(text = "Amount") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = {
                val amount = amountText.toLongOrNull()
                if (amount != null && amount > 0) {
                    onGrantGems(amount)
                }
            }
        ) {
            Text(text = "Grant Gems")
        }
    }
}'''
new = '''private fun ManualGrantGemsSection(
    onGrantGems: (String, Long, String) -> Unit
) {
    var characterId by remember { mutableStateOf("") }
    var amountText by remember { mutableStateOf("500") }
    var reason by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(12.dp)
    ) {
        Text(text = "Grant Gems", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = characterId,
            onValueChange = { characterId = it },
            label = { Text(text = "Character ID") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = amountText,
            onValueChange = { input -> if (input.all { it.isDigit() }) amountText = input },
            label = { Text(text = "Amount") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = reason,
            onValueChange = { reason = it },
            label = { Text(text = "Reason") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = {
                val amount = amountText.toLongOrNull()
                if (amount != null && amount > 0 && characterId.isNotBlank() && reason.isNotBlank()) {
                    onGrantGems(characterId, amount, reason)
                }
            }
        ) {
            Text(text = "Grant Gems")
        }
    }
}'''
results.append(guarded_replace(path, old, new, "ManualGrantGemsSection targets any character"))

# ---------------------------------------------------------
# 5. MainActivity.kt - onGrantGems wiring
# ---------------------------------------------------------
path = BASE + "MainActivity.kt"
old = '''                                ModerationScreen(
                                    state = moderation,
                                    onResolveReport = { id, action -> gameViewModel.resolveReport(id, action) },
                                    onResolveAppeal = { id, grant, notes -> gameViewModel.resolveAppeal(id, grant, notes) },
                                    onMuteCharacter = { id, dur, reason -> gameViewModel.muteCharacterAsModerator(id, dur, reason) },
                                    onUnmuteCharacter = { id -> gameViewModel.unmuteCharacterAsModerator(id) },
                                    onGrantGems = { amount -> gameViewModel.grantTestGems(amount) }
                                )'''
new = '''                                ModerationScreen(
                                    state = moderation,
                                    onResolveReport = { id, action -> gameViewModel.resolveReport(id, action) },
                                    onResolveAppeal = { id, grant, notes -> gameViewModel.resolveAppeal(id, grant, notes) },
                                    onMuteCharacter = { id, dur, reason -> gameViewModel.muteCharacterAsModerator(id, dur, reason) },
                                    onUnmuteCharacter = { id -> gameViewModel.unmuteCharacterAsModerator(id) },
                                    onGrantGems = { id, amount, reason -> gameViewModel.grantGemsAsModerator(id, amount, reason) }
                                )'''
results.append(guarded_replace(path, old, new, "onGrantGems passes characterId/reason"))

# ---------------------------------------------------------
# 6. AccountCharacterSystem.kt - add unlockPreset (local-only, no currency touch)
# ---------------------------------------------------------
path = BASE + "AccountCharacterSystem.kt"
old = '''    fun purchasePreset(accountId: String, presetId: String): ServiceResult<Account> {
        val account = accountsById[accountId] ?: return ServiceResult.Failure("Account not found.")
        if (presetId in account.unlockedPresets) return ServiceResult.Failure("Already unlocked.")
        val preset = PremiumPresetCatalog.find(presetId) ?: return ServiceResult.Failure("Unknown preset.")
        if (account.premiumCurrency < preset.gemCost) return ServiceResult.Failure("Not enough Gems.")
        account.premiumCurrency -= preset.gemCost
        account.unlockedPresets.add(presetId)
        return ServiceResult.Success(account)
    }'''
new = '''    fun purchasePreset(accountId: String, presetId: String): ServiceResult<Account> {
        val account = accountsById[accountId] ?: return ServiceResult.Failure("Account not found.")
        if (presetId in account.unlockedPresets) return ServiceResult.Failure("Already unlocked.")
        val preset = PremiumPresetCatalog.find(presetId) ?: return ServiceResult.Failure("Unknown preset.")
        if (account.premiumCurrency < preset.gemCost) return ServiceResult.Failure("Not enough Gems.")
        account.premiumCurrency -= preset.gemCost
        account.unlockedPresets.add(presetId)
        return ServiceResult.Success(account)
    }

    // Local-only preset unlock, used once currency has already been spent
    // server-side via SupabaseMarketRepository.spendGems (see
    // GameViewModel.purchasePreset). Does not touch premiumCurrency - that
    // field is a vestige of the old local-only gem flow and is no longer
    // the source of truth for gem balances.
    fun unlockPreset(accountId: String, presetId: String): ServiceResult<Account> {
        val account = accountsById[accountId] ?: return ServiceResult.Failure("Account not found.")
        if (presetId in account.unlockedPresets) return ServiceResult.Failure("Already unlocked.")
        val preset = PremiumPresetCatalog.find(presetId) ?: return ServiceResult.Failure("Unknown preset.")
        account.unlockedPresets.add(presetId)
        return ServiceResult.Success(account)
    }'''
results.append(guarded_replace(path, old, new, "add unlockPreset to AccountService"))

print()
print("=== Brace balance check ===")
for rel in [
    "SupabaseModerationRepository.kt",
    "SupabaseMarketRepository.kt",
    "GameViewModel.kt",
    "ModerationScreen.kt",
    "MainActivity.kt",
    "AccountCharacterSystem.kt",
]:
    check_braces(BASE + rel)

if not all(results):
    print()
    print("One or more edits FAILED - review output above before committing.")
    sys.exit(1)

print()
print("All edits applied successfully.")
