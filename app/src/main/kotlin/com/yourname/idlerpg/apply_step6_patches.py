"""
Step 6 patch script: wires Crafting and Smithing into the UI.

Run from the repo root:
    python3 apply_step6_patches.py

Unlike the Step 5 script, these patches use indentation-tolerant regex
matching rather than exact whitespace strings -- safer given how much this
conversation has gone through. Each patch still asserts exactly ONE match
before touching anything; if a pattern doesn't match your actual file
(e.g. it was refactored since I last saw it), the script stops with a
clear error naming which patch failed, and changes nothing.

After running, diff every touched file before building:
    git diff app/src/main/kotlin/com/yourname/idlerpg/SkillDetailScreen.kt
    git diff app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt

SmithingScreen.kt is a brand new file (no patching needed) -- copy it into
place separately, see STEP6_INSTRUCTIONS.md.
"""

import re

BASE = "app/src/main/kotlin/com/yourname/idlerpg/"


def apply_regex_patch(path, pattern, build_replacement, label, flags=re.MULTILINE):
    with open(path, "r") as f:
        content = f.read()
    matches = list(re.finditer(pattern, content, flags))
    assert len(matches) == 1, (
        f"[{label}] Expected exactly 1 match in {path}, found {len(matches)}.\n"
        f"--- pattern ---\n{pattern}\n--- end pattern ---"
    )
    m = matches[0]
    replacement = build_replacement(m)
    content = content[: m.start()] + replacement + content[m.end() :]
    with open(path, "w") as f:
        f.write(content)
    print(f"OK  [{label}] patched {path}")


# =========================================================
# FILE 1: SkillDetailScreen.kt -- add configurable start-button label
# =========================================================
p = BASE + "SkillDetailScreen.kt"

# 1a. Function signature: add startButtonLabel parameter with a default
#     that preserves current behavior for every skill that doesn't pass one.
pattern_1a = (
    r"(fun SkillDetailScreen\(\s*"
    r"state: SkillDetailState,\s*"
    r"onBack: \(\) -> Unit,\s*"
    r"onStartAction: \(String\) -> Unit,\s*"
    r"modifier: Modifier = Modifier\s*"
    r"\))"
)

def build_1a(m):
    original = m.group(1)
    # insert a new parameter right before the closing paren
    return original[:-1].rstrip() + ",\n    startButtonLabel: String = \"Start \" + state.displayName\n)"

apply_regex_patch(p, pattern_1a, build_1a, label="1a: SkillDetailScreen signature")

# 1b. The button's Text(...) content: swap the hardcoded "Start " + displayName
#     for the new parameter.
pattern_1b = r'Text\(text = "Start " \+ state\.displayName\)'
apply_regex_patch(p, pattern_1b, lambda m: "Text(text = startButtonLabel)", label="1b: button text")

print()

# =========================================================
# FILE 2: MainActivity.kt
# =========================================================
p = BASE + "MainActivity.kt"

# 2a. buildSkillDetailState: branch CRAFTING through RecipeCatalog instead
#     of ActionCatalog, everything else unchanged.
pattern_2a = (
    r"( *)val actions = ActionCatalog\.allFor\(skillType\)\s*\n"
    r" *\.filter \{ it\.levelRequired <= summary\.level \}\s*\n"
    r" *\.map \{ SkillActionSummary\(it\.itemId, it\.displayName, it\.levelRequired\) \}"
)

def build_2a(m):
    indent = m.group(1)
    return (
        f"{indent}val actions = if (skillType == SkillType.CRAFTING) {{\n"
        f"{indent}    RecipeCatalog.recipes\n"
        f"{indent}        .filter {{ it.skillRequired == \"CRAFTING\" && it.levelRequired <= summary.level }}\n"
        f"{indent}        .map {{ SkillActionSummary(it.outputItemId, ItemCatalog.find(it.outputItemId)?.name ?: it.outputItemId, it.levelRequired) }}\n"
        f"{indent}        .sortedBy {{ it.levelRequired }}\n"
        f"{indent}}} else {{\n"
        f"{indent}    ActionCatalog.allFor(skillType)\n"
        f"{indent}        .filter {{ it.levelRequired <= summary.level }}\n"
        f"{indent}        .map {{ SkillActionSummary(it.itemId, it.displayName, it.levelRequired) }}\n"
        f"{indent}}}"
    )

apply_regex_patch(p, pattern_2a, build_2a, label="2a: buildSkillDetailState CRAFTING branch")

# 2b. Call site: route SMITHING to SmithingScreen, CRAFTING to SkillDetailScreen
#     with the "Select Recipe" label + startCraftingAction, everything else unchanged.
pattern_2b = (
    r"( *)is SkillsScreenState\.Detail -> allSkills\[screen\.skillId\]\?\.let \{\s*\n"
    r" *SkillDetailScreen\(\s*\n"
    r" *buildSkillDetailState\(screen\.skillId, it\),\s*\n"
    r" *\{ skillsScreenState = SkillsScreenState\.List \},\s*\n"
    r" *\{ actionId -> gameViewModel\.startSkillAction\(SkillType\.valueOf\(screen\.skillId\), actionId\) \}\s*\n"
    r" *\)\s*\n"
    r" *\}"
)

