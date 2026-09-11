#!/usr/bin/env python3
"""
Guarded patch: show bone burying in the Home tab's active queue card,
including how many bones are left to bury. ActiveQueue.BuryQueue already
existed with the exact shape needed (itemId, targetQuantity,
quantityCompleted, secondsPerAction, startedAt) - it just fell through
the `else -> null` branch that builds ActiveQueueInfo, so it silently
never showed anywhere.
"""
import os

path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = (
    "            is ActiveQueue.CraftingQueue -> ActiveQueueInfo(\n"
    "                label = \"Crafting \" + formatItemName(queue.itemId),\n"
    "                secondsPerAction = queue.secondsPerAction,\n"
    "                startedAt = queue.startedAt\n"
    "            )\n"
    "            else -> null\n"
)
new = (
    "            is ActiveQueue.CraftingQueue -> ActiveQueueInfo(\n"
    "                label = \"Crafting \" + formatItemName(queue.itemId),\n"
    "                secondsPerAction = queue.secondsPerAction,\n"
    "                startedAt = queue.startedAt\n"
    "            )\n"
    "            is ActiveQueue.BuryQueue -> {\n"
    "                val remaining = queue.targetQuantity - queue.quantityCompleted\n"
    "                ActiveQueueInfo(\n"
    "                    label = \"Burying \" + formatItemName(queue.itemId) + \" (\" + remaining + \" left)\",\n"
    "                    secondsPerAction = queue.secondsPerAction,\n"
    "                    startedAt = queue.startedAt\n"
    "                )\n"
    "            }\n"
    "            else -> null\n"
)

marker = "is ActiveQueue.BuryQueue -> {"
if marker in content:
    print("SKIP (already applied)")
else:
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly 1 match, found {count}.\n--- old_str ---\n{old}\n--- end ---")
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("PATCHED: ActiveQueue.BuryQueue now shows in Home tab queue")

print("Done.")
