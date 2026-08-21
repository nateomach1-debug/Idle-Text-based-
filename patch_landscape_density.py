"""
Patch: adds a landscape density-shrink for page content.

Adds a private adaptiveDensity() composable to MainActivity.kt that
returns a smaller Density (and slightly smaller fontScale) when the
device is in landscape orientation, unchanged in portrait. Wraps this
around ONLY the page content Box (not the SideRail), via
CompositionLocalProvider(LocalDensity provides adaptiveDensity()).

Because LocalDensity affects all .dp measurements for every composable
inside its scope, this proportionally shrinks padding, spacers, icon
sizes, and font sizes across every screen at once, from one tunable
place, without editing each screen file individually.

Tune the two multipliers below (currently 0.78 for density / 0.9 for
fontScale) if the effect feels too strong or too weak after testing.

Guarded with asserts - makes no changes if anchors aren't found exactly.
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(BASE, "MainActivity.kt")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# ---------------------------------------------------------------
# 1. Add required imports
# ---------------------------------------------------------------
old_imports = (
    "import androidx.compose.foundation.layout.padding\n"
    "import androidx.compose.ui.unit.dp\n"
)
new_imports = (
    "import androidx.compose.foundation.layout.padding\n"
    "import androidx.compose.ui.unit.dp\n"
    "import androidx.compose.ui.unit.Density\n"
    "import androidx.compose.ui.platform.LocalDensity\n"
    "import androidx.compose.ui.platform.LocalConfiguration\n"
    "import android.content.res.Configuration\n"
)
assert old_imports in content, "import anchor not found"
assert content.count(old_imports) == 1, "import anchor not unique"
content = content.replace(old_imports, new_imports)

# ---------------------------------------------------------------
# 2. Add the adaptiveDensity() helper, right before class MainActivity
# ---------------------------------------------------------------
old_class_decl = "class MainActivity : ComponentActivity() {"
new_class_decl = (
    "// Shrinks all dp-based sizing (padding, spacers, icons, fonts) proportionally\n"
    "// in landscape, unchanged in portrait. Adjust the two multipliers here to\n"
    "// retune density app-wide from one place.\n"
    "@Composable\n"
    "private fun adaptiveDensity(): Density {\n"
    "    val configuration = LocalConfiguration.current\n"
    "    val baseDensity = LocalDensity.current\n"
    "    return if (configuration.orientation == Configuration.ORIENTATION_LANDSCAPE) {\n"
    "        Density(density = baseDensity.density * 0.78f, fontScale = baseDensity.fontScale * 0.9f)\n"
    "    } else {\n"
    "        baseDensity\n"
    "    }\n"
    "}\n"
    "\n"
    "class MainActivity : ComponentActivity() {"
)
assert old_class_decl in content, "class declaration anchor not found"
assert content.count(old_class_decl) == 1, "class declaration anchor not unique"
content = content.replace(old_class_decl, new_class_decl)

# ---------------------------------------------------------------
# 3. Wrap the page content Box's OPEN with CompositionLocalProvider
#    (SideRail stays outside this scope, unaffected)
# ---------------------------------------------------------------
old_box_open = (
    "                        Box(modifier = Modifier.weight(1f)) {\n"
    "                        when (currentDestination) {"
)
new_box_open = (
    "                        CompositionLocalProvider(LocalDensity provides adaptiveDensity()) {\n"
    "                        Box(modifier = Modifier.weight(1f)) {\n"
    "                        when (currentDestination) {"
)
assert old_box_open in content, "Box open anchor not found"
assert content.count(old_box_open) == 1, "Box open anchor not unique"
content = content.replace(old_box_open, new_box_open)

# ---------------------------------------------------------------
# 4. Close the CompositionLocalProvider right after the Box's own close
#    (matched via the unique "else -> ... coming soon" fallback branch
#    that immediately precedes the when/Box/Row closing braces)
# ---------------------------------------------------------------
old_box_close = (
    "                            else -> androidx.compose.material3.Text(\n"
    "                                text = currentDestination.label + \" screen coming soon\",\n"
    "                                modifier = Modifier.fillMaxSize()\n"
    "                            )\n"
    "                        }\n"
    "                        }\n"
    "                    }\n"
    "\n"
    "                    val chatMessagesFromVm by gameViewModel.chatMessages.collectAsState()"
)
new_box_close = (
    "                            else -> androidx.compose.material3.Text(\n"
    "                                text = currentDestination.label + \" screen coming soon\",\n"
    "                                modifier = Modifier.fillMaxSize()\n"
    "                            )\n"
    "                        }\n"
    "                        }\n"
    "                        }\n"
    "                    }\n"
    "\n"
    "                    val chatMessagesFromVm by gameViewModel.chatMessages.collectAsState()"
)
assert old_box_close in content, "Box close anchor not found"
assert content.count(old_box_close) == 1, "Box close anchor not unique"
content = content.replace(old_box_close, new_box_close)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched MainActivity.kt: adaptiveDensity() added and scoped around page content.")
