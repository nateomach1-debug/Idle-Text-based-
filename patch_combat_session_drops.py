import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"

def find_file(name):
    for dirpath, _, files in os.walk(ROOT):
        if name in files:
            return os.path.join(dirpath, name)
    raise SystemExit(f"!!! FILE NOT FOUND: {name} !!!")

def guarded_replace(path, old, new, expected_count=1):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    count = content.count(old)
    if count != expected_count:
        raise SystemExit(
            f"!!! ABORTING: expected {expected_count} occurrence(s) of anchor in {path}, found {count} !!!\n"
            f"--- anchor was ---\n{old}\n--- end anchor ---"
        )
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"patched {path} (replaced {count} occurrence(s))")

# ---------------------------------------------------------------------------
# 1. CombatViewScreen.kt - SessionDropEntry, CombatViewData field, panel UI
# ---------------------------------------------------------------------------
combat_view_path = find_file("CombatViewScreen.kt")

data_class_old = """data class CombatViewData(
    val zoneName: String,
    val viewState: CombatViewState,
    val searchEndsAt: Instant?,          // set only when SEARCHING
    val monsterName: String?,            // set only when IN_COMBAT
    val monsterCurrentHp: Int?,
    val monsterMaxHp: Int?,
    val playerCurrentHp: Int,
    val playerMaxHp: Int,
    val lastHitChancePercent: Double?,   // advanced view only
    val lastDamageDealt: Int?,           // advanced view only
    val combatLog: List<CombatLogEntry>
)"""
data_class_new = """data class SessionDropEntry(
    val itemName: String,
    val quantity: Int
)

data class CombatViewData(
    val zoneName: String,
    val viewState: CombatViewState,
    val searchEndsAt: Instant?,          // set only when SEARCHING
    val monsterName: String?,            // set only when IN_COMBAT
    val monsterCurrentHp: Int?,
    val monsterMaxHp: Int?,
    val playerCurrentHp: Int,
    val playerMaxHp: Int,
    val lastHitChancePercent: Double?,   // advanced view only
    val lastDamageDealt: Int?,           // advanced view only
    val combatLog: List<CombatLogEntry>,
    val sessionDrops: List<SessionDropEntry>
)"""
guarded_replace(combat_view_path, data_class_old, data_class_new)

layout_old = """        when (data.viewState) {
            CombatViewState.SEARCHING -> SearchingView(data.searchEndsAt)
            CombatViewState.IN_COMBAT -> InCombatView(data)
        }

        Spacer(modifier = Modifier.height(16.dp))

        TextButton(onClick = { showAdvanced = !showAdvanced }) {"""
layout_new = """        when (data.viewState) {
            CombatViewState.SEARCHING -> SearchingView(data.searchEndsAt)
            CombatViewState.IN_COMBAT -> InCombatView(data)
        }

        Spacer(modifier = Modifier.height(16.dp))
        SessionDropsPanel(data.sessionDrops)

        Spacer(modifier = Modifier.height(16.dp))

        TextButton(onClick = { showAdvanced = !showAdvanced }) {"""
guarded_replace(combat_view_path, layout_old, layout_new)

panel_anchor_old = """@Composable
private fun HpBarRow(label: String, current: Int, max: Int, color: androidx.compose.ui.graphics.Color) {"""
panel_anchor_new = """@Composable
private fun SessionDropsPanel(drops: List<SessionDropEntry>) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(16.dp)
    ) {
        Text(text = "Drops This Session", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(6.dp))
        if (drops.isEmpty()) {
            Text(text = "No items yet.", style = MaterialTheme.typography.labelSmall)
        } else {
            drops.forEach { drop ->
                Text(
                    text = drop.itemName + " x" + drop.quantity,
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(vertical = 2.dp)
                )
            }
        }
    }
}

@Composable
private fun HpBarRow(label: String, current: Int, max: Int, color: androidx.compose.ui.graphics.Color) {"""
guarded_replace(combat_view_path, panel_anchor_old, panel_anchor_new)

# ---------------------------------------------------------------------------
# 2. GameViewModel.kt - sessionDropsFor tracker: import, declaration, clear-on-
#    enter, populate-on-loot, expose in CombatViewData construction
# ---------------------------------------------------------------------------
game_vm_path = find_file("GameViewModel.kt")

import_old = "import com.yourname.idlerpg.ui.screens.CombatLogEntry"
import_new = """import com.yourname.idlerpg.ui.screens.CombatLogEntry
import com.yourname.idlerpg.ui.screens.SessionDropEntry"""
guarded_replace(game_vm_path, import_old, import_new)

decl_old = "    private val combatLogFor: MutableMap<String, MutableList<CombatLogEntry>> = mutableMapOf()"
decl_new = """    private val combatLogFor: MutableMap<String, MutableList<CombatLogEntry>> = mutableMapOf()
    private val sessionDropsFor: MutableMap<String, MutableMap<String, Int>> = mutableMapOf()"""
guarded_replace(game_vm_path, decl_old, decl_new)

clear_old = """            combatLogFor.getOrPut(characterId) { mutableListOf() }.apply {
                clear()
                add(CombatLogEntry("Entered " + result.value.zone.name + "."))
            }"""
clear_new = """            combatLogFor.getOrPut(characterId) { mutableListOf() }.apply {
                clear()
                add(CombatLogEntry("Entered " + result.value.zone.name + "."))
            }
            sessionDropsFor.getOrPut(characterId) { mutableMapOf() }.clear()"""
guarded_replace(game_vm_path, clear_old, clear_new)

populate_old = """                    loot.value.forEach { entry -> inventoryService.inventoryFor(characterId).addItem(entry.itemId, entry.minQty) }
                    refreshInventory()"""
populate_new = """                    loot.value.forEach { entry ->
                        inventoryService.inventoryFor(characterId).addItem(entry.itemId, entry.minQty)
                        sessionDropsFor.getOrPut(characterId) { mutableMapOf() }.merge(entry.itemId, entry.minQty, Int::plus)
                    }
                    refreshInventory()"""
guarded_replace(game_vm_path, populate_old, populate_new)

expose_old = """            lastHitChancePercent = lastHitChancePercent,
            lastDamageDealt = lastDamageDealt,
            combatLog = log
        )
    }"""
expose_new = """            lastHitChancePercent = lastHitChancePercent,
            lastDamageDealt = lastDamageDealt,
            combatLog = log,
            sessionDrops = sessionDropsFor.getOrPut(characterId) { mutableMapOf() }
                .map { (itemId, qty) -> SessionDropEntry(ItemCatalog.find(itemId)?.name ?: formatItemName(itemId), qty) }
                .sortedByDescending { it.quantity }
        )
    }"""
guarded_replace(game_vm_path, expose_old, expose_new)

print("ALL PATCHES APPLIED SUCCESSFULLY")
