"""
Fix: neither the Equipment nor Loadout button had weight(1f), so in a
constrained Row, Equipment (measured first) claimed its full intrinsic
width and Loadout (measured second) was left with almost nothing --
forcing its text to wrap one letter per line and the button to stretch
into an oversized capsule. Splitting the Row evenly with weight(1f) on
both, plus forcing single-line/ellipsis text as a guard against this
happening again under tight width.

Run from repo root: python3 apply_layout_5_inventory_buttons.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/InventoryScreen.kt")

OLD_IMPORT = "import androidx.compose.ui.draw.clip\nimport androidx.compose.ui.platform.LocalContext"
NEW_IMPORT = (
    "import androidx.compose.ui.draw.clip\n"
    "import androidx.compose.ui.platform.LocalContext\n"
    "import androidx.compose.ui.text.style.TextOverflow"
)

OLD_ROW = '''        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedButton(onClick = onOpenEquipment) { Text(text = "Equipment") }
            OutlinedButton(onClick = onOpenLoadout) { Text(text = "Loadout") }
        }'''
NEW_ROW = '''        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedButton(onClick = onOpenEquipment, modifier = Modifier.weight(1f)) {
                Text(text = "Equipment", maxLines = 1, softWrap = false, overflow = TextOverflow.Ellipsis)
            }
            OutlinedButton(onClick = onOpenLoadout, modifier = Modifier.weight(1f)) {
                Text(text = "Loadout", maxLines = 1, softWrap = false, overflow = TextOverflow.Ellipsis)
            }
        }'''


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

    if "Modifier.weight(1f)) {\n                Text(text = \"Equipment\"" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    content = replace_once(content, OLD_IMPORT, NEW_IMPORT, "TextOverflow import")
    content = replace_once(content, OLD_ROW, NEW_ROW, "Equipment/Loadout button row")

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
