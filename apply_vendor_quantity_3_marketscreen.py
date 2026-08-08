"""
Fix (3/3): Vendor tab could only sell an entire stack at once ("Sell All").
Replaces that with an editable quantity field, defaulting to your full
stack (so hitting Sell with no edits still behaves like the old "Sell
All"), clamped so it can never exceed what you actually own.

Run from repo root: python3 apply_vendor_quantity_3_marketscreen.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/MarketScreen.kt")

OLD_IMPORTS = "import androidx.compose.foundation.shape.RoundedCornerShape\nimport androidx.compose.material3.*"
NEW_IMPORTS = (
    "import androidx.compose.foundation.shape.RoundedCornerShape\n"
    "import androidx.compose.foundation.text.KeyboardOptions\n"
    "import androidx.compose.material3.*"
)

OLD_IMPORTS_2 = "import androidx.compose.ui.draw.clip\nimport androidx.compose.ui.unit.dp"
NEW_IMPORTS_2 = (
    "import androidx.compose.ui.draw.clip\n"
    "import androidx.compose.ui.text.input.KeyboardType\n"
    "import androidx.compose.ui.unit.dp"
)

OLD_ROW = '''@Composable
private fun VendorItemRow(item: InventoryItemSummary, onSell: (String, Int) -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(14.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text(text = item.displayName, style = MaterialTheme.typography.titleMedium)
            Text(
                text = "x" + item.quantity + " \u2014 " + item.npcValuePerUnit + " each",
                style = MaterialTheme.typography.labelSmall
            )
        }
        Button(onClick = { onSell(item.itemId, item.quantity) }) {
            Text(text = "Sell All")
        }
    }
}'''

NEW_ROW = '''@Composable
private fun VendorItemRow(item: InventoryItemSummary, onSell: (String, Int) -> Unit) {
    var quantityText by remember(item.itemId, item.quantity) { mutableStateOf(item.quantity.toString()) }
    val enteredQuantity = quantityText.toIntOrNull()
    val isValidQuantity = enteredQuantity != null && enteredQuantity in 1..item.quantity

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(14.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(text = item.displayName, style = MaterialTheme.typography.titleMedium)
            Text(
                text = "x" + item.quantity + " \u2014 " + item.npcValuePerUnit + " each",
                style = MaterialTheme.typography.labelSmall
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

    if "quantityText" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    content = replace_once(content, OLD_IMPORTS, NEW_IMPORTS, "KeyboardOptions import")
    content = replace_once(content, OLD_IMPORTS_2, NEW_IMPORTS_2, "KeyboardType import")
    content = replace_once(content, OLD_ROW, NEW_ROW, "VendorItemRow")

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
