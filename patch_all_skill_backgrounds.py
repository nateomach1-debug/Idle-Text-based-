#!/usr/bin/env python3
"""
Guarded patch: require the correct weapon type equipped before allowing
Archery (bow -> CombatStyle.RANGED) or Magic (staff -> CombatStyle.MAGIC)
to be selected as the trained combat skill.
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


# =======================================================================
# 1. GameViewModel.kt - setTrainingSkill() now validates equipped weapon
#    for Archery/Magic and returns a ServiceResult instead of Unit.
# =======================================================================
gvm_path = os.path.join(ROOT, "GameViewModel.kt")

guarded_replace(
    gvm_path,
    old=(
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
    ),
    new=(
        "    fun setTrainingSkill(skillType: SkillType): ServiceResult<Unit> {\n"
        "        val characterId = _currentCharacterId.value\n"
        "\n"
        "        // Archery/Magic require the matching weapon type equipped - trainingSkill\n"
        "        // (which skill earns XP) was previously completely unlinked from the\n"
        "        // equipped weapon's actual combatStyle (which drives the combat math in\n"
        "        // tickCombat), letting you e.g. train Archery with no bow equipped at all.\n"
        "        val requiredStyle = when (skillType) {\n"
        "            SkillType.ARCHERY -> CombatStyle.RANGED\n"
        "            SkillType.MAGIC -> CombatStyle.MAGIC\n"
        "            else -> null\n"
        "        }\n"
        "        if (requiredStyle != null) {\n"
        "            val equippedWeaponId = characterId?.let { inventoryService.inventoryFor(it).equippedItemIn(EquipSlot.WEAPON) }\n"
        "            val equippedStyle = equippedWeaponId?.let { ItemCatalog.find(it)?.combatStyle }\n"
        "            if (equippedStyle != requiredStyle) {\n"
        "                val weaponNoun = if (skillType == SkillType.ARCHERY) \"a bow\" else \"a magic weapon\"\n"
        "                val skillLabel = skillType.name.lowercase().replaceFirstChar { it.uppercase() }\n"
        "                return ServiceResult.Failure(\"Equip \" + weaponNoun + \" to train \" + skillLabel + \".\")\n"
        "            }\n"
        "        }\n"
        "\n"
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
        "        _trainingSkillLevel.value = characterId?.let { skillLevel(it, skillType) } ?: 1\n"
        "        return ServiceResult.Success(Unit)\n"
        "    }\n"
    ),
    marker="Archery/Magic require the matching weapon type equipped",
)

# =======================================================================
# 2. MainActivity.kt - handle the ServiceResult at the call site,
#    surfacing failures via Toast.
# =======================================================================
ma_path = os.path.join(ROOT, "MainActivity.kt")

guarded_replace(
    ma_path,
    old="import androidx.compose.ui.platform.LocalContext\n" if False else "",
    new="",
    marker="__noop__",  # placeholder, real import handled below with a safe check
)

content = read(ma_path)
if "import android.widget.Toast\n" not in content:
    # Insert right after the package line, safe regardless of existing import ordering.
    guarded_replace(
        ma_path,
        old="package com.yourname.idlerpg\n",
        new="package com.yourname.idlerpg\n\nimport android.widget.Toast\n",
        marker="import android.widget.Toast",
    )
else:
    print("SKIP (already imported): android.widget.Toast")

guarded_replace(
    ma_path,
    old="    var currentDestination by rememberSaveable { mutableStateOf(AppDestination.HOME) }\n",
    new=(
        "    val context = androidx.compose.ui.platform.LocalContext.current\n"
        "    var currentDestination by rememberSaveable { mutableStateOf(AppDestination.HOME) }\n"
    ),
    marker="val context = androidx.compose.ui.platform.LocalContext.current",
)

guarded_replace(
    ma_path,
    old=(
        "                                    onSkillSelected = { selectedSkillId ->\n"
        "                                        if (selectedSkillId in COMBAT_TRAINING_SKILL_IDS) {\n"
        "                                            gameViewModel.setTrainingSkill(SkillType.valueOf(selectedSkillId))\n"
        "                                            currentDestination = AppDestination.COMBAT\n"
        "                                            combatScreenState = CombatScreenState.ZoneSelect\n"
        "                                        } else {\n"
        "                                            skillsScreenState = SkillsScreenState.Detail(selectedSkillId)\n"
        "                                        }\n"
        "                                    },\n"
    ),
    new=(
        "                                    onSkillSelected = { selectedSkillId ->\n"
        "                                        if (selectedSkillId in COMBAT_TRAINING_SKILL_IDS) {\n"
        "                                            when (val result = gameViewModel.setTrainingSkill(SkillType.valueOf(selectedSkillId))) {\n"
        "                                                is ServiceResult.Failure -> Toast.makeText(context, result.reason, Toast.LENGTH_SHORT).show()\n"
        "                                                is ServiceResult.Success -> {\n"
        "                                                    currentDestination = AppDestination.COMBAT\n"
        "                                                    combatScreenState = CombatScreenState.ZoneSelect\n"
        "                                                }\n"
        "                                            }\n"
        "                                        } else {\n"
        "                                            skillsScreenState = SkillsScreenState.Detail(selectedSkillId)\n"
        "                                        }\n"
        "                                    },\n"
    ),
    marker="when (val result = gameViewModel.setTrainingSkill(SkillType.valueOf(selectedSkillId))) {",
)

print("\nAll weapon-gating patches applied successfully.")
