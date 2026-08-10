"""
Food/Potion feature, patch 3a/4 (of the LoadoutScreen redesign work):
backend foundation for the Food/Potion slots.

Inventory gets three new fields (selectedFoodId, selectedPotionId,
potionTimerRemainingSeconds) plus selectFood()/selectPotion() (validated
against ConsumableType so you can't put a sword in the food slot) and
consumeSelectedFood()/consumeSelectedPotion() (decrement quantity, return
the item's effect data). These aren't "equipped" like gear -- nothing
leaves your inventory slot, they just mark which item to auto-consume.

CombatService gets healCharacter(), mirroring the existing
applyDamageToCharacter() but adding instead of subtracting, capped at
max HP. Real and callable now; naturally dormant until something deals
damage, since nothing currently calls it.

Run from repo root: python3 apply_consumables_3a_inventory_combat.py
"""
from pathlib import Path

INVENTORY_TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/ItemsEquipmentSystem.kt")
COMBAT_TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/CombatSystem.kt")

OLD_CLASS_HEADER = '''class Inventory(
    var maxSlots: Int = 100,
    private val entries: MutableMap<String, InventorySlotEntry> = mutableMapOf(),
    private val equipped: MutableMap<EquipSlot, String> = mutableMapOf()
) {'''
NEW_CLASS_HEADER = '''class Inventory(
    var maxSlots: Int = 100,
    private val entries: MutableMap<String, InventorySlotEntry> = mutableMapOf(),
    private val equipped: MutableMap<EquipSlot, String> = mutableMapOf(),
    var selectedFoodId: String? = null,
    var selectedPotionId: String? = null,
    var potionTimerRemainingSeconds: Int = 0
) {'''

OLD_RESTORE_EQUIPPED = '''    fun restoreEquipped(slot: EquipSlot, itemId: String) {
        equipped[slot] = itemId
    }
}'''
NEW_RESTORE_EQUIPPED = '''    fun restoreEquipped(slot: EquipSlot, itemId: String) {
        equipped[slot] = itemId
    }

    // ---------------- Food / Potion selection ----------------

    fun selectFood(itemId: String?): ServiceResult<Unit> {
        if (itemId != null) {
            val definition = ItemCatalog.find(itemId) ?: return ServiceResult.Failure("Unknown item.")
            if (definition.consumableType != ConsumableType.FOOD) return ServiceResult.Failure("Not a food item.")
        }
        selectedFoodId = itemId
        return ServiceResult.Success(Unit)
    }

    fun selectPotion(itemId: String?): ServiceResult<Unit> {
        if (itemId != null) {
            val definition = ItemCatalog.find(itemId) ?: return ServiceResult.Failure("Unknown item.")
            if (definition.consumableType != ConsumableType.POTION) return ServiceResult.Failure("Not a potion item.")
        }
        selectedPotionId = itemId
        potionTimerRemainingSeconds = 0
        return ServiceResult.Success(Unit)
    }

    fun consumeSelectedFood(): ItemDefinition? {
        val foodId = selectedFoodId ?: return null
        val definition = ItemCatalog.find(foodId) ?: return null
        if (quantityOf(foodId) <= 0) return null
        removeItem(foodId, 1)
        return definition
    }

    fun consumeSelectedPotion(): ItemDefinition? {
        val potionId = selectedPotionId ?: return null
        val definition = ItemCatalog.find(potionId) ?: return null
        if (quantityOf(potionId) <= 0) return null
        removeItem(potionId, 1)
        return definition
    }
}'''

OLD_HEAL = '''    fun resolveRecoveryIfReady(characterId: String, now: Instant = Instant.now()): ServiceResult<CharacterCombatState> {'''
NEW_HEAL = '''    fun healCharacter(characterId: String, amount: Int): ServiceResult<CharacterCombatState> {
        val state = stateFor(characterId)
        state.currentHp = (state.currentHp + amount).coerceAtMost(state.maxHp)
        return ServiceResult.Success(state)
    }

    fun resolveRecoveryIfReady(characterId: String, now: Instant = Instant.now()): ServiceResult<CharacterCombatState> {'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 0:
        raise SystemExit(f"ABORT: could not find expected block for '{label}'. No changes written.")
    if count > 1:
        raise SystemExit(f"ABORT: found {count} matches for '{label}', expected exactly 1. No changes written.")
    return text.replace(old, new, 1)


def main() -> None:
    if not INVENTORY_TARGET.exists():
        raise SystemExit(f"ABORT: could not find {INVENTORY_TARGET} from the current directory. Run this from the repo root.")
    if not COMBAT_TARGET.exists():
        raise SystemExit(f"ABORT: could not find {COMBAT_TARGET} from the current directory. Run this from the repo root.")

    inv_content = INVENTORY_TARGET.read_text()
    combat_content = COMBAT_TARGET.read_text()

    if "selectedFoodId" in inv_content:
        raise SystemExit("ABORT: Inventory patch looks already applied. No changes written.")
    if "fun healCharacter" in combat_content:
        raise SystemExit("ABORT: CombatService patch looks already applied. No changes written.")

    inv_content = replace_once(inv_content, OLD_CLASS_HEADER, NEW_CLASS_HEADER, "Inventory class header")
    inv_content = replace_once(inv_content, OLD_RESTORE_EQUIPPED, NEW_RESTORE_EQUIPPED, "Inventory food/potion methods")
    combat_content = replace_once(combat_content, OLD_HEAL, NEW_HEAL, "CombatService.healCharacter")

    if inv_content.count("{") != inv_content.count("}"):
        raise SystemExit("ABORT: brace mismatch in Inventory file -- refusing to write. No changes written.")
    if combat_content.count("{") != combat_content.count("}"):
        raise SystemExit("ABORT: brace mismatch in CombatSystem file -- refusing to write. No changes written.")

    INVENTORY_TARGET.write_text(inv_content)
    COMBAT_TARGET.write_text(combat_content)
    print(f"OK: patched {INVENTORY_TARGET}")
    print(f"OK: patched {COMBAT_TARGET}")


if __name__ == "__main__":
    main()
