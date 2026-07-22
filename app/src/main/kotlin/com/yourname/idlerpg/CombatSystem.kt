package com.yourname.idlerpg

class CombatSystem {

    fun processCombatTick(state: PlayerGameState, enemy: Enemy): PlayerGameState {
        val playerStats = state.stats
        val currentEnemyHp = enemy.currentHp - playerStats.attackPower
        val playerHp = playerStats.hp - enemy.attackPower

        // Case A: Player defeated enemy
        if (currentEnemyHp <= 0) {
            val updatedGold = playerStats.gold + enemy.goldReward
            
            // Instantly respawn enemy for endless idle fighting
            val respawnedEnemy = enemy.copy(currentHp = enemy.maxHp)
            
            val updatedStats = playerStats.copy(
                hp = if (playerHp <= 0) playerStats.maxHp else playerHp,
                gold = updatedGold,
                activeEnemy = respawnedEnemy
            )

            // Award Combat XP to the Attack Skill
            val attackSkill = state.skills[SkillType.ATTACK] ?: SkillState()
            val newAttackXp = attackSkill.currentXp + enemy.xpReward
            val updatedSkills = state.skills.toMutableMap().apply {
                put(SkillType.ATTACK, attackSkill.copy(currentXp = newAttackXp))
            }

            return state.copy(stats = updatedStats, skills = updatedSkills)
        }

        // Case B: Battle ongoing
        val updatedEnemy = enemy.copy(currentHp = currentEnemyHp)
        val updatedStats = playerStats.copy(
            hp = playerHp.coerceAtLeast(1),
            activeEnemy = updatedEnemy
        )

        return state.copy(stats = updatedStats)
    }
}
