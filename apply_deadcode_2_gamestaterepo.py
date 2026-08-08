"""
Cleanup (2/3): remove softCurrency from the save/load JSON round-trip in
GameStateRepository, matching the field removal in step 1/3.

Run from repo root: python3 apply_deadcode_2_gamestaterepo.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/GameStateRepository.kt")

OLD_SAVE = '''            obj.put("subscriptionTier", acc.subscriptionTier)
            obj.put("softCurrency", acc.softCurrency)
            obj.put("premiumCurrency", acc.premiumCurrency)'''
NEW_SAVE = '''            obj.put("subscriptionTier", acc.subscriptionTier)
            obj.put("premiumCurrency", acc.premiumCurrency)'''

OLD_LOAD = '''                    subscriptionTier = obj.getString("subscriptionTier"),
                    softCurrency = obj.getLong("softCurrency"), premiumCurrency = obj.getLong("premiumCurrency")'''
NEW_LOAD = '''                    subscriptionTier = obj.getString("subscriptionTier"),
                    premiumCurrency = obj.getLong("premiumCurrency")'''


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

    if 'obj.put("softCurrency"' not in content:
        raise SystemExit("ABORT: softCurrency already gone from this file -- looks like this patch was already applied. No changes written.")

    content = replace_once(content, OLD_SAVE, NEW_SAVE, "save JSON write")
    content = replace_once(content, OLD_LOAD, NEW_LOAD, "load JSON read")

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
