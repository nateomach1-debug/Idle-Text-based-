#!/usr/bin/env python3
"""
Guarded patch: bone-burying "X left" count wasn't live-updating on the
Home tab because refreshActiveQueue() was only called when the queue
stopped (target reached / ran out of bones), never after each batch of
completed buries mid-queue.
"""
import os

path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = (
    "        if (effectiveAttempts > 0) {\n"
    "            inventory.removeItem(queue.itemId, effectiveAttempts)\n"
    "            progressionService.grantXp(characterId, SkillType.PRAYER, boneInfo.xpAmount * effectiveAttempts, guildXpBonusEffects())\n"
    "            queue.quantityCompleted += effectiveAttempts\n"
    "            refreshInventory()\n"
    "            refreshSkills()\n"
    "        }\n"
)
new = (
    "        if (effectiveAttempts > 0) {\n"
    "            inventory.removeItem(queue.itemId, effectiveAttempts)\n"
    "            progressionService.grantXp(characterId, SkillType.PRAYER, boneInfo.xpAmount * effectiveAttempts, guildXpBonusEffects())\n"
    "            queue.quantityCompleted += effectiveAttempts\n"
    "            refreshInventory()\n"
    "            refreshSkills()\n"
    "            refreshActiveQueue()\n"
    "        }\n"
)

marker = "queue.quantityCompleted += effectiveAttempts\n            refreshInventory()\n            refreshSkills()\n            refreshActiveQueue()\n"
if marker in content:
    print("SKIP (already applied)")
else:
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly 1 match, found {count}.\n--- old_str ---\n{old}\n--- end ---")
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("PATCHED: refreshActiveQueue() now called after each completed bury batch")

print("Done.")
