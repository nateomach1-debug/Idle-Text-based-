#!/usr/bin/env python3
"""
Smithing show-details patch: adds the same "Show details" / "Hide details"
toggle that every other skill page already has -- exact XP numbers, next
unlock preview, and an earned-unlocks list -- to SmithingScreen.kt.

SmithingState gains earnedUnlocks/nextUnlock fields (computed in
buildSmithingState() in MainActivity.kt via a separate patch).

Run from repo root:
    python3 apply_smithing_showdetails.py
"""
import sys
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/SmithingScreen.kt")


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

    if "showAdvanced" in text:
        fail("showAdvanced already present -- patch may already be applied")

    # 1. Import SkillUnlockSummary alongside the existing ui.screens imports
    text = replace_once(
        text,
        (
            "import com.yourname.idlerpg.ui.screens.MissingIngredientSummary\n"
            "import com.yourname.idlerpg.ui.screens.MissingIngredientsDialog\n"
        ),
        (
            "import com.yourname.idlerpg.ui.screens.MissingIngredientSummary\n"
            "import com.yourname.idlerpg.ui.screens.MissingIngredientsDialog\n"
            "import com.yourname.idlerpg.ui.screens.SkillUnlockSummary\n"
        ),
        "ui.screens import block",
    )

    # 2. SmithingState gains earnedUnlocks/nextUnlock
    text = replace_once(
        text,
        (
            "data class SmithingState(\n"
            "    val displayName: String,\n"
            "    val level: Int,\n"
            "    val currentXp: Long,\n"
            "    val xpToNextLevel: Long,\n"
            "    val materials: List<SmithingMaterialCatalogEntry>\n"
            ")\n"
        ),
        (
            "data class SmithingState(\n"
            "    val displayName: String,\n"
            "    val level: Int,\n"
            "    val currentXp: Long,\n"
            "    val xpToNextLevel: Long,\n"
            "    val materials: List<SmithingMaterialCatalogEntry>,\n"
            "    val earnedUnlocks: List<SkillUnlockSummary> = emptyList(),\n"
            "    val nextUnlock: SkillUnlockSummary? = null\n"
            ")\n"
        ),
        "SmithingState declaration",
    )

    # 3. Add showAdvanced state
    text = replace_once(
        text,
        (
            "    var materialDropdownExpanded by remember { mutableStateOf(false) }\n"
            "    var selectedMaterialId by remember { mutableStateOf<String?>(null) }\n"
        ),
        (
            "    var materialDropdownExpanded by remember { mutableStateOf(false) }\n"
            "    var selectedMaterialId by remember { mutableStateOf<String?>(null) }\n"
            "    var showAdvanced by remember { mutableStateOf(false) }\n"
        ),
        "showAdvanced state declaration",
    )

    # 4. Insert the advanced-details block + toggle button after the XP bar,
    #    before the material picker Box
    text = replace_once(
        text,
        (
            "        SmithingXpBar(state.currentXp, state.xpToNextLevel)\n"
            "\n"
            "        Spacer(modifier = Modifier.height(24.dp))\n"
            "\n"
            "        Box {\n"
        ),
        (
            "        SmithingXpBar(state.currentXp, state.xpToNextLevel)\n"
            "\n"
            "        if (showAdvanced) {\n"
            "            Spacer(modifier = Modifier.height(8.dp))\n"
            "            Text(\n"
            "                text = \"XP: \" + state.currentXp + \"  |  \" + state.xpToNextLevel + \" to next level\",\n"
            "                style = MaterialTheme.typography.labelSmall\n"
            "            )\n"
            "            state.nextUnlock?.let {\n"
            "                Spacer(modifier = Modifier.height(4.dp))\n"
            "                Text(\n"
            "                    text = \"Next unlock at level \" + it.levelRequired + \": \" + it.description,\n"
            "                    style = MaterialTheme.typography.labelSmall\n"
            "                )\n"
            "            }\n"
            "        }\n"
            "\n"
            "        Spacer(modifier = Modifier.height(12.dp))\n"
            "\n"
            "        TextButton(onClick = { showAdvanced = !showAdvanced }) {\n"
            "            Text(text = if (showAdvanced) \"Hide details\" else \"Show details\")\n"
            "        }\n"
            "\n"
            "        Spacer(modifier = Modifier.height(16.dp))\n"
            "\n"
            "        Box {\n"
        ),
        "advanced-details block insertion before material picker Box",
    )

    # 5. Earned-unlocks section after the material picker Box, before the
    #    Column's closing brace
    text = replace_once(
        text,
        (
            "                }\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "\n"
            "    val selectedEntry = state.materials.find { it.material.materialId == selectedMaterialId }\n"
        ),
        (
            "                }\n"
            "            }\n"
            "        }\n"
            "\n"
            "        if (state.earnedUnlocks.isNotEmpty()) {\n"
            "            Spacer(modifier = Modifier.height(24.dp))\n"
            "            Text(text = \"Unlocks earned\", style = MaterialTheme.typography.titleMedium)\n"
            "            Spacer(modifier = Modifier.height(8.dp))\n"
            "            state.earnedUnlocks.forEach { unlock ->\n"
            "                Text(\n"
            "                    text = \"\\u2022 \" + unlock.description + \" (Lv. \" + unlock.levelRequired + \")\",\n"
            "                    style = MaterialTheme.typography.bodyMedium,\n"
            "                    modifier = Modifier.padding(vertical = 2.dp)\n"
            "                )\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "\n"
            "    val selectedEntry = state.materials.find { it.material.materialId == selectedMaterialId }\n"
        ),
        "earned-unlocks section insertion",
    )

    if text == original:
        fail("no changes were made -- aborting")

    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
