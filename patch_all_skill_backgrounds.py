import pathlib

account_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/AccountCharacterSystem.kt")
monetization_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/MonetizationSystem.kt")
gamestate_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/GameStateRepository.kt")
gvm_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")

account_text = account_path.read_text()
monetization_text = monetization_path.read_text()
gamestate_text = gamestate_path.read_text()
gvm_text = gvm_path.read_text()

errors = []


def apply_edit(text, old, new, marker, label, errors):
    """marker: a substring that only exists once the edit has already landed.
    Checked first so appending-style edits (where old is a prefix of new) don't
    get re-applied on a second run."""
    if text.count(marker) >= 1:
        return text, False  # already applied
    count_old = text.count(old)
    if count_old == 1:
        return text.replace(old, new), True
    errors.append(f"{label}: expected exactly 1 match of old block (and marker absent), found old={count_old}")
    return text, False


# ============================================================
# AccountCharacterSystem.kt
# ============================================================

acc_old_1 = """    var subscriptionTier: SubscriptionTier = SubscriptionTier.NONE,
    var premiumCurrency: Long = 0
) {"""
acc_new_1 = """    var subscriptionTier: SubscriptionTier = SubscriptionTier.NONE,
    var premiumCurrency: Long = 0,
    var unlockedPresets: MutableSet<String> = mutableSetOf()
) {"""
account_text, c1 = apply_edit(account_text, acc_old_1, acc_new_1, "var unlockedPresets: MutableSet<String>", "Account data class", errors)

acc_old_2 = """data class AccountExport(
    val id: String, val email: String, val username: String, val passwordHash: String, val passwordSalt: String,
    val createdAt: String, val lastLoginAt: String, val ageBracket: String, val region: String,
    val isBanned: Boolean, val banReason: String?, val mutedUntil: String?,
    val subscriptionTier: String, val premiumCurrency: Long
)"""
acc_new_2 = """data class AccountExport(
    val id: String, val email: String, val username: String, val passwordHash: String, val passwordSalt: String,
    val createdAt: String, val lastLoginAt: String, val ageBracket: String, val region: String,
    val isBanned: Boolean, val banReason: String?, val mutedUntil: String?,
    val subscriptionTier: String, val premiumCurrency: Long,
    val unlockedPresets: String = ""
)"""
account_text, c2 = apply_edit(account_text, acc_old_2, acc_new_2, 'val unlockedPresets: String = ""', "AccountExport data class", errors)

acc_old_3 = """    fun exportAllAccounts(): List<AccountExport> = accountsById.values.map {
        AccountExport(
            it.id, it.email, it.username, it.exposePasswordHashForExport(), it.exposePasswordSaltForExport(),
            it.createdAt.toString(), it.lastLoginAt.toString(), it.ageBracket.name, it.region,
            it.isBanned, it.banReason, it.mutedUntil?.toString(),
            it.subscriptionTier.name, it.premiumCurrency
        )
    }"""
acc_new_3 = """    fun exportAllAccounts(): List<AccountExport> = accountsById.values.map {
        AccountExport(
            it.id, it.email, it.username, it.exposePasswordHashForExport(), it.exposePasswordSaltForExport(),
            it.createdAt.toString(), it.lastLoginAt.toString(), it.ageBracket.name, it.region,
            it.isBanned, it.banReason, it.mutedUntil?.toString(),
            it.subscriptionTier.name, it.premiumCurrency,
            it.unlockedPresets.joinToString(",")
        )
    }"""
account_text, c3 = apply_edit(account_text, acc_old_3, acc_new_3, "it.unlockedPresets.joinToString", "exportAllAccounts()", errors)

acc_old_4 = """    fun restoreAccount(export: AccountExport) {
        val account = Account(
            id = export.id, email = export.email, username = export.username,
            passwordHash = export.passwordHash, passwordSalt = export.passwordSalt,
            createdAt = Instant.parse(export.createdAt), lastLoginAt = Instant.parse(export.lastLoginAt),
            ageBracket = AgeBracket.valueOf(export.ageBracket), region = export.region,
            isBanned = export.isBanned, banReason = export.banReason,
            mutedUntil = export.mutedUntil?.let { Instant.parse(it) },
            subscriptionTier = SubscriptionTier.valueOf(export.subscriptionTier),
            premiumCurrency = export.premiumCurrency
        )
        accountsById[account.id] = account
        accountsByUsername[account.username.lowercase()] = account.id
        accountsByEmail[account.email.lowercase()] = account.id
    }"""
