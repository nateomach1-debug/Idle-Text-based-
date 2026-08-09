"""
Corrective fix: the previous patch (apply_layout_8_vendorrow_sizing.py)
added contentPadding to the OutlinedTextField call, but OutlinedTextField
does not have a contentPadding parameter (that's Button-only in Compose
Material3) -- causing a build failure. Removing that line; the 56dp width
already does the sizing work intended.

Run from repo root: python3 apply_layout_9_fix_textfield_padding.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/MarketScreen.kt")

OLD = '''            OutlinedTextField(
                value = quantityText,
                onValueChange = { new -> if (new.length <= 6 && new.all { it.isDigit() }) quantityText = new },
                modifier = Modifier.width(56.dp),
                singleLine = true,
                textStyle = MaterialTheme.typography.bodyMedium,
                contentPadding = PaddingValues(horizontal = 8.dp, vertical = 8.dp),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
            )'''

NEW = '''            OutlinedTextField(
                value = quantityText,
                onValueChange = { new -> if (new.length <= 6 && new.all { it.isDigit() }) quantityText = new },
                modifier = Modifier.width(56.dp),
                singleLine = true,
                textStyle = MaterialTheme.typography.bodyMedium,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
            )'''


def main() -> None:
    if not TARGET.exists():
        raise SystemExit(f"ABORT: could not find {TARGET} from the current directory. Run this from the repo root.")

    content = TARGET.read_text(encoding="utf-8")

    count = content.count(OLD)
    if count == 0:
        if NEW in content:
            raise SystemExit("ABORT: this patch looks already applied. No changes written.")
        raise SystemExit("ABORT: could not find the expected OutlinedTextField block. No changes written.")
    if count > 1:
        raise SystemExit(f"ABORT: found {count} matches, expected exactly 1. No changes written.")

    content = content.replace(OLD, NEW, 1)

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content, encoding="utf-8")
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
