package com.yourname.idlerpg

import java.time.Duration
import java.time.Instant
import kotlin.random.Random

data class Weapon(
    val name: String,
    val style: CombatStyle,
    val attackSpeedSeconds: Double,
    val baseAccuracy: Int,
    val baseMaxHit: Int
)

data class Spell(
    val name: String,
    val levelRequired: Int,
    val attackSpeedSeconds: Double,
    val baseAccuracy: Int,
    val baseMaxHit: Int
)

object SpellBook {
    private val spells = listOf(
        Spell("Spark Bolt", levelRequired = 1, attackSpeedSeconds = 2.4, baseAccuracy = 20, baseMaxHit = 4),
        Spell("Flame Lance", levelRequired = 15, attackSpeedSeconds = 2.8, baseAccuracy = 28, baseMaxHit = 8),
        Spell("Frost Spike", levelRequired = 30, attackSpeedSeconds = 3.0, baseAccuracy = 35, baseMaxHit = 12)
    )

    fun availableSpells(magicLevel: Int): List<Spell> = spells.filter { it.levelRequired <= magicLevel }
}

// Which combat skills a character can select to train, based on the equipped
// weapon's style. Defense is always trainable regardless of weapon style,
// matching the classic "defensive style still uses your main weapon" model.
object CombatSkillRules {
    fun allowedTrainingSkills(style: CombatStyle): List<SkillType> = when (style) {
        CombatStyle.MELEE -> listOf(SkillType.ATTACK, SkillType.STRENGTH, SkillType.DEFENSE)
        CombatStyle.RANGED -> listOf(SkillType.ARCHERY, SkillType.DEFENSE)
        CombatStyle.MAGIC -> listOf(SkillType.MAGIC, SkillType.DEFENSE)
    }
}

data class LootEntry(val itemId: String, val minQty: Int, val maxQty: Int, val dropChancePercent: Double)

data class Monster(
    val id: String,
    val name: String,
    val levelRequirement: Int,
    val maxHealth: Int,
    val defenseRating: Int,
    val mainLootTable: List<LootEntry>,
    val rareLootTable: List<LootEntry>
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
        ),
        Zone(
            id = "farmland_outskirts",
            name = "Farmland Outskirts",
            levelRequirement = 1,
            monsters = listOf(
                Monster(
                    id = "wild_cow",
                    name = "Wild Cow",
                    levelRequirement = 1,
                    maxHealth = 20,
                    defenseRating = 3,
                    mainLootTable = listOf(
                        LootEntry("cowhide", 1, 1, 65.0),
                        LootEntry("raw_beef", 1, 2, 65.0)
                    ),
                    rareLootTable = listOf()
                ),
                Monster(
                    id = "feral_chicken",
                    name = "Feral Chicken",
                    levelRequirement = 1,
                    maxHealth = 12,
                    defenseRating = 1,
                    mainLootTable = listOf(
                        LootEntry("raw_chicken", 1, 1, 65.0),
                        LootEntry("feathers", 1, 5, 70.0)
                    ),
                    rareLootTable = listOf()
                )
            )
        ),
        Zone(
            id = "serpent_marsh",
            name = "Serpent Marsh",
            levelRequirement = 10,
            monsters = listOf(
                Monster(
                    id = "marsh_snake",
                    name = "Marsh Snake",
                    levelRequirement = 10,
                    maxHealth = 35,
                    defenseRating = 10,
                    mainLootTable = listOf(
                        LootEntry("snake_hide", 1, 1, 55.0)
                    ),
                    rareLootTable = listOf()
                )
            )
        ),
        Zone(
            id = "gem_cavern",
            name = "Gem Cavern",
            levelRequirement = 15,
            monsters = listOf(
                Monster(
                    id = "gem_hoarder",
                    name = "Gem Hoarder",
                    levelRequirement = 15,
                    maxHealth = 45,
                    defenseRating = 15,
                    mainLootTable = listOf(
                        LootEntry("uncut_gemstone", 1, 2, 45.0)
                    ),
                    rareLootTable = listOf(
                        LootEntry("uncut_opal", 1, 1, 8.0),
                        LootEntry("uncut_jade", 1, 1, 6.0),
                        LootEntry("uncut_red_topaz", 1, 1, 5.0),
                        LootEntry("uncut_sapphire", 1, 1, 4.0),
                        LootEntry("uncut_emerald", 1, 1, 3.0),
                        LootEntry("uncut_ruby", 1, 1, 2.0),
                        LootEntry("uncut_diamond", 1, 1, 1.2),
                        LootEntry("uncut_dragonstone", 1, 1, 0.6),
                        LootEntry("uncut_onyx", 1, 1, 0.3),
                        LootEntry("uncut_zenyte", 1, 1, 0.15),
                        LootEntry("uncut_celestial_crystal", 1, 1, 0.05)
                    )
                )
            )
        ),
        Zone(
            id = "dragons_lair",
            name = "Dragon's Lair",
            levelRequirement = 60,
            monsters = listOf(
                Monster(
                    id = "green_dragon",
                    name = "Green Dragon",
                    levelRequirement = 60,
                    maxHealth = 220,
                    defenseRating = 65,
                    mainLootTable = listOf(
                        LootEntry("green_dragonhide", 1, 1, 60.0)
                    ),
                    rareLootTable = listOf()
                ),
                Monster(
                    id = "blue_dragon",
                    name = "Blue Dragon",
                    levelRequirement = 65,
                    maxHealth = 260,
                    defenseRating = 75,
                    mainLootTable = listOf(
                        LootEntry("blue_dragonhide", 1, 1, 55.0)
                    ),
                    rareLootTable = listOf()
                )
            )
        )
    )

    fun zonesAvailableAt(level: Int): List<Zone> = zones.filter { it.levelRequirement <= level }
}

