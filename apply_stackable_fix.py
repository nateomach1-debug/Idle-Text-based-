"""
Fix: Inventory.addItem() silently discards items when a non-stackable item
(e.g. a crafted weapon/armor piece) is added while one is already present.
This caused crafting materials to be consumed with no output on repeated
successful crafts of weapons/armor (confirmed: bronze dagger/sword capped
at 1 output no matter how many bronze bars were consumed).

Fix: non-stackable items now accumulate a quantity count in their existing
inventory slot too, same as stackable items. This removes the silent-loss
path entirely (crafting, gathering, and re-equipping a duplicate item will
no longer vanish).

Run from repo root: python3 apply_stackable_fix.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/ItemsEquipmentSystem.kt")

OLD = '''        val existing = entries[itemId]
        if (existing != null) {
            if (!definition.isStackable) return ServiceResult.Failure("Item is not stackable and already present.")
            entries[itemId] = existing.copy(quantity = existing.quantity + quantity)
            return ServiceResult.Success(Unit)
        }'''

NEW = '''        val existing = entries[itemId]
        if (existing != null) {
            entries[itemId] = existing.copy(quantity = existing.quantity + quantity)
            return ServiceResult.Success(Unit)
        }'''

MARKER = 'if (!definition.isStackable) return ServiceResult.Failure("Item is not stackable and already present.")'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 0:
        raise SystemExit(f"ABORT: could not find expected block for '{label}' -- file may have changed. No changes written.")
    if count > 1:
        raise SystemExit(f"ABORT: found {count} matches for '{label}', expected exactly 1. No changes written.")
    return text.replace(old, new, 1)


def main() -> None:
    if not TARGET.exists():
        raise SystemExit(f"ABORT: could not find {TARGET} from the current directory. Run this from the repo root.")

    content = TARGET.read_text()

    if MARKER not in content:
        raise SystemExit(
            "ABORT: the non-stackable check is already gone from this file -- "
            "looks like this patch was already applied. No changes written."
        )

    content = replace_once(content, OLD, NEW, "Inventory.addItem non-stackable guard")

    # sanity check: brace balance unchanged by this edit (we only removed one line)
    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
