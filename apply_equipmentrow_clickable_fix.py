"""
Fix: tapping an equipped item in the Equipment tab did nothing.

Root cause: EquipmentSlotRow's Row accepted an onClick parameter but never
actually applied a .clickable() modifier to the Row -- so nothing in that
composable ever triggered onSlotTapped, regardless of the backend wiring.
Equipping worked because it goes through a separate real Button on the
Inventory tab; only the Equipment tab's row itself had no tap target.

Run from repo root: python3 apply_equipmentrow_clickable_fix.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/EquipmentScreen.kt")

OLD_IMPORT = "import androidx.compose.foundation.background\nimport androidx.compose.foundation.layout.*"
NEW_IMPORT = (
    "import androidx.compose.foundation.background\n"
    "import androidx.compose.foundation.clickable\n"
    "import androidx.compose.foundation.layout.*"
)

OLD_ROW = '''    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(14.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text(text = slot.name, style = MaterialTheme.typography.labelSmall)'''

NEW_ROW = '''    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .clickable(onClick = onClick)
            .padding(14.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text(text = slot.name, style = MaterialTheme.typography.labelSmall)'''


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

    if ".clickable(onClick = onClick)" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    content = replace_once(content, OLD_IMPORT, NEW_IMPORT, "clickable import")
    content = replace_once(content, OLD_ROW, NEW_ROW, "EquipmentSlotRow Row modifier")

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
