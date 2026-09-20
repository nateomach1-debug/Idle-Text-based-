#!/usr/bin/env python3
"""
patch_M2_monster_picker.py

1) Monster-selection popup: tapping an unlocked zone now opens a dialog listing
   every monster in that zone (name, Lv., "Weak: <type>"); tapping one starts
   fighting THAT monster. The choice is remembered per character (device-local
   SharedPreferences) and used for live combat (every re-search after a kill) AND
   offline combat progress. Zones entered without a pick fall back to random.
2) Weakness display: on the popup and on each zone card of ZoneSelectScreen
   ("Goblin Scout (Wind) • Goblin Shaman (Earth) ...").

Files touched: CombatSystem.kt, GameViewModel.kt, MainActivity.kt, ZoneSelectScreen.kt
Requires patch_L (DamageType / Monster.weakness) to already be applied.
Independent of patch_M1 (works with or without the extra monsters).
Run from the repo root. Idempotent. All-or-nothing: if any anchor is
missing/ambiguous, nothing is written and the script exits 1.
"""
import os
import sys

SRC = "app/src/main/kotlin/com/yourname/idlerpg"
FILES = {
    "CombatSystem.kt": os.path.join(SRC, "CombatSystem.kt"),
    "GameViewModel.kt": os.path.join(SRC, "GameViewModel.kt"),
    "MainActivity.kt": os.path.join(SRC, "MainActivity.kt"),
    "ZoneSelectScreen.kt": None,  # located below (lives under ui/screens or flat)
}

EDITS = []  # (file_key, label, old, new)


def edit(fkey, label, old, new):
    EDITS.append((fkey, label, old, new))


# ---------------------------------------------------------------- CombatSystem.kt
edit("CombatSystem.kt", "DamageType.displayName()",
     "enum class DamageType { MELEE, RANGED, FIRE, EARTH, WATER, WIND }",
     "enum class DamageType { MELEE, RANGED, FIRE, EARTH, WATER, WIND }\n"
     "\n"
     "// Player-facing label for a damage type (zone screen + monster picker).\n"
     "fun DamageType.displayName(): String = when (this) {\n"
     "    DamageType.MELEE -> \"Melee\"\n"
     "    DamageType.RANGED -> \"Ranged\"\n"
     "    DamageType.FIRE -> \"Fire\"\n"
     "    DamageType.EARTH -> \"Earth\"\n"
     "    DamageType.WATER -> \"Water\"\n"
     "    DamageType.WIND -> \"Wind\"\n"
     "}")

edit("CombatSystem.kt", "CombatService target provider",
     "    private val states: MutableMap<String, CharacterCombatState> = mutableMapOf()",
     "    private val states: MutableMap<String, CharacterCombatState> = mutableMapOf()\n"
     "\n"
     "    // Which monster the player picked to hunt (monster id), supplied per character by\n"
     "    // GameViewModel from persisted settings. Null/unknown/not-in-this-zone -> random pick.\n"
     "    var targetMonsterIdProvider: (String) -> String? = { null }\n"
     "\n"
     "    private fun targetMonsterFor(characterId: String, zone: Zone): Monster? {\n"
     "        val targetId = targetMonsterIdProvider(characterId) ?: return null\n"
     "        return zone.monsters.find { it.id == targetId }\n"
     "    }")

edit("CombatSystem.kt", "live search uses target",
     "        val monster = session.zone.monsters.random()",
     "        val monster = targetMonsterFor(characterId, session.zone) ?: session.zone.monsters.random()")

edit("CombatSystem.kt", "offline averages use target",
     "        val avgMonsterHealth = zone.monsters.map { it.maxHealth }.average()\n"
     "        val avgMonsterDefense = zone.monsters.map { it.defenseRating }.average()",
     "        // If the player picked a specific monster, offline progress assumes they keep\n"
     "        // fighting only that monster; otherwise average across the zone as before.\n"
     "        val targetMonster = targetMonsterFor(characterId, zone)\n"
     "        val offlinePool: List<Monster> = if (targetMonster != null) listOf(targetMonster) else zone.monsters\n"
     "        val avgMonsterHealth = offlinePool.map { it.maxHealth }.average()\n"
     "        val avgMonsterDefense = offlinePool.map { it.defenseRating }.average()")

