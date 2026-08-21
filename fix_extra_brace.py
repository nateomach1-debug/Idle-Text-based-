"""
Fix: MainActivity.kt currently has ONE EXTRA closing brace at the point
where `when(currentDestination)`, the content Box, and the
CompositionLocalProvider all need to close - there are 4 closing braces
at that indent level where only 3 are needed, which prematurely closes
an outer scope and causes the "Expecting a top level declaration" EOF
error seen in the failed build.

This removes exactly one of the four braces, using anchor text confirmed
from a fresh dump. Guarded with asserts.
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(BASE, "MainActivity.kt")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old_block = (
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
new_block = (
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

assert old_block in content, "expected 4-brace block not found - file state may differ from expected"
assert content.count(old_block) == 1, "anchor not unique"
content = content.replace(old_block, new_block)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched MainActivity.kt: removed the one extra closing brace.")
