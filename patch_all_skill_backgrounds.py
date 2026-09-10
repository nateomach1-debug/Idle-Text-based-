#!/usr/bin/env python3
"""
Guarded patch: add a per-skill info button (Skills tab, both List and
Grid views) that opens a dialog explaining what that skill does.
"""
import os

path = "app/src/main/kotlin/com/yourname/idlerpg/SkillsScreen.kt"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()


def guarded_replace(content, old, new, marker):
    if marker in content:
        print(f"SKIP (already applied): {marker[:50]}")
        return content
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly 1 match, found {count}.\n--- old_str ---\n{old}\n--- end ---")
    print(f"PATCHED: {marker[:50]}")
    return content.replace(old, new)


# 1. Import for the info icon
content = guarded_replace(
    content,
    old="import androidx.compose.material.icons.filled.GridView\n",
    new="import androidx.compose.material.icons.filled.GridView\nimport androidx.compose.material.icons.filled.Info\n",
    marker="import androidx.compose.material.icons.filled.Info",
)

# 2. Descriptions map + shared dialog composable, inserted right after
#    the PREFS constants at the top of the file.
old_prefs = (
    "private const val PREFS_NAME = \"idlerpg_prefs\"\n"
    "private const val KEY_SKILLS_VIEW_MODE = \"skills_view_mode\"\n"
)
new_prefs = (
    "private const val PREFS_NAME = \"idlerpg_prefs\"\n"
    "private const val KEY_SKILLS_VIEW_MODE = \"skills_view_mode\"\n"
    "\n"
    "private val SKILL_DESCRIPTIONS: Map<String, String> = mapOf(\n"
    "    \"MINING\" to \"Mine ore from rocks. Higher levels unlock better ore and mine faster.\",\n"
    "    \"WOODCUTTING\" to \"Chop trees for logs. Higher levels unlock better trees and chop faster.\",\n"
    "    \"FISHING\" to \"Catch fish at fishing spots. Higher levels unlock better fish and catch faster.\",\n"
    "    \"FARMING\" to \"Harvest crops from farm plots. Higher levels unlock better crops and harvest faster.\",\n"
    "    \"THIEVING\" to \"Pickpocket and steal for loot and coin. Higher levels unlock riskier, more rewarding targets.\",\n"
    "    \"SMITHING\" to \"Smelt ore into bars and forge them into weapons and armor.\",\n"
    "    \"COOKING\" to \"Cook raw food into meals you can eat to heal during combat.\",\n"
    "    \"CRAFTING\" to \"Craft leather, cloth, and jewelry into wearable gear.\",\n"
    "    \"FLETCHING\" to \"Craft bows and arrows for use with the Archery combat style.\",\n"
    "    \"ALCHEMY\" to \"Brew potions that grant temporary combat and skilling boosts.\",\n"
    "    \"MAGIC\" to \"Train your magic combat style, and unlock utility spells like teleportation.\",\n"
    "    \"ATTACK\" to \"Trains your melee hit chance. Higher levels land more hits with melee weapons.\",\n"
    "    \"STRENGTH\" to \"Trains your melee hit damage. Higher levels deal more damage per hit with melee weapons.\",\n"
    "    \"DEFENSE\" to \"Reduces the damage you take from monsters. Higher levels reduce incoming damage further.\",\n"
    "    \"PRAYER\" to \"Activate prayers for combat bonuses like extra damage reduction.\",\n"
    "    \"ARCHERY\" to \"Trains your ranged hit chance and damage when fighting with a bow.\"\n"
    ")\n"
    "\n"
    "@Composable\n"
    "private fun SkillInfoButton(skillId: String) {\n"
    "    var showDialog by remember { mutableStateOf(false) }\n"
    "    IconButton(onClick = { showDialog = true }, modifier = Modifier.size(28.dp)) {\n"
    "        Icon(\n"
    "            imageVector = Icons.Filled.Info,\n"
    "            contentDescription = \"What does this skill do?\",\n"
    "            tint = overrideColor(MaterialTheme.colorScheme.onSurfaceVariant)\n"
    "        )\n"
    "    }\n"
    "    if (showDialog) {\n"
    "        AlertDialog(\n"
    "            onDismissRequest = { showDialog = false },\n"
    "            confirmButton = {\n"
    "                TextButton(onClick = { showDialog = false }) { Text(\"Got it\") }\n"
    "            },\n"
    "            title = { Text(skillId.lowercase().replaceFirstChar { it.uppercase() }) },\n"
    "            text = { Text(SKILL_DESCRIPTIONS[skillId] ?: \"No description available.\") }\n"
    "        )\n"
    "    }\n"
    "}\n"
)
content = guarded_replace(content, old_prefs, new_prefs, marker="private val SKILL_DESCRIPTIONS: Map<String, String>")

# 3. SkillListRow: add the info button next to the skill name
old_list_row = (
    "            Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {\n"
    "                Text(text = skill.displayName, style = MaterialTheme.typography.titleMedium)\n"
    "                Text(text = \"Lv. \" + skill.level, style = MaterialTheme.typography.titleMedium)\n"
    "            }\n"
)
new_list_row = (
    "            Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {\n"
    "                Row(verticalAlignment = Alignment.CenterVertically) {\n"
    "                    Text(text = skill.displayName, style = MaterialTheme.typography.titleMedium)\n"
    "                    SkillInfoButton(skillId = skill.skillId)\n"
    "                }\n"
    "                Text(text = \"Lv. \" + skill.level, style = MaterialTheme.typography.titleMedium)\n"
    "            }\n"
)
content = guarded_replace(content, old_list_row, new_list_row, marker="SkillInfoButton(skillId = skill.skillId)\n                }\n                Text(text = \"Lv. \" + skill.level")

# 4. SkillGridTile: add the info button next to the skill name
old_grid_tile = (
    "        Text(text = skill.displayName, style = MaterialTheme.typography.labelSmall)\n"
    "        Spacer(modifier = Modifier.height(4.dp))\n"
    "        Text(text = \"Lv. \" + skill.level, style = MaterialTheme.typography.titleMedium)\n"
)
new_grid_tile = (
    "        Row(verticalAlignment = Alignment.CenterVertically) {\n"
    "            Text(text = skill.displayName, style = MaterialTheme.typography.labelSmall)\n"
    "            SkillInfoButton(skillId = skill.skillId)\n"
    "        }\n"
    "        Spacer(modifier = Modifier.height(4.dp))\n"
    "        Text(text = \"Lv. \" + skill.level, style = MaterialTheme.typography.titleMedium)\n"
)
content = guarded_replace(content, old_grid_tile, new_grid_tile, marker="SkillInfoButton(skillId = skill.skillId)\n        }\n        Spacer(modifier = Modifier.height(4.dp))")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("\nAll skill info button patches applied successfully.")
