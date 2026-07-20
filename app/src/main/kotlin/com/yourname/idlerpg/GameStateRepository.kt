package com.yourname.idlerpg.data

import com.yourname.idlerpg.*
import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

// =========================================================
// GAME STATE REPOSITORY
// Saves/loads the whole game's state as one JSON file in the
// app's private internal storage. Survives full app closure --
// this is what makes offline progress calculation possible.
// =========================================================

class GameStateRepository(private val context: Context) {
    private val saveFile: File get() = File(context.filesDir, "game_state.json")

    fun save(accounts: List<AccountExport>, characters: List<CharacterExport>) {
        val root = JSONObject()

        val accountsArray = JSONArray()
        accounts.forEach { acc ->
            val obj = JSONObject()
            obj.put("id", acc.id)
            obj.put("email", acc.email)
            obj.put("username", acc.username)
            obj.put("passwordHash", acc.passwordHash)
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

        return SavedGameState(accounts, characters)
    }
}

data class SavedGameState(
    val accounts: List<AccountExport>,
    val characters: List<CharacterExport>
)
