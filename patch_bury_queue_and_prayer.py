#!/usr/bin/env python3
"""
Guarded patch: Leaderboards UI (screen + nav entry + ViewModel wiring).

Each step does an exact string match and fails LOUDLY (raises) if the
anchor text isn't found or is found more than once, rather than silently
no-op'ing - per established convention, a silent skip here has caused
wasted round-trips before.

Run from repo root (same convention as prior patch scripts this project).
"""
import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def guarded_replace(path, old, new, already_applied_marker=None):
    """Replace old->new in path. Exactly one match required, unless
    already_applied_marker is present (then treat as already-patched
    and skip cleanly, for idempotent re-runs)."""
    content = read(path)
    if already_applied_marker and already_applied_marker in content:
        print(f"SKIP (already applied): {path}")
        return
    count = content.count(old)
    if count != 1:
        raise RuntimeError(
            f"Expected exactly 1 match in {path}, found {count}.\n"
            f"--- old_str ---\n{old}\n--- end ---"
        )
    write(path, content.replace(old, new))
    print(f"PATCHED: {path}")


# ---------------------------------------------------------------------
# 1. NavigationDestinations.kt - add LEADERBOARDS entry before MODERATION
# ---------------------------------------------------------------------
nav_path = os.path.join(ROOT, "NavigationDestinations.kt")
guarded_replace(
    nav_path,
    old='    GUILD("Guild", "flag"),\n    MODERATION("Moderation", "shield_person")',
    new='    GUILD("Guild", "flag"),\n    LEADERBOARDS("Leaderboards", "leaderboard"),\n    MODERATION("Moderation", "shield_person")',
    already_applied_marker='LEADERBOARDS("Leaderboards"',
)

# ---------------------------------------------------------------------
# 2. SideRail.kt - add icon mapping for LEADERBOARDS
# ---------------------------------------------------------------------
side_rail_path = os.path.join(ROOT, "SideRail.kt")
guarded_replace(
    side_rail_path,
    old="    AppDestination.GUILD -> Icons.Filled.Flag\n    AppDestination.MODERATION -> Icons.Filled.AdminPanelSettings",
    new="    AppDestination.GUILD -> Icons.Filled.Flag\n    AppDestination.LEADERBOARDS -> Icons.Filled.Leaderboard\n    AppDestination.MODERATION -> Icons.Filled.AdminPanelSettings",
    already_applied_marker="AppDestination.LEADERBOARDS -> Icons.Filled.Leaderboard",
)

# ---------------------------------------------------------------------
# 3. New file: LeaderboardModels.kt (LeaderboardCategory enum + LeaderboardRow DTO)
#    Flat package (com.yourname.idlerpg) so both GameViewModel.kt (.data)
#    and LeaderboardsScreen.kt (.ui.screens) can import it explicitly.
# ---------------------------------------------------------------------
models_path = os.path.join(ROOT, "LeaderboardModels.kt")
models_content = '''package com.yourname.idlerpg

// Unified UI-facing row that every leaderboard category maps into, so
// LeaderboardsScreen itself never needs per-category branching.
data class LeaderboardRow(
    val rank: Int,
    val name: String,
    val valueLabel: String
)

// All leaderboard categories shown in the category picker. The 16 skill
// entries deliberately match SkillType.name exactly, so category.name can
// be passed straight into fetch_skill_leaderboard without a lookup table.
enum class LeaderboardCategory(val label: String) {
    TOTAL_LEVEL("Total Level"),
    COMBAT_LEVEL("Combat Level"),
    GUILDS("Guilds"),
    MINING("Mining"),
    WOODCUTTING("Woodcutting"),
    FISHING("Fishing"),
    FARMING("Farming"),
    THIEVING("Thieving"),
    SMITHING("Smithing"),
    COOKING("Cooking"),
    CRAFTING("Crafting"),
    FLETCHING("Fletching"),
    ALCHEMY("Alchemy"),
    MAGIC("Magic"),
    ATTACK("Attack"),
    STRENGTH("Strength"),
    DEFENSE("Defense"),
    PRAYER("Prayer"),
    ARCHERY("Archery");

    val isSkillCategory: Boolean
        get() = this != TOTAL_LEVEL && this != COMBAT_LEVEL && this != GUILDS
}
'''
if os.path.exists(models_path) and "enum class LeaderboardCategory" in read(models_path):
    print(f"SKIP (already exists): {models_path}")
else:
    write(models_path, models_content)
    print(f"CREATED: {models_path}")

