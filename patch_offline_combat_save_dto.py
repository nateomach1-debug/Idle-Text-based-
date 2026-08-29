path = "app/src/main/kotlin/com/yourname/idlerpg/GameStateRepository.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor1 = '''    fun save(
        accounts: List<AccountExport>,
        characters: List<CharacterExport>,
        skills: List<SkillExport>,
        skillingQueues: List<SkillingQueueExport>,
        craftingQueues: List<CraftingQueueExport>,
        lastSeen: List<LastSeenExport>,
        lastSaleCheck: List<LastSaleCheckExport>,
        inventoryItems: List<InventorySlotExport>,
        equippedSlots: List<EquippedSlotExport>,
        loadoutSettings: List<LoadoutSettingsExport>,
        marketAccounts: List<PlayerEconomyAccountExport>,
        marketOrders: List<MarketOrderExport>,
        marketPriceHistory: List<PriceHistoryExport>
    ) {'''
count1 = content.count(anchor1)
assert count1 == 1, f"Expected 1 match for anchor1, found {count1}."
replacement1 = '''    fun save(
        accounts: List<AccountExport>,
        characters: List<CharacterExport>,
        skills: List<SkillExport>,
        skillingQueues: List<SkillingQueueExport>,
        craftingQueues: List<CraftingQueueExport>,
        lastSeen: List<LastSeenExport>,
        lastSaleCheck: List<LastSaleCheckExport>,
        inventoryItems: List<InventorySlotExport>,
        equippedSlots: List<EquippedSlotExport>,
        loadoutSettings: List<LoadoutSettingsExport>,
        marketAccounts: List<PlayerEconomyAccountExport>,
        marketOrders: List<MarketOrderExport>,
        marketPriceHistory: List<PriceHistoryExport>,
        combatSessions: List<CombatSessionExport> = emptyList(),
        offlineCombatQueues: List<OfflineCombatQueueExport> = emptyList()
    ) {'''
content = content.replace(anchor1, replacement1, 1)

anchor2 = '''        root.put("marketPriceHistory", marketPriceHistoryArray)

        saveFile.writeText(root.toString())
    }'''
count2 = content.count(anchor2)
assert count2 == 1, f"Expected 1 match for anchor2, found {count2}."
replacement2 = '''        root.put("marketPriceHistory", marketPriceHistoryArray)

        val combatSessionsArray = JSONArray()
        combatSessions.forEach { cs ->
            val obj = JSONObject()
            obj.put("characterId", cs.characterId)
            obj.put("currentHp", cs.currentHp)
            obj.put("maxHp", cs.maxHp)
            obj.put("recoveringUntil", cs.recoveringUntil)
            obj.put("zoneId", cs.zoneId)
            obj.put("sessionState", cs.sessionState)
            obj.put("searchEndsAt", cs.searchEndsAt)
            obj.put("currentMonsterId", cs.currentMonsterId)
            obj.put("currentMonsterHealth", cs.currentMonsterHealth)
            combatSessionsArray.put(obj)
        }
        root.put("combatSessions", combatSessionsArray)

        val offlineCombatQueuesArray = JSONArray()
        offlineCombatQueues.forEach { q ->
            val obj = JSONObject()
            obj.put("characterId", q.characterId)
            obj.put("zoneId", q.zoneId)
            obj.put("startedAt", q.startedAt)
            offlineCombatQueuesArray.put(obj)
        }
        root.put("offlineCombatQueues", offlineCombatQueuesArray)

        saveFile.writeText(root.toString())
    }'''
content = content.replace(anchor2, replacement2, 1)

anchor3 = '''        val lastSaleCheck = mutableListOf<LastSaleCheckExport>()
        val lastSaleCheckArray = root.optJSONArray("lastSaleCheck") ?: JSONArray()
        for (i in 0 until lastSaleCheckArray.length()) {
            val obj = lastSaleCheckArray.getJSONObject(i)
            lastSaleCheck.add(LastSaleCheckExport(characterId = obj.getString("characterId"), lastSaleCheckAt = obj.getString("lastSaleCheckAt")))
        }

        val inventoryItems = mutableListOf<InventorySlotExport>()'''
count3 = content.count(anchor3)
assert count3 == 1, f"Expected 1 match for anchor3, found {count3}."
replacement3 = '''        val lastSaleCheck = mutableListOf<LastSaleCheckExport>()
        val lastSaleCheckArray = root.optJSONArray("lastSaleCheck") ?: JSONArray()
        for (i in 0 until lastSaleCheckArray.length()) {
            val obj = lastSaleCheckArray.getJSONObject(i)
            lastSaleCheck.add(LastSaleCheckExport(characterId = obj.getString("characterId"), lastSaleCheckAt = obj.getString("lastSaleCheckAt")))
        }

        val combatSessions = mutableListOf<CombatSessionExport>()
        val combatSessionsArray = root.optJSONArray("combatSessions") ?: JSONArray()
        for (i in 0 until combatSessionsArray.length()) {
            val obj = combatSessionsArray.getJSONObject(i)
            combatSessions.add(
                CombatSessionExport(
                    characterId = obj.getString("characterId"),
                    currentHp = obj.getInt("currentHp"),
                    maxHp = obj.getInt("maxHp"),
                    recoveringUntil = if (obj.isNull("recoveringUntil")) null else obj.getString("recoveringUntil"),
                    zoneId = if (obj.isNull("zoneId")) null else obj.getString("zoneId"),
                    sessionState = if (obj.isNull("sessionState")) null else obj.getString("sessionState"),
                    searchEndsAt = if (obj.isNull("searchEndsAt")) null else obj.getString("searchEndsAt"),
                    currentMonsterId = if (obj.isNull("currentMonsterId")) null else obj.getString("currentMonsterId"),
                    currentMonsterHealth = obj.getInt("currentMonsterHealth")
                )
            )
        }

        val offlineCombatQueues = mutableListOf<OfflineCombatQueueExport>()
        val offlineCombatQueuesArray = root.optJSONArray("offlineCombatQueues") ?: JSONArray()
        for (i in 0 until offlineCombatQueuesArray.length()) {
            val obj = offlineCombatQueuesArray.getJSONObject(i)
            offlineCombatQueues.add(
                OfflineCombatQueueExport(
                    characterId = obj.getString("characterId"),
                    zoneId = obj.getString("zoneId"),
                    startedAt = obj.getString("startedAt")
                )
            )
        }

        val inventoryItems = mutableListOf<InventorySlotExport>()'''
content = content.replace(anchor3, replacement3, 1)

anchor4 = '''        return SavedGameState(
            accounts, characters, skills, skillingQueues, craftingQueues, lastSeen, lastSaleCheck, inventoryItems, equippedSlots,
            loadoutSettings, marketAccounts, marketOrders, marketPriceHistory
        )
    }
}'''
count4 = content.count(anchor4)
assert count4 == 1, f"Expected 1 match for anchor4, found {count4}."
replacement4 = '''        return SavedGameState(
            accounts, characters, skills, skillingQueues, craftingQueues, lastSeen, lastSaleCheck, inventoryItems, equippedSlots,
            loadoutSettings, marketAccounts, marketOrders, marketPriceHistory, combatSessions, offlineCombatQueues
        )
    }
}'''
content = content.replace(anchor4, replacement4, 1)

anchor5 = '''data class SavedGameState(
    val accounts: List<AccountExport>,
    val characters: List<CharacterExport>,
    val skills: List<SkillExport>,
    val skillingQueues: List<SkillingQueueExport>,
    val craftingQueues: List<CraftingQueueExport>,
    val lastSeen: List<LastSeenExport>,
    val lastSaleCheck: List<LastSaleCheckExport>,
    val inventoryItems: List<InventorySlotExport>,
    val equippedSlots: List<EquippedSlotExport>,
    val loadoutSettings: List<LoadoutSettingsExport>,
    val marketAccounts: List<PlayerEconomyAccountExport>,
    val marketOrders: List<MarketOrderExport>,
    val marketPriceHistory: List<PriceHistoryExport>
)'''
count5 = content.count(anchor5)
assert count5 == 1, f"Expected 1 match for anchor5, found {count5}."
replacement5 = '''data class SavedGameState(
    val accounts: List<AccountExport>,
    val characters: List<CharacterExport>,
    val skills: List<SkillExport>,
    val skillingQueues: List<SkillingQueueExport>,
    val craftingQueues: List<CraftingQueueExport>,
    val lastSeen: List<LastSeenExport>,
    val lastSaleCheck: List<LastSaleCheckExport>,
    val inventoryItems: List<InventorySlotExport>,
    val equippedSlots: List<EquippedSlotExport>,
    val loadoutSettings: List<LoadoutSettingsExport>,
    val marketAccounts: List<PlayerEconomyAccountExport>,
    val marketOrders: List<MarketOrderExport>,
    val marketPriceHistory: List<PriceHistoryExport>,
    val combatSessions: List<CombatSessionExport> = emptyList(),
    val offlineCombatQueues: List<OfflineCombatQueueExport> = emptyList()
)'''
content = content.replace(anchor5, replacement5, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("patch_offline_combat_save_dto.py applied cleanly.")