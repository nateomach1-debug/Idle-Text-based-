"""
Item 11: eat food outside combat via the inventory's existing "Use" button.

The Use button (InventoryScreen.kt) already exists and already calls
onUseItem(item.itemId) for any consumable - but onUseItem was wired to
an empty no-op lambda in MainActivity.kt, so tapping it currently does
nothing at all, in or out of combat.

This adds a new GameViewModel.useInventoryItem(itemId) function that:
  - Looks up the item's definition via ItemCatalog.find(itemId)
  - Only acts if it's FOOD (potions have a different buff-timer mechanic,
    out of scope here - tapping Use on a potion remains a no-op for now)
  - Removes 1 from inventory via the existing generic removeItem(itemId, qty)
  - Heals via the existing combatService.healCharacter(characterId, amount)
    (same call already used by the in-combat auto-heal tick, so it works
    identically whether in combat or not)
  - Refreshes inventory state so the quantity updates on screen

Then wires MainActivity's onUseItem = { } to call it.

Guarded with asserts.
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"

# ---------------------------------------------------------------
# 1. GameViewModel.kt - add useInventoryItem()
# ---------------------------------------------------------------
path = os.path.join(BASE, "GameViewModel.kt")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = (
    "    fun selectPotion(itemId: String?) {\n"
    "        val characterId = _currentCharacterId.value ?: return\n"
    "        inventoryService.inventoryFor(characterId).selectPotion(itemId)\n"
    "        refreshInventory()\n"
    "    }\n"
)
new = (
    "    fun selectPotion(itemId: String?) {\n"
    "        val characterId = _currentCharacterId.value ?: return\n"
    "        inventoryService.inventoryFor(characterId).selectPotion(itemId)\n"
    "        refreshInventory()\n"
    "    }\n"
    "\n"
    "    fun useInventoryItem(itemId: String) {\n"
    "        val characterId = _currentCharacterId.value ?: return\n"
    "        val definition = ItemCatalog.find(itemId) ?: return\n"
    "        if (definition.consumableType != ConsumableType.FOOD) return\n"
    "        val inventory = inventoryService.inventoryFor(characterId)\n"
    "        val removed = inventory.removeItem(itemId, 1)\n"
    "        if (removed is ServiceResult.Success) {\n"
    "            combatService.healCharacter(characterId, definition.healAmount ?: 0)\n"
    "            refreshInventory()\n"
    "        }\n"
    "    }\n"
)

assert old in content, "selectPotion anchor not found in GameViewModel.kt"
assert content.count(old) == 1, "selectPotion anchor not unique"
content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched GameViewModel.kt: added useInventoryItem().")

# ---------------------------------------------------------------
# 2. MainActivity.kt - wire onUseItem to the new function
# ---------------------------------------------------------------
path = os.path.join(BASE, "MainActivity.kt")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "                                    onUseItem = { },\n"
new = "                                    onUseItem = { itemId -> gameViewModel.useInventoryItem(itemId) },\n"

assert old in content, "onUseItem anchor not found in MainActivity.kt"
assert content.count(old) == 1, "onUseItem anchor not unique"
content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched MainActivity.kt: onUseItem now calls gameViewModel.useInventoryItem(itemId).")