# ---------------------------------------------------------------------
# 4. New file: LeaderboardsScreen.kt
#    Flat file, but declares package com.yourname.idlerpg.ui.screens
#    (same established exception as GuildHomeScreen.kt/HomeScreen.kt/etc)
#    so it's automatically visible via MainActivity.kt's existing
#    `import com.yourname.idlerpg.ui.screens.*` wildcard.
# ---------------------------------------------------------------------
screen_path = os.path.join(ROOT, "LeaderboardsScreen.kt")
screen_content = '''package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.yourname.idlerpg.LeaderboardCategory
import com.yourname.idlerpg.LeaderboardRow

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LeaderboardsScreen(
    selectedCategory: LeaderboardCategory,
    rows: List<LeaderboardRow>,
    isLoading: Boolean,
    onCategorySelected: (LeaderboardCategory) -> Unit,
    modifier: Modifier = Modifier
) {
    var dropdownExpanded by remember { mutableStateOf(false) }

    Column(modifier = modifier.fillMaxSize().padding(16.dp)) {
        Text(text = "Leaderboards", style = MaterialTheme.typography.headlineSmall)
        Box(modifier = Modifier.height(12.dp))

        ExposedDropdownMenuBox(
            expanded = dropdownExpanded,
            onExpandedChange = { dropdownExpanded = it }
        ) {
            OutlinedTextField(
                value = selectedCategory.label,
                onValueChange = {},
                readOnly = true,
                label = { Text("Category") },
                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = dropdownExpanded) },
                modifier = Modifier.menuAnchor().fillMaxWidth()
            )
            androidx.compose.material3.ExposedDropdownMenu(
                expanded = dropdownExpanded,
                onDismissRequest = { dropdownExpanded = false }
            ) {
                LeaderboardCategory.values().forEach { category ->
                    DropdownMenuItem(
                        text = { Text(category.label) },
                        onClick = {
                            onCategorySelected(category)
                            dropdownExpanded = false
                        }
                    )
                }
            }
        }

        Box(modifier = Modifier.height(16.dp))

        when {
            isLoading -> Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
            rows.isEmpty() -> Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text(text = "No entries yet.", style = MaterialTheme.typography.bodyMedium)
            }
            else -> LazyColumn(modifier = Modifier.fillMaxSize()) {
                items(rows) { row ->
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(text = "#" + row.rank + "  " + row.name, style = MaterialTheme.typography.bodyLarge)
                        Text(text = row.valueLabel, style = MaterialTheme.typography.bodyMedium)
                    }
                    HorizontalDivider()
                }
            }
        }
    }
}
'''
if os.path.exists(screen_path) and "fun LeaderboardsScreen" in read(screen_path):
    print(f"SKIP (already exists): {screen_path}")
else:
    write(screen_path, screen_content)
    print(f"CREATED: {screen_path}")

# ---------------------------------------------------------------------
# 5. GameViewModel.kt - imports, StateFlows, fetchLeaderboard()
# ---------------------------------------------------------------------
gvm_path = os.path.join(ROOT, "GameViewModel.kt")
gvm_content = read(gvm_path)

# 5a. Explicit imports (harmless even if a wildcard import already covers
# these - Kotlin allows redundant imports without error).
if "import com.yourname.idlerpg.LeaderboardCategory" not in gvm_content:
    guarded_replace(
        gvm_path,
        old="package com.yourname.idlerpg.data\n",
        new=(
            "package com.yourname.idlerpg.data\n\n"
            "import com.yourname.idlerpg.LeaderboardCategory\n"
            "import com.yourname.idlerpg.LeaderboardRow\n"
            "import com.yourname.idlerpg.SupabaseLeaderboardRepository\n"
        ),
        already_applied_marker="import com.yourname.idlerpg.LeaderboardCategory",
    )
else:
    print(f"SKIP (imports already present): {gvm_path}")

# 5b. StateFlows + fetchLeaderboard(), inserted right after the existing
# guildLeaderboard StateFlow declaration (same section, same pattern).
guarded_replace(
    gvm_path,
    old=(
        "    private val _guildLeaderboard = MutableStateFlow<List<GuildLeaderboardEntry>>(emptyList())\n"
        "    val guildLeaderboard: StateFlow<List<GuildLeaderboardEntry>> = _guildLeaderboard.asStateFlow()\n"
    ),
    new=(
        "    private val _guildLeaderboard = MutableStateFlow<List<GuildLeaderboardEntry>>(emptyList())\n"
        "    val guildLeaderboard: StateFlow<List<GuildLeaderboardEntry>> = _guildLeaderboard.asStateFlow()\n"
        "\n"
        "    private val _leaderboardRows = MutableStateFlow<List<LeaderboardRow>>(emptyList())\n"
        "    val leaderboardRows: StateFlow<List<LeaderboardRow>> = _leaderboardRows.asStateFlow()\n"
        "\n"
        "    private val _leaderboardLoading = MutableStateFlow(false)\n"
        "    val leaderboardLoading: StateFlow<Boolean> = _leaderboardLoading.asStateFlow()\n"
        "\n"
        "    private val _selectedLeaderboardCategory = MutableStateFlow(LeaderboardCategory.TOTAL_LEVEL)\n"
        "    val selectedLeaderboardCategory: StateFlow<LeaderboardCategory> = _selectedLeaderboardCategory.asStateFlow()\n"
        "\n"
        "    fun fetchLeaderboard(category: LeaderboardCategory) {\n"
        "        _selectedLeaderboardCategory.value = category\n"
        "        viewModelScope.launch {\n"
        "            _leaderboardLoading.value = true\n"
        "            val rows: List<LeaderboardRow> = when (category) {\n"
        "                LeaderboardCategory.TOTAL_LEVEL -> SupabaseLeaderboardRepository.fetchTotalLevelLeaderboard()\n"
        "                    .getOrDefault(emptyList())\n"
        "                    .mapIndexed { index, entry ->\n"
        "                        LeaderboardRow(rank = index + 1, name = entry.displayName, valueLabel = \"Lv \" + entry.totalLevel)\n"
        "                    }\n"
        "                LeaderboardCategory.COMBAT_LEVEL -> SupabaseLeaderboardRepository.fetchCombatLevelLeaderboard()\n"
        "                    .getOrDefault(emptyList())\n"
        "                    .mapIndexed { index, entry ->\n"
        "                        LeaderboardRow(rank = index + 1, name = entry.displayName, valueLabel = \"Lv \" + entry.combatLevel)\n"
        "                    }\n"
        "                LeaderboardCategory.GUILDS -> SupabaseLeaderboardRepository.fetchGuildLeaderboard()\n"
        "                    .getOrDefault(emptyList())\n"
        "                    .mapIndexed { index, entry ->\n"
        "                        LeaderboardRow(rank = index + 1, name = entry.guildName, valueLabel = \"Lv \" + entry.guildLevel + \" \\u00b7 \" + entry.guildCoins + \" coins\")\n"
        "                    }\n"
        "                else -> SupabaseLeaderboardRepository.fetchSkillLeaderboard(category.name)\n"
        "                    .getOrDefault(emptyList())\n"
        "                    .mapIndexed { index, entry ->\n"
        "                        LeaderboardRow(rank = index + 1, name = entry.displayName, valueLabel = \"Lv \" + entry.level)\n"
        "                    }\n"
        "            }\n"
        "            _leaderboardRows.value = rows\n"
        "            _leaderboardLoading.value = false\n"
        "        }\n"
        "    }\n"
    ),
    already_applied_marker="fun fetchLeaderboard(category: LeaderboardCategory)",
)

