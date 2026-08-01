"""
Step 5 patch script: wires CraftingService into the live game loop and
offline catch-up, mirroring the existing SkillingQueue pattern exactly.

Run this from the repo root:
    python3 apply_step5_patches.py

Every edit uses an exact-match assert -- if any anchor text doesn't match
your actual file (whitespace drift, prior edits, etc.), the script will
raise an AssertionError naming exactly which file/anchor failed, rather
than silently corrupting anything. Fix the mismatch (or tell me what the
real text is) and re-run -- it's safe to re-run after a partial failure
since nothing is written until the matching text is found.

After running, diff every touched file before committing:
    git diff app/src/main/kotlin/com/yourname/idlerpg/OfflineIdleMechanicsSystem.kt
    git diff app/src/main/kotlin/com/yourname/idlerpg/GameStateRepository.kt
    git diff app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt
    git diff app/src/main/kotlin/com/yourname/idlerpg/ItemsEquipmentSystem.kt

One manual step this script does NOT do (see bottom of this file for why):
wiring tickCrafting() into the main per-second tick loop alongside
tickSkilling(). Instructions for that are printed at the end.
"""

import re

BASE = "app/src/main/kotlin/com/yourname/idlerpg/"


def apply_patch(path, old, new, label):
    with open(path, "r") as f:
        content = f.read()
    count = content.count(old)
    assert count == 1, (
        f"[{label}] Expected exactly 1 match in {path}, found {count}.\n"
        f"--- anchor text I searched for ---\n{old}\n--- end anchor ---"
    )
    content = content.replace(old, new, 1)
    with open(path, "w") as f:
        f.write(content)
    print(f"OK  [{label}] patched {path}")


# =========================================================
# FILE 1: OfflineIdleMechanicsSystem.kt
# =========================================================
p = BASE + "OfflineIdleMechanicsSystem.kt"

# 1a. Add CraftingQueueExport data class next to SkillingQueueExport
apply_patch(
    p,
    old="""data class SkillingQueueExport(
    val characterId: String,
    val skillId: String,
    val itemId: String,
    val secondsPerAction: Long,
    val startedAt: String
)

data class LastSeenExport(val characterId: String, val lastSeenAt: String)""",
    new="""data class SkillingQueueExport(
    val characterId: String,
    val skillId: String,
    val itemId: String,
    val secondsPerAction: Long,
    val startedAt: String
)

data class CraftingQueueExport(
    val characterId: String,
    val itemId: String,
    val secondsPerAction: Long,
    val targetQuantity: Int?,
    val quantityCompleted: Int,
    val startedAt: String
)

data class LastSeenExport(val characterId: String, val lastSeenAt: String)""",
    label="1a: CraftingQueueExport data class",
)

# 1b. Add exportCraftingQueues() next to exportSkillingQueues()
apply_patch(
    p,
    old="""    fun exportSkillingQueues(): List<SkillingQueueExport> =
        activeQueues.values.filterIsInstance<ActiveQueue.SkillingQueue>().map {
            SkillingQueueExport(it.characterId, it.skillId, it.itemId, it.secondsPerAction, it.startedAt.toString())
        }

    fun exportLastSeen(): List<LastSeenExport> =""",
    new="""    fun exportSkillingQueues(): List<SkillingQueueExport> =
        activeQueues.values.filterIsInstance<ActiveQueue.SkillingQueue>().map {
            SkillingQueueExport(it.characterId, it.skillId, it.itemId, it.secondsPerAction, it.startedAt.toString())
        }

    fun exportCraftingQueues(): List<CraftingQueueExport> =
        activeQueues.values.filterIsInstance<ActiveQueue.CraftingQueue>().map {
            CraftingQueueExport(
                it.characterId,
                it.itemId,
                it.secondsPerAction,
                it.targetQuantity,
                it.quantityCompleted,
                it.startedAt.toString()
            )
        }

    fun exportLastSeen(): List<LastSeenExport> =""",
    label="1b: exportCraftingQueues()",
)

# 1c. Add restoreCraftingQueue() next to restoreSkillingQueue()
apply_patch(
    p,
    old="""    fun restoreSkillingQueue(export: SkillingQueueExport) {
        activeQueues[export.characterId] = ActiveQueue.SkillingQueue(
            characterId = export.characterId,
            skillId = export.skillId,
            itemId = export.itemId,
            secondsPerAction = export.secondsPerAction,
            startedAt = Instant.parse(export.startedAt)
        )
    }

    fun restoreLastSeen(export: LastSeenExport) {""",
    new="""    fun restoreSkillingQueue(export: SkillingQueueExport) {
        activeQueues[export.characterId] = ActiveQueue.SkillingQueue(
            characterId = export.characterId,
            skillId = export.skillId,
            itemId = export.itemId,
            secondsPerAction = export.secondsPerAction,
            startedAt = Instant.parse(export.startedAt)
        )
    }

    fun restoreCraftingQueue(export: CraftingQueueExport) {
        val queue = ActiveQueue.CraftingQueue(
            characterId = export.characterId,
            itemId = export.itemId,
            secondsPerAction = export.secondsPerAction,
            targetQuantity = export.targetQuantity,
            startedAt = Instant.parse(export.startedAt)
        )
        queue.quantityCompleted = export.quantityCompleted
        activeQueues[export.characterId] = queue
    }

    fun restoreLastSeen(export: LastSeenExport) {""",
    label="1c: restoreCraftingQueue()",
)

