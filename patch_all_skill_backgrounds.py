#!/usr/bin/env python3
"""
Corrective patch: add the missing overrideColor import to every file
where it was used but not imported.
"""
import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"

# (filename, package declaration line) - screens are ui.screens, SideRail is ui.navigation
FILES = [
    ("CharacterSelectScreen.kt", "package com.yourname.idlerpg.ui.screens\n"),
    ("CombatViewScreen.kt", "package com.yourname.idlerpg.ui.screens\n"),
    ("LoadoutScreen.kt", "package com.yourname.idlerpg.ui.screens\n"),
    ("LoginScreen.kt", "package com.yourname.idlerpg.ui.screens\n"),
    ("SkillDetailScreen.kt", "package com.yourname.idlerpg.ui.screens\n"),
    ("SkillsScreen.kt", "package com.yourname.idlerpg.ui.screens\n"),
    ("SmithingScreen.kt", "package com.yourname.idlerpg.ui.screens\n"),
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

    if package_line not in content:
        raise RuntimeError(f"Package line not found in {filename} - expected: {package_line.strip()}")

    count = content.count(package_line)
    if count != 1:
        raise RuntimeError(f"Expected exactly 1 package line in {filename}, found {count}")

    content = content.replace(package_line, package_line + "\n" + IMPORT_LINE)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"PATCHED: {filename}")

print("\nDone.")
