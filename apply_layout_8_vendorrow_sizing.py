"""
Fix: the quantity input box was sized too wide (80dp with default M3
OutlinedTextField padding, rendering as a large square), and the "Sell"
button had no overflow protection so its text could still wrap to two
lines ("Sel/l") under any residual width pressure. Shrinking the box to
56dp and forcing the Sell button's text to a single line with tighter
content padding.

Run from repo root: python3 apply_layout_8_vendorrow_sizing.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/MarketScreen.kt")

OLD = '''            OutlinedTextField(
                value = quantityText,
                onValueChange = { new -> if (new.length <= 6 && new.all { it.isDigit() }) quantityText = new },
                modifier = Modifier.width(80.dp),
                singleLine = true,
                textStyle = MaterialTheme.typography.bodyMedium,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
            )
            Button(
                onClick = { enteredQuantity?.let { onSell(item.itemId, it) } },
                enabled = isValidQuantity
            ) {
                Text(text = "Sell")
            }'''

NEW = '''            OutlinedTextField(
                value = quantityText,
                onValueChange = { new -> if (new.length <= 6 && new.all { it.isDigit() }) quantityText = new },
                modifier = Modifier.width(56.dp),
                singleLine = true,
                textStyle = MaterialTheme.typography.bodyMedium,
                contentPadding = PaddingValues(horizontal = 8.dp, vertical = 8.dp),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
            )
            Button(
                onClick = { enteredQuantity?.let { onSell(item.itemId, it) } },
                enabled = isValidQuantity,
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp)
            ) {
                Text(text = "Sell", maxLines = 1, softWrap = false, overflow = TextOverflow.Ellipsis)
            }'''


def main() -> None:
    if not TARGET.exists():
        raise SystemExit(f"ABORT: could not find {TARGET} from the current directory. Run this from the repo root.")

    content = TARGET.read_text(encoding="utf-8")

    if "Modifier.width(56.dp)" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    count = content.count(OLD)
    if count == 0:
        raise SystemExit("ABORT: could not find the expected quantity box / Sell button block. No changes written.")
    if count > 1:
        raise SystemExit(f"ABORT: found {count} matches, expected exactly 1. No changes written.")

    content = content.replace(OLD, NEW, 1)

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content, encoding="utf-8")
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