print()

# =========================================================
# FILE 2: GameStateRepository.kt
# =========================================================
p = BASE + "GameStateRepository.kt"

# 2a. save() signature: add craftingQueues param
apply_patch(
    p,
    old="""    fun save(
        accounts: List<AccountExport>,
        characters: List<CharacterExport>,
        skills: List<SkillExport>,
        skillingQueues: List<SkillingQueueExport>,
        lastSeen: List<LastSeenExport>,
        inventoryItems: List<InventorySlotExport>,
        equippedSlots: List<EquippedSlotExport>
    ) {""",
    new="""    fun save(
        accounts: List<AccountExport>,
        characters: List<CharacterExport>,
        skills: List<SkillExport>,
        skillingQueues: List<SkillingQueueExport>,
        craftingQueues: List<CraftingQueueExport>,
        lastSeen: List<LastSeenExport>,
        inventoryItems: List<InventorySlotExport>,
        equippedSlots: List<EquippedSlotExport>
    ) {""",
    label="2a: save() signature",
)

# 2b. save() body: serialize craftingQueues after skillingQueues
apply_patch(
    p,
    old="""        val queuesArray = JSONArray()
        skillingQueues.forEach { queue ->
            val obj = JSONObject()
            obj.put("characterId", queue.characterId)
            obj.put("skillId", queue.skillId)
            obj.put("itemId", queue.itemId)
            obj.put("secondsPerAction", queue.secondsPerAction)
            obj.put("startedAt", queue.startedAt)
            queuesArray.put(obj)
        }
        root.put("skillingQueues", queuesArray)

        val lastSeenArray = JSONArray()""",
    new="""        val queuesArray = JSONArray()
        skillingQueues.forEach { queue ->
            val obj = JSONObject()
            obj.put("characterId", queue.characterId)
            obj.put("skillId", queue.skillId)
            obj.put("itemId", queue.itemId)
            obj.put("secondsPerAction", queue.secondsPerAction)
            obj.put("startedAt", queue.startedAt)
            queuesArray.put(obj)
        }
        root.put("skillingQueues", queuesArray)

        val craftingQueuesArray = JSONArray()
        craftingQueues.forEach { queue ->
            val obj = JSONObject()
            obj.put("characterId", queue.characterId)
            obj.put("itemId", queue.itemId)
            obj.put("secondsPerAction", queue.secondsPerAction)
            obj.put("targetQuantity", queue.targetQuantity)
            obj.put("quantityCompleted", queue.quantityCompleted)
            obj.put("startedAt", queue.startedAt)
            craftingQueuesArray.put(obj)
        }
        root.put("craftingQueues", craftingQueuesArray)

        val lastSeenArray = JSONArray()""",
    label="2b: serialize craftingQueues",
)

# 2c. load(): parse craftingQueues after skillingQueues
apply_patch(
    p,
    old="""        val skillingQueues = mutableListOf<SkillingQueueExport>()
        val queuesArray = root.optJSONArray("skillingQueues") ?: JSONArray()
        for (i in 0 until queuesArray.length()) {
            val obj = queuesArray.getJSONObject(i)
            skillingQueues.add(
                SkillingQueueExport(
                    characterId = obj.getString("characterId"),
                    skillId = obj.getString("skillId"),
                    itemId = obj.getString("itemId"),
                    secondsPerAction = obj.getLong("secondsPerAction"),
                    startedAt = obj.getString("startedAt")
                )
            )
        }

        val lastSeen = mutableListOf<LastSeenExport>()""",
    new="""        val skillingQueues = mutableListOf<SkillingQueueExport>()
        val queuesArray = root.optJSONArray("skillingQueues") ?: JSONArray()
        for (i in 0 until queuesArray.length()) {
            val obj = queuesArray.getJSONObject(i)
            skillingQueues.add(
                SkillingQueueExport(
                    characterId = obj.getString("characterId"),
                    skillId = obj.getString("skillId"),
                    itemId = obj.getString("itemId"),
                    secondsPerAction = obj.getLong("secondsPerAction"),
                    startedAt = obj.getString("startedAt")
                )
            )
        }

        val craftingQueues = mutableListOf<CraftingQueueExport>()
        val craftingQueuesArray = root.optJSONArray("craftingQueues") ?: JSONArray()
        for (i in 0 until craftingQueuesArray.length()) {
            val obj = craftingQueuesArray.getJSONObject(i)
            craftingQueues.add(
                CraftingQueueExport(
                    characterId = obj.getString("characterId"),
                    itemId = obj.getString("itemId"),
                    secondsPerAction = obj.getLong("secondsPerAction"),
                    targetQuantity = if (obj.isNull("targetQuantity")) null else obj.getInt("targetQuantity"),
                    quantityCompleted = obj.getInt("quantityCompleted"),
                    startedAt = obj.getString("startedAt")
                )
            )
        }

        val lastSeen = mutableListOf<LastSeenExport>()""",
    label="2c: parse craftingQueues",
)

