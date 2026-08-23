"""
Fix: Login only ever checked the local in-memory account store, with no
Supabase fallback at all - so after local data loss, there was no way
to actually log back into a real account via the Login button (only
Signup happened to work, because syncSupabaseAuth already ran there).

This adds: on local login failure, attempt Supabase sign-in with the
same email/password. If that succeeds, find the existing character for
that profile (via get_or_create_character - the SQL fix means passing
a fresh placeholder local id correctly returns the existing character
rather than creating a new one), download its cloud save, and restore
it - recreating the local account/character from the recovered data.
If there's no cloud backup for that account (nothing was ever
uploaded), surface a clear message via the existing _characterSyncError
state rather than silently failing or creating a blank account.

Guarded with asserts.
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(BASE, "GameViewModel.kt")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = (
    "fun login(email: String, password: String): ServiceResult<Account> {\n"
    "    val result = accountService.login(email, password)\n"
    "    if (result is ServiceResult.Success) {\n"
    "        sessionManager.saveSession(result.value.id)\n"
    "            _currentAccountId.value = result.value.id\n"
    "            refreshCurrency()\n"
    "            syncSupabaseAuth(email, password, isNewAccount = false)\n"
    "    }\n"
    "    return result\n"
    "}\n"
)
new = (
    "fun login(email: String, password: String): ServiceResult<Account> {\n"
    "    val result = accountService.login(email, password)\n"
    "    if (result is ServiceResult.Success) {\n"
    "        sessionManager.saveSession(result.value.id)\n"
    "            _currentAccountId.value = result.value.id\n"
    "            refreshCurrency()\n"
    "            syncSupabaseAuth(email, password, isNewAccount = false)\n"
    "    } else {\n"
    "        attemptCloudRecoveryLogin(email, password)\n"
    "    }\n"
    "    return result\n"
    "}\n"
    "\n"
    "private fun attemptCloudRecoveryLogin(email: String, password: String) {\n"
    "    viewModelScope.launch {\n"
    "        try {\n"
    "            auth.signInWith(io.github.jan.supabase.auth.providers.builtin.Email) {\n"
    "                this.email = email\n"
    "                this.password = password\n"
    "            }\n"
    "        } catch (e: Exception) {\n"
    "            _characterSyncError.value = \"No local account found, and no matching cloud account either.\"\n"
    "            return@launch\n"
    "        }\n"
    "\n"
    "        val placeholderLocalId = java.util.UUID.randomUUID().toString()\n"
    "        val charResult = SupabaseCharacterRepository.getOrCreateCharacter(placeholderLocalId, \"Recovered\")\n"
    "        val supabaseCharacterId = charResult.getOrNull()\n"
    "        if (supabaseCharacterId == null) {\n"
    "            _characterSyncError.value = \"Found a cloud account but couldn't sync a character to it.\"\n"
    "            return@launch\n"
    "        }\n"
    "\n"
    "        val cloudJson = SupabaseCharacterRepository.downloadCharacterSave(supabaseCharacterId).getOrNull()\n"
    "        if (cloudJson == null) {\n"
    "            _characterSyncError.value = \"This account has no cloud backup saved yet - its local data can't be recovered.\"\n"
    "            return@launch\n"
    "        }\n"
    "\n"
    "        repository.overwriteRawJson(cloudJson)\n"
    "        val recovered = repository.load()\n"
    "        if (recovered == null) {\n"
    "            _characterSyncError.value = \"Recovered cloud data was corrupted or empty.\"\n"
    "            return@launch\n"
    "        }\n"
    "\n"
    "        recovered.accounts.forEach { accountService.restoreAccount(it) }\n"
    "        recovered.characters.forEach { accountService.restoreCharacter(it) }\n"
    "        recovered.skills.forEach { progressionService.restoreSkill(it) }\n"
    "        recovered.skillingQueues.forEach { offlineIdleService.restoreSkillingQueue(it) }\n"
    "        recovered.craftingQueues.forEach { offlineIdleService.restoreCraftingQueue(it) }\n"
    "        recovered.lastSeen.forEach { offlineIdleService.restoreLastSeen(it) }\n"
    "        recovered.inventoryItems.forEach { inventoryService.restoreItem(it) }\n"
    "        recovered.equippedSlots.forEach { inventoryService.restoreEquipped(it) }\n"
    "        recovered.loadoutSettings.forEach { inventoryService.restoreLoadoutSettings(it) }\n"
    "        recovered.marketAccounts.forEach { marketService.restoreAccount(it) }\n"
    "        recovered.marketOrders.forEach { marketService.restoreOrder(it) }\n"
    "        recovered.marketPriceHistory.forEach { marketService.restorePriceHistoryEntry(it) }\n"
    "\n"
    "        val recoveredAccount = recovered.accounts.firstOrNull { it.email.equals(email, ignoreCase = true) }\n"
    "        if (recoveredAccount == null) {\n"
    "            _characterSyncError.value = \"Recovered cloud data but couldn't match it to this email.\"\n"
    "            return@launch\n"
    "        }\n"
    "\n"
    "        sessionManager.saveSession(recoveredAccount.id)\n"
    "        _currentAccountId.value = recoveredAccount.id\n"
    "        refreshCurrency()\n"
    "        _currentSupabaseCharacterId.value = supabaseCharacterId\n"
    "        _characterSyncError.value = null\n"
    "\n"
    "        val recoveredCharacter = recovered.characters.firstOrNull { it.accountId == recoveredAccount.id }\n"
    "        if (recoveredCharacter != null) {\n"
    "            _currentCharacterId.value = recoveredCharacter.id\n"
    "        }\n"
    "    }\n"
    "}\n"
)

assert old in content, "login() anchor not found"
assert content.count(old) == 1, "login() anchor not unique"
content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched GameViewModel.kt: Login now falls back to Supabase cloud recovery when local login fails.")
