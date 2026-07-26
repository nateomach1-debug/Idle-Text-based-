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
        skills: List<SkillExport>
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

        return SavedGameState(accounts, characters, skills)
    }
}

data class SavedGameState(
    val accounts: List<AccountExport>,
    val characters: List<CharacterExport>,
    val skills: List<SkillExport>
)
