"""
Fix (1/3): vendor sell price shown to the player didn't match what they
actually got paid -- the display used the full undiscounted item value
while sellToVendor() only ever paid 40% of it.

This adds a single vendorPayoutPerUnit() function to MarketService so the
40% math lives in exactly one place, and sellToVendor() now calls it
instead of duplicating the formula. Step 2/3 will point the UI's displayed
price at this same function.

Run from repo root: python3 apply_vendor_price_1_economymarket.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/EconomyMarketSystem.kt")

OLD = '''    fun sellToVendor(characterId: String, itemId: String, quantity: Int): ServiceResult<Long> {
        requireMainCharacter(characterId)?.let { return it as ServiceResult.Failure }
        val account = accounts.getValue(characterId)
        val item = ItemCatalog.find(itemId) ?: return ServiceResult.Failure("Unknown item.")

        if (quantity <= 0) return ServiceResult.Failure("Quantity must be positive.")
        if (!account.removeItem(itemId, quantity)) {
            return ServiceResult.Failure("Insufficient item quantity to sell.")
        }

        val baseValue = ItemCatalog.baseValueFor(item.id)
        val payout = ((baseValue * vendorPayoutPercent) / 100.0).toLong() * quantity
        account.currencyBalance += payout
        monitoring.recordVendorPayout(payout)

        return ServiceResult.Success(payout)
    }'''

NEW = '''    fun vendorPayoutPerUnit(itemId: String): Long {
        val baseValue = ItemCatalog.baseValueFor(itemId)
        return ((baseValue * vendorPayoutPercent) / 100.0).toLong()
    }

    fun sellToVendor(characterId: String, itemId: String, quantity: Int): ServiceResult<Long> {
        requireMainCharacter(characterId)?.let { return it as ServiceResult.Failure }
        val account = accounts.getValue(characterId)
        val item = ItemCatalog.find(itemId) ?: return ServiceResult.Failure("Unknown item.")

        if (quantity <= 0) return ServiceResult.Failure("Quantity must be positive.")
        if (!account.removeItem(itemId, quantity)) {
            return ServiceResult.Failure("Insufficient item quantity to sell.")
        }

        val payout = vendorPayoutPerUnit(item.id) * quantity
        account.currencyBalance += payout
        monitoring.recordVendorPayout(payout)

        return ServiceResult.Success(payout)
    }'''

MARKER = "val baseValue = ItemCatalog.baseValueFor(item.id)"


def main() -> None:
    if not TARGET.exists():
        raise SystemExit(f"ABORT: could not find {TARGET} from the current directory. Run this from the repo root.")

    content = TARGET.read_text()

    if MARKER not in content:
        raise SystemExit(
            "ABORT: expected sellToVendor() block not found -- looks like this patch "
            "was already applied, or the file has changed. No changes written."
        )

    count = content.count(OLD)
    if count == 0:
        raise SystemExit("ABORT: could not find the exact sellToVendor() block to replace. No changes written.")
    if count > 1:
        raise SystemExit(f"ABORT: found {count} matches, expected exactly 1. No changes written.")

    content = content.replace(OLD, NEW, 1)

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
