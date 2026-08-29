path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor1 = '''    fun enterCombatZone(zoneId: String): ServiceResult<CombatSession> {
        val characterId = _currentCharacterId.value ?: return ServiceResult.Failure("No character selected.")
        // Entering combat stops any active skilling/crafting queue - only one
        // activity can run at a time.
        offlineIdleService.stopQueue(characterId)
        skillActionProgressSeconds = 0
        craftActionProgressSeconds = 0
        refreshActiveQueue()
        combatService.stateFor(characterId, maxHpFor(characterId))
        val result = combatService.enterZone(characterId, zoneId, skillLevel(characterId, _trainingSkill.value))
        if (result is ServiceResult.Success) {
            combatLogFor.getOrPut(characterId) { mutableListOf() }.apply {
                clear()
                add(CombatLogEntry("Entered " + result.value.zone.name + "."))
            }
            sessionDropsFor.getOrPut(characterId) { mutableMapOf() }.clear()
            refreshCombatView()
        }
        return result
    }'''
count1 = content.count(anchor1)
assert count1 == 1, f"Expected 1 match for anchor1, found {count1}."
replacement1 = '''    fun enterCombatZone(zoneId: String): ServiceResult<CombatSession> {
        val characterId = _currentCharacterId.value ?: return ServiceResult.Failure("No character selected.")
        // Entering combat stops any active skilling/crafting queue - only one
        // activity can run at a time.
        offlineIdleService.stopQueue(characterId)
        skillActionProgressSeconds = 0
        craftActionProgressSeconds = 0
        refreshActiveQueue()
        combatService.stateFor(characterId, maxHpFor(characterId))
        val result = combatService.enterZone(characterId, zoneId, skillLevel(characterId, _trainingSkill.value))
        if (result is ServiceResult.Success) {
            combatLogFor.getOrPut(characterId) { mutableListOf() }.apply {
                clear()
                add(CombatLogEntry("Entered " + result.value.zone.name + "."))
            }
            sessionDropsFor.getOrPut(characterId) { mutableMapOf() }.clear()
            // Registers an offline-progress queue so combat keeps advancing while
            // the app is closed, mirroring skilling/crafting queues. Mutual
            // exclusion is already guaranteed by the stopQueue() call above.
            offlineIdleService.optIntoOfflineCombat(characterId, zoneId)
            refreshCombatView()
        }
        return result
    }'''
content = content.replace(anchor1, replacement1, 1)

anchor2 = '''    fun leaveCombatZone() {
        val characterId = _currentCharacterId.value ?: return
        combatService.leaveZone(characterId)
        _combatViewData.value = null
    }'''
count2 = content.count(anchor2)
assert count2 == 1, f"Expected 1 match for anchor2, found {count2}."
replacement2 = '''    fun leaveCombatZone() {
        val characterId = _currentCharacterId.value ?: return
        combatService.leaveZone(characterId)
        offlineIdleService.stopQueue(characterId)
        _combatViewData.value = null
    }'''
content = content.replace(anchor2, replacement2, 1)

anchor3 = '''    fun saveGame() {
        repository.save(
            accountService.exportAllAccounts(),
            accountService.exportAllCharacters(),
            progressionService.exportAllSkills(),
            offlineIdleService.exportSkillingQueues(),
            offlineIdleService.exportCraftingQueues(),
            offlineIdleService.exportLastSeen(),
            offlineIdleService.exportLastSaleCheck(),
            inventoryService.exportAllItems(),
            inventoryService.exportAllEquipped(),
            inventoryService.exportAllLoadoutSettings(),
            marketService.exportAccounts(),
            marketService.exportOrders(),
            marketService.exportPriceHistory()
        )'''
count3 = content.count(anchor3)
assert count3 == 1, f"Expected 1 match for anchor3, found {count3}."
replacement3 = '''    fun saveGame() {
        repository.save(
            accountService.exportAllAccounts(),
            accountService.exportAllCharacters(),
            progressionService.exportAllSkills(),
            offlineIdleService.exportSkillingQueues(),
            offlineIdleService.exportCraftingQueues(),
            offlineIdleService.exportLastSeen(),
            offlineIdleService.exportLastSaleCheck(),
            inventoryService.exportAllItems(),
            inventoryService.exportAllEquipped(),
            inventoryService.exportAllLoadoutSettings(),
            marketService.exportAccounts(),
            marketService.exportOrders(),
            marketService.exportPriceHistory(),
            combatService.exportSessions(),
            offlineIdleService.exportOfflineCombatQueues()
        )'''
content = content.replace(anchor3, replacement3, 1)

anchor4 = '''        saved.marketAccounts.forEach { marketService.restoreAccount(it) }
        saved.marketOrders.forEach { marketService.restoreOrder(it) }
        saved.marketPriceHistory.forEach { marketService.restorePriceHistoryEntry(it) }
    }
suspend fun login(email: String, password: String): ServiceResult<Account> {'''
count4 = content.count(anchor4)
assert count4 == 1, f"Expected 1 match for anchor4, found {count4}."
replacement4 = '''        saved.marketAccounts.forEach { marketService.restoreAccount(it) }
        saved.marketOrders.forEach { marketService.restoreOrder(it) }
        saved.marketPriceHistory.forEach { marketService.restorePriceHistoryEntry(it) }
        saved.combatSessions.forEach { combatService.restoreSession(it) }
        saved.offlineCombatQueues.forEach { offlineIdleService.restoreOfflineCombatQueue(it) }
    }
suspend fun login(email: String, password: String): ServiceResult<Account> {'''
content = content.replace(anchor4, replacement4, 1)