edit("CombatSystem.kt", "offline loot uses target",
     "            val monster = zone.monsters.random()\n"
     "            rollLoot(state, monster, dropRateMultiplier)",
     "            val monster = offlinePool.random()\n"
     "            rollLoot(state, monster, dropRateMultiplier)")

# ---------------------------------------------------------------- GameViewModel.kt
edit("GameViewModel.kt", "import ZoneMonsterSummary",
     "import com.yourname.idlerpg.ui.screens.ZoneSummary",
     "import com.yourname.idlerpg.ui.screens.ZoneSummary\n"
     "import com.yourname.idlerpg.ui.screens.ZoneMonsterSummary")

edit("GameViewModel.kt", "persisted target provider",
     "    private val settingsPrefs = application.getSharedPreferences(\"idlerpg_prefs\", android.content.Context.MODE_PRIVATE)",
     "    private val settingsPrefs = application.getSharedPreferences(\"idlerpg_prefs\", android.content.Context.MODE_PRIVATE)\n"
     "\n"
     "    // Monster the player picked in the zone popup, stored per character (device-local).\n"
     "    // CombatService reads it lazily whenever it picks the next monster, including when\n"
     "    // resolving offline combat progress after a restart.\n"
     "    private fun combatTargetKey(characterId: String): String = \"combat_target_monster_\" + characterId\n"
     "\n"
     "    init {\n"
     "        combatService.targetMonsterIdProvider = { characterId ->\n"
     "            settingsPrefs.getString(combatTargetKey(characterId), null)\n"
     "        }\n"
     "    }")

edit("GameViewModel.kt", "zoneSummaries carries monsters",
     "                monsterNames = zone.monsters.map { it.name }\n"
     "            )",
     "                monsterNames = zone.monsters.map { it.name },\n"
     "                monsters = zone.monsters.map { monster ->\n"
     "                    ZoneMonsterSummary(\n"
     "                        monsterId = monster.id,\n"
     "                        name = monster.name,\n"
     "                        level = monster.levelRequirement,\n"
     "                        weaknessLabel = monster.weakness?.displayName() ?: \"None\"\n"
     "                    )\n"
     "                }\n"
     "            )")

edit("GameViewModel.kt", "enterCombatZone signature",
     "    fun enterCombatZone(zoneId: String): ServiceResult<CombatSession> {",
     "    fun enterCombatZone(zoneId: String, monsterId: String? = null): ServiceResult<CombatSession> {")

edit("GameViewModel.kt", "enterCombatZone persists pick",
     "            offlineIdleService.optIntoOfflineCombat(characterId, zoneId)",
     "            // Remember which monster was picked (or clear it -> random) so live combat and\n"
     "            // offline progress both keep targeting it. Ignored if it isn't in this zone.\n"
     "            val chosenMonsterId = monsterId?.takeIf { pickedId ->\n"
     "                ZoneCatalog.zones.find { it.id == zoneId }?.monsters?.any { it.id == pickedId } == true\n"
     "            }\n"
     "            if (chosenMonsterId != null) {\n"
     "                settingsPrefs.edit().putString(combatTargetKey(characterId), chosenMonsterId).apply()\n"
     "            } else {\n"
     "                settingsPrefs.edit().remove(combatTargetKey(characterId)).apply()\n"
     "            }\n"
     "            offlineIdleService.optIntoOfflineCombat(characterId, zoneId)")

# ---------------------------------------------------------------- MainActivity.kt
edit("MainActivity.kt", "call site passes monsterId",
     "                                    onZoneSelected = { zoneId ->\n"
     "                                        val result = gameViewModel.enterCombatZone(zoneId)",
     "                                    onZoneSelected = { zoneId, monsterId ->\n"
     "                                        val result = gameViewModel.enterCombatZone(zoneId, monsterId)")

