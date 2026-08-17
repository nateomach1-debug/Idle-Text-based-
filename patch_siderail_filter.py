path = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(path, "r") as f:
    content = f.read()

old = (
    "                        SideRail(\n"
    "                            currentDestination = currentDestination,\n"
    "                            onDestinationSelected = {\n"
)
new = (
    "                        val isModerator by gameViewModel.isModerator.collectAsState()\n"
    "                        SideRail(\n"
    "                            currentDestination = currentDestination,\n"
    "                            destinations = AppDestination.values().filter { it != AppDestination.MODERATION || isModerator },\n"
    "                            onDestinationSelected = {\n"
)

assert old in content, "Pattern not found - call site text may differ from what was dumped"
count = content.count(old)
assert count == 1, f"Expected exactly 1 match, found {count}"

content = content.replace(old, new)
with open(path, "w") as f:
    f.write(content)

print(f"Patched {path}")
