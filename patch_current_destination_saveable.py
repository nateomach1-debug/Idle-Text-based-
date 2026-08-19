path = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(path, "r") as f:
    content = f.read()

# 1. Make sure rememberSaveable is imported.
if "import androidx.compose.runtime.saveable.rememberSaveable" not in content:
    anchor = "import androidx.compose.runtime.*\n"
    assert anchor in content, "Could not find an anchor import line to insert rememberSaveable import near"
    content = content.replace(
        anchor,
        anchor + "import androidx.compose.runtime.saveable.rememberSaveable\n",
        1
    )

# 2. currentDestination: plain enum, safe to switch to rememberSaveable directly -
#    this is the actual cause of "rotation defaults back to Home", since it was
#    reset to HOME on every Activity recreation before combatScreenState ever
#    got a chance to matter.
old = "    var currentDestination by remember { mutableStateOf(AppDestination.HOME) }\n"
new = "    var currentDestination by rememberSaveable { mutableStateOf(AppDestination.HOME) }\n"
assert old in content, "currentDestination declaration not found"
assert content.count(old) == 1, "currentDestination pattern not unique"
content = content.replace(old, new)

with open(path, "w") as f:
    f.write(content)

print("Patched: currentDestination now survives rotation via rememberSaveable.")
print("Combined with the earlier combatScreenState self-correction, rotating on")
print("the combat screen should now stay on Combat instead of bouncing to Home.")
