import java.time.Duration
import java.time.Instant
import kotlin.random.Random

// =========================================================
// COMBAT STYLE & SKILLS
// (References SkillType from the Skill & Progression module --
//  assumed available in the same project once combined.)
// =========================================================

enum class CombatStyle { MELEE, RANGED, MAGIC }

enum class EquipmentSlot { WEAPON, ARMOR, ACCESSORY }

// =========================================================
// EQUIPMENT (minimal stand-in until the real Items module exists)
// =========================================================

data class Weapon(
    val name: String,
    val style: CombatStyle,
    val attackSpeedSeconds: Double, // time between attacks -- varies per weapon/spell
    val baseAccuracy: Int,
    val baseMaxHit: Int
)

// =========================================================
// SPELLS (Magic-specific, level-gated, lower damage ceiling)
// =========================================================

data class Spell(
    val name: String,
    val levelRequired: Int,
    val attackSpeedSeconds: Double,
    val baseAccuracy: Int,
    val baseMaxHit: Int // intentionally scaled lower than equivalent-level Melee/Ranged weapons
)

object SpellBook {
    private val spells = listOf(
        Spell("Spark Bolt", levelRequired = 1, attackSpeedSeconds = 2.4, baseAccuracy = 20, baseMaxHit = 4),
        Spell("Flame Lance", levelRequired = 15, attackSpeedSeconds = 2.8, baseAccuracy = 28, baseMaxHit = 8),
        Spell("Frost Spike", levelRequired = 30, attackSpeedSeconds = 3.0, baseAccuracy = 35, baseMaxHit = 12)
    )

    /** Only spells the character's Magic level actually qualifies for. */
    fun availableSpells(magicLevel: Int): List<Spell> = spells.filter { it.levelRequired <= magicLevel }
}

// =========================================================
// MONSTERS & ZONES
// =========================================================

data class LootEntry(val itemId: String, val minQty: Int, val maxQty: Int, val dropChancePercent: Double)

data class Monster(
    val id: String,
    val name: String,
    val levelRequirement: Int,
    val maxHealth: Int,
    val defenseRating: Int,
    val mainLootTable: List<LootEntry>,
    val rareLootTable: List<LootEntry> // separate, typically very low dropChancePercent
)

data class Zone(
    val id: String,
    val name: String,
    val levelRequirement: Int,
    val monsters: List<Monster>
)

object ZoneCatalog {
    val zones = listOf(
        Zone(
            id = "goblin_camp",
            name = "Goblin Camp",
            levelRequirement = 1,
            monsters = listOf(
                Monster(
                    id = "goblin_grunt",
                    name = "Goblin Grunt",
                    levelRequirement = 1,
                    maxHealth = 25,
                    defenseRating = 5,
                    mainLootTable = listOf(
                        LootEntry("bone", 1, 1, 60.0),
                        LootEntry("goblin_ear", 1, 2, 40.0)
                    ),
                    rareLootTable = listOf(
                        LootEntry("rusty_dagger", 1, 1, 2.0)
                    )
                )
            )
        ),
        Zone(
            id = "shadow_ruins",
            name = "Shadow Ruins",
            levelRequirement = 20,
            monsters = listOf(
                Monster(
                    id = "wraith",
                    name = "Wraith",
                    levelRequirement = 20,
                    maxHealth = 80,
                    defenseRating = 25,
                    mainLootTable = listOf(
                        LootEntry("ectoplasm", 1, 3, 55.0)
                    ),
                    rareLootTable = listOf(
                        LootEntry("wraith_essence", 1, 1, 0.5)
                    )
                )
            )
        )
    )

    fun zonesAvailableAt(level: Int): List<Zone> = zones.filter { it.levelRequirement <= level }
}

// =========================================================
// LOADOUT CONFIG (set before entering combat)
// =========================================================

data class CombatLoadout(
    val style: CombatStyle,
    val equippedWeapon: Weapon?,       // required if style is MELEE or RANGED
    val equippedSpell: Spell?,         // required if style is MAGIC
    val autoHealThresholdPercent: Int, // e.g. 30 = heal when HP drops to 30%
    val autoFleeThresholdPercent: Int  // e.g. 10 = flee when HP drops to 10%
)

// =========================================================
// COMBAT SESSION STATE (per character, only while in a zone)
// =========================================================

enum class SessionState { SEARCHING, PAUSED, IN_COMBAT }

