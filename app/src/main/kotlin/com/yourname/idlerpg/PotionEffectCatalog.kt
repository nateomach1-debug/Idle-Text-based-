
package com.yourname.idlerpg

data class PotionEffectDefinition(
    val description: List<String>,
    val accuracyBonusPercent: Double = 0.0,
    val damageBonusPercent: Double = 0.0,
    val incomingDamageReductionPercent: Double = 0.0,
    val skillingSpeedBonusPercent: Double = 0.0,
    val lootChanceBonusPercent: Double = 0.0,
    val healAmount: Int = 0,
    val prayerRestorePoints: Int = 0,
    val poisonImmunitySeconds: Int = 0,
    val fireDamageReductionPercent: Double = 0.0
)

object PotionEffectCatalog {

    private val effects = mapOf(
        "attack_potion" to PotionEffectDefinition(
            description = listOf("+10% melee accuracy"),
            accuracyBonusPercent = 10.0
        ),
        "strength_potion" to PotionEffectDefinition(
            description = listOf("+15% melee damage"),
            damageBonusPercent = 15.0
        ),
        "defense_potion" to PotionEffectDefinition(
            description = listOf("15% less incoming damage"),
            incomingDamageReductionPercent = 15.0
        ),
        "restore_potion" to PotionEffectDefinition(
            description = listOf("Restores 30 HP"),
            healAmount = 30
        ),
        "energy_potion" to PotionEffectDefinition(
            description = listOf("20% faster skilling actions"),
            skillingSpeedBonusPercent = 20.0
        ),
        "combat_potion" to PotionEffectDefinition(
            description = listOf("+10% melee accuracy", "+10% melee damage"),
            accuracyBonusPercent = 10.0,
            damageBonusPercent = 10.0
        ),
        "prayer_potion" to PotionEffectDefinition(
            description = listOf("Restores 25 Prayer points"),
            prayerRestorePoints = 25
        ),
        "super_attack_potion" to PotionEffectDefinition(
            description = listOf("+15% melee accuracy"),
            accuracyBonusPercent = 15.0
        ),
        "super_strength_potion" to PotionEffectDefinition(
            description = listOf("+20% melee damage"),
            damageBonusPercent = 20.0
        ),
        "super_defense_potion" to PotionEffectDefinition(
            description = listOf("20% less incoming damage"),
            incomingDamageReductionPercent = 20.0
        ),
        "ranging_potion" to PotionEffectDefinition(
            description = listOf("+15% ranged accuracy", "+15% ranged damage"),
            accuracyBonusPercent = 15.0,
            damageBonusPercent = 15.0
        ),
        "magic_potion" to PotionEffectDefinition(
            description = listOf("+15% magic accuracy", "+15% magic damage"),
            accuracyBonusPercent = 15.0,
            damageBonusPercent = 15.0
        ),
        "super_restore_potion" to PotionEffectDefinition(
            description = listOf("Restores 50 HP", "Restores 50 Prayer points"),
            healAmount = 50,
            prayerRestorePoints = 50
        ),
        "antipoison" to PotionEffectDefinition(
            description = listOf("Cures poison", "Provides 180 seconds of poison immunity"),
            poisonImmunitySeconds = 180
        ),
        "antidote_plus" to PotionEffectDefinition(
            description = listOf("Cures poison", "Provides 300 seconds of poison immunity"),
            poisonImmunitySeconds = 300
        ),
        "brew_of_vigor" to PotionEffectDefinition(
            description = listOf("+15% defense", "10% faster skilling actions"),
            incomingDamageReductionPercent = 15.0,
            skillingSpeedBonusPercent = 10.0
        ),
        "antifire_potion" to PotionEffectDefinition(
            description = listOf("Reduces incoming fire damage by 50%"),
            fireDamageReductionPercent = 50.0
        ),
        "extreme_attack_potion" to PotionEffectDefinition(
            description = listOf("+20% melee accuracy"),
            accuracyBonusPercent = 20.0
        ),
        "extreme_strength_potion" to PotionEffectDefinition(
            description = listOf("+25% melee damage"),
            damageBonusPercent = 25.0
        ),
        "overload_potion" to PotionEffectDefinition(
            description = listOf("+20% accuracy for all combat styles", "+25% damage for all combat styles"),
            accuracyBonusPercent = 20.0,
            damageBonusPercent = 25.0
        ),
        "divine_potion" to PotionEffectDefinition(
            description = listOf("+25% accuracy for all combat styles", "+30% damage for all combat styles"),
            accuracyBonusPercent = 25.0,
            damageBonusPercent = 30.0
        ),
        "elixir_of_the_ancients" to PotionEffectDefinition(
            description = listOf("+20% accuracy", "+20% damage", "+10% loot chance"),
            accuracyBonusPercent = 20.0,
            damageBonusPercent = 20.0,
            lootChanceBonusPercent = 10.0
        )
    )

    fun find(itemId: String): PotionEffectDefinition? = effects[itemId]

    fun effectsFor(itemId: String): List<String> {
        val effect = find(itemId) ?: return emptyList()

        return buildList {
            addAll(effect.description)

            val duration = ItemCatalog.find(itemId)?.buffDurationSeconds
            if (duration != null && duration > 0) {
                add("Duration: $duration seconds")
            }
        }
    }
}
