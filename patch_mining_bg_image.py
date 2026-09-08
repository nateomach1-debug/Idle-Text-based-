#!/usr/bin/env python3
"""
Corrective patch: missing ImageBitmap import in PatternBackground.kt.
"""
import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(ROOT, "PatternBackground.kt")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "import androidx.compose.ui.graphics.ImageShader\n"
new = "import androidx.compose.ui.graphics.ImageBitmap\nimport androidx.compose.ui.graphics.ImageShader\n"

if "import androidx.compose.ui.graphics.ImageBitmap\n" in content:
    print("SKIP (already fixed)")
elif old in content:
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("PATCHED: added ImageBitmap import")
else:
    raise RuntimeError("Anchor text not found")

print("Done.")