class CombatSession(
    val zone: Zone,
    var state: SessionState = SessionState.SEARCHING,
    var searchEndsAt: Instant? = null,
    var currentMonster: Monster? = null,
    var currentMonsterHealth: Int = 0
)

// =========================================================
// RECOVERY STATUS (independent, global, blocks WEAPON changes only)
// =========================================================

class RecoveryStatus {
    var recoveringUntil: Instant? = null

    fun isRecovering(now: Instant = Instant.now()): Boolean {
        val until = recoveringUntil ?: return false
        return now.isBefore(until)
    }
}

// =========================================================
// CHARACTER COMBAT STATE (aggregates everything above per character)
// =========================================================

class CharacterCombatState(
    var currentHp: Int,
    var maxHp: Int,
    val recovery: RecoveryStatus = RecoveryStatus(),
    var session: CombatSession? = null,
    val lootPool: MutableList<LootEntry> = mutableListOf() // accumulated, uncollected drops
)

// =========================================================
// RESULT TYPES
// =========================================================

sealed class ServiceResult<out T> {
    data class Success<T>(val value: T) : ServiceResult<T>()
    data class Failure(val reason: String) : ServiceResult<Nothing>()
}

data class AttackResult(
    val didHit: Boolean,
    val damageDealt: Int,
    val monsterHpRemaining: Int,
    val monsterDefeated: Boolean
)

// =========================================================
// COMBAT SERVICE
// =========================================================

class CombatService {
    private val recoveryDuration: Duration = Duration.ofSeconds(600)
    private val states: MutableMap<String, CharacterCombatState> = mutableMapOf()

    fun stateFor(characterId: String, maxHp: Int = 100): CharacterCombatState =
        states.getOrPut(characterId) { CharacterCombatState(currentHp = maxHp, maxHp = maxHp) }

    // ---------------- Zone / searching ----------------

    fun enterZone(characterId: String, zoneId: String, characterLevel: Int): ServiceResult<CombatSession> {
        val state = stateFor(characterId)
        if (state.recovery.isRecovering()) {
            return ServiceResult.Failure("Cannot enter combat while recovering.")
        }
        val zone = ZoneCatalog.zones.find { it.id == zoneId }
            ?: return ServiceResult.Failure("Zone not found.")
        if (zone.levelRequirement > characterLevel) {
            return ServiceResult.Failure("Requires level " + zone.levelRequirement + " to enter " + zone.name + ".")
        }

        val session = CombatSession(zone = zone)
        state.session = session
        return startSearching(characterId)
    }

    fun startSearching(characterId: String, now: Instant = Instant.now()): ServiceResult<CombatSession> {
        val state = stateFor(characterId)
        val session = state.session ?: return ServiceResult.Failure("Not currently in a zone.")
        if (state.recovery.isRecovering(now)) {
            return ServiceResult.Failure("Cannot search while recovering.")
        }

        val searchSeconds = Random.nextInt(3, 11) // 3-10 seconds inclusive
        session.state = SessionState.SEARCHING
        session.searchEndsAt = now.plusSeconds(searchSeconds.toLong())
        session.currentMonster = null
        return ServiceResult.Success(session)
    }

    fun pauseSearching(characterId: String): ServiceResult<CombatSession> {
        val state = stateFor(characterId)
        val session = state.session ?: return ServiceResult.Failure("Not currently in a zone.")
        if (session.state != SessionState.SEARCHING) {
            return ServiceResult.Failure("Can only pause while searching.")
        }
        session.state = SessionState.PAUSED
        return ServiceResult.Success(session)
    }

    /** Call periodically (e.g. by a game loop) to check if the search timer has elapsed. */
    fun resolveSearchIfReady(characterId: String, now: Instant = Instant.now()): ServiceResult<Monster> {
        val state = stateFor(characterId)
        val session = state.session ?: return ServiceResult.Failure("Not currently in a zone.")
        if (session.state != SessionState.SEARCHING) {
            return ServiceResult.Failure("Not currently searching.")
        }
        val endsAt = session.searchEndsAt ?: return ServiceResult.Failure("No active search timer.")
        if (now.isBefore(endsAt)) {
            return ServiceResult.Failure("Search still in progress.")
        }

        val monster = session.zone.monsters.random()
        session.currentMonster = monster
        session.currentMonsterHealth = monster.maxHealth
        session.state = SessionState.IN_COMBAT
        return ServiceResult.Success(monster)
    }

