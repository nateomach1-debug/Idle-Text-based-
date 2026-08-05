#!/usr/bin/env python3
"""
Ingredient-check patch, part 3: MainActivity.kt

- New `inventoryQuantities: Map<String, Int>` built once from inventoryItemEntries.
- New shared `missingIngredientsFor()` helper comparing a recipe's ingredients
  against inventoryQuantities.
- buildSkillDetailState() / buildSmithingState() both take inventoryQuantities
  and attach missingIngredients to each action/recipe.
- Both call sites in the skill-detail routing `when` block pass
  inventoryQuantities through.

Run from repo root, AFTER apply_ingredientcheck_skilldetail.py and
apply_ingredientcheck_smithing.py:
    python3 apply_ingredientcheck_mainactivity.py
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

    if "inventoryQuantities" in text:
        fail("inventoryQuantities already present -- patch may already be applied")

    # 1. New inventoryQuantities derived state, right after inventoryItems
    text = replace_once(
        text,
        (
            "    val inventoryItemEntries by gameViewModel.inventoryItems.collectAsState()\n"
            "    val inventoryItems = remember(inventoryItemEntries) { buildInventoryItemSummaries(inventoryItemEntries) }\n"
        ),
        (
            "    val inventoryItemEntries by gameViewModel.inventoryItems.collectAsState()\n"
            "    val inventoryItems = remember(inventoryItemEntries) { buildInventoryItemSummaries(inventoryItemEntries) }\n"
            "    val inventoryQuantities = remember(inventoryItemEntries) {\n"
            "        inventoryItemEntries.associate { it.itemId to it.quantity }\n"
            "    }\n"
        ),
        "inventoryQuantities declaration",
    )

    # 2. Shared missingIngredientsFor() helper, right before buildSkillDetailState
    text = replace_once(
        text,
        "private fun buildSkillDetailState(skillId: String, summary: SkillSummary): SkillDetailState {",
        (
            "private fun missingIngredientsFor(\n"
            "    ingredients: List<RecipeIngredient>,\n"
            "    inventoryQuantities: Map<String, Int>\n"
            "): List<MissingIngredientSummary> {\n"
            "    return ingredients.mapNotNull { ingredient ->\n"
            "        val have = inventoryQuantities[ingredient.itemId] ?: 0\n"
            "        if (have < ingredient.quantity) {\n"
            "            MissingIngredientSummary(\n"
            "                displayName = ItemCatalog.find(ingredient.itemId)?.name ?: ingredient.itemId,\n"
            "                required = ingredient.quantity,\n"
            "                have = have\n"
            "            )\n"
            "        } else {\n"
            "            null\n"
            "        }\n"
            "    }\n"
            "}\n\n"
            "private fun buildSkillDetailState(\n"
            "    skillId: String,\n"
            "    summary: SkillSummary,\n"
            "    inventoryQuantities: Map<String, Int>\n"
            "): SkillDetailState {"
        ),
        "buildSkillDetailState signature + missingIngredientsFor helper",
    )

    # 3. buildSkillDetailState's recipe-based actions branch: attach missingIngredients
    text = replace_once(
        text,
        (
            "    val actions = if (skillId in RECIPE_BASED_SKILL_LABELS) {\n"
            "        RecipeCatalog.recipes\n"
            "            .filter { it.skillRequired == skillId && it.levelRequired <= summary.level }\n"
            "            .map { SkillActionSummary(it.outputItemId, ItemCatalog.find(it.outputItemId)?.name ?: it.outputItemId, it.levelRequired) }\n"
            "            .sortedBy { it.levelRequired }\n"
            "    } else {\n"
        ),
        (
            "    val actions = if (skillId in RECIPE_BASED_SKILL_LABELS) {\n"
            "        RecipeCatalog.recipes\n"
            "            .filter { it.skillRequired == skillId && it.levelRequired <= summary.level }\n"
            "            .map {\n"
            "                SkillActionSummary(\n"
            "                    actionId = it.outputItemId,\n"
            "                    displayName = ItemCatalog.find(it.outputItemId)?.name ?: it.outputItemId,\n"
            "                    levelRequired = it.levelRequired,\n"
            "                    missingIngredients = missingIngredientsFor(it.ingredients, inventoryQuantities)\n"
            "                )\n"
            "            }\n"
            "            .sortedBy { it.levelRequired }\n"
            "    } else {\n"
        ),
        "buildSkillDetailState recipe-based actions mapping",
    )

    # 4. buildSmithingState signature + bar/gear recipe mapping
    text = replace_once(
        text,
        (
            "private fun buildSmithingState(summary: SkillSummary): SmithingState {\n"
            "    val materials = SMITHING_METALS.map { (materialId, displayName, barItemId) ->\n"
            "        val barRecipe = RecipeCatalog.forOutput(barItemId)?.let { recipeToSmithingSummary(it) }\n"
            "        val gearRecipes = RecipeCatalog.recipes\n"
            "            .filter { it.skillRequired == \"SMITHING\" && it.ingredients.any { ing -> ing.itemId == barItemId } }\n"
            "            .map { recipeToSmithingSummary(it) }\n"
            "            .sortedBy { it.levelRequired }\n"
        ),
        (
            "private fun buildSmithingState(summary: SkillSummary, inventoryQuantities: Map<String, Int>): SmithingState {\n"
            "    val materials = SMITHING_METALS.map { (materialId, displayName, barItemId) ->\n"
            "        val barRecipe = RecipeCatalog.forOutput(barItemId)?.let {\n"
            "            recipeToSmithingSummary(it).copy(\n"
            "                missingIngredients = missingIngredientsFor(it.ingredients, inventoryQuantities)\n"
            "            )\n"
            "        }\n"
            "        val gearRecipes = RecipeCatalog.recipes\n"
            "            .filter { it.skillRequired == \"SMITHING\" && it.ingredients.any { ing -> ing.itemId == barItemId } }\n"
            "            .map {\n"
            "                recipeToSmithingSummary(it).copy(\n"
            "                    missingIngredients = missingIngredientsFor(it.ingredients, inventoryQuantities)\n"
            "                )\n"
            "            }\n"
            "            .sortedBy { it.levelRequired }\n"
        ),
        "buildSmithingState signature + recipe mapping",
    )

    # 5. Routing when-block call sites: pass inventoryQuantities through
    text = replace_once(
        text,
        (
            "                                    when (screen.skillId) {\n"
            "                                        \"SMITHING\" -> SmithingScreen(\n"
            "                                            buildSmithingState(it),\n"
            "                                            { skillsScreenState = SkillsScreenState.List },\n"
            "                                            { itemId -> gameViewModel.startCraftingAction(itemId) }\n"
            "                                        )\n"
            "                                        in RECIPE_BASED_SKILL_LABELS -> SkillDetailScreen(\n"
            "                                            buildSkillDetailState(screen.skillId, it),\n"
            "                                            { skillsScreenState = SkillsScreenState.List },\n"
            "                                            { itemId -> gameViewModel.startCraftingAction(itemId) },\n"
            "                                            startButtonLabel = RECIPE_BASED_SKILL_LABELS.getValue(screen.skillId)\n"
            "                                        )\n"
            "                                        else -> SkillDetailScreen(\n"
            "                                            buildSkillDetailState(screen.skillId, it),\n"
            "                                            { skillsScreenState = SkillsScreenState.List },\n"
            "                                            { actionId -> gameViewModel.startSkillAction(SkillType.valueOf(screen.skillId), actionId) }\n"
            "                                        )\n"
            "                                    }\n"
        ),
        (
            "                                    when (screen.skillId) {\n"
            "                                        \"SMITHING\" -> SmithingScreen(\n"
            "                                            buildSmithingState(it, inventoryQuantities),\n"
            "                                            { skillsScreenState = SkillsScreenState.List },\n"
            "                                            { itemId -> gameViewModel.startCraftingAction(itemId) }\n"
            "                                        )\n"
            "                                        in RECIPE_BASED_SKILL_LABELS -> SkillDetailScreen(\n"
            "                                            buildSkillDetailState(screen.skillId, it, inventoryQuantities),\n"
            "                                            { skillsScreenState = SkillsScreenState.List },\n"
            "                                            { itemId -> gameViewModel.startCraftingAction(itemId) },\n"
            "                                            startButtonLabel = RECIPE_BASED_SKILL_LABELS.getValue(screen.skillId)\n"
            "                                        )\n"
            "                                        else -> SkillDetailScreen(\n"
            "                                            buildSkillDetailState(screen.skillId, it, inventoryQuantities),\n"
            "                                            { skillsScreenState = SkillsScreenState.List },\n"
            "                                            { actionId -> gameViewModel.startSkillAction(SkillType.valueOf(screen.skillId), actionId) }\n"
            "                                        )\n"
            "                                    }\n"
        ),
        "routing when-block call sites",
    )

    if text == original:
        fail("no changes were made -- aborting")

    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")
    print("Run: git diff", TARGET, "to verify before rebuilding.")


if __name__ == "__main__":
    main()
