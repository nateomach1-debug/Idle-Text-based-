package com.yourname.idlerpg.data

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.yourname.idlerpg.*
import com.yourname.idlerpg.ui.screens.SkillSummary
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class GameViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = GameStateRepository(application)

    val accountService = AccountService()
    val progressionService = ProgressionService()
    val sessionManager = SessionManager(application)
    // TODO: replace with a real inventory check once ItemsEquipmentSystem is wired up.
    // Skilling queues don't consume materials, only crafting does, so this is unused for now.
    val offlineIdleService = OfflineIdleService(MaterialAvailabilityCheck { _, _ -> true })

    private val _currentCharacterId = MutableStateFlow<String?>(null)
    val currentCharacterId: StateFlow<String?> = _currentCharacterId.asStateFlow()

    private val _skills = MutableStateFlow<Map<String, SkillSummary>>(emptyMap())
    val skills: StateFlow<Map<String, SkillSummary>> = _skills.asStateFlow()

    init {
        viewModelScope.launch(Dispatchers.Default) {
            while (true) {
                delay(1000L)
                tickSkilling()
            }
        }
    }
init {
    viewModelScope.launch(Dispatchers.Default) {
        while (true) {
            delay(1000L)
            tickSkilling()
        }
    }
    viewModelScope.launch(Dispatchers.Default) {
        while (true) {
            delay(30_000L)
            saveGame()
        }
    }
}

override fun onCleared() {
    super.onCleared()
    saveGame()
}
    fun loadGame() {
        val saved = repository.load() ?: return
        saved.accounts.forEach { accountService.restoreAccount(it) }
        saved.characters.forEach { accountService.restoreCharacter(it) }
        saved.skills.forEach { progressionService.restoreSkill(it) }
    }
fun login(email: String, password: String): ServiceResult<Account> {
    val result = accountService.login(email, password)
    if (result is ServiceResult.Success) {
        sessionManager.saveSession(result.value.id)
    }
    return result
}
  fun createAccount(email: String, username: String, password: String): ServiceResult<Account> {
    val result = accountService.createAccount(email, username, password, AgeBracket.ADULT_18_PLUS, "US")
    if (result is ServiceResult.Success) {
        sessionManager.saveSession(result.value.id)
    }
    return result
  }
  fun tryAutoLogin(): Account? {
    val accountId = sessionManager.getSavedAccountId() ?: return null
    return accountService.accountById(accountId)
}

fun logout() {
    sessionManager.clearSession()
}
    fun saveGame() {
        repository.save(
            accountService.exportAllAccounts(),
            accountService.exportAllCharacters(),
            progressionService.exportAllSkills()
        )
    }

    fun selectCharacter(characterId: String) {
        _currentCharacterId.value = characterId
        offlineIdleService.recordLastSeen(characterId)
        refreshSkills()
    }

    fun startSkillAction(skillType: SkillType, itemId: String) {
        val characterId = _currentCharacterId.value ?: return
        val action = ActionCatalog.find(skillType, itemId) ?: return
        offlineIdleService.stopQueue(characterId)
        offlineIdleService.startSkillingQueue(characterId, skillType.name, itemId, action.secondsPerAction)
        offlineIdleService.recordLastSeen(characterId)
    }

    fun stopSkillAction() {
        val characterId = _currentCharacterId.value ?: return
        offlineIdleService.stopQueue(characterId)
    }

    private fun tickSkilling() {
        val characterId = _currentCharacterId.value ?: return
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.SkillingQueue ?: return

        val result = offlineIdleService.resolveOfflineProgress(characterId)
        offlineIdleService.recordLastSeen(characterId)

        if (result is ServiceResult.Success && result.value.actionsCompleted > 0) {
            val skillType = SkillType.valueOf(queue.skillId)
            val action = ActionCatalog.find(skillType, queue.itemId)
            if (action != null) {
                progressionService.grantXp(characterId, skillType, action.xpPerAction * result.value.actionsCompleted)
                refreshSkills()
            }
        }
    }

    fun refreshSkills() {
        val characterId = _currentCharacterId.value ?: return
        val book = progressionService.skillBookFor(characterId)
        _skills.value = book.all().associate { skill ->
            val level = LevelCurve.levelForXp(skill.xp)
            val xpAtLevelStart = LevelCurve.xpRequiredForLevel(level)
            val xpAtNextLevel = LevelCurve.xpRequiredForLevel(level + 1)
            val displayName = skill.type.name.lowercase().replaceFirstChar { it.uppercase() }
            skill.type.name to SkillSummary(
                skillId = skill.type.name,
                displayName = displayName,
                level = level,
                currentXp = skill.xp - xpAtLevelStart,
                xpToNextLevel = xpAtNextLevel - skill.xp
            )
        }
    }
}
