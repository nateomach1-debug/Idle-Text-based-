path = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(path, "r") as f:
    content = f.read()

# --- 1. The Surface now picks its background dynamically: the active skill's color while
#         viewing that skill's detail screen, general gold tone everywhere else. This replaces
#         the old setup where the outer Surface always used the gold tone AND the skill detail
#         Box drew its own separate tint on top - two different gradients side by side was
#         exactly what caused the seam in the Skills tab. ---
old_surface = "            Surface(modifier = Modifier.fillMaxSize().appPatternBackground(), color = Color.Transparent) {"
new_surface = '''            val activeSkillId = (skillsScreenState as? SkillsScreenState.Detail)?.skillId
            val screenBackgroundModifier = if (currentDestination == AppDestination.SKILLS && activeSkillId != null) {
                Modifier.fillMaxSize().skillPatternBackground(activeSkillId)
            } else {
                Modifier.fillMaxSize().appPatternBackground()
            }
            Surface(modifier = screenBackgroundModifier, color = Color.Transparent) {'''
assert content.count(old_surface) == 1, "Surface line not found or not unique"
content = content.replace(old_surface, new_surface, 1)

# --- 2. The skill detail Box no longer needs its own separate background - the outer
#         Surface now handles it for the whole screen, rail included. ---
old_skill_box = "                                is SkillsScreenState.Detail -> allSkills[screen.skillId]?.let {\n                                    Box(modifier = Modifier.fillMaxSize().skillPatternBackground(screen.skillId)) {"
new_skill_box = "                                is SkillsScreenState.Detail -> allSkills[screen.skillId]?.let {\n                                    Box(modifier = Modifier.fillMaxSize()) {"
assert content.count(old_skill_box) == 1, "skill detail Box block not found or not unique"
content = content.replace(old_skill_box, new_skill_box, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: MainActivity.kt patched (single dynamic background covering the whole screen including the rail).")
