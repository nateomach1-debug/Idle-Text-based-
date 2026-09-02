# PART Q: Move training-skill restoration to run synchronously and immediately
# in selectCharacter() - it was previously gated behind the Supabase auth check,
# so a slow/failed auth handshake (common right after a cold app start) silently
# skipped it every time via the early-return path, leaving trainingSkill stuck
# at its ATTACK default. Also re-applies it for the rare cloud-recovery case
# where the character id changes mid-flow.

gvm_path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(gvm_path, encoding="utf-8") as f:
    content = f.read()

anchor_top = '''    fun selectCharacter(characterId: String) {
        _currentCharacterId.value = characterId

        val selectedCharacter = accountService.charactersFor(_currentAccountId.value ?: "").firstOrNull { it.id == characterId }'''
count = content.count(anchor_top)
assert count == 1, f"Expected 1 match, found {count}."
replacement_top = '''    fun selectCharacter(characterId: String) {
        _currentCharacterId.value = characterId

        // Restore the persisted training skill immediately - this is purely
        // local (no Supabase dependency), so it must run regardless of whether
        // the auth check below succeeds, fails, or times out. Previously this
        // only happened after auth succeeded, so a slow/failed auth handshake
        // (common right after a cold app start) silently skipped it every time
        // via the early-return path, leaving trainingSkill stuck at ATTACK.
        fun restoreTrainingSkillFor(id: String) {
            val restoredTrainingSkillId = inventoryService.inventoryFor(id).trainingSkillId
            val restoredTrainingSkill = restoredTrainingSkillId?.let {
                runCatching { SkillType.valueOf(it) }.getOrNull()
            } ?: SkillType.ATTACK
            setTrainingSkill(restoredTrainingSkill)
        }
        restoreTrainingSkillFor(characterId)

        val selectedCharacter = accountService.charactersFor(_currentAccountId.value ?: "").firstOrNull { it.id == characterId }'''
content = content.replace(anchor_top, replacement_top, 1)

anchor_old_restore = '''                val finalCharacterId = recoveredToRemoteId ?: characterId
                // Restore the persisted training skill for THIS character before
                // resolving offline rewards below - previously trainingSkill stayed
                // at its hardcoded ATTACK default every cold start (never restored
                // anywhere), so offline combat XP always landed on Attack regardless
                // of what the player had actually selected before closing the app.
                val restoredTrainingSkillId = inventoryService.inventoryFor(finalCharacterId).trainingSkillId
                val restoredTrainingSkill = restoredTrainingSkillId?.let {
                    runCatching { SkillType.valueOf(it) }.getOrNull()
                } ?: SkillType.ATTACK
                setTrainingSkill(restoredTrainingSkill)
                // Only one of these ever fires per selection: whichever character id'''
count = content.count(anchor_old_restore)
assert count == 1, f"Expected 1 match, found {count}."
replacement_old_restore = '''                val finalCharacterId = recoveredToRemoteId ?: characterId
                // Only relevant for the rare cloud-recovery case where the character
                // id changed mid-flow - re-apply against the correct (recovered) id.
                if (finalCharacterId != characterId) {
                    restoreTrainingSkillFor(finalCharacterId)
                }
                // Only one of these ever fires per selection: whichever character id'''
content = content.replace(anchor_old_restore, replacement_old_restore, 1)

with open(gvm_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part Q (GameViewModel.kt) applied cleanly.")