def build_2b(m):
    indent = m.group(1)
    inner = indent + "    "
    return (
        f"{indent}is SkillsScreenState.Detail -> allSkills[screen.skillId]?.let {{\n"
        f"{inner}when (screen.skillId) {{\n"
        f"{inner}    \"SMITHING\" -> SmithingScreen(\n"
        f"{inner}        buildSmithingState(it),\n"
        f"{inner}        {{ skillsScreenState = SkillsScreenState.List }},\n"
        f"{inner}        {{ itemId -> gameViewModel.startCraftingAction(itemId) }}\n"
        f"{inner}    )\n"
        f"{inner}    \"CRAFTING\" -> SkillDetailScreen(\n"
        f"{inner}        buildSkillDetailState(screen.skillId, it),\n"
        f"{inner}        {{ skillsScreenState = SkillsScreenState.List }},\n"
        f"{inner}        {{ itemId -> gameViewModel.startCraftingAction(itemId) }},\n"
        f"{inner}        startButtonLabel = \"Select Recipe\"\n"
        f"{inner}    )\n"
        f"{inner}    else -> SkillDetailScreen(\n"
        f"{inner}        buildSkillDetailState(screen.skillId, it),\n"
        f"{inner}        {{ skillsScreenState = SkillsScreenState.List }},\n"
        f"{inner}        {{ actionId -> gameViewModel.startSkillAction(SkillType.valueOf(screen.skillId), actionId) }}\n"
        f"{inner}    )\n"
        f"{inner}}}\n"
        f"{indent}}}"
    )

apply_regex_patch(p, pattern_2b, build_2b, label="2b: skill detail routing")

# 2c. Insert buildSmithingState / buildCraftingActions / recipeToSummary /
#     SMITHING_METALS right before demoZones(), a stable, distinctive anchor.
pattern_2c = r"( *)private fun demoZones\(\): List<ZoneSummary> = listOf\("

def build_2c(m):
    indent = m.group(1)
    helpers = f"""{indent}private val SMITHING_METALS = listOf(
{indent}    Triple("bronze", "Bronze", "bronze_bar"),
{indent}    Triple("iron", "Iron", "iron_bar"),
{indent}    Triple("steel", "Steel", "steel_bar"),
{indent}    Triple("mithril", "Mithril", "mithril_bar"),
{indent}    Triple("adamant", "Adamant", "adamantite_bar"),
{indent}    Triple("rune", "Rune", "runite_bar"),
{indent}    Triple("orichalcum", "Orichalcum", "orichalcum_bar"),
{indent}    Triple("celestial", "Celestial", "celestial_alloy_bar")
{indent})

{indent}private fun recipeToSmithingSummary(recipe: Recipe): SmithingRecipeSummary {{
{indent}    val displayName = ItemCatalog.find(recipe.outputItemId)?.name ?: recipe.outputItemId
{indent}    val ingredients = recipe.ingredients.map {{ ing ->
{indent}        val ingName = ItemCatalog.find(ing.itemId)?.name ?: ing.itemId
{indent}        SmithingIngredientSummary(ing.itemId, ingName, ing.quantity)
{indent}    }}
{indent}    return SmithingRecipeSummary(recipe.outputItemId, displayName, recipe.levelRequired, ingredients)
{indent}}}

{indent}private fun buildSmithingState(summary: SkillSummary): SmithingState {{
{indent}    val materials = SMITHING_METALS.map {{ (materialId, displayName, barItemId) ->
{indent}        val barRecipe = RecipeCatalog.forOutput(barItemId)?.let {{ recipeToSmithingSummary(it) }}
{indent}        val gearRecipes = RecipeCatalog.recipes
{indent}            .filter {{ it.skillRequired == "SMITHING" && it.ingredients.any {{ ing -> ing.itemId == barItemId }} }}
{indent}            .map {{ recipeToSmithingSummary(it) }}
{indent}            .sortedBy {{ it.levelRequired }}
{indent}        SmithingMaterialCatalogEntry(
{indent}            material = SmithingMaterialOption(materialId, displayName),
{indent}            bar = barRecipe,
{indent}            gear = gearRecipes
{indent}        )
{indent}    }}
{indent}    return SmithingState(
{indent}        displayName = summary.displayName,
{indent}        level = summary.level,
{indent}        currentXp = summary.currentXp,
{indent}        xpToNextLevel = summary.xpToNextLevel,
{indent}        materials = materials
{indent}    )
{indent}}}

"""
    return helpers + indent + 'private fun demoZones(): List<ZoneSummary> = listOf('

apply_regex_patch(p, pattern_2c, build_2c, label="2c: buildSmithingState + helpers")

print()
print("=" * 60)
print("All Step 6 patches applied successfully.")
print("=" * 60)
print()
print("Remaining manual step: copy SmithingScreen.kt into place --")
print("it's a brand new file, not a patch:")
print()
print("  cp SmithingScreen.kt app/src/main/kotlin/com/yourname/idlerpg/SmithingScreen.kt")
print()
print("Then git diff both touched files, then rebuild.")
