#!/usr/bin/env python3
"""
Two independent MainActivity.kt edits, bundled since both are small:

1. Scroll-memory: hoists a LazyListState + LazyGridState at the app-root
   level (same scope as inventoryQuantities/equipped, which never gets
   disposed by `when(destination)` switches) and passes them into
   SkillsScreen(), so scroll position survives navigating away and back.

2. Smithing show-details: buildSmithingState() now computes earned/next
   unlocks via UnlockTable for SkillType.SMITHING (same pattern already
   used in buildSkillDetailState()) and passes them into SmithingState.

Run from repo root, AFTER apply_scrollmemory_skillsscreen.py and
apply_smithing_showdetails.py:
    python3 apply_mainactivity_details_scroll.py
Then rebuild:
    ./gradlew assembleDebug --console=plain --no-daemon --no-configuration-cache
"""
import sys
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")


def fail(msg):
    print(f"FAILED: {msg}")
    sys.exit(1)


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        fail(f"expected exactly 1 occurrence of [{label}], found {count}")
    return text.replace(old, new, 1)


def main():
    if not TARGET.exists():
        fail(f"{TARGET} not found -- run this from the repo root")

    text = TARGET.read_text()
    original = text

    if "skillsListScrollState" in text:
        fail("skillsListScrollState already present -- patch may already be applied")

    # 1. Imports for Lazy state + rememberLazyListState/rememberLazyGridState
    text = replace_once(
        text,
        "import java.time.Instant\n",
        (
            "import androidx.compose.foundation.lazy.LazyListState\n"
            "import androidx.compose.foundation.lazy.rememberLazyListState\n"
            "import androidx.compose.foundation.lazy.grid.LazyGridState\n"
            "import androidx.compose.foundation.lazy.grid.rememberLazyGridState\n"
            "import java.time.Instant\n"
        ),
        "import block",
    )

    # 2. Hoist scroll state near inventoryQuantities/equipped
    text = replace_once(
        text,
        (
            "    val inventoryQuantities = remember(inventoryItemEntries) {\n"
            "        inventoryItemEntries.associate { it.itemId to it.quantity }\n"
            "    }\n"
            "    val equipped = remember { demoEquipped() }\n"
        ),
        (
            "    val inventoryQuantities = remember(inventoryItemEntries) {\n"
            "        inventoryItemEntries.associate { it.itemId to it.quantity }\n"
            "    }\n"
            "    val equipped = remember { demoEquipped() }\n"
            "    val skillsListScrollState = rememberLazyListState()\n"
            "    val skillsGridScrollState = rememberLazyGridState()\n"
        ),
        "hoisted scroll state declaration",
    )

    # 3. buildSmithingState(): compute earned/next unlocks via UnlockTable
    text = replace_once(
        text,
        (
            "private fun buildSmithingState(summary: SkillSummary, inventoryQuantities: Map<String, Int>): SmithingState {\n"
            "    val materials = SMITHING_METALS.map { (materialId, displayName, barItemId) ->\n"
        ),
        (
            "private fun buildSmithingState(summary: SkillSummary, inventoryQuantities: Map<String, Int>): SmithingState {\n"
            "    val skillType = SkillType.SMITHING\n"
            "    val earned = UnlockTable.unlocksEarnedAt(skillType, summary.level).map { unlock ->\n"
            "        SkillUnlockSummary(\n"
            "            description = unlock.grantedEffects.joinToString(\", \") { effectSummaryText(it) },\n"
            "            levelRequired = unlock.levelRequired\n"
            "        )\n"
            "    }\n"
            "    val next = UnlockTable.allUnlocksFor(skillType)\n"
            "        .filter { it.levelRequired > summary.level }\n"
            "        .minByOrNull { it.levelRequired }\n"
            "        ?.let { unlock ->\n"
            "            SkillUnlockSummary(\n"
            "                description = unlock.grantedEffects.joinToString(\", \") { effectSummaryText(it) },\n"
            "                levelRequired = unlock.levelRequired\n"
            "            )\n"
            "        }\n\n"
            "    val materials = SMITHING_METALS.map { (materialId, displayName, barItemId) ->\n"
        ),
        "buildSmithingState unlock computation",
    )

    # 4. buildSmithingState(): pass earned/next into SmithingState
    text = replace_once(
        text,
        (
            "    return SmithingState(\n"
            "        displayName = summary.displayName,\n"
            "        level = summary.level,\n"
            "        currentXp = summary.currentXp,\n"
            "        xpToNextLevel = summary.xpToNextLevel,\n"
            "        materials = materials\n"
            "    )\n"
            "}\n"
        ),
        (
            "    return SmithingState(\n"
            "        displayName = summary.displayName,\n"
            "        level = summary.level,\n"
            "        currentXp = summary.currentXp,\n"
            "        xpToNextLevel = summary.xpToNextLevel,\n"
            "        materials = materials,\n"
            "        earnedUnlocks = earned,\n"
            "        nextUnlock = next\n"
            "    )\n"
            "}\n"
        ),
        "buildSmithingState SmithingState construction",
    )

    # 5. SkillsScreen() call site: pass hoisted scroll state through
    text = replace_once(
        text,
        (
            "                                is SkillsScreenState.List -> SkillsScreen(\n"
            "                                    allSkills = allSkills,\n"
            "                                    onSkillSelected = { skillsScreenState = SkillsScreenState.Detail(it) }\n"
            "                                )\n"
        ),
        (
            "                                is SkillsScreenState.List -> SkillsScreen(\n"
            "                                    allSkills = allSkills,\n"
            "                                    onSkillSelected = { skillsScreenState = SkillsScreenState.Detail(it) },\n"
            "                                    listState = skillsListScrollState,\n"
            "                                    gridState = skillsGridScrollState\n"
            "                                )\n"
        ),
        "SkillsScreen() call site",
    )

    if text == original:
        fail("no changes were made -- aborting")

    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")
    print("Run: git diff", TARGET, "to verify before rebuilding.")


if __name__ == "__main__":
    main()
