# PART K: Fix OfflineCombatQueue's startedAt override (a typo I introduced in my own
# earlier fix - the replacement text had the same bug as the anchor, just never caught),
# and add the missing BuryQueue branch to resolveOfflineProgress()'s exhaustive when.
path = "app/src/main/kotlin/com/yourname/idlerpg/OfflineIdleMechanicsSystem.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor_offlinecombat = '''    data class OfflineCombatQueue(
        override val characterId: String,
        val zoneId: String,
        val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.OFFLINE_COMBAT
    }'''
count = content.count(anchor_offlinecombat)
assert count == 1, f"Expected 1 match, found {count}."
replacement_offlinecombat = '''    data class OfflineCombatQueue(
        override val characterId: String,
        val zoneId: String,
        override val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.OFFLINE_COMBAT
    }'''
content = content.replace(anchor_offlinecombat, replacement_offlinecombat, 1)

anchor_when = '''            is ActiveQueue.OfflineCombatQueue -> {
                actionsCompleted = 0
            }
        }'''
count2 = content.count(anchor_when)
assert count2 == 1, f"Expected 1 match, found {count2}."
replacement_when = '''            is ActiveQueue.OfflineCombatQueue -> {
                actionsCompleted = 0
            }
            is ActiveQueue.BuryQueue -> {
                // Burying is resolved through its own dedicated live-tick logic
                // (tickBurying() in GameViewModel), not through this generic
                // elapsed-time catch-up path - no offline progress for it here,
                // same treatment as OfflineCombatQueue above.
                actionsCompleted = 0
            }
        }'''
content = content.replace(anchor_when, replacement_when, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part K (OfflineIdleMechanicsSystem.kt) applied cleanly.")
