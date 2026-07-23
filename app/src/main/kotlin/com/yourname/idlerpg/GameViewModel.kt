package com.yourname.idlerpg.data

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import com.yourname.idlerpg.*

class GameViewModel(application: Application) : AndroidViewModel(application) {

    val accountService = AccountService()
    val progressionService = ProgressionService()
    val combatService = CombatService()
    val economyMonitoringService = EconomyMonitoringService()
    val marketService = MarketService(economyMonitoringService)
    val guildService = GuildService()
    val chatModerationService = ChatModerationService()
    val questService = QuestService()
    val dailyTaskService = DailyTaskService()
    val offlineIdleService = OfflineIdleService(materialCheck = { _, _ -> true })
    val flagRegistry = FlagRegistry()
    val rateLimitService = RateLimitService(flagRegistry)

    private val repository = GameStateRepository(application)

    fun saveGame() {
        repository.save(
            accounts = accountService.exportAllAccounts(),
            characters = accountService.exportAllCharacters(),
            skills = progressionService.exportAllSkills()
        )
    }

    fun loadGame() {
        val saved = repository.load() ?: return
        saved.accounts.forEach { accountService.restoreAccount(it) }
        saved.characters.forEach { accountService.restoreCharacter(it) }
        saved.skills.forEach { progressionService.restoreSkill(it) }
    }
}
