# PART I: Fix Long/Int mismatch...
path = "app/src/main/kotlin/com/yourname/idlerpg/OfflineIdleMechanicsSystem.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor_buryqueue_class = '''    data class BuryQueue(
        override val characterId: String,
        val itemId: String,
        val targetQuantity: Int,
        var quantityCompleted: Int = 0,
        val secondsPerAction: Int,
        val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.BURYING
        fun isTargetReached(): Boolean = quantityCompleted >= targetQuantity
    }
}'''
count = content.count(anchor_buryqueue_class)
assert count == 1, f"Expected 1 match, found {count}."
replacement_buryqueue_class = '''    data class BuryQueue(
        override val characterId: String,
        val itemId: String,
        val targetQuantity: Int,
        var quantityCompleted: Int = 0,
        val secondsPerAction: Long,
        override val startedAt: Instant = Instant.now()
    ) : ActiveQueue() {
        override val type = QueueType.BURYING
        fun isTargetReached(): Boolean = quantityCompleted >= targetQuantity
    }
}'''
content = content.replace(anchor_buryqueue_class, replacement_buryqueue_class, 1)

anchor_startburyqueue = '''    fun startBuryQueue(characterId: String, itemId: String, targetQuantity: Int, secondsPerAction: Int): ServiceResult<ActiveQueue> {'''
count3 = content.count(anchor_startburyqueue)
assert count3 == 1, f"Expected 1 match, found {count3}."
content = content.replace(
    anchor_startburyqueue,
    '    fun startBuryQueue(characterId: String, itemId: String, targetQuantity: Int, secondsPerAction: Long): ServiceResult<ActiveQueue> {',
    1
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part I (OfflineIdleMechanicsSystem.kt Long/Int fix) applied cleanly.")

# PART J: Add the missing PrayerDefinition import to LoadoutScreen.kt
path = "app/src/main/kotlin/com/yourname/idlerpg/LoadoutScreen.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor = "import com.yourname.idlerpg.SkillType"
count = content.count(anchor)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(anchor, anchor + "\nimport com.yourname.idlerpg.PrayerDefinition", 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part J (LoadoutScreen.kt import fix) applied cleanly.")