    fun leaveZone(characterId: String): ServiceResult<Unit> {
        val state = stateFor(characterId)
        state.session = null
        return ServiceResult.Success(Unit)
    }

    // ---------------- Equipment (slot-aware locking) ----------------

    /**
     * Recovery locks ONLY the WEAPON slot -- armor/accessories remain changeable
     * even while recovering. IN_COMBAT still locks every slot, regardless of type.
     */
    fun canChangeEquipment(characterId: String, slot: EquipmentSlot, now: Instant = Instant.now()): Boolean {
        val state = stateFor(characterId)

        if (state.recovery.isRecovering(now) && slot == EquipmentSlot.WEAPON) return false

        val session = state.session ?: return true // not in a zone at all -- always changeable
        return session.state != SessionState.IN_COMBAT
    }

    // ---------------- Attack resolution (two-step: hit chance, then damage) ----------------

    fun resolveAttack(
        characterId: String,
        loadout: CombatLoadout,
        attackerAccuracy: Int,
        attackerMaxHit: Int
    ): ServiceResult<AttackResult> {
        val state = stateFor(characterId)
        val session = state.session ?: return ServiceResult.Failure("Not currently in a zone.")
        if (session.state != SessionState.IN_COMBAT) {
            return ServiceResult.Failure("Not currently in combat.")
        }
        val monster = session.currentMonster ?: return ServiceResult.Failure("No active target.")

        // Step 1: hit chance vs. monster defense
        val hitChancePercent = (attackerAccuracy.toDouble() / (attackerAccuracy + monster.defenseRating)) * 100.0
        val didHit = Random.nextDouble(0.0, 100.0) < hitChancePercent

        if (!didHit) {
            return ServiceResult.Success(
                AttackResult(didHit = false, damageDealt = 0, monsterHpRemaining = session.currentMonsterHealth, monsterDefeated = false)
            )
        }

        // Step 2: damage roll, only if the hit landed
        val damage = Random.nextInt(0, attackerMaxHit + 1)
        session.currentMonsterHealth = (session.currentMonsterHealth - damage).coerceAtLeast(0)
        val defeated = session.currentMonsterHealth <= 0

        if (defeated) {
            rollLoot(state, monster)
            session.currentMonster = null
            startSearching(characterId)
        }

        return ServiceResult.Success(
            AttackResult(didHit = true, damageDealt = damage, monsterHpRemaining = session.currentMonsterHealth, monsterDefeated = defeated)
        )
    }

    private fun rollLoot(state: CharacterCombatState, monster: Monster) {
        (monster.mainLootTable + monster.rareLootTable).forEach { entry ->
            if (Random.nextDouble(0.0, 100.0) < entry.dropChancePercent) {
                val qty = Random.nextInt(entry.minQty, entry.maxQty + 1)
                state.lootPool.add(entry.copy(minQty = qty, maxQty = qty))
            }
        }
    }

    fun collectLoot(characterId: String): ServiceResult<List<LootEntry>> {
        val state = stateFor(characterId)
        val collected = state.lootPool.toList()
        state.lootPool.clear()
        return ServiceResult.Success(collected)
    }

    // ---------------- Death & recovery ----------------

    fun applyDamageToCharacter(characterId: String, damage: Int, now: Instant = Instant.now()): ServiceResult<CharacterCombatState> {
        val state = stateFor(characterId)
        state.currentHp = (state.currentHp - damage).coerceAtLeast(0)

        if (state.currentHp <= 0) {
            state.recovery.recoveringUntil = now.plus(recoveryDuration)
            state.session = null // knocked out of whatever zone/fight they were in
        }
        return ServiceResult.Success(state)
    }

    /** Call periodically to check if a recovering character should be restored. */
    fun resolveRecoveryIfReady(characterId: String, now: Instant = Instant.now()): ServiceResult<CharacterCombatState> {
        val state = stateFor(characterId)
        val until = state.recovery.recoveringUntil
            ?: return ServiceResult.Failure("Character is not recovering.")
        if (now.isBefore(until)) {
            return ServiceResult.Failure("Recovery still in progress.")
        }
        state.currentHp = (state.maxHp * 0.5).toInt()
        state.recovery.recoveringUntil = null
        return ServiceResult.Success(state)
    }
}

// =========================================================
// DEMO
// =========================================================

