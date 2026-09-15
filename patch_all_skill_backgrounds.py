BASE = "app/src/main/kotlin/com/yourname/idlerpg/"

def guarded_replace(path, old, new, label):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    if new in text:
        print(f"SKIP (already applied): {label} ({path})")
        return True

    count = text.count(old)
    if count == 1:
        text = text.replace(old, new)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"OK: {label} ({path})")
        return True
    elif count == 0:
        print(f"FAIL (old_str not found, new_str not found either): {label} ({path})")
        return False
    else:
        print(f"FAIL (old_str matched {count} times, expected 1): {label} ({path})")
        return False


path = BASE + "ModerationScreen.kt"
old = "    onGrantGems: (Long) -> Unit = {},"
new = "    onGrantGems: (String, Long, String) -> Unit = { _, _, _ -> },"
ok = guarded_replace(path, old, new, "fix ModerationScreen's onGrantGems parameter type")

if not ok:
    import sys
    sys.exit(1)

print("Done.")
