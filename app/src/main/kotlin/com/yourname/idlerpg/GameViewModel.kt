package com.yourname.idlerpg.data

import io.github.jan.supabase.auth.status.SessionStatus

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.yourname.idlerpg.*
import com.yourname.idlerpg.ui.screens.SkillSummary
import com.yourname.idlerpg.ui.screens.CombatViewData
import com.yourname.idlerpg.ui.screens.CombatViewState
import com.yourname.idlerpg.ui.screens.CombatLogEntry
import com.yourname.idlerpg.ui.screens.ZoneSummary
import com.yourname.idlerpg.ui.screens.GuildHomeState
import com.yourname.idlerpg.ui.screens.GuildLeaderboardEntry
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.time.Instant
import kotlin.random.Random
import io.github.jan.supabase.auth.auth
import com.yourname.idlerpg.ui.components.ChatChannelUi
import com.yourname.idlerpg.ui.components.ChatMessageUi
import com.yourname.idlerpg.ui.components.DmConversationSummary
import com.yourname.idlerpg.ui.screens.VendorBuyCatalog

data class OfflineSummary(
    val awaySeconds: Long,
    val skillActionName: String,
    val itemName: String,
    val quantity: Int,
    val xpEarned: Long
)

data class SaleNotification(
    val itemName: String,
    val quantity: Int,
    val netProceeds: Long
)

