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
}

data class Character(
    val id: String,
    val accountId: String,
    var displayName: String,
    var avatarId: String,
    val createdAt: Instant,
    var displayNameLastChangedAt: Instant,
    var isMarketActive: Boolean = false
)

object AvatarCatalog {
    val presets = listOf("knight", "mage", "archer", "rogue", "cleric", "blacksmith")
    fun isValid(avatarId: String) = presets.contains(avatarId)
}

// =========================================================
// RESULT TYPE
// =========================================================

sealed class ServiceResult<out T> {
    data class Success<T>(val value: T) : ServiceResult<T>()
    data class Failure(val reason: String) : ServiceResult<Nothing>()
}

// =========================================================
// SERVICE LAYER
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

    fun setMarketActive(characterId: String): ServiceResult<Character> {
        val character = charactersById[characterId] ?: return ServiceResult.Failure("Character not found.")
        val siblings = charactersByAccountId[character.accountId].orEmpty().mapNotNull { charactersById[it] }
        siblings.forEach { it.isMarketActive = false }
        character.isMarketActive = true
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
        return "hashed:" + password
    }
}

// =========================================================
// DEMO
// =========================================================

fun main() {
    val service = AccountService()

    println("=== Creating accounts ===")
    val alice = service.createAccount(
        email = "alice@example.com",
        username = "AliceAdventurer",
        password = "hunter22bunny",
        ageBracket = AgeBracket.ADULT_18_PLUS,
        region = "US"
    )
    printResult("Create Alice", alice)

    val duplicate = service.createAccount(
        email = "alice2@example.com",
        username = "aliceadventurer",
        password = "anotherpassword",
        ageBracket = AgeBracket.ADULT_18_PLUS,
        region = "US"
    )
    printResult("Create duplicate username", duplicate)

    println("")
    println("=== Creating a character ===")
    val aliceAccount = (alice as ServiceResult.Success).value
    val charResult = service.createCharacter(aliceAccount.id, "Lyra", "mage")
    printResult("Create character Lyra", charResult)

    println("")
    println("=== Invalid avatar ===")
    printResult("Invalid avatar attempt", service.createCharacter(aliceAccount.id, "Thorne", "dragon-rider"))

    println("")
    println("=== Display name change, immediate (should fail: cooldown) ===")
    val lyra = (charResult as ServiceResult.Success).value
    printResult("Immediate rename attempt", service.changeDisplayName(lyra.id, "Starfall"))

    println("")
    println("=== Display name change, after 31 simulated days ===")
    val futureTime = lyra.displayNameLastChangedAt.plus(Duration.ofDays(31))
    printResult("Rename after cooldown", service.changeDisplayName(lyra.id, "Starfall", now = futureTime))

    println("")
    println("=== Adding currency ===")
    printResult("Add currency", service.addCurrency(aliceAccount.id, soft = 500, premium = 10))

    println("")
    println("=== Marking Lyra as the market-active character ===")
    printResult("Set market-active", service.setMarketActive(lyra.id))

    println("")
    println("=== Listing Alice's characters ===")
    service.charactersFor(aliceAccount.id).forEach {
        println("- " + it.displayName + " (" + it.avatarId + ") marketActive=" + it.isMarketActive)
    }

    println("")
    println("=== Banning the account ===")
    printResult("Ban Alice", service.banAccount(aliceAccount.id, "Testing ban flow"))
    printResult(
        "Create character on banned account (should fail)",
        service.createCharacter(aliceAccount.id, "SecondChar", "rogue")
    )
}

fun <T> printResult(label: String, result: ServiceResult<T>) {
    when (result) {
        is ServiceResult.Success -> println("[OK] " + label + " -> " + result.value)
        is ServiceResult.Failure -> println("[FAIL] " + label + " -> " + result.reason)
    }
}
