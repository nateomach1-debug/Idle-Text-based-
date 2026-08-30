path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor = '''    fun selectCharacter(characterId: String) {
        _currentCharacterId.value = characterId

        val selectedCharacter = accountService.charactersFor(_currentAccountId.value ?: "").firstOrNull { it.id == characterId }
        if (selectedCharacter != null) {
            viewModelScope.launch {
                val authState = withTimeoutOrNull(10_000L) {
                    supabaseAuthState.first { it != SupabaseAuthState.SIGNING_IN }
                }
                if (authState != SupabaseAuthState.SIGNED_IN) {
                    _characterSyncError.value = "Not signed in to multiplayer services yet - character sync will retry on next action."
                    return@launch
                }
                val result = SupabaseCharacterRepository.getOrCreateCharacter(characterId, selectedCharacter.displayName)
                result.onFailure { _characterSyncError.value = it.message ?: it.toString() }
                result.onSuccess { _characterSyncError.value = null }
                _currentSupabaseCharacterId.value = result.getOrNull()
                val supabaseCharacterId = result.getOrNull()
                if (supabaseCharacterId != null) {
                    val remoteLocalId = SupabaseCharacterRepository.getCharacterLocalId(supabaseCharacterId).getOrNull()
                    if (remoteLocalId != null && remoteLocalId != characterId) {
                        // The server returned an EXISTING character from a different
                        // device/install, not the one just created locally - recover
                        // its real save instead of keeping the throwaway new one.
                        val cloudJson = SupabaseCharacterRepository.downloadCharacterSave(supabaseCharacterId).getOrNull()
                        if (cloudJson != null) {
                            repository.overwriteRawJson(cloudJson)
                            val recovered = repository.load()
                            if (recovered != null) {
                                recovered.accounts.forEach { accountService.restoreAccount(it) }
                                recovered.characters.forEach { accountService.restoreCharacter(it) }
                                recovered.skills.forEach { progressionService.restoreSkill(it) }
                                recovered.skillingQueues.forEach { offlineIdleService.restoreSkillingQueue(it) }
                                recovered.craftingQueues.forEach { offlineIdleService.restoreCraftingQueue(it) }
                                recovered.lastSeen.forEach { offlineIdleService.restoreLastSeen(it) }
                                recovered.lastSaleCheck.forEach { offlineIdleService.restoreLastSaleCheck(it) }
                                recovered.inventoryItems.forEach { inventoryService.restoreItem(it) }
                                recovered.equippedSlots.forEach { inventoryService.restoreEquipped(it) }
                                recovered.loadoutSettings.forEach { inventoryService.restoreLoadoutSettings(it) }
                                recovered.marketAccounts.forEach { marketService.restoreAccount(it) }
                                recovered.marketOrders.forEach { marketService.restoreOrder(it) }
                                recovered.marketPriceHistory.forEach { marketService.restorePriceHistoryEntry(it) }
                                recovered.combatSessions.forEach { combatService.restoreSession(it) }
                                recovered.offlineCombatQueues.forEach { offlineIdleService.restoreOfflineCombatQueue(it) }
                                _currentCharacterId.value = remoteLocalId
                                val recoveredCharacter = recovered.characters.firstOrNull { it.id == remoteLocalId }
                                if (recoveredCharacter != null) {
                                    _currentAccountId.value = recoveredCharacter.accountId
                                }
                                resolveOfflineRewardsAndSync(remoteLocalId)
                            }
                        }
                    }
                }
            }
        } else {
            _characterSyncError.value = "selectedCharacter was null - accountId=${_currentAccountId.value}, characterId=$characterId"
        }

        resolveOfflineRewardsAndSync(characterId)
    }'''
