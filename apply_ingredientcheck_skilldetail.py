#!/usr/bin/env python3
"""
Ingredient-check patch, part 1: SkillDetailScreen.kt

- SkillActionSummary gains `missingIngredients: List<MissingIngredientSummary>`
  (defaults to empty, so gathering skills that don't pass it are unaffected).
- New MissingIngredientSummary + MissingIngredientsDialog (public, so
  SmithingScreen.kt can reuse the dialog too).
- The inline action Row in ActionPickerSheet becomes its own ActionRow
  composable: grayed out when missingIngredients isn't empty, and tapping
  it opens the missing-ingredients popup instead of starting the action.

Run from repo root:
    python3 apply_ingredientcheck_skilldetail.py
"""
import sys
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/SkillDetailScreen.kt")


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
        fail("MissingIngredientSummary already present -- patch may already be applied")

    # 1. SkillActionSummary gains missingIngredients; add MissingIngredientSummary above it
    text = replace_once(
        text,
        'data class SkillActionSummary(val actionId: String, val displayName: String, val levelRequired: Int)\n',
        (
            'data class MissingIngredientSummary(val displayName: String, val required: Int, val have: Int)\n\n'
            'data class SkillActionSummary(\n'
            '    val actionId: String,\n'
            '    val displayName: String,\n'
            '    val levelRequired: Int,\n'
            '    val missingIngredients: List<MissingIngredientSummary> = emptyList()\n'
            ')\n'
        ),
        "SkillActionSummary declaration",
    )

    # 2. Replace the inline Row in ActionPickerSheet's LazyColumn with a call to ActionRow
    text = replace_once(
        text,
        (
            "                LazyColumn(modifier = Modifier.heightIn(max = 300.dp)) {\n"
            "                    items(actions) { action ->\n"
            "                        Row(\n"
            "                            modifier = Modifier\n"
            "                                .fillMaxWidth()\n"
            "                                .clip(RoundedCornerShape(10.dp))\n"
            "                                .clickable { onActionSelected(action.actionId) }\n"
            "                                .padding(vertical = 12.dp, horizontal = 8.dp),\n"
            "                            horizontalArrangement = Arrangement.SpaceBetween\n"
            "                        ) {\n"
            "                            Text(text = action.displayName, style = MaterialTheme.typography.bodyMedium)\n"
            "                            Text(text = \"Lv. \" + action.levelRequired, style = MaterialTheme.typography.labelSmall)\n"
            "                        }\n"
            "                    }\n"
            "                }\n"
        ),
        (
            "                LazyColumn(modifier = Modifier.heightIn(max = 300.dp)) {\n"
            "                    items(actions) { action ->\n"
            "                        ActionRow(action = action, onActionSelected = onActionSelected)\n"
            "                    }\n"
            "                }\n"
        ),
        "ActionPickerSheet LazyColumn body",
    )

    # 3. Insert ActionRow + MissingIngredientsDialog composables right after ActionPickerSheet's
    #    closing brace (before ThinProgressBarPublic)
    text = replace_once(
        text,
        (
            "@Composable\n"
            "private fun ThinProgressBarPublic(fraction: Float) {\n"
        ),
        (
            "@Composable\n"
            "private fun ActionRow(action: SkillActionSummary, onActionSelected: (String) -> Unit) {\n"
            "    var showMissingDialog by remember { mutableStateOf(false) }\n"
            "    val affordable = action.missingIngredients.isEmpty()\n"
            "    val contentColor = if (affordable) {\n"
            "        MaterialTheme.colorScheme.onSurface\n"
            "    } else {\n"
            "        MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f)\n"
            "    }\n\n"
            "    Row(\n"
            "        modifier = Modifier\n"
            "            .fillMaxWidth()\n"
            "            .clip(RoundedCornerShape(10.dp))\n"
            "            .clickable {\n"
            "                if (affordable) onActionSelected(action.actionId) else showMissingDialog = true\n"
            "            }\n"
            "            .padding(vertical = 12.dp, horizontal = 8.dp),\n"
            "        horizontalArrangement = Arrangement.SpaceBetween\n"
            "    ) {\n"
            "        Text(text = action.displayName, style = MaterialTheme.typography.bodyMedium, color = contentColor)\n"
            "        Text(text = \"Lv. \" + action.levelRequired, style = MaterialTheme.typography.labelSmall, color = contentColor)\n"
            "    }\n\n"
            "    if (showMissingDialog) {\n"
            "        MissingIngredientsDialog(\n"
            "            itemName = action.displayName,\n"
            "            missing = action.missingIngredients,\n"
            "            onDismiss = { showMissingDialog = false }\n"
            "        )\n"
            "    }\n"
            "}\n\n"
            "@Composable\n"
            "fun MissingIngredientsDialog(\n"
            "    itemName: String,\n"
            "    missing: List<MissingIngredientSummary>,\n"
            "    onDismiss: () -> Unit\n"
            ") {\n"
            "    AlertDialog(\n"
            "        onDismissRequest = onDismiss,\n"
            "        title = { Text(text = \"Missing materials\", style = MaterialTheme.typography.titleMedium) },\n"
            "        text = {\n"
            "            Column {\n"
            "                Text(\n"
            "                    text = \"You need the following to craft \" + itemName + \":\",\n"
            "                    style = MaterialTheme.typography.bodyMedium\n"
            "                )\n"
            "                Spacer(modifier = Modifier.height(8.dp))\n"
            "                missing.forEach {\n"
            "                    Text(\n"
            "                        text = \"\\u2022 \" + it.displayName + \": have \" + it.have + \" / need \" + it.required,\n"
            "                        style = MaterialTheme.typography.bodyMedium\n"
            "                    )\n"
            "                }\n"
            "            }\n"
            "        },\n"
            "        confirmButton = {\n"
            "            TextButton(onClick = onDismiss) {\n"
            "                Text(text = \"OK\")\n"
            "            }\n"
            "        }\n"
            "    )\n"
            "}\n\n"
            "@Composable\n"
            "private fun ThinProgressBarPublic(fraction: Float) {\n"
        ),
        "insertion point before ThinProgressBarPublic",
    )

    if text == original:
        fail("no changes were made -- aborting")

    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
