#!/usr/bin/env python3
"""
Market persistence, part 3: GameViewModel.kt

Wires marketService's export/import methods into the existing
saveGame()/loadGame() cycle, same pattern as every other service.

Run from repo root, AFTER apply_market_backend.py, apply_market_viewmodel.py,
apply_market_persistence_backend.py, and apply_market_persistence_repository.py:
    python3 apply_market_persistence_viewmodel.py
Then rebuild:
    ./gradlew assembleDebug --console=plain --no-daemon --no-configuration-cache
"""
import sys
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")


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

    if "restoreAccount(it) }\n        saved.marketOrders" in text or "marketService.exportAccounts" in text:
        fail("market persistence wiring already present -- patch may already be applied")

    # 1. loadGame(): restore market state after the existing restores
    text = replace_once(
        text,
        (
            "        saved.inventoryItems.forEach { inventoryService.restoreItem(it) }\n"
            "        saved.equippedSlots.forEach { inventoryService.restoreEquipped(it) }\n"
            "    }\n"
        ),
        (
            "        saved.inventoryItems.forEach { inventoryService.restoreItem(it) }\n"
            "        saved.equippedSlots.forEach { inventoryService.restoreEquipped(it) }\n"
            "        saved.marketAccounts.forEach { marketService.restoreAccount(it) }\n"
            "        saved.marketOrders.forEach { marketService.restoreOrder(it) }\n"
            "        saved.marketPriceHistory.forEach { marketService.restorePriceHistoryEntry(it) }\n"
            "    }\n"
        ),
        "loadGame() market restore",
    )

    # 2. saveGame(): export market state as the last three repository.save() args
    text = replace_once(
        text,
        (
            "            inventoryService.exportAllItems(),\n"
            "            inventoryService.exportAllEquipped()\n"
            "        )\n"
            "    }\n"
        ),
        (
            "            inventoryService.exportAllItems(),\n"
            "            inventoryService.exportAllEquipped(),\n"
            "            marketService.exportAccounts(),\n"
            "            marketService.exportOrders(),\n"
            "            marketService.exportPriceHistory()\n"
            "        )\n"
            "    }\n"
        ),
        "saveGame() market export",
    )

    if text == original:
        fail("no changes were made -- aborting")

    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")
    print("Run: git diff", TARGET, "to verify before rebuilding.")


if __name__ == "__main__":
    main()
