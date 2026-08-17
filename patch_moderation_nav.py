import re

BASE = "app/src/main/kotlin/com/yourname/idlerpg"

# ---------------------------------------------------------
# 1. NavigationDestinations.kt - add MODERATION enum entry
# ---------------------------------------------------------
nav_path = f"{BASE}/NavigationDestinations.kt"
with open(nav_path, "r") as f:
    content = f.read()

old = '    CHAT("Chat", "chat_bubble")\n}'
new = '    CHAT("Chat", "chat_bubble"),\n    MODERATION("Moderation", "shield_person")\n}'
assert old in content, f"Pattern not found in {nav_path}"
content = content.replace(old, new)
with open(nav_path, "w") as f:
    f.write(content)
print(f"Patched {nav_path}")

# ---------------------------------------------------------
# 2. SideRail.kt - icon mapping + filterable destinations param
# ---------------------------------------------------------
rail_path = f"{BASE}/SideRail.kt"
with open(rail_path, "r") as f:
    content = f.read()

old_icon = '    AppDestination.CHAT -> Icons.Filled.ChatBubble\n}'
new_icon = '    AppDestination.CHAT -> Icons.Filled.ChatBubble\n    AppDestination.MODERATION -> Icons.Filled.AdminPanelSettings\n}'
assert old_icon in content, f"Icon pattern not found in {rail_path}"
content = content.replace(old_icon, new_icon)

old_sig = (
    "fun SideRail(\n"
    "    currentDestination: AppDestination,\n"
    "    onDestinationSelected: (AppDestination) -> Unit,\n"
    "    badgedDestinations: Set<AppDestination> = emptySet(),\n"
    "    modifier: Modifier = Modifier\n"
    ")"
)
new_sig = (
    "fun SideRail(\n"
    "    currentDestination: AppDestination,\n"
    "    onDestinationSelected: (AppDestination) -> Unit,\n"
    "    badgedDestinations: Set<AppDestination> = emptySet(),\n"
    "    destinations: List<AppDestination> = AppDestination.values().toList(),\n"
    "    modifier: Modifier = Modifier\n"
    ")"
)
assert old_sig in content, f"Signature pattern not found in {rail_path}"
content = content.replace(old_sig, new_sig)

old_loop = "AppDestination.values().forEach { destination ->"
new_loop = "destinations.forEach { destination ->"
assert old_loop in content, f"Loop pattern not found in {rail_path}"
content = content.replace(old_loop, new_loop)

with open(rail_path, "w") as f:
    f.write(content)
print(f"Patched {rail_path}")

# ---------------------------------------------------------
# 3. MainActivity.kt - filter destinations by isModerator,
#    add MODERATION screen branch, call checkModeratorStatus()
# ---------------------------------------------------------
main_path = f"{BASE}/MainActivity.kt"
with open(main_path, "r") as f:
    content = f.read()

old_launch = "LaunchedEffect(Unit) { gameViewModel.loadInitialChatState() }"
new_launch = (
    "LaunchedEffect(Unit) { gameViewModel.loadInitialChatState() }\n"
    "                                LaunchedEffect(Unit) { gameViewModel.checkModeratorStatus() }"
)
assert old_launch in content, f"LaunchedEffect pattern not found in {main_path}"
content = content.replace(old_launch, new_launch, 1)

old_guild_branch_end = (
    "                            else -> androidx.compose.material3.Text(\n"
    "                                text = currentDestination.label + \" screen coming soon\",\n"
    "                                modifier = Modifier.fillMaxSize()\n"
    "                            )"
)
new_moderation_branch = (
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
    "                            }\n\n"
    + old_guild_branch_end
)
assert old_guild_branch_end in content, f"else-branch pattern not found in {main_path}"
content = content.replace(old_guild_branch_end, new_moderation_branch, 1)

with open(main_path, "w") as f:
    f.write(content)
print(f"Patched {main_path}")

print("\nAll three files patched successfully.")
print("NOTE: SideRail(...) call site in MainActivity.kt was NOT auto-patched")
print("with the destinations= filter (its exact call-site text wasn't captured")
print("in the dumps so far) - see manual step below.")