anchor5 = '''                                recovered.marketAccounts.forEach { marketService.restoreAccount(it) }
                                recovered.marketOrders.forEach { marketService.restoreOrder(it) }
                                recovered.marketPriceHistory.forEach { marketService.restorePriceHistoryEntry(it) }
                                _currentCharacterId.value = remoteLocalId
                                val recoveredCharacter = recovered.characters.firstOrNull { it.id == remoteLocalId }
                                if (recoveredCharacter != null) {
                                    _currentAccountId.value = recoveredCharacter.accountId
                                }
                                resolveOfflineRewardsAndSync(remoteLocalId)'''
count5 = content.count(anchor5)
assert count5 == 1, f"Expected 1 match for anchor5, found {count5}."
replacement5 = '''                                recovered.marketAccounts.forEach { marketService.restoreAccount(it) }
                                recovered.marketOrders.forEach { marketService.restoreOrder(it) }
                                recovered.marketPriceHistory.forEach { marketService.restorePriceHistoryEntry(it) }
                                recovered.combatSessions.forEach { combatService.restoreSession(it) }
                                recovered.offlineCombatQueues.forEach { offlineIdleService.restoreOfflineCombatQueue(it) }
                                _currentCharacterId.value = remoteLocalId
                                val recoveredCharacter = recovered.characters.firstOrNull { it.id == remoteLocalId }
                                if (recoveredCharacter != null) {
                                    _currentAccountId.value = recoveredCharacter.accountId
                                }
                                resolveOfflineRewardsAndSync(remoteLocalId)'''
content = content.replace(anchor5, replacement5, 1)

anchor6 = '''    recovered.marketAccounts.forEach { marketService.restoreAccount(it) }
    recovered.marketOrders.forEach { marketService.restoreOrder(it) }
    recovered.marketPriceHistory.forEach { marketService.restorePriceHistoryEntry(it) }

    val recoveredAccountExport = recovered.accounts.firstOrNull { it.email.equals(email, ignoreCase = true) }'''
count6 = content.count(anchor6)
assert count6 == 1, f"Expected 1 match for anchor6, found {count6}."
replacement6 = '''    recovered.marketAccounts.forEach { marketService.restoreAccount(it) }
    recovered.marketOrders.forEach { marketService.restoreOrder(it) }
    recovered.marketPriceHistory.forEach { marketService.restorePriceHistoryEntry(it) }
    recovered.combatSessions.forEach { combatService.restoreSession(it) }
    recovered.offlineCombatQueues.forEach { offlineIdleService.restoreOfflineCombatQueue(it) }

    val recoveredAccountExport = recovered.accounts.firstOrNull { it.email.equals(email, ignoreCase = true) }'''
content = content.replace(anchor6, replacement6, 1)

anchor7 = '''        val craftingQueue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.CraftingQueue
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
'''
count7 = content.count(anchor7)
assert count7 == 1, f"Expected 1 match for anchor7, found {count7}."
replacement7 = anchor7 + '''
        val combatQueue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.OfflineCombatQueue
        if (combatQueue != null) {
            val combatResult = offlineIdleService.resolveOfflineProgress(characterId)
            if (combatResult is ServiceResult.Success) {
                val elapsedSeconds = combatResult.value.effectiveElapsed.seconds
                if (elapsedSeconds > 0) {
                    // Mirrors tickCombat()'s per-style accuracy/max-hit computation exactly,
                    // using the character's live gear/levels at resolution time.
                    val weapon = equippedWeapon(characterId)
                    val trainingSkill = _trainingSkill.value
                    val accuracy: Int
                    val maxHit: Int
                    when (weapon?.style) {
                        CombatStyle.MAGIC -> {
                            val magicLevel = skillLevel(characterId, SkillType.MAGIC)
                            accuracy = magicLevel * 2 + weapon.baseAccuracy
                            maxHit = (magicLevel / 3) + weapon.baseMaxHit
                        }
                        CombatStyle.RANGED -> {
                            val archeryLevel = skillLevel(characterId, SkillType.ARCHERY)
                            accuracy = archeryLevel * 2 + weapon.baseAccuracy
                            maxHit = (archeryLevel / 3) + weapon.baseMaxHit
                        }
                        else -> {
                            val attackLevel = skillLevel(characterId, SkillType.ATTACK)
                            val strengthLevel = skillLevel(characterId, SkillType.STRENGTH)
                            accuracy = attackLevel * 2 + (weapon?.baseAccuracy ?: 5)
                            maxHit = (strengthLevel / 3) + (weapon?.baseMaxHit ?: 1)
                        }
                    }
                    val outcome = combatService.resolveOfflineCombat(characterId, combatQueue.zoneId, elapsedSeconds, accuracy, maxHit)
                    if (outcome is ServiceResult.Success && outcome.value.estimatedKills > 0) {
                        if (outcome.value.xpEarned > 0) {
                            progressionService.grantXp(characterId, trainingSkill, outcome.value.xpEarned)
                        }
                        val loot = combatService.collectLoot(characterId)
                        if (loot is ServiceResult.Success) {
                            loot.value.forEach { entry ->
                                inventoryService.inventoryFor(characterId).addItem(entry.itemId, entry.minQty)
                            }
                        }
                        val coinsEarned = combatService.collectCoins(characterId)
                        if (coinsEarned > 0) {
                            grantCombatCoins(characterId, coinsEarned)
                        }
                        _offlineSummary.value = OfflineSummary(
                            awaySeconds = combatResult.value.claimedElapsed.seconds,
                            skillActionName = "Combat",
                            itemName = "kills",
                            quantity = outcome.value.estimatedKills,
                            xpEarned = outcome.value.xpEarned
                        )
                    }
                }
            }
        }
'''
content = content.replace(anchor7, replacement7, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("patch_offline_combat_viewmodel.py applied cleanly.")