package com.yourname.idlerpg

class SkillProgressionSystem {

    fun processSkillTick(state: PlayerGameState, skill: SkillType): PlayerGameState {
        val currentSkillState = state.skills[skill] ?: SkillState()
        val addedXp = 15L // Base XP earned per second

        var newXp = currentSkillState.currentXp + addedXp
        var newLevel = currentSkillState.level
        var nextLevelXp = currentSkillState.xpToNextLevel

        // Check if player levels up
        if (newXp >= nextLevelXp) {
            newLevel++
            nextLevelXp = (nextLevelXp * 1.5).toLong()
        }

        val updatedSkills = state.skills.toMutableMap().apply {
            put(skill, SkillState(level = newLevel, currentXp = newXp, xpToNextLevel = nextLevelXp))
        }

        // Generate resource items in inventory based on active skill
        val lootItem = when (skill) {
            SkillType.WOODCUTTING -> "Oak Log"
            SkillType.MINING -> "Copper Ore"
            else -> "Resource"
        }
        val updatedInventory = state.inventory.toMutableMap().apply {
            put(lootItem, (get(lootItem) ?: 0) + 1)
        }

        return state.copy(
            skills = updatedSkills,
            inventory = updatedInventory
        )
    }
}
