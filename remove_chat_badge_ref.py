path = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(path, "r") as f:
    content = f.read()

old = "badgedDestinations = setOf(AppDestination.CHAT, AppDestination.GUILD)"
new = "badgedDestinations = setOf(AppDestination.GUILD)"

assert old in content, "Pattern not found - badgedDestinations line may differ from what was dumped"
count = content.count(old)
assert count == 1, f"Expected exactly 1 match, found {count}"

content = content.replace(old, new)
with open(path, "w") as f:
    f.write(content)

print(f"Patched {path}")
