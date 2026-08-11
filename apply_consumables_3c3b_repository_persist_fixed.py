"""
Corrected version of apply_consumables_3c3_repository_persist.py -- the
original guessed that file.writeText() immediately followed the
equippedSlots block, which was wrong on two counts: the real variable is
saveFile (not file), and there's a full marketAccounts/marketOrders/
marketPriceHistory serialization block in between that was never seen.
The original aborted safely (nothing was written), so this is safe to
run in its place. The save() signature, load()-side, and SavedGameState
class edits were already correct and are unchanged here.

Run from repo root: python3 apply_consumables_3c3b_repository_persist_fixed.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/GameStateRepository.kt")

OLD_SAVE_SIG = '''        inventoryItems: List<InventorySlotExport>,
        equippedSlots: List<EquippedSlotExport>,
        marketAccounts: List<PlayerEconomyAccountExport>,
        marketOrders: List<MarketOrderExport>,
        marketPriceHistory: List<PriceHistoryExport>
    ) {
        val root = JSONObject()'''
NEW_SAVE_SIG = '''        inventoryItems: List<InventorySlotExport>,
        equippedSlots: List<EquippedSlotExport>,
        loadoutSettings: List<LoadoutSettingsExport>,
        marketAccounts: List<PlayerEconomyAccountExport>,
        marketOrders: List<MarketOrderExport>,
        marketPriceHistory: List<PriceHistoryExport>
    ) {
        val root = JSONObject()'''

OLD_SAVE_WRITE = '''        root.put("equippedSlots", equippedArray)

        val marketAccountsArray = JSONArray()'''
NEW_SAVE_WRITE = '''        root.put("equippedSlots", equippedArray)

        val loadoutSettingsArray = JSONArray()
        loadoutSettings.forEach { entry ->
            val obj = JSONObject()
            obj.put("characterId", entry.characterId)
            obj.put("selectedFoodId", entry.selectedFoodId ?: JSONObject.NULL)
            obj.put("selectedPotionId", entry.selectedPotionId ?: JSONObject.NULL)
            obj.put("potionTimerRemainingSeconds", entry.potionTimerRemainingSeconds)
            obj.put("autoHealThresholdPercent", entry.autoHealThresholdPercent)
            obj.put("autoFleeThresholdPercent", entry.autoFleeThresholdPercent)
            loadoutSettingsArray.put(obj)
        }
        root.put("loadoutSettings", loadoutSettingsArray)

        val marketAccountsArray = JSONArray()'''

OLD_LOAD_READ = '''        return SavedGameState(
            accounts, characters, skills, skillingQueues, craftingQueues, lastSeen, inventoryItems, equippedSlots,
            marketAccounts, marketOrders, marketPriceHistory
        )'''
NEW_LOAD_READ = '''        val loadoutSettings = mutableListOf<LoadoutSettingsExport>()
        val loadoutSettingsArray = root.optJSONArray("loadoutSettings") ?: JSONArray()
        for (i in 0 until loadoutSettingsArray.length()) {
            val obj = loadoutSettingsArray.getJSONObject(i)
            loadoutSettings.add(
                LoadoutSettingsExport(
                    characterId = obj.getString("characterId"),
                    selectedFoodId = if (obj.isNull("selectedFoodId")) null else obj.getString("selectedFoodId"),
                    selectedPotionId = if (obj.isNull("selectedPotionId")) null else obj.getString("selectedPotionId"),
                    potionTimerRemainingSeconds = obj.getInt("potionTimerRemainingSeconds"),
                    autoHealThresholdPercent = obj.getInt("autoHealThresholdPercent"),
                    autoFleeThresholdPercent = obj.getInt("autoFleeThresholdPercent")
                )
            )
        }

        return SavedGameState(
            accounts, characters, skills, skillingQueues, craftingQueues, lastSeen, inventoryItems, equippedSlots,
            loadoutSettings, marketAccounts, marketOrders, marketPriceHistory
        )'''

OLD_STATE_CLASS = '''    val inventoryItems: List<InventorySlotExport>,
    val equippedSlots: List<EquippedSlotExport>,
    val marketAccounts: List<PlayerEconomyAccountExport>,'''
NEW_STATE_CLASS = '''    val inventoryItems: List<InventorySlotExport>,
    val equippedSlots: List<EquippedSlotExport>,
    val loadoutSettings: List<LoadoutSettingsExport>,
    val marketAccounts: List<PlayerEconomyAccountExport>,'''


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

    if "loadoutSettings: List<LoadoutSettingsExport>" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    content = replace_once(content, OLD_SAVE_SIG, NEW_SAVE_SIG, "save() signature")
    content = replace_once(content, OLD_SAVE_WRITE, NEW_SAVE_WRITE, "save() JSON write")
    content = replace_once(content, OLD_LOAD_READ, NEW_LOAD_READ, "load() JSON read + SavedGameState call")
    content = replace_once(content, OLD_STATE_CLASS, NEW_STATE_CLASS, "SavedGameState class field")

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
