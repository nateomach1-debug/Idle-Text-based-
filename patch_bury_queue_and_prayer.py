def apply(content, old, new, label):
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"FAILED [{label}]: expected 1 match, found {count}")
    return content.replace(old, new, 1)

# ---------- CombatSystem.kt ----------
CS_PATH = "app/src/main/kotlin/com/yourname/idlerpg/CombatSystem.kt"
with open(CS_PATH, "r", encoding="utf-8") as f:
    cs = f.read()

cs = apply(cs,
"""    fun resolveAttack(
        characterId: String,
        loadout: CombatLoadout,
        attackerAccuracy: Int,
        attackerMaxHit: Int
    ): ServiceResult<AttackResult> {""",
"""    fun resolveAttack(
        characterId: String,
        loadout: CombatLoadout,
        attackerAccuracy: Int,
        attackerMaxHit: Int,
        attackerMinHit: Int = 0
    ): ServiceResult<AttackResult> {""",
    "resolveAttack signature: add attackerMinHit"
)

cs = apply(cs,
"""        val effectiveAccuracy = if (loadout.selectedPrayerId == "clarity_of_thought") (attackerAccuracy * 1.1).toInt() else attackerAccuracy
        val effectiveMaxHit = if (loadout.selectedPrayerId == "burst_of_strength") (attackerMaxHit * 1.1).toInt() else attackerMaxHit

        val hitChancePercent = (effectiveAccuracy.toDouble() / (effectiveAccuracy + monster.defenseRating)) * 100.0
        val didHit = Random.nextDouble(0.0, 100.0) < hitChancePercent

        if (!didHit) {
            return ServiceResult.Success(
                AttackResult(didHit = false, damageDealt = 0, monsterHpRemaining = session.currentMonsterHealth, monsterDefeated = false)
            )
        }

        val damage = Random.nextInt(0, effectiveMaxHit + 1)""",
"""        val effectiveAccuracy = if (loadout.selectedPrayerId == "clarity_of_thought") (attackerAccuracy * 1.1).toInt() else attackerAccuracy
        val effectiveMaxHit = if (loadout.selectedPrayerId == "burst_of_strength") (attackerMaxHit * 1.1).toInt() else attackerMaxHit
        val effectiveMinHit = if (loadout.selectedPrayerId == "burst_of_strength") (attackerMinHit * 1.1).toInt() else attackerMinHit

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
        val damage = Random.nextInt(safeMinHit, effectiveMaxHit + 1)""",
    "resolveAttack: min-hit roll + explicit hit-chance cap"
)

with open(CS_PATH, "w", encoding="utf-8") as f:
    f.write(cs)

# ---------- GameViewModel.kt ----------
GVM_PATH = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(GVM_PATH, "r", encoding="utf-8") as f:
    gvm = f.read()

gvm = apply(gvm,
"""        val weapon = equippedWeapon(characterId)
        val trainingSkill = _trainingSkill.value
        val accuracy: Int
        val maxHit: Int
        val attackSpeedSeconds: Double
        when (weapon?.style) {
            CombatStyle.MAGIC -> {
                val magicLevel = skillLevel(characterId, SkillType.MAGIC)
                accuracy = magicLevel * 2 + weapon.baseAccuracy
                maxHit = (magicLevel / 3) + weapon.baseMaxHit
                attackSpeedSeconds = weapon.attackSpeedSeconds
            }
            CombatStyle.RANGED -> {
                val archeryLevel = skillLevel(characterId, SkillType.ARCHERY)
                accuracy = archeryLevel * 2 + weapon.baseAccuracy
                maxHit = (archeryLevel / 3) + weapon.baseMaxHit
                attackSpeedSeconds = weapon.attackSpeedSeconds
            }
            else -> {
                val attackLevel = skillLevel(characterId, SkillType.ATTACK)
                val strengthLevel = skillLevel(characterId, SkillType.STRENGTH)
                accuracy = attackLevel * 2 + (weapon?.baseAccuracy ?: 5)
                maxHit = (strengthLevel / 3) + (weapon?.baseMaxHit ?: 1)
                attackSpeedSeconds = weapon?.attackSpeedSeconds ?: 2.4
            }
        }""",
"""        val weapon = equippedWeapon(characterId)
        val trainingSkill = _trainingSkill.value
        val accuracy: Int
        val maxHit: Int
        val minHit: Int
        val attackSpeedSeconds: Double
        // minHit scales slowly (roughly +1 per 10 levels of the relevant stat) so
        // low-level combat is unaffected, while high-level characters get a
        // meaningfully more consistent damage floor instead of every hit still
        // being able to roll as low as 0. Tunable - CombatSystem.resolveAttack()
        // clamps minHit to never exceed maxHit regardless of the value passed here.
        when (weapon?.style) {
            CombatStyle.MAGIC -> {
                val magicLevel = skillLevel(characterId, SkillType.MAGIC)
                accuracy = magicLevel * 2 + weapon.baseAccuracy
                maxHit = (magicLevel / 3) + weapon.baseMaxHit
                minHit = magicLevel / 10
                attackSpeedSeconds = weapon.attackSpeedSeconds
            }
            CombatStyle.RANGED -> {
                val archeryLevel = skillLevel(characterId, SkillType.ARCHERY)
                accuracy = archeryLevel * 2 + weapon.baseAccuracy
                maxHit = (archeryLevel / 3) + weapon.baseMaxHit
                minHit = archeryLevel / 10
                attackSpeedSeconds = weapon.attackSpeedSeconds
            }
            else -> {
                val attackLevel = skillLevel(characterId, SkillType.ATTACK)
                val strengthLevel = skillLevel(characterId, SkillType.STRENGTH)
                accuracy = attackLevel * 2 + (weapon?.baseAccuracy ?: 5)
                maxHit = (strengthLevel / 3) + (weapon?.baseMaxHit ?: 1)
                minHit = strengthLevel / 10
                attackSpeedSeconds = weapon?.attackSpeedSeconds ?: 2.4
            }
        }""",
    "tickCombat: compute minHit per style"
)

