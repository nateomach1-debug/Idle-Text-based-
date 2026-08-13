path = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(path, "r") as f:
    content = f.read()

# --- 1. Add the two missing imports (background modifier + skillThemeBackground lookup). ---
old_import_anchor = "import com.yourname.idlerpg.ui.theme.IdleRpgTheme\n"
new_import_anchor = (
    "import com.yourname.idlerpg.ui.theme.IdleRpgTheme\n"
    "import com.yourname.idlerpg.ui.theme.skillThemeBackground\n"
    "import androidx.compose.foundation.background\n"
)
assert content.count(old_import_anchor) == 1, "IdleRpgTheme import anchor not found or not unique"
content = content.replace(old_import_anchor, new_import_anchor, 1)

# --- 2. Wrap the skill-detail routing in a themed Box. Combat skills fall through with
#         skillThemeBackground() returning null, so they render exactly as before. ---
old_detail_routing = '''                                is SkillsScreenState.Detail -> allSkills[screen.skillId]?.let {
                                    when (screen.skillId) {
                                        "SMITHING" -> SmithingScreen(
                                            buildSmithingState(it, inventoryQuantities),
                                            { skillsScreenState = SkillsScreenState.List },
                                            { itemId -> gameViewModel.startCraftingAction(itemId) }
                                        )
                                        in RECIPE_BASED_SKILL_LABELS -> SkillDetailScreen(
                                            buildSkillDetailState(screen.skillId, it, inventoryQuantities),
                                            { skillsScreenState = SkillsScreenState.List },
                                            { itemId -> gameViewModel.startCraftingAction(itemId) },
                                            startButtonLabel = RECIPE_BASED_SKILL_LABELS.getValue(screen.skillId)
                                        )
                                        else -> SkillDetailScreen(
                                            buildSkillDetailState(screen.skillId, it, inventoryQuantities),
                                            { skillsScreenState = SkillsScreenState.List },
                                            { actionId -> gameViewModel.startSkillAction(SkillType.valueOf(screen.skillId), actionId) }
                                        )
                                    }
                                }'''
new_detail_routing = '''                                is SkillsScreenState.Detail -> allSkills[screen.skillId]?.let {
                                    val skillBackground = skillThemeBackground(screen.skillId)
                                    val skillBoxModifier = if (skillBackground != null) {
                                        Modifier.fillMaxSize().background(skillBackground)
                                    } else {
                                        Modifier.fillMaxSize()
                                    }
                                    Box(modifier = skillBoxModifier) {
                                        when (screen.skillId) {
                                            "SMITHING" -> SmithingScreen(
                                                buildSmithingState(it, inventoryQuantities),
                                                { skillsScreenState = SkillsScreenState.List },
                                                { itemId -> gameViewModel.startCraftingAction(itemId) }
                                            )
                                            in RECIPE_BASED_SKILL_LABELS -> SkillDetailScreen(
                                                buildSkillDetailState(screen.skillId, it, inventoryQuantities),
                                                { skillsScreenState = SkillsScreenState.List },
                                                { itemId -> gameViewModel.startCraftingAction(itemId) },
                                                startButtonLabel = RECIPE_BASED_SKILL_LABELS.getValue(screen.skillId)
                                            )
                                            else -> SkillDetailScreen(
                                                buildSkillDetailState(screen.skillId, it, inventoryQuantities),
                                                { skillsScreenState = SkillsScreenState.List },
                                                { actionId -> gameViewModel.startSkillAction(SkillType.valueOf(screen.skillId), actionId) }
                                            )
                                        }
                                    }
                                }'''
assert content.count(old_detail_routing) == 1, "skill detail routing block not found or not unique"
content = content.replace(old_detail_routing, new_detail_routing, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: MainActivity.kt patched (skill detail screens wrapped in themed background).")
