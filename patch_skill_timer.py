HOME_SCREEN = "app/src/main/kotlin/com/yourname/idlerpg/HomeScreen.kt"
SKILL_DETAIL_SCREEN = "app/src/main/kotlin/com/yourname/idlerpg/SkillDetailScreen.kt"
MAIN_ACTIVITY = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"


def patch_home_screen():
    with open(HOME_SCREEN, "r", encoding="utf-8") as fh:
        content = fh.read()
    before = content.count("{") - content.count("}")

    old = "private fun CycleCountdown(queue: ActiveQueueInfo) {"
    new = "fun CycleCountdown(queue: ActiveQueueInfo) {"
    assert content.count(old) == 1, f"expected 1, found {content.count(old)}"
    content = content.replace(old, new)

    after = content.count("{") - content.count("}")
    assert before == after, f"brace balance changed: {before} -> {after}"

    with open(HOME_SCREEN, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Patched {HOME_SCREEN} (brace balance unchanged: {before})")


def patch_skill_detail_screen():
    with open(SKILL_DETAIL_SCREEN, "r", encoding="utf-8") as fh:
        content = fh.read()
    before = content.count("{") - content.count("}")

    # 1. Import
    old1 = '''import androidx.compose.ui.unit.dp

// =========================================================
// SKILL DETAIL SCREEN'''
    assert content.count(old1) == 1, f"1: expected 1, found {content.count(old1)}"
    new1 = '''import androidx.compose.ui.unit.dp
import com.yourname.idlerpg.data.ActiveQueueInfo

// =========================================================
// SKILL DETAIL SCREEN'''
    content = content.replace(old1, new1)

    # 2. New param (defaults to null so any other/future callers keep compiling)
    old2 = '''fun SkillDetailScreen(
    state: SkillDetailState,
    onBack: () -> Unit,
    onStartAction: (String) -> Unit,
    modifier: Modifier = Modifier,
    startButtonLabel: String = "Start " + state.displayName
) {'''
    assert content.count(old2) == 1, f"2: expected 1, found {content.count(old2)}"
    new2 = '''fun SkillDetailScreen(
    state: SkillDetailState,
    onBack: () -> Unit,
    onStartAction: (String) -> Unit,
    modifier: Modifier = Modifier,
    startButtonLabel: String = "Start " + state.displayName,
    activeQueue: ActiveQueueInfo? = null
) {'''
    content = content.replace(old2, new2)

    # 3. Render the timer under the title, matching HomeScreen's own spacing convention
    old3 = '''            Text(text = state.displayName, style = MaterialTheme.typography.headlineMedium)
        }

        Spacer(modifier = Modifier.height(20.dp))'''
    assert content.count(old3) == 1, f"3: expected 1, found {content.count(old3)}"
    new3 = '''            Text(text = state.displayName, style = MaterialTheme.typography.headlineMedium)
        }

        activeQueue?.let {
            Spacer(modifier = Modifier.height(8.dp))
            CycleCountdown(queue = it)
        }

        Spacer(modifier = Modifier.height(20.dp))'''
    content = content.replace(old3, new3)

    after = content.count("{") - content.count("}")
    assert before == after, f"brace balance changed: {before} -> {after}"

    with open(SKILL_DETAIL_SCREEN, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Patched {SKILL_DETAIL_SCREEN} (brace balance unchanged: {before})")


def patch_main_activity():
    with open(MAIN_ACTIVITY, "r", encoding="utf-8") as fh:
        content = fh.read()
    before = content.count("{") - content.count("}")

    old1 = '''                                            in RECIPE_BASED_SKILL_LABELS -> SkillDetailScreen(
                                                buildSkillDetailState(screen.skillId, it, inventoryQuantities),
                                                { skillsScreenState = SkillsScreenState.List },
                                                { itemId -> gameViewModel.startCraftingAction(itemId) },
                                                startButtonLabel = RECIPE_BASED_SKILL_LABELS.getValue(screen.skillId)
                                            )'''
    assert content.count(old1) == 1, f"1: expected 1, found {content.count(old1)}"
    new1 = '''                                            in RECIPE_BASED_SKILL_LABELS -> SkillDetailScreen(
                                                buildSkillDetailState(screen.skillId, it, inventoryQuantities),
                                                { skillsScreenState = SkillsScreenState.List },
                                                { itemId -> gameViewModel.startCraftingAction(itemId) },
                                                startButtonLabel = RECIPE_BASED_SKILL_LABELS.getValue(screen.skillId),
                                                activeQueue = activeQueue
                                            )'''
    content = content.replace(old1, new1)

    old2 = '''                                            else -> SkillDetailScreen(
                                                buildSkillDetailState(screen.skillId, it, inventoryQuantities),
                                                { skillsScreenState = SkillsScreenState.List },
                                                { actionId -> gameViewModel.startSkillAction(SkillType.valueOf(screen.skillId), actionId) }
                                            )'''
    assert content.count(old2) == 1, f"2: expected 1, found {content.count(old2)}"
    new2 = '''                                            else -> SkillDetailScreen(
                                                buildSkillDetailState(screen.skillId, it, inventoryQuantities),
                                                { skillsScreenState = SkillsScreenState.List },
                                                { actionId -> gameViewModel.startSkillAction(SkillType.valueOf(screen.skillId), actionId) },
                                                activeQueue = activeQueue
                                            )'''
    content = content.replace(old2, new2)

    after = content.count("{") - content.count("}")
    assert before == after, f"brace balance changed: {before} -> {after}"

    with open(MAIN_ACTIVITY, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Patched {MAIN_ACTIVITY} (brace balance unchanged: {before})")


if __name__ == "__main__":
    patch_home_screen()
    patch_skill_detail_screen()
    patch_main_activity()
    print("Done.")
