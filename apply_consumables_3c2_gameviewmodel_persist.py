"""
Food/Potion feature, patch 3c-2/3: corrects the global-scoped
autoHeal/autoFlee StateFlows from patch 3b to be per-character (reading
from the Inventory fields added in 3c-1), adds a LoadoutSettingsSnapshot
StateFlow for the UI to observe, and wires the new export/restore
functions into saveGame()/loadGame().

Run from repo root: python3 apply_consumables_3c2_gameviewmodel_persist.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")

OLD_FIELDS = '''    private val _autoHealThresholdPercent = MutableStateFlow(30)
    val autoHealThresholdPercent: StateFlow<Int> = _autoHealThresholdPercent.asStateFlow()

    private val _autoFleeThresholdPercent = MutableStateFlow(10)
    val autoFleeThresholdPercent: StateFlow<Int> = _autoFleeThresholdPercent.asStateFlow()

    fun setAutoHealThreshold(percent: Int) {
        _autoHealThresholdPercent.value = percent.coerceIn(0, 100)
    }

    fun setAutoFleeThreshold(percent: Int) {
        _autoFleeThresholdPercent.value = percent.coerceIn(0, 100)
    }'''
NEW_FIELDS = '''    data class LoadoutSettingsSnapshot(
        val selectedFoodId: String?,
        val selectedPotionId: String?,
        val potionTimerRemainingSeconds: Int,
        val autoHealThresholdPercent: Int,
        val autoFleeThresholdPercent: Int
    )

    private val _loadoutSettings = MutableStateFlow(LoadoutSettingsSnapshot(null, null, 0, 30, 10))
    val loadoutSettings: StateFlow<LoadoutSettingsSnapshot> = _loadoutSettings.asStateFlow()

    fun setAutoHealThreshold(percent: Int) {
        val characterId = _currentCharacterId.value ?: return
        inventoryService.inventoryFor(characterId).autoHealThresholdPercent = percent.coerceIn(0, 100)
        refreshInventory()
    }

    fun setAutoFleeThreshold(percent: Int) {
        val characterId = _currentCharacterId.value ?: return
        inventoryService.inventoryFor(characterId).autoFleeThresholdPercent = percent.coerceIn(0, 100)
        refreshInventory()
    }'''

OLD_TICK = "            if (hpPercent <= _autoHealThresholdPercent.value) {"
NEW_TICK = "            if (hpPercent <= inventory.autoHealThresholdPercent) {"

OLD_REFRESH = '''    fun refreshInventory() {
        val characterId = _currentCharacterId.value ?: return
        val inv = inventoryService.inventoryFor(characterId)
        _inventoryItems.value = inv.allItems()
        _equippedItems.value = inv.allEquipped()
    }'''
NEW_REFRESH = '''    fun refreshInventory() {
        val characterId = _currentCharacterId.value ?: return
        val inv = inventoryService.inventoryFor(characterId)
        _inventoryItems.value = inv.allItems()
        _equippedItems.value = inv.allEquipped()
        _loadoutSettings.value = LoadoutSettingsSnapshot(
            inv.selectedFoodId, inv.selectedPotionId, inv.potionTimerRemainingSeconds,
            inv.autoHealThresholdPercent, inv.autoFleeThresholdPercent
        )
    }'''

OLD_SAVE = '''            inventoryService.exportAllItems(),
            inventoryService.exportAllEquipped(),
            marketService.exportAccounts(),'''
NEW_SAVE = '''            inventoryService.exportAllItems(),
            inventoryService.exportAllEquipped(),
            inventoryService.exportAllLoadoutSettings(),
            marketService.exportAccounts(),'''

OLD_LOAD = '''        saved.inventoryItems.forEach { inventoryService.restoreItem(it) }
        saved.equippedSlots.forEach { inventoryService.restoreEquipped(it) }
        saved.marketAccounts.forEach { marketService.restoreAccount(it) }'''
NEW_LOAD = '''        saved.inventoryItems.forEach { inventoryService.restoreItem(it) }
        saved.equippedSlots.forEach { inventoryService.restoreEquipped(it) }
        saved.loadoutSettings.forEach { inventoryService.restoreLoadoutSettings(it) }
        saved.marketAccounts.forEach { marketService.restoreAccount(it) }'''


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

    if "LoadoutSettingsSnapshot" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    content = replace_once(content, OLD_FIELDS, NEW_FIELDS, "per-character threshold fields")
    content = replace_once(content, OLD_TICK, NEW_TICK, "tickConsumables per-character read")
    content = replace_once(content, OLD_REFRESH, NEW_REFRESH, "refreshInventory loadoutSettings")
    content = replace_once(content, OLD_SAVE, NEW_SAVE, "saveGame loadout export")
    content = replace_once(content, OLD_LOAD, NEW_LOAD, "loadGame loadout restore")

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
