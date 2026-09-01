# PART P: Add offline-progress resolution (and training-skill restoration) for
# the "app cold-starts directly into AppFlowState.InGame" path - previously
# resolveOfflineRewardsAndSync() only ever ran from inside selectCharacter(),
# which never fires on this path at all (only on explicit character-select tap
# or new-character creation).

gvm_path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(gvm_path, encoding="utf-8") as f:
    content = f.read()

anchor = "    private fun resolveOfflineRewardsAndSync(characterId: String) {"
count = content.count(anchor)
assert count == 1, f"Expected 1 match, found {count}."
replacement = '''    // Handles the case where the app cold-starts directly into AppFlowState.InGame
    // (a character id was already cached locally) - selectCharacter() is never
    // called on this path, so nothing would otherwise trigger offline-progress
    // resolution or restore the persisted training skill for this session.
    fun resumeCurrentCharacterIfNeeded() {
        val characterId = _currentCharacterId.value ?: return
        val restoredTrainingSkillId = inventoryService.inventoryFor(characterId).trainingSkillId
        val restoredTrainingSkill = restoredTrainingSkillId?.let {
            runCatching { SkillType.valueOf(it) }.getOrNull()
        } ?: SkillType.ATTACK
        setTrainingSkill(restoredTrainingSkill)
        resolveOfflineRewardsAndSync(characterId)
    }

''' + anchor
content = content.replace(anchor, replacement, 1)

with open(gvm_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part P (1/2 - GameViewModel.kt) applied cleanly.")

main_path = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(main_path, encoding="utf-8") as f:
    content = f.read()

anchor2 = '''    LaunchedEffect(Unit) {
        gameViewModel.loadGame()
        if (flowState == AppFlowState.Login) {
            val autoAccount = gameViewModel.tryAutoLogin()
            if (autoAccount != null) {
                val chars = gameViewModel.accountService.charactersFor(autoAccount.id)
                flowState = if (chars.isEmpty()) AppFlowState.CharacterCreate else AppFlowState.CharacterSelect
            }
        }
    }'''
count = content.count(anchor2)
assert count == 1, f"Expected 1 match, found {count}."
replacement2 = '''    LaunchedEffect(Unit) {
        gameViewModel.loadGame()
        if (flowState == AppFlowState.Login) {
            val autoAccount = gameViewModel.tryAutoLogin()
            if (autoAccount != null) {
                val chars = gameViewModel.accountService.charactersFor(autoAccount.id)
                flowState = if (chars.isEmpty()) AppFlowState.CharacterCreate else AppFlowState.CharacterSelect
            }
        } else if (flowState == AppFlowState.InGame) {
            gameViewModel.resumeCurrentCharacterIfNeeded()
        }
    }'''
content = content.replace(anchor2, replacement2, 1)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part P (2/2 - MainActivity.kt) applied cleanly.")
