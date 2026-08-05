#!/usr/bin/env python3
"""
Ingredient-check patch, part 2: SmithingScreen.kt

- SmithingRecipeSummary gains `missingIngredients: List<MissingIngredientSummary>`
  (reusing the type from SkillDetailScreen.kt / com.yourname.idlerpg.ui.screens).
- SmithingRecipeRow's existing level-based grey-out (`eligible`) extends to also
  require missingIngredients.isEmpty(); the row now always has a clickable
  modifier so a level-OK-but-missing-ingredients tap can open the shared
  MissingIngredientsDialog instead of doing nothing.

Run from repo root, AFTER apply_ingredientcheck_skilldetail.py (this file
reuses MissingIngredientSummary/MissingIngredientsDialog defined there):
    python3 apply_ingredientcheck_smithing.py
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

    if "MissingIngredientSummary" in text:
        fail("MissingIngredientSummary already referenced -- patch may already be applied")

    # 1. Import the shared types from SkillDetailScreen.kt's package
    text = replace_once(
        text,
        "package com.yourname.idlerpg\n\n",
        (
            "package com.yourname.idlerpg\n\n"
            "import com.yourname.idlerpg.ui.screens.MissingIngredientSummary\n"
            "import com.yourname.idlerpg.ui.screens.MissingIngredientsDialog\n"
        ),
        "package/import header",
    )

    # 2. SmithingRecipeSummary gains missingIngredients
    text = replace_once(
        text,
        (
            "data class SmithingRecipeSummary(\n"
            "    val itemId: String,\n"
            "    val displayName: String,\n"
            "    val levelRequired: Int,\n"
            "    val ingredients: List<SmithingIngredientSummary>\n"
            ")\n"
        ),
        (
            "data class SmithingRecipeSummary(\n"
            "    val itemId: String,\n"
            "    val displayName: String,\n"
            "    val levelRequired: Int,\n"
            "    val ingredients: List<SmithingIngredientSummary>,\n"
            "    val missingIngredients: List<MissingIngredientSummary> = emptyList()\n"
            ")\n"
        ),
        "SmithingRecipeSummary declaration",
    )

    # 3. SmithingRecipeRow: extend eligibility, always attach clickable, add popup
    text = replace_once(
        text,
        (
            "@Composable\n"
            "private fun SmithingRecipeRow(\n"
            "    recipe: SmithingRecipeSummary,\n"
            "    playerLevel: Int,\n"
            "    showIngredients: Boolean,\n"
            "    onClick: () -> Unit\n"
            ") {\n"
            "    val eligible = playerLevel >= recipe.levelRequired\n"
            "    val contentColor = if (eligible) {\n"
            "        MaterialTheme.colorScheme.onSurface\n"
            "    } else {\n"
            "        MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f)\n"
            "    }\n\n"
            "    Column(\n"
            "        modifier = Modifier\n"
            "            .fillMaxWidth()\n"
            "            .clip(RoundedCornerShape(10.dp))\n"
            "            .then(if (eligible) Modifier.clickable { onClick() } else Modifier)\n"
            "            .padding(vertical = 10.dp, horizontal = 8.dp)\n"
            "    ) {\n"
        ),
        (
            "@Composable\n"
            "private fun SmithingRecipeRow(\n"
            "    recipe: SmithingRecipeSummary,\n"
            "    playerLevel: Int,\n"
            "    showIngredients: Boolean,\n"
            "    onClick: () -> Unit\n"
            ") {\n"
            "    var showMissingDialog by remember { mutableStateOf(false) }\n"
            "    val levelOk = playerLevel >= recipe.levelRequired\n"
            "    val ingredientsOk = recipe.missingIngredients.isEmpty()\n"
            "    val eligible = levelOk && ingredientsOk\n"
            "    val contentColor = if (eligible) {\n"
            "        MaterialTheme.colorScheme.onSurface\n"
            "    } else {\n"
            "        MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f)\n"
            "    }\n\n"
            "    Column(\n"
            "        modifier = Modifier\n"
            "            .fillMaxWidth()\n"
            "            .clip(RoundedCornerShape(10.dp))\n"
            "            .clickable {\n"
            "                if (!levelOk) return@clickable\n"
            "                if (!ingredientsOk) showMissingDialog = true else onClick()\n"
            "            }\n"
            "            .padding(vertical = 10.dp, horizontal = 8.dp)\n"
            "    ) {\n"
        ),
        "SmithingRecipeRow eligibility + clickable",
    )

    # 4. Add the popup dialog call right before the row's closing brace
    text = replace_once(
        text,
        (
            "        if (showIngredients && recipe.ingredients.isNotEmpty()) {\n"
            "            Spacer(modifier = Modifier.height(2.dp))\n"
            "            Text(\n"
            "                text = recipe.ingredients.joinToString(\", \") { it.quantity.toString() + \"x \" + it.displayName },\n"
            "                style = MaterialTheme.typography.labelSmall,\n"
            "                color = contentColor\n"
            "            )\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        (
            "        if (showIngredients && recipe.ingredients.isNotEmpty()) {\n"
            "            Spacer(modifier = Modifier.height(2.dp))\n"
            "            Text(\n"
            "                text = recipe.ingredients.joinToString(\", \") { it.quantity.toString() + \"x \" + it.displayName },\n"
            "                style = MaterialTheme.typography.labelSmall,\n"
            "                color = contentColor\n"
            "            )\n"
            "        }\n"
            "    }\n\n"
            "    if (showMissingDialog) {\n"
            "        MissingIngredientsDialog(\n"
            "            itemName = recipe.displayName,\n"
            "            missing = recipe.missingIngredients,\n"
            "            onDismiss = { showMissingDialog = false }\n"
            "        )\n"
            "    }\n"
            "}\n"
        ),
        "SmithingRecipeRow closing brace / popup insertion",
    )

    if text == original:
        fail("no changes were made -- aborting")

    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