data class CombatLoadout(
    val style: CombatStyle,
    val trainingSkill: SkillType,
    val equippedWeapon: Weapon?,
    val equippedSpell: Spell?,
    val autoHealThresholdPercent: Int,
    val autoFleeThresholdPercent: Int
)

enum class SessionState { SEARCHING, PAUSED, IN_COMBAT }

class CombatSession(
    val zone: Zone,
    var state: SessionState = SessionState.SEARCHING,
    var searchEndsAt: Instant? = null,
    var currentMonster: Monster? = null,
    var currentMonsterHealth: Int = 0
)

class RecoveryStatus {
    var recoveringUntil: Instant? = null

    fun isRecovering(now: Instant = Instant.now()): Boolean {
        val until = recoveringUntil ?: return false
        return now.isBefore(until)
    }
}

class CharacterCombatState(
    var currentHp: Int,
    var maxHp: Int,
    val recovery: RecoveryStatus = RecoveryStatus(),
    var session: CombatSession? = null,
    val lootPool: MutableList<LootEntry> = mutableListOf(),
    var pendingCoins: Long = 0L
)

object CoinDropTable {
    fun rollCoins(monsterLevel: Int): Long {
        val base = (monsterLevel * 3).coerceAtLeast(1)
        val variance = (base * 0.4).toInt().coerceAtLeast(1)
        val roll = base - (variance / 2) + Random.nextInt(variance + 1)
        return roll.toLong().coerceAtLeast(1L)
    }
}

data class AttackResult(
    val didHit: Boolean,
    val damageDealt: Int,
    val monsterHpRemaining: Int,
    val monsterDefeated: Boolean
)

class CombatService {
    private val recoveryDuration: Duration = Duration.ofSeconds(600)
    private val states: MutableMap<String, CharacterCombatState> = mutableMapOf()

    fun stateFor(characterId: String, maxHp: Int = 100): CharacterCombatState =
        states.getOrPut(characterId) { CharacterCombatState(currentHp = maxHp, maxHp = maxHp) }

    // trainingSkillLevel must be the level of whichever SkillType the character
    // currently has selected to train (loadout.trainingSkill) - NOT a blended
    // "character level". Each combat skill unlocks zones independently.
    fun enterZone(characterId: String, zoneId: String, trainingSkillLevel: Int): ServiceResult<CombatSession> {
        val state = stateFor(characterId)
        if (state.recovery.isRecovering()) {
            return ServiceResult.Failure("Cannot enter combat while recovering.")
        }
        val zone = ZoneCatalog.zones.find { it.id == zoneId }
            ?: return ServiceResult.Failure("Zone not found.")
        if (zone.levelRequirement > trainingSkillLevel) {
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

        val searchSeconds = Random.nextInt(3, 11)
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

    fun canChangeEquipment(characterId: String, slot: EquipmentSlot, now: Instant = Instant.now()): Boolean {
        if (slot == EquipmentSlot.TOOL) return true

        val state = stateFor(characterId)

        if (state.recovery.isRecovering(now) && slot == EquipmentSlot.WEAPON) return false

        val session = state.session ?: return true
        return session.state != SessionState.IN_COMBAT
    }

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

        val hitChancePercent = (attackerAccuracy.toDouble() / (attackerAccuracy + monster.defenseRating)) * 100.0
        val didHit = Random.nextDouble(0.0, 100.0) < hitChancePercent

        if (!didHit) {
            return ServiceResult.Success(
                AttackResult(didHit = false, damageDealt = 0, monsterHpRemaining = session.currentMonsterHealth, monsterDefeated = false)
            )
        }

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
        state.pendingCoins += CoinDropTable.rollCoins(monster.levelRequirement)
    }

    fun collectLoot(characterId: String): ServiceResult<List<LootEntry>> {
        val state = stateFor(characterId)
        val collected = state.lootPool.toList()
        state.lootPool.clear()
        return ServiceResult.Success(collected)
    }

    fun collectCoins(characterId: String): Long {
        val state = stateFor(characterId)
        val collected = state.pendingCoins
        state.pendingCoins = 0L
        return collected
    }

    fun applyDamageToCharacter(characterId: String, damage: Int, now: Instant = Instant.now()): ServiceResult<CharacterCombatState> {
        val state = stateFor(characterId)
        state.currentHp = (state.currentHp - damage).coerceAtLeast(0)

        if (state.currentHp <= 0) {
            state.recovery.recoveringUntil = now.plus(recoveryDuration)
            state.session = null
        }
        return ServiceResult.Success(state)
    }

    fun healCharacter(characterId: String, amount: Int): ServiceResult<CharacterCombatState> {
        val state = stateFor(characterId)
        state.currentHp = (state.currentHp + amount).coerceAtMost(state.maxHp)
        return ServiceResult.Success(state)
    }

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
