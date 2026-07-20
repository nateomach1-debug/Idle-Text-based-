package com.yourname.idlerpg

import java.time.Duration
import java.time.Instant
import java.util.UUID

// =========================================================
// DOMAIN MODELS
// =========================================================

enum class AgeBracket { UNDER_13, TEEN_13_17, ADULT_18_PLUS }

enum class SubscriptionTier { NONE, QOL_SUBSCRIBER }

data class Account(
    val id: String,
    val email: String,
    val username: String,
    private var passwordHash: String,
    val createdAt: Instant,
    var lastLoginAt: Instant,
    var ageBracket: AgeBracket,
    var region: String,
    var isBanned: Boolean = false,
    var banReason: String? = null,
    var mutedUntil: Instant? = null,
    var subscriptionTier: SubscriptionTier = SubscriptionTier.NONE,
    var softCurrency: Long = 0,
    var premiumCurrency: Long = 0
) {
    fun isMuted(now: Instant = Instant.now()): Boolean = mutedUntil?.isAfter(now) == true
    internal fun exposePasswordHashForExport(): String = passwordHash
}

data class Character(
    val id: String,
    val accountId: String,
    var displayName: String,
    var avatarId: String,
    val createdAt: Instant,
    var displayNameLastChangedAt: Instant,
    var isMainCharacter: Boolean = false // renamed from isMarketActive per Economy & Market module
)

object AvatarCatalog {
    val presets = listOf("knight", "mage", "archer", "rogue", "cleric", "blacksmith")
    fun isValid(avatarId: String) = presets.contains(avatarId)
}

// =========================================================
// SERVICE LAYER
// (ServiceResult now comes from SharedTypes.kt -- no longer defined here.)
// =========================================================

class AccountService {
    private val accountsById = mutableMapOf<String, Account>()
    private val accountsByUsername = mutableMapOf<String, String>()
    private val accountsByEmail = mutableMapOf<String, String>()
    private val charactersById = mutableMapOf<String, Character>()
    private val charactersByAccountId = mutableMapOf<String, MutableList<String>>()

    private val bannedWords = setOf("badword1", "badword2")

    private val displayNameChangeCooldown: Duration = Duration.ofDays(30)

    fun createAccount(
        email: String,
        username: String,
        password: String,
        ageBracket: AgeBracket,
        region: String
    ): ServiceResult<Account> {
        val normalizedUsername = username.trim().lowercase()
        val normalizedEmail = email.trim().lowercase()

        if (username.isBlank() || username.length < 3 || username.length > 20) {
            return ServiceResult.Failure("Username must be between 3 and 20 characters.")
        }
        if (containsBannedWord(normalizedUsername)) {
            return ServiceResult.Failure("Username contains a disallowed word.")
        }
        if (accountsByUsername.containsKey(normalizedUsername)) {
            return ServiceResult.Failure("Username is already taken.")
        }
        if (accountsByEmail.containsKey(normalizedEmail)) {
            return ServiceResult.Failure("An account already exists for this email.")
        }
        if (password.length < 8) {
            return ServiceResult.Failure("Password must be at least 8 characters.")
        }

        val now = Instant.now()
        val account = Account(
            id = UUID.randomUUID().toString(),
            email = email,
            username = username,
            passwordHash = hashPassword(password),
            createdAt = now,
            lastLoginAt = now,
            ageBracket = ageBracket,
            region = region
        )

        accountsById[account.id] = account
        accountsByUsername[normalizedUsername] = account.id
        accountsByEmail[normalizedEmail] = account.id

        return ServiceResult.Success(account)
    }

