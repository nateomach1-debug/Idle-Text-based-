#!/usr/bin/env python3
"""
Corrective patch #2: SmithingScreen.kt doesn't need the overrideColor
import at all (it's package com.yourname.idlerpg - the same flat package
overrideColor is declared in - confirmed via discovery). Only SideRail.kt
still needs it, since the prior run stopped before reaching it.
"""
import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(ROOT, "SideRail.kt")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

package_line = "package com.yourname.idlerpg.ui.navigation\n"
import_line = "import com.yourname.idlerpg.ui.theme.overrideColor\n"

if import_line in content:
    print("SKIP (already imported): SideRail.kt")
else:
    count = content.count(package_line)
    if count != 1:
        raise RuntimeError(f"Expected exactly 1 package line, found {count}")
    content = content.replace(package_line, package_line + "\n" + import_line)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("PATCHED: SideRail.kt")

print("Done.")