count = content.count(anchor)
assert count == 1, f"Expected 1 match for anchor, found {count}."
replacement = '''    fun selectCharacter(characterId: String) {
        _currentCharacterId.value = characterId

        val selectedCharacter = accountService.charactersFor(_currentAccountId.value ?: "").firstOrNull { it.id == characterId }
        if (selectedCharacter != null) {
            viewModelScope.launch {
                val authState = withTimeoutOrNull(10_000L) {
                    supabaseAuthState.first { it != SupabaseAuthState.SIGNING_IN }
                }
                if (authState != SupabaseAuthState.SIGNED_IN) {
                    _characterSyncError.value = "Not signed in to multiplayer services yet - character sync will retry on next action."
                    resolveOfflineRewardsAndSync(characterId)
                    return@launch
                }
                val result = SupabaseCharacterRepository.getOrCreateCharacter(characterId, selectedCharacter.displayName)
                result.onFailure { _characterSyncError.value = it.message ?: it.toString() }
                result.onSuccess { _characterSyncError.value = null }
                _currentSupabaseCharacterId.value = result.getOrNull()
                val supabaseCharacterId = result.getOrNull()
                var recoveredToRemoteId: String? = null
                if (supabaseCharacterId != null) {
                    val remoteLocalId = SupabaseCharacterRepository.getCharacterLocalId(supabaseCharacterId).getOrNull()
                    if (remoteLocalId != null && remoteLocalId != characterId) {
                        // The server returned an EXISTING character from a different
                        // device/install, not the one just created locally - recover
                        // its real save instead of keeping the throwaway new one.
                        val cloudJson = SupabaseCharacterRepository.downloadCharacterSave(supabaseCharacterId).getOrNull()
                        if (cloudJson != null) {
                            repository.overwriteRawJson(cloudJson)
                            val recovered = repository.load()
                            if (recovered != null) {
                                recovered.accounts.forEach { accountService.restoreAccount(it) }
                                recovered.characters.forEach { accountService.restoreCharacter(it) }
                                recovered.skills.forEach { progressionService.restoreSkill(it) }
                                recovered.skillingQueues.forEach { offlineIdleService.restoreSkillingQueue(it) }
                                recovered.craftingQueues.forEach { offlineIdleService.restoreCraftingQueue(it) }
                                recovered.lastSeen.forEach { offlineIdleService.restoreLastSeen(it) }
                                recovered.lastSaleCheck.forEach { offlineIdleService.restoreLastSaleCheck(it) }
                                recovered.inventoryItems.forEach { inventoryService.restoreItem(it) }
                                recovered.equippedSlots.forEach { inventoryService.restoreEquipped(it) }
                                recovered.loadoutSettings.forEach { inventoryService.restoreLoadoutSettings(it) }
                                recovered.marketAccounts.forEach { marketService.restoreAccount(it) }
                                recovered.marketOrders.forEach { marketService.restoreOrder(it) }
                                recovered.marketPriceHistory.forEach { marketService.restorePriceHistoryEntry(it) }
                                recovered.combatSessions.forEach { combatService.restoreSession(it) }
                                recovered.offlineCombatQueues.forEach { offlineIdleService.restoreOfflineCombatQueue(it) }
                                _currentCharacterId.value = remoteLocalId
                                val recoveredCharacter = recovered.characters.firstOrNull { it.id == remoteLocalId }
                                if (recoveredCharacter != null) {
                                    _currentAccountId.value = recoveredCharacter.accountId
                                }
                                recoveredToRemoteId = remoteLocalId
                            }
                        }
                    }
                }
                // Only one of these ever fires per selection: whichever character id
                // turned out to be correct once the async cloud-recovery check above
                // finished. Previously an immediate, unconditional call fired outside
                // this coroutine entirely, racing this check - it would briefly show
                // an offline-progress popup built from the wrong (pre-recovery)
                // character before this corrected one silently replaced it.
                resolveOfflineRewardsAndSync(recoveredToRemoteId ?: characterId)
            }
        } else {
            _characterSyncError.value = "selectedCharacter was null - accountId=${_currentAccountId.value}, characterId=$characterId"
            resolveOfflineRewardsAndSync(characterId)
        }
    }'''
content = content.replace(anchor, replacement, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("patch_fix_duplicate_offline_popup.py applied cleanly.")
