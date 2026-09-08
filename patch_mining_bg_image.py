#!/usr/bin/env python3
"""
Corrective patch: imageResource() call-site fix in PatternBackground.kt.

imageResource is declared as an extension function on ImageBitmap.Companion,
not a free-standing top-level function - needs the ImageBitmap. receiver.
"""
import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(ROOT, "PatternBackground.kt")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "    val imageBitmap = imageResource(id = R.drawable.bg_mining_pickaxes)\n"
new = "    val imageBitmap = ImageBitmap.imageResource(id = R.drawable.bg_mining_pickaxes)\n"

if "ImageBitmap.imageResource(id = R.drawable.bg_mining_pickaxes)" in content:
    print("SKIP (already fixed)")
elif old in content:
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("PATCHED: imageResource call site")
else:
    raise RuntimeError("Anchor text not found")

print("Done.")
