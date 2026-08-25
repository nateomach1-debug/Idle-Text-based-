GVM = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"

with open(GVM, "r", encoding="utf-8") as f:
    content = f.read()


def patch(old, new):
    global content
    count = content.count(old)
    assert count == 1, f"expected exactly 1 match, found {count} for:\n{old!r}"
    content = content.replace(old, new)
    print(f"OK: patched ({len(old)} -> {len(new)} chars)")


# 1. Replace the inline offline-reward block in selectCharacter with a call to
#    the new extracted function, and define that function right after.
old_block = """        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.SkillingQueue
        if (queue != null) {
            val result = offlineIdleService.resolveOfflineProgress(characterId)
            if (result is ServiceResult.Success && result.value.actionsCompleted > 0) {
                val skillType = SkillType.valueOf(queue.skillId)
                val action = ActionCatalog.find(skillType, queue.itemId)
                if (action != null) {
                    val xpEarned = action.xpPerAction * result.value.actionsCompleted
                    progressionService.grantXp(characterId, skillType, xpEarned)
                    inventoryService.inventoryFor(characterId).addItem(queue.itemId, result.value.actionsCompleted)
                    _offlineSummary.value = OfflineSummary(
                        awaySeconds = result.value.claimedElapsed.seconds,
                        skillActionName = action.displayName,
                        itemName = formatItemName(queue.itemId),
                        quantity = result.value.actionsCompleted,
                        xpEarned = xpEarned
                    )
                }
            }
        }

        val craftingQueue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.CraftingQueue
        if (craftingQueue != null) {
            val craftResult = offlineIdleService.resolveOfflineProgress(characterId)
            if (craftResult is ServiceResult.Success && craftResult.value.actionsCompleted > 0) {
                val batch = craftItems(characterId, craftingQueue.itemId, craftResult.value.actionsCompleted)
                if (batch.xpGranted > 0) {
                    _offlineSummary.value = OfflineSummary(
                        awaySeconds = craftResult.value.claimedElapsed.seconds,
                        skillActionName = "Craft " + formatItemName(craftingQueue.itemId),
                        itemName = formatItemName(craftingQueue.itemId),
                        quantity = batch.itemsProduced,
                        xpEarned = batch.xpGranted
                    )
                }
            }
        }

        offlineIdleService.recordLastSeen(characterId)
        skillActionProgressSeconds = 0
        craftActionProgressSeconds = 0
        refreshSkills()
        refreshInventory()
        refreshActiveQueue()

        if (marketService.accountFor(characterId) == null) {
            val character = accountService.charactersFor(_currentAccountId.value ?: "")
                .find { it.id == characterId }
            marketService.registerAccount(
                PlayerEconomyAccount(
                    characterId = characterId,
                    accountId = _currentAccountId.value ?: "",
                    isMainCharacter = character?.isMainCharacter ?: true,
                    currencyBalance = 0L
                )
            )
        }
        refreshCurrency()
        refreshMarketListings()
        refreshMyOrders()
    }

    fun startSkillAction(skillType: SkillType, itemId: String) {"""

new_block = """        resolveOfflineRewardsAndSync(characterId)
    }

    // Grants offline-progress rewards (skilling/crafting), records last-seen, and
    // syncs currency/market state for the given character. Extracted so it can be
    // re-run against a cloud-recovered character id after async recovery completes
    // (see selectCharacter) - a throwaway local character's offline queue is never
    // the "real" one in that scenario, so re-resolving against the recovered
    // character's actual data is the correct behavior, not just a race-condition
    // workaround.
    private fun resolveOfflineRewardsAndSync(characterId: String) {
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.SkillingQueue
        if (queue != null) {
            val result = offlineIdleService.resolveOfflineProgress(characterId)
            if (result is ServiceResult.Success && result.value.actionsCompleted > 0) {
                val skillType = SkillType.valueOf(queue.skillId)
                val action = ActionCatalog.find(skillType, queue.itemId)
                if (action != null) {
                    val xpEarned = action.xpPerAction * result.value.actionsCompleted
                    progressionService.grantXp(characterId, skillType, xpEarned)
                    inventoryService.inventoryFor(characterId).addItem(queue.itemId, result.value.actionsCompleted)
                    _offlineSummary.value = OfflineSummary(
                        awaySeconds = result.value.claimedElapsed.seconds,
                        skillActionName = action.displayName,
                        itemName = formatItemName(queue.itemId),
                        quantity = result.value.actionsCompleted,
                        xpEarned = xpEarned
                    )
                }
            }
        }

        val craftingQueue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.CraftingQueue
        if (craftingQueue != null) {
            val craftResult = offlineIdleService.resolveOfflineProgress(characterId)
            if (craftResult is ServiceResult.Success && craftResult.value.actionsCompleted > 0) {
                val batch = craftItems(characterId, craftingQueue.itemId, craftResult.value.actionsCompleted)
                if (batch.xpGranted > 0) {
                    _offlineSummary.value = OfflineSummary(
                        awaySeconds = craftResult.value.claimedElapsed.seconds,
                        skillActionName = "Craft " + formatItemName(craftingQueue.itemId),
                        itemName = formatItemName(craftingQueue.itemId),
                        quantity = batch.itemsProduced,
                        xpEarned = batch.xpGranted
                    )
                }
            }
        }

        offlineIdleService.recordLastSeen(characterId)
        skillActionProgressSeconds = 0
        craftActionProgressSeconds = 0
        refreshSkills()
        refreshInventory()
        refreshActiveQueue()

        if (marketService.accountFor(characterId) == null) {
            val character = accountService.charactersFor(_currentAccountId.value ?: "")
                .find { it.id == characterId }
            marketService.registerAccount(
                PlayerEconomyAccount(
                    characterId = characterId,
                    accountId = _currentAccountId.value ?: "",
                    isMainCharacter = character?.isMainCharacter ?: true,
                    currencyBalance = 0L
                )
            )
        }
        refreshCurrency()
        refreshMarketListings()
        refreshMyOrders()
    }

    fun startSkillAction(skillType: SkillType, itemId: String) {"""

patch(old_block, new_block)

# 2. Re-run offline-reward resolution against the recovered character once
#    cloud recovery actually swaps in a different local character id.
patch(
    """                                _currentCharacterId.value = remoteLocalId
                                val recoveredCharacter = recovered.characters.firstOrNull { it.id == remoteLocalId }
                                if (recoveredCharacter != null) {
                                    _currentAccountId.value = recoveredCharacter.accountId
                                }""",
    """                                _currentCharacterId.value = remoteLocalId
                                val recoveredCharacter = recovered.characters.firstOrNull { it.id == remoteLocalId }
                                if (recoveredCharacter != null) {
                                    _currentAccountId.value = recoveredCharacter.accountId
                                }
                                resolveOfflineRewardsAndSync(remoteLocalId)""",
)

with open(GVM, "w", encoding="utf-8") as f:
    f.write(content)

print("\nAll offline-reward race-condition patches applied successfully.")
