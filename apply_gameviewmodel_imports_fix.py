path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(path, "r") as f:
    content = f.read()

old_import = "import com.yourname.idlerpg.ui.screens.SkillSummary\n"
new_import = (
    "import com.yourname.idlerpg.ui.screens.SkillSummary\n"
    "import com.yourname.idlerpg.ui.screens.CombatViewData\n"
    "import com.yourname.idlerpg.ui.screens.CombatViewState\n"
    "import com.yourname.idlerpg.ui.screens.CombatLogEntry\n"
    "import com.yourname.idlerpg.ui.screens.ZoneSummary\n"
)
assert content.count(old_import) == 1, "SkillSummary import anchor not found or not unique"
content = content.replace(old_import, new_import, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: missing ui.screens imports added to GameViewModel.kt.")
