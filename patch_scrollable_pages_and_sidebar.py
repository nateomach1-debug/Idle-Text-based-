"""
Patch: adds verticalScroll to the 4 screens/components that the discovery
scan flagged as NOT already scrollable:
  - CharacterSelectScreen.kt (both CharacterSelectScreen and CharacterCreateScreen)
  - LoginScreen.kt
  - HomeScreen.kt (top-level HomeScreen Column only)
  - SideRail.kt (the rail's own Column)

Every edit is a guarded str.replace: if the expected old text isn't found
exactly, this raises an AssertionError and makes NO changes to that file,
so a failed run is safe to re-run after inspecting the error.
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"


def patch_file(filename, replacements):
    path = os.path.join(BASE, filename)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    for old, new in replacements:
        assert old in content, f"{filename}: anchor text not found:\n{old!r}"
        assert content.count(old) == 1, f"{filename}: anchor text not unique:\n{old!r}"
        content = content.replace(old, new)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Patched {filename}")


# ---------------------------------------------------------------
# CharacterSelectScreen.kt
# ---------------------------------------------------------------
patch_file(
    "CharacterSelectScreen.kt",
    [
        (
            "import androidx.compose.foundation.background\n"
            "import androidx.compose.foundation.clickable\n"
            "import androidx.compose.foundation.layout.*\n",
            "import androidx.compose.foundation.background\n"
            "import androidx.compose.foundation.clickable\n"
            "import androidx.compose.foundation.layout.*\n"
            "import androidx.compose.foundation.rememberScrollState\n"
            "import androidx.compose.foundation.verticalScroll\n",
        ),
        (
            "    Column(modifier = modifier.fillMaxSize().padding(24.dp)) {\n"
            "        Text(text = \"Select a Character\", style = MaterialTheme.typography.headlineMedium)",
            "    Column(\n"
            "        modifier = modifier\n"
            "            .fillMaxSize()\n"
            "            .verticalScroll(rememberScrollState())\n"
            "            .padding(24.dp)\n"
            "    ) {\n"
            "        Text(text = \"Select a Character\", style = MaterialTheme.typography.headlineMedium)",
        ),
        (
            "    Column(modifier = modifier.fillMaxSize().padding(24.dp)) {\n"
            "        Text(text = \"Create Your Character\", style = MaterialTheme.typography.headlineMedium)",
            "    Column(\n"
            "        modifier = modifier\n"
            "            .fillMaxSize()\n"
            "            .verticalScroll(rememberScrollState())\n"
            "            .padding(24.dp)\n"
            "    ) {\n"
            "        Text(text = \"Create Your Character\", style = MaterialTheme.typography.headlineMedium)",
        ),
    ],
)

# ---------------------------------------------------------------
# LoginScreen.kt
# ---------------------------------------------------------------
patch_file(
    "LoginScreen.kt",
    [
        (
            "import androidx.compose.foundation.layout.*\n"
            "import androidx.compose.material3.*\n",
            "import androidx.compose.foundation.layout.*\n"
            "import androidx.compose.foundation.rememberScrollState\n"
            "import androidx.compose.foundation.verticalScroll\n"
            "import androidx.compose.material3.*\n",
        ),
        (
            "    Column(\n"
            "        modifier = modifier\n"
            "            .fillMaxSize()\n"
            "            .padding(24.dp),\n"
            "        verticalArrangement = Arrangement.Center,",
            "    Column(\n"
            "        modifier = modifier\n"
            "            .fillMaxSize()\n"
            "            .verticalScroll(rememberScrollState())\n"
            "            .padding(24.dp),\n"
            "        verticalArrangement = Arrangement.Center,",
        ),
    ],
)

# ---------------------------------------------------------------
# HomeScreen.kt
# ---------------------------------------------------------------
patch_file(
    "HomeScreen.kt",
    [
        (
            "import androidx.compose.foundation.background\n"
            "import androidx.compose.foundation.layout.*\n",
            "import androidx.compose.foundation.background\n"
            "import androidx.compose.foundation.layout.*\n"
            "import androidx.compose.foundation.rememberScrollState\n"
            "import androidx.compose.foundation.verticalScroll\n",
        ),
        (
            "    Column(\n"
            "        modifier = modifier\n"
            "            .fillMaxSize()\n"
            "            .padding(20.dp)\n"
            "    ) {\n"
            "        Text(\n"
            "            text = \"Home\",",
            "    Column(\n"
            "        modifier = modifier\n"
            "            .fillMaxSize()\n"
            "            .verticalScroll(rememberScrollState())\n"
            "            .padding(20.dp)\n"
            "    ) {\n"
            "        Text(\n"
            "            text = \"Home\",",
        ),
    ],
)

# ---------------------------------------------------------------
# SideRail.kt
# ---------------------------------------------------------------
patch_file(
    "SideRail.kt",
    [
        (
            "import androidx.compose.foundation.background\n"
            "import androidx.compose.foundation.clickable\n"
            "import androidx.compose.foundation.layout.*\n",
            "import androidx.compose.foundation.background\n"
            "import androidx.compose.foundation.clickable\n"
            "import androidx.compose.foundation.layout.*\n"
            "import androidx.compose.foundation.rememberScrollState\n"
            "import androidx.compose.foundation.verticalScroll\n",
        ),
        (
            "    Column(\n"
            "        modifier = modifier\n"
            "            .fillMaxHeight()\n"
            "            .animateContentSize()\n"
            "            .width(if (expanded) 140.dp else 64.dp)\n"
            "            .padding(vertical = 12.dp),",
            "    Column(\n"
            "        modifier = modifier\n"
            "            .fillMaxHeight()\n"
            "            .verticalScroll(rememberScrollState())\n"
            "            .animateContentSize()\n"
            "            .width(if (expanded) 140.dp else 64.dp)\n"
            "            .padding(vertical = 12.dp),",
        ),
    ],
)

print("All patches applied successfully.")
