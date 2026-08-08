"""
Fix (2/3): make buildInventoryItemSummaries() take a vendorPayoutFor lookup
and use it for npcValuePerUnit, instead of the raw undiscounted
ItemCatalog.baseValueFor(). Wires the call site to
gameViewModel.marketService::vendorPayoutPerUnit (added in step 1/3), so
the price shown in Inventory/Vendor screens always matches what
sellToVendor() actually pays.

Run from repo root: python3 apply_vendor_price_2_mainactivity.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")

OLD_SIGNATURE = "private fun buildInventoryItemSummaries(entries: List<InventorySlotEntry>): List<InventoryItemSummary> {"
NEW_SIGNATURE = (
    "private fun buildInventoryItemSummaries(\n"
    "    entries: List<InventorySlotEntry>,\n"
    "    vendorPayoutFor: (String) -> Long\n"
    "): List<InventoryItemSummary> {"
)

OLD_LINE_1 = "                npcValuePerUnit = ItemCatalog.baseValueFor(entry.itemId),\n                statsDescription = statsText"
NEW_LINE_1 = "                npcValuePerUnit = vendorPayoutFor(entry.itemId),\n                statsDescription = statsText"

OLD_LINE_2 = '''                isConsumable = false,
                npcValuePerUnit = ItemCatalog.baseValueFor(entry.itemId)
            )
        }
    }
}'''
NEW_LINE_2 = '''                isConsumable = false,
                npcValuePerUnit = vendorPayoutFor(entry.itemId)
            )
        }
    }
}'''

OLD_CALL_SITE = "val inventoryItems = remember(inventoryItemEntries) { buildInventoryItemSummaries(inventoryItemEntries) }"
NEW_CALL_SITE = (
    "val inventoryItems = remember(inventoryItemEntries) {\n"
    "        buildInventoryItemSummaries(inventoryItemEntries, gameViewModel.marketService::vendorPayoutPerUnit)\n"
    "    }"
)


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

    if "vendorPayoutFor: (String) -> Long" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    content = replace_once(content, OLD_SIGNATURE, NEW_SIGNATURE, "buildInventoryItemSummaries signature")
    content = replace_once(content, OLD_LINE_1, NEW_LINE_1, "npcValuePerUnit (defined item branch)")
    content = replace_once(content, OLD_LINE_2, NEW_LINE_2, "npcValuePerUnit (fallback material branch)")
    content = replace_once(content, OLD_CALL_SITE, NEW_CALL_SITE, "buildInventoryItemSummaries call site")

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
