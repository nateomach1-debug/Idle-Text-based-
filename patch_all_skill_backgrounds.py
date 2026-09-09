#!/usr/bin/env python3
"""
Corrective patch #3: re-apply the overrideColor import to all 7 files
that actually need it, in one script that will NOT crash partway through
(the previous attempt crashed on SmithingScreen.kt, which meant its
apply-patch job's commit+push never ran - none of the 6 successful
in-script writes before the crash were ever actually persisted).

SmithingScreen.kt is package com.yourname.idlerpg (flat) - confirmed via
discovery - so it needs NO import at all and is correctly excluded here.
"""
import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"

FILES = [
    ("CharacterSelectScreen.kt", "package com.yourname.idlerpg.ui.screens\n"),
    ("CombatViewScreen.kt", "package com.yourname.idlerpg.ui.screens\n"),
    ("LoadoutScreen.kt", "package com.yourname.idlerpg.ui.screens\n"),
    ("LoginScreen.kt", "package com.yourname.idlerpg.ui.screens\n"),
    ("SkillDetailScreen.kt", "package com.yourname.idlerpg.ui.screens\n"),
    ("SkillsScreen.kt", "package com.yourname.idlerpg.ui.screens\n"),
    ("SideRail.kt", "package com.yourname.idlerpg.ui.navigation\n"),
]

IMPORT_LINE = "import com.yourname.idlerpg.ui.theme.overrideColor\n"

for filename, package_line in FILES:
    path = os.path.join(ROOT, filename)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if IMPORT_LINE in content:
        print(f"SKIP (already imported): {filename}")
        continue

    count = content.count(package_line)
    if count != 1:
        print(f"WARNING: package line mismatch in {filename} (found {count}), skipping this file rather than crashing the whole script")
        continue

    content = content.replace(package_line, package_line + "\n" + IMPORT_LINE)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"PATCHED: {filename}")

print("\nDone (script completed without raising, so commit+push should proceed).")
