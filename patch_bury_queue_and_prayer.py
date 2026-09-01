# PART L: Make BuryQueue actually progress offline - resolveOfflineProgress()
# computes elapsed-time-based actionsCompleted (capped by remaining target,
# mirroring SkillingQueue), and resolveOfflineRewardsAndSync() caps that further
# by actual bone stock, consumes bones, grants Prayer XP, and shows the summary.

# 1. resolveOfflineProgress()'s BuryQueue branch (replaces the earlier "no offline
#    progress" stub from Part K, if that was applied - falls back to inserting
#    fresh if not).
path = "app/src/main/kotlin/com/yourname/idlerpg/OfflineIdleMechanicsSystem.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor_stub = '''            is ActiveQueue.BuryQueue -> {
                // Burying is resolved through its own dedicated live-tick logic
                // (tickBurying() in GameViewModel), not through this generic
                // elapsed-time catch-up path - no offline progress for it here,
                // same treatment as OfflineCombatQueue above.
                actionsCompleted = 0
            }
        }'''
anchor_no_branch = '''            is ActiveQueue.OfflineCombatQueue -> {
                actionsCompleted = 0
            }
        }'''

real_branch = '''            is ActiveQueue.OfflineCombatQueue -> {
                actionsCompleted = 0
            }
            is ActiveQueue.BuryQueue -> {
                var possibleActions = (finalEffectiveElapsed.seconds / queue.secondsPerAction).toInt()
                val remaining = queue.targetQuantity - queue.quantityCompleted
                possibleActions = possibleActions.coerceAtMost(remaining)
                queue.quantityCompleted += possibleActions
                actionsCompleted = possibleActions
                if (queue.isTargetReached()) queueExhausted = true
            }
        }'''

if content.count(anchor_stub) == 1:
    content = content.replace(anchor_stub, real_branch, 1)
elif content.count(anchor_no_branch) == 1:
    content = content.replace(anchor_no_branch, real_branch, 1)
else:
    raise AssertionError("Neither the stub nor the plain OfflineCombatQueue-only branch was found - check current file state.")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part L (1/2 - OfflineIdleMechanicsSystem.kt) applied cleanly.")

# 2. resolveOfflineRewardsAndSync()'s new BuryQueue branch - caps further by
#    actual bone stock, consumes bones, grants Prayer XP, shows the summary.
gvm_path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(gvm_path, encoding="utf-8") as f:
    content = f.read()

anchor_crafting_branch = '''        val craftingQueue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.CraftingQueue
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
        }'''
count = content.count(anchor_crafting_branch)
assert count == 1, f"Expected 1 match, found {count}."
replacement = anchor_crafting_branch + '''

        val buryQueue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.BuryQueue
        if (buryQueue != null) {
            val buryResult = offlineIdleService.resolveOfflineProgress(characterId)
            if (buryResult is ServiceResult.Success && buryResult.value.actionsCompleted > 0) {
                val boneInfo = PrayerBoneRequirements[buryQueue.itemId]
                if (boneInfo != null) {
                    val inventory = inventoryService.inventoryFor(characterId)
                    val available = inventory.quantityOf(buryQueue.itemId)
                    val effectiveActions = minOf(buryResult.value.actionsCompleted, available)
                    if (effectiveActions > 0) {
                        inventory.removeItem(buryQueue.itemId, effectiveActions)
                        val xpGranted = boneInfo.xpAmount * effectiveActions
                        progressionService.grantXp(characterId, SkillType.PRAYER, xpGranted)
                        _offlineSummary.value = OfflineSummary(
                            awaySeconds = buryResult.value.claimedElapsed.seconds,
                            skillActionName = "Bury " + formatItemName(buryQueue.itemId),
                            itemName = formatItemName(buryQueue.itemId),
                            quantity = effectiveActions,
                            xpEarned = xpGranted
                        )
                    }
                }
            }
        }'''
content = content.replace(anchor_crafting_branch, replacement, 1)

with open(gvm_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part L (2/2 - GameViewModel.kt) applied cleanly.")
