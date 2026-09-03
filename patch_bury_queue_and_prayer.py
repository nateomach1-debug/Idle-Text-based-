PATH = "app/src/main/kotlin/com/yourname/idlerpg/SkillsScreen.kt"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

def apply(old, new, label):
    global content
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"FAILED [{label}]: expected 1 match, found {count}")
    content = content.replace(old, new, 1)

# 1. List row: add numeric XP text under the progress bar
apply(
"""        Column(modifier = Modifier.weight(1f)) {
            Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                Text(text = skill.displayName, style = MaterialTheme.typography.titleMedium)
                Text(text = "Lv. " + skill.level, style = MaterialTheme.typography.titleMedium)
            }
            Spacer(modifier = Modifier.height(6.dp))
            ThinProgressBar(progressFraction)
        }""",
"""        Column(modifier = Modifier.weight(1f)) {
            Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                Text(text = skill.displayName, style = MaterialTheme.typography.titleMedium)
                Text(text = "Lv. " + skill.level, style = MaterialTheme.typography.titleMedium)
            }
            Spacer(modifier = Modifier.height(6.dp))
            ThinProgressBar(progressFraction)
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = formatXpProgress(skill),
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.fillMaxWidth(),
                textAlign = androidx.compose.ui.text.style.TextAlign.End
            )
        }""",
    "SkillListRow numeric XP"
)

# 2. Grid tile: add a progress bar + numeric XP (it currently has neither)
apply(
"""@Composable
private fun SkillGridTile(skill: SkillSummary, onClick: () -> Unit) {
    Column(
        modifier = Modifier
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .clickable { onClick() }
            .padding(12.dp)
            .fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = skill.displayName, style = MaterialTheme.typography.labelSmall)
        Spacer(modifier = Modifier.height(4.dp))
        Text(text = "Lv. " + skill.level, style = MaterialTheme.typography.titleMedium)
    }
}""",
"""@Composable
private fun SkillGridTile(skill: SkillSummary, onClick: () -> Unit) {
    val progressFraction = skillProgressFraction(skill)
    Column(
        modifier = Modifier
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .clickable { onClick() }
            .padding(12.dp)
            .fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = skill.displayName, style = MaterialTheme.typography.labelSmall)
        Spacer(modifier = Modifier.height(4.dp))
        Text(text = "Lv. " + skill.level, style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(4.dp))
        ThinProgressBar(progressFraction)
        Spacer(modifier = Modifier.height(2.dp))
        Text(
            text = formatXpProgress(skill),
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}""",
    "SkillGridTile progress bar + numeric XP"
)

# 3. Helper to format "1,234 / 3,456 XP"
apply(
"""private fun skillProgressFraction(skill: SkillSummary): Float {
    val total = skill.currentXp + skill.xpToNextLevel
    if (total <= 0) return 0f
    return (skill.currentXp.toFloat() / total.toFloat()).coerceIn(0f, 1f)
}""",
"""private fun skillProgressFraction(skill: SkillSummary): Float {
    val total = skill.currentXp + skill.xpToNextLevel
    if (total <= 0) return 0f
    return (skill.currentXp.toFloat() / total.toFloat()).coerceIn(0f, 1f)
}

private fun formatXpProgress(skill: SkillSummary): String {
    val total = skill.currentXp + skill.xpToNextLevel
    return "%,d / %,d XP".format(skill.currentXp, total)
}""",
    "formatXpProgress helper"
)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied successfully.")
