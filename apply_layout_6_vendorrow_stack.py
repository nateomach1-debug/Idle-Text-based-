"""
Fix: even with weight(1f) and ellipsis, the Vendor row's item name Column
was still squeezed to near-nothing by the quantity box + Sell button
sharing the same row -- showing just a truncated dot. Restructuring to a
vertical stack: item name and quantity/price on their own full-width
lines, with the quantity box + Sell button in a row below. Removes the
horizontal contention entirely.

Run from repo root: python3 apply_layout_6_vendorrow_stack.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/MarketScreen.kt")

OLD = '''    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(14.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
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
        }
        Spacer(modifier = Modifier.width(8.dp))
        OutlinedTextField(
            value = quantityText,
            onValueChange = { new -> if (new.length <= 6 && new.all { it.isDigit() }) quantityText = new },
            modifier = Modifier.width(64.dp),
            singleLine = true,
            textStyle = MaterialTheme.typography.bodyMedium,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Button(
            onClick = { enteredQuantity?.let { onSell(item.itemId, it) } },
            enabled = isValidQuantity
        ) {
            Text(text = "Sell")
        }
    }'''

NEW = '''    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(14.dp)
    ) {
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
        Spacer(modifier = Modifier.height(10.dp))
        Row(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
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
            }
        }
    }'''


def main() -> None:
    if not TARGET.exists():
        raise SystemExit(f"ABORT: could not find {TARGET} from the current directory. Run this from the repo root.")

    content = TARGET.read_text(encoding="utf-8")

    if "Spacer(modifier = Modifier.height(10.dp))" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    count = content.count(OLD)
    if count == 0:
        raise SystemExit("ABORT: could not find the expected VendorItemRow block. No changes written.")
    if count > 1:
        raise SystemExit(f"ABORT: found {count} matches, expected exactly 1. No changes written.")

    content = content.replace(OLD, NEW, 1)

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content, encoding="utf-8")
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
