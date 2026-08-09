"""
Fix: the Market tab buttons (Browse/Orders/Vendor) and the Vendor item
row's item name were wrapping character-by-character under tight width
(narrow available space after the side rail + default M3 button padding
left almost no room for text), which is what made them look like empty
oversized capsules -- they were actually rendering, just one letter per
line, stretching the button to absurd height.

This makes wrapping impossible for that text (single line, ellipsis on
overflow) so worst case is a truncated label, never vertical letter
salad, and trims the tab buttons' default horizontal content padding so
more of the tight available width goes to the label itself instead of
padding.

Run from repo root: python3 apply_layout_4_market_textwrap.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/MarketScreen.kt")

OLD_IMPORT = "import androidx.compose.ui.draw.clip\nimport androidx.compose.ui.text.input.KeyboardType"
NEW_IMPORT = (
    "import androidx.compose.ui.draw.clip\n"
    "import androidx.compose.ui.text.input.KeyboardType\n"
    "import androidx.compose.ui.text.style.TextOverflow"
)

OLD_TABBUTTON = '''    if (isSelected) {
        Button(onClick = onClick, modifier = modifier) {
            Text(text = label, style = MaterialTheme.typography.labelMedium)
        }
    } else {
        OutlinedButton(onClick = onClick, modifier = modifier) {
            Text(text = label, style = MaterialTheme.typography.labelMedium)
        }
    }'''
NEW_TABBUTTON = '''    val tabPadding = PaddingValues(horizontal = 4.dp, vertical = 8.dp)
    if (isSelected) {
        Button(onClick = onClick, modifier = modifier, contentPadding = tabPadding) {
            Text(
                text = label,
                style = MaterialTheme.typography.labelMedium,
                maxLines = 1,
                softWrap = false,
                overflow = TextOverflow.Ellipsis
            )
        }
    } else {
        OutlinedButton(onClick = onClick, modifier = modifier, contentPadding = tabPadding) {
            Text(
                text = label,
                style = MaterialTheme.typography.labelMedium,
                maxLines = 1,
                softWrap = false,
                overflow = TextOverflow.Ellipsis
            )
        }
    }'''

OLD_VENDORROW = '''        Column(modifier = Modifier.weight(1f)) {
            Text(text = item.displayName, style = MaterialTheme.typography.titleMedium)
            Text(
                text = "x" + item.quantity + " \u2014 " + item.npcValuePerUnit + " each",
                style = MaterialTheme.typography.labelSmall
            )
        }'''
NEW_VENDORROW = '''        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = item.displayName,
                style = MaterialTheme.typography.titleMedium,
                maxLines = 1,
                softWrap = false,
                overflow = TextOverflow.Ellipsis
            )
            Text(
                text = "x" + item.quantity + " \u2014 " + item.npcValuePerUnit + " each",
                style = MaterialTheme.typography.labelSmall,
                maxLines = 1,
                softWrap = false,
                overflow = TextOverflow.Ellipsis
            )
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

    if "val tabPadding" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    content = replace_once(content, OLD_IMPORT, NEW_IMPORT, "TextOverflow import")
    content = replace_once(content, OLD_TABBUTTON, NEW_TABBUTTON, "MarketTabButton")
    content = replace_once(content, OLD_VENDORROW, NEW_VENDORROW, "VendorItemRow displayName/quantity text")

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
