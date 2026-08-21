"""
Item 8: training location selector from the Skills tab's combat skill rows.

Tapping Attack, Strength, Defense, Magic, or Archery (Range) on the Skills
tab now calls gameViewModel.setTrainingSkill(...) and jumps straight to
Combat's zone-select screen for that skill, instead of opening the
generic (and non-functional-for-combat-skills) SkillDetailScreen.

Non-combat skills (mining, cooking, etc.) are unaffected - they still
open SkillsScreenState.Detail as before.

Prayer is intentionally left as a normal skill (not routed to combat
zone-select) since it wasn't one of the 5 skills requested.

Only MainActivity.kt needs editing - SkillsScreen.kt's onSkillSelected
callback signature is unchanged, only what MainActivity does with the
selected skillId changes.

Guarded with asserts.
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(BASE, "MainActivity.kt")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = (
    "                                is SkillsScreenState.List -> SkillsScreen(\n"
    "                                    allSkills = allSkills,\n"
    "                                    onSkillSelected = { skillsScreenState = SkillsScreenState.Detail(it) },\n"
    "                                    listState = skillsListScrollState,\n"
    "                                    gridState = skillsGridScrollState\n"
    "                                )"
)
new = (
    "                                is SkillsScreenState.List -> SkillsScreen(\n"
    "                                    allSkills = allSkills,\n"
    "                                    onSkillSelected = { selectedSkillId ->\n"
    "                                        if (selectedSkillId in COMBAT_TRAINING_SKILL_IDS) {\n"
    "                                            gameViewModel.setTrainingSkill(SkillType.valueOf(selectedSkillId))\n"
    "                                            currentDestination = AppDestination.COMBAT\n"
    "                                            combatScreenState = CombatScreenState.ZoneSelect\n"
    "                                        } else {\n"
    "                                            skillsScreenState = SkillsScreenState.Detail(selectedSkillId)\n"
    "                                        }\n"
    "                                    },\n"
    "                                    listState = skillsListScrollState,\n"
    "                                    gridState = skillsGridScrollState\n"
    "                                )"
)

assert old in content, "onSkillSelected anchor not found"
assert content.count(old) == 1, "onSkillSelected anchor not unique"
content = content.replace(old, new)

# Add the COMBAT_TRAINING_SKILL_IDS constant right before class MainActivity
old_class_decl = "class MainActivity : ComponentActivity() {"
new_class_decl = (
    "// Skills tab rows that route directly into training-location selection\n"
    "// (Combat's zone-select) instead of the generic skill-detail screen.\n"
    "// Prayer is deliberately excluded.\n"
    "private val COMBAT_TRAINING_SKILL_IDS = setOf(\"ATTACK\", \"STRENGTH\", \"DEFENSE\", \"MAGIC\", \"ARCHERY\")\n"
    "\n"
    "class MainActivity : ComponentActivity() {"
)
assert old_class_decl in content, "class declaration anchor not found"
assert content.count(old_class_decl) == 1, "class declaration anchor not unique"
content = content.replace(old_class_decl, new_class_decl)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched MainActivity.kt: combat skill taps on the Skills tab now route to training-location select.")
