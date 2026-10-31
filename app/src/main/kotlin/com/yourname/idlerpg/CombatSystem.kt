package com.yourname.idlerpg

import java.time.Duration
import java.time.Instant
import kotlin.random.Random

enum class DamageType { MELEE, RANGED, FIRE, EARTH, WATER, WIND }

// Player-facing label for a damage type (zone screen + monster picker).
fun DamageType.displayName(): String = when (this) {
    DamageType.MELEE -> "Melee"
    DamageType.RANGED -> "Ranged"
    DamageType.FIRE -> "Fire"
    DamageType.EARTH -> "Earth"
    DamageType.WATER -> "Water"
    DamageType.WIND -> "Wind"
}

data class Weapon(
    val name: String,
    val style: CombatStyle,
    val attackSpeedSeconds: Double,
    val baseAccuracy: Int,
    val baseMaxHit: Int,
    val elementalType: DamageType? = null
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
    val rareLootTable: List<LootEntry>,
    val weakness: DamageType? = null
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
                    weakness = DamageType.RANGED,
                    mainLootTable = listOf(
                        LootEntry("goblin_ear", 1, 2, 40.0)
                    ),
                    rareLootTable = listOf(
                        LootEntry("rusty_dagger", 1, 1, 2.0)
                    )
                ),
                Monster(
                    id = "goblin_scout",
                    name = "Goblin Scout",
                    levelRequirement = 1,
                    maxHealth = 20,
                    defenseRating = 3,
                    weakness = DamageType.WIND,
                    mainLootTable = listOf(
                        LootEntry("goblin_ear", 1, 1, 35.0)
                    ),
                    rareLootTable = listOf(
                        LootEntry("rusty_dagger", 1, 1, 1.5)
                    )
                ),
                Monster(
                    id = "goblin_shaman",
                    name = "Goblin Shaman",
                    levelRequirement = 4,
                    maxHealth = 32,
                    defenseRating = 7,
                    weakness = DamageType.EARTH,
                    mainLootTable = listOf(
                        LootEntry("goblin_ear", 1, 2, 45.0)
                    ),
                    rareLootTable = listOf(
                        LootEntry("rusty_dagger", 1, 1, 2.5)
                    )
                ),
                Monster(
                    id = "goblin_brute",
                    name = "Goblin Brute",
                    levelRequirement = 7,
                    maxHealth = 50,
                    defenseRating = 12,
                    weakness = DamageType.WATER,
                    mainLootTable = listOf(
                        LootEntry("goblin_ear", 2, 3, 50.0)
                    ),
                    rareLootTable = listOf(
                        LootEntry("rusty_dagger", 1, 1, 4.0)
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
                    weakness = DamageType.FIRE,
                    mainLootTable = listOf(
                        LootEntry("ectoplasm", 1, 3, 55.0)
                    ),
                    rareLootTable = listOf(
                        LootEntry("wraith_essence", 1, 1, 0.5)
                    )
                ),
                Monster(
                    id = "restless_skeleton",
                    name = "Restless Skeleton",
                    levelRequirement = 20,
                    maxHealth = 70,
                    defenseRating = 22,
                    weakness = DamageType.MELEE,
                    mainLootTable = listOf(
                        LootEntry("ectoplasm", 1, 1, 30.0)
                    ),
                    rareLootTable = listOf(
                        LootEntry("rusty_dagger", 1, 1, 6.0),
                        LootEntry("wraith_essence", 1, 1, 0.2)
                    )
                ),
                Monster(
                    id = "shadow_stalker",
                    name = "Shadow Stalker",
                    levelRequirement = 26,
                    maxHealth = 100,
                    defenseRating = 31,
                    weakness = DamageType.RANGED,
                    mainLootTable = listOf(
                        LootEntry("ectoplasm", 1, 3, 60.0)
                    ),
                    rareLootTable = listOf(
                        LootEntry("wraith_essence", 1, 1, 0.8)
                    )
                ),
                Monster(
                    id = "ruin_banshee",
                    name = "Ruin Banshee",
                    levelRequirement = 33,
                    maxHealth = 130,
                    defenseRating = 40,
                    weakness = DamageType.EARTH,
                    mainLootTable = listOf(
                        LootEntry("ectoplasm", 2, 4, 65.0)
                    ),
                    rareLootTable = listOf(
                        LootEntry("wraith_essence", 1, 1, 1.2)
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
                    weakness = DamageType.MELEE,
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
                    weakness = DamageType.RANGED,
                    mainLootTable = listOf(
                        LootEntry("raw_chicken", 1, 1, 65.0),
                        LootEntry("feathers", 1, 5, 70.0)
                    ),
                    rareLootTable = listOf()
                ),
                Monster(
                    id = "crop_crow",
                    name = "Crop Crow",
                    levelRequirement = 2,
                    maxHealth = 14,
                    defenseRating = 2,
                    weakness = DamageType.EARTH,
                    mainLootTable = listOf(
                        LootEntry("feathers", 1, 3, 70.0),
                        LootEntry("raw_chicken", 1, 1, 35.0)
                    ),
                    rareLootTable = listOf()
                ),
                Monster(
                    id = "angry_goat",
                    name = "Angry Goat",
                    levelRequirement = 4,
                    maxHealth = 30,
                    defenseRating = 6,
                    weakness = DamageType.WIND,
                    mainLootTable = listOf(
                        LootEntry("cowhide", 1, 1, 55.0),
                        LootEntry("raw_beef", 1, 2, 55.0)
                    ),
                    rareLootTable = listOf()
                ),
                Monster(
                    id = "haunted_scarecrow",
                    name = "Haunted Scarecrow",
                    levelRequirement = 6,
                    maxHealth = 42,
                    defenseRating = 9,
                    weakness = DamageType.FIRE,
                    mainLootTable = listOf(
                        LootEntry("feathers", 2, 4, 60.0),
                        LootEntry("cowhide", 1, 1, 30.0)
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
                    weakness = DamageType.EARTH,
                    mainLootTable = listOf(
                        LootEntry("snake_hide", 1, 1, 55.0)
                    ),
                    rareLootTable = listOf()
                ),
                Monster(
                    id = "bog_toad",
                    name = "Bog Toad",
                    levelRequirement = 10,
                    maxHealth = 30,
                    defenseRating = 8,
                    weakness = DamageType.FIRE,
                    mainLootTable = listOf(
                        LootEntry("snake_hide", 1, 1, 35.0)
                    ),
                    rareLootTable = listOf()
                ),
                Monster(
                    id = "swamp_leech",
                    name = "Swamp Leech",
                    levelRequirement = 12,
                    maxHealth = 40,
                    defenseRating = 12,
                    weakness = DamageType.MELEE,
                    mainLootTable = listOf(
                        LootEntry("snake_hide", 1, 1, 45.0)
                    ),
                    rareLootTable = listOf()
                ),
                Monster(
                    id = "bog_lurker",
                    name = "Bog Lurker",
                    levelRequirement = 14,
                    maxHealth = 55,
                    defenseRating = 16,
                    weakness = DamageType.RANGED,
                    mainLootTable = listOf(
                        LootEntry("snake_hide", 1, 2, 60.0)
                    ),
                    rareLootTable = listOf(
                        LootEntry("uncut_gemstone", 1, 1, 2.0)
                    )
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
                    weakness = DamageType.WATER,
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
                ),
                Monster(
                    id = "cave_bat",
                    name = "Cave Bat",
                    levelRequirement = 15,
                    maxHealth = 32,
                    defenseRating = 12,
                    weakness = DamageType.WIND,
                    mainLootTable = listOf(
                        LootEntry("uncut_gemstone", 1, 1, 25.0)
                    ),
                    rareLootTable = listOf()
                ),
                Monster(
                    id = "gemstone_spider",
                    name = "Gemstone Spider",
                    levelRequirement = 17,
                    maxHealth = 52,
                    defenseRating = 18,
                    weakness = DamageType.FIRE,
                    mainLootTable = listOf(
                        LootEntry("uncut_gemstone", 1, 1, 40.0)
                    ),
                    rareLootTable = listOf(
                        LootEntry("uncut_opal", 1, 1, 5.0),
                        LootEntry("uncut_jade", 1, 1, 3.5),
                        LootEntry("uncut_red_topaz", 1, 1, 2.5),
                        LootEntry("uncut_sapphire", 1, 1, 1.5)
                    )
                ),
                Monster(
                    id = "crystal_golem",
                    name = "Crystal Golem",
                    levelRequirement = 19,
                    maxHealth = 70,
                    defenseRating = 22,
                    weakness = DamageType.MELEE,
                    mainLootTable = listOf(
                        LootEntry("uncut_gemstone", 1, 3, 60.0)
                    ),
                    rareLootTable = listOf(
                        LootEntry("uncut_sapphire", 1, 1, 3.0),
                        LootEntry("uncut_emerald", 1, 1, 2.0),
                        LootEntry("uncut_ruby", 1, 1, 1.2),
                        LootEntry("uncut_diamond", 1, 1, 0.6)
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
                    weakness = DamageType.WIND,
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
                    weakness = DamageType.FIRE,
                    mainLootTable = listOf(
                        LootEntry("blue_dragonhide", 1, 1, 55.0)
                    ),
                    rareLootTable = listOf()
                ),
                Monster(
                    id = "dragon_whelp",
                    name = "Dragon Whelp",
                    levelRequirement = 60,
                    maxHealth = 160,
                    defenseRating = 50,
                    weakness = DamageType.RANGED,
                    mainLootTable = listOf(
                        LootEntry("green_dragonhide", 1, 1, 30.0)
                    ),
                    rareLootTable = listOf(
                        LootEntry("uncut_dragonstone", 1, 1, 0.4)
                    )
                ),
                Monster(
                    id = "red_dragon",
                    name = "Red Dragon",
                    levelRequirement = 70,
                    maxHealth = 300,
                    defenseRating = 85,
                    weakness = DamageType.WATER,
                    mainLootTable = listOf(
                        LootEntry("blue_dragonhide", 1, 1, 45.0)
                    ),
                    rareLootTable = listOf(
                        LootEntry("uncut_dragonstone", 1, 1, 1.0)
                    )
                ),
                Monster(
                    id = "black_dragon",
                    name = "Black Dragon",
                    levelRequirement = 75,
                    maxHealth = 340,
                    defenseRating = 95,
                    weakness = DamageType.EARTH,
                    mainLootTable = listOf(
                        LootEntry("blue_dragonhide", 1, 1, 60.0)
                    ),
                    rareLootTable = listOf(
                        LootEntry("uncut_dragonstone", 1, 1, 1.5)
                    )
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
    val autoFleeThresholdPercent: Int,
    val selectedPrayerId: String? = null,
    val damageType: DamageType? = null
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
    val monsterDefeated: Boolean,
    val wasWeaknessHit: Boolean = false
)

data class CombatSessionExport(
    val characterId: String,
    val currentHp: Int,
    val maxHp: Int,
    val recoveringUntil: String?,
    val zoneId: String?,
    val sessionState: String?,
    val searchEndsAt: String?,
    val currentMonsterId: String?,
    val currentMonsterHealth: Int
)

data class OfflineCombatOutcome(
    val estimatedKills: Int,
    val xpEarned: Long
)

class CombatService {
    private val recoveryDuration: Duration = Duration.ofSeconds(600)
    private val states: MutableMap<String, CharacterCombatState> = mutableMapOf()

    // Fired once per monster kill - live combat AND offline-progress kills alike.
    // GameViewModel uses it to keep per-monster kill counts (Slayer titles).
    var onMonsterKilled: (String, Monster) -> Unit = { _, _ -> }

    // Which monster the player picked to hunt (monster id), supplied per character by
    // GameViewModel from persisted settings. Null/unknown/not-in-this-zone -> random pick.
    var targetMonsterIdProvider: (String) -> String? = { null }

    private fun targetMonsterFor(characterId: String, zone: Zone): Monster? {
        val targetId = targetMonsterIdProvider(characterId) ?: return null
        return zone.monsters.find { it.id == targetId }
    }

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

        val monster = targetMonsterFor(characterId, session.zone) ?: session.zone.monsters.random()
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
        attackerMaxHit: Int,
        attackerMinHit: Int = 0,
        potionItemId: String? = null
    ): ServiceResult<AttackResult> {
        val state = stateFor(characterId)
        val session = state.session ?: return ServiceResult.Failure("Not currently in a zone.")
        if (session.state != SessionState.IN_COMBAT) {
            return ServiceResult.Failure("Not currently in combat.")
        }
        val monster = session.currentMonster ?: return ServiceResult.Failure("No active target.")

        // Prayer bonuses applied here (rather than at the caller) since this is the
        // one place both live and any future callers already thread the loadout through.
                val potionAccuracyBonus = potionItemId?.let {
            PotionEffectCatalog.accuracyBonusFor(it, loadout.style)
        } ?: 0.0

        val potionDamageBonus = potionItemId?.let {
            PotionEffectCatalog.damageBonusFor(it, loadout.style)
        } ?: 0.0

        val prayerAccuracyMultiplier =
            if (loadout.selectedPrayerId == "clarity_of_thought") 1.1 else 1.0

        val prayerDamageMultiplier =
            if (loadout.selectedPrayerId == "burst_of_strength") 1.1 else 1.0

        val effectiveAccuracy = (
            attackerAccuracy *
                prayerAccuracyMultiplier *
                (1.0 + potionAccuracyBonus / 100.0)
            ).toInt()

        val effectiveMaxHit = (
            attackerMaxHit *
                prayerDamageMultiplier *
                (1.0 + potionDamageBonus / 100.0)
            ).toInt()

        val effectiveMinHit = (
            attackerMinHit *
                prayerDamageMultiplier *
                (1.0 + potionDamageBonus / 100.0)
            ).toInt()
        // Explicit cap even though the accuracy-vs-defense ratio is already
        // mathematically bounded below 100% for any positive defenseRating -
        // this makes the "never exceeds 100% per mob" guarantee an explicit
        // invariant rather than an incidental property of the formula.
        val hitChancePercent = ((effectiveAccuracy.toDouble() / (effectiveAccuracy + monster.defenseRating)) * 100.0)
            .coerceIn(0.0, 100.0)
        val didHit = Random.nextDouble(0.0, 100.0) < hitChancePercent

        if (!didHit) {
            return ServiceResult.Success(
                AttackResult(didHit = false, damageDealt = 0, monsterHpRemaining = session.currentMonsterHealth, monsterDefeated = false)
            )
        }

        // Guard against minHit exceeding maxHit (e.g. from prayer rounding at low
        // levels) - Random.nextInt(from, until) throws if from > until.
        val safeMinHit = effectiveMinHit.coerceIn(0, effectiveMaxHit)
        val rawDamage = Random.nextInt(safeMinHit, effectiveMaxHit + 1)
        // Elemental/style weakness: 50% bonus damage when the attacker's
        // damage type matches the monster's weakness. Damage-only (doesn't
        // affect hit chance), same convention as the prayer bonuses above.
        val isWeaknessHit = monster.weakness != null && monster.weakness == loadout.damageType
        val damage = if (isWeaknessHit) (rawDamage * 1.5).toInt().coerceAtLeast(rawDamage) else rawDamage
        session.currentMonsterHealth = (session.currentMonsterHealth - damage).coerceAtLeast(0)
        val defeated = session.currentMonsterHealth <= 0

        if (defeated) {
            val dropRateMultiplier = if (loadout.selectedPrayerId == "fortunes_favor") 1.15 else 1.0
            val potionLootBonus = potionItemId
                ?.let { PotionEffectCatalog.find(it)?.lootChanceBonusPercent }
                ?: 0.0

            rollLoot(
                state,
                monster,
                dropRateMultiplier * (1.0 + potionLootBonus / 100.0)
            )
            onMonsterKilled(characterId, monster)
            session.currentMonster = null
            startSearching(characterId)
        }

        return ServiceResult.Success(
            AttackResult(didHit = true, damageDealt = damage, monsterHpRemaining = session.currentMonsterHealth, monsterDefeated = defeated, wasWeaknessHit = isWeaknessHit)
        )
    }

    private fun rollLoot(state: CharacterCombatState, monster: Monster, dropRateMultiplier: Double = 1.0) {
        (monster.mainLootTable + monster.rareLootTable).forEach { entry ->
            val effectiveChance = (entry.dropChancePercent * dropRateMultiplier).coerceAtMost(100.0)
            if (Random.nextDouble(0.0, 100.0) < effectiveChance) {
                val qty = Random.nextInt(entry.minQty, entry.maxQty + 1)
                state.lootPool.add(entry.copy(minQty = qty, maxQty = qty))
            }
        }
        // Every monster guarantees exactly 1 bone per kill, tiered by monster level.
        // Guaranteed - not affected by drop-rate prayers.
        val boneType = when {
            monster.levelRequirement >= 60 -> "dragon_bones"
            monster.levelRequirement >= 20 -> "big_bones"
            monster.levelRequirement >= 15 -> "gem_bones"
            else -> "bone"
        }
        state.lootPool.add(LootEntry(boneType, 1, 1, 100.0))
        state.pendingCoins += CoinDropTable.rollCoins(monster.levelRequirement)

        // Elemental essences (Fire/Earth/Water/Wind) used for magic weapon
        // crafting - a flat chance per kill to gather one, uniformly random
        // type, independent of the monster's own loot table (same guaranteed-
        // roll pattern as bones, works across all zones without needing
        // per-monster loot table entries).
        if (Random.nextDouble(0.0, 100.0) < 15.0) {
            val essenceType = listOf("fire_essence", "earth_essence", "water_essence", "wind_essence").random()
            state.lootPool.add(LootEntry(essenceType, 1, 1, 100.0))
        }
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

    fun exportSessions(): List<CombatSessionExport> =
        states.map { (characterId, state) ->
            CombatSessionExport(
                characterId = characterId,
                currentHp = state.currentHp,
                maxHp = state.maxHp,
                recoveringUntil = state.recovery.recoveringUntil?.toString(),
                zoneId = state.session?.zone?.id,
                sessionState = state.session?.state?.name,
                searchEndsAt = state.session?.searchEndsAt?.toString(),
                currentMonsterId = state.session?.currentMonster?.id,
                currentMonsterHealth = state.session?.currentMonsterHealth ?: 0
            )
        }

    fun restoreSession(export: CombatSessionExport) {
        val state = stateFor(export.characterId, export.maxHp)
        state.currentHp = export.currentHp
        state.maxHp = export.maxHp
        state.recovery.recoveringUntil = export.recoveringUntil?.let { Instant.parse(it) }
        val zoneId = export.zoneId
        if (zoneId != null) {
            val zone = ZoneCatalog.zones.find { it.id == zoneId }
            if (zone != null) {
                val monster = export.currentMonsterId?.let { mId -> zone.monsters.find { it.id == mId } }
                state.session = CombatSession(
                    zone = zone,
                    state = export.sessionState?.let { SessionState.valueOf(it) } ?: SessionState.SEARCHING,
                    searchEndsAt = export.searchEndsAt?.let { Instant.parse(it) },
                    currentMonster = monster,
                    currentMonsterHealth = export.currentMonsterHealth
                )
            }
        }
    }

    // Stat-aware estimator for offline combat progress. Mirrors live combat's own
    // formulas rather than inventing new ones: hitChance uses the same
    // accuracy-vs-defense ratio, damage uses the same uniform 0..maxHit
    // distribution (averaged), and XP uses the same damagePerHit * 4 + 5 per-hit
    // formula, scaled by elapsed time assuming the same 1-attack-per-second
    // cadence as the live tick. Average monster stats are used since live combat
    // itself picks a random monster from the zone per encounter. Loot/coins are
    // rolled per estimated kill through the same rollLoot() used by live combat,
    // so they land in the same lootPool/pendingCoins for the caller to collect
    // via the existing collectLoot()/collectCoins().
    fun resolveOfflineCombat(
        characterId: String,
        zoneId: String,
        elapsedSeconds: Long,
        attackerAccuracy: Int,
        attackerMaxHit: Int,
        dropRateMultiplier: Double = 1.0,
        attackerMinHit: Int = 0,
        damageType: DamageType? = null,
        attackSpeedSeconds: Double = 1.0,
        combatStyle: CombatStyle = CombatStyle.MELEE,
        potionItemId: String? = null
    ): ServiceResult<OfflineCombatOutcome> {
        val state = stateFor(characterId)
        val zone = ZoneCatalog.zones.find { it.id == zoneId }
            ?: return ServiceResult.Failure("Zone not found.")
        if (zone.monsters.isEmpty()) {
            return ServiceResult.Failure("Zone has no monsters.")
        }
        if (elapsedSeconds <= 0) {
            return ServiceResult.Success(OfflineCombatOutcome(estimatedKills = 0, xpEarned = 0L))
        }

        // If the player picked a specific monster, offline progress assumes they keep
        // fighting only that monster; otherwise average across the zone as before.
        val targetMonster = targetMonsterFor(characterId, zone)
        val offlinePool: List<Monster> = if (targetMonster != null) listOf(targetMonster) else zone.monsters
        val avgMonsterHealth = offlinePool.map { it.maxHealth }.average()
        val avgMonsterDefense = offlinePool.map { it.defenseRating }.average()

        val potionAccuracyBonus = potionItemId?.let {
            PotionEffectCatalog.accuracyBonusFor(it, combatStyle)
        } ?: 0.0

        val effectiveAccuracy = (
            attackerAccuracy * (1.0 + potionAccuracyBonus / 100.0)
            ).toInt()

        val hitChance = (
            effectiveAccuracy.toDouble() /
                (effectiveAccuracy + avgMonsterDefense)
        ).coerceIn(0.0, 1.0)

        val safeMinHit = attackerMinHit.coerceIn(
            0,
            attackerMaxHit.coerceAtLeast(0)
        )
        val safeMaxHit = attackerMaxHit.coerceAtLeast(safeMinHit)
        val potionDamageBonus = potionItemId?.let {
    PotionEffectCatalog.damageBonusFor(it, combatStyle)
} ?: 0.0

val rawAverageDamage =
    ((safeMinHit + safeMaxHit) / 2.0) *
        (1.0 + potionDamageBonus / 100.0)

        val avgDamageMultiplier = offlinePool.map { monster ->
            if (monster.weakness != null && monster.weakness == damageType) {
                1.5
            } else {
                1.0
            }
        }.average()

        val avgDamagePerHit = rawAverageDamage * avgDamageMultiplier
        val safeAttackSpeed =
            attackSpeedSeconds.takeIf { it.isFinite() && it > 0.0 } ?: 1.0

        if (hitChance <= 0.0 || avgDamagePerHit <= 0.0) {
            return ServiceResult.Success(
                OfflineCombatOutcome(estimatedKills = 0, xpEarned = 0L)
            )
        }

        // Estimate XP using the expected damage per attack and weapon speed.
        val attacksAttempted = elapsedSeconds / safeAttackSpeed
        val xpPerAttack = hitChance * (avgDamagePerHit * 4 + 5)
        val xpEarned = (xpPerAttack * attacksAttempted).toLong()

        // Live combat averages a 3–10 second search window between encounters.
        val avgSearchSeconds = 6.5
        val avgHitsToKill = avgMonsterHealth / avgDamagePerHit
        val avgAttacksToKill = avgHitsToKill / hitChance
        val avgTimeToKillSeconds =
            avgSearchSeconds + avgAttacksToKill * safeAttackSpeed

        val estimatedKills =
            (elapsedSeconds / avgTimeToKillSeconds).toInt().coerceAtLeast(0)

        repeat(estimatedKills) {
            val monster = offlinePool.random()
            val potionLootBonus = potionItemId
                ?.let { PotionEffectCatalog.find(it)?.lootChanceBonusPercent }
                ?: 0.0

            rollLoot(
                state,
                monster,
                dropRateMultiplier * (1.0 + potionLootBonus / 100.0)
            )
            onMonsterKilled(characterId, monster)
        }

        return ServiceResult.Success(OfflineCombatOutcome(estimatedKills = estimatedKills, xpEarned = xpEarned))
    }
}
