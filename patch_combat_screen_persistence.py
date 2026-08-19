path = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(path, "r") as f:
    content = f.read()

# 1. Stop force-resetting combatScreenState on every nav tap (item 3: return to
#    current battle). Skills/inventory/market resets stay as-is - only combat
#    needs to remember where it was, since a session can genuinely still be
#    running in the background.
old_reset = (
    "                            onDestinationSelected = {\n"
    "                                currentDestination = it\n"
    "                                skillsScreenState = SkillsScreenState.List\n"
    "                                combatScreenState = CombatScreenState.ZoneSelect\n"
    "                                inventoryScreenState = InventoryScreenState.Items\n"
    "                                marketTab = MarketTab.BROWSE\n"
    "                                selectedMarketItemId = null\n"
    "                            },\n"
)
new_reset = (
    "                            onDestinationSelected = {\n"
    "                                currentDestination = it\n"
    "                                skillsScreenState = SkillsScreenState.List\n"
    "                                // combatScreenState intentionally NOT reset here - if a\n"
    "                                // battle is still running in the background, navigating\n"
    "                                // away and back should return to it, not zone-select.\n"
    "                                inventoryScreenState = InventoryScreenState.Items\n"
    "                                marketTab = MarketTab.BROWSE\n"
    "                                selectedMarketItemId = null\n"
    "                            },\n"
)
assert old_reset in content, "onDestinationSelected reset block not found"
assert content.count(old_reset) == 1, "onDestinationSelected pattern not unique"
content = content.replace(old_reset, new_reset)

# 2. Self-correct combatScreenState after rotation (item 7). Rotation recreates
#    the Activity, wiping local `remember` state back to its ZoneSelect default -
#    but combatViewData lives in the ViewModel and survives rotation intact, so
#    use it as the source of truth to re-sync the UI state on every recomposition.
old_combat_view_data = "    val combatViewData by gameViewModel.combatViewData.collectAsState()\n"
new_combat_view_data = (
    "    val combatViewData by gameViewModel.combatViewData.collectAsState()\n\n"
    "    // Survives rotation: if the ViewModel still has an active combat session\n"
    "    // but the local UI state reset back to ZoneSelect (e.g. after an\n"
    "    // orientation change recreated the Activity), snap back to InZone.\n"
    "    LaunchedEffect(combatViewData) {\n"
    "        if (combatViewData != null && combatScreenState == CombatScreenState.ZoneSelect) {\n"
    "            combatScreenState = CombatScreenState.InZone\n"
    "        }\n"
    "    }\n"
)
assert old_combat_view_data in content, "combatViewData declaration not found"
assert content.count(old_combat_view_data) == 1, "combatViewData pattern not unique"
content = content.replace(old_combat_view_data, new_combat_view_data)

with open(path, "w") as f:
    f.write(content)

print("Patched MainActivity.kt: combatScreenState no longer resets on nav tap,")
print("and now self-corrects to InZone after rotation if a session is active.")
