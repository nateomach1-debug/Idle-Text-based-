import pathlib

main_activity_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")
skill_detail_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/SkillDetailScreen.kt")

main_activity_text = main_activity_path.read_text()
skill_detail_text = skill_detail_path.read_text()

errors = []
ma_changed = False
sd_changed = False

# ============================================================
# MainActivity.kt: buildSkillDetailState
# ============================================================

# Case A: the Crafting/Fletching-only patch already landed - just widen it to all 4 skills.
ma_case_a_old = """    val showLockedRecipes = skillId == "CRAFTING" || skillId == "FLETCHING"
    val actions = if (skillId in RECIPE_BASED_SKILL_LABELS) {
        RecipeCatalog.recipes
            .filter { it.skillRequired == skillId && (showLockedRecipes || it.levelRequired <= summary.level) }
            .map {
                SkillActionSummary(
                    actionId = it.outputItemId,
                    displayName = ItemCatalog.find(it.outputItemId)?.name ?: it.outputItemId,
                    levelRequired = it.levelRequired,
                    missingIngredients = if (it.levelRequired <= summary.level) missingIngredientsFor(it.ingredients, inventoryQuantities) else emptyList(),
                    isLocked = it.levelRequired > summary.level
                )
            }
            .sortedBy { it.levelRequired }"""

# Case B: neither patch has landed yet - the original unmodified code.
ma_case_b_old = """    val actions = if (skillId in RECIPE_BASED_SKILL_LABELS) {
        RecipeCatalog.recipes
            .filter { it.skillRequired == skillId && it.levelRequired <= summary.level }
            .map {
                SkillActionSummary(
                    actionId = it.outputItemId,
                    displayName = ItemCatalog.find(it.outputItemId)?.name ?: it.outputItemId,
                    levelRequired = it.levelRequired,
                    missingIngredients = missingIngredientsFor(it.ingredients, inventoryQuantities)
                )
            }
            .sortedBy { it.levelRequired }"""

ma_new = """    val actions = if (skillId in RECIPE_BASED_SKILL_LABELS) {
        RecipeCatalog.recipes
            .filter { it.skillRequired == skillId }
            .map {
                SkillActionSummary(
                    actionId = it.outputItemId,
                    displayName = ItemCatalog.find(it.outputItemId)?.name ?: it.outputItemId,
                    levelRequired = it.levelRequired,
                    missingIngredients = if (it.levelRequired <= summary.level) missingIngredientsFor(it.ingredients, inventoryQuantities) else emptyList(),
                    isLocked = it.levelRequired > summary.level
                )
            }
            .sortedBy { it.levelRequired }"""

count_a = main_activity_text.count(ma_case_a_old)
count_b = main_activity_text.count(ma_case_b_old)
count_already_done = main_activity_text.count(ma_new)

if count_already_done == 1 and count_a == 0 and count_b == 0:
    pass  # already fully applied, nothing to do
elif count_a == 1:
    main_activity_text = main_activity_text.replace(ma_case_a_old, ma_new)
    ma_changed = True
elif count_b == 1:
    main_activity_text = main_activity_text.replace(ma_case_b_old, ma_new)
    ma_changed = True
else:
    errors.append(
        f"MainActivity.kt: none of the expected states matched cleanly "
        f"(case A count={count_a}, case B count={count_b}, already-done count={count_already_done})"
    )

# ============================================================
# SkillDetailScreen.kt: SkillActionSummary + ActionRow
# ============================================================

sd_old_1 = """data class SkillActionSummary(
    val actionId: String,
    val displayName: String,
    val levelRequired: Int,
    val missingIngredients: List<MissingIngredientSummary> = emptyList()
)"""

sd_new_1 = """data class SkillActionSummary(
    val actionId: String,
    val displayName: String,
    val levelRequired: Int,
    val missingIngredients: List<MissingIngredientSummary> = emptyList(),
    val isLocked: Boolean = false
)"""

