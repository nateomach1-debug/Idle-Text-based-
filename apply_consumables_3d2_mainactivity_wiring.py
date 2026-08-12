"""
Food/Potion feature, patch 3d-2/2: wires both LoadoutScreen call sites
(reachable from Combat and Inventory tabs) to the real data from
GameViewModel.loadoutSettings (patch 3c) instead of the old
loadoutStyle/loadoutWeaponId/autoHeal/autoFlee local state and
demoWeapons(). Adds availableFoodOptions/availablePotionOptions derived
from the live inventory, filtered by ConsumableType.

Note: this leaves loadoutStyle/loadoutWeaponId/autoHeal/autoFlee and
demoWeapons() as unused dead code -- harmless (Kotlin doesn't error on
unused locals), worth a cleanup pass later but not blocking here.

Run from repo root: python3 apply_consumables_3d2_mainactivity_wiring.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")

OLD_DERIVED_STATE = '''    val equippedBackend by gameViewModel.equippedItems.collectAsState()
    val equipped = remember(equippedBackend) {
        EquipSlotUi.values().associateWith { uiSlot ->
            equippedBackend[EquipSlot.valueOf(uiSlot.name)]?.let { itemId ->
                ItemCatalog.find(itemId)?.let { def -> EquippedItemInfo(itemId, def.name) }
            }
        }
    }'''
NEW_DERIVED_STATE = '''    val equippedBackend by gameViewModel.equippedItems.collectAsState()
    val equipped = remember(equippedBackend) {
        EquipSlotUi.values().associateWith { uiSlot ->
            equippedBackend[EquipSlot.valueOf(uiSlot.name)]?.let { itemId ->
                ItemCatalog.find(itemId)?.let { def -> EquippedItemInfo(itemId, def.name) }
            }
        }
    }
    val loadoutSettings by gameViewModel.loadoutSettings.collectAsState()
    val availableFoodOptions = remember(inventoryItemEntries) {
        inventoryItemEntries.mapNotNull { entry ->
            val definition = ItemCatalog.find(entry.itemId)
            if (definition?.consumableType == ConsumableType.FOOD) {
                ConsumableOption(entry.itemId, definition.name, entry.quantity)
            } else null
        }
    }
    val availablePotionOptions = remember(inventoryItemEntries) {
        inventoryItemEntries.mapNotNull { entry ->
            val definition = ItemCatalog.find(entry.itemId)
            if (definition?.consumableType == ConsumableType.POTION) {
                ConsumableOption(entry.itemId, definition.name, entry.quantity)
            } else null
        }
    }'''

OLD_COMBAT_LOADOUT = '''                                CombatScreenState.Loadout -> LoadoutScreen(
                                    state = LoadoutState(
                                        loadoutStyle, demoWeapons(loadoutStyle), loadoutWeaponId, autoHeal, autoFlee,
                                        combatViewState == CombatViewState.IN_COMBAT, "Locked during combat"
                                    ),
                                    onBack = { combatScreenState = CombatScreenState.ZoneSelect },
                                    onStyleSelected = { loadoutStyle = it; loadoutWeaponId = demoWeapons(it).firstOrNull()?.itemId },
                                    onWeaponSelected = { loadoutWeaponId = it },
                                    onAutoHealChanged = { autoHeal = it },
                                    onAutoFleeChanged = { autoFlee = it }
                                )'''
NEW_COMBAT_LOADOUT = '''                                CombatScreenState.Loadout -> LoadoutScreen(
                                    state = LoadoutState(
                                        availableFoodOptions, loadoutSettings.selectedFoodId,
                                        availablePotionOptions, loadoutSettings.selectedPotionId,
                                        loadoutSettings.potionTimerRemainingSeconds,
                                        loadoutSettings.autoHealThresholdPercent, loadoutSettings.autoFleeThresholdPercent
                                    ),
                                    onBack = { combatScreenState = CombatScreenState.ZoneSelect },
                                    onFoodSelected = { gameViewModel.selectFood(it) },
                                    onPotionSelected = { gameViewModel.selectPotion(it) },
                                    onAutoHealChanged = { gameViewModel.setAutoHealThreshold(it) },
                                    onAutoFleeChanged = { gameViewModel.setAutoFleeThreshold(it) }
                                )'''

OLD_INVENTORY_LOADOUT = '''                                InventoryScreenState.Loadout -> LoadoutScreen(
                                    state = LoadoutState(
                                        loadoutStyle, demoWeapons(loadoutStyle), loadoutWeaponId, autoHeal, autoFlee,
                                        combatViewState == CombatViewState.IN_COMBAT, "Locked during combat"
                                    ),
                                    onBack = { inventoryScreenState = InventoryScreenState.Items },
                                    onStyleSelected = { loadoutStyle = it; loadoutWeaponId = demoWeapons(it).firstOrNull()?.itemId },
                                    onWeaponSelected = { loadoutWeaponId = it },
                                    onAutoHealChanged = { autoHeal = it },
                                    onAutoFleeChanged = { autoFlee = it }
                                )'''
NEW_INVENTORY_LOADOUT = '''                                InventoryScreenState.Loadout -> LoadoutScreen(
                                    state = LoadoutState(
                                        availableFoodOptions, loadoutSettings.selectedFoodId,
                                        availablePotionOptions, loadoutSettings.selectedPotionId,
                                        loadoutSettings.potionTimerRemainingSeconds,
                                        loadoutSettings.autoHealThresholdPercent, loadoutSettings.autoFleeThresholdPercent
                                    ),
                                    onBack = { inventoryScreenState = InventoryScreenState.Items },
                                    onFoodSelected = { gameViewModel.selectFood(it) },
                                    onPotionSelected = { gameViewModel.selectPotion(it) },
                                    onAutoHealChanged = { gameViewModel.setAutoHealThreshold(it) },
                                    onAutoFleeChanged = { gameViewModel.setAutoFleeThreshold(it) }
                                )'''


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

    if "availableFoodOptions" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    content = replace_once(content, OLD_DERIVED_STATE, NEW_DERIVED_STATE, "derived food/potion state")
    content = replace_once(content, OLD_COMBAT_LOADOUT, NEW_COMBAT_LOADOUT, "Combat tab LoadoutScreen call site")
    content = replace_once(content, OLD_INVENTORY_LOADOUT, NEW_INVENTORY_LOADOUT, "Inventory tab LoadoutScreen call site")

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
