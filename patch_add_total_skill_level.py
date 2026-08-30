# patch_add_total_skill_level.py
path = "app/src/main/kotlin/com/yourname/idlerpg/SkillsScreen.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor = '''        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(text = "Skills", style = MaterialTheme.typography.headlineMedium)
            ViewModeToggle('''
count = content.count(anchor)
assert count == 1, f"Expected 1 match, found {count}."
replacement = '''        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(text = "Skills", style = MaterialTheme.typography.headlineMedium)
                val totalLevel = remember(allSkills) { allSkills.values.sumOf { it.level } }
                Text(
                    text = "Total level: " + totalLevel,
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            ViewModeToggle('''
content = content.replace(anchor, replacement, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("patch_add_total_skill_level.py applied cleanly.")
