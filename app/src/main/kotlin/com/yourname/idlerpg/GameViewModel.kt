package com.yourname.idlerpg

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import com.yourname.idlerpg.model.GameUiState
import com.yourname.idlerpg.model.Skill      

class GameViewModel(
    private val repository: GameStateRepository = GameStateRepository(),
    private val skillSystem: SkillProgressionSystem = SkillProgressionSystem(),
    private val combatSystem: CombatSystem = CombatSystem(),
    private val offlineSystem: OfflineIdleMechanicsSystem = OfflineIdleMechanicsSystem()
) : ViewModel() {

    private val _uiState = MutableStateFlow(repository.getGameState())
    val uiState: StateFlow<PlayerGameState> = _uiState.asStateFlow()

    init {
        processOfflineProgress()
        startGameLoop()
    }

    private fun processOfflineProgress() {
        val currentTime = System.currentTimeMillis()
        val lastSaved = _uiState.value.lastSavedTimestamp
            val elapsedSeconds = (currentTime - lastSaved) / 1000L

        if (elapsedSeconds > 5) {
                _uiState.update { currentState: GameUiState ->
                offlineSystem.calculateOfflineGains(currentState, elapsedSeconds)
            }
        }
    }

    private fun startGameLoop() {
        viewModelScope.launch(Dispatchers.Default) {
            while (true) {
                delay(1000L) // Runs once every 1000ms (1 second)
                tick()
            }
        }
    }

    private fun tick() {
          _uiState.update { currentState: GameUiState ->
            var updatedState = currentState.copy(lastSavedTimestamp = System.currentTimeMillis())

            // 1. Tick Active Skill (if performing one)
                updatedState.stats.activeSkill?.let { activeSkill: Skill ->
                updatedState = skillSystem.processSkillTick(updatedState, activeSkill)
            }

            // 2. Tick Active Combat (if fighting an enemy)
               updatedState.stats.activeEnemy?.let { enemy: Enemy ->
                updatedState = combatSystem.processCombatTick(updatedState, enemy)
            }

            repository.saveGameState(updatedState)
            updatedState
        }
    }

    // --- Actions called by UI screens ---

    fun startSkillAction(skill: SkillType) {
            _uiState.update { state: GameUiState ->
            // Using .copy() creates a new instance so StateFlow properly triggers a UI refresh
            state.copy(
                stats = state.stats.copy(
                    activeEnemy = null, // Stop combat if starting a skill
                    activeSkill = skill
                )
            )
        }
    }

    fun startCombat(targetEnemy: Enemy) {
            _uiState.update { state: GameUiState ->
            state.copy(
                stats = state.stats.copy(
                    activeSkill = null, // Stop skill if starting combat
                    activeEnemy = targetEnemy.copy(currentHp = targetEnemy.maxHp)
                )
            )
        }
    }

    fun stopAllActions() {
            _uiState.update { state: GameUiState ->
            state.copy(
                stats = state.stats.copy(
                    activeSkill = null,
                    activeEnemy = null
                )
            )
        }
    }
}
