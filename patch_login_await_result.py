"""
Fix: login() showed a synchronous local-failure error immediately, while
the actual Supabase cloud-recovery attempt ran fire-and-forget in the
background afterward - so users could see a scary "no account found"
error and give up, even when recovery was about to succeed a moment
later (confirmed this happened to a friend's account that DID have
real Supabase history).

Fix: convert login() to a suspend function that actually awaits the
cloud recovery attempt and returns the REAL final result, instead of
returning the local failure immediately and letting recovery mutate
state asynchronously afterward. The UI's onLogin callback now launches
a coroutine (via rememberCoroutineScope, already available through the
existing androidx.compose.runtime.* wildcard import) so it can call the
suspend login() and only show a message once the true outcome is known.

Touches: GameViewModel.kt, MainActivity.kt. Guarded with asserts.
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"

# ---------------------------------------------------------------
# 1. GameViewModel.kt - convert login() and attemptCloudRecoveryLogin()
#    to suspend functions that return the real final result.
# ---------------------------------------------------------------
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
    "    } else {\n"
    "        attemptCloudRecoveryLogin(email, password)\n"
    "    }\n"
    "    return result\n"
    "}\n"
    "\n"
    "private fun attemptCloudRecoveryLogin(email: String, password: String) {\n"
    "    viewModelScope.launch {\n"
    "        try {\n"
    "            SupabaseClientProvider.client.auth.signInWith(io.github.jan.supabase.auth.providers.builtin.Email) {\n"
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

new = (
    "suspend fun login(email: String, password: String): ServiceResult<Account> {\n"
    "    val result = accountService.login(email, password)\n"
    "    if (result is ServiceResult.Success) {\n"
    "        sessionManager.saveSession(result.value.id)\n"
    "            _currentAccountId.value = result.value.id\n"
    "            refreshCurrency()\n"
    "            syncSupabaseAuth(email, password, isNewAccount = false)\n"
    "        return result\n"
    "    }\n"
    "    return attemptCloudRecoveryLogin(email, password)\n"
    "}\n"
    "\n"
    "private suspend fun attemptCloudRecoveryLogin(email: String, password: String): ServiceResult<Account> {\n"
    "    try {\n"
    "        SupabaseClientProvider.client.auth.signInWith(io.github.jan.supabase.auth.providers.builtin.Email) {\n"
    "            this.email = email\n"
    "            this.password = password\n"
    "        }\n"
    "    } catch (e: Exception) {\n"
    "        return ServiceResult.Failure(\"No local account found, and no matching cloud account either.\")\n"
    "    }\n"
    "\n"
    "    val placeholderLocalId = java.util.UUID.randomUUID().toString()\n"
    "    val charResult = SupabaseCharacterRepository.getOrCreateCharacter(placeholderLocalId, \"Recovered\")\n"
    "    val supabaseCharacterId = charResult.getOrNull()\n"
    "        ?: return ServiceResult.Failure(\"Found a cloud account but couldn't sync a character to it.\")\n"
    "\n"
    "    val cloudJson = SupabaseCharacterRepository.downloadCharacterSave(supabaseCharacterId).getOrNull()\n"
    "        ?: return ServiceResult.Failure(\"This account has no cloud backup saved yet - its local data can't be recovered.\")\n"
    "\n"
    "    repository.overwriteRawJson(cloudJson)\n"
    "    val recovered = repository.load()\n"
    "        ?: return ServiceResult.Failure(\"Recovered cloud data was corrupted or empty.\")\n"
    "\n"
    "    recovered.accounts.forEach { accountService.restoreAccount(it) }\n"
    "    recovered.characters.forEach { accountService.restoreCharacter(it) }\n"
    "    recovered.skills.forEach { progressionService.restoreSkill(it) }\n"
    "    recovered.skillingQueues.forEach { offlineIdleService.restoreSkillingQueue(it) }\n"
    "    recovered.craftingQueues.forEach { offlineIdleService.restoreCraftingQueue(it) }\n"
    "    recovered.lastSeen.forEach { offlineIdleService.restoreLastSeen(it) }\n"
    "    recovered.inventoryItems.forEach { inventoryService.restoreItem(it) }\n"
    "    recovered.equippedSlots.forEach { inventoryService.restoreEquipped(it) }\n"
    "    recovered.loadoutSettings.forEach { inventoryService.restoreLoadoutSettings(it) }\n"
    "    recovered.marketAccounts.forEach { marketService.restoreAccount(it) }\n"
    "    recovered.marketOrders.forEach { marketService.restoreOrder(it) }\n"
    "    recovered.marketPriceHistory.forEach { marketService.restorePriceHistoryEntry(it) }\n"
    "\n"
    "    val recoveredAccount = recovered.accounts.firstOrNull { it.email.equals(email, ignoreCase = true) }\n"
    "        ?: return ServiceResult.Failure(\"Recovered cloud data but couldn't match it to this email.\")\n"
    "\n"
    "    sessionManager.saveSession(recoveredAccount.id)\n"
    "    _currentAccountId.value = recoveredAccount.id\n"
    "    refreshCurrency()\n"
    "    _currentSupabaseCharacterId.value = supabaseCharacterId\n"
    "    _characterSyncError.value = null\n"
    "\n"
    "    val recoveredCharacter = recovered.characters.firstOrNull { it.accountId == recoveredAccount.id }\n"
    "    if (recoveredCharacter != null) {\n"
    "        _currentCharacterId.value = recoveredCharacter.id\n"
    "    }\n"
    "\n"
    "    return ServiceResult.Success(recoveredAccount)\n"
    "}\n"
)

assert old in content, "login()/attemptCloudRecoveryLogin anchor not found in GameViewModel.kt"
assert content.count(old) == 1, "anchor not unique in GameViewModel.kt"
content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Patched GameViewModel.kt")

# ---------------------------------------------------------------
# 2. MainActivity.kt - launch a coroutine so onLogin can await the
#    suspend login() and only show a message once the real result
#    is known.
# ---------------------------------------------------------------
path = os.path.join(BASE, "MainActivity.kt")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old_import = "import java.time.Duration\n"
new_import = "import java.time.Duration\nimport kotlinx.coroutines.launch\n"
assert old_import in content, "Duration import anchor not found"
assert content.count(old_import) == 1, "Duration import anchor not unique"
content = content.replace(old_import, new_import)

old_callback = (
    "                onLogin = { email, password ->\n"
    "                    val result = gameViewModel.login(email, password)\n"
    "                    when (result) {\n"
    "                        is ServiceResult.Success -> {\n"
    "                            val chars = gameViewModel.accountService.charactersFor(result.value.id)\n"
    "                            flowState = if (chars.isEmpty()) AppFlowState.CharacterCreate else AppFlowState.CharacterSelect\n"
    "                            loginError = null\n"
    "                        }\n"
    "                        is ServiceResult.Failure -> loginError = result.reason\n"
    "                    }\n"
    "                },\n"
)
new_callback = (
    "                onLogin = { email, password ->\n"
    "                    loginCoroutineScope.launch {\n"
    "                        val result = gameViewModel.login(email, password)\n"
    "                        when (result) {\n"
    "                            is ServiceResult.Success -> {\n"
    "                                val chars = gameViewModel.accountService.charactersFor(result.value.id)\n"
    "                                flowState = if (chars.isEmpty()) AppFlowState.CharacterCreate else AppFlowState.CharacterSelect\n"
    "                                loginError = null\n"
    "                            }\n"
    "                            is ServiceResult.Failure -> loginError = result.reason\n"
    "                        }\n"
    "                    }\n"
    "                },\n"
)
assert old_callback in content, "onLogin callback anchor not found"
assert content.count(old_callback) == 1, "onLogin callback anchor not unique"
content = content.replace(old_callback, new_callback)

old_login_block_open = "        AppFlowState.Login -> {\n            LoginScreen(\n"
new_login_block_open = (
    "        AppFlowState.Login -> {\n"
    "            val loginCoroutineScope = rememberCoroutineScope()\n"
    "            LoginScreen(\n"
)
assert old_login_block_open in content, "AppFlowState.Login block-open anchor not found"
assert content.count(old_login_block_open) == 1, "AppFlowState.Login block-open anchor not unique"
content = content.replace(old_login_block_open, new_login_block_open)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Patched MainActivity.kt")

print("Both files patched successfully.")