# 2d. return statement + SavedGameState data class
apply_patch(
    p,
    old="""        return SavedGameState(accounts, characters, skills, skillingQueues, lastSeen, inventoryItems, equippedSlots)
    }
}

data class SavedGameState(
    val accounts: List<AccountExport>,
    val characters: List<CharacterExport>,
    val skills: List<SkillExport>,
    val skillingQueues: List<SkillingQueueExport>,
    val lastSeen: List<LastSeenExport>,
    val inventoryItems: List<InventorySlotExport>,
    val equippedSlots: List<EquippedSlotExport>
)""",
    new="""        return SavedGameState(accounts, characters, skills, skillingQueues, craftingQueues, lastSeen, inventoryItems, equippedSlots)
    }
}

data class SavedGameState(
    val accounts: List<AccountExport>,
    val characters: List<CharacterExport>,
    val skills: List<SkillExport>,
    val skillingQueues: List<SkillingQueueExport>,
    val craftingQueues: List<CraftingQueueExport>,
    val lastSeen: List<LastSeenExport>,
    val inventoryItems: List<InventorySlotExport>,
    val equippedSlots: List<EquippedSlotExport>
)""",
    label="2d: SavedGameState + return",
)

print()

# =========================================================
# FILE 3: ItemsEquipmentSystem.kt -- add CraftingTierCurve
# =========================================================
p = BASE + "ItemsEquipmentSystem.kt"

apply_patch(
    p,
    old="""    fun rollSuccess(playerSkillLevel: Int, recipe: Recipe): Boolean {
        val chance = successChancePercent(playerSkillLevel, recipe)
        return Random.nextDouble(0.0, 100.0) < chance
    }
}""",
    new="""    fun rollSuccess(playerSkillLevel: Int, recipe: Recipe): Boolean {
        val chance = successChancePercent(playerSkillLevel, recipe)
        return Random.nextDouble(0.0, 100.0) < chance
    }
}

// =========================================================
// CRAFTING TIER CURVE
// Decoupled from ActionCatalog on purpose -- Recipe.levelRequired is
// the sole source of truth for crafting XP/time, reusing the same
// tier ladder ActionCatalog already uses elsewhere in the game.
// =========================================================

object CraftingTierCurve {
    private val tierLevels = intArrayOf(1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 99)
    private val tierXp = intArrayOf(10, 19, 30, 41, 52, 63, 74, 85, 96, 107, 118, 129, 140, 151, 162, 173, 184, 195, 206, 226)
    private val tierSeconds = longArrayOf(3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6)

    private fun tierIndexFor(level: Int): Int {
        var index = 0
        for (i in tierLevels.indices) {
            if (level >= tierLevels[i]) index = i else break
        }
        return index
    }

    fun xpFor(level: Int): Int = tierXp[tierIndexFor(level)]
    fun secondsFor(level: Int): Long = tierSeconds[tierIndexFor(level)]
}""",
    label="3: CraftingTierCurve",
)

print()

# =========================================================
# FILE 4: GameViewModel.kt
# =========================================================
p = BASE + "GameViewModel.kt"

# 4a. saveGame(): add exportCraftingQueues()
apply_patch(
    p,
    old="""    fun saveGame() {
        repository.save(
            accountService.exportAllAccounts(),
            accountService.exportAllCharacters(),
            progressionService.exportAllSkills(),
            offlineIdleService.exportSkillingQueues(),
            offlineIdleService.exportLastSeen(),
            inventoryService.exportAllItems(),
            inventoryService.exportAllEquipped()
        )
    }""",
    new="""    fun saveGame() {
        repository.save(
            accountService.exportAllAccounts(),
            accountService.exportAllCharacters(),
            progressionService.exportAllSkills(),
            offlineIdleService.exportSkillingQueues(),
            offlineIdleService.exportCraftingQueues(),
            offlineIdleService.exportLastSeen(),
            inventoryService.exportAllItems(),
            inventoryService.exportAllEquipped()
        )
    }""",
    label="4a: saveGame()",
)

