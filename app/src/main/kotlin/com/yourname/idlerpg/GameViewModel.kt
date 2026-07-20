package com.yourname.idlerpg.data

import android.app.Application
import androidx.lifecycle.AndroidViewModel

// =========================================================
// GAME VIEWMODEL
// Single shared holder for every backend service. Survives
// screen navigation and configuration changes (rotation).
// Other 11 services are instantiated here now; save/load
// support gets added to each incrementally as we wire it.
// =========================================================

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
    val offlineIdleService = OfflineIdleService(materialCheck = { _, _ -> true }) // stub, refined when Items is wired
    val flagRegistry = FlagRegistry()
    val rateLimitService = RateLimitService(flagRegistry)

    private val repository = GameStateRepository(application)

    /** Call after any meaningful change (account created, etc.) to persist immediately. */
    fun saveGame() {
        repository.save(
            accounts = accountService.exportAllAccounts(),
            characters = accountService.exportAllCharacters()
        )
    }

    /** Call once on app launch to restore prior state, if any exists. */
    fun loadGame() {
        val saved = repository.load() ?: return
        saved.accounts.forEach { accountService.restoreAccount(it) }
        saved.characters.forEach { accountService.restoreCharacter(it) }
    }
}
