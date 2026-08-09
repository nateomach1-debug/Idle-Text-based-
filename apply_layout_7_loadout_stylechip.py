"""
Fix: StyleChip's Text had no overflow protection, and none of the three
chips in the Combat Style Row have weight() -- so under tight width, the
last chip measured (MAGIC) can get squeezed to almost nothing and wrap
one letter per line, same root cause as the Market tab buttons and
Inventory's Loadout button. Not adding weight(1f) here since these are
meant to stay compact pills, not stretch to fill the row -- just guarding
with maxLines/ellipsis so the worst case is a truncated label, never
vertical letter wrap.

Run from repo root: python3 apply_layout_7_loadout_stylechip.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/LoadoutScreen.kt")

OLD_IMPORT = "import androidx.compose.ui.draw.clip\nimport androidx.compose.ui.unit.dp"
NEW_IMPORT = (
    "import androidx.compose.ui.draw.clip\n"
    "import androidx.compose.ui.text.style.TextOverflow\n"
    "import androidx.compose.ui.unit.dp"
)

OLD_TEXT = '''        Text(
            text = style.name,
            style = MaterialTheme.typography.labelSmall.copy(
                color = MaterialTheme.typography.labelSmall.color.copy(alpha = contentAlpha)
            )
        )'''
NEW_TEXT = '''        Text(
            text = style.name,
            style = MaterialTheme.typography.labelSmall.copy(
                color = MaterialTheme.typography.labelSmall.color.copy(alpha = contentAlpha)
            ),
            maxLines = 1,
            softWrap = false,
            overflow = TextOverflow.Ellipsis
        )'''


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

    if "import androidx.compose.ui.text.style.TextOverflow" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    content = replace_once(content, OLD_IMPORT, NEW_IMPORT, "TextOverflow import")
    content = replace_once(content, OLD_TEXT, NEW_TEXT, "StyleChip Text")

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
