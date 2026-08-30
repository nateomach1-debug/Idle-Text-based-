path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

# 1. Track why a crafting batch stopped early.
anchor1 = '''    private data class CraftBatchResult(val successfulCrafts: Int, val itemsProduced: Int, val xpGranted: Long)

    private fun craftItems(characterId: String, itemId: String, attempts: Int): CraftBatchResult {
        val recipe = RecipeCatalog.forOutput(itemId) ?: return CraftBatchResult(0, 0, 0)
        val skillType = SkillType.valueOf(recipe.skillRequired)
        val book = progressionService.skillBookFor(characterId)
        val skill = book.all().find { it.type == skillType }
        val playerLevel = if (skill != null) LevelCurve.levelForXp(skill.xp) else 1
        val inventory = inventoryService.inventoryFor(characterId)
        val xpPerAttempt = CraftingTierCurve.xpFor(recipe.levelRequired)

        var successes = 0
        var totalProduced = 0
        var xpGranted = 0L
        for (i in 0 until attempts) {
            val result = craftingService.craftOnce(inventory, itemId, playerLevel)
            if (result is ServiceResult.Success) {
                xpGranted += xpPerAttempt
                if (result.value.succeeded) {
                    successes += 1
                    totalProduced += result.value.quantityProduced
                }
            } else {
                break
            }
        }
        if (xpGranted > 0) {
            progressionService.grantXp(characterId, skillType, xpGranted)
        }
        return CraftBatchResult(successes, totalProduced, xpGranted)
    }'''
count1 = content.count(anchor1)
assert count1 == 1, f"Expected 1 match, found {count1}."
replacement1 = '''    private data class CraftBatchResult(val successfulCrafts: Int, val itemsProduced: Int, val xpGranted: Long, val stoppedReason: String? = null)

    private fun craftItems(characterId: String, itemId: String, attempts: Int): CraftBatchResult {
        val recipe = RecipeCatalog.forOutput(itemId) ?: return CraftBatchResult(0, 0, 0)
        val skillType = SkillType.valueOf(recipe.skillRequired)
        val book = progressionService.skillBookFor(characterId)
        val skill = book.all().find { it.type == skillType }
        val playerLevel = if (skill != null) LevelCurve.levelForXp(skill.xp) else 1
        val inventory = inventoryService.inventoryFor(characterId)
        val xpPerAttempt = CraftingTierCurve.xpFor(recipe.levelRequired)

        var successes = 0
        var totalProduced = 0
        var xpGranted = 0L
        var stoppedReason: String? = null
        for (i in 0 until attempts) {
            val result = craftingService.craftOnce(inventory, itemId, playerLevel)
            if (result is ServiceResult.Success) {
                xpGranted += xpPerAttempt
                if (result.value.succeeded) {
                    successes += 1
                    totalProduced += result.value.quantityProduced
                }
            } else {
                stoppedReason = (result as? ServiceResult.Failure)?.message ?: "Missing materials or requirements."
                break
            }
        }
        if (xpGranted > 0) {
            progressionService.grantXp(characterId, skillType, xpGranted)
        }
        return CraftBatchResult(successes, totalProduced, xpGranted, stoppedReason)
    }'''
content = content.replace(anchor1, replacement1, 1)

# 2. tickCrafting() now actually stops the queue (and notifies) when materials
#    run out mid-batch, instead of silently failing every attempt forever.
anchor2 = '''    private fun tickCrafting() {
        val characterId = _currentCharacterId.value ?: return
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.CraftingQueue ?: return

        craftActionProgressSeconds += 1
        if (craftActionProgressSeconds < queue.secondsPerAction) return

        val attempts = (craftActionProgressSeconds / queue.secondsPerAction).toInt()
        craftActionProgressSeconds %= queue.secondsPerAction

        val remainingToTarget = queue.targetQuantity?.let { it - queue.quantityCompleted }
        val cappedAttempts = if (remainingToTarget != null) minOf(attempts, remainingToTarget) else attempts
        if (cappedAttempts <= 0) return

        val batch = craftItems(characterId, queue.itemId, cappedAttempts)
        queue.quantityCompleted += batch.successfulCrafts
        refreshSkills()
        refreshInventory()

        if (queue.isTargetReached()) {
            offlineIdleService.stopQueue(characterId)
            refreshActiveQueue()
        }
    }'''