gvm = apply(gvm,
"""            val result = combatService.resolveAttack(characterId, loadout, accuracy, maxHit)""",
"""            val result = combatService.resolveAttack(characterId, loadout, accuracy, maxHit, minHit)""",
    "tickCombat: pass minHit to resolveAttack"
)

gvm = apply(gvm,
"""                val monsterDefense = session.currentMonster?.defenseRating ?: 1
                lastHitChancePercent = (accuracy.toDouble() / (accuracy + monsterDefense)) * 100.0""",
"""                val monsterDefense = session.currentMonster?.defenseRating ?: 1
                lastHitChancePercent = ((accuracy.toDouble() / (accuracy + monsterDefense)) * 100.0).coerceIn(0.0, 100.0)""",
    "tickCombat: clamp displayed hit chance to match resolveAttack's cap"
)

gvm = apply(gvm,
"""                val monster = session.currentMonster
                if (monster != null && Random.nextDouble(0.0, 100.0) < 40.0) {
                    val rawDmg = Random.nextInt(1, (monster.defenseRating / 3).coerceAtLeast(1) + 1)
                    val dmg = if (inventoryService.inventoryFor(characterId).selectedPrayerId == "rock_skin") {
                        (rawDmg * 0.8).toInt().coerceAtLeast(1)
                    } else {
                        rawDmg
                    }
                    combatService.applyDamageToCharacter(characterId, dmg)
                    log.add(CombatLogEntry(monster.name + " hits you for " + dmg + "."))
                }""",
"""                val monster = session.currentMonster
                if (monster != null && Random.nextDouble(0.0, 100.0) < 40.0) {
                    val rawDmg = Random.nextInt(1, (monster.defenseRating / 3).coerceAtLeast(1) + 1)
                    val prayerAdjustedDmg = if (inventoryService.inventoryFor(characterId).selectedPrayerId == "rock_skin") {
                        (rawDmg * 0.8).toInt().coerceAtLeast(1)
                    } else {
                        rawDmg
                    }
                    // Defense passively reduces incoming damage regardless of which skill is
                    // currently selected to train, matching the classic "defense stat" model
                    // rather than only mattering while actively training it. Capped at 50%
                    // reduction so high Defense meaningfully helps survivability without making
                    // combat damage-immune; at least 1 damage always gets through.
                    val defenseLevel = skillLevel(characterId, SkillType.DEFENSE)
                    val defenseReductionPercent = (defenseLevel * 0.5).coerceAtMost(50.0)
                    val dmg = (prayerAdjustedDmg * (1.0 - defenseReductionPercent / 100.0)).toInt().coerceAtLeast(1)
                    combatService.applyDamageToCharacter(characterId, dmg)
                    log.add(CombatLogEntry(monster.name + " hits you for " + dmg + "."))
                }""",
    "tickCombat: Defense-based incoming damage reduction"
)

with open(GVM_PATH, "w", encoding="utf-8") as f:
    f.write(gvm)

print("All edits applied successfully to both files.")
