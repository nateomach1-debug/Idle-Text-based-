import sys

BASE = "app/src/main/kotlin/com/yourname/idlerpg/"
SHARED_TYPES = BASE + "SharedTypes.kt"
COMBAT_SYSTEM = BASE + "CombatSystem.kt"
GAME_VIEW_MODEL = BASE + "GameViewModel.kt"
ITEM_CATALOG = BASE + "GeneratedItemCatalog.kt"


def guarded_replace(path, old, new, label):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    if new in text:
        print(f"SKIP (already applied): {label} ({path})")
        return True

    count = text.count(old)
    if count == 1:
        text = text.replace(old, new)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"OK: {label} ({path})")
        return True
    elif count == 0:
        print(f"FAIL (old_str not found, new_str not found either): {label} ({path})")
        return False
    else:
        print(f"FAIL (old_str matched {count} times, expected 1): {label} ({path})")
        return False


def check_braces(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    opens = text.count("{")
    closes = text.count("}")
    ok = opens == closes
    print(f"{'Brace check OK' if ok else 'WARNING: brace mismatch'}: {path} ({{ = {opens}, }} = {closes})")
    return ok


def check_parens(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    opens = text.count("(")
    closes = text.count(")")
    ok = opens == closes
    print(f"{'Paren check OK' if ok else 'WARNING: paren mismatch'}: {path} (( = {opens}, ) = {closes})")
    return ok


results = []

# ===========================================================
# 1. SharedTypes.kt - ItemDefinition gains elementalType
# ===========================================================
old = '''data class ItemDefinition(
    val id: String,
    val name: String,
    val category: ItemCategory,
    val rarity: Rarity = Rarity.COMMON,
    val isTradeable: Boolean,
    val isStackable: Boolean,
    val isRealMoneyPurchasable: Boolean = false,
    val equipSlot: EquipSlot? = null,
    val combatStyle: CombatStyle? = null,
    val levelRequired: Int = 1,
    val skillRequired: String? = null,
    val stats: ItemStats = ItemStats(),
    val consumableType: ConsumableType? = null,
    val healAmount: Int? = null,
    val buffDurationSeconds: Int? = null
)'''
new = '''data class ItemDefinition(
    val id: String,
    val name: String,
    val category: ItemCategory,
    val rarity: Rarity = Rarity.COMMON,
    val isTradeable: Boolean,
    val isStackable: Boolean,
    val isRealMoneyPurchasable: Boolean = false,
    val equipSlot: EquipSlot? = null,
    val combatStyle: CombatStyle? = null,
    val elementalType: DamageType? = null,
    val levelRequired: Int = 1,
    val skillRequired: String? = null,
    val stats: ItemStats = ItemStats(),
    val consumableType: ConsumableType? = null,
    val healAmount: Int? = null,
    val buffDurationSeconds: Int? = null
)'''
results.append(guarded_replace(SHARED_TYPES, old, new, "SharedTypes.kt ItemDefinition.elementalType"))

# ===========================================================
# 2. CombatSystem.kt - DamageType enum + Weapon.elementalType
# ===========================================================
old = '''data class Weapon(
    val name: String,
    val style: CombatStyle,
    val attackSpeedSeconds: Double,
    val baseAccuracy: Int,
    val baseMaxHit: Int
)'''
new = '''enum class DamageType { MELEE, RANGED, FIRE, EARTH, WATER, WIND }

data class Weapon(
    val name: String,
    val style: CombatStyle,
    val attackSpeedSeconds: Double,
    val baseAccuracy: Int,
    val baseMaxHit: Int,
    val elementalType: DamageType? = null
)'''
results.append(guarded_replace(COMBAT_SYSTEM, old, new, "CombatSystem.kt DamageType enum + Weapon.elementalType"))

# ===========================================================
# 3. CombatSystem.kt - Monster.weakness
# ===========================================================
old = '''data class Monster(
    val id: String,
    val name: String,
    val levelRequirement: Int,
    val maxHealth: Int,
    val defenseRating: Int,
    val mainLootTable: List<LootEntry>,
    val rareLootTable: List<LootEntry>
)'''
new = '''data class Monster(
    val id: String,
    val name: String,
    val levelRequirement: Int,
    val maxHealth: Int,
    val defenseRating: Int,
    val mainLootTable: List<LootEntry>,
    val rareLootTable: List<LootEntry>,
    val weakness: DamageType? = null
)'''
results.append(guarded_replace(COMBAT_SYSTEM, old, new, "CombatSystem.kt Monster.weakness"))

# ===========================================================
# 4. CombatSystem.kt - CombatLoadout.damageType
# ===========================================================
old = '''data class CombatLoadout(
    val style: CombatStyle,
    val trainingSkill: SkillType,
    val equippedWeapon: Weapon?,
    val equippedSpell: Spell?,
    val autoHealThresholdPercent: Int,
    val autoFleeThresholdPercent: Int,
    val selectedPrayerId: String? = null
)'''
new = '''data class CombatLoadout(
    val style: CombatStyle,
    val trainingSkill: SkillType,
    val equippedWeapon: Weapon?,
    val equippedSpell: Spell?,
    val autoHealThresholdPercent: Int,
    val autoFleeThresholdPercent: Int,
    val selectedPrayerId: String? = null,
    val damageType: DamageType? = null
)'''
results.append(guarded_replace(COMBAT_SYSTEM, old, new, "CombatSystem.kt CombatLoadout.damageType"))

# ===========================================================
# 5. CombatSystem.kt - AttackResult.wasWeaknessHit
# ===========================================================
old = '''data class AttackResult(
    val didHit: Boolean,
    val damageDealt: Int,
    val monsterHpRemaining: Int,
    val monsterDefeated: Boolean
)'''
new = '''data class AttackResult(
    val didHit: Boolean,
    val damageDealt: Int,
    val monsterHpRemaining: Int,
    val monsterDefeated: Boolean,
    val wasWeaknessHit: Boolean = false
)'''
results.append(guarded_replace(COMBAT_SYSTEM, old, new, "CombatSystem.kt AttackResult.wasWeaknessHit"))

# ===========================================================
# 6. CombatSystem.kt - 8 monster weakness assignments
# ===========================================================
monster_weaknesses = [
    ("goblin_grunt", "Goblin Grunt", "1", "25", "5", "RANGED"),
    ("wraith", "Wraith", "20", "80", "25", "FIRE"),
    ("wild_cow", "Wild Cow", "1", "20", "3", "MELEE"),
    ("feral_chicken", "Feral Chicken", "1", "12", "1", "RANGED"),
    ("marsh_snake", "Marsh Snake", "10", "35", "10", "EARTH"),
    ("gem_hoarder", "Gem Hoarder", "15", "45", "15", "WATER"),
    ("green_dragon", "Green Dragon", "60", "220", "65", "WIND"),
    ("blue_dragon", "Blue Dragon", "65", "260", "75", "FIRE"),
]
for mob_id, mob_name, level, hp, defense, weakness in monster_weaknesses:
    old = f'''                    id = "{mob_id}",
                    name = "{mob_name}",
                    levelRequirement = {level},
                    maxHealth = {hp},
                    defenseRating = {defense},'''
    new = f'''                    id = "{mob_id}",
                    name = "{mob_name}",
                    levelRequirement = {level},
                    maxHealth = {hp},
                    defenseRating = {defense},
                    weakness = DamageType.{weakness},'''
    results.append(guarded_replace(COMBAT_SYSTEM, old, new, f"CombatSystem.kt {mob_name} weakness"))

# ===========================================================
# 7. CombatSystem.kt - resolveAttack applies weakness multiplier
# ===========================================================
old = '''        // Guard against minHit exceeding maxHit (e.g. from prayer rounding at low
        // levels) - Random.nextInt(from, until) throws if from > until.
        val safeMinHit = effectiveMinHit.coerceIn(0, effectiveMaxHit)
        val damage = Random.nextInt(safeMinHit, effectiveMaxHit + 1)
        session.currentMonsterHealth = (session.currentMonsterHealth - damage).coerceAtLeast(0)
        val defeated = session.currentMonsterHealth <= 0'''
new = '''        // Guard against minHit exceeding maxHit (e.g. from prayer rounding at low
        // levels) - Random.nextInt(from, until) throws if from > until.
        val safeMinHit = effectiveMinHit.coerceIn(0, effectiveMaxHit)
        val rawDamage = Random.nextInt(safeMinHit, effectiveMaxHit + 1)
        // Elemental/style weakness: 50% bonus damage when the attacker's
        // damage type matches the monster's weakness. Damage-only (doesn't
        // affect hit chance), same convention as the prayer bonuses above.
        val isWeaknessHit = monster.weakness != null && monster.weakness == loadout.damageType
        val damage = if (isWeaknessHit) (rawDamage * 1.5).toInt().coerceAtLeast(rawDamage) else rawDamage
        session.currentMonsterHealth = (session.currentMonsterHealth - damage).coerceAtLeast(0)
        val defeated = session.currentMonsterHealth <= 0'''
results.append(guarded_replace(COMBAT_SYSTEM, old, new, "CombatSystem.kt resolveAttack weakness multiplier"))

# ===========================================================
# 8. CombatSystem.kt - resolveAttack return includes wasWeaknessHit
# ===========================================================
old = '''        return ServiceResult.Success(
            AttackResult(didHit = true, damageDealt = damage, monsterHpRemaining = session.currentMonsterHealth, monsterDefeated = defeated)
        )
    }'''
new = '''        return ServiceResult.Success(
            AttackResult(didHit = true, damageDealt = damage, monsterHpRemaining = session.currentMonsterHealth, monsterDefeated = defeated, wasWeaknessHit = isWeaknessHit)
        )
    }'''
results.append(guarded_replace(COMBAT_SYSTEM, old, new, "CombatSystem.kt resolveAttack return wasWeaknessHit"))

# ===========================================================
# 9. GameViewModel.kt - equippedWeapon carries elementalType
# ===========================================================
old = '''    private fun equippedWeapon(characterId: String): Weapon? {
        val itemId = _equippedItems.value[EquipSlot.WEAPON] ?: return null
        val def = ItemCatalog.items.find { it.id == itemId } ?: return null
        val style = def.combatStyle ?: return null
        return Weapon(
            name = def.name,
            style = style,
            attackSpeedSeconds = 2.4,
            baseAccuracy = 5 + def.stats.accuracyBonus,
            baseMaxHit = 1 + def.stats.maxHitBonus
        )
    }'''
new = '''    private fun equippedWeapon(characterId: String): Weapon? {
        val itemId = _equippedItems.value[EquipSlot.WEAPON] ?: return null
        val def = ItemCatalog.items.find { it.id == itemId } ?: return null
        val style = def.combatStyle ?: return null
        return Weapon(
            name = def.name,
            style = style,
            attackSpeedSeconds = 2.4,
            baseAccuracy = 5 + def.stats.accuracyBonus,
            baseMaxHit = 1 + def.stats.maxHitBonus,
            elementalType = def.elementalType
        )
    }'''
results.append(guarded_replace(GAME_VIEW_MODEL, old, new, "GameViewModel.kt equippedWeapon elementalType"))

# ===========================================================
# 10. GameViewModel.kt - tickCombat computes damageType
# ===========================================================
old = '''            else -> {
                val attackLevel = skillLevel(characterId, SkillType.ATTACK)
                val strengthLevel = skillLevel(characterId, SkillType.STRENGTH)
                val attackMastery = masteryBonusPercent(attackLevel, hasSkillCapeEquipped(characterId, SkillType.ATTACK), 5.0, 10.0)
                val strengthMastery = masteryBonusPercent(strengthLevel, hasSkillCapeEquipped(characterId, SkillType.STRENGTH), 5.0, 10.0)
                accuracy = ((attackLevel * 2 + (weapon?.baseAccuracy ?: 5)) * (1.0 + attackMastery / 100.0)).toInt()
                maxHit = (((strengthLevel / 3) + (weapon?.baseMaxHit ?: 1)) * (1.0 + strengthMastery / 100.0)).toInt()
                minHit = ((strengthLevel / 10) * (1.0 + strengthMastery / 100.0)).toInt()
                attackSpeedSeconds = weapon?.attackSpeedSeconds ?: 2.4
            }
        }

        combatActionProgressSeconds += elapsedSeconds'''
new = '''            else -> {
                val attackLevel = skillLevel(characterId, SkillType.ATTACK)
                val strengthLevel = skillLevel(characterId, SkillType.STRENGTH)
                val attackMastery = masteryBonusPercent(attackLevel, hasSkillCapeEquipped(characterId, SkillType.ATTACK), 5.0, 10.0)
                val strengthMastery = masteryBonusPercent(strengthLevel, hasSkillCapeEquipped(characterId, SkillType.STRENGTH), 5.0, 10.0)
                accuracy = ((attackLevel * 2 + (weapon?.baseAccuracy ?: 5)) * (1.0 + attackMastery / 100.0)).toInt()
                maxHit = (((strengthLevel / 3) + (weapon?.baseMaxHit ?: 1)) * (1.0 + strengthMastery / 100.0)).toInt()
                minHit = ((strengthLevel / 10) * (1.0 + strengthMastery / 100.0)).toInt()
                attackSpeedSeconds = weapon?.attackSpeedSeconds ?: 2.4
            }
        }

        // Elemental/style weakness matching - MAGIC uses the weapon's specific
        // element (null for the non-elemental starter Staff, matching nothing),
        // RANGED/MELEE match monsters weak to those whole combat styles.
        val damageType: DamageType? = when (weapon?.style) {
            CombatStyle.MAGIC -> weapon.elementalType
            CombatStyle.RANGED -> DamageType.RANGED
            else -> DamageType.MELEE
        }

        combatActionProgressSeconds += elapsedSeconds'''
results.append(guarded_replace(GAME_VIEW_MODEL, old, new, "GameViewModel.kt tickCombat damageType"))

# ===========================================================
# 11. GameViewModel.kt - CombatLoadout construction passes damageType
# ===========================================================
old = '''            val loadout = CombatLoadout(
                style = weapon?.style ?: CombatStyle.MELEE,
                trainingSkill = trainingSkill,
                selectedPrayerId = inventoryService.inventoryFor(characterId).selectedPrayerId,
                equippedWeapon = weapon,
                equippedSpell = null,
                autoHealThresholdPercent = inventoryService.inventoryFor(characterId).autoHealThresholdPercent,
                autoFleeThresholdPercent = inventoryService.inventoryFor(characterId).autoFleeThresholdPercent
            )'''
new = '''            val loadout = CombatLoadout(
                style = weapon?.style ?: CombatStyle.MELEE,
                trainingSkill = trainingSkill,
                selectedPrayerId = inventoryService.inventoryFor(characterId).selectedPrayerId,
                equippedWeapon = weapon,
                equippedSpell = null,
                autoHealThresholdPercent = inventoryService.inventoryFor(characterId).autoHealThresholdPercent,
                autoFleeThresholdPercent = inventoryService.inventoryFor(characterId).autoFleeThresholdPercent,
                damageType = damageType
            )'''
results.append(guarded_replace(GAME_VIEW_MODEL, old, new, "GameViewModel.kt CombatLoadout.damageType wired"))

# ===========================================================
# 12. GameViewModel.kt - combat log notes weakness hit
# ===========================================================
old = '''                if (attack.didHit) {
                    log.add(CombatLogEntry("You hit for " + attack.damageDealt + "."))'''
new = '''                if (attack.didHit) {
                    val weaknessNote = if (attack.wasWeaknessHit) " Super effective!" else ""
                    log.add(CombatLogEntry("You hit for " + attack.damageDealt + "." + weaknessNote))'''
results.append(guarded_replace(GAME_VIEW_MODEL, old, new, "GameViewModel.kt combat log weakness note"))

# ===========================================================
# 13. GeneratedItemCatalog.kt - elementalType on all 12 elemental weapons
# ===========================================================
elemental_weapons = [
    ("fire_staff", "Fire Staff", "10", "15, strengthBonus = 0, accuracyBonus = 25, maxHitBonus = 15", "FIRE"),
    ("earth_staff", "Earth Staff", "10", "15, strengthBonus = 0, accuracyBonus = 25, maxHitBonus = 15", "EARTH"),
    ("water_staff", "Water Staff", "10", "15, strengthBonus = 0, accuracyBonus = 25, maxHitBonus = 15", "WATER"),
    ("wind_staff", "Wind Staff", "10", "15, strengthBonus = 0, accuracyBonus = 25, maxHitBonus = 15", "WIND"),
    ("fire_battlestaff", "Fire Battlestaff", "50", "50, strengthBonus = 0, accuracyBonus = 85, maxHitBonus = 55", "FIRE"),
    ("earth_battlestaff", "Earth Battlestaff", "50", "50, strengthBonus = 0, accuracyBonus = 85, maxHitBonus = 55", "EARTH"),
    ("water_battlestaff", "Water Battlestaff", "50", "50, strengthBonus = 0, accuracyBonus = 85, maxHitBonus = 55", "WATER"),
    ("wind_battlestaff", "Wind Battlestaff", "50", "50, strengthBonus = 0, accuracyBonus = 85, maxHitBonus = 55", "WIND"),
    ("mystic_fire_staff", "Mystic Fire Staff", "75", "70, strengthBonus = 0, accuracyBonus = 120, maxHitBonus = 75", "FIRE"),
    ("mystic_earth_staff", "Mystic Earth Staff", "75", "70, strengthBonus = 0, accuracyBonus = 120, maxHitBonus = 75", "EARTH"),
    ("mystic_water_staff", "Mystic Water Staff", "75", "70, strengthBonus = 0, accuracyBonus = 120, maxHitBonus = 75", "WATER"),
    ("mystic_wind_staff", "Mystic Wind Staff", "75", "70, strengthBonus = 0, accuracyBonus = 120, maxHitBonus = 75", "WIND"),
]
for item_id, item_name, level, stats, element in elemental_weapons:
    old = f'''    ItemDefinition(
        id = "{item_id}",
        name = "{item_name}",
        category = ItemCategory.WEAPON,
        isTradeable = true,
        isStackable = false,
        equipSlot = EquipSlot.WEAPON,
        combatStyle = CombatStyle.MAGIC,
        levelRequired = {level},
        skillRequired = "MAGIC",
        stats = ItemStats(attackBonus = {stats})
    ),'''
    new = f'''    ItemDefinition(
        id = "{item_id}",
        name = "{item_name}",
        category = ItemCategory.WEAPON,
        isTradeable = true,
        isStackable = false,
        equipSlot = EquipSlot.WEAPON,
        combatStyle = CombatStyle.MAGIC,
        elementalType = DamageType.{element},
        levelRequired = {level},
        skillRequired = "MAGIC",
        stats = ItemStats(attackBonus = {stats})
    ),'''
    results.append(guarded_replace(ITEM_CATALOG, old, new, f"GeneratedItemCatalog.kt {item_name} elementalType"))

print()
print("=== Brace/paren balance check ===")
for p in [SHARED_TYPES, COMBAT_SYSTEM, GAME_VIEW_MODEL, ITEM_CATALOG]:
    check_braces(p)
    check_parens(p)

if not all(results):
    print()
    print("One or more edits FAILED - review output above before committing.")
    sys.exit(1)

print()
print("All edits applied successfully.")
