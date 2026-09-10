#!/usr/bin/env python3
"""
Guarded patch: show combat as a Home tab queue entry - zone + monster
name when actively fighting, "Searching in <zone>" between encounters.
"""
import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def guarded_replace(path, old, new, marker):
    content = read(path)
    if marker in content:
        print(f"SKIP (already applied): {path} :: {marker[:50]}")
        return
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly 1 match in {path}, found {count}.\n--- old_str ---\n{old}\n--- end ---")
    write(path, content.replace(old, new))
    print(f"PATCHED: {path} :: {marker[:50]}")


home_path = os.path.join(ROOT, "HomeScreen.kt")

# 1. HomeScreenState gets a new activeCombat field
guarded_replace(
    home_path,
    old=(
        "data class HomeScreenState(\n"
        "    val activeQueue: ActiveQueueInfo?, // null if no active queue\n"
    ),
    new=(
        "data class HomeScreenState(\n"
        "    val activeQueue: ActiveQueueInfo?, // null if no active queue\n"
        "    val activeCombat: CombatViewData?, // null if not currently in a combat zone\n"
    ),
    marker="val activeCombat: CombatViewData?, // null if not currently in a combat zone",
)

# 2. HomeScreen() passes the new field down to QueueCard
guarded_replace(
    home_path,
    old="        QueueCard(queue = state.activeQueue)\n",
    new="        QueueCard(queue = state.activeQueue, combat = state.activeCombat)\n",
    marker="QueueCard(queue = state.activeQueue, combat = state.activeCombat)",
)

# 3. QueueCard renders combat status when present, ahead of the
#    skilling/crafting queue rendering (the two are mutually exclusive -
#    a character is either training a skill/crafting, or fighting).
guarded_replace(
    home_path,
    old=(
        "private fun QueueCard(queue: ActiveQueueInfo?) {\n"
        "    Column(\n"
        "        modifier = Modifier\n"
        "            .fillMaxWidth()\n"
        "            .clip(RoundedCornerShape(14.dp))\n"
        "            .background(MaterialTheme.colorScheme.surface)\n"
        "            .padding(16.dp)\n"
        "    ) {\n"
        "        if (queue == null) {\n"
        "            Text(text = \"No active queue\", style = MaterialTheme.typography.bodyMedium)\n"
        "            return@Column\n"
        "        }\n"
    ),
    new=(
        "private fun QueueCard(queue: ActiveQueueInfo?, combat: CombatViewData?) {\n"
        "    Column(\n"
        "        modifier = Modifier\n"
        "            .fillMaxWidth()\n"
        "            .clip(RoundedCornerShape(14.dp))\n"
        "            .background(MaterialTheme.colorScheme.surface)\n"
        "            .padding(16.dp)\n"
        "    ) {\n"
        "        if (combat != null) {\n"
        "            Text(text = combat.zoneName, style = MaterialTheme.typography.titleMedium)\n"
        "            Spacer(modifier = Modifier.height(8.dp))\n"
        "            val statusText = when (combat.viewState) {\n"
        "                CombatViewState.IN_COMBAT -> \"Fighting \" + (combat.monsterName ?: \"a monster\")\n"
        "                CombatViewState.SEARCHING -> \"Searching in \" + combat.zoneName\n"
        "            }\n"
        "            Text(text = statusText, style = MaterialTheme.typography.bodyMedium)\n"
        "            return@Column\n"
        "        }\n"
        "\n"
        "        if (queue == null) {\n"
        "            Text(text = \"No active queue\", style = MaterialTheme.typography.bodyMedium)\n"
        "            return@Column\n"
        "        }\n"
    ),
    marker="if (combat != null) {\n            Text(text = combat.zoneName, style = MaterialTheme.typography.titleMedium)",
)

# 4. MainActivity.kt: collect combatViewData and thread it into homeState
main_activity_path = os.path.join(ROOT, "MainActivity.kt")
guarded_replace(
    main_activity_path,
    old=(
        "    val activeQueue by gameViewModel.activeQueueInfo.collectAsState()\n"
        "    val currency by gameViewModel.currency.collectAsState()\n"
        "    val combatHp by gameViewModel.combatHp.collectAsState()\n"
        "    val homeState = HomeScreenState(\n"
        "        activeQueue = activeQueue,\n"
        "        softCurrency = currency.first,\n"
    ),
    new=(
        "    val activeQueue by gameViewModel.activeQueueInfo.collectAsState()\n"
        "    val currency by gameViewModel.currency.collectAsState()\n"
        "    val combatHp by gameViewModel.combatHp.collectAsState()\n"
        "    val homeCombatViewData by gameViewModel.combatViewData.collectAsState()\n"
        "    val homeState = HomeScreenState(\n"
        "        activeQueue = activeQueue,\n"
        "        activeCombat = homeCombatViewData,\n"
        "        softCurrency = currency.first,\n"
    ),
    marker="val homeCombatViewData by gameViewModel.combatViewData.collectAsState()",
)

print("\nAll Home-tab combat queue patches applied successfully.")
