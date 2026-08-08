"""
Cleanup (1/3): Account.softCurrency (AccountCharacterSystem.kt) is dead --
confirmed nothing anywhere calls AccountService.addCurrency() (its only
writer), and the Home screen's Gold display is built entirely from
PlayerEconomyAccount.currencyBalance, not this field. Removing it and its
"soft" export/import plumbing. account.premiumCurrency is left untouched
-- it IS read for the Home screen's Gems display, even though nothing
currently grants it either (that's a separate, bigger monetization gap,
not part of this cleanup).

Run from repo root: python3 apply_deadcode_1_softcurrency.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/AccountCharacterSystem.kt")

EDITS = [
    (
        "    var subscriptionTier: SubscriptionTier = SubscriptionTier.NONE,\n    var softCurrency: Long = 0,\n    var premiumCurrency: Long = 0\n) {",
        "    var subscriptionTier: SubscriptionTier = SubscriptionTier.NONE,\n    var premiumCurrency: Long = 0\n) {",
        "Account class field",
    ),
    (
        "    val subscriptionTier: String, val softCurrency: Long, val premiumCurrency: Long\n)",
        "    val subscriptionTier: String, val premiumCurrency: Long\n)",
        "AccountExport field",
    ),
    (
        '''    fun addCurrency(accountId: String, soft: Long = 0, premium: Long = 0): ServiceResult<Account> {
        val account = accountsById[accountId] ?: return ServiceResult.Failure("Account not found.")
        if (soft < 0 || premium < 0) return ServiceResult.Failure("Currency amounts cannot be negative.")
        account.softCurrency += soft
        account.premiumCurrency += premium
        return ServiceResult.Success(account)
    }''',
        '''    fun addCurrency(accountId: String, premium: Long = 0): ServiceResult<Account> {
        val account = accountsById[accountId] ?: return ServiceResult.Failure("Account not found.")
        if (premium < 0) return ServiceResult.Failure("Currency amounts cannot be negative.")
        account.premiumCurrency += premium
        return ServiceResult.Success(account)
    }''',
        "addCurrency() function",
    ),
    (
        "            it.subscriptionTier.name, it.softCurrency, it.premiumCurrency\n        )",
        "            it.subscriptionTier.name, it.premiumCurrency\n        )",
        "exportAllAccounts() mapping",
    ),
    (
        "            subscriptionTier = SubscriptionTier.valueOf(export.subscriptionTier),\n            softCurrency = export.softCurrency, premiumCurrency = export.premiumCurrency\n        )",
        "            subscriptionTier = SubscriptionTier.valueOf(export.subscriptionTier),\n            premiumCurrency = export.premiumCurrency\n        )",
        "restoreAccount() mapping",
    ),
]


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

    if "var softCurrency" not in content:
        raise SystemExit("ABORT: softCurrency field already gone -- looks like this patch was already applied. No changes written.")

    for old, new, label in EDITS:
        content = replace_once(content, old, new, label)

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
