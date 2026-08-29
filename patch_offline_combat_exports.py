path = "app/src/main/kotlin/com/yourname/idlerpg/OfflineIdleMechanicsSystem.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor1 = 'data class LastSaleCheckExport(val characterId: String, val lastSaleCheckAt: String)'
count1 = content.count(anchor1)
assert count1 == 1, f"Expected 1 match for anchor1, found {count1}. Anchor: {anchor1!r}"
replacement1 = anchor1 + '\n\ndata class OfflineCombatQueueExport(val characterId: String, val zoneId: String, val startedAt: String)'
content = content.replace(anchor1, replacement1, 1)

anchor2 = '''    fun exportLastSaleCheck(): List<LastSaleCheckExport> =
        lastSaleCheckAt.map { (characterId, instant) -> LastSaleCheckExport(characterId, instant.toString()) }'''
count2 = content.count(anchor2)
assert count2 == 1, f"Expected 1 match for anchor2, found {count2}. Anchor: {anchor2!r}"
replacement2 = anchor2 + '''

    fun exportOfflineCombatQueues(): List<OfflineCombatQueueExport> =
        activeQueues.values.filterIsInstance<ActiveQueue.OfflineCombatQueue>().map {
            OfflineCombatQueueExport(it.characterId, it.zoneId, it.startedAt.toString())
        }'''
content = content.replace(anchor2, replacement2, 1)

anchor3 = '''    fun restoreLastSaleCheck(export: LastSaleCheckExport) {
        lastSaleCheckAt[export.characterId] = Instant.parse(export.lastSaleCheckAt)
    }
}'''
count3 = content.count(anchor3)
assert count3 == 1, f"Expected 1 match for anchor3, found {count3}. Anchor: {anchor3!r}"
replacement3 = '''    fun restoreLastSaleCheck(export: LastSaleCheckExport) {
        lastSaleCheckAt[export.characterId] = Instant.parse(export.lastSaleCheckAt)
    }

    fun restoreOfflineCombatQueue(export: OfflineCombatQueueExport) {
        activeQueues[export.characterId] = ActiveQueue.OfflineCombatQueue(
            characterId = export.characterId,
            zoneId = export.zoneId,
            startedAt = Instant.parse(export.startedAt)
        )
    }
}'''
content = content.replace(anchor3, replacement3, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("patch_offline_combat_exports.py applied cleanly.")