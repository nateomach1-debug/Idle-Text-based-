path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor = '''    fun startSkillAction(skillType: SkillType, itemId: String) {
        val characterId = _currentCharacterId.value ?: return
        val action = ActionCatalog.find(skillType, itemId) ?: return
        // Starting a skill stops any active combat session - only one
        // activity can run at a time.
        leaveCombatZone()
        offlineIdleService.stopQueue(characterId)
        offlineIdleService.startSkillingQueue(characterId, skillType.name, itemId, action.secondsPerAction)
        offlineIdleService.recordLastSeen(characterId)
        checkForRecentSales(characterId)
        skillActionProgressSeconds = 0
        refreshActiveQueue()
    }

    fun stopSkillAction() {
        val characterId = _currentCharacterId.value ?: return
        offlineIdleService.stopQueue(characterId)
        skillActionProgressSeconds = 0
        refreshActiveQueue()
    }

    private fun tickSkilling() {
        val characterId = _currentCharacterId.value ?: return
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.SkillingQueue ?: return

        skillActionProgressSeconds += 1
        if (skillActionProgressSeconds < queue.secondsPerAction) return

        val actionsCompleted = skillActionProgressSeconds / queue.secondsPerAction
        skillActionProgressSeconds %= queue.secondsPerAction

        val skillType = SkillType.valueOf(queue.skillId)
        val action = ActionCatalog.find(skillType, queue.itemId)
        if (action != null) {
            progressionService.grantXp(characterId, skillType, action.xpPerAction * actionsCompleted)
            inventoryService.inventoryFor(characterId).addItem(queue.itemId, actionsCompleted.toInt())
            if (skillType == SkillType.MINING) {
                MiningBonusGemTable.rollAndGrant(inventoryService.inventoryFor(characterId), actionsCompleted.toInt())
            }
            refreshSkills()
            refreshInventory()
        }
    }'''
count = content.count(anchor)
assert count == 1, f"Expected 1 match, found {count}."
replacement = '''    // Crop-harvest FARMING actions each require consuming one of the
    // corresponding seed/sapling item per action performed. Pure seed-gathering
    // actions (the values on the right, e.g. "guam_seed") are unaffected - they
    // remain free. Deliberately excludes willow_sapling/magic_sapling/
    // elder_sapling/world_tree_sapling (no separate crop step) and flax (no
    // seed at all).
    private val farmingSeedRequirements: Map<String, String> = mapOf(
        "potato" to "potato_seed",
        "onion" to "onion_seed",
        "cabbage" to "cabbage_seed",
        "tomato" to "tomato_seed",
        "sweetcorn" to "sweetcorn_seed",
        "guam_leaf" to "guam_seed",
        "strawberry" to "strawberry_seed",
        "marrentill" to "marrentill_seed",
        "watermelon" to "watermelon_seed",
        "apple" to "apple_sapling",
        "tarromin" to "tarromin_seed",
        "banana" to "banana_sapling",
        "harralander" to "harralander_seed",
        "orange" to "orange_sapling",
        "ranarr_weed" to "ranarr_seed",
        "grapes" to "grape_seed",
        "toadflax" to "toadflax_seed",
        "papaya" to "papaya_sapling",
        "irit_leaf" to "irit_seed",
        "coconut" to "palm_sapling",
        "avantoe" to "avantoe_seed",
        "kwuarm" to "kwuarm_seed",
        "snapdragon" to "snapdragon_seed",
        "torstol" to "torstol_seed",
        "celestial_herb" to "celestial_herb_seed",
        "lemon" to "lemon_sapling",
        "pumpkin" to "pumpkin_seed"
    )

    fun startSkillAction(skillType: SkillType, itemId: String) {
        val characterId = _currentCharacterId.value ?: return
        val action = ActionCatalog.find(skillType, itemId) ?: return
        val requiredSeedId = farmingSeedRequirements[itemId]
        if (requiredSeedId != null) {
            val availableSeeds = inventoryService.inventoryFor(characterId).quantityOf(requiredSeedId)
            if (availableSeeds <= 0) return
        }
        // Starting a skill stops any active combat session - only one
        // activity can run at a time.
        leaveCombatZone()
        offlineIdleService.stopQueue(characterId)
        offlineIdleService.startSkillingQueue(characterId, skillType.name, itemId, action.secondsPerAction)
        offlineIdleService.recordLastSeen(characterId)
        checkForRecentSales(characterId)
        skillActionProgressSeconds = 0
        refreshActiveQueue()
    }

    fun stopSkillAction() {
        val characterId = _currentCharacterId.value ?: return
        offlineIdleService.stopQueue(characterId)
        skillActionProgressSeconds = 0
        refreshActiveQueue()
    }

    private fun tickSkilling() {
        val characterId = _currentCharacterId.value ?: return
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.SkillingQueue ?: return

        skillActionProgressSeconds += 1
        if (skillActionProgressSeconds < queue.secondsPerAction) return

        val actionsCompleted = skillActionProgressSeconds / queue.secondsPerAction
        skillActionProgressSeconds %= queue.secondsPerAction

        val skillType = SkillType.valueOf(queue.skillId)
        val action = ActionCatalog.find(skillType, queue.itemId)
        if (action != null) {
            val inventory = inventoryService.inventoryFor(characterId)
            val requiredSeedId = farmingSeedRequirements[queue.itemId]
            val effectiveActions = if (requiredSeedId != null) {
                minOf(actionsCompleted, inventory.quantityOf(requiredSeedId).toLong())
            } else {
                actionsCompleted
            }
            if (effectiveActions > 0) {
                if (requiredSeedId != null) {
                    inventory.removeItem(requiredSeedId, effectiveActions.toInt())
                }
                progressionService.grantXp(characterId, skillType, action.xpPerAction * effectiveActions)
                inventory.addItem(queue.itemId, effectiveActions.toInt())
                if (skillType == SkillType.MINING) {
                    MiningBonusGemTable.rollAndGrant(inventory, effectiveActions.toInt())
                }
            }
            if (requiredSeedId != null && effectiveActions < actionsCompleted) {
                // Ran out of seeds mid-batch - stop the queue instead of spinning uselessly.
                offlineIdleService.stopQueue(characterId)
                skillActionProgressSeconds = 0
            }
            refreshSkills()
            refreshInventory()
        }
    }'''
content = content.replace(anchor, replacement, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("patch_require_seed_for_farming.py applied cleanly.")
