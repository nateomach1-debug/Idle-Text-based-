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
        lastSeen: List<LastSeenExport>
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

        val lastSeenArray = JSONArray()
        lastSeen.forEach { entry ->
            val obj = JSONObject()
            obj.put("characterId", entry.characterId)
            obj.put("lastSeenAt", entry.lastSeenAt)
            lastSeenArray.put(obj)
        }
        root.put("lastSeen", lastSeenArray)

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

        val lastSeen = mutableListOf<LastSeenExport>()
        val lastSeenArray = root.optJSONArray("lastSeen") ?: JSONArray()
        for (i in 0 until lastSeenArray.length()) {
            val obj = lastSeenArray.getJSONObject(i)
            lastSeen.add(LastSeenExport(characterId = obj.getString("characterId"), lastSeenAt = obj.getString("lastSeenAt")))
        }

        return SavedGameState(accounts, characters, skills, skillingQueues, lastSeen)
    }
}

data class SavedGameState(
    val accounts: List<AccountExport>,
    val characters: List<CharacterExport>,
    val skills: List<SkillExport>,
    val skillingQueues: List<SkillingQueueExport>,
    val lastSeen: List<LastSeenExport>
)
