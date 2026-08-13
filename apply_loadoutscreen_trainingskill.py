path = "app/src/main/kotlin/com/yourname/idlerpg/ui/screens/LoadoutScreen.kt"
with open(path, "r") as f:
    content = f.read()

# --- 1. Add SkillType import (same-package class in com.yourname.idlerpg, needs explicit import
#         here since this file lives in the ui.screens subpackage). ---
old_import = "import androidx.compose.ui.unit.dp\n"
new_import = "import androidx.compose.ui.unit.dp\nimport com.yourname.idlerpg.SkillType\n"
assert content.count(old_import) == 1, "dp import anchor not found or not unique"
content = content.replace(old_import, new_import, 1)

# --- 2. Function signature gains optional training-skill params (defaulted so the existing
#         Inventory-tab call site, which doesn't pass them, keeps compiling unchanged). ---
old_signature = '''@Composable
fun LoadoutScreen(
    state: LoadoutState,
    onBack: () -> Unit,
    onFoodSelected: (String) -> Unit,
    onPotionSelected: (String) -> Unit,
    onAutoHealChanged: (Int) -> Unit,
    onAutoFleeChanged: (Int) -> Unit,
    modifier: Modifier = Modifier
) {'''
new_signature = '''@Composable
fun LoadoutScreen(
    state: LoadoutState,
    onBack: () -> Unit,
    onFoodSelected: (String) -> Unit,
    onPotionSelected: (String) -> Unit,
    onAutoHealChanged: (Int) -> Unit,
    onAutoFleeChanged: (Int) -> Unit,
    trainingSkill: SkillType? = null,
    allowedTrainingSkills: List<SkillType> = emptyList(),
    onTrainingSkillSelected: (SkillType) -> Unit = {},
    modifier: Modifier = Modifier
) {'''
assert content.count(old_signature) == 1, "LoadoutScreen signature not found or not unique"
content = content.replace(old_signature, new_signature, 1)

# --- 3. Insert the picker between the Auto-Flee slider and the Food section. Only renders
#         when a trainingSkill is actually passed in (i.e. from the Combat tab). ---
old_section = '''        Text(text = "Auto-Flee Threshold: " + state.autoFleeThresholdPercent + "%", style = MaterialTheme.typography.titleMedium)
        Slider(
            value = state.autoFleeThresholdPercent.toFloat(),
            onValueChange = { onAutoFleeChanged(it.toInt()) },
            valueRange = 0f..100f
        )

        Spacer(modifier = Modifier.height(24.dp))

        Text(text = "Food", style = MaterialTheme.typography.titleMedium)'''
new_section = '''        Text(text = "Auto-Flee Threshold: " + state.autoFleeThresholdPercent + "%", style = MaterialTheme.typography.titleMedium)
        Slider(
            value = state.autoFleeThresholdPercent.toFloat(),
            onValueChange = { onAutoFleeChanged(it.toInt()) },
            valueRange = 0f..100f
        )

        Spacer(modifier = Modifier.height(24.dp))

        if (trainingSkill != null && allowedTrainingSkills.isNotEmpty()) {
            Text(text = "Training", style = MaterialTheme.typography.titleMedium)
            Spacer(modifier = Modifier.height(8.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                allowedTrainingSkills.forEach { skill ->
                    val selected = skill == trainingSkill
                    val background = if (selected) {
                        MaterialTheme.colorScheme.primary.copy(alpha = 0.2f)
                    } else {
                        MaterialTheme.colorScheme.surfaceVariant
                    }
                    Text(
                        text = skill.name.lowercase().replaceFirstChar { it.uppercase() },
                        style = MaterialTheme.typography.bodyMedium,
                        modifier = Modifier
                            .clip(RoundedCornerShape(10.dp))
                            .background(background)
                            .clickable { onTrainingSkillSelected(skill) }
                            .padding(horizontal = 12.dp, vertical = 8.dp)
                    )
                }
            }
            Spacer(modifier = Modifier.height(24.dp))
        }

        Text(text = "Food", style = MaterialTheme.typography.titleMedium)'''
assert content.count(old_section) == 1, "Auto-Flee/Food section not found or not unique"
content = content.replace(old_section, new_section, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: LoadoutScreen.kt patched (training-skill picker added, optional/backward-compatible).")