fun main() {
    val combat = CombatService()
    val characterId = "lyra-character-id"
    combat.stateFor(characterId, maxHp = 100)

    println("=== Entering Goblin Camp at level 1 ===")
    printResult(combat.enterZone(characterId, "goblin_camp", characterLevel = 1))

    println("")
    println("=== Equipment check while SEARCHING (all slots should be changeable) ===")
    println("Can change weapon: " + combat.canChangeEquipment(characterId, EquipmentSlot.WEAPON))
    println("Can change armor: " + combat.canChangeEquipment(characterId, EquipmentSlot.ARMOR))
    println("Can change accessory: " + combat.canChangeEquipment(characterId, EquipmentSlot.ACCESSORY))

    println("")
    println("=== Forcing search resolution (simulating time passing) ===")
    val state = combat.stateFor(characterId)
    state.session?.searchEndsAt = Instant.now().minusSeconds(1) // force it to be "ready"
    printResult(combat.resolveSearchIfReady(characterId))

    println("")
    println("=== Equipment check during IN_COMBAT (all slots should be locked) ===")
    println("Can change weapon: " + combat.canChangeEquipment(characterId, EquipmentSlot.WEAPON))
    println("Can change armor: " + combat.canChangeEquipment(characterId, EquipmentSlot.ARMOR))
    println("Can change accessory: " + combat.canChangeEquipment(characterId, EquipmentSlot.ACCESSORY))

    val loadout = CombatLoadout(
        style = CombatStyle.MELEE,
        equippedWeapon = Weapon("Bronze Sword", CombatStyle.MELEE, attackSpeedSeconds = 2.4, baseAccuracy = 40, baseMaxHit = 6),
        equippedSpell = null,
        autoHealThresholdPercent = 30,
        autoFleeThresholdPercent = 10
    )

    println("")
    println("=== Fighting until the monster is defeated ===")
    var defeated = false
    var rounds = 0
    while (!defeated && rounds < 50) {
        val result = combat.resolveAttack(characterId, loadout, attackerAccuracy = 40, attackerMaxHit = 6)
        if (result is ServiceResult.Success) {
            val r = result.value
            println("Round " + (rounds + 1) + ": hit=" + r.didHit + " dmg=" + r.damageDealt + " monsterHp=" + r.monsterHpRemaining)
            defeated = r.monsterDefeated
        }
        rounds++
    }

    println("")
    println("=== Collecting loot pool ===")
    val loot = combat.collectLoot(characterId)
    if (loot is ServiceResult.Success) {
        if (loot.value.isEmpty()) println("No loot dropped this run.")
        loot.value.forEach { println("- " + it.itemId + " x" + it.minQty) }
    }

    println("")
    println("=== Simulating character death and recovery ===")
    combat.applyDamageToCharacter(characterId, damage = 500) // guaranteed lethal
    val postDeath = combat.stateFor(characterId)
    println("HP after lethal damage: " + postDeath.currentHp + " | Recovering: " + postDeath.recovery.isRecovering())

    println("")
    println("=== Equipment check while RECOVERING (weapon locked, armor/accessory free) ===")
    println("Can change weapon: " + combat.canChangeEquipment(characterId, EquipmentSlot.WEAPON))
    println("Can change armor: " + combat.canChangeEquipment(characterId, EquipmentSlot.ARMOR))
    println("Can change accessory: " + combat.canChangeEquipment(characterId, EquipmentSlot.ACCESSORY))

    println("")
    println("=== Attempting recovery resolution too early (should fail) ===")
    printResult(combat.resolveRecoveryIfReady(characterId))

    println("")
    println("=== Attempting recovery resolution after simulating 601 seconds ===")
    val future = Instant.now().plusSeconds(601)
    printResult(combat.resolveRecoveryIfReady(characterId, now = future))
    val postRecovery = combat.stateFor(characterId)
    println("HP after recovery: " + postRecovery.currentHp + " / " + postRecovery.maxHp)

    println("")
    println("=== Equipment check after recovery ends (all slots free again) ===")
    println("Can change weapon: " + combat.canChangeEquipment(characterId, EquipmentSlot.WEAPON))
    println("Can change armor: " + combat.canChangeEquipment(characterId, EquipmentSlot.ARMOR))
    println("Can change accessory: " + combat.canChangeEquipment(characterId, EquipmentSlot.ACCESSORY))
}

fun <T> printResult(result: ServiceResult<T>) {
    when (result) {
        is ServiceResult.Success -> println("[OK] " + result.value)
        is ServiceResult.Failure -> println("[FAIL] " + result.reason)
    }
}
