#!/usr/bin/env python3
"""
Fix: the Market screen's three tab buttons (Browse / My Orders / Vendor)
had no width constraint, so a plain Row laid them out at natural content
width -- if "Browse" + "My Orders" ate up most of the row, "Vendor" got
squeezed into whatever space was left, wrapping its text letter-by-letter.

Fix: give the Row fillMaxWidth() and each button Modifier.weight(1f), so
all three split the row evenly (same pattern already used for the
Gear/Bars toggle in SmithingScreen.kt's material picker dialog).

Run from repo root:
    python3 apply_market_tabbutton_fix.py
Then rebuild:
    ./gradlew assembleDebug --console=plain --no-daemon --no-configuration-cache
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

    if "MarketTabButton(\n    label: String" in text:
        fail("MarketTabButton already takes a modifier parameter -- patch may already be applied")

    # 1. Tab row: fillMaxWidth + weight(1f) on each button call
    text = replace_once(
        text,
        (
            "        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {\n"
            "            MarketTabButton(\"Browse\", currentTab == MarketTab.BROWSE) { onTabSelected(MarketTab.BROWSE) }\n"
            "            MarketTabButton(\"My Orders\", currentTab == MarketTab.MY_ORDERS) { onTabSelected(MarketTab.MY_ORDERS) }\n"
            "            MarketTabButton(\"Vendor\", currentTab == MarketTab.SELL_TO_VENDOR) { onTabSelected(MarketTab.SELL_TO_VENDOR) }\n"
            "        }\n"
        ),
        (
            "        Row(\n"
            "            modifier = Modifier.fillMaxWidth(),\n"
            "            horizontalArrangement = Arrangement.spacedBy(8.dp)\n"
            "        ) {\n"
            "            MarketTabButton(\n"
            "                label = \"Browse\",\n"
            "                isSelected = currentTab == MarketTab.BROWSE,\n"
            "                modifier = Modifier.weight(1f)\n"
            "            ) { onTabSelected(MarketTab.BROWSE) }\n"
            "            MarketTabButton(\n"
            "                label = \"My Orders\",\n"
            "                isSelected = currentTab == MarketTab.MY_ORDERS,\n"
            "                modifier = Modifier.weight(1f)\n"
            "            ) { onTabSelected(MarketTab.MY_ORDERS) }\n"
            "            MarketTabButton(\n"
            "                label = \"Vendor\",\n"
            "                isSelected = currentTab == MarketTab.SELL_TO_VENDOR,\n"
            "                modifier = Modifier.weight(1f)\n"
            "            ) { onTabSelected(MarketTab.SELL_TO_VENDOR) }\n"
            "        }\n"
        ),
        "tab row",
    )

    # 2. MarketTabButton(): accept and apply a modifier
    text = replace_once(
        text,
        (
            "private fun MarketTabButton(label: String, isSelected: Boolean, onClick: () -> Unit) {\n"
            "    if (isSelected) {\n"
            "        Button(onClick = onClick) { Text(text = label) }\n"
            "    } else {\n"
            "        OutlinedButton(onClick = onClick) { Text(text = label) }\n"
            "    }\n"
            "}\n"
        ),
        (
            "private fun MarketTabButton(\n"
            "    label: String,\n"
            "    isSelected: Boolean,\n"
            "    modifier: Modifier = Modifier,\n"
            "    onClick: () -> Unit\n"
            ") {\n"
            "    if (isSelected) {\n"
            "        Button(onClick = onClick, modifier = modifier) { Text(text = label) }\n"
            "    } else {\n"
            "        OutlinedButton(onClick = onClick, modifier = modifier) { Text(text = label) }\n"
            "    }\n"
            "}\n"
        ),
        "MarketTabButton() definition",
    )

    if text == original:
        fail("no changes were made -- aborting")

    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")
    print("Run: git diff", TARGET, "to verify before rebuilding.")


if __name__ == "__main__":
    main()
