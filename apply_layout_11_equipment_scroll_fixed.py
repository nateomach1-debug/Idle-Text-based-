"""
Corrected version of apply_layout_10_equipment_scroll.py -- the original
matched against a stale copy of this file that predated the clickable
import added by apply_equipmentrow_clickable_fix.py earlier in this
project. That script aborted safely (nothing was written) so this is
safe to run instead.

Fix: EquipSlotUi has 13 values, but the Column listing them had no
verticalScroll() modifier -- content past what fits one screen (LEGS,
SHIELD, CAPE, TOOL, RING_2, AMMO) was simply cut off with no way to
scroll to it. Adds verticalScroll(rememberScrollState()) to the outer
Column.

Run from repo root: python3 apply_layout_11_equipment_scroll_fixed.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/EquipmentScreen.kt")

OLD_IMPORT = "import androidx.compose.foundation.clickable\nimport androidx.compose.foundation.layout.*"
NEW_IMPORT = (
    "import androidx.compose.foundation.clickable\n"
    "import androidx.compose.foundation.layout.*\n"
    "import androidx.compose.foundation.rememberScrollState\n"
    "import androidx.compose.foundation.verticalScroll"
)

OLD_COLUMN = "    Column(modifier = modifier.fillMaxSize().padding(20.dp)) {"
NEW_COLUMN = "    Column(modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp)) {"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 0:
        raise SystemExit(f"ABORT: could not find expected block for '{label}'. No changes written.")
    if count > 1:
        raise SystemExit(f"ABORT: found {count} matches for '{label}', expected exactly 1. No changes written.")
    return text.replace(old, new, 1)


def main() -> None:
    if not TARGET.exists():
        raise SystemExit(f"ABORT: could not find {TARGET} from the current directory. Run this from the repo root.")

    content = TARGET.read_text()

    if "verticalScroll" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    content = replace_once(content, OLD_IMPORT, NEW_IMPORT, "scroll imports")
    content = replace_once(content, OLD_COLUMN, NEW_COLUMN, "outer Column modifier")

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
