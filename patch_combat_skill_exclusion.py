path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(path, "r") as f:
    content = f.read()

# 1. enterCombatZone: stop any active skilling/crafting queue before entering combat.
old_enter = (
    "    fun enterCombatZone(zoneId: String): ServiceResult<CombatSession> {\n"
    "        val characterId = _currentCharacterId.value ?: return ServiceResult.Failure(\"No character selected.\")\n"
    "        combatService.stateFor(characterId, maxHpFor(characterId))\n"
)
new_enter = (
    "    fun enterCombatZone(zoneId: String): ServiceResult<CombatSession> {\n"
    "        val characterId = _currentCharacterId.value ?: return ServiceResult.Failure(\"No character selected.\")\n"
    "        // Entering combat stops any active skilling/crafting queue - only one\n"
    "        // activity can run at a time.\n"
    "        offlineIdleService.stopQueue(characterId)\n"
    "        skillActionProgressSeconds = 0\n"
    "        craftActionProgressSeconds = 0\n"
    "        refreshActiveQueue()\n"
    "        combatService.stateFor(characterId, maxHpFor(characterId))\n"
)
assert old_enter in content, "enterCombatZone pattern not found"
assert content.count(old_enter) == 1, "enterCombatZone pattern not unique"
content = content.replace(old_enter, new_enter)

# 2. startSkillAction: leave combat zone before starting a skilling queue.
old_skill = (
    "    fun startSkillAction(skillType: SkillType, itemId: String) {\n"
    "        val characterId = _currentCharacterId.value ?: return\n"
    "        val action = ActionCatalog.find(skillType, itemId) ?: return\n"
    "        offlineIdleService.stopQueue(characterId)\n"
)
new_skill = (
    "    fun startSkillAction(skillType: SkillType, itemId: String) {\n"
    "        val characterId = _currentCharacterId.value ?: return\n"
    "        val action = ActionCatalog.find(skillType, itemId) ?: return\n"
    "        // Starting a skill stops any active combat session - only one\n"
    "        // activity can run at a time.\n"
    "        leaveCombatZone()\n"
    "        offlineIdleService.stopQueue(characterId)\n"
)
assert old_skill in content, "startSkillAction pattern not found"
assert content.count(old_skill) == 1, "startSkillAction pattern not unique"
content = content.replace(old_skill, new_skill)

with open(path, "w") as f:
    f.write(content)

print("Patched enterCombatZone and startSkillAction for mutual exclusion.")
print("NOTE: crafting's start function was not patched yet - its exact name/body")
print("still needs to be found and handled the same way (stop combat on craft start,")
print("stop skilling on craft start, since craftItems()/whatever starts it also")
print("needs the same leaveCombatZone() + offlineIdleService.stopQueue() calls).")
