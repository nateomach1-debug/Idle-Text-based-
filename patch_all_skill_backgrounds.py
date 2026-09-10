#!/usr/bin/env python3
"""
Guarded patch: remove the hardcoded "2 new notifications" placeholder
from the Home tab by zeroing out unreadNotificationCount (HomeScreen.kt
already hides the NotificationSummary block entirely when count <= 0,
so no changes needed there).
"""
import os

path = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "        unreadNotificationCount = 2\n"
new = "        unreadNotificationCount = 0\n"

if new in content and old not in content:
    print("SKIP (already applied)")
else:
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly 1 match, found {count}")
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("PATCHED: unreadNotificationCount set to 0")

print("Done.")