acc_new_4 = """    fun restoreAccount(export: AccountExport) {
        val account = Account(
            id = export.id, email = export.email, username = export.username,
            passwordHash = export.passwordHash, passwordSalt = export.passwordSalt,
            createdAt = Instant.parse(export.createdAt), lastLoginAt = Instant.parse(export.lastLoginAt),
            ageBracket = AgeBracket.valueOf(export.ageBracket), region = export.region,
            isBanned = export.isBanned, banReason = export.banReason,
            mutedUntil = export.mutedUntil?.let { Instant.parse(it) },
            subscriptionTier = SubscriptionTier.valueOf(export.subscriptionTier),
            premiumCurrency = export.premiumCurrency,
            unlockedPresets = export.unlockedPresets.split(",").filter { it.isNotBlank() }.toMutableSet()
        )
        accountsById[account.id] = account
        accountsByUsername[account.username.lowercase()] = account.id
        accountsByEmail[account.email.lowercase()] = account.id
    }"""
account_text, c4 = apply_edit(account_text, acc_old_4, acc_new_4, "unlockedPresets = export.unlockedPresets.split", "restoreAccount()", errors)

acc_old_5 = """    fun addCurrency(accountId: String, premium: Long = 0): ServiceResult<Account> {
        val account = accountsById[accountId] ?: return ServiceResult.Failure("Account not found.")
        if (premium < 0) return ServiceResult.Failure("Currency amounts cannot be negative.")
        account.premiumCurrency += premium
        return ServiceResult.Success(account)
    }"""
acc_new_5 = """    fun addCurrency(accountId: String, premium: Long = 0): ServiceResult<Account> {
        val account = accountsById[accountId] ?: return ServiceResult.Failure("Account not found.")
        if (premium < 0) return ServiceResult.Failure("Currency amounts cannot be negative.")
        account.premiumCurrency += premium
        return ServiceResult.Success(account)
    }

    fun purchasePreset(accountId: String, presetId: String): ServiceResult<Account> {
        val account = accountsById[accountId] ?: return ServiceResult.Failure("Account not found.")
        if (presetId in account.unlockedPresets) return ServiceResult.Failure("Already unlocked.")
        val preset = PremiumPresetCatalog.find(presetId) ?: return ServiceResult.Failure("Unknown preset.")
        if (account.premiumCurrency < preset.gemCost) return ServiceResult.Failure("Not enough Gems.")
        account.premiumCurrency -= preset.gemCost
        account.unlockedPresets.add(presetId)
        return ServiceResult.Success(account)
    }"""
account_text, c5 = apply_edit(account_text, acc_old_5, acc_new_5, "fun purchasePreset(accountId: String, presetId: String)", "AccountService.addCurrency/purchasePreset", errors)

# ============================================================
# MonetizationSystem.kt
# ============================================================

mon_old = """object CurrencyBundleCatalog {
    val bundles = listOf(
        CurrencyBundle(id = "bundle_small", realMoneyPriceUsd = 4.99, premiumCurrencyGranted = 500),
        CurrencyBundle(id = "bundle_medium", realMoneyPriceUsd = 9.99, premiumCurrencyGranted = 1100, bonusPercent = 10.0),
        CurrencyBundle(id = "bundle_large", realMoneyPriceUsd = 24.99, premiumCurrencyGranted = 3000, bonusPercent = 20.0)
    )

    fun find(bundleId: String): CurrencyBundle? = bundles.find { it.id == bundleId }
}"""
mon_new = """object CurrencyBundleCatalog {
    val bundles = listOf(
        CurrencyBundle(id = "bundle_small", realMoneyPriceUsd = 4.99, premiumCurrencyGranted = 500),
        CurrencyBundle(id = "bundle_medium", realMoneyPriceUsd = 9.99, premiumCurrencyGranted = 1100, bonusPercent = 10.0),
        CurrencyBundle(id = "bundle_large", realMoneyPriceUsd = 24.99, premiumCurrencyGranted = 3000, bonusPercent = 20.0)
    )

    fun find(bundleId: String): CurrencyBundle? = bundles.find { it.id == bundleId }
}

// =========================================================
// PREMIUM COSMETIC TEXT PRESETS (Gem-purchasable Settings presets)
// =========================================================

data class PremiumPreset(
    val id: String,
    val displayName: String,
    val gemCost: Long,
    val textColorArgb: Long,
    val outlineColorArgb: Long
)

object PremiumPresetCatalog {
    val presets = listOf(
        PremiumPreset(id = "preset_ember_glow", displayName = "Ember Glow", gemCost = 150, textColorArgb = 0xFFFFB86CL, outlineColorArgb = 0xFF8B0000L),
        PremiumPreset(id = "preset_arctic_shimmer", displayName = "Arctic Shimmer", gemCost = 150, textColorArgb = 0xFF9AEAFFL, outlineColorArgb = 0xFF00E5FFL),
        PremiumPreset(id = "preset_royal_amethyst", displayName = "Royal Amethyst", gemCost = 150, textColorArgb = 0xFFC77DFFL, outlineColorArgb = 0xFF7209B7L)
    )

    fun find(presetId: String): PremiumPreset? = presets.find { it.id == presetId }
}"""
monetization_text, c6 = apply_edit(monetization_text, mon_old, mon_new, "object PremiumPresetCatalog", "MonetizationSystem.kt PremiumPresetCatalog", errors)