# ---------------------------------------------------------------------
# 6. MainActivity.kt - new when-branch for AppDestination.LEADERBOARDS,
#    inserted between the MODERATION branch and the `else ->` fallback.
# ---------------------------------------------------------------------
main_activity_path = os.path.join(ROOT, "MainActivity.kt")
guarded_replace(
    main_activity_path,
    old=(
        "                            AppDestination.MODERATION -> {\n"
        "                                val moderation by gameViewModel.moderationState.collectAsState()\n"
        "                                LaunchedEffect(Unit) { gameViewModel.refreshModeration() }\n"
        "                                ModerationScreen(\n"
        "                                    state = moderation,\n"
        "                                    onResolveReport = { id, action -> gameViewModel.resolveReport(id, action) },\n"
        "                                    onResolveAppeal = { id, grant, notes -> gameViewModel.resolveAppeal(id, grant, notes) },\n"
        "                                    onMuteCharacter = { id, dur, reason -> gameViewModel.muteCharacterAsModerator(id, dur, reason) },\n"
        "                                    onUnmuteCharacter = { id -> gameViewModel.unmuteCharacterAsModerator(id) }\n"
        "                                )\n"
        "                            }\n"
        "\n"
        "                            else -> androidx.compose.material3.Text(\n"
    ),
    new=(
        "                            AppDestination.MODERATION -> {\n"
        "                                val moderation by gameViewModel.moderationState.collectAsState()\n"
        "                                LaunchedEffect(Unit) { gameViewModel.refreshModeration() }\n"
        "                                ModerationScreen(\n"
        "                                    state = moderation,\n"
        "                                    onResolveReport = { id, action -> gameViewModel.resolveReport(id, action) },\n"
        "                                    onResolveAppeal = { id, grant, notes -> gameViewModel.resolveAppeal(id, grant, notes) },\n"
        "                                    onMuteCharacter = { id, dur, reason -> gameViewModel.muteCharacterAsModerator(id, dur, reason) },\n"
        "                                    onUnmuteCharacter = { id -> gameViewModel.unmuteCharacterAsModerator(id) }\n"
        "                                )\n"
        "                            }\n"
        "\n"
        "                            AppDestination.LEADERBOARDS -> {\n"
        "                                val leaderboardRows by gameViewModel.leaderboardRows.collectAsState()\n"
        "                                val leaderboardLoading by gameViewModel.leaderboardLoading.collectAsState()\n"
        "                                val selectedLeaderboardCategory by gameViewModel.selectedLeaderboardCategory.collectAsState()\n"
        "                                LaunchedEffect(Unit) { gameViewModel.fetchLeaderboard(selectedLeaderboardCategory) }\n"
        "                                LeaderboardsScreen(\n"
        "                                    selectedCategory = selectedLeaderboardCategory,\n"
        "                                    rows = leaderboardRows,\n"
        "                                    isLoading = leaderboardLoading,\n"
        "                                    onCategorySelected = { gameViewModel.fetchLeaderboard(it) }\n"
        "                                )\n"
        "                            }\n"
        "\n"
        "                            else -> androidx.compose.material3.Text(\n"
    ),
    already_applied_marker="AppDestination.LEADERBOARDS -> {\n                                val leaderboardRows",
)

print("\nAll Leaderboards UI patches applied successfully.")
