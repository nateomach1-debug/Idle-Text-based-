"""
Food/Potion feature, patch 3c-1/3: move autoHeal/autoFlee thresholds onto
the per-character Inventory (correcting patch 3b's global-scoping design
mistake -- every other setting in this game is per-character), and add
the persistence plumbing (LoadoutSettingsExport + export/restore) needed
to save/restore food/potion selections and thresholds.

Run from repo root: python3 apply_consumables_3c1_inventory_persist.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/ItemsEquipmentSystem.kt")

OLD_EXPORT_CLASSES = '''data class InventorySlotExport(val characterId: String, val itemId: String, val quantity: Int)
data class EquippedSlotExport(val characterId: String, val slot: String, val itemId: String)'''
NEW_EXPORT_CLASSES = '''data class InventorySlotExport(val characterId: String, val itemId: String, val quantity: Int)
data class EquippedSlotExport(val characterId: String, val slot: String, val itemId: String)
data class LoadoutSettingsExport(
    val characterId: String,
    val selectedFoodId: String?,
    val selectedPotionId: String?,
    val potionTimerRemainingSeconds: Int,
    val autoHealThresholdPercent: Int,
    val autoFleeThresholdPercent: Int
)'''

OLD_INVENTORY_HEADER = '''    var selectedFoodId: String? = null,
    var selectedPotionId: String? = null,
    var potionTimerRemainingSeconds: Int = 0
) {'''
NEW_INVENTORY_HEADER = '''    var selectedFoodId: String? = null,
    var selectedPotionId: String? = null,
    var potionTimerRemainingSeconds: Int = 0,
    var autoHealThresholdPercent: Int = 30,
    var autoFleeThresholdPercent: Int = 10
) {'''

OLD_RESTORE_EQUIPPED_SVC = '''    fun restoreEquipped(export: EquippedSlotExport) {
        inventoryFor(export.characterId).restoreEquipped(EquipSlot.valueOf(export.slot), export.itemId)
    }
}'''
NEW_RESTORE_EQUIPPED_SVC = '''    fun restoreEquipped(export: EquippedSlotExport) {
        inventoryFor(export.characterId).restoreEquipped(EquipSlot.valueOf(export.slot), export.itemId)
    }

    fun exportAllLoadoutSettings(): List<LoadoutSettingsExport> = inventories.map { (characterId, inv) ->
        LoadoutSettingsExport(
            characterId, inv.selectedFoodId, inv.selectedPotionId, inv.potionTimerRemainingSeconds,
            inv.autoHealThresholdPercent, inv.autoFleeThresholdPercent
        )
    }

    fun restoreLoadoutSettings(export: LoadoutSettingsExport) {
        val inv = inventoryFor(export.characterId)
        inv.selectedFoodId = export.selectedFoodId
        inv.selectedPotionId = export.selectedPotionId
        inv.potionTimerRemainingSeconds = export.potionTimerRemainingSeconds
        inv.autoHealThresholdPercent = export.autoHealThresholdPercent
        inv.autoFleeThresholdPercent = export.autoFleeThresholdPercent
    }
}'''


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

    if "class LoadoutSettingsExport" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    content = replace_once(content, OLD_EXPORT_CLASSES, NEW_EXPORT_CLASSES, "LoadoutSettingsExport class")
    content = replace_once(content, OLD_INVENTORY_HEADER, NEW_INVENTORY_HEADER, "Inventory autoHeal/autoFlee fields")
    content = replace_once(content, OLD_RESTORE_EQUIPPED_SVC, NEW_RESTORE_EQUIPPED_SVC, "InventoryService export/restore loadout settings")

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