# 4b. loadGame(): restore craftingQueues
apply_patch(
    p,
    old="""        saved.skillingQueues.forEach { offlineIdleService.restoreSkillingQueue(it) }
        saved.lastSeen.forEach { offlineIdleService.restoreLastSeen(it) }""",
    new="""        saved.skillingQueues.forEach { offlineIdleService.restoreSkillingQueue(it) }
        saved.craftingQueues.forEach { offlineIdleService.restoreCraftingQueue(it) }
        saved.lastSeen.forEach { offlineIdleService.restoreLastSeen(it) }""",
    label="4b: loadGame()",
)

# 4c. selectCharacter(): offline crafting catch-up branch
apply_patch(
    p,
    old="""        offlineIdleService.recordLastSeen(characterId)
        skillActionProgressSeconds = 0
        refreshSkills()
        refreshInventory()
    }

    fun startSkillAction(skillType: SkillType, itemId: String) {""",
    new="""        val craftingQueue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.CraftingQueue
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
    }

    fun startSkillAction(skillType: SkillType, itemId: String) {""",
    label="4c: selectCharacter() crafting catch-up",
)

# 4d. New functions: startCraftingAction / stopCraftingAction / tickCrafting / craftItems,
#     inserted right after tickSkilling()'s closing brace.
apply_patch(
    p,
    old="""        val skillType = SkillType.valueOf(queue.skillId)
        val action = ActionCatalog.find(skillType, queue.itemId)
        if (action != null) {
            progressionService.grantXp(characterId, skillType, action.xpPerAction * actionsCompleted)
            inventoryService.inventoryFor(characterId).addItem(queue.itemId, actionsCompleted.toInt())
            refreshSkills()
            refreshInventory()
        }
    }

    fun refreshSkills() {""",
    new="""        val skillType = SkillType.valueOf(queue.skillId)
        val action = ActionCatalog.find(skillType, queue.itemId)
        if (action != null) {
            progressionService.grantXp(characterId, skillType, action.xpPerAction * actionsCompleted)
            inventoryService.inventoryFor(characterId).addItem(queue.itemId, actionsCompleted.toInt())
            refreshSkills()
            refreshInventory()
        }
    }

    // =========================================================
    // CRAFTING -- mirrors the SkillingQueue flow above. Recipe.levelRequired
    // (via CraftingTierCurve) is the source of truth for timing/XP, decoupled
    // from ActionCatalog since production item ids don't line up with
    // ActionCatalog's generic class-action ids (see Step 5 handoff notes).
    // =========================================================

    private var craftActionProgressSeconds: Long = 0

    private val craftingService = CraftingService()

    private data class CraftBatchResult(val successfulCrafts: Int, val itemsProduced: Int, val xpGranted: Int)

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
        var xpGranted = 0
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
    }

    fun startCraftingAction(itemId: String, targetQuantity: Int? = null) {
        val characterId = _currentCharacterId.value ?: return
        val recipe = RecipeCatalog.forOutput(itemId) ?: return
        offlineIdleService.stopQueue(characterId)
        offlineIdleService.startCraftingQueue(
            characterId,
            itemId,
            CraftingTierCurve.secondsFor(recipe.levelRequired),
            targetQuantity
        )
        offlineIdleService.recordLastSeen(characterId)
        craftActionProgressSeconds = 0
    }

    fun stopCraftingAction() {
        val characterId = _currentCharacterId.value ?: return
        offlineIdleService.stopQueue(characterId)
        craftActionProgressSeconds = 0
    }

    private fun tickCrafting() {
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
        }
    }

    fun refreshSkills() {""",
    label="4d: startCraftingAction / stopCraftingAction / tickCrafting / craftItems",
)

print()
print("=" * 60)
print("All patches applied successfully.")
print("=" * 60)
print()
print("MANUAL STEP STILL REQUIRED (not automated -- see script docstring):")
print("Find your main per-second tick loop and add a tickCrafting() call")
print("alongside the existing tickSkilling() call. Run this to find it:")
print()
print("  grep -n -B3 -A3 'tickSkilling()' app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")
print()
print("Look for the line that CALLS tickSkilling() (inside a loop/coroutine --")
print("NOT the 'private fun tickSkilling() {' definition line). Once you see")
print("it, this sed will add the crafting tick right after it -- but read the")
print("grep output first to make sure the pattern below actually matches your")
print("loop and won't also touch the function definition:")
print()
print("  sed -i '/^\\s*tickSkilling()\\s*$/a\\            tickCrafting()' \\")
print("      app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")
print()
print("Then verify with git diff before building.")
