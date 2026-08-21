"""
Follow-up patch: MainActivity.kt is currently in a partially-patched state
(a prior run applied the imports, adaptiveDensity() helper, and the
CompositionLocalProvider open-wrap around the page content Box, but hit
an assert failure before adding the matching closing brace - this is
why the build failed with a brace-mismatch-style error).

This patch ONLY adds the missing closing brace, using exact anchor text
confirmed from a fresh dump. Guarded with asserts - makes no changes if
the anchor isn't found exactly, or if it looks like this was already fixed.
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(BASE, "MainActivity.kt")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old_close = (
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
new_close = (
    "                            else -> androidx.compose.material3.Text(\n"
    "                                text = currentDestination.label + \" screen coming soon\",\n"
    "                                modifier = Modifier.fillMaxSize()\n"
    "                            )\n"
    "                        }\n"
    "                        }\n"
    "                        }\n"
    "                        }\n"
    "                    }\n"
    "\n"
    "                    val chatMessagesFromVm by gameViewModel.chatMessages.collectAsState()"
)

assert old_close in content, "close anchor not found - may already be fixed, or file state differs from expected"
assert content.count(old_close) == 1, "close anchor not unique"
content = content.replace(old_close, new_close)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched MainActivity.kt: added the missing CompositionLocalProvider closing brace.")
