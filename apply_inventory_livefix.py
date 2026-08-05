#!/usr/bin/env python3
"""
Fix: inventory tab not updating live while an action runs.

Root cause: InventorySlotEntry.quantity was a mutable `var`, and
addItem()/removeItem() mutated the existing entry object in place. Since
Kotlin's generated equals() short-circuits on reference identity
(`this === other`), two Lists containing the same (mutated) object
reference compare as "equal" even after a quantity change -- so
MutableStateFlow's built-in distinct-value check silently skips notifying
observers. That's why the Inventory screen looked right on first
navigation (a fresh composition always reads the current .value) but
never live-updated while sitting on the tab watching a repeating action.

Fix: make quantity immutable and replace the map entry with a new object
(.copy()) on every change, so there's a genuine reference/value change
for StateFlow to detect.

Run from repo root:
    python3 apply_inventory_livefix.py
Then rebuild:
    ./gradlew assembleDebug --console=plain --no-daemon --no-configuration-cache
"""
import sys
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/ItemsEquipmentSystem.kt")


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

    # 1. Make quantity immutable
    text = replace_once(
        text,
        "data class InventorySlotEntry(val itemId: String, var quantity: Int)",
        "data class InventorySlotEntry(val itemId: String, val quantity: Int)",
        "InventorySlotEntry declaration",
    )

    # 2. addItem(): replace in-place mutation with a fresh copy in the map
    text = replace_once(
        text,
        (
            "        val existing = entries[itemId]\n"
            "        if (existing != null) {\n"
            "            if (!definition.isStackable) return ServiceResult.Failure(\"Item is not stackable and already present.\")\n"
            "            existing.quantity += quantity\n"
            "            return ServiceResult.Success(Unit)\n"
            "        }\n"
        ),
        (
            "        val existing = entries[itemId]\n"
            "        if (existing != null) {\n"
            "            if (!definition.isStackable) return ServiceResult.Failure(\"Item is not stackable and already present.\")\n"
            "            entries[itemId] = existing.copy(quantity = existing.quantity + quantity)\n"
            "            return ServiceResult.Success(Unit)\n"
            "        }\n"
        ),
        "addItem() in-place mutation",
    )

    # 3. removeItem(): same fix, plus keep the remove-when-empty behavior
    text = replace_once(
        text,
        (
            "    fun removeItem(itemId: String, quantity: Int): ServiceResult<Unit> {\n"
            "        val entry = entries[itemId] ?: return ServiceResult.Failure(\"Item not in inventory.\")\n"
            "        if (entry.quantity < quantity) return ServiceResult.Failure(\"Not enough quantity to remove.\")\n"
            "\n"
            "        entry.quantity -= quantity\n"
            "        if (entry.quantity <= 0) entries.remove(itemId)\n"
            "        return ServiceResult.Success(Unit)\n"
            "    }\n"
        ),
        (
            "    fun removeItem(itemId: String, quantity: Int): ServiceResult<Unit> {\n"
            "        val entry = entries[itemId] ?: return ServiceResult.Failure(\"Item not in inventory.\")\n"
            "        if (entry.quantity < quantity) return ServiceResult.Failure(\"Not enough quantity to remove.\")\n"
            "\n"
            "        val newQuantity = entry.quantity - quantity\n"
            "        if (newQuantity <= 0) {\n"
            "            entries.remove(itemId)\n"
            "        } else {\n"
            "            entries[itemId] = entry.copy(quantity = newQuantity)\n"
            "        }\n"
            "        return ServiceResult.Success(Unit)\n"
            "    }\n"
        ),
        "removeItem() in-place mutation",
    )

    if text == original:
        fail("no changes were made -- aborting")

    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")
    print("Run: git diff", TARGET, "to verify before rebuilding.")


if __name__ == "__main__":
    main()