# ---------------------------------------------------------------- ZoneSelectScreen.kt
edit("ZoneSelectScreen.kt", "imports",
     "import androidx.compose.runtime.Composable",
     "import androidx.compose.foundation.rememberScrollState\n"
     "import androidx.compose.foundation.verticalScroll\n"
     "import androidx.compose.runtime.Composable\n"
     "import androidx.compose.runtime.getValue\n"
     "import androidx.compose.runtime.mutableStateOf\n"
     "import androidx.compose.runtime.saveable.rememberSaveable\n"
     "import androidx.compose.runtime.setValue")

edit("ZoneSelectScreen.kt", "ZoneSummary.monsters",
     "    val monsterNames: List<String>\n)",
     "    val monsterNames: List<String>,\n"
     "    val monsters: List<ZoneMonsterSummary> = emptyList()\n"
     ")\n"
     "\n"
     "// One selectable monster in a zone. weaknessLabel is display text (\"Fire\", \"Melee\", ...).\n"
     "data class ZoneMonsterSummary(\n"
     "    val monsterId: String,\n"
     "    val name: String,\n"
     "    val level: Int,\n"
     "    val weaknessLabel: String\n"
     ")")

edit("ZoneSelectScreen.kt", "onZoneSelected signature",
     "    onZoneSelected: (String) -> Unit,",
     "    onZoneSelected: (zoneId: String, monsterId: String) -> Unit,")

edit("ZoneSelectScreen.kt", "picker state",
     "    Column(modifier = modifier.fillMaxSize().padding(20.dp)) {",
     "    var pickerZoneId by rememberSaveable { mutableStateOf<String?>(null) }\n"
     "\n"
     "    Column(modifier = modifier.fillMaxSize().padding(20.dp)) {")

edit("ZoneSelectScreen.kt", "caption above list",
     "        LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {",
     "        Text(\n"
     "            text = \"Tap a zone to choose a monster. Brackets show each monster's weakness.\",\n"
     "            style = MaterialTheme.typography.labelSmall,\n"
     "            modifier = Modifier.alpha(0.7f)\n"
     "        )\n"
     "        Spacer(modifier = Modifier.height(10.dp))\n"
     "\n"
     "        LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {")

edit("ZoneSelectScreen.kt", "zone tap opens picker + dialog host",
     "                    onClick = { if (playerLevel >= zone.levelRequirement) onZoneSelected(zone.zoneId) }\n"
     "                )\n"
     "            }\n"
     "        }\n"
     "    }\n"
     "}\n",
     "                    onClick = { if (playerLevel >= zone.levelRequirement) pickerZoneId = zone.zoneId }\n"
     "                )\n"
     "            }\n"
     "        }\n"
     "    }\n"
     "\n"
     "    val pickerZone = zones.find { it.zoneId == pickerZoneId }\n"
     "    if (pickerZone != null) {\n"
     "        MonsterPickerDialog(\n"
     "            zone = pickerZone,\n"
     "            onPick = { monsterId ->\n"
     "                pickerZoneId = null\n"
     "                onZoneSelected(pickerZone.zoneId, monsterId)\n"
     "            },\n"
     "            onDismiss = { pickerZoneId = null }\n"
     "        )\n"
     "    }\n"
     "}\n")

