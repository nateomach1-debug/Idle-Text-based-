#!/usr/bin/env python3
"""
Guarded patch: close the combat exploit where switching trainingSkill
mid-combat never actually ends the active session, letting an under-
leveled skill keep earning XP in a zone it never legitimately unlocked.
"""
import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(ROOT, "GameViewModel.kt")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = (
    "    fun setTrainingSkill(skillType: SkillType) {\n"
    "        _trainingSkill.value = skillType\n"
    "        val characterId = _currentCharacterId.value\n"
    "        _trainingSkillLevel.value = characterId?.let { skillLevel(it, skillType) } ?: 1\n"
    "    }\n"
)
new = (
    "    fun setTrainingSkill(skillType: SkillType) {\n"
    "        // Switching the trained skill mid-combat previously left the active\n"
    "        // session running in whatever zone was already entered - the zone's\n"
    "        // level gate is only checked in enterCombatZone(), not on every skill\n"
    "        // switch, so a lower-level skill could keep fighting (and earning XP)\n"
    "        // in a zone it never actually unlocked. End the session here so the\n"
    "        // player must legitimately re-enter a zone, correctly re-validated\n"
    "        // against the new skill's level.\n"
    "        if (_combatViewData.value != null) {\n"
    "            leaveCombatZone()\n"
    "        }\n"
    "        _trainingSkill.value = skillType\n"
    "        val characterId = _currentCharacterId.value\n"
    "        _trainingSkillLevel.value = characterId?.let { skillLevel(it, skillType) } ?: 1\n"
    "    }\n"
)

marker = "Switching the trained skill mid-combat previously left"
if marker in content:
    print("SKIP (already applied)")
else:
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly 1 match, found {count}.\n--- old_str ---\n{old}\n--- end ---")
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("PATCHED: setTrainingSkill now ends active combat session on skill switch")

print("Done.")
