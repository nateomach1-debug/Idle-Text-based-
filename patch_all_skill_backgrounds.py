#!/usr/bin/env python3
"""
Corrective patch #4: SmithingScreen.kt also needs the overrideColor
import - my earlier assumption that its flat package matched Theme.kt's
package was wrong. overrideColor lives in com.yourname.idlerpg.ui.theme,
a different package from SmithingScreen.kt's com.yourname.idlerpg.
"""
import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(ROOT, "SmithingScreen.kt")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

package_line = "package com.yourname.idlerpg\n"
import_line = "import com.yourname.idlerpg.ui.theme.overrideColor\n"

if import_line in content:
    print("SKIP (already imported): SmithingScreen.kt")
else:
    count = content.count(package_line)
    if count != 1:
        raise RuntimeError(f"Expected exactly 1 package line, found {count}")
    content = content.replace(package_line, package_line + "\n" + import_line)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("PATCHED: SmithingScreen.kt")

print("Done.")
