package com.yourname.idlerpg.data

import android.content.Context
import com.yourname.idlerpg.*
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

class GameStateRepository(private val context: Context) {
    private val saveFile: File get() = File(context.filesDir, "game_state.json")

    fun save(
        accounts: List<AccountExport>,
        characters: List<CharacterExport>,
        skills: List<SkillExport>,
        skillingQueues: List<SkillingQueueExport>,
        craftingQueues: List<CraftingQueueExport>,
        lastSeen: List<LastSeenExport>,
        inventoryItems: List<InventorySlotExport>,
        equippedSlots: List<EquippedSlotExport>,
        marketAccounts: List<PlayerEconomyAccountExport>,
        marketOrders: List<MarketOrderExport>,
        marketPriceHistory: List<PriceHistoryExport>
    ) {
        val root = JSONObject()

        val accountsArray = JSONArray()
        accounts.forEach { acc ->
            val obj = JSONObject()
            obj.put("id", acc.id)
            obj.put("email", acc.email)
            obj.put("username", acc.username)
            obj.put("passwordHash", acc.passwordHash)
            obj.put("passwordSalt", acc.passwordSalt)
            obj.put("createdAt", acc.createdAt)
            obj.put("lastLoginAt", acc.lastLoginAt)
            obj.put("ageBracket", acc.ageBracket)
            obj.put("region", acc.region)
            obj.put("isBanned", acc.isBanned)
            obj.put("banReason", acc.banReason)
            obj.put("mutedUntil", acc.mutedUntil)
            obj.put("subscriptionTier", acc.subscriptionTier)
            obj.put("softCurrency", acc.softCurrency)
            obj.put("premiumCurrency", acc.premiumCurrency)
            accountsArray.put(obj)
        }
        root.put("accounts", accountsArray)

        val charactersArray = JSONArray()
        characters.forEach { char ->
            val obj = JSONObject()
            obj.put("id", char.id)
            obj.put("accountId", char.accountId)
            obj.put("displayName", char.displayName)
            obj.put("avatarId", char.avatarId)
            obj.put("createdAt", char.createdAt)
            obj.put("displayNameLastChangedAt", char.displayNameLastChangedAt)
            obj.put("isMainCharacter", char.isMainCharacter)
            charactersArray.put(obj)
        }
        root.put("characters", charactersArray)

        val skillsArray = JSONArray()
        skills.forEach { skill ->
            val obj = JSONObject()
            obj.put("characterId", skill.characterId)
            obj.put("skillId", skill.skillId)
            obj.put("xp", skill.xp)
            skillsArray.put(obj)
        }
        root.put("skills", skillsArray)

        val queuesArray = JSONArray()
        skillingQueues.forEach { queue ->
            val obj = JSONObject()
            obj.put("characterId", queue.characterId)
            obj.put("skillId", queue.skillId)
            obj.put("itemId", queue.itemId)
            obj.put("secondsPerAction", queue.secondsPerAction)
            obj.put("startedAt", queue.startedAt)
            queuesArray.put(obj)
        }
        root.put("skillingQueues", queuesArray)

        val craftingQueuesArray = JSONArray()
        craftingQueues.forEach { queue ->
            val obj = JSONObject()
            obj.put("characterId", queue.characterId)
            obj.put("itemId", queue.itemId)
            obj.put("secondsPerAction", queue.secondsPerAction)
            obj.put("targetQuantity", queue.targetQuantity)
            obj.put("quantityCompleted", queue.quantityCompleted)
            obj.put("startedAt", queue.startedAt)
            craftingQueuesArray.put(obj)
        }
        root.put("craftingQueues", craftingQueuesArray)

        val lastSeenArray = JSONArray()
        lastSeen.forEach { entry ->
            val obj = JSONObject()
            obj.put("characterId", entry.characterId)
            obj.put("lastSeenAt", entry.lastSeenAt)
            lastSeenArray.put(obj)
        }
        root.put("lastSeen", lastSeenArray)

        val inventoryArray = JSONArray()
        inventoryItems.forEach { entry ->
            val obj = JSONObject()
            obj.put("characterId", entry.characterId)
            obj.put("itemId", entry.itemId)
            obj.put("quantity", entry.quantity)
            inventoryArray.put(obj)
        }
        root.put("inventoryItems", inventoryArray)

        val equippedArray = JSONArray()
        equippedSlots.forEach { entry ->
            val obj = JSONObject()
            obj.put("characterId", entry.characterId)
            obj.put("slot", entry.slot)
            obj.put("itemId", entry.itemId)
            equippedArray.put(obj)
        }
        root.put("equippedSlots", equippedArray)

        val marketAccountsArray = JSONArray()
        marketAccounts.forEach { acc ->
            val obj = JSONObject()
            obj.put("characterId", acc.characterId)
            obj.put("accountId", acc.accountId)
            obj.put("isMainCharacter", acc.isMainCharacter)
            obj.put("currencyBalance", acc.currencyBalance)
            val inventoryObj = JSONObject()
            acc.inventory.forEach { (itemId, qty) -> inventoryObj.put(itemId, qty) }
            obj.put("inventory", inventoryObj)
            marketAccountsArray.put(obj)
        }
        root.put("marketAccounts", marketAccountsArray)

        val marketOrdersArray = JSONArray()
        marketOrders.forEach { order ->
            val obj = JSONObject()
            obj.put("id", order.id)
            obj.put("characterId", order.characterId)
            obj.put("itemId", order.itemId)
            obj.put("side", order.side)
            obj.put("pricePerUnit", order.pricePerUnit)
            obj.put("originalQuantity", order.originalQuantity)
            obj.put("remainingQuantity", order.remainingQuantity)
            obj.put("status", order.status)
            obj.put("createdAt", order.createdAt)
            marketOrdersArray.put(obj)
        }
        root.put("marketOrders", marketOrdersArray)

        val marketPriceHistoryArray = JSONArray()
        marketPriceHistory.forEach { entry ->
            val obj = JSONObject()
            obj.put("itemId", entry.itemId)
            obj.put("pricePerUnit", entry.pricePerUnit)
            obj.put("quantity", entry.quantity)
            obj.put("executedAt", entry.executedAt)
            marketPriceHistoryArray.put(obj)
        }
        root.put("marketPriceHistory", marketPriceHistoryArray)

        saveFile.writeText(root.toString())
    }