edit("ZoneSelectScreen.kt", "picker dialog composable",
     "@Composable\nprivate fun ZoneCard(zone: ZoneSummary, isUnlocked: Boolean, onClick: () -> Unit) {",
     "@Composable\n"
     "private fun MonsterPickerDialog(\n"
     "    zone: ZoneSummary,\n"
     "    onPick: (String) -> Unit,\n"
     "    onDismiss: () -> Unit\n"
     ") {\n"
     "    AlertDialog(\n"
     "        onDismissRequest = onDismiss,\n"
     "        title = { Text(text = zone.name) },\n"
     "        text = {\n"
     "            Column(\n"
     "                modifier = Modifier.verticalScroll(rememberScrollState()),\n"
     "                verticalArrangement = Arrangement.spacedBy(8.dp)\n"
     "            ) {\n"
     "                Text(\n"
     "                    text = \"Choose which monster to fight:\",\n"
     "                    style = MaterialTheme.typography.bodyMedium\n"
     "                )\n"
     "                zone.monsters.forEach { monster ->\n"
     "                    Row(\n"
     "                        modifier = Modifier\n"
     "                            .fillMaxWidth()\n"
     "                            .clip(RoundedCornerShape(10.dp))\n"
     "                            .background(MaterialTheme.colorScheme.onSurface.copy(alpha = 0.08f))\n"
     "                            .clickable { onPick(monster.monsterId) }\n"
     "                            .padding(12.dp),\n"
     "                        horizontalArrangement = Arrangement.SpaceBetween,\n"
     "                        verticalAlignment = Alignment.CenterVertically\n"
     "                    ) {\n"
     "                        Column(modifier = Modifier.weight(1f)) {\n"
     "                            Text(text = monster.name, style = MaterialTheme.typography.titleSmall)\n"
     "                            Text(text = \"Lv. \" + monster.level, style = MaterialTheme.typography.labelSmall)\n"
     "                        }\n"
     "                        Text(\n"
     "                            text = \"Weak: \" + monster.weaknessLabel,\n"
     "                            style = MaterialTheme.typography.labelMedium\n"
     "                        )\n"
     "                    }\n"
     "                }\n"
     "            }\n"
     "        },\n"
     "        confirmButton = {},\n"
     "        dismissButton = {\n"
     "            TextButton(onClick = onDismiss) { Text(text = \"Cancel\") }\n"
     "        }\n"
     "    )\n"
     "}\n"
     "\n"
     "@Composable\nprivate fun ZoneCard(zone: ZoneSummary, isUnlocked: Boolean, onClick: () -> Unit) {")

edit("ZoneSelectScreen.kt", "zone card text column weight",
     "        Column(modifier = Modifier.alpha(contentAlpha)) {",
     "        Column(modifier = Modifier.weight(1f).padding(end = 8.dp).alpha(contentAlpha)) {")

edit("ZoneSelectScreen.kt", "zone card weakness summary",
     "                text = zone.monsterNames.joinToString(\", \"),",
     "                text = if (zone.monsters.isNotEmpty()) {\n"
     "                    zone.monsters.joinToString(\"  \\u2022  \") { it.name + \" (\" + it.weaknessLabel + \")\" }\n"
     "                } else {\n"
     "                    zone.monsterNames.joinToString(\", \")\n"
     "                },")


def find_zone_select():
    for root, _dirs, files in os.walk("app/src/main"):
        if "ZoneSelectScreen.kt" in files:
            return os.path.join(root, "ZoneSelectScreen.kt")
    return None


def main():
    FILES["ZoneSelectScreen.kt"] = find_zone_select()
    contents = {}
    for key, path in FILES.items():
        if not path or not os.path.exists(path):
            print("FAIL: %s not found (run from repo root)" % key)
            sys.exit(1)
        with open(path, encoding="utf-8", newline="") as f:
            contents[key] = f.read()

    original = dict(contents)
    failed, applied, skipped = False, 0, 0
    for fkey, label, old, new in EDITS:
        if new in original[fkey]:
            print("SKIP  %-16s %s (already applied)" % (fkey, label))
            skipped += 1
            continue
        n = contents[fkey].count(old)
        if n != 1:
            print("FAIL  %-16s %s: anchor matched %d times (expected 1)" % (fkey, label, n))
            failed = True
            continue
        contents[fkey] = contents[fkey].replace(old, new, 1)
        print("OK    %-16s %s" % (fkey, label))
        applied += 1
    if failed:
        print("Aborting - nothing written.")
        sys.exit(1)

    for key, path in FILES.items():
        if contents[key] != original[key]:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(contents[key])
    print("Done. %d edit(s) applied, %d already present." % (applied, skipped))


if __name__ == "__main__":
    main()
