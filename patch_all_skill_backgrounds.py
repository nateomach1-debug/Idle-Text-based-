#!/usr/bin/env python3
"""
Guarded patch: add the currently-trained combat skill to the Home tab's
combat queue card.
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

# 1. HomeScreenState gets a new trainingSkillLabel field
guarded_replace(
    home_path,
    old="    val activeCombat: CombatViewData?, // null if not currently in a combat zone\n",
    new=(
        "    val activeCombat: CombatViewData?, // null if not currently in a combat zone\n"
        "    val trainingSkillLabel: String?,   // e.g. \"Attack\" - only rendered alongside activeCombat\n"
    ),
    marker="val trainingSkillLabel: String?,   // e.g. \"Attack\" - only rendered alongside activeCombat",
)

# 2. HomeScreen() passes it down to QueueCard
guarded_replace(
    home_path,
    old="        QueueCard(queue = state.activeQueue, combat = state.activeCombat)\n",
    new="        QueueCard(queue = state.activeQueue, combat = state.activeCombat, trainingSkillLabel = state.trainingSkillLabel)\n",
    marker="QueueCard(queue = state.activeQueue, combat = state.activeCombat, trainingSkillLabel = state.trainingSkillLabel)",
)

# 3. QueueCard renders the skill label between zone name and status
guarded_replace(
    home_path,
    old=(
        "private fun QueueCard(queue: ActiveQueueInfo?, combat: CombatViewData?) {\n"
    ),
    new=(
        "private fun QueueCard(queue: ActiveQueueInfo?, combat: CombatViewData?, trainingSkillLabel: String? = null) {\n"
    ),
    marker="private fun QueueCard(queue: ActiveQueueInfo?, combat: CombatViewData?, trainingSkillLabel: String? = null) {",
)

guarded_replace(
    home_path,
    old=(
        "        if (combat != null) {\n"
        "            Text(text = combat.zoneName, style = MaterialTheme.typography.titleMedium)\n"
        "            Spacer(modifier = Modifier.height(8.dp))\n"
    ),
    new=(
        "        if (combat != null) {\n"
        "            Text(text = combat.zoneName, style = MaterialTheme.typography.titleMedium)\n"
        "            if (trainingSkillLabel != null) {\n"
        "                Text(text = \"Training \" + trainingSkillLabel, style = MaterialTheme.typography.bodySmall)\n"
        "            }\n"
        "            Spacer(modifier = Modifier.height(8.dp))\n"
    ),
    marker="Text(text = \"Training \" + trainingSkillLabel, style = MaterialTheme.typography.bodySmall)",
)

# 4. MainActivity.kt: pass the already-collected trainingSkill through
main_activity_path = os.path.join(ROOT, "MainActivity.kt")
guarded_replace(
    main_activity_path,
    old=(
        "    val homeCombatViewData by gameViewModel.combatViewData.collectAsState()\n"
        "    val homeState = HomeScreenState(\n"
        "        activeQueue = activeQueue,\n"
        "        activeCombat = homeCombatViewData,\n"
        "        softCurrency = currency.first,\n"
    ),
    new=(
        "    val homeCombatViewData by gameViewModel.combatViewData.collectAsState()\n"
        "    val homeState = HomeScreenState(\n"
        "        activeQueue = activeQueue,\n"
        "        activeCombat = homeCombatViewData,\n"
        "        trainingSkillLabel = trainingSkill.name.lowercase().replaceFirstChar { it.uppercase() },\n"
        "        softCurrency = currency.first,\n"
    ),
    marker="trainingSkillLabel = trainingSkill.name.lowercase().replaceFirstChar { it.uppercase() },",
)

print("\nAll training-skill-label patches applied successfully.")
