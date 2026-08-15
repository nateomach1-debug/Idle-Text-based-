path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(path, "r") as f:
    content = f.read()

old_import = "import com.yourname.idlerpg.ui.screens.ZoneSummary\n"
new_import = (
    "import com.yourname.idlerpg.ui.screens.ZoneSummary\n"
    "import com.yourname.idlerpg.ui.screens.GuildHomeState\n"
    "import com.yourname.idlerpg.ui.screens.GuildLeaderboardEntry\n"
)
assert content.count(old_import) == 1, "ZoneSummary import anchor not found or not unique"
content = content.replace(old_import, new_import, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: GameViewModel.kt patched (added missing GuildHomeState/GuildLeaderboardEntry imports).")