    fun load(): SavedGameState? {
        if (!saveFile.exists()) return null

        val root = JSONObject(saveFile.readText())

        val accounts = mutableListOf<AccountExport>()
        val accountsArray = root.optJSONArray("accounts") ?: JSONArray()
        for (i in 0 until accountsArray.length()) {
            val obj = accountsArray.getJSONObject(i)
            accounts.add(
                AccountExport(
                    id = obj.getString("id"), email = obj.getString("email"),
                    username = obj.getString("username"), passwordHash = obj.getString("passwordHash"),
                    passwordSalt = obj.getString("passwordSalt"),
                    createdAt = obj.getString("createdAt"), lastLoginAt = obj.getString("lastLoginAt"),
                    ageBracket = obj.getString("ageBracket"), region = obj.getString("region"),
                    isBanned = obj.getBoolean("isBanned"),
                    banReason = if (obj.isNull("banReason")) null else obj.getString("banReason"),
                    mutedUntil = if (obj.isNull("mutedUntil")) null else obj.getString("mutedUntil"),
                    subscriptionTier = obj.getString("subscriptionTier"),
                    softCurrency = obj.getLong("softCurrency"), premiumCurrency = obj.getLong("premiumCurrency")
                )
            )
        }

        val characters = mutableListOf<CharacterExport>()
        val charactersArray = root.optJSONArray("characters") ?: JSONArray()
        for (i in 0 until charactersArray.length()) {
            val obj = charactersArray.getJSONObject(i)
            characters.add(
                CharacterExport(
                    id = obj.getString("id"), accountId = obj.getString("accountId"),
                    displayName = obj.getString("displayName"), avatarId = obj.getString("avatarId"),
                    createdAt = obj.getString("createdAt"),
                    displayNameLastChangedAt = obj.getString("displayNameLastChangedAt"),
                    isMainCharacter = obj.getBoolean("isMainCharacter")
                )
            )
        }

        val skills = mutableListOf<SkillExport>()
        val skillsArray = root.optJSONArray("skills") ?: JSONArray()
        for (i in 0 until skillsArray.length()) {
            val obj = skillsArray.getJSONObject(i)
            skills.add(
                SkillExport(
                    characterId = obj.getString("characterId"),
                    skillId = obj.getString("skillId"),
                    xp = obj.getLong("xp")
                )
            )
        }

        val skillingQueues = mutableListOf<SkillingQueueExport>()
        val queuesArray = root.optJSONArray("skillingQueues") ?: JSONArray()
        for (i in 0 until queuesArray.length()) {
            val obj = queuesArray.getJSONObject(i)
            skillingQueues.add(
                SkillingQueueExport(
                    characterId = obj.getString("characterId"),
                    skillId = obj.getString("skillId"),
                    itemId = obj.getString("itemId"),
                    secondsPerAction = obj.getLong("secondsPerAction"),
                    startedAt = obj.getString("startedAt")
                )
            )
        }

        val craftingQueues = mutableListOf<CraftingQueueExport>()
        val craftingQueuesArray = root.optJSONArray("craftingQueues") ?: JSONArray()
        for (i in 0 until craftingQueuesArray.length()) {
            val obj = craftingQueuesArray.getJSONObject(i)
            craftingQueues.add(
                CraftingQueueExport(
                    characterId = obj.getString("characterId"),
                    itemId = obj.getString("itemId"),
                    secondsPerAction = obj.getLong("secondsPerAction"),
                    targetQuantity = if (obj.isNull("targetQuantity")) null else obj.getInt("targetQuantity"),
                    quantityCompleted = obj.getInt("quantityCompleted"),
                    startedAt = obj.getString("startedAt")
                )
            )
        }

        val lastSeen = mutableListOf<LastSeenExport>()
        val lastSeenArray = root.optJSONArray("lastSeen") ?: JSONArray()
        for (i in 0 until lastSeenArray.length()) {
            val obj = lastSeenArray.getJSONObject(i)
            lastSeen.add(LastSeenExport(characterId = obj.getString("characterId"), lastSeenAt = obj.getString("lastSeenAt")))
        }

        val inventoryItems = mutableListOf<InventorySlotExport>()
        val inventoryArray = root.optJSONArray("inventoryItems") ?: JSONArray()
        for (i in 0 until inventoryArray.length()) {
            val obj = inventoryArray.getJSONObject(i)
            inventoryItems.add(
                InventorySlotExport(
                    characterId = obj.getString("characterId"),
                    itemId = obj.getString("itemId"),
                    quantity = obj.getInt("quantity")
                )
            )
        }

        val equippedSlots = mutableListOf<EquippedSlotExport>()
        val equippedArray = root.optJSONArray("equippedSlots") ?: JSONArray()
        for (i in 0 until equippedArray.length()) {
            val obj = equippedArray.getJSONObject(i)
            equippedSlots.add(
                EquippedSlotExport(
                    characterId = obj.getString("characterId"),
                    slot = obj.getString("slot"),
                    itemId = obj.getString("itemId")
                )
            )
        }

        val marketAccounts = mutableListOf<PlayerEconomyAccountExport>()
        val marketAccountsArray = root.optJSONArray("marketAccounts") ?: JSONArray()
        for (i in 0 until marketAccountsArray.length()) {
            val obj = marketAccountsArray.getJSONObject(i)
            val inventoryObj = obj.optJSONObject("inventory") ?: JSONObject()
            val inventory = mutableMapOf<String, Int>()
            inventoryObj.keys().forEach { key -> inventory[key] = inventoryObj.getInt(key) }
            marketAccounts.add(
                PlayerEconomyAccountExport(
                    characterId = obj.getString("characterId"),
                    accountId = obj.getString("accountId"),
                    isMainCharacter = obj.getBoolean("isMainCharacter"),
                    currencyBalance = obj.getLong("currencyBalance"),
                    inventory = inventory
                )
            )
        }

        val marketOrders = mutableListOf<MarketOrderExport>()
        val marketOrdersArray = root.optJSONArray("marketOrders") ?: JSONArray()
        for (i in 0 until marketOrdersArray.length()) {
            val obj = marketOrdersArray.getJSONObject(i)
            marketOrders.add(
                MarketOrderExport(
                    id = obj.getString("id"),
                    characterId = obj.getString("characterId"),
                    itemId = obj.getString("itemId"),
                    side = obj.getString("side"),
                    pricePerUnit = obj.getLong("pricePerUnit"),
                    originalQuantity = obj.getInt("originalQuantity"),
                    remainingQuantity = obj.getInt("remainingQuantity"),
                    status = obj.getString("status"),
                    createdAt = obj.getString("createdAt")
                )
            )
        }

        val marketPriceHistory = mutableListOf<PriceHistoryExport>()
        val marketPriceHistoryArray = root.optJSONArray("marketPriceHistory") ?: JSONArray()
        for (i in 0 until marketPriceHistoryArray.length()) {
            val obj = marketPriceHistoryArray.getJSONObject(i)
            marketPriceHistory.add(
                PriceHistoryExport(
                    itemId = obj.getString("itemId"),
                    pricePerUnit = obj.getLong("pricePerUnit"),
                    quantity = obj.getInt("quantity"),
                    executedAt = obj.getString("executedAt")
                )
            )
        }

        return SavedGameState(
            accounts, characters, skills, skillingQueues, craftingQueues, lastSeen, inventoryItems, equippedSlots,
            marketAccounts, marketOrders, marketPriceHistory
        )
    }
}

data class SavedGameState(
    val accounts: List<AccountExport>,
    val characters: List<CharacterExport>,
    val skills: List<SkillExport>,
    val skillingQueues: List<SkillingQueueExport>,
    val craftingQueues: List<CraftingQueueExport>,
    val lastSeen: List<LastSeenExport>,
    val inventoryItems: List<InventorySlotExport>,
    val equippedSlots: List<EquippedSlotExport>,
    val marketAccounts: List<PlayerEconomyAccountExport>,
    val marketOrders: List<MarketOrderExport>,
    val marketPriceHistory: List<PriceHistoryExport>
)
