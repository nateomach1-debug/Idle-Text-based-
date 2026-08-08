"""
Fix (2/2): wires the Equipment tab and Inventory's "Equip" button to the
real equip/unequip functions added in step 1/2, and replaces the
hardcoded demoEquipped() fake loadout with the live equippedItems
StateFlow. Also removes demoEquipped() itself since nothing references it
anymore.

Run from repo root: python3 apply_equip_2_mainactivity.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")

OLD_EQUIPPED_LINE = "    val equipped = remember { demoEquipped() }"
NEW_EQUIPPED_LINE = '''    val equippedBackend by gameViewModel.equippedItems.collectAsState()
    val equipped = remember(equippedBackend) {
        EquipSlotUi.values().associateWith { uiSlot ->
            equippedBackend[EquipSlot.valueOf(uiSlot.name)]?.let { itemId ->
                ItemCatalog.find(itemId)?.let { def -> EquippedItemInfo(itemId, def.name) }
            }
        }
    }'''

OLD_ONEQUIP = "                                    onEquipItem = { },"
NEW_ONEQUIP = "                                    onEquipItem = { itemId -> gameViewModel.equipItem(itemId) },"

OLD_ONSLOTTAPPED = "                                    onSlotTapped = { }"
NEW_ONSLOTTAPPED = "                                    onSlotTapped = { slot -> gameViewModel.unequipSlot(EquipSlot.valueOf(slot.name)) }"

OLD_DEMOEQUIPPED_FN = '''private fun demoEquipped(): Map<EquipSlotUi, EquippedItemInfo?> = mapOf(
    EquipSlotUi.WEAPON to EquippedItemInfo("bronze_sword", "Bronze Sword"),
    EquipSlotUi.HELMET to null,
    EquipSlotUi.CHESTPLATE to null,
    EquipSlotUi.GLOVES to null,
    EquipSlotUi.BOOTS to EquippedItemInfo("leather_boots_common", "Leather Boots"),
    EquipSlotUi.NECKLACE to null,
    EquipSlotUi.RING_1 to null,
    EquipSlotUi.RING_2 to null,
    EquipSlotUi.TOOL to EquippedItemInfo("pickaxe_bronze", "Bronze Pickaxe")
)
'''
NEW_DEMOEQUIPPED_FN = ""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 0:
        raise SystemExit(f"ABORT: could not find expected block for '{label}'. No changes written.")
    if count > 1:
        raise SystemExit(f"ABORT: found {count} matches for '{label}', expected exactly 1. No changes written.")
    return text.replace(old, new, 1)


def main() -> None:
    if not TARGET.exists():
        raise SystemExit(f"ABORT: could not find {TARGET} from the current directory. Run this from the repo root.")

    content = TARGET.read_text()

    if "equippedBackend" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    content = replace_once(content, OLD_EQUIPPED_LINE, NEW_EQUIPPED_LINE, "equipped state (demoEquipped -> real StateFlow)")
    content = replace_once(content, OLD_ONEQUIP, NEW_ONEQUIP, "onEquipItem callback")
    content = replace_once(content, OLD_ONSLOTTAPPED, NEW_ONSLOTTAPPED, "onSlotTapped callback")
    content = replace_once(content, OLD_DEMOEQUIPPED_FN, NEW_DEMOEQUIPPED_FN, "demoEquipped() function removal")

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
