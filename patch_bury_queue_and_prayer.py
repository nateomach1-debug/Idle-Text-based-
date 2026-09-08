#!/usr/bin/env python3
"""
Guarded patch: show cape bonus in the skill detail screen, only while
that skill's cape is equipped.

Touches only MainActivity.kt: a new capeBonusDescriptionFor() helper,
hasCapeEquipped param threaded into buildSkillDetailState()/
buildSmithingState(), a new equippedItems collection in the InGame scope,
and the 3 call sites updated to pass the equipped-check.
"""
import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(ROOT, "MainActivity.kt")


def read():
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write(content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def guarded_replace(old, new, already_applied_marker):
    content = read()
    if already_applied_marker in content:
        print(f"SKIP (already applied): {already_applied_marker[:50]}")
        return
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly 1 match, found {count}.\n--- old_str ---\n{old}\n--- end ---")
    write(content.replace(old, new))
    print(f"PATCHED: {already_applied_marker[:50]}")


# 1. New helper: capeBonusDescriptionFor(skillType) - right after effectSummaryText()
guarded_replace(
    old=(
        '    is Effect.MaterialSaveChance -> "+" + effect.percent + "% material save chance"\n'
        '    is Effect.CraftSuccessBoost -> "+" + effect.percent + "% success chance"\n'
        '}\n'
    ),
    new=(
        '    is Effect.MaterialSaveChance -> "+" + effect.percent + "% material save chance"\n'
        '    is Effect.CraftSuccessBoost -> "+" + effect.percent + "% success chance"\n'
        '}\n'
        '\n'
        '// Cape\'s OWN individual contribution (mirrors capeBonusEffects() in\n'
        '// GameViewModel.kt exactly - the level-50 perk already grants the base\n'
        '// bonus + 5% XP, the cape grants this same amount again on top).\n'
        '// Combat skills aren\'t Effect-driven (hardcoded in tickCombat), hence\n'
        'private val COMBAT_CAPE_BONUS_TEXT: Map<SkillType, String> = mapOf(\n'
        '    SkillType.ATTACK to "+5% hit chance (melee)",\n'
        '    SkillType.STRENGTH to "+5% min/max hit damage (melee)",\n'
        '    SkillType.DEFENSE to "+5% incoming damage reduction",\n'
        '    SkillType.ARCHERY to "+5% hit chance (ranged)",\n'
        '    SkillType.MAGIC to "+5% hit chance (magic)",\n'
        '    SkillType.PRAYER to "+5% reduced monster damage while a prayer is active"\n'
        ')\n'
        '\n'
        'private fun capeBonusDescriptionFor(skillType: SkillType): String {\n'
        '    val specific = COMBAT_CAPE_BONUS_TEXT[skillType] ?: when (skillType) {\n'
        '        SkillType.MINING, SkillType.WOODCUTTING, SkillType.FISHING, SkillType.FARMING, SkillType.THIEVING -> "+10% drop rate"\n'
        '        SkillType.SMITHING, SkillType.CRAFTING, SkillType.FLETCHING, SkillType.ALCHEMY -> "+10% material save chance"\n'
        '        SkillType.COOKING -> "+10% success chance"\n'
        '        else -> ""\n'
        '    }\n'
        '    return specific + ", +5% XP"\n'
        '}\n'
    ),
    already_applied_marker="private fun capeBonusDescriptionFor(skillType: SkillType): String {",
)

# 2. buildSkillDetailState() - add hasCapeEquipped param + append cape entry to `earned`
guarded_replace(
    old=(
        'private fun buildSkillDetailState(\n'
        '    skillId: String,\n'
        '    summary: SkillSummary,\n'
        '    inventoryQuantities: Map<String, Int>\n'
        '): SkillDetailState {\n'
        '    val skillType = SkillType.valueOf(skillId)\n'
        '\n'
        '    val earned = UnlockTable.unlocksEarnedAt(skillType, summary.level).map { unlock ->\n'
        '        SkillUnlockSummary(\n'
        '            description = unlock.grantedEffects.joinToString(", ") { effectSummaryText(it) },\n'
        '            levelRequired = unlock.levelRequired\n'
        '        )\n'
        '    }\n'
    ),
    new=(
        'private fun buildSkillDetailState(\n'
        '    skillId: String,\n'
        '    summary: SkillSummary,\n'
        '    inventoryQuantities: Map<String, Int>,\n'
        '    hasCapeEquipped: Boolean = false\n'
        '): SkillDetailState {\n'
        '    val skillType = SkillType.valueOf(skillId)\n'
        '\n'
        '    val earned = UnlockTable.unlocksEarnedAt(skillType, summary.level).map { unlock ->\n'
        '        SkillUnlockSummary(\n'
        '            description = unlock.grantedEffects.joinToString(", ") { effectSummaryText(it) },\n'
        '            levelRequired = unlock.levelRequired\n'
        '        )\n'
        '    } + if (hasCapeEquipped) {\n'
        '        listOf(SkillUnlockSummary(description = "Cape equipped: " + capeBonusDescriptionFor(skillType), levelRequired = 99))\n'
        '    } else {\n'
        '        emptyList()\n'
        '    }\n'
    ),
    already_applied_marker="hasCapeEquipped: Boolean = false\n): SkillDetailState {",
)

# 3. buildSmithingState() - same addition
guarded_replace(
    old=(
        'private fun buildSmithingState(summary: SkillSummary, inventoryQuantities: Map<String, Int>): SmithingState {\n'
        '    val skillType = SkillType.SMITHING\n'
        '    val earned = UnlockTable.unlocksEarnedAt(skillType, summary.level).map { unlock ->\n'
        '        SkillUnlockSummary(\n'
        '            description = unlock.grantedEffects.joinToString(", ") { effectSummaryText(it) },\n'
        '            levelRequired = unlock.levelRequired\n'
        '        )\n'
        '    }\n'
    ),
    new=(
        'private fun buildSmithingState(summary: SkillSummary, inventoryQuantities: Map<String, Int>, hasCapeEquipped: Boolean = false): SmithingState {\n'
        '    val skillType = SkillType.SMITHING\n'
        '    val earned = UnlockTable.unlocksEarnedAt(skillType, summary.level).map { unlock ->\n'
        '        SkillUnlockSummary(\n'
        '            description = unlock.grantedEffects.joinToString(", ") { effectSummaryText(it) },\n'
        '            levelRequired = unlock.levelRequired\n'
        '        )\n'
        '    } + if (hasCapeEquipped) {\n'
        '        listOf(SkillUnlockSummary(description = "Cape equipped: " + capeBonusDescriptionFor(skillType), levelRequired = 99))\n'
        '    } else {\n'
        '        emptyList()\n'
        '    }\n'
    ),
    already_applied_marker="hasCapeEquipped: Boolean = false): SmithingState {",
)

# 4. New equippedItems collection in the InGame scope
guarded_replace(
    old=(
        '                    Row(modifier = Modifier.fillMaxSize().weight(1f)) {\n'
        '                        val isModerator by gameViewModel.isModerator.collectAsState()\n'
    ),
    new=(
        '                    Row(modifier = Modifier.fillMaxSize().weight(1f)) {\n'
        '                        val isModerator by gameViewModel.isModerator.collectAsState()\n'
        '                        val equippedItemsForSkills by gameViewModel.equippedItems.collectAsState()\n'
    ),
    already_applied_marker="val equippedItemsForSkills by gameViewModel.equippedItems.collectAsState()",
)

# 5. Call sites: pass hasCapeEquipped
guarded_replace(
    old="                                                buildSmithingState(it, inventoryQuantities),\n",
    new=(
        '                                                buildSmithingState(\n'
        '                                                    it,\n'
        '                                                    inventoryQuantities,\n'
        '                                                    hasCapeEquipped = equippedItemsForSkills[EquipSlot.CAPE] == "smithing_cape"\n'
        '                                                ),\n'
    ),
    already_applied_marker='hasCapeEquipped = equippedItemsForSkills[EquipSlot.CAPE] == "smithing_cape"',
)

guarded_replace(
    old=(
        '                                            in RECIPE_BASED_SKILL_LABELS -> SkillDetailScreen(\n'
        '                                                buildSkillDetailState(screen.skillId, it, inventoryQuantities),\n'
    ),
    new=(
        '                                            in RECIPE_BASED_SKILL_LABELS -> SkillDetailScreen(\n'
        '                                                buildSkillDetailState(\n'
        '                                                    screen.skillId,\n'
        '                                                    it,\n'
        '                                                    inventoryQuantities,\n'
        '                                                    hasCapeEquipped = equippedItemsForSkills[EquipSlot.CAPE] == screen.skillId.lowercase() + "_cape"\n'
        '                                                ),\n'
    ),
    already_applied_marker="in RECIPE_BASED_SKILL_LABELS -> SkillDetailScreen(\n                                                buildSkillDetailState(\n                                                    screen.skillId,",
)

guarded_replace(
    old=(
        '                                            else -> SkillDetailScreen(\n'
        '                                                buildSkillDetailState(screen.skillId, it, inventoryQuantities),\n'
    ),
    new=(
        '                                            else -> SkillDetailScreen(\n'
        '                                                buildSkillDetailState(\n'
        '                                                    screen.skillId,\n'
        '                                                    it,\n'
        '                                                    inventoryQuantities,\n'
        '                                                    hasCapeEquipped = equippedItemsForSkills[EquipSlot.CAPE] == screen.skillId.lowercase() + "_cape"\n'
        '                                                ),\n'
    ),
    already_applied_marker="else -> SkillDetailScreen(\n                                                buildSkillDetailState(\n                                                    screen.skillId,",
)

print("\nAll cape-display patches applied successfully.")
