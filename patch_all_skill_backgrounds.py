import pathlib

main_activity_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")
skill_detail_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/SkillDetailScreen.kt")

main_activity_text = main_activity_path.read_text()
skill_detail_text = skill_detail_path.read_text()

errors = []

# --- MainActivity.kt: buildSkillDetailState filter/map ---
ma_old = """    val actions = if (skillId in RECIPE_BASED_SKILL_LABELS) {
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

ma_new = """    val showLockedRecipes = skillId == "CRAFTING" || skillId == "FLETCHING"
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

count = main_activity_text.count(ma_old)
if count != 1:
    errors.append(f"MainActivity.kt buildSkillDetailState edit: expected 1 match, found {count}")

# --- SkillDetailScreen.kt: SkillActionSummary data class ---
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

count = skill_detail_text.count(sd_old_1)
if count != 1:
    errors.append(f"SkillDetailScreen.kt SkillActionSummary edit: expected 1 match, found {count}")

# --- SkillDetailScreen.kt: ActionRow ---
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

count = skill_detail_text.count(sd_old_2)
if count != 1:
    errors.append(f"SkillDetailScreen.kt ActionRow edit: expected 1 match, found {count}")

if errors:
    raise SystemExit(
        "PATCH FAILED: one or more expected blocks did not match exactly once. "
        "No changes made to either file.\n" + "\n".join(f"  - {e}" for e in errors)
    )

main_activity_text = main_activity_text.replace(ma_old, ma_new)
skill_detail_text = skill_detail_text.replace(sd_old_1, sd_new_1).replace(sd_old_2, sd_new_2)

main_activity_path.write_text(main_activity_text)
skill_detail_path.write_text(skill_detail_text)

print("Patched MainActivity.kt: Crafting/Fletching recipes no longer hidden, just marked isLocked.")
print("Patched SkillDetailScreen.kt: SkillActionSummary.isLocked added, ActionRow shows locked items with a lock icon + 'Not yet unlocked' dialog.")
