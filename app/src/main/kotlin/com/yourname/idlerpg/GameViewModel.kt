package com.yourname.idlerpg

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.yourname.idlerpg.ui.screens.SkillSummary
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class GameViewModel(
    private val accountService: AccountService = AccountService(),
    private val progressionService: ProgressionService = ProgressionService()
) : ViewModel() {

    private val _currentAccountId = MutableStateFlow<String?>(null)
    val currentAccountId: StateFlow<String?> = _currentAccountId.asStateFlow()

    private val _currentCharacterId = MutableStateFlow<String?>(null)
    val currentCharacterId: StateFlow<String?> = _currentCharacterId.asStateFlow()

    private val _skills = MutableStateFlow<Map<String, SkillSummary>>(emptyMap())
    val skills: StateFlow<Map<String, SkillSummary>> = _skills.asStateFlow()

    private val _authError = MutableStateFlow<String?>(null)
    val authError: StateFlow<String?> = _authError.asStateFlow()

    fun login(email: String, password: String) {
        // TODO: AccountService has no login-by-credentials lookup yet (no accountByEmail).
        // Placeholder until that's added — flag this back to me when we get to LoginScreen wiring.
        _authError.value = "Login not yet implemented in AccountService."
    }

    fun createAccount(email: String, username: String, password: String) {
        when (val result = accountService.createAccount(
            email = email, username = username, password = password,
            ageBracket = AgeBracket.ADULT_18_PLUS, region = "unknown"
        )) {
            is ServiceResult.Success -> {
                _currentAccountId.value = result.value.id
                _authError.value = null
            }
            is ServiceResult.Failure -> _authError.value = result.reason
        }
    }

    fun charactersForCurrentAccount(): List<Character> {
        val accountId = _currentAccountId.value ?: return emptyList()
        return accountService.charactersFor(accountId)
    }

    fun createCharacter(displayName: String, avatarId: String) {
        val accountId = _currentAccountId.value ?: return
        when (val result = accountService.createCharacter(accountId, displayName, avatarId)) {
            is ServiceResult.Success -> selectCharacter(result.value.id)
            is ServiceResult.Failure -> _authError.value = result.reason
        }
    }

    fun selectCharacter(characterId: String) {
        _currentCharacterId.value = characterId
        refreshSkills()
    }

    fun refreshSkills() {
        val characterId = _currentCharacterId.value ?: return
        val book = progressionService.skillBookFor(characterId)
        _skills.value = book.all().associate { skill ->
            val level = LevelCurve.levelForXp(skill.xp)
            val xpAtLevelStart = LevelCurve.xpRequiredForLevel(level)
            val xpAtNextLevel = LevelCurve.xpRequiredForLevel(level + 1)
            val summary = SkillSummary(
                skillId = skill.type.name,
                displayName = skill.type.name.lowercase().replaceFirstChar { it.uppercase() },
                level = level,
                currentXp = skill.xp - xpAtLevelStart,
                xpToNextLevel = xpAtNextLevel - skill.xp
            )
            skill.type.name to summary
        }
    }
}
