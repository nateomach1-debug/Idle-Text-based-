#!/usr/bin/env python3
"""
Market tab polish: renames "My Orders" -> "Orders", and shrinks the tab
button text (labelLarge instead of the Button/OutlinedButton default,
which is titleMedium-ish).

Run from repo root:
    python3 apply_market_tab_labels.py
"""
import sys
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/MarketScreen.kt")


def fail(msg):
    print(f"FAILED: {msg}")
    sys.exit(1)


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        fail(f"expected exactly 1 occurrence of [{label}], found {count}")
    return text.replace(old, new, 1)


def main():
    if not TARGET.exists():
        fail(f"{TARGET} not found -- run this from the repo root")

    text = TARGET.read_text()
    original = text

    # 1. Rename "My Orders" -> "Orders"
    text = replace_once(
        text,
        '                label = "My Orders",\n',
        '                label = "Orders",\n',
        "My Orders label",
    )

    # 2. MarketTabButton: pass a smaller text style
    text = replace_once(
        text,
        (
            "    if (isSelected) {\n"
            "        Button(onClick = onClick, modifier = modifier) { Text(text = label) }\n"
            "    } else {\n"
            "        OutlinedButton(onClick = onClick, modifier = modifier) { Text(text = label) }\n"
            "    }\n"
        ),
        (
            "    if (isSelected) {\n"
            "        Button(onClick = onClick, modifier = modifier) {\n"
            "            Text(text = label, style = MaterialTheme.typography.labelMedium)\n"
            "        }\n"
            "    } else {\n"
            "        OutlinedButton(onClick = onClick, modifier = modifier) {\n"
            "            Text(text = label, style = MaterialTheme.typography.labelMedium)\n"
            "        }\n"
            "    }\n"
        ),
        "MarketTabButton text style",
    )

    if text == original:
        fail("no changes were made -- aborting")

    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
