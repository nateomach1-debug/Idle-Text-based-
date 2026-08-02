#!/usr/bin/env python3
"""
Step 7 patch: wire Cooking, Fletching, and Alchemy into the skill-detail UI
via RecipeCatalog, same pattern as Crafting. Introduces a single
RECIPE_BASED_SKILL_LABELS map used both for the action-list filter in
buildSkillDetailState() and for routing + button labels in MainActivity's
skill-detail `when (screen.skillId)` block.

Run from repo root:
    python3 apply_step7_patches.py

Then rebuild:
    ./gradlew assembleDebug --console=plain --no-daemon --no-configuration-cache
"""
import re
import sys
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")

def fail(msg):
    print(f"FAILED: {msg}")
    sys.exit(1)

def main():
    if not TARGET.exists():
        fail(f"{TARGET} not found -- run this from the repo root ({TARGET.parent.parent.parent.parent.parent.parent})")

    text = TARGET.read_text()
    original = text

    # ---------------------------------------------------------------
    # Patch 1: insert the RECIPE_BASED_SKILL_LABELS map just before
    # buildSkillDetailState(), tolerant of surrounding whitespace.
    # ---------------------------------------------------------------
    map_block = (
        'private val RECIPE_BASED_SKILL_LABELS: Map<String, String> = mapOf(\n'
        '    "CRAFTING" to "Select Recipe",\n'
        '    "COOKING" to "Select Dish",\n'
        '    "FLETCHING" to "Select Item",\n'
        '    "ALCHEMY" to "Select Potion"\n'
        ')\n\n'
    )

    fn_anchor_pattern = re.compile(
        r'private fun buildSkillDetailState\(skillId: String, summary: SkillSummary\): SkillDetailState \{'
    )
    matches = list(fn_anchor_pattern.finditer(text))
    if len(matches) != 1:
        fail(f"expected exactly 1 match for buildSkillDetailState() signature, found {len(matches)}")

    if "RECIPE_BASED_SKILL_LABELS" in text:
        fail("RECIPE_BASED_SKILL_LABELS already present in file -- patch may already be applied")

    insert_at = matches[0].start()
    text = text[:insert_at] + map_block + text[insert_at:]

    # ---------------------------------------------------------------
    # Patch 2: swap the CRAFTING-only check for the map-based check,
    # and generalize the hardcoded "CRAFTING" skillRequired filter.
    # Whitespace-tolerant regex so minor indentation drift doesn't break it.
    # ---------------------------------------------------------------
    actions_pattern = re.compile(
        r'val actions = if \(skillType == SkillType\.CRAFTING\) \{\s*'
        r'RecipeCatalog\.recipes\s*'
        r'\.filter \{ it\.skillRequired == "CRAFTING" && it\.levelRequired <= summary\.level \}\s*'
        r'\.map \{ SkillActionSummary\(it\.outputItemId, ItemCatalog\.find\(it\.outputItemId\)\?\.name \?: it\.outputItemId, it\.levelRequired\) \}\s*'
        r'\.sortedBy \{ it\.levelRequired \}\s*'
        r'\} else \{\s*'
        r'ActionCatalog\.allFor\(skillType\)\s*'
        r'\.filter \{ it\.levelRequired <= summary\.level \}\s*'
        r'\.map \{ SkillActionSummary\(it\.itemId, it\.displayName, it\.levelRequired\) \}\s*'
        r'\}'
    )
    matches = list(actions_pattern.finditer(text))
    if len(matches) != 1:
        fail(f"expected exactly 1 match for the actions if/else block, found {len(matches)}")

    new_actions_block = (
        'val actions = if (skillId in RECIPE_BASED_SKILL_LABELS) {\n'
        '        RecipeCatalog.recipes\n'
        '            .filter { it.skillRequired == skillId && it.levelRequired <= summary.level }\n'
        '            .map { SkillActionSummary(it.outputItemId, ItemCatalog.find(it.outputItemId)?.name ?: it.outputItemId, it.levelRequired) }\n'
        '            .sortedBy { it.levelRequired }\n'
        '    } else {\n'
        '        ActionCatalog.allFor(skillType)\n'
        '            .filter { it.levelRequired <= summary.level }\n'
        '            .map { SkillActionSummary(it.itemId, it.displayName, it.levelRequired) }\n'
        '    }'
    )
    text = actions_pattern.sub(lambda m: new_actions_block, text, count=1)

    # ---------------------------------------------------------------
    # Patch 3: routing `when (screen.skillId)` block -- replace the
    # "CRAFTING" branch with a map-membership branch covering all four
    # recipe-based skills.
    # ---------------------------------------------------------------
    routing_pattern = re.compile(
        r'when \(screen\.skillId\) \{\s*'
        r'"SMITHING" -> SmithingScreen\(\s*'
        r'buildSmithingState\(it\),\s*'
        r'\{ skillsScreenState = SkillsScreenState\.List \},\s*'
        r'\{ itemId -> gameViewModel\.startCraftingAction\(itemId\) \}\s*'
        r'\)\s*'
        r'"CRAFTING" -> SkillDetailScreen\(\s*'
        r'buildSkillDetailState\(screen\.skillId, it\),\s*'
        r'\{ skillsScreenState = SkillsScreenState\.List \},\s*'
        r'\{ itemId -> gameViewModel\.startCraftingAction\(itemId\) \},\s*'
        r'startButtonLabel = "Select Recipe"\s*'
        r'\)\s*'
        r'else -> SkillDetailScreen\(\s*'
        r'buildSkillDetailState\(screen\.skillId, it\),\s*'
        r'\{ skillsScreenState = SkillsScreenState\.List \},\s*'
        r'\{ actionId -> gameViewModel\.startSkillAction\(SkillType\.valueOf\(screen\.skillId\), actionId\) \}\s*'
        r'\)\s*'
        r'\}'
    )
    matches = list(routing_pattern.finditer(text))
    if len(matches) != 1:
        fail(f"expected exactly 1 match for the skill-detail routing when-block, found {len(matches)}")

    # Capture the original indentation of the block so the replacement lines up.
    match = matches[0]
    # Find indentation of the "when (screen.skillId) {" line itself
    line_start = text.rfind('\n', 0, match.start()) + 1
    indent = text[line_start:match.start()]
    inner_indent = indent + '    '

    new_routing_block = (
        'when (screen.skillId) {\n'
        f'{inner_indent}"SMITHING" -> SmithingScreen(\n'
        f'{inner_indent}    buildSmithingState(it),\n'
        f'{inner_indent}    {{ skillsScreenState = SkillsScreenState.List }},\n'
        f'{inner_indent}    {{ itemId -> gameViewModel.startCraftingAction(itemId) }}\n'
        f'{inner_indent})\n'
        f'{inner_indent}in RECIPE_BASED_SKILL_LABELS -> SkillDetailScreen(\n'
        f'{inner_indent}    buildSkillDetailState(screen.skillId, it),\n'
        f'{inner_indent}    {{ skillsScreenState = SkillsScreenState.List }},\n'
        f'{inner_indent}    {{ itemId -> gameViewModel.startCraftingAction(itemId) }},\n'
        f'{inner_indent}    startButtonLabel = RECIPE_BASED_SKILL_LABELS.getValue(screen.skillId)\n'
        f'{inner_indent})\n'
        f'{inner_indent}else -> SkillDetailScreen(\n'
        f'{inner_indent}    buildSkillDetailState(screen.skillId, it),\n'
        f'{inner_indent}    {{ skillsScreenState = SkillsScreenState.List }},\n'
        f'{inner_indent}    {{ actionId -> gameViewModel.startSkillAction(SkillType.valueOf(screen.skillId), actionId) }}\n'
        f'{inner_indent})\n'
        f'{indent}}}'
    )
    text = text[:match.start()] + new_routing_block + text[match.end():]

    if text == original:
        fail("no changes were made -- patterns matched but produced identical output, aborting")

    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")
    print("Now run: git diff", TARGET, "to verify before rebuilding.")

if __name__ == "__main__":
    main()