count2 = content.count(anchor2)
assert count2 == 1, f"Expected 1 match, found {count2}."
replacement2 = '''    private fun tickCrafting() {
        val characterId = _currentCharacterId.value ?: return
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.CraftingQueue ?: return

        craftActionProgressSeconds += 1
        if (craftActionProgressSeconds < queue.secondsPerAction) return

        val attempts = (craftActionProgressSeconds / queue.secondsPerAction).toInt()
        craftActionProgressSeconds %= queue.secondsPerAction

        val remainingToTarget = queue.targetQuantity?.let { it - queue.quantityCompleted }
        val cappedAttempts = if (remainingToTarget != null) minOf(attempts, remainingToTarget) else attempts
        if (cappedAttempts <= 0) return

        val batch = craftItems(characterId, queue.itemId, cappedAttempts)
        queue.quantityCompleted += batch.successfulCrafts
        refreshSkills()
        refreshInventory()

        if (queue.isTargetReached()) {
            offlineIdleService.stopQueue(characterId)
            refreshActiveQueue()
        } else if (batch.stoppedReason != null) {
            offlineIdleService.stopQueue(characterId)
            craftActionProgressSeconds = 0
            refreshActiveQueue()
            _actionStoppedNotifications.value = _actionStoppedNotifications.value + ActionStoppedNotice(
                itemName = formatItemName(queue.itemId),
                reason = batch.stoppedReason
            )
        }
    }'''
content = content.replace(anchor2, replacement2, 1)

# 3. Apply the same stop+notify behavior to the farming seed-exhaustion case.
anchor3 = '''            if (requiredSeedId != null && effectiveActions < actionsCompleted) {
                // Ran out of seeds mid-batch - stop the queue instead of spinning uselessly.
                offlineIdleService.stopQueue(characterId)
                skillActionProgressSeconds = 0
            }'''
count3 = content.count(anchor3)
assert count3 == 1, f"Expected 1 match, found {count3}."
replacement3 = '''            if (requiredSeedId != null && effectiveActions < actionsCompleted) {
                // Ran out of seeds mid-batch - stop the queue instead of spinning uselessly.
                offlineIdleService.stopQueue(characterId)
                skillActionProgressSeconds = 0
                _actionStoppedNotifications.value = _actionStoppedNotifications.value + ActionStoppedNotice(
                    itemName = formatItemName(queue.itemId),
                    reason = "Out of " + formatItemName(requiredSeedId) + "."
                )
            }'''
content = content.replace(anchor3, replacement3, 1)

# 4. New shared notification mechanism, mirroring the existing
#    pendingSaleNotifications queue pattern exactly.
anchor4 = '''    private data class CraftBatchResult(val successfulCrafts: Int, val itemsProduced: Int, val xpGranted: Long, val stoppedReason: String? = null)'''
count4 = content.count(anchor4)
assert count4 == 1, f"Expected 1 match, found {count4}."
replacement4 = '''    data class ActionStoppedNotice(val itemName: String, val reason: String)

    private val _actionStoppedNotifications = MutableStateFlow<List<ActionStoppedNotice>>(emptyList())
    val actionStoppedNotifications: StateFlow<List<ActionStoppedNotice>> = _actionStoppedNotifications.asStateFlow()

    fun dismissActionStoppedNotification() {
        _actionStoppedNotifications.value = _actionStoppedNotifications.value.drop(1)
    }

    private data class CraftBatchResult(val successfulCrafts: Int, val itemsProduced: Int, val xpGranted: Long, val stoppedReason: String? = null)'''
content = content.replace(anchor4, replacement4, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

main_path = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(main_path, encoding="utf-8") as f:
    content = f.read()

anchor5 = '''    val pendingSaleNotifications by gameViewModel.pendingSaleNotifications.collectAsState()
    pendingSaleNotifications.firstOrNull()?.let { sale ->
        androidx.compose.material3.AlertDialog(
            onDismissRequest = { gameViewModel.dismissSaleNotification() },
            title = { androidx.compose.material3.Text("Item Sold!") },
            text = {
                androidx.compose.material3.Text(
                    "Sold " + sale.quantity + "x " + sale.itemName + "\\n" +
                    "You received " + sale.netProceeds + " coins (after tax)."
                )
            },
            confirmButton = {
                androidx.compose.material3.TextButton(onClick = { gameViewModel.dismissSaleNotification() }) {
                    androidx.compose.material3.Text("Nice!")
                }
            }
        )
    }'''
count5 = content.count(anchor5)
assert count5 == 1, f"Expected 1 match, found {count5}."
replacement5 = anchor5 + '''

    val actionStoppedNotifications by gameViewModel.actionStoppedNotifications.collectAsState()
    actionStoppedNotifications.firstOrNull()?.let { notice ->
        androidx.compose.material3.AlertDialog(
            onDismissRequest = { gameViewModel.dismissActionStoppedNotification() },
            title = { androidx.compose.material3.Text("Action Stopped") },
            text = {
                androidx.compose.material3.Text(
                    "Ran out of materials for " + notice.itemName + ".\\n" + notice.reason
                )
            },
            confirmButton = {
                androidx.compose.material3.TextButton(onClick = { gameViewModel.dismissActionStoppedNotification() }) {
                    androidx.compose.material3.Text("OK")
                }
            }
        )
    }'''
content = content.replace(anchor5, replacement5, 1)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("patch_stop_and_notify_on_exhausted_materials.py applied cleanly.")