# ============================================================
# GameStateRepository.kt
# ============================================================

gs_old_1 = """            obj.put("subscriptionTier", acc.subscriptionTier)
            obj.put("premiumCurrency", acc.premiumCurrency)
            accountsArray.put(obj)"""
gs_new_1 = """            obj.put("subscriptionTier", acc.subscriptionTier)
            obj.put("premiumCurrency", acc.premiumCurrency)
            obj.put("unlockedPresets", acc.unlockedPresets)
            accountsArray.put(obj)"""
gamestate_text, c7 = apply_edit(gamestate_text, gs_old_1, gs_new_1, 'obj.put("unlockedPresets"', "GameStateRepository.kt save()", errors)

gs_old_2 = """                    subscriptionTier = obj.getString("subscriptionTier"),
                    premiumCurrency = obj.getLong("premiumCurrency")
                )
            )
        }

        val characters = mutableListOf<CharacterExport>()"""
gs_new_2 = """                    subscriptionTier = obj.getString("subscriptionTier"),
                    premiumCurrency = obj.getLong("premiumCurrency"),
                    unlockedPresets = obj.optString("unlockedPresets", "")
                )
            )
        }

        val characters = mutableListOf<CharacterExport>()"""
gamestate_text, c8 = apply_edit(gamestate_text, gs_old_2, gs_new_2, 'unlockedPresets = obj.optString("unlockedPresets"', "GameStateRepository.kt load()", errors)

# ============================================================
# GameViewModel.kt
# ============================================================

gvm_old_1 = """    private val _currency = MutableStateFlow(0L to 0L)
    val currency: StateFlow<Pair<Long, Long>> = _currency.asStateFlow()"""
gvm_new_1 = """    private val _currency = MutableStateFlow(0L to 0L)
    val currency: StateFlow<Pair<Long, Long>> = _currency.asStateFlow()

    private val _unlockedPresets = MutableStateFlow<Set<String>>(emptySet())
    val unlockedPresets: StateFlow<Set<String>> = _unlockedPresets.asStateFlow()

    private val _premiumActionError = MutableStateFlow<String?>(null)
    val premiumActionError: StateFlow<String?> = _premiumActionError.asStateFlow()"""
gvm_text, c9 = apply_edit(gvm_text, gvm_old_1, gvm_new_1, "_unlockedPresets = MutableStateFlow<Set<String>>", "GameViewModel.kt new StateFlows", errors)

gvm_old_2 = """    fun refreshCurrency() {
        val accountId = _currentAccountId.value ?: return
        val account = accountService.accountById(accountId) ?: return
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val gold = SupabaseMarketRepository.currencyBalance(characterId).getOrNull() ?: 0L
            _currency.value = gold to account.premiumCurrency
        }
    }"""
gvm_new_2 = """    fun refreshCurrency() {
        val accountId = _currentAccountId.value ?: return
        val account = accountService.accountById(accountId) ?: return
        _unlockedPresets.value = account.unlockedPresets.toSet()
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val gold = SupabaseMarketRepository.currencyBalance(characterId).getOrNull() ?: 0L
            _currency.value = gold to account.premiumCurrency
        }
    }

    fun creditPremiumCurrency(bundleId: String) {
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
    }"""
gvm_text, c10 = apply_edit(gvm_text, gvm_old_2, gvm_new_2, "fun creditPremiumCurrency(bundleId: String)", "GameViewModel.kt refreshCurrency + new functions", errors)

if errors:
    raise SystemExit(
        "PATCH A FAILED: one or more expected blocks did not match. No changes made to any file.\n"
        + "\n".join(f"  - {e}" for e in errors)
    )

account_path.write_text(account_text)
monetization_path.write_text(monetization_text)
gamestate_path.write_text(gamestate_text)
gvm_path.write_text(gvm_text)

print("Patch A applied successfully:")
print("  - AccountCharacterSystem.kt: Account.unlockedPresets field, AccountExport threading, AccountService.purchasePreset")
print("  - MonetizationSystem.kt: PremiumPreset + PremiumPresetCatalog (3 presets, 150 Gems each)")
print("  - GameStateRepository.kt: unlockedPresets save/load (backward-compatible with old saves)")
print("  - GameViewModel.kt: unlockedPresets/premiumActionError StateFlows, creditPremiumCurrency(), purchasePreset()")