sd_old_2 = """@Composable
private fun ActionRow(action: SkillActionSummary, onActionSelected: (String) -> Unit) {
    var showMissingDialog by remember { mutableStateOf(false) }
    val affordable = action.missingIngredients.isEmpty()
    val contentColor = if (affordable) {
        MaterialTheme.colorScheme.onSurface
    } else {
        MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f)
    }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .clickable {
                if (affordable) onActionSelected(action.actionId) else showMissingDialog = true
            }
            .padding(vertical = 12.dp, horizontal = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(text = action.displayName, style = MaterialTheme.typography.bodyMedium, color = overrideColor(contentColor))
        Text(text = "Lv. " + action.levelRequired, style = MaterialTheme.typography.labelSmall, color = overrideColor(contentColor))
    }

    if (showMissingDialog) {
        MissingIngredientsDialog(
            itemName = action.displayName,
            missing = action.missingIngredients,
            onDismiss = { showMissingDialog = false }
        )
    }
}"""

sd_new_2 = """@Composable
private fun ActionRow(action: SkillActionSummary, onActionSelected: (String) -> Unit) {
    var showMissingDialog by remember { mutableStateOf(false) }
    var showLockedDialog by remember { mutableStateOf(false) }
    val affordable = !action.isLocked && action.missingIngredients.isEmpty()
    val contentColor = if (affordable) {
        MaterialTheme.colorScheme.onSurface
    } else {
        MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f)
    }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .clickable {
                when {
                    action.isLocked -> showLockedDialog = true
                    affordable -> onActionSelected(action.actionId)
                    else -> showMissingDialog = true
                }
            }
            .padding(vertical = 12.dp, horizontal = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = (if (action.isLocked) "\\uD83D\\uDD12 " else "") + action.displayName,
            style = MaterialTheme.typography.bodyMedium,
            color = overrideColor(contentColor)
        )
        Text(text = "Lv. " + action.levelRequired, style = MaterialTheme.typography.labelSmall, color = overrideColor(contentColor))
    }

    if (showMissingDialog) {
        MissingIngredientsDialog(
            itemName = action.displayName,
            missing = action.missingIngredients,
            onDismiss = { showMissingDialog = false }
        )
    }

    if (showLockedDialog) {
        AlertDialog(
            onDismissRequest = { showLockedDialog = false },
            title = { Text(text = "Not yet unlocked", style = MaterialTheme.typography.titleMedium) },
            text = {
                Text(text = action.displayName + " requires level " + action.levelRequired + ".")
            },
            confirmButton = {
                TextButton(onClick = { showLockedDialog = false }) {
                    Text(text = "OK")
                }
            }
        )
    }
}"""

count_sd1_old = skill_detail_text.count(sd_old_1)
count_sd1_new = skill_detail_text.count(sd_new_1)
count_sd2_old = skill_detail_text.count(sd_old_2)
count_sd2_new = skill_detail_text.count(sd_new_2)

if count_sd1_new == 1:
    pass  # already applied
elif count_sd1_old == 1:
    skill_detail_text = skill_detail_text.replace(sd_old_1, sd_new_1)
    sd_changed = True
else:
    errors.append(f"SkillDetailScreen.kt SkillActionSummary: expected old or new form exactly once, found old={count_sd1_old} new={count_sd1_new}")

if count_sd2_new == 1:
    pass  # already applied
elif count_sd2_old == 1:
    skill_detail_text = skill_detail_text.replace(sd_old_2, sd_new_2)
    sd_changed = True
else:
    errors.append(f"SkillDetailScreen.kt ActionRow: expected old or new form exactly once, found old={count_sd2_old} new={count_sd2_new}")

if errors:
    raise SystemExit(
        "PATCH FAILED: could not confidently determine current file state. "
        "No changes made to either file.\n" + "\n".join(f"  - {e}" for e in errors)
    )

if ma_changed:
    main_activity_path.write_text(main_activity_text)
    print("Patched MainActivity.kt: all 4 recipe-based skills (Crafting/Cooking/Fletching/Alchemy) now show locked recipes.")
else:
    print("MainActivity.kt: already up to date, no change needed.")

if sd_changed:
    skill_detail_path.write_text(skill_detail_text)
    print("Patched SkillDetailScreen.kt.")
else:
    print("SkillDetailScreen.kt: already up to date, no change needed.")
