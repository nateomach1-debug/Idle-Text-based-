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

data class OfflineSummary(
    val awaySeconds: Long,
    val skillActionName: String,
    val itemName: String,
    val quantity: Int,
    val xpEarned: Long
)

private fun formatItemName(itemId: String): String =
    itemId.split("_").joinToString(" ") { it.replaceFirstChar { c -> c.uppercase() } }

class GameViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = GameStateRepository(application)

    val accountService = AccountService()
    val progressionService = ProgressionService()
    val inventoryService = InventoryService()
    val sessionManager = SessionManager(application)
    // TODO: replace with a real inventory check once ItemsEquipmentSystem is wired up.
    // Skilling queues don't consume materials, only crafting does, so this is unused for now.
    val offlineIdleService = OfflineIdleService(MaterialAvailabilityCheck { _, _ -> true })

    private var skillActionProgressSeconds: Long = 0

    private val _currentAccountId = MutableStateFlow<String?>(null)
    val currentAccountId: StateFlow<String?> = _currentAccountId.asStateFlow()

    private val _offlineSummary = MutableStateFlow<OfflineSummary?>(null)
    val offlineSummary: StateFlow<OfflineSummary?> = _offlineSummary.asStateFlow()

    private val _currentCharacterId = MutableStateFlow<String?>(null)
    val currentCharacterId: StateFlow<String?> = _currentCharacterId.asStateFlow()

    private val _skills = MutableStateFlow<Map<String, SkillSummary>>(emptyMap())
    val skills: StateFlow<Map<String, SkillSummary>> = _skills.asStateFlow()

    private val _inventoryItems = MutableStateFlow<List<InventorySlotEntry>>(emptyList())
    val inventoryItems: StateFlow<List<InventorySlotEntry>> = _inventoryItems.asStateFlow()

    private val _equippedItems = MutableStateFlow<Map<EquipSlot, String>>(emptyMap())
    val equippedItems: StateFlow<Map<EquipSlot, String>> = _equippedItems.asStateFlow()

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
            delay(30_000L)
            saveGame()
        }
    }
}

override fun onCleared() {
    super.onCleared()
    saveGame()
}
    private var hasLoaded = false

    fun loadGame() {
        if (hasLoaded) return
        hasLoaded = true
        val saved = repository.load() ?: return
        saved.accounts.forEach { accountService.restoreAccount(it) }
        saved.characters.forEach { accountService.restoreCharacter(it) }
        saved.skills.forEach { progressionService.restoreSkill(it) }
        saved.skillingQueues.forEach { offlineIdleService.restoreSkillingQueue(it) }
        saved.lastSeen.forEach { offlineIdleService.restoreLastSeen(it) }
        saved.inventoryItems.forEach { inventoryService.restoreItem(it) }
        saved.equippedSlots.forEach { inventoryService.restoreEquipped(it) }
    }
fun login(email: String, password: String): ServiceResult<Account> {
    val result = accountService.login(email, password)
    if (result is ServiceResult.Success) {
        sessionManager.saveSession(result.value.id)
            _currentAccountId.value = result.value.id
    }
    return result
}
  fun createAccount(email: String, username: String, password: String): ServiceResult<Account> {
    val result = accountService.createAccount(email, username, password, AgeBracket.ADULT_18_PLUS, "US")
    if (result is ServiceResult.Success) {
        sessionManager.saveSession(result.value.id)
            _currentAccountId.value = result.value.id
    }
    return result
  }
  fun tryAutoLogin(): Account? {
    val accountId = sessionManager.getSavedAccountId() ?: return null
    val account = accountService.accountById(accountId) ?: return null
    _currentAccountId.value = account.id
    return account
}

fun logout() {
    sessionManager.clearSession()
    _currentAccountId.value = null
    _currentCharacterId.value = null
}

    fun clearOfflineSummary() {
        _offlineSummary.value = null
    }
    fun saveGame() {
        repository.save(
            accountService.exportAllAccounts(),
            accountService.exportAllCharacters(),
            progressionService.exportAllSkills(),
            offlineIdleService.exportSkillingQueues(),
            offlineIdleService.exportLastSeen(),
            inventoryService.exportAllItems(),
            inventoryService.exportAllEquipped()
        )
    }

    fun selectCharacter(characterId: String) {
        _currentCharacterId.value = characterId

        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.SkillingQueue
        if (queue != null) {
            val result = offlineIdleService.resolveOfflineProgress(characterId)
            if (result is ServiceResult.Success && result.value.actionsCompleted > 0) {
                val skillType = SkillType.valueOf(queue.skillId)
                val action = ActionCatalog.find(skillType, queue.itemId)
                if (action != null) {
                    val xpEarned = action.xpPerAction * result.value.actionsCompleted
                    progressionService.grantXp(characterId, skillType, xpEarned)
                    inventoryService.inventoryFor(characterId).addItem(queue.itemId, result.value.actionsCompleted)
                    _offlineSummary.value = OfflineSummary(
                        awaySeconds = result.value.claimedElapsed.seconds,
                        skillActionName = action.displayName,
                        itemName = formatItemName(queue.itemId),
                        quantity = result.value.actionsCompleted,
                        xpEarned = xpEarned
                    )
                }
            }
        }

        offlineIdleService.recordLastSeen(characterId)
        skillActionProgressSeconds = 0
        refreshSkills()
        refreshInventory()
    }

    fun startSkillAction(skillType: SkillType, itemId: String) {
        val characterId = _currentCharacterId.value ?: return
        val action = ActionCatalog.find(skillType, itemId) ?: return
        offlineIdleService.stopQueue(characterId)
        offlineIdleService.startSkillingQueue(characterId, skillType.name, itemId, action.secondsPerAction)
        offlineIdleService.recordLastSeen(characterId)
        skillActionProgressSeconds = 0
    }

    fun stopSkillAction() {
        val characterId = _currentCharacterId.value ?: return
        offlineIdleService.stopQueue(characterId)
        skillActionProgressSeconds = 0
    }

    private fun tickSkilling() {
        val characterId = _currentCharacterId.value ?: return
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.SkillingQueue ?: return

        skillActionProgressSeconds += 1
        if (skillActionProgressSeconds < queue.secondsPerAction) return

        val actionsCompleted = skillActionProgressSeconds / queue.secondsPerAction
        skillActionProgressSeconds %= queue.secondsPerAction

        val skillType = SkillType.valueOf(queue.skillId)
        val action = ActionCatalog.find(skillType, queue.itemId)
        if (action != null) {
            progressionService.grantXp(characterId, skillType, action.xpPerAction * actionsCompleted)
            inventoryService.inventoryFor(characterId).addItem(queue.itemId, actionsCompleted.toInt())
            refreshSkills()
            refreshInventory()
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

    fun refreshInventory() {
        val characterId = _currentCharacterId.value ?: return
        val inv = inventoryService.inventoryFor(characterId)
        _inventoryItems.value = inv.allItems()
        _equippedItems.value = inv.allEquipped()
    }
}