data class ActiveQueueInfo(
    val label: String,
    val secondsPerAction: Long,
    val startedAt: Instant
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

    private val _pendingSaleNotifications = MutableStateFlow<List<SaleNotification>>(emptyList())
    val pendingSaleNotifications: StateFlow<List<SaleNotification>> = _pendingSaleNotifications.asStateFlow()

    private val _currentCharacterId = MutableStateFlow<String?>(null)
    val currentCharacterId: StateFlow<String?> = _currentCharacterId.asStateFlow()

    private val _skills = MutableStateFlow<Map<String, SkillSummary>>(emptyMap())
    val skills: StateFlow<Map<String, SkillSummary>> = _skills.asStateFlow()

    private val _inventoryItems = MutableStateFlow<List<InventorySlotEntry>>(emptyList())
    val inventoryItems: StateFlow<List<InventorySlotEntry>> = _inventoryItems.asStateFlow()

    private val _equippedItems = MutableStateFlow<Map<EquipSlot, String>>(emptyMap())
    val equippedItems: StateFlow<Map<EquipSlot, String>> = _equippedItems.asStateFlow()

    val economyMonitoring = EconomyMonitoringService()
    val marketService = MarketService(economyMonitoring)
    val combatService = CombatService()

    // =========================================================
    // SUPABASE AUTH (guild/chat multiplayer only - local play never depends on this)
    // =========================================================

    private val _supabaseAuthState = MutableStateFlow(SupabaseAuthState.SIGNED_OUT)
    val supabaseAuthState: StateFlow<SupabaseAuthState> = _supabaseAuthState.asStateFlow()

    private val _supabaseAuthError = MutableStateFlow<String?>(null)
    val supabaseAuthError: StateFlow<String?> = _supabaseAuthError.asStateFlow()

    // Fire-and-forget: runs in the background after a successful LOCAL login/account
    // creation. If this fails (no network, Supabase down, etc.) local gameplay is
    // completely unaffected - only guild/chat multiplayer stays unavailable.
    private fun syncSupabaseAuth(email: String, password: String, isNewAccount: Boolean) {
        viewModelScope.launch {
            _supabaseAuthState.value = SupabaseAuthState.SIGNING_IN
            try {
                val auth = SupabaseClientProvider.client.auth
                if (isNewAccount) {
                    try {
                        auth.signUpWith(io.github.jan.supabase.auth.providers.builtin.Email) {
                            this.email = email
                            this.password = password
                        }
                    } catch (signUpError: Exception) {
                        val message = signUpError.message ?: ""
                        if (message.contains("user_already_exists", ignoreCase = true) ||
                            message.contains("already registered", ignoreCase = true)
                        ) {
                            // Account already exists on the server (e.g. new phone, lost
                            // local account, re-registered with the same email) - log in
                            // to that existing account instead of failing outright.
                            auth.signInWith(io.github.jan.supabase.auth.providers.builtin.Email) {
                                this.email = email
                                this.password = password
                            }
                        } else {
                            throw signUpError
                        }
                    }
                } else {
                    try {
                        auth.signInWith(io.github.jan.supabase.auth.providers.builtin.Email) {
                            this.email = email
                            this.password = password
                        }
                    } catch (signInError: Exception) {
                        // Local account existed before Supabase sync was added - no
                        // matching Supabase account exists yet. Lazily create one now
                        // with the same credentials, so future logins sign in normally.
                        auth.signUpWith(io.github.jan.supabase.auth.providers.builtin.Email) {
                            this.email = email
                            this.password = password
                        }
                    }
                }
                _supabaseAuthState.value = SupabaseAuthState.SIGNED_IN
            } catch (e: Exception) {
                _supabaseAuthState.value = SupabaseAuthState.ERROR
                _supabaseAuthError.value = e.message ?: e.toString()
            }
        }
    }

        // =========================================================
    // GUILD (Supabase-backed, best-effort - local play never depends on this)
    // =========================================================

    private val _guildHomeState = MutableStateFlow<GuildHomeState?>(null)
    val guildHomeState: StateFlow<GuildHomeState?> = _guildHomeState.asStateFlow()

    private val _guildId = MutableStateFlow<String?>(null)

    private val _guildLeaderboard = MutableStateFlow<List<GuildLeaderboardEntry>>(emptyList())
    val guildLeaderboard: StateFlow<List<GuildLeaderboardEntry>> = _guildLeaderboard.asStateFlow()

    private val _browsableGuilds = MutableStateFlow<List<GuildBrowseEntry>>(emptyList())
    val browsableGuilds: StateFlow<List<GuildBrowseEntry>> = _browsableGuilds.asStateFlow()

    private val _guildActionError = MutableStateFlow<String?>(null)
    val guildActionError: StateFlow<String?> = _guildActionError.asStateFlow()

    // The Supabase characters.id for the current character - a DIFFERENT
    // id than _currentCharacterId (which is the local Room-database id).
    // Every Supabase RPC call needs this one, not the local id.
    private val _currentSupabaseCharacterId = MutableStateFlow<String?>(null)
    val currentSupabaseCharacterId: StateFlow<String?> = _currentSupabaseCharacterId.asStateFlow()

    private val _characterSyncError = MutableStateFlow<String?>(null)
    val characterSyncError: StateFlow<String?> = _characterSyncError.asStateFlow()

    fun refreshGuildHome() {
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val membership = SupabaseGuildRepository.findMembership(characterId)
            _guildId.value = membership?.first
            if (membership == null) {
                _guildHomeState.value = null
                _guildLeaderboard.value = emptyList()
                _browsableGuilds.value = SupabaseGuildRepository.listGuilds()
            } else {
                _guildHomeState.value = SupabaseGuildRepository.fetchGuildHome(characterId)
                _guildLeaderboard.value = SupabaseGuildRepository.fetchLeaderboard(characterId)
            }
        }
    }

    fun createGuild(name: String) {
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseGuildRepository.createGuild(name, characterId)
            result.onFailure { _guildActionError.value = it.message }
            refreshGuildHome()
        }
    }

    fun joinGuild(guildId: String) {
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseGuildRepository.joinGuild(guildId, characterId)
            result.onFailure { _guildActionError.value = it.message }
            refreshGuildHome()
        }
    }

    fun kickGuildMember(targetCharacterId: String) {
        val guildId = _guildId.value ?: return
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseGuildRepository.kickMember(guildId, characterId, targetCharacterId)
            result.onFailure { _guildActionError.value = it.message }
            refreshGuildHome()
        }
    }

    fun promoteGuildMemberToOfficer(targetCharacterId: String) {
        val guildId = _guildId.value ?: return
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseGuildRepository.promoteToOfficer(guildId, characterId, targetCharacterId)
            result.onFailure { _guildActionError.value = it.message }
            refreshGuildHome()
        }
    }

    fun promoteGuildMemberToLeader(targetCharacterId: String) {
        val guildId = _guildId.value ?: return
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseGuildRepository.promoteToLeader(guildId, characterId, targetCharacterId)
            result.onFailure { _guildActionError.value = it.message }
            refreshGuildHome()
        }
    }
    // =========================================================
    // MODERATION (Supabase-backed, moderator-only, best-effort)
    // =========================================================

    private val _isModerator = MutableStateFlow(false)
    val isModerator: StateFlow<Boolean> = _isModerator.asStateFlow()

    private val _moderationState = MutableStateFlow(ModerationState())
    val moderationState: StateFlow<ModerationState> = _moderationState.asStateFlow()

    fun checkModeratorStatus() {
        val profileId = SupabaseClientProvider.client.auth.currentUserOrNull()?.id ?: return
        viewModelScope.launch {
            _isModerator.value = SupabaseModerationRepository.isCallerModerator(profileId)
        }
    }

    fun refreshModeration() {
        if (!_isModerator.value) return
        viewModelScope.launch {
            _moderationState.value = _moderationState.value.copy(isLoading = true)
            val reports = SupabaseModerationRepository.fetchPendingReports()
            val appeals = SupabaseModerationRepository.fetchPendingAppeals()
            _moderationState.value = ModerationState(reports, appeals, isLoading = false)
        }
    }

    fun resolveReport(reportId: String, actionTaken: Boolean) {
        viewModelScope.launch {
            SupabaseModerationRepository.resolveReport(reportId, actionTaken)
            refreshModeration()
        }
    }

    fun resolveAppeal(appealId: String, grant: Boolean, notes: String) {
        viewModelScope.launch {
            SupabaseModerationRepository.resolveAppeal(appealId, grant, notes)
            refreshModeration()
        }
    }

    fun muteCharacterAsModerator(characterId: String, durationSeconds: Int, reason: String) {
        viewModelScope.launch {
            SupabaseModerationRepository.muteCharacter(characterId, durationSeconds, reason)
        }
    }

    fun unmuteCharacterAsModerator(characterId: String) {
        viewModelScope.launch {
            SupabaseModerationRepository.unmuteCharacter(characterId)
        }
    }
    // =========================================================
    // CHAT
    // =========================================================

    private val _selectedChatChannel = MutableStateFlow(ChatChannelUi.GLOBAL)
    val selectedChatChannel: StateFlow<ChatChannelUi> = _selectedChatChannel.asStateFlow()

    private val _chatMessages = MutableStateFlow<List<ChatMessageUi>>(emptyList())
    val chatMessages: StateFlow<List<ChatMessageUi>> = _chatMessages.asStateFlow()

    private val _dmConversations = MutableStateFlow<List<DmConversationSummary>>(emptyList())
    val dmConversations: StateFlow<List<DmConversationSummary>> = _dmConversations.asStateFlow()

    private val _selectedDmCharacterId = MutableStateFlow<String?>(null)
    val selectedDmCharacterId: StateFlow<String?> = _selectedDmCharacterId.asStateFlow()

    // Not exposed as UI state - internal detail of which DM channel row
    // backs the currently selected DM conversation.
    private var selectedDmChannelId: String? = null

    private val _globalChatOptOut = MutableStateFlow(false)
    val globalChatOptOut: StateFlow<Boolean> = _globalChatOptOut.asStateFlow()

    private val _chatActionError = MutableStateFlow<String?>(null)
    val chatActionError: StateFlow<String?> = _chatActionError.asStateFlow()

    private val _marketActionError = MutableStateFlow<String?>(null)
    val marketActionError: StateFlow<String?> = _marketActionError.asStateFlow()

    private suspend fun resolveChatChannelId(channel: ChatChannelUi): String? {
        return when (channel) {
            ChatChannelUi.GUILD -> _guildId.value?.let {
                SupabaseChatRepository.getOrCreateGuildChannel(it).getOrNull()
            }
            ChatChannelUi.DMS -> selectedDmChannelId
            else -> SupabaseChatRepository.fetchSingletonChannelId(channel)
        }
    }

    fun selectChatChannel(channel: ChatChannelUi) {
        _selectedChatChannel.value = channel
        if (channel == ChatChannelUi.DMS) {
            refreshDmConversations()
            _chatMessages.value = if (selectedDmChannelId != null) _chatMessages.value else emptyList()
        } else {
            refreshChatMessages()
        }
    }

    fun refreshChatMessages() {
        val characterId = _currentSupabaseCharacterId.value ?: return
        val channel = _selectedChatChannel.value
        viewModelScope.launch {
            val channelId = resolveChatChannelId(channel)
            if (channelId == null) {
                _chatMessages.value = emptyList()
                return@launch
            }
            _chatMessages.value = SupabaseChatRepository.fetchChannelMessages(characterId, channelId, channel)
        }
    }

    fun sendChatMessage(content: String) {
        if (content.isBlank()) return
        val characterId = _currentSupabaseCharacterId.value ?: return
        val channel = _selectedChatChannel.value
        viewModelScope.launch {
            val channelId = resolveChatChannelId(channel)
            if (channelId == null) {
                _chatActionError.value = "Could not resolve chat channel."
                return@launch
            }
            val result = SupabaseChatRepository.sendMessage(characterId, channelId, content)
            result.onFailure { _chatActionError.value = it.message }
            refreshChatMessages()
        }
    }

    fun refreshDmConversations() {
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            _dmConversations.value = SupabaseChatRepository.fetchDmConversations(characterId)
        }
    }

    // Also used by the MESSAGE_PLAYER chat action to jump into a DM.
    fun selectDmConversation(otherCharacterId: String) {
        val characterId = _currentSupabaseCharacterId.value ?: return
        _selectedDmCharacterId.value = otherCharacterId
        viewModelScope.launch {
            val result = SupabaseChatRepository.getOrCreateDmChannel(characterId, otherCharacterId)
            result.onFailure {
                _chatActionError.value = it.message
                return@launch
            }
            selectedDmChannelId = result.getOrNull()
            refreshChatMessages()
        }
    }

    fun reportChatMessage(message: ChatMessageUi, category: String, reason: String) {
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseChatRepository.reportMessage(characterId, message.id, category, reason)
            result.onFailure { _chatActionError.value = it.message }
            refreshChatMessages()
        }
    }

    fun selfMuteCharacter(targetCharacterId: String) {
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseChatRepository.selfMute(characterId, targetCharacterId)
            result.onFailure { _chatActionError.value = it.message }
            refreshChatMessages()
        }
    }

    fun toggleGlobalChatOptOut(optOut: Boolean) {
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseChatRepository.setGlobalChatOptOut(characterId, optOut)
            result.onFailure {
                _chatActionError.value = it.message
                return@launch
            }
            _globalChatOptOut.value = optOut
        }
    }

    fun loadInitialChatState() {
        refreshChatMessages()
        val characterId = _currentSupabaseCharacterId.value
        if (characterId != null) {
            viewModelScope.launch {
                _globalChatOptOut.value = SupabaseChatRepository.getGlobalChatOptOut(characterId)
            }
        }
    }

    fun blockCharacter(targetCharacterId: String) {
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseChatRepository.blockCharacter(characterId, targetCharacterId)
            result.onFailure { _chatActionError.value = it.message }
            refreshChatMessages()
        }
    }
        // =========================================================
    // COMBAT
    // =========================================================

    private val _trainingSkill = MutableStateFlow(SkillType.ATTACK)
    val trainingSkill: StateFlow<SkillType> = _trainingSkill.asStateFlow()

    private val _trainingSkillLevel = MutableStateFlow(1)
    val trainingSkillLevel: StateFlow<Int> = _trainingSkillLevel.asStateFlow()

    private val _combatViewData = MutableStateFlow<CombatViewData?>(null)
    val combatViewData: StateFlow<CombatViewData?> = _combatViewData.asStateFlow()

    private val _combatHp = MutableStateFlow<Pair<Int, Int>?>(null)
    val combatHp: StateFlow<Pair<Int, Int>?> = _combatHp.asStateFlow()

    private var lastHitChancePercent: Double? = null
    private var lastDamageDealt: Int? = null
    private val combatLogFor: MutableMap<String, MutableList<CombatLogEntry>> = mutableMapOf()

    val zoneSummaries: List<ZoneSummary>
        get() = ZoneCatalog.zones.sortedBy { it.levelRequirement }.map { zone ->
            ZoneSummary(
                zoneId = zone.id,
                name = zone.name,
                levelRequirement = zone.levelRequirement,
                monsterNames = zone.monsters.map { it.name }
            )
        }

    val allowedTrainingSkills: List<SkillType>
        get() {
            val characterId = _currentCharacterId.value ?: return listOf(SkillType.DEFENSE)
            val style = equippedWeapon(characterId)?.style ?: CombatStyle.MELEE
            return CombatSkillRules.allowedTrainingSkills(style)
        }

    // Placeholder max-HP formula until a dedicated stat exists: base 100 + 5 per Defense level above 1.
    // Same "reasonable placeholder, tune later" approach used for food/potion heal amounts.
    private fun maxHpFor(characterId: String): Int {
        val defenseLevel = LevelCurve.levelForXp(progressionService.skillBookFor(characterId).get(SkillType.DEFENSE).xp)
        return 100 + (defenseLevel - 1) * 5
    }

    private fun equippedWeapon(characterId: String): Weapon? {
        val itemId = _equippedItems.value[EquipSlot.WEAPON] ?: return null
        val def = ItemCatalog.items.find { it.id == itemId } ?: return null
        val style = def.combatStyle ?: return null
        return Weapon(
            name = def.name,
            style = style,
            attackSpeedSeconds = 2.4,
            baseAccuracy = 5 + def.stats.accuracyBonus,
            baseMaxHit = 1 + def.stats.maxHitBonus
        )
    }

    private fun skillLevel(characterId: String, skillType: SkillType): Int =
        LevelCurve.levelForXp(progressionService.skillBookFor(characterId).get(skillType).xp)

    fun setTrainingSkill(skillType: SkillType) {
        _trainingSkill.value = skillType
        val characterId = _currentCharacterId.value
        _trainingSkillLevel.value = characterId?.let { skillLevel(it, skillType) } ?: 1
    }

    private fun refreshCombatHp() {
        val characterId = _currentCharacterId.value ?: return
        val state = combatService.stateFor(characterId, maxHpFor(characterId))
        _combatHp.value = state.currentHp to state.maxHp
    }

    fun enterCombatZone(zoneId: String): ServiceResult<CombatSession> {
        val characterId = _currentCharacterId.value ?: return ServiceResult.Failure("No character selected.")
        // Entering combat stops any active skilling/crafting queue - only one
        // activity can run at a time.
        offlineIdleService.stopQueue(characterId)
        skillActionProgressSeconds = 0
        craftActionProgressSeconds = 0
        refreshActiveQueue()
        combatService.stateFor(characterId, maxHpFor(characterId))
        val result = combatService.enterZone(characterId, zoneId, skillLevel(characterId, _trainingSkill.value))
        if (result is ServiceResult.Success) {
            combatLogFor.getOrPut(characterId) { mutableListOf() }.apply {
                clear()
                add(CombatLogEntry("Entered " + result.value.zone.name + "."))
            }
            refreshCombatView()
        }
        return result
    }

    fun leaveCombatZone() {
        val characterId = _currentCharacterId.value ?: return
        combatService.leaveZone(characterId)
        _combatViewData.value = null
    }

    private fun refreshCombatView() {
        val characterId = _currentCharacterId.value ?: return
        val state = combatService.stateFor(characterId, maxHpFor(characterId))
        _combatHp.value = state.currentHp to state.maxHp
        val session = state.session
        if (session == null) {
            _combatViewData.value = null
            return
        }
        val log = combatLogFor.getOrPut(characterId) { mutableListOf() }
        _combatViewData.value = CombatViewData(
            zoneName = session.zone.name,
            viewState = if (session.state == SessionState.IN_COMBAT) CombatViewState.IN_COMBAT else CombatViewState.SEARCHING,
            searchEndsAt = session.searchEndsAt,
            monsterName = session.currentMonster?.name,
            monsterCurrentHp = session.currentMonster?.let { session.currentMonsterHealth },
            monsterMaxHp = session.currentMonster?.maxHealth,
            playerCurrentHp = state.currentHp,
            playerMaxHp = state.maxHp,
            lastHitChancePercent = lastHitChancePercent,
            lastDamageDealt = lastDamageDealt,
            combatLog = log
        )
    }

    private fun tickCombat() {
        val characterId = _currentCharacterId.value ?: return
        val state = combatService.stateFor(characterId, maxHpFor(characterId))

        if (state.recovery.isRecovering()) {
            refreshCombatHp()
            return
        }
        if (combatService.resolveRecoveryIfReady(characterId) is ServiceResult.Success) {
            refreshCombatHp()
        }

        val session = state.session ?: return

        if (session.state == SessionState.SEARCHING) {
            val result = combatService.resolveSearchIfReady(characterId)
            if (result is ServiceResult.Success) {
                combatLogFor.getOrPut(characterId) { mutableListOf() }
                    .add(CombatLogEntry(result.value.name + " appears!"))
            }
            refreshCombatView()
            return
        }

        if (session.state != SessionState.IN_COMBAT) return

        val weapon = equippedWeapon(characterId)
        val trainingSkill = _trainingSkill.value
        val accuracy: Int
        val maxHit: Int
        when (weapon?.style) {
            CombatStyle.MAGIC -> {
                val magicLevel = skillLevel(characterId, SkillType.MAGIC)
                accuracy = magicLevel * 2 + weapon.baseAccuracy
                maxHit = (magicLevel / 3) + weapon.baseMaxHit
            }
            CombatStyle.RANGED -> {
                val archeryLevel = skillLevel(characterId, SkillType.ARCHERY)
                accuracy = archeryLevel * 2 + weapon.baseAccuracy
                maxHit = (archeryLevel / 3) + weapon.baseMaxHit
            }
            else -> {
                val attackLevel = skillLevel(characterId, SkillType.ATTACK)
                val strengthLevel = skillLevel(characterId, SkillType.STRENGTH)
                accuracy = attackLevel * 2 + (weapon?.baseAccuracy ?: 5)
                maxHit = (strengthLevel / 3) + (weapon?.baseMaxHit ?: 1)
            }
        }

        val loadout = CombatLoadout(
            style = weapon?.style ?: CombatStyle.MELEE,
            trainingSkill = trainingSkill,
            equippedWeapon = weapon,
            equippedSpell = null,
            autoHealThresholdPercent = inventoryService.inventoryFor(characterId).autoHealThresholdPercent,
            autoFleeThresholdPercent = inventoryService.inventoryFor(characterId).autoFleeThresholdPercent
        )

        val result = combatService.resolveAttack(characterId, loadout, accuracy, maxHit)
        val log = combatLogFor.getOrPut(characterId) { mutableListOf() }

        if (result is ServiceResult.Success) {
            val attack = result.value
            val monsterDefense = session.currentMonster?.defenseRating ?: 1
            lastHitChancePercent = (accuracy.toDouble() / (accuracy + monsterDefense)) * 100.0
            lastDamageDealt = attack.damageDealt

            if (attack.didHit) {
                log.add(CombatLogEntry("You hit for " + attack.damageDealt + "."))
                val xpGrant = progressionService.grantXp(characterId, trainingSkill, (attack.damageDealt * 4 + 5).toLong())
                if (xpGrant is ServiceResult.Success) refreshSkills()
            } else {
                log.add(CombatLogEntry("You missed."))
            }

            if (attack.monsterDefeated) {
                val defeatedName = session.currentMonster?.name ?: "the enemy"
                log.add(CombatLogEntry("Defeated " + defeatedName + "!"))
                val loot = combatService.collectLoot(characterId)
                if (loot is ServiceResult.Success && loot.value.isNotEmpty()) {
                    loot.value.forEach { entry -> inventoryService.inventoryFor(characterId).addItem(entry.itemId, entry.minQty) }
                    refreshInventory()
                }
                val coinsEarned = combatService.collectCoins(characterId)
                if (coinsEarned > 0) {
                    log.add(CombatLogEntry("Found " + coinsEarned + " coins."))
                    grantCombatCoins(characterId, coinsEarned)
                }
            }

            // Monsters don't have a dedicated offensive stat yet, so their counter-attack uses a flat
            // hit chance with damage scaled off defenseRating as a stand-in. Placeholder, same spirit
            // as the maxHp formula above - safe to retune once real monster balance is worked out.
            val monster = session.currentMonster
            if (monster != null && Random.nextDouble(0.0, 100.0) < 40.0) {
                val dmg = Random.nextInt(1, (monster.defenseRating / 3).coerceAtLeast(1) + 1)
                combatService.applyDamageToCharacter(characterId, dmg)
                log.add(CombatLogEntry(monster.name + " hits you for " + dmg + "."))
            }

            val freshState = combatService.stateFor(characterId, maxHpFor(characterId))
            if (freshState.currentHp <= 0) {
                log.add(CombatLogEntry("You were defeated and are recovering."))
            } else if (freshState.maxHp > 0 &&
                (freshState.currentHp * 100 / freshState.maxHp) <= inventoryService.inventoryFor(characterId).autoFleeThresholdPercent
            ) {
                combatService.leaveZone(characterId)
                log.add(CombatLogEntry("Fled to safety."))
            }
        }
        refreshCombatView()
    }

    data class LoadoutSettingsSnapshot(
        val selectedFoodId: String?,
        val selectedPotionId: String?,
        val potionTimerRemainingSeconds: Int,
        val autoHealThresholdPercent: Int,
        val autoFleeThresholdPercent: Int
    )

    private val _loadoutSettings = MutableStateFlow(LoadoutSettingsSnapshot(null, null, 0, 30, 10))
    val loadoutSettings: StateFlow<LoadoutSettingsSnapshot> = _loadoutSettings.asStateFlow()

    fun setAutoHealThreshold(percent: Int) {
        val characterId = _currentCharacterId.value ?: return
        inventoryService.inventoryFor(characterId).autoHealThresholdPercent = percent.coerceIn(0, 100)
        refreshInventory()
    }

    fun setAutoFleeThreshold(percent: Int) {
        val characterId = _currentCharacterId.value ?: return
        inventoryService.inventoryFor(characterId).autoFleeThresholdPercent = percent.coerceIn(0, 100)
        refreshInventory()
    }

    fun selectFood(itemId: String?) {
        val characterId = _currentCharacterId.value ?: return
        inventoryService.inventoryFor(characterId).selectFood(itemId)
        refreshInventory()
    }

    fun selectPotion(itemId: String?) {
        val characterId = _currentCharacterId.value ?: return
        inventoryService.inventoryFor(characterId).selectPotion(itemId)
        refreshInventory()
    }

    fun useInventoryItem(itemId: String) {
        val characterId = _currentCharacterId.value ?: return
        val definition = ItemCatalog.find(itemId) ?: return
        if (definition.consumableType != ConsumableType.FOOD) return
        val inventory = inventoryService.inventoryFor(characterId)
        val removed = inventory.removeItem(itemId, 1)
        if (removed is ServiceResult.Success) {
            combatService.healCharacter(characterId, definition.healAmount ?: 0)
            refreshInventory()
        }
    }

    private fun tickConsumables() {
        val characterId = _currentCharacterId.value ?: return
        val inventory = inventoryService.inventoryFor(characterId)
        val combatState = combatService.stateFor(characterId)

        if (combatState.maxHp > 0) {
            val hpPercent = (combatState.currentHp * 100) / combatState.maxHp
            if (hpPercent <= inventory.autoHealThresholdPercent) {
                inventory.consumeSelectedFood()?.let { food ->
                    combatService.healCharacter(characterId, food.healAmount ?: 0)
                }
            }
        }

        if (inventory.selectedPotionId != null) {
            if (inventory.potionTimerRemainingSeconds > 0) {
                inventory.potionTimerRemainingSeconds -= 1
            }
            if (inventory.potionTimerRemainingSeconds <= 0) {
                inventory.consumeSelectedPotion()?.let { potion ->
                    inventory.potionTimerRemainingSeconds = potion.buffDurationSeconds ?: 0
                }
            }
        }

        refreshInventory()
        refreshCombatHp()
    }

    private val _marketListings = MutableStateFlow<List<MarketPriceSummary>>(emptyList())
    val marketListings: StateFlow<List<MarketPriceSummary>> = _marketListings.asStateFlow()

    private val _myBuyOrders = MutableStateFlow<List<MarketOrder>>(emptyList())
    val myBuyOrders: StateFlow<List<MarketOrder>> = _myBuyOrders.asStateFlow()

    private val _mySellOrders = MutableStateFlow<List<MarketOrder>>(emptyList())
    val mySellOrders: StateFlow<List<MarketOrder>> = _mySellOrders.asStateFlow()

    private val _activeQueueInfo = MutableStateFlow<ActiveQueueInfo?>(null)
    val activeQueueInfo: StateFlow<ActiveQueueInfo?> = _activeQueueInfo.asStateFlow()

    private val _currency = MutableStateFlow(0L to 0L)
    val currency: StateFlow<Pair<Long, Long>> = _currency.asStateFlow()

    init {
        viewModelScope.launch(Dispatchers.Default) {
            while (true) {
                delay(1000L)
                tickSkilling()
            tickCrafting()
            tickConsumables()
            tickCombat()
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

init {
        viewModelScope.launch {
            SupabaseClientProvider.client.auth.sessionStatus.collect { status ->
                when (status) {
                    is SessionStatus.Authenticated -> {
                        _supabaseAuthState.value = SupabaseAuthState.SIGNED_IN
                        _supabaseAuthError.value = null
                    }
                    is SessionStatus.NotAuthenticated -> {
                        _supabaseAuthState.value = SupabaseAuthState.SIGNED_OUT
                    }
                    else -> {
                        // Covers Initializing/LoadingFromStorage and RefreshFailure,
                        // whichever names this supabase-kt version uses - all transient.
                        _supabaseAuthState.value = SupabaseAuthState.SIGNING_IN
                    }
                }
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
        saved.craftingQueues.forEach { offlineIdleService.restoreCraftingQueue(it) }
        saved.lastSeen.forEach { offlineIdleService.restoreLastSeen(it) }
        saved.lastSaleCheck.forEach { offlineIdleService.restoreLastSaleCheck(it) }
        saved.inventoryItems.forEach { inventoryService.restoreItem(it) }
        saved.equippedSlots.forEach { inventoryService.restoreEquipped(it) }
        saved.loadoutSettings.forEach { inventoryService.restoreLoadoutSettings(it) }
        saved.marketAccounts.forEach { marketService.restoreAccount(it) }
        saved.marketOrders.forEach { marketService.restoreOrder(it) }
        saved.marketPriceHistory.forEach { marketService.restorePriceHistoryEntry(it) }
    }
suspend fun login(email: String, password: String): ServiceResult<Account> {
    val result = accountService.login(email, password)
    if (result is ServiceResult.Success) {
        sessionManager.saveSession(result.value.id)
            _currentAccountId.value = result.value.id
            refreshCurrency()
            syncSupabaseAuth(email, password, isNewAccount = false)
        return result
    }
    return attemptCloudRecoveryLogin(email, password)
}

private suspend fun attemptCloudRecoveryLogin(email: String, password: String): ServiceResult<Account> {
    try {
        SupabaseClientProvider.client.auth.signInWith(io.github.jan.supabase.auth.providers.builtin.Email) {
            this.email = email
            this.password = password
        }
    } catch (e: Exception) {
        return ServiceResult.Failure("No local account found, and no matching cloud account either. (${e.message})")
    }

    val placeholderLocalId = java.util.UUID.randomUUID().toString()
    val charResult = SupabaseCharacterRepository.getOrCreateCharacter(placeholderLocalId, "Recovered")
    val supabaseCharacterId = charResult.getOrNull()
        ?: return ServiceResult.Failure("Found a cloud account but couldn't sync a character to it.")

    val cloudJson = SupabaseCharacterRepository.downloadCharacterSave(supabaseCharacterId).getOrNull()
        ?: return ServiceResult.Failure("This account has no cloud backup saved yet - its local data can't be recovered.")

    repository.overwriteRawJson(cloudJson)
    val recovered = repository.load()
        ?: return ServiceResult.Failure("Recovered cloud data was corrupted or empty.")

    recovered.accounts.forEach { accountService.restoreAccount(it) }
    recovered.characters.forEach { accountService.restoreCharacter(it) }
    recovered.skills.forEach { progressionService.restoreSkill(it) }
    recovered.skillingQueues.forEach { offlineIdleService.restoreSkillingQueue(it) }
    recovered.craftingQueues.forEach { offlineIdleService.restoreCraftingQueue(it) }
    recovered.lastSeen.forEach { offlineIdleService.restoreLastSeen(it) }
    recovered.lastSaleCheck.forEach { offlineIdleService.restoreLastSaleCheck(it) }
    recovered.inventoryItems.forEach { inventoryService.restoreItem(it) }
    recovered.equippedSlots.forEach { inventoryService.restoreEquipped(it) }
    recovered.loadoutSettings.forEach { inventoryService.restoreLoadoutSettings(it) }
    recovered.marketAccounts.forEach { marketService.restoreAccount(it) }
    recovered.marketOrders.forEach { marketService.restoreOrder(it) }
    recovered.marketPriceHistory.forEach { marketService.restorePriceHistoryEntry(it) }

    val recoveredAccountExport = recovered.accounts.firstOrNull { it.email.equals(email, ignoreCase = true) }
        ?: return ServiceResult.Failure("Recovered cloud data but couldn't match it to this email.")
    val recoveredAccount = accountService.accountById(recoveredAccountExport.id)
        ?: return ServiceResult.Failure("Recovered account data but couldn't load it.")

    sessionManager.saveSession(recoveredAccount.id)
    _currentAccountId.value = recoveredAccount.id
    refreshCurrency()
    _currentSupabaseCharacterId.value = supabaseCharacterId
    _characterSyncError.value = null

    val recoveredCharacter = recovered.characters.firstOrNull { it.accountId == recoveredAccount.id }
    if (recoveredCharacter != null) {
        _currentCharacterId.value = recoveredCharacter.id
    }

    return ServiceResult.Success(recoveredAccount)
}
  fun createAccount(email: String, username: String, password: String): ServiceResult<Account> {
    val result = accountService.createAccount(email, username, password, AgeBracket.ADULT_18_PLUS, "US")
    if (result is ServiceResult.Success) {
        sessionManager.saveSession(result.value.id)
            _currentAccountId.value = result.value.id
            refreshCurrency()
            syncSupabaseAuth(email, password, isNewAccount = true)
    }
    return result
  }
  fun tryAutoLogin(): Account? {
    val accountId = sessionManager.getSavedAccountId() ?: return null
    val account = accountService.accountById(accountId) ?: return null
    _currentAccountId.value = account.id
    refreshCurrency()
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

    fun dismissSaleNotification() {
        _pendingSaleNotifications.value = _pendingSaleNotifications.value.drop(1)
    }

    private fun checkForRecentSales(characterId: String) {
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        val since = offlineIdleService.lastSaleCheckFor(characterId)?.toString()
            ?: Instant.now().minusSeconds(86400).toString()
        offlineIdleService.recordSaleCheck(characterId)
        viewModelScope.launch {
            val result = SupabaseMarketRepository.myRecentSales(supabaseCharacterId, since)
            result.onSuccess { rows ->
                if (rows.isNotEmpty()) {
                    val notifications = rows.map { row ->
                        val netProceeds = (row.pricePerUnit * row.quantity) - row.taxCollected
                        SaleNotification(
                            itemName = ItemCatalog.find(row.itemId)?.name ?: formatItemName(row.itemId),
                            quantity = row.quantity,
                            netProceeds = netProceeds
                        )
                    }
                    _pendingSaleNotifications.value = _pendingSaleNotifications.value + notifications
                }
            }
        }
    }
    fun saveGame() {
        repository.save(
            accountService.exportAllAccounts(),
            accountService.exportAllCharacters(),
            progressionService.exportAllSkills(),
            offlineIdleService.exportSkillingQueues(),
            offlineIdleService.exportCraftingQueues(),
            offlineIdleService.exportLastSeen(),
            offlineIdleService.exportLastSaleCheck(),
            inventoryService.exportAllItems(),
            inventoryService.exportAllEquipped(),
            inventoryService.exportAllLoadoutSettings(),
            marketService.exportAccounts(),
            marketService.exportOrders(),
            marketService.exportPriceHistory()
        )
        val supabaseCharacterId = _currentSupabaseCharacterId.value
        val json = repository.currentSaveJson()
        if (supabaseCharacterId != null && json != null) {
            viewModelScope.launch {
                SupabaseCharacterRepository.uploadCharacterSave(supabaseCharacterId, json)
            }
        }
    }

    fun selectCharacter(characterId: String) {
        _currentCharacterId.value = characterId

        val selectedCharacter = accountService.charactersFor(_currentAccountId.value ?: "").firstOrNull { it.id == characterId }
        if (selectedCharacter != null) {
            viewModelScope.launch {
                val result = SupabaseCharacterRepository.getOrCreateCharacter(characterId, selectedCharacter.displayName)
                result.onFailure { _characterSyncError.value = it.message ?: it.toString() }
                result.onSuccess { _characterSyncError.value = null }
                _currentSupabaseCharacterId.value = result.getOrNull()
                val supabaseCharacterId = result.getOrNull()
                if (supabaseCharacterId != null) {
                    val remoteLocalId = SupabaseCharacterRepository.getCharacterLocalId(supabaseCharacterId).getOrNull()
                    if (remoteLocalId != null && remoteLocalId != characterId) {
                        // The server returned an EXISTING character from a different
                        // device/install, not the one just created locally - recover
                        // its real save instead of keeping the throwaway new one.
                        val cloudJson = SupabaseCharacterRepository.downloadCharacterSave(supabaseCharacterId).getOrNull()
                        if (cloudJson != null) {
                            repository.overwriteRawJson(cloudJson)
                            val recovered = repository.load()
                            if (recovered != null) {
                                recovered.accounts.forEach { accountService.restoreAccount(it) }
                                recovered.characters.forEach { accountService.restoreCharacter(it) }
                                recovered.skills.forEach { progressionService.restoreSkill(it) }
                                recovered.skillingQueues.forEach { offlineIdleService.restoreSkillingQueue(it) }
                                recovered.craftingQueues.forEach { offlineIdleService.restoreCraftingQueue(it) }
                                recovered.lastSeen.forEach { offlineIdleService.restoreLastSeen(it) }
                                recovered.lastSaleCheck.forEach { offlineIdleService.restoreLastSaleCheck(it) }
                                recovered.inventoryItems.forEach { inventoryService.restoreItem(it) }
                                recovered.equippedSlots.forEach { inventoryService.restoreEquipped(it) }
                                recovered.loadoutSettings.forEach { inventoryService.restoreLoadoutSettings(it) }
                                recovered.marketAccounts.forEach { marketService.restoreAccount(it) }
                                recovered.marketOrders.forEach { marketService.restoreOrder(it) }
                                recovered.marketPriceHistory.forEach { marketService.restorePriceHistoryEntry(it) }
                                _currentCharacterId.value = remoteLocalId
                                val recoveredCharacter = recovered.characters.firstOrNull { it.id == remoteLocalId }
                                if (recoveredCharacter != null) {
                                    _currentAccountId.value = recoveredCharacter.accountId
                                }
                                resolveOfflineRewardsAndSync(remoteLocalId)
                            }
                        }
                    }
                }
            }
        } else {
            _characterSyncError.value = "selectedCharacter was null - accountId=${_currentAccountId.value}, characterId=$characterId"
        }

        resolveOfflineRewardsAndSync(characterId)
    }

    // Grants offline-progress rewards (skilling/crafting), records last-seen, and
    // syncs currency/market state for the given character. Extracted so it can be
    // re-run against a cloud-recovered character id after async recovery completes
    // (see selectCharacter) - a throwaway local character's offline queue is never
    // the "real" one in that scenario, so re-resolving against the recovered
    // character's actual data is the correct behavior, not just a race-condition
    // workaround.
    private fun resolveOfflineRewardsAndSync(characterId: String) {
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
                    if (skillType == SkillType.MINING) {
                        MiningBonusGemTable.rollAndGrant(inventoryService.inventoryFor(characterId), result.value.actionsCompleted)
                    }
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

        val craftingQueue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.CraftingQueue
        if (craftingQueue != null) {
            val craftResult = offlineIdleService.resolveOfflineProgress(characterId)
            if (craftResult is ServiceResult.Success && craftResult.value.actionsCompleted > 0) {
                val batch = craftItems(characterId, craftingQueue.itemId, craftResult.value.actionsCompleted)
                if (batch.xpGranted > 0) {
                    _offlineSummary.value = OfflineSummary(
                        awaySeconds = craftResult.value.claimedElapsed.seconds,
                        skillActionName = "Craft " + formatItemName(craftingQueue.itemId),
                        itemName = formatItemName(craftingQueue.itemId),
                        quantity = batch.itemsProduced,
                        xpEarned = batch.xpGranted
                    )
                }
            }
        }

        offlineIdleService.recordLastSeen(characterId)
        checkForRecentSales(characterId)
        skillActionProgressSeconds = 0
        craftActionProgressSeconds = 0
        refreshSkills()
        refreshInventory()
        refreshActiveQueue()

        if (marketService.accountFor(characterId) == null) {
            val character = accountService.charactersFor(_currentAccountId.value ?: "")
                .find { it.id == characterId }
            marketService.registerAccount(
                PlayerEconomyAccount(
                    characterId = characterId,
                    accountId = _currentAccountId.value ?: "",
                    isMainCharacter = character?.isMainCharacter ?: true,
                    currencyBalance = 0L
                )
            )
        }
        refreshCurrency()
        refreshMarketListings()
        refreshMyOrders()
    }

    fun startSkillAction(skillType: SkillType, itemId: String) {
        val characterId = _currentCharacterId.value ?: return
        val action = ActionCatalog.find(skillType, itemId) ?: return
        // Starting a skill stops any active combat session - only one
        // activity can run at a time.
        leaveCombatZone()
        offlineIdleService.stopQueue(characterId)
        offlineIdleService.startSkillingQueue(characterId, skillType.name, itemId, action.secondsPerAction)
        offlineIdleService.recordLastSeen(characterId)
        checkForRecentSales(characterId)
        skillActionProgressSeconds = 0
        refreshActiveQueue()
    }

    fun stopSkillAction() {
        val characterId = _currentCharacterId.value ?: return
        offlineIdleService.stopQueue(characterId)
        skillActionProgressSeconds = 0
        refreshActiveQueue()
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
            if (skillType == SkillType.MINING) {
                MiningBonusGemTable.rollAndGrant(inventoryService.inventoryFor(characterId), actionsCompleted.toInt())
            }
            refreshSkills()
            refreshInventory()
        }
    }

    // =========================================================
    // CRAFTING -- mirrors the SkillingQueue flow above. Recipe.levelRequired
    // (via CraftingTierCurve) is the source of truth for timing/XP, decoupled
    // from ActionCatalog since production item ids don't line up with
    // ActionCatalog's generic class-action ids (see Step 5 handoff notes).
    // =========================================================

    private var craftActionProgressSeconds: Long = 0

    private val craftingService = CraftingService()

    private data class CraftBatchResult(val successfulCrafts: Int, val itemsProduced: Int, val xpGranted: Long)

    private fun craftItems(characterId: String, itemId: String, attempts: Int): CraftBatchResult {
        val recipe = RecipeCatalog.forOutput(itemId) ?: return CraftBatchResult(0, 0, 0)
        val skillType = SkillType.valueOf(recipe.skillRequired)
        val book = progressionService.skillBookFor(characterId)
        val skill = book.all().find { it.type == skillType }
        val playerLevel = if (skill != null) LevelCurve.levelForXp(skill.xp) else 1
        val inventory = inventoryService.inventoryFor(characterId)
        val xpPerAttempt = CraftingTierCurve.xpFor(recipe.levelRequired)

        var successes = 0
        var totalProduced = 0
        var xpGranted = 0L
        for (i in 0 until attempts) {
            val result = craftingService.craftOnce(inventory, itemId, playerLevel)
            if (result is ServiceResult.Success) {
                xpGranted += xpPerAttempt
                if (result.value.succeeded) {
                    successes += 1
                    totalProduced += result.value.quantityProduced
                }
            } else {
                break
            }
        }
        if (xpGranted > 0) {
            progressionService.grantXp(characterId, skillType, xpGranted)
        }
        return CraftBatchResult(successes, totalProduced, xpGranted)
    }

    fun startCraftingAction(itemId: String, targetQuantity: Int? = null) {
        val characterId = _currentCharacterId.value ?: return
        val recipe = RecipeCatalog.forOutput(itemId) ?: return
        // Starting crafting stops any active combat session - only one
        // activity can run at a time.
        leaveCombatZone()
        offlineIdleService.stopQueue(characterId)
        offlineIdleService.startCraftingQueue(
            characterId,
            itemId,
            CraftingTierCurve.secondsFor(recipe.levelRequired),
            targetQuantity
        )
        offlineIdleService.recordLastSeen(characterId)
        craftActionProgressSeconds = 0
        refreshActiveQueue()
    }

    fun stopCraftingAction() {
        val characterId = _currentCharacterId.value ?: return
        offlineIdleService.stopQueue(characterId)
        craftActionProgressSeconds = 0
        refreshActiveQueue()
    }

    private fun tickCrafting() {
        val characterId = _currentCharacterId.value ?: return
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.CraftingQueue ?: return

        craftActionProgressSeconds += 1
        if (craftActionProgressSeconds < queue.secondsPerAction) return

        val attempts = (craftActionProgressSeconds / queue.secondsPerAction).toInt()
        craftActionProgressSeconds %= queue.secondsPerAction

        val remainingToTarget = queue.targetQuantity?.let { it - queue.quantityCompleted }
        val cappedAttempts = if (remainingToTarget != null) minOf(attempts, remainingToTarget) else attempts
        if (cappedAttempts <= 0) return

        val batch = craftItems(characterId, queue.itemId, cappedAttempts)
        queue.quantityCompleted += batch.successfulCrafts
        refreshSkills()
        refreshInventory()

        if (queue.isTargetReached()) {
            offlineIdleService.stopQueue(characterId)
            refreshActiveQueue()
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
        _trainingSkillLevel.value = _skills.value[_trainingSkill.value.name]?.level ?: 1
    }

    fun refreshInventory() {
        val characterId = _currentCharacterId.value ?: return
        val inv = inventoryService.inventoryFor(characterId)
        _inventoryItems.value = inv.allItems()
        _equippedItems.value = inv.allEquipped()
        _loadoutSettings.value = LoadoutSettingsSnapshot(
            inv.selectedFoodId, inv.selectedPotionId, inv.potionTimerRemainingSeconds,
            inv.autoHealThresholdPercent, inv.autoFleeThresholdPercent
        )
    }

    private fun grantCombatCoins(characterId: String, amount: Long) {
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseMarketRepository.grantCombatCoins(supabaseCharacterId, amount)
            result.onFailure {
                _marketActionError.value = it.message ?: it.toString()
            }
            result.onSuccess {
                _marketActionError.value = null
                refreshCurrency()
            }
        }
    }

    fun equipItem(itemId: String): ServiceResult<Unit> {
        val characterId = _currentCharacterId.value ?: return ServiceResult.Failure("No character selected.")
        val playerSkillLevels = progressionService.skillBookFor(characterId).all()
            .associate { it.type.name to LevelCurve.levelForXp(it.xp) }
        val playerLevel = playerSkillLevels.values.maxOrNull() ?: 1
        val result = inventoryService.inventoryFor(characterId).equip(itemId, playerLevel, playerSkillLevels) { true }
        if (result is ServiceResult.Success) refreshInventory()
        return result
    }

    fun unequipSlot(slot: EquipSlot): ServiceResult<Unit> {
        val characterId = _currentCharacterId.value ?: return ServiceResult.Failure("No character selected.")
        val result = inventoryService.inventoryFor(characterId).unequip(slot) { true }
        if (result is ServiceResult.Success) refreshInventory()
        return result
    }

    fun refreshActiveQueue() {
        val characterId = _currentCharacterId.value
        val queue = characterId?.let { offlineIdleService.activeQueueFor(it) }
        _activeQueueInfo.value = when (queue) {
            is ActiveQueue.SkillingQueue -> {
                val skillType = SkillType.valueOf(queue.skillId)
                val action = ActionCatalog.find(skillType, queue.itemId)
                ActiveQueueInfo(
                    label = action?.displayName ?: formatItemName(queue.itemId),
                    secondsPerAction = queue.secondsPerAction,
                    startedAt = queue.startedAt
                )
            }
            is ActiveQueue.CraftingQueue -> ActiveQueueInfo(
                label = "Crafting " + formatItemName(queue.itemId),
                secondsPerAction = queue.secondsPerAction,
                startedAt = queue.startedAt
            )
            else -> null
        }
    }

    fun refreshCurrency() {
        val accountId = _currentAccountId.value ?: return
        val account = accountService.accountById(accountId) ?: return
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val gold = SupabaseMarketRepository.currencyBalance(characterId).getOrNull() ?: 0L
            _currency.value = gold to account.premiumCurrency
        }
    }

    // =========================================================
    // MARKET (server-side via Supabase - shared order book across all players)
    // =========================================================

    fun refreshMarketListings() {
        viewModelScope.launch {
            val listings = SupabaseMarketRepository.listings().getOrNull() ?: emptyList()
            _marketListings.value = listings.map { MarketPriceSummary(it.itemId, it.bestBuyPrice, it.bestBuyQuantity, it.bestSellPrice, it.bestSellQuantity) }
        }
    }

    private fun MarketOrderRow.toDomain(): MarketOrder = MarketOrder(
        id = id,
        characterId = characterId,
        itemId = itemId,
        side = OrderSide.valueOf(side),
        pricePerUnit = pricePerUnit,
        originalQuantity = originalQuantity,
        remainingQuantity = remainingQuantity,
        status = OrderStatus.valueOf(status),
        createdAt = java.time.OffsetDateTime.parse(createdAt).toInstant()
    )

    fun refreshMyOrders() {
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val orders = SupabaseMarketRepository.myOrders(characterId).getOrNull()?.map { it.toDomain() } ?: emptyList()
            _myBuyOrders.value = orders.filter { it.side == OrderSide.BUY }
            _mySellOrders.value = orders.filter { it.side == OrderSide.SELL }
        }
    }

    fun placeBuyOrder(itemId: String, quantity: Int, pricePerUnit: Long) {
        val characterId = _currentCharacterId.value ?: return
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseMarketRepository.placeBuyOrder(supabaseCharacterId, itemId, quantity, pricePerUnit)
            result.onFailure { _marketActionError.value = it.message ?: it.toString() }
            result.onSuccess { order ->
                _marketActionError.value = null
                val filled = order.originalQuantity - order.remainingQuantity
                if (filled > 0) {
                    inventoryService.inventoryFor(characterId).addItem(itemId, filled)
                    refreshInventory()
                }
                refreshCurrency()
                refreshMarketListings()
                refreshMyOrders()
            }
        }
    }

    fun placeSellOrder(itemId: String, quantity: Int, pricePerUnit: Long) {
        val characterId = _currentCharacterId.value ?: return
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        val realInventory = inventoryService.inventoryFor(characterId)
        if (realInventory.quantityOf(itemId) < quantity) return

        realInventory.removeItem(itemId, quantity)
        refreshInventory()

        viewModelScope.launch {
            val result = SupabaseMarketRepository.placeSellOrder(supabaseCharacterId, itemId, quantity, pricePerUnit)
            result.onFailure {
                _marketActionError.value = it.message ?: it.toString()
                realInventory.addItem(itemId, quantity)
                refreshInventory()
            }
            result.onSuccess {
                _marketActionError.value = null
                refreshCurrency()
                refreshMarketListings()
                refreshMyOrders()
            }
        }
    }

    fun cancelMarketOrder(orderId: String) {
        val characterId = _currentCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseMarketRepository.cancelOrder(orderId)
            result.onFailure { _marketActionError.value = it.message ?: it.toString() }
            result.onSuccess { cancelled ->
                _marketActionError.value = null
                if (cancelled.side == "SELL" && cancelled.remainingQuantityBeforeCancel > 0) {
                    inventoryService.inventoryFor(characterId).addItem(cancelled.itemId, cancelled.remainingQuantityBeforeCancel)
                    refreshInventory()
                }
                refreshCurrency()
                refreshMarketListings()
                refreshMyOrders()
            }
        }
    }

    fun sellItemToVendor(itemId: String, quantity: Int) {
        val characterId = _currentCharacterId.value ?: return
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        val realInventory = inventoryService.inventoryFor(characterId)
        if (realInventory.quantityOf(itemId) < quantity) return
        val payoutPerUnit = ((ItemCatalog.baseValueFor(itemId) * 40.0) / 100.0).toLong()

        realInventory.removeItem(itemId, quantity)
        refreshInventory()

        viewModelScope.launch {
            val result = SupabaseMarketRepository.sellToVendor(supabaseCharacterId, itemId, quantity, payoutPerUnit)
            result.onFailure {
                _marketActionError.value = it.message ?: it.toString()
                realInventory.addItem(itemId, quantity)
                refreshInventory()
            }
            result.onSuccess {
                _marketActionError.value = null
                refreshCurrency()
            }
        }
    }

    fun buyItemFromVendor(itemId: String, quantity: Int) {
        val characterId = _currentCharacterId.value ?: return
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        val realInventory = inventoryService.inventoryFor(characterId)
        val pricePerUnit = VendorBuyCatalog.items.find { it.itemId == itemId }?.pricePerUnit ?: return
        if (quantity <= 0) return

        realInventory.addItem(itemId, quantity)
        refreshInventory()

        viewModelScope.launch {
            val result = SupabaseMarketRepository.buyFromVendor(supabaseCharacterId, itemId, quantity, pricePerUnit)
            result.onFailure {
                _marketActionError.value = it.message ?: it.toString()
                realInventory.removeItem(itemId, quantity)
                refreshInventory()
            }
            result.onSuccess {
                _marketActionError.value = null
                refreshCurrency()
            }
        }
    }
}