    fun createCharacter(accountId: String, displayName: String, avatarId: String): ServiceResult<Character> {
        val account = accountsById[accountId] ?: return ServiceResult.Failure("Account not found.")

        if (account.isBanned) {
            return ServiceResult.Failure("This account is banned and cannot create characters.")
        }
        if (displayName.isBlank() || displayName.length < 3 || displayName.length > 16) {
            return ServiceResult.Failure("Display name must be between 3 and 16 characters.")
        }
        if (containsBannedWord(displayName.lowercase())) {
            return ServiceResult.Failure("Display name contains a disallowed word.")
        }
        if (!AvatarCatalog.isValid(avatarId)) {
            return ServiceResult.Failure("Avatar '" + avatarId + "' is not a valid preset.")
        }

        val now = Instant.now()
        val character = Character(
            id = UUID.randomUUID().toString(),
            accountId = accountId,
            displayName = displayName,
            avatarId = avatarId,
            createdAt = now,
            displayNameLastChangedAt = now
        )

        charactersById[character.id] = character
        charactersByAccountId.getOrPut(accountId) { mutableListOf() }.add(character.id)

        return ServiceResult.Success(character)
    }

    fun changeDisplayName(
        characterId: String,
        newName: String,
        now: Instant = Instant.now()
    ): ServiceResult<Character> {
        val character = charactersById[characterId] ?: return ServiceResult.Failure("Character not found.")

        val elapsed = Duration.between(character.displayNameLastChangedAt, now)
        if (elapsed < displayNameChangeCooldown) {
            val daysRemaining = (displayNameChangeCooldown - elapsed).toDays() + 1
            return ServiceResult.Failure("Display name can be changed again in " + daysRemaining + " day(s).")
        }
        if (newName.isBlank() || newName.length < 3 || newName.length > 16) {
            return ServiceResult.Failure("Display name must be between 3 and 16 characters.")
        }
        if (containsBannedWord(newName.lowercase())) {
            return ServiceResult.Failure("Display name contains a disallowed word.")
        }

        character.displayName = newName
        character.displayNameLastChangedAt = now
        return ServiceResult.Success(character)
    }

    /** Enforces the "one Main character per account" rule used by Economy & Market. */
    fun setMainCharacter(characterId: String): ServiceResult<Character> {
        val character = charactersById[characterId] ?: return ServiceResult.Failure("Character not found.")
        val siblings = charactersByAccountId[character.accountId].orEmpty().mapNotNull { charactersById[it] }
        siblings.forEach { it.isMainCharacter = false }
        character.isMainCharacter = true
        return ServiceResult.Success(character)
    }

    fun recordLogin(accountId: String, now: Instant = Instant.now()): ServiceResult<Account> {
        val account = accountsById[accountId] ?: return ServiceResult.Failure("Account not found.")
        account.lastLoginAt = now
        return ServiceResult.Success(account)
    }

    fun banAccount(accountId: String, reason: String): ServiceResult<Account> {
        val account = accountsById[accountId] ?: return ServiceResult.Failure("Account not found.")
        account.isBanned = true
        account.banReason = reason
        return ServiceResult.Success(account)
    }

    fun muteAccount(accountId: String, duration: Duration, now: Instant = Instant.now()): ServiceResult<Account> {
        val account = accountsById[accountId] ?: return ServiceResult.Failure("Account not found.")
        account.mutedUntil = now.plus(duration)
        return ServiceResult.Success(account)
    }

    fun addCurrency(accountId: String, soft: Long = 0, premium: Long = 0): ServiceResult<Account> {
        val account = accountsById[accountId] ?: return ServiceResult.Failure("Account not found.")
        if (soft < 0 || premium < 0) return ServiceResult.Failure("Currency amounts cannot be negative.")
        account.softCurrency += soft
        account.premiumCurrency += premium
        return ServiceResult.Success(account)
    }

    fun charactersFor(accountId: String): List<Character> =
        charactersByAccountId[accountId]?.mapNotNull { charactersById[it] } ?: emptyList()

    private fun containsBannedWord(text: String): Boolean = bannedWords.any { text.contains(it) }

    private fun hashPassword(password: String): String {
        // STUB ONLY -- a real backend must use bcrypt/argon2 with a per-user salt.
        return "hashed:" + password
    }
    package com.yourname.idlerpg.data

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
}
