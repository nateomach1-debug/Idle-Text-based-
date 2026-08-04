#!/usr/bin/env python3
"""
Quick-wins patch, part 2b: MainActivity.kt

- Replaces the hardcoded `val homeState = remember { HomeScreenState(...) }`
  literal with one built from real GameViewModel StateFlows
  (activeQueueInfo, currency), recomposing whenever they change.
- Removes the now-gone `onCollectLoot` argument from the HomeScreen() call.

Run this AFTER apply_quickwins_gameviewmodel.py and
apply_quickwins_homescreen.py (this file references activeQueueInfo/currency
and the new HomeScreen() signature, both defined by those patches).

Run from repo root:
    python3 apply_quickwins_mainactivity.py
Then rebuild:
    ./gradlew assembleDebug --console=plain --no-daemon --no-configuration-cache
"""
import sys
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")


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

    if "activeQueueInfo.collectAsState" in text:
        fail("homeState already wired to activeQueueInfo -- patch may already be applied")

    # 1. Replace the hardcoded homeState block
    text = replace_once(
        text,
        (
            "    val homeState = remember {\n"
            "        HomeScreenState(\"Mining Iron Ore\", Instant.now().plusSeconds(90), 1250, 40, 80, 100, false, 3, 2)\n"
            "    }\n"
        ),
        (
            "    val activeQueue by gameViewModel.activeQueueInfo.collectAsState()\n"
            "    val currency by gameViewModel.currency.collectAsState()\n"
            "    val homeState = HomeScreenState(\n"
            "        activeQueue = activeQueue,\n"
            "        softCurrency = currency.first,\n"
            "        premiumCurrency = currency.second,\n"
            "        currentHp = null,\n"
            "        maxHp = null,\n"
            "        isRecovering = false,\n"
            "        unreadNotificationCount = 2\n"
            "    )\n"
        ),
        "homeState declaration",
    )

    # 2. Drop the onCollectLoot argument from the HomeScreen() call
    text = replace_once(
        text,
        "AppDestination.HOME -> HomeScreen(state = homeState, onCollectLoot = { })",
        "AppDestination.HOME -> HomeScreen(state = homeState)",
        "HomeScreen() call site",
    )

    if text == original:
        fail("no changes were made -- aborting")

    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")
    print("Run: git diff", TARGET, "to verify before rebuilding.")


if __name__ == "__main__":
    main()
