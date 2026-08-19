path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(path, "r") as f:
    content = f.read()

old_craft = (
    "    fun startCraftingAction(itemId: String, targetQuantity: Int? = null) {\n"
    "        val characterId = _currentCharacterId.value ?: return\n"
    "        val recipe = RecipeCatalog.forOutput(itemId) ?: return\n"
    "        offlineIdleService.stopQueue(characterId)\n"
)
new_craft = (
    "    fun startCraftingAction(itemId: String, targetQuantity: Int? = null) {\n"
    "        val characterId = _currentCharacterId.value ?: return\n"
    "        val recipe = RecipeCatalog.forOutput(itemId) ?: return\n"
    "        // Starting crafting stops any active combat session - only one\n"
    "        // activity can run at a time.\n"
    "        leaveCombatZone()\n"
    "        offlineIdleService.stopQueue(characterId)\n"
)
assert old_craft in content, "startCraftingAction pattern not found"
assert content.count(old_craft) == 1, "startCraftingAction pattern not unique"
content = content.replace(old_craft, new_craft)

with open(path, "w") as f:
    f.write(content)

print("Patched startCraftingAction to leave combat before starting a craft queue.")
print("Mutual exclusion is now complete: entering combat stops skilling/crafting,")
print("starting skilling stops combat, starting crafting stops combat.")
print("(offlineIdleService.stopQueue already handles skilling<->crafting exclusion")
print("on its own, since both share the same queue slot.)")
