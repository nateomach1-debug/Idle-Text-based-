"""
Fix (1/2): the Equipment tab and Inventory's "Equip" buttons were both
no-ops -- the real InventoryService equip/unequip logic already existed on
the Inventory class, and GameViewModel already had a live equippedItems
StateFlow kept in sync via refreshInventory(), but nothing in the UI layer
ever actually called equip()/unequip().

This adds equipItem(itemId) and unequipSlot(slot) wrapper functions to
GameViewModel. Step 2/2 wires MainActivity's UI callbacks to call them and
replaces the hardcoded demoEquipped() with the real StateFlow.

Note: "canChangeSlot" is passed as { true } (always allowed) since there's
no real combat system yet to gate equipment changes against -- this should
be revisited once real combat is built (separate item on the review list).

"Overall player level" (used for items with no specific skillRequired) is
computed as the highest of all current skill levels, since this codebase
doesn't have an existing "character level" concept -- flagging this
assumption in case a different definition is wanted.

Run from repo root: python3 apply_equip_1_gameviewmodel.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")

OLD = '''    fun refreshInventory() {
        val characterId = _currentCharacterId.value ?: return
        val inv = inventoryService.inventoryFor(characterId)
        _inventoryItems.value = inv.allItems()
        _equippedItems.value = inv.allEquipped()
    }'''

NEW = '''    fun refreshInventory() {
        val characterId = _currentCharacterId.value ?: return
        val inv = inventoryService.inventoryFor(characterId)
        _inventoryItems.value = inv.allItems()
        _equippedItems.value = inv.allEquipped()
    }

    fun equipItem(itemId: String): ServiceResult<Unit> {
        val characterId = _currentCharacterId.value ?: return ServiceResult.Failure("No character selected.")
        val playerSkillLevels = progressionService.skillBookFor(characterId).all()
            .associate { it.type.name to LevelCurve.levelForXp(it.xp) }
        val playerLevel = playerSkillLevels.values.maxOrNull() ?: 1
        val result = inventoryService.inventoryFor(characterId).equip(itemId, playerLevel, playerSkillLevels) { true }
        if (result is ServiceResult.Success) refreshInventory()
        return result
    }

    fun unequipSlot(slot: EquipSlot): ServiceResult<Unit> {
        val characterId = _currentCharacterId.value ?: return ServiceResult.Failure("No character selected.")
        val result = inventoryService.inventoryFor(characterId).unequip(slot) { true }
        if (result is ServiceResult.Success) refreshInventory()
        return result
    }'''


def main() -> None:
    if not TARGET.exists():
        raise SystemExit(f"ABORT: could not find {TARGET} from the current directory. Run this from the repo root.")

    content = TARGET.read_text()

    if "fun equipItem(" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    count = content.count(OLD)
    if count == 0:
        raise SystemExit("ABORT: could not find the expected refreshInventory() block. No changes written.")
    if count > 1:
        raise SystemExit(f"ABORT: found {count} matches, expected exactly 1. No changes written.")

    content = content.replace(OLD, NEW, 1)

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
