#!/usr/bin/env python3
"""
Corrective patch #4: GameViewModel.kt build failure.

VendorBuyCatalog / VendorBuyableItem live in MarketScreen.kt, which
declares package com.yourname.idlerpg.ui.screens (same flat-file/
different-package convention as every other *Screen.kt file) - not the
flat com.yourname.idlerpg package. Fix the import paths.
"""
import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(ROOT, "GameViewModel.kt")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = (
    "import com.yourname.idlerpg.VendorBuyCatalog\n"
    "import com.yourname.idlerpg.VendorBuyableItem\n"
)
new = (
    "import com.yourname.idlerpg.ui.screens.VendorBuyCatalog\n"
    "import com.yourname.idlerpg.ui.screens.VendorBuyableItem\n"
)

if "import com.yourname.idlerpg.ui.screens.VendorBuyCatalog" in content:
    print("SKIP (already fixed)")
elif old in content:
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("PATCHED: import paths corrected")
else:
    raise RuntimeError("Anchor text not found - imports may already differ from expected")

print("Done.")
