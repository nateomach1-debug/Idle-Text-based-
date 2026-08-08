package com.yourname.idlerpg

import java.time.Duration
import java.time.Instant
import java.util.UUID
import java.security.SecureRandom
import java.security.spec.KeySpec
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.PBEKeySpec
import java.util.Base64

enum class AgeBracket { UNDER_13, TEEN_13_17, ADULT_18_PLUS }

enum class SubscriptionTier { NONE, QOL_SUBSCRIBER }

data class Account(
    val id: String,
    val email: String,
    val username: String,
    private var passwordHash: String,
private var passwordSalt: String, // Base64-encoded
    val createdAt: Instant,
    var lastLoginAt: Instant,
    var ageBracket: AgeBracket,
    var region: String,
    var isBanned: Boolean = false,
    var banReason: String? = null,
    var mutedUntil: Instant? = null,
    var subscriptionTier: SubscriptionTier = SubscriptionTier.NONE,
    var premiumCurrency: Long = 0
) {
    fun isMuted(now: Instant = Instant.now()): Boolean = mutedUntil?.isAfter(now) == true
    internal fun exposePasswordHashForExport(): String = passwordHash
    internal fun exposePasswordSaltForExport(): String = passwordSalt
}

data class Character(
    val id: String,
    val accountId: String,
    var displayName: String,
    var avatarId: String,
    val createdAt: Instant,
    var displayNameLastChangedAt: Instant,
    var isMainCharacter: Boolean = false
)

object AvatarCatalog {
    val presets = listOf("knight", "mage", "archer", "rogue", "cleric", "blacksmith")
    fun isValid(avatarId: String) = presets.contains(avatarId)
}

data class AccountExport(
    val id: String, val email: String, val username: String, val passwordHash: String, val passwordSalt: String,
    val createdAt: String, val lastLoginAt: String, val ageBracket: String, val region: String,
    val isBanned: Boolean, val banReason: String?, val mutedUntil: String?,
    val subscriptionTier: String, val premiumCurrency: Long
)

data class CharacterExport(
    val id: String, val accountId: String, val displayName: String, val avatarId: String,
    val createdAt: String, val displayNameLastChangedAt: String, val isMainCharacter: Boolean
)

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
        val salt = generateSalt()
        val account = Account(
            id = UUID.randomUUID().toString(),
            email = email,
            username = username,
            passwordHash = hashPassword(password, salt),
            passwordSalt = Base64.getEncoder().encodeToString(salt),
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

    fun addCurrency(accountId: String, premium: Long = 0): ServiceResult<Account> {
        val account = accountsById[accountId] ?: return ServiceResult.Failure("Account not found.")
        if (premium < 0) return ServiceResult.Failure("Currency amounts cannot be negative.")
        account.premiumCurrency += premium
        return ServiceResult.Success(account)
    }

    fun charactersFor(accountId: String): List<Character> =
        charactersByAccountId[accountId]?.mapNotNull { charactersById[it] } ?: emptyList()

    fun login(email: String, password: String): ServiceResult<Account> {
        val normalizedEmail = email.trim().lowercase()
        val accountId = accountsByEmail[normalizedEmail]
            ?: return ServiceResult.Failure("No account found with that email.")
        val account = accountsById.getValue(accountId)
        if (account.isBanned) {
            return ServiceResult.Failure("This account is banned.")
        }
        val salt = Base64.getDecoder().decode(account.exposePasswordSaltForExport())
        if (!verifyPassword(password, salt, account.exposePasswordHashForExport())) {
            return ServiceResult.Failure("Incorrect password.")
        }
        account.lastLoginAt = Instant.now()
        return ServiceResult.Success(account)
    }

    fun accountById(accountId: String): Account? = accountsById[accountId]

    private fun containsBannedWord(text: String): Boolean = bannedWords.any { text.contains(it) }

    private fun hashPassword(password: String, salt: ByteArray): String {
    val spec: KeySpec = PBEKeySpec(password.toCharArray(), salt, 120_000, 256)
    val factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
    val hash = factory.generateSecret(spec).encoded
    return Base64.getEncoder().encodeToString(hash)
}

private fun generateSalt(): ByteArray {
    val salt = ByteArray(16)
    SecureRandom().nextBytes(salt)
    return salt
}

private fun verifyPassword(password: String, salt: ByteArray, expectedHash: String): Boolean {
    return hashPassword(password, salt) == expectedHash
}

    fun exportAllAccounts(): List<AccountExport> = accountsById.values.map {
        AccountExport(
            it.id, it.email, it.username, it.exposePasswordHashForExport(), it.exposePasswordSaltForExport(),
            it.createdAt.toString(), it.lastLoginAt.toString(), it.ageBracket.name, it.region,
            it.isBanned, it.banReason, it.mutedUntil?.toString(),
            it.subscriptionTier.name, it.premiumCurrency
        )
    }

    fun exportAllCharacters(): List<CharacterExport> = charactersById.values.map {
        CharacterExport(
            it.id, it.accountId, it.displayName, it.avatarId,
            it.createdAt.toString(), it.displayNameLastChangedAt.toString(), it.isMainCharacter
        )
    }

    fun restoreAccount(export: AccountExport) {
        val account = Account(
            id = export.id, email = export.email, username = export.username,
            passwordHash = export.passwordHash, passwordSalt = export.passwordSalt,
            createdAt = Instant.parse(export.createdAt), lastLoginAt = Instant.parse(export.lastLoginAt),
            ageBracket = AgeBracket.valueOf(export.ageBracket), region = export.region,
            isBanned = export.isBanned, banReason = export.banReason,
            mutedUntil = export.mutedUntil?.let { Instant.parse(it) },
            subscriptionTier = SubscriptionTier.valueOf(export.subscriptionTier),
            premiumCurrency = export.premiumCurrency
        )
        accountsById[account.id] = account
        accountsByUsername[account.username.lowercase()] = account.id
        accountsByEmail[account.email.lowercase()] = account.id
    }

    fun restoreCharacter(export: CharacterExport) {
        val character = Character(
            id = export.id, accountId = export.accountId, displayName = export.displayName,
            avatarId = export.avatarId, createdAt = Instant.parse(export.createdAt),
            displayNameLastChangedAt = Instant.parse(export.displayNameLastChangedAt),
            isMainCharacter = export.isMainCharacter
        )
        charactersById[character.id] = character
        val siblingIds = charactersByAccountId.getOrPut(character.accountId) { mutableListOf() }
        if (!siblingIds.contains(character.id)) {
            siblingIds.add(character.id)
        }
    }
}
