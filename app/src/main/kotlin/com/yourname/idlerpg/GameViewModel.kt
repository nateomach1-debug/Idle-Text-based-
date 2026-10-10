package com.yourname.idlerpg.data

import com.yourname.idlerpg.LeaderboardCategory
import com.yourname.idlerpg.LeaderboardRow
import com.yourname.idlerpg.SupabaseLeaderboardRepository
import com.yourname.idlerpg.UnlockTable
import com.yourname.idlerpg.EffectStacker
import com.yourname.idlerpg.ui.screens.VendorBuyCatalog
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import com.yourname.idlerpg.ui.screens.VendorBuyableItem

import io.github.jan.supabase.auth.status.SessionStatus
import kotlinx.coroutines.withTimeoutOrNull
import kotlinx.coroutines.flow.first

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.yourname.idlerpg.*
import com.yourname.idlerpg.ui.screens.SkillSummary
import com.yourname.idlerpg.ui.screens.CombatViewData
import com.yourname.idlerpg.ui.screens.CombatViewState
import com.yourname.idlerpg.ui.screens.CombatLogEntry
import com.yourname.idlerpg.ui.screens.SessionDropEntry
import com.yourname.idlerpg.ui.screens.ZoneSummary
import com.yourname.idlerpg.ui.screens.ZoneMonsterSummary
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
    private val _inventoryCapacity = MutableStateFlow(100)
    val inventoryCapacity: StateFlow<Int> = _inventoryCapacity.asStateFlow()

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

    private val _leaderboardRows = MutableStateFlow<List<LeaderboardRow>>(emptyList())
    val leaderboardRows: StateFlow<List<LeaderboardRow>> = _leaderboardRows.asStateFlow()

    private val _leaderboardLoading = MutableStateFlow(false)
    val leaderboardLoading: StateFlow<Boolean> = _leaderboardLoading.asStateFlow()

    private val _selectedLeaderboardCategory = MutableStateFlow(LeaderboardCategory.TOTAL_LEVEL)
    val selectedLeaderboardCategory: StateFlow<LeaderboardCategory> = _selectedLeaderboardCategory.asStateFlow()

    // =========================================================
    // SETTINGS: text color override + outline (Settings tab)
    // Persisted via SharedPreferences (idlerpg_prefs, same file/
    // convention as inventory/skills view-mode prefs).
    // =========================================================
    private val settingsPrefs = application.getSharedPreferences("idlerpg_prefs", android.content.Context.MODE_PRIVATE)

    // Monster the player picked in the zone popup, stored per character (device-local).
    // CombatService reads it lazily whenever it picks the next monster, including when
    // resolving offline combat progress after a restart.
    private fun combatTargetKey(characterId: String): String = "combat_target_monster_" + characterId

    init {
        combatService.targetMonsterIdProvider = { characterId ->
            settingsPrefs.getString(combatTargetKey(characterId), null)
        }
    }

    private val _textColorOverride = MutableStateFlow<Color?>(
        if (settingsPrefs.contains("text_color_override")) Color(settingsPrefs.getInt("text_color_override", 0)) else null
    )
    val textColorOverride: StateFlow<Color?> = _textColorOverride.asStateFlow()

    private val _textOutlineEnabled = MutableStateFlow(settingsPrefs.getBoolean("text_outline_enabled", false))
    val textOutlineEnabled: StateFlow<Boolean> = _textOutlineEnabled.asStateFlow()

    private val _textOutlineColor = MutableStateFlow(Color(settingsPrefs.getInt("text_outline_color", android.graphics.Color.BLACK)))
    val textOutlineColor: StateFlow<Color> = _textOutlineColor.asStateFlow()

    fun setTextColorOverride(color: Color?) {
        _textColorOverride.value = color
        if (color == null) {
            settingsPrefs.edit().remove("text_color_override").apply()
        } else {
            settingsPrefs.edit().putInt("text_color_override", color.toArgb()).apply()
        }
    }

    fun setTextOutlineEnabled(enabled: Boolean) {
        _textOutlineEnabled.value = enabled
        settingsPrefs.edit().putBoolean("text_outline_enabled", enabled).apply()
    }

    fun setTextOutlineColor(color: Color) {
        _textOutlineColor.value = color
        settingsPrefs.edit().putInt("text_outline_color", color.toArgb()).apply()
    }

    private val _textEffectMode = MutableStateFlow(
        com.yourname.idlerpg.ui.theme.TextEffectMode.valueOf(
            settingsPrefs.getString("text_effect_mode", com.yourname.idlerpg.ui.theme.TextEffectMode.SOLID.name)
                ?: com.yourname.idlerpg.ui.theme.TextEffectMode.SOLID.name
        )
    )
    val textEffectMode: StateFlow<com.yourname.idlerpg.ui.theme.TextEffectMode> = _textEffectMode.asStateFlow()

    private val _textSecondaryColor = MutableStateFlow<Color?>(
        if (settingsPrefs.contains("text_secondary_color")) Color(settingsPrefs.getInt("text_secondary_color", 0)) else null
    )
    val textSecondaryColor: StateFlow<Color?> = _textSecondaryColor.asStateFlow()

    fun setTextEffectMode(mode: com.yourname.idlerpg.ui.theme.TextEffectMode) {
        _textEffectMode.value = mode
        settingsPrefs.edit().putString("text_effect_mode", mode.name).apply()
    }

    fun setTextSecondaryColor(color: Color?) {
        _textSecondaryColor.value = color
        if (color == null) {
            settingsPrefs.edit().remove("text_secondary_color").apply()
        } else {
            settingsPrefs.edit().putInt("text_secondary_color", color.toArgb()).apply()
        }
    }

    fun fetchLeaderboard(category: LeaderboardCategory) {
        _selectedLeaderboardCategory.value = category
        viewModelScope.launch {
            _leaderboardLoading.value = true
            val rows: List<LeaderboardRow> = when (category) {
                LeaderboardCategory.TOTAL_LEVEL -> SupabaseLeaderboardRepository.fetchTotalLevelLeaderboard()
                    .getOrDefault(emptyList())
                    .mapIndexed { index, entry ->
                        LeaderboardRow(rank = index + 1, name = entry.displayName, valueLabel = "Lv " + entry.totalLevel)
                    }
                LeaderboardCategory.COMBAT_LEVEL -> SupabaseLeaderboardRepository.fetchCombatLevelLeaderboard()
                    .getOrDefault(emptyList())
                    .mapIndexed { index, entry ->
                        LeaderboardRow(rank = index + 1, name = entry.displayName, valueLabel = "Lv " + entry.combatLevel)
                    }
                LeaderboardCategory.GUILDS -> SupabaseLeaderboardRepository.fetchGuildLeaderboard()
                    .getOrDefault(emptyList())
                    .mapIndexed { index, entry ->
                        LeaderboardRow(rank = index + 1, name = entry.guildName, valueLabel = "Lv " + entry.guildLevel + " \u00b7 " + entry.guildCoins + " coins")
                    }
                else -> SupabaseLeaderboardRepository.fetchSkillLeaderboard(category.name)
                    .getOrDefault(emptyList())
                    .mapIndexed { index, entry ->
                        LeaderboardRow(rank = index + 1, name = entry.displayName, valueLabel = "Lv " + entry.level)
                    }
            }
            _leaderboardRows.value = rows
            _leaderboardLoading.value = false
        }
    }

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
            try {
                val membership = SupabaseGuildRepository.findMembership(characterId)
                _guildId.value = membership?.first
                if (membership == null) {
                    _guildHomeState.value = null
                    _guildLeaderboard.value = emptyList()
                    _browsableGuilds.value = SupabaseGuildRepository.listGuilds()
                } else {
                    SupabaseGuildRepository.closeExpiredGuildEventIfNeeded(membership.first)
                    _guildHomeState.value = SupabaseGuildRepository.fetchGuildHome(characterId)
                    _guildLeaderboard.value = SupabaseGuildRepository.fetchLeaderboard(characterId)
                    claimGuildEventPayouts()
                }
            } catch (e: Exception) {
                // Temporary diagnostic: fetchGuildHome() previously had no error
                // surfacing at all, so any exception (e.g. a date-parsing or
                // decode failure) silently left stale state in place with no
                // visible sign anything went wrong.
                _guildActionError.value = "refreshGuildHome failed: " + (e.message ?: e.toString())
            }
        }
    }

    // Per-member base quantity by rarity - rarer items require far fewer units
    // to reach the same milestone. Guild-coin reward per milestone is keyed
    // off rarity directly (not off requiredQuantity) so rarer-item events
    // don't perversely pay LESS just because fewer units are needed. Both
    // tables are first-pass numbers, flagged as tunable during balancing.
    // x10 from the original first-pass numbers, per explicit user request.
    private fun eventPerMemberQuantityFor(rarity: Rarity): Int = when (rarity) {
        Rarity.COMMON -> 400
        Rarity.UNCOMMON -> 250
        Rarity.RARE -> 150
        Rarity.EPIC -> 80
        Rarity.LEGENDARY -> 30
    }

    private fun eventGuildCoinRewardPerMilestoneFor(rarity: Rarity): Long = when (rarity) {
        Rarity.COMMON -> 100L
        Rarity.UNCOMMON -> 200L
        Rarity.RARE -> 400L
        Rarity.EPIC -> 800L
        Rarity.LEGENDARY -> 1600L
    }

    // x5 from the original first-pass numbers, per explicit user request.
    private fun eventGuildXpRewardPerMilestoneFor(rarity: Rarity): Long = when (rarity) {
        Rarity.COMMON -> 125L
        Rarity.UNCOMMON -> 250L
        Rarity.RARE -> 500L
        Rarity.EPIC -> 1000L
        Rarity.LEGENDARY -> 2000L
    }

    // Must match the SQL curve in contribute_to_guild_event() - level L needs
    // 1000*L XP to advance to L+1. Exposed here so the UI can show a progress
    // bar without a network round trip.
    fun guildXpRequiredForLevel(level: Int): Long = 1000L * level

    // Guild-exclusive perk: +0.5% XP per guild level, capped at +15% (reached
    // around guild level 30). Noticeable by the mid game, never mandatory.
    // Reuses the existing Effect.XpBoost mechanism (grantXp()'s extraEffects
    // param) rather than a separate bolt-on multiplier - nothing else in the
    // game currently produces an XpBoost effect, so this is genuinely
    // guild-exclusive. One effect per SkillGroup so it applies uniformly
    // across combat/gathering/production without double-counting (a skill
    // belongs to exactly one group).
    fun guildXpBonusPercent(): Double {
        val level = _guildHomeState.value?.guildLevel ?: return 0.0
        return (level * 0.5).coerceAtMost(15.0)
    }

    private fun guildXpBonusEffects(): List<Effect> {
        val percent = guildXpBonusPercent()
        if (percent <= 0.0) return emptyList()
        return SkillGroup.entries.map { group -> Effect.XpBoost(EffectScope.Group(group), percent) }
    }

    // =========================================================
    // MASTERY PERKS + SKILL CAPES
    // Level-50 perks live in UnlockTable (existing level->effect
    // mechanism). Capes add an equal-sized extra bonus on top while
    // worn, mirroring the guild XP bonus pattern above: extra Effects
    // merged in at every grantXp() call site via capeBonusEffects().
    // Combat's hit-chance/damage/reduction bonuses are NOT routed
    // through the Effect system (combat's accuracy/damage formulas
    // are already hardcoded, not effect-driven) - those use direct
    // level/cape checks via masteryBonusPercent() instead.
    // =========================================================
    private fun capeItemIdFor(skillType: SkillType): String = skillType.name.lowercase() + "_cape"

    private fun hasSkillCapeEquipped(characterId: String, skillType: SkillType): Boolean =
        inventoryService.inventoryFor(characterId).equippedItemIn(EquipSlot.CAPE) == capeItemIdFor(skillType)

    private fun masteryBonusPercent(level: Int, hasCape: Boolean, baseBonus: Double, capeBonus: Double): Double = when {
        hasCape -> capeBonus
        level >= 50 -> baseBonus
        else -> 0.0
    }

    private fun capeBonusEffects(characterId: String): List<Effect> {
        val equippedCapeId = inventoryService.inventoryFor(characterId).equippedItemIn(EquipSlot.CAPE) ?: return emptyList()
        val skill = SkillType.values().find { capeItemIdFor(it) == equippedCapeId } ?: return emptyList()
        val xpBoost = Effect.XpBoost(EffectScope.SingleSkill(skill), 5.0)
        val specific: Effect? = when (skill) {
            SkillType.MINING, SkillType.WOODCUTTING, SkillType.FISHING, SkillType.FARMING, SkillType.THIEVING ->
                Effect.DropRateBoost(EffectScope.SingleSkill(skill), 10.0)
            SkillType.SMITHING, SkillType.CRAFTING, SkillType.FLETCHING, SkillType.ALCHEMY ->
                Effect.MaterialSaveChance(EffectScope.SingleSkill(skill), 10.0)
            SkillType.COOKING -> Effect.CraftSuccessBoost(EffectScope.SingleSkill(skill), 10.0)
            else -> null // combat skills: handled directly via hasSkillCapeEquipped() in tickCombat
        }
        return listOfNotNull(xpBoost, specific)
    }

    fun vendorBuyableItems(): List<VendorBuyableItem> {
        val characterId = _currentCharacterId.value
        return VendorBuyCatalog.items.filter { vendorItem ->
            val def = ItemCatalog.find(vendorItem.itemId)
            val requiredSkillName = def?.skillRequired
            if (requiredSkillName == null || characterId == null) {
                true
            } else {
                val skillType = SkillType.values().find { it.name == requiredSkillName }
                if (skillType == null) true else skillLevel(characterId, skillType) >= (def.levelRequired)
            }
        }
    }

    fun currentInventoryQuantityOf(itemId: String): Int {
        val characterId = _currentCharacterId.value ?: return 0
        return inventoryService.inventoryFor(characterId).quantityOf(itemId)
    }

    fun clearGuildActionError() {
        _guildActionError.value = null
    }

    // Caps event items to a level appropriate for the guild's current level,
    // so a level-1 guild never gets asked to contribute a level-90 item. This
    // cap should rise as the planned guild-leveling feature ships - for now,
    // with all guilds still at guild_level 1, it effectively caps events to
    // low-level items across the board. Tunable curve, first pass.
    private fun maxEventItemLevelFor(guildLevel: Int): Int = (guildLevel * 10).coerceAtLeast(10)

    // Picks a random skill, then a random item tagged to that skill at or
    // below maxItemLevel. Retries with a different skill (up to a small cap)
    // if the chosen skill happens to have zero eligible items at that level,
    // rather than ever throwing.
    private fun pickRandomGuildEventResource(maxItemLevel: Int): ItemDefinition? {
        val skills = SkillType.entries.toList()
        repeat(20) {
            val skill = skills.random()
            val candidates = ItemCatalog.items.filter { it.skillRequired == skill.name && it.levelRequired <= maxItemLevel }
            if (candidates.isNotEmpty()) return candidates.random()
        }
        return null
    }

    fun startGuildEvent() {
        val guildId = _guildId.value ?: return
        val actingCharacterId = _currentSupabaseCharacterId.value ?: return
        val memberCount = (_guildHomeState.value?.members?.size ?: 1).coerceAtLeast(1)
        val guildLevel = _guildHomeState.value?.guildLevel ?: 1
        val item = pickRandomGuildEventResource(maxEventItemLevelFor(guildLevel)) ?: run {
            _guildActionError.value = "No eligible items found for an event right now."
            return
        }
        val requiredQuantity = eventPerMemberQuantityFor(item.rarity) * memberCount
        val rewardPerMilestone = eventGuildCoinRewardPerMilestoneFor(item.rarity)
        val xpRewardPerMilestone = eventGuildXpRewardPerMilestoneFor(item.rarity)
        val displayName = item.name + " Drive"

        viewModelScope.launch {
            val result = SupabaseGuildRepository.startGuildEvent(
                guildId = guildId,
                actingCharacterId = actingCharacterId,
                displayName = displayName,
                itemId = item.id,
                skillName = item.skillRequired ?: "",
                requiredQuantity = requiredQuantity,
                guildCoinRewardPerMilestone = rewardPerMilestone,
                guildXpRewardPerMilestone = xpRewardPerMilestone
            )
            result.onFailure {
                _guildActionError.value = it.message ?: it.toString()
            }
            result.onSuccess {
                _guildActionError.value = null
                refreshGuildHome()
            }
        }
    }

    fun contributeToGuildEvent(quantity: Int) {
        val localCharacterId = _currentCharacterId.value ?: return
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        val event = _guildHomeState.value?.activeEvent ?: run {
            _guildActionError.value = "No active guild event."
            return
        }
        if (quantity <= 0) return

        val removal = inventoryService.inventoryFor(localCharacterId).removeItem(event.itemId, quantity)
        if (removal is ServiceResult.Failure) {
            _guildActionError.value = removal.reason
            return
        }
        refreshInventory()

        viewModelScope.launch {
            val result = SupabaseGuildRepository.contributeToGuildEvent(event.id, supabaseCharacterId, quantity)
            result.onFailure {
                // Note: the item was already removed from local inventory above and is
                // not refunded on network failure here, consistent with how other
                // best-effort cloud-sync actions in this codebase behave elsewhere.
                _guildActionError.value = it.message ?: it.toString()
            }
            result.onSuccess {
                _guildActionError.value = null
                refreshGuildHome()
            }
        }
    }

    // Claims any personal guild-event-milestone payouts queued for this
    // character (including ones triggered by other members' contributions)
    // and credits them via the existing self-grant currency path.
    private fun claimGuildEventPayouts() {
        val localCharacterId = _currentCharacterId.value ?: return
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseGuildRepository.claimGuildEventPayouts(supabaseCharacterId)
            result.onSuccess { total ->
                if (total > 0) {
                    grantCombatCoins(localCharacterId, total)
                }
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

    private val _moderationLookupError = MutableStateFlow<String?>(null)
    val moderationLookupError: StateFlow<String?> = _moderationLookupError.asStateFlow()

    // Moderator convenience - resolves a display name (the name shown in
    // chat) to its Supabase character id via admin_find_character_id, then
    // delegates to the existing mute/unmute/grant RPCs directly. A failed
    // lookup (typo, no such name) surfaces in moderationLookupError instead
    // of silently doing nothing.
    fun muteCharacterByNameAsModerator(displayName: String, durationSeconds: Int, reason: String) {
        viewModelScope.launch {
            _moderationLookupError.value = null
            val idResult = SupabaseModerationRepository.findCharacterIdByName(displayName)
            idResult.onFailure { _moderationLookupError.value = it.message ?: it.toString() }
            idResult.onSuccess { characterId ->
                SupabaseModerationRepository.muteCharacter(characterId, durationSeconds, reason)
            }
        }
    }

    fun unmuteCharacterByNameAsModerator(displayName: String) {
        viewModelScope.launch {
            _moderationLookupError.value = null
            val idResult = SupabaseModerationRepository.findCharacterIdByName(displayName)
            idResult.onFailure { _moderationLookupError.value = it.message ?: it.toString() }
            idResult.onSuccess { characterId ->
                SupabaseModerationRepository.unmuteCharacter(characterId)
            }
        }
    }

    fun grantGemsByNameAsModerator(displayName: String, amount: Long, reason: String) {
        viewModelScope.launch {
            _moderationLookupError.value = null
            val idResult = SupabaseModerationRepository.findCharacterIdByName(displayName)
            idResult.onFailure { _moderationLookupError.value = it.message ?: it.toString() }
            idResult.onSuccess { characterId ->
                SupabaseModerationRepository.grantGems(characterId, amount, reason)
            }
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
    private val sessionDropsFor: MutableMap<String, MutableMap<String, Int>> = mutableMapOf()

    val zoneSummaries: List<ZoneSummary>
        get() = ZoneCatalog.zones.sortedBy { it.levelRequirement }.map { zone ->
            ZoneSummary(
                zoneId = zone.id,
                name = zone.name,
                levelRequirement = zone.levelRequirement,
                monsterNames = zone.monsters.map { it.name },
                monsters = zone.monsters.map { monster ->
                    ZoneMonsterSummary(
                        monsterId = monster.id,
                        name = monster.name,
                        level = monster.levelRequirement,
                        weaknessLabel = monster.weakness?.displayName() ?: "None"
                    )
                }
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
            baseMaxHit = 1 + def.stats.maxHitBonus,
            elementalType = def.elementalType
        )
    }

    private fun skillLevel(characterId: String, skillType: SkillType): Int =
        LevelCurve.levelForXp(progressionService.skillBookFor(characterId).get(skillType).xp)

    fun setTrainingSkill(skillType: SkillType): ServiceResult<Unit> {
        val characterId = _currentCharacterId.value

        // Archery/Magic require the matching weapon type equipped - trainingSkill
        // (which skill earns XP) was previously completely unlinked from the
        // equipped weapon's actual combatStyle (which drives the combat math in
        // tickCombat), letting you e.g. train Archery with no bow equipped at all.
        val requiredStyle = when (skillType) {
            SkillType.ARCHERY -> CombatStyle.RANGED
            SkillType.MAGIC -> CombatStyle.MAGIC
            else -> null
        }
        if (requiredStyle != null) {
            val equippedWeaponId = characterId?.let { inventoryService.inventoryFor(it).equippedItemIn(EquipSlot.WEAPON) }
            val equippedStyle = equippedWeaponId?.let { ItemCatalog.find(it)?.combatStyle }
            if (equippedStyle != requiredStyle) {
                val weaponNoun = if (skillType == SkillType.ARCHERY) "a bow" else "a magic weapon"
                val skillLabel = skillType.name.lowercase().replaceFirstChar { it.uppercase() }
                return ServiceResult.Failure("Equip " + weaponNoun + " to train " + skillLabel + ".")
            }
        }

        // Switching the trained skill mid-combat previously left the active
        // session running in whatever zone was already entered - the zone's
        // level gate is only checked in enterCombatZone(), not on every skill
        // switch, so a lower-level skill could keep fighting (and earning XP)
        // in a zone it never actually unlocked. End the session here so the
        // player must legitimately re-enter a zone, correctly re-validated
        // against the new skill's level.
        if (_combatViewData.value != null) {
            leaveCombatZone()
        }
        _trainingSkill.value = skillType
        _trainingSkillLevel.value = characterId?.let { skillLevel(it, skillType) } ?: 1
        return ServiceResult.Success(Unit)
    }

    private fun refreshCombatHp() {
        val characterId = _currentCharacterId.value ?: return
        val state = combatService.stateFor(characterId, maxHpFor(characterId))
        _combatHp.value = state.currentHp to state.maxHp
    }

    fun enterCombatZone(zoneId: String, monsterId: String? = null): ServiceResult<CombatSession> {
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
            sessionDropsFor.getOrPut(characterId) { mutableMapOf() }.clear()
            // Registers an offline-progress queue so combat keeps advancing while
            // the app is closed, mirroring skilling/crafting queues. Mutual
            // exclusion is already guaranteed by the stopQueue() call above.
            // Remember which monster was picked (or clear it -> random) so live combat and
            // offline progress both keep targeting it. Ignored if it isn't in this zone.
            val chosenMonsterId = monsterId?.takeIf { pickedId ->
                ZoneCatalog.zones.find { it.id == zoneId }?.monsters?.any { it.id == pickedId } == true
            }
            if (chosenMonsterId != null) {
                settingsPrefs.edit().putString(combatTargetKey(characterId), chosenMonsterId).apply()
            } else {
                settingsPrefs.edit().remove(combatTargetKey(characterId)).apply()
            }
            offlineIdleService.optIntoOfflineCombat(characterId, zoneId)
            refreshCombatView()
        }
        return result
    }

    fun leaveCombatZone() {
        val characterId = _currentCharacterId.value ?: return
        combatService.leaveZone(characterId)
        offlineIdleService.stopQueue(characterId)
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
            combatLog = log,
            sessionDrops = sessionDropsFor.getOrPut(characterId) { mutableMapOf() }
                .map { (itemId, qty) -> SessionDropEntry(ItemCatalog.find(itemId)?.name ?: formatItemName(itemId), qty) }
                .sortedByDescending { it.quantity }
        )
    }

    private var combatActionProgressSeconds: Double = 0.0

    private fun tickCombat(elapsedSeconds: Long) {
        val characterId = _currentCharacterId.value ?: return
        val state = combatService.stateFor(characterId, maxHpFor(characterId))

        if (state.recovery.isRecovering()) {
            refreshCombatHp()
            return
        }
        if (combatService.resolveRecoveryIfReady(characterId) is ServiceResult.Success) {
            refreshCombatHp()
        }

        var session = state.session ?: return

        if (session.state == SessionState.SEARCHING) {
            val result = combatService.resolveSearchIfReady(characterId)
            if (result is ServiceResult.Success) {
                combatLogFor.getOrPut(characterId) { mutableListOf() }
                    .add(CombatLogEntry(result.value.name + " appears!"))
                // Fall through into the attack logic below using this same tick's
                // elapsedSeconds budget, instead of returning - otherwise every single
                // fight pays an extra full tick-interval of pure dead time before the
                // first attack lands, which gets far more expensive once tick intervals
                // are inflated by background scheduling throttling.
                session = combatService.stateFor(characterId, maxHpFor(characterId)).session ?: return
            } else {
                refreshCombatView()
                return
            }
        }

        if (session.state != SessionState.IN_COMBAT) return

        val weapon = equippedWeapon(characterId)
        val trainingSkill = _trainingSkill.value
        val accuracy: Int
        val maxHit: Int
        val minHit: Int
        val attackSpeedSeconds: Double
        // minHit scales slowly (roughly +1 per 10 levels of the relevant stat) so
        // low-level combat is unaffected, while high-level characters get a
        // meaningfully more consistent damage floor instead of every hit still
        // being able to roll as low as 0. Tunable - CombatSystem.resolveAttack()
        // clamps minHit to never exceed maxHit regardless of the value passed here.
        when (weapon?.style) {
            CombatStyle.MAGIC -> {
                val magicLevel = skillLevel(characterId, SkillType.MAGIC)
                val magicMastery = masteryBonusPercent(magicLevel, hasSkillCapeEquipped(characterId, SkillType.MAGIC), 5.0, 10.0)
                accuracy = ((magicLevel * 2 + weapon.baseAccuracy) * (1.0 + magicMastery / 100.0)).toInt()
                maxHit = (magicLevel / 3) + weapon.baseMaxHit
                minHit = magicLevel / 10
                attackSpeedSeconds = weapon.attackSpeedSeconds
            }
            CombatStyle.RANGED -> {
                val archeryLevel = skillLevel(characterId, SkillType.ARCHERY)
                val archeryMastery = masteryBonusPercent(archeryLevel, hasSkillCapeEquipped(characterId, SkillType.ARCHERY), 5.0, 10.0)
                accuracy = ((archeryLevel * 2 + weapon.baseAccuracy) * (1.0 + archeryMastery / 100.0)).toInt()
                maxHit = (archeryLevel / 3) + weapon.baseMaxHit
                minHit = archeryLevel / 10
                attackSpeedSeconds = weapon.attackSpeedSeconds
            }
            else -> {
                val attackLevel = skillLevel(characterId, SkillType.ATTACK)
                val strengthLevel = skillLevel(characterId, SkillType.STRENGTH)
                val attackMastery = masteryBonusPercent(attackLevel, hasSkillCapeEquipped(characterId, SkillType.ATTACK), 5.0, 10.0)
                val strengthMastery = masteryBonusPercent(strengthLevel, hasSkillCapeEquipped(characterId, SkillType.STRENGTH), 5.0, 10.0)
                accuracy = ((attackLevel * 2 + (weapon?.baseAccuracy ?: 5)) * (1.0 + attackMastery / 100.0)).toInt()
                maxHit = (((strengthLevel / 3) + (weapon?.baseMaxHit ?: 1)) * (1.0 + strengthMastery / 100.0)).toInt()
                minHit = ((strengthLevel / 10) * (1.0 + strengthMastery / 100.0)).toInt()
                attackSpeedSeconds = weapon?.attackSpeedSeconds ?: 2.4
            }
        }

        // Elemental/style weakness matching - MAGIC uses the weapon's specific
        // element (null for the non-elemental starter Staff, matching nothing),
        // RANGED/MELEE match monsters weak to those whole combat styles.
        val damageType: DamageType? = when (weapon?.style) {
            CombatStyle.MAGIC -> weapon.elementalType
            CombatStyle.RANGED -> DamageType.RANGED
            else -> DamageType.MELEE
        }

        combatActionProgressSeconds += elapsedSeconds
        if (combatActionProgressSeconds < attackSpeedSeconds) {
            refreshCombatView()
            return
        }

        val log = combatLogFor.getOrPut(characterId) { mutableListOf() }

        while (combatActionProgressSeconds >= attackSpeedSeconds) {
            combatActionProgressSeconds -= attackSpeedSeconds

            val loadout = CombatLoadout(
                style = weapon?.style ?: CombatStyle.MELEE,
                trainingSkill = trainingSkill,
                selectedPrayerId = inventoryService.inventoryFor(characterId).selectedPrayerId,
                equippedWeapon = weapon,
                equippedSpell = null,
                autoHealThresholdPercent = inventoryService.inventoryFor(characterId).autoHealThresholdPercent,
                autoFleeThresholdPercent = inventoryService.inventoryFor(characterId).autoFleeThresholdPercent,
                damageType = damageType
            )

            val result = combatService.resolveAttack(characterId, loadout, accuracy, maxHit, minHit)

            if (result is ServiceResult.Success) {
                val attack = result.value
                val monsterDefense = session.currentMonster?.defenseRating ?: 1
                lastHitChancePercent = ((accuracy.toDouble() / (accuracy + monsterDefense)) * 100.0).coerceIn(0.0, 100.0)
                lastDamageDealt = attack.damageDealt

                if (attack.didHit) {
                    val weaknessNote = if (attack.wasWeaknessHit) " Super effective!" else ""
                    log.add(CombatLogEntry("You hit for " + attack.damageDealt + "." + weaknessNote))
                    val xpGrant = progressionService.grantXp(characterId, trainingSkill, (attack.damageDealt * 4 + 5).toLong(), guildXpBonusEffects() + capeBonusEffects(characterId))
                    if (xpGrant is ServiceResult.Success) refreshSkills()
                } else {
                    log.add(CombatLogEntry("You missed."))
                }

                if (attack.monsterDefeated) {
                    val defeatedName = session.currentMonster?.name ?: "the enemy"
                    log.add(CombatLogEntry("Defeated " + defeatedName + "!"))
                    val loot = combatService.collectLoot(characterId)
                    if (loot is ServiceResult.Success && loot.value.isNotEmpty()) {
                        loot.value.forEach { entry ->
                            inventoryService.inventoryFor(characterId).addItem(entry.itemId, entry.minQty)
                            sessionDropsFor.getOrPut(characterId) { mutableMapOf() }.merge(entry.itemId, entry.minQty, Int::plus)
                        }
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
                    val rawDmg = Random.nextInt(1, (monster.defenseRating / 3).coerceAtLeast(1) + 1)
                    val activePrayerId = inventoryService.inventoryFor(characterId).selectedPrayerId
                    val prayerSpecificDmg = if (activePrayerId == "rock_skin") {
                        (rawDmg * 0.8).toInt().coerceAtLeast(1)
                    } else {
                        rawDmg
                    }
                    // Mastery Perk (Prayer): extra reduction whenever ANY prayer is
                    // active, stacking on top of that prayer's own specific effect.
                    val prayerMasteryReductionPercent = if (activePrayerId != null) {
                        val prayerLevel = skillLevel(characterId, SkillType.PRAYER)
                        masteryBonusPercent(prayerLevel, hasSkillCapeEquipped(characterId, SkillType.PRAYER), 5.0, 10.0)
                    } else {
                        0.0
                    }
                    val prayerAdjustedDmg = (prayerSpecificDmg * (1.0 - prayerMasteryReductionPercent / 100.0)).toInt().coerceAtLeast(1)
                    // Defense passively reduces incoming damage regardless of which skill is
                    // currently selected to train, matching the classic "defense stat" model
                    // rather than only mattering while actively training it. Capped at 50%
                    // reduction so high Defense meaningfully helps survivability without making
                    // combat damage-immune; at least 1 damage always gets through.
                    val defenseLevel = skillLevel(characterId, SkillType.DEFENSE)
                    val defenseMastery = masteryBonusPercent(defenseLevel, hasSkillCapeEquipped(characterId, SkillType.DEFENSE), 5.0, 10.0)
                    val defenseReductionPercent = (defenseLevel * 0.5 + defenseMastery).coerceAtMost(50.0)
                    val dmg = (prayerAdjustedDmg * (1.0 - defenseReductionPercent / 100.0)).toInt().coerceAtLeast(1)
                    combatService.applyDamageToCharacter(characterId, dmg)
                    log.add(CombatLogEntry(monster.name + " hits you for " + dmg + "."))
                }

                val freshState = combatService.stateFor(characterId, maxHpFor(characterId))
                if (freshState.currentHp <= 0) {
                    log.add(CombatLogEntry("You were defeated and are recovering."))
                    combatActionProgressSeconds = 0.0
                    break
                } else if (freshState.maxHp > 0 &&
                    (freshState.currentHp * 100 / freshState.maxHp) <= inventoryService.inventoryFor(characterId).autoFleeThresholdPercent
                ) {
                    combatService.leaveZone(characterId)
                    log.add(CombatLogEntry("Fled to safety."))
                    combatActionProgressSeconds = 0.0
                    break
                }
            }

            val postAttackSession = combatService.stateFor(characterId, maxHpFor(characterId)).session
            if (postAttackSession == null || postAttackSession.state != SessionState.IN_COMBAT) break
        }

        refreshCombatView()
    }

    data class LoadoutSettingsSnapshot(
        val selectedFoodId: String?,
        val selectedPotionId: String?,
        val potionTimerRemainingSeconds: Int,
        val autoHealThresholdPercent: Int,
        val autoFleeThresholdPercent: Int,
        val selectedPrayerId: String? = null
    )

    private val _loadoutSettings = MutableStateFlow(LoadoutSettingsSnapshot(null, null, 0, 30, 10, null))
    val loadoutSettings: StateFlow<LoadoutSettingsSnapshot> = _loadoutSettings.asStateFlow()

    val prayerOptions: List<PrayerDefinition> get() = PrayerCatalog

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

    fun selectPrayer(prayerId: String?) {
        val characterId = _currentCharacterId.value ?: return
        if (prayerId != null) {
            val prayer = PrayerCatalog.find { it.id == prayerId } ?: return
            if (skillLevel(characterId, SkillType.PRAYER) < prayer.levelRequired) return
        }
        inventoryService.inventoryFor(characterId).selectPrayer(prayerId)
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

    private var buryActionProgressSeconds: Long = 0

    fun startBuryAction(itemId: String, quantity: Int) {
        val characterId = _currentCharacterId.value ?: return
        val boneInfo = PrayerBoneRequirements[itemId] ?: return
        val prayerLevel = skillLevel(characterId, SkillType.PRAYER)
        if (prayerLevel < boneInfo.levelRequired) return
        val inventory = inventoryService.inventoryFor(characterId)
        val available = inventory.quantityOf(itemId)
        if (available <= 0 || quantity <= 0) return
        val cappedQuantity = minOf(quantity, available)
        val baseSeconds = 2L
        val effectiveSeconds = if (inventory.selectedPrayerId == "efficient_hands") {
            (baseSeconds * 0.85).toLong().coerceAtLeast(1L)
        } else {
            baseSeconds
        }
        // Starting a bury queue stops any active combat session - only one
        // activity can run at a time.
        leaveCombatZone()
        offlineIdleService.stopQueue(characterId)
        offlineIdleService.startBuryQueue(characterId, itemId, cappedQuantity, effectiveSeconds)
        offlineIdleService.recordLastSeen(characterId)
        buryActionProgressSeconds = 0
        refreshActiveQueue()
    }

    fun stopBuryAction() {
        val characterId = _currentCharacterId.value ?: return
        offlineIdleService.stopQueue(characterId)
        buryActionProgressSeconds = 0
        refreshActiveQueue()
    }

    private fun tickBurying(elapsedSeconds: Long) {
        val characterId = _currentCharacterId.value ?: return
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.BuryQueue ?: return

        buryActionProgressSeconds += elapsedSeconds
        if (buryActionProgressSeconds < queue.secondsPerAction) return

        val attempts = (buryActionProgressSeconds / queue.secondsPerAction).toInt()
        buryActionProgressSeconds %= queue.secondsPerAction

        val remainingToTarget = queue.targetQuantity - queue.quantityCompleted
        val cappedAttempts = minOf(attempts, remainingToTarget)
        if (cappedAttempts <= 0) return

        val boneInfo = PrayerBoneRequirements[queue.itemId] ?: return
        val inventory = inventoryService.inventoryFor(characterId)
        val available = inventory.quantityOf(queue.itemId)
        val effectiveAttempts = minOf(cappedAttempts, available)

        if (effectiveAttempts > 0) {
            inventory.removeItem(queue.itemId, effectiveAttempts)
            progressionService.grantXp(characterId, SkillType.PRAYER, boneInfo.xpAmount * effectiveAttempts, guildXpBonusEffects())
            queue.quantityCompleted += effectiveAttempts
            refreshInventory()
            refreshSkills()
            refreshActiveQueue()
        }

        if (queue.isTargetReached()) {
            offlineIdleService.stopQueue(characterId)
            buryActionProgressSeconds = 0
            refreshActiveQueue()
            _actionStoppedNotifications.value = _actionStoppedNotifications.value + ActionStoppedNotice(
                itemName = formatItemName(queue.itemId),
                reason = "Buried " + queue.quantityCompleted + "x " + formatItemName(queue.itemId) +
                    " (+" + (queue.quantityCompleted * boneInfo.xpAmount) + " Prayer XP).",
                isCompletion = true
            )
        } else if (effectiveAttempts < cappedAttempts) {
            // Ran out of bones mid-batch - stop instead of spinning uselessly.
            offlineIdleService.stopQueue(characterId)
            buryActionProgressSeconds = 0
            refreshActiveQueue()
            _actionStoppedNotifications.value = _actionStoppedNotifications.value + ActionStoppedNotice(
                itemName = formatItemName(queue.itemId),
                reason = "Ran out of " + formatItemName(queue.itemId) + "."
            )
        }
    }

    private fun tickConsumables(elapsedSeconds: Long) {
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
                inventory.potionTimerRemainingSeconds = (inventory.potionTimerRemainingSeconds - elapsedSeconds.toInt()).coerceAtLeast(0)
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

    private val _unlockedPresets = MutableStateFlow<Set<String>>(emptySet())
    val unlockedPresets: StateFlow<Set<String>> = _unlockedPresets.asStateFlow()

    private val _premiumActionError = MutableStateFlow<String?>(null)
    val premiumActionError: StateFlow<String?> = _premiumActionError.asStateFlow()

    // =========================================================
    // CHAT COSMETICS (titles + badges) + PER-MONSTER KILL COUNTS
    // Ownership / equipped state / kill totals are server-side
    // (see cosmetics_schema.sql). This block keeps a local tally of
    // kills (live AND offline kills both fire combatService.onMonsterKilled),
    // flushes it to the server every ~30s, loads owned/equipped state
    // once per character, and claims earned titles (Master <Skill> at
    // level 99, Master <Monster> Slayer at 10,000 kills) as they qualify.
    // Everything runs in its own background loop and is best-effort -
    // gameplay never waits on it.
    // =========================================================
    private val cosmeticKillTally: MutableMap<String, Int> = mutableMapOf() // key = localCharacterId + "|" + monsterId
    private var cosmeticServerKills: Map<String, Long> = emptyMap()
    private var cosmeticsLoadedFor: String? = null

    private val _ownedCosmetics = MutableStateFlow<Set<String>>(emptySet())
    val ownedCosmetics: StateFlow<Set<String>> = _ownedCosmetics.asStateFlow()

    private val _equippedTitleId = MutableStateFlow<String?>(null)
    val equippedTitleId: StateFlow<String?> = _equippedTitleId.asStateFlow()

    private val _equippedBadgeId = MutableStateFlow<String?>(null)
    val equippedBadgeId: StateFlow<String?> = _equippedBadgeId.asStateFlow()

    private val _monsterKillTotals = MutableStateFlow<Map<String, Long>>(emptyMap())
    val monsterKillTotals: StateFlow<Map<String, Long>> = _monsterKillTotals.asStateFlow()

    private val _cosmeticSkillLevels = MutableStateFlow<Map<String, Int>>(emptyMap())
    val cosmeticSkillLevels: StateFlow<Map<String, Int>> = _cosmeticSkillLevels.asStateFlow()

    private val _cosmeticActionError = MutableStateFlow<String?>(null)
    val cosmeticActionError: StateFlow<String?> = _cosmeticActionError.asStateFlow()

    init {
        combatService.onMonsterKilled = { killerCharacterId, monster ->
            if (killerCharacterId == _currentCharacterId.value) {
                synchronized(cosmeticKillTally) {
                    val key = killerCharacterId + "|" + monster.id
                    cosmeticKillTally[key] = (cosmeticKillTally[key] ?: 0) + 1
                }
            }
        }
        viewModelScope.launch(Dispatchers.Default) {
            // Delay first: the constructor may still be running when this coroutine starts.
            delay(3000L)
            while (true) {
                val supabaseId = _currentSupabaseCharacterId.value
                val localId = _currentCharacterId.value
                if (supabaseId != null && localId != null) {
                    runCatching { cosmeticsTick(localId, supabaseId) }
                }
                delay(if (cosmeticsLoadedFor == supabaseId) 30_000L else 3_000L)
            }
        }
    }

    private suspend fun cosmeticsTick(localId: String, supabaseId: String) {
        if (cosmeticsLoadedFor != supabaseId) {
            val owned = SupabaseCosmeticRepository.myCosmetics(supabaseId).getOrNull() ?: return
            val kills = SupabaseCosmeticRepository.monsterKills(supabaseId).getOrNull() ?: return
            val equipped = SupabaseCosmeticRepository.fetchEquipped(listOf(supabaseId))[supabaseId]
            _ownedCosmetics.value = owned.toSet()
            _equippedTitleId.value = equipped?.titleId
            _equippedBadgeId.value = equipped?.badgeId
            cosmeticServerKills = kills
            cosmeticsLoadedFor = supabaseId
        }

        val prefix = localId + "|"
        val toSend: Map<String, Int> = synchronized(cosmeticKillTally) {
            val mine = cosmeticKillTally.filterKeys { it.startsWith(prefix) }
            mine.keys.forEach { cosmeticKillTally.remove(it) }
            mine.mapKeys { it.key.removePrefix(prefix) }
        }
        if (toSend.isNotEmpty()) {
            val sent = SupabaseCosmeticRepository.recordKills(supabaseId, toSend)
            if (sent.isSuccess) {
                val merged = cosmeticServerKills.toMutableMap()
                toSend.forEach { (monsterId, count) -> merged[monsterId] = (merged[monsterId] ?: 0L) + count }
                cosmeticServerKills = merged
            } else {
                // Put them back so the next pass retries.
                synchronized(cosmeticKillTally) {
                    toSend.forEach { (monsterId, count) ->
                        val key = prefix + monsterId
                        cosmeticKillTally[key] = (cosmeticKillTally[key] ?: 0) + count
                    }
                }
            }
        }

        val pendingNow: Map<String, Int> = synchronized(cosmeticKillTally) {
            cosmeticKillTally.filterKeys { it.startsWith(prefix) }.mapKeys { it.key.removePrefix(prefix) }
        }
        val totals = cosmeticServerKills.toMutableMap()
        pendingNow.forEach { (monsterId, count) -> totals[monsterId] = (totals[monsterId] ?: 0L) + count }
        _monsterKillTotals.value = totals
        _cosmeticSkillLevels.value = SkillType.values().associate { it.name to skillLevel(localId, it) }

        claimEarnedTitles(supabaseId)
    }

    private suspend fun claimEarnedTitles(supabaseId: String) {
        val owned = _ownedCosmetics.value
        val levels = _cosmeticSkillLevels.value
        for (title in ChatCosmeticCatalog.earnedTitles) {
            if (title.id in owned) continue
            val skill = title.earnedSkill
            val monsterId = title.earnedMonsterId
            val qualifies = when {
                skill != null -> (levels[skill.name] ?: 0) >= ChatCosmeticCatalog.MASTER_SKILL_LEVEL
                monsterId != null -> (cosmeticServerKills[monsterId] ?: 0L) >= ChatCosmeticCatalog.SLAYER_KILLS_REQUIRED
                else -> false
            }
            if (!qualifies) continue
            val claimed = SupabaseCosmeticRepository.claimEarnedTitle(supabaseId, title.id)
            if (claimed.isSuccess) {
                _ownedCosmetics.value = _ownedCosmetics.value + title.id
            }
        }
    }

    fun purchaseCosmetic(cosmeticId: String) {
        val supabaseId = _currentSupabaseCharacterId.value ?: return
        val cosmetic = ChatCosmeticCatalog.find(cosmeticId) ?: return
        if (cosmetic.isEarned) {
            _cosmeticActionError.value = "That one is earned in-game, not bought."
            return
        }
        if (cosmeticId in _ownedCosmetics.value) {
            _cosmeticActionError.value = "You already own that."
            return
        }
        viewModelScope.launch {
            val result = SupabaseCosmeticRepository.purchaseCosmetic(supabaseId, cosmeticId)
            result.onFailure { _cosmeticActionError.value = it.message ?: it.toString() }
            result.onSuccess {
                _cosmeticActionError.value = null
                _ownedCosmetics.value = _ownedCosmetics.value + cosmeticId
                refreshCurrency()
            }
        }
    }

    fun equipTitle(titleId: String?) = saveEquippedCosmetics(titleId, _equippedBadgeId.value)

    fun equipBadge(badgeId: String?) = saveEquippedCosmetics(_equippedTitleId.value, badgeId)

    private fun saveEquippedCosmetics(titleId: String?, badgeId: String?) {
        val supabaseId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseCosmeticRepository.setEquipped(supabaseId, titleId, badgeId)
            result.onFailure { _cosmeticActionError.value = it.message ?: it.toString() }
            result.onSuccess {
                _cosmeticActionError.value = null
                _equippedTitleId.value = titleId
                _equippedBadgeId.value = badgeId
                refreshChatMessages()
            }
        }
    }

    init {
        viewModelScope.launch(Dispatchers.Default) {
            var lastTickMillis = System.currentTimeMillis()
            while (true) {
                delay(1000L)
                val now = System.currentTimeMillis()
                val elapsedSeconds = ((now - lastTickMillis) / 1000L).coerceAtLeast(1L)
                lastTickMillis += elapsedSeconds * 1000L
                tickSkilling(elapsedSeconds)
                tickCrafting(elapsedSeconds)
                tickBurying(elapsedSeconds)
                tickConsumables(elapsedSeconds)
                tickCombat(elapsedSeconds)
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
        saved.combatSessions.forEach { combatService.restoreSession(it) }
        saved.offlineCombatQueues.forEach { offlineIdleService.restoreOfflineCombatQueue(it) }
        saved.buryQueues.forEach { offlineIdleService.restoreBuryQueue(it) }
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
    recovered.combatSessions.forEach { combatService.restoreSession(it) }
    recovered.offlineCombatQueues.forEach { offlineIdleService.restoreOfflineCombatQueue(it) }
    recovered.buryQueues.forEach { offlineIdleService.restoreBuryQueue(it) }

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
        viewModelScope.launch {
            val result = SupabaseMarketRepository.myRecentSales(supabaseCharacterId, since)
            result.onFailure {
                _marketActionError.value = it.message ?: it.toString()
            }
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
                    // Use the server's own latest executed_at as the new checkpoint,
                    // never the device clock - avoids any client/server clock-skew risk.
                    val latestServerTimestamp = rows.maxOf { it.executedAt }
                    offlineIdleService.recordSaleCheckAt(characterId, latestServerTimestamp)
                }
            }
        }
    }
    fun saveGame() {
        _currentCharacterId.value?.let { characterId ->
            inventoryService.inventoryFor(characterId).trainingSkillId = _trainingSkill.value.name
        }
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
            marketService.exportPriceHistory(),
            combatService.exportSessions(),
            offlineIdleService.exportOfflineCombatQueues(),
            offlineIdleService.exportBuryQueues()
        )
        val supabaseCharacterId = _currentSupabaseCharacterId.value
        val json = repository.currentSaveJson()
        if (supabaseCharacterId != null && json != null) {
            viewModelScope.launch {
                SupabaseCharacterRepository.uploadCharacterSave(supabaseCharacterId, json)
            }
        }
        val localCharacterIdForSkills = _currentCharacterId.value
        if (supabaseCharacterId != null && localCharacterIdForSkills != null) {
            viewModelScope.launch {
                SupabaseCharacterRepository.reportSkillLevels(
                    supabaseCharacterId,
                    progressionService.skillBookFor(localCharacterIdForSkills).all()
                )
            }
        }
    }

    fun selectCharacter(characterId: String) {
        _currentCharacterId.value = characterId

        // Restore the persisted training skill immediately - this is purely
        // local (no Supabase dependency), so it must run regardless of whether
        // the auth check below succeeds, fails, or times out. Previously this
        // only happened after auth succeeded, so a slow/failed auth handshake
        // (common right after a cold app start) silently skipped it every time
        // via the early-return path, leaving trainingSkill stuck at ATTACK.
        fun restoreTrainingSkillFor(id: String) {
            val restoredTrainingSkillId = inventoryService.inventoryFor(id).trainingSkillId
            val restoredTrainingSkill = restoredTrainingSkillId?.let {
                runCatching { SkillType.valueOf(it) }.getOrNull()
            } ?: SkillType.ATTACK
            setTrainingSkill(restoredTrainingSkill)
        }
        restoreTrainingSkillFor(characterId)

        val selectedCharacter = accountService.charactersFor(_currentAccountId.value ?: "").firstOrNull { it.id == characterId }
        if (selectedCharacter != null) {
            viewModelScope.launch {
                val authState = withTimeoutOrNull(10_000L) {
                    supabaseAuthState.first { it != SupabaseAuthState.SIGNING_IN }
                }
                if (authState != SupabaseAuthState.SIGNED_IN) {
                    _characterSyncError.value = "Not signed in to multiplayer services yet - character sync will retry on next action."
                    resolveOfflineRewardsAndSync(characterId)
                    return@launch
                }
                val result = SupabaseCharacterRepository.getOrCreateCharacter(characterId, selectedCharacter.displayName)
                result.onFailure { _characterSyncError.value = it.message ?: it.toString() }
                result.onSuccess { _characterSyncError.value = null }
                _currentSupabaseCharacterId.value = result.getOrNull()
                val supabaseCharacterId = result.getOrNull()
                var recoveredToRemoteId: String? = null
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
                                recovered.combatSessions.forEach { combatService.restoreSession(it) }
                                recovered.offlineCombatQueues.forEach { offlineIdleService.restoreOfflineCombatQueue(it) }
                                recovered.buryQueues.forEach { offlineIdleService.restoreBuryQueue(it) }
                                _currentCharacterId.value = remoteLocalId
                                val recoveredCharacter = recovered.characters.firstOrNull { it.id == remoteLocalId }
                                if (recoveredCharacter != null) {
                                    _currentAccountId.value = recoveredCharacter.accountId
                                }
                                recoveredToRemoteId = remoteLocalId
                            }
                        }
                    }
                }
                val finalCharacterId = recoveredToRemoteId ?: characterId
                // Only relevant for the rare cloud-recovery case where the character
                // id changed mid-flow - re-apply against the correct (recovered) id.
                if (finalCharacterId != characterId) {
                    restoreTrainingSkillFor(finalCharacterId)
                }
                // Only one of these ever fires per selection: whichever character id
                // turned out to be correct once the async cloud-recovery check above
                // finished. Previously an immediate, unconditional call fired outside
                // this coroutine entirely, racing this check - it would briefly show
                // an offline-progress popup built from the wrong (pre-recovery)
                // character before this corrected one silently replaced it.
                resolveOfflineRewardsAndSync(finalCharacterId)
                // Prefetch guild/chat data now (a live signed-in session is
                // guaranteed at this point) instead of waiting for the user to
                // visit the Guild tab, where these previously only started
                // fetching on first navigation - making the network round trip
                // visible every time instead of already being warm.
                refreshGuildHome()
                loadInitialChatState()
                // Prefetch guild/chat data now (a live signed-in session is
                // guaranteed at this point) instead of waiting for the user to
                // visit the Guild tab, where these previously only started
                // fetching on first navigation - making the network round trip
                // visible every time instead of already being warm.
                refreshGuildHome()
                loadInitialChatState()
                // Prefetch guild/chat data now (a live signed-in session is
                // guaranteed at this point) instead of waiting for the user to
                // visit the Guild tab, where these previously only started
                // fetching on first navigation - making the network round trip
                // visible every time instead of already being warm.
                refreshGuildHome()
                loadInitialChatState()
                // Prefetch guild/chat data now (a live signed-in session is
                // guaranteed at this point) instead of waiting for the user to
                // visit the Guild tab, where these previously only started
                // fetching on first navigation - making the network round trip
                // visible every time instead of already being warm.
                refreshGuildHome()
                loadInitialChatState()
            }
        } else {
            _characterSyncError.value = "selectedCharacter was null - accountId=${_currentAccountId.value}, characterId=$characterId"
            resolveOfflineRewardsAndSync(characterId)
        }
    }

    // Grants offline-progress rewards (skilling/crafting), records last-seen, and
    // syncs currency/market state for the given character. Extracted so it can be
    // re-run against a cloud-recovered character id after async recovery completes
    // (see selectCharacter) - a throwaway local character's offline queue is never
    // the "real" one in that scenario, so re-resolving against the recovered
    // character's actual data is the correct behavior, not just a race-condition
    // workaround.
    // Handles the case where the app cold-starts directly into AppFlowState.InGame
    // (a character id was already cached locally) - selectCharacter() is never
    // called on this path, so nothing would otherwise trigger offline-progress
    // resolution or restore the persisted training skill for this session.
    fun resumeCurrentCharacterIfNeeded() {
        val characterId = _currentCharacterId.value ?: return
        val restoredTrainingSkillId = inventoryService.inventoryFor(characterId).trainingSkillId
        val restoredTrainingSkill = restoredTrainingSkillId?.let {
            runCatching { SkillType.valueOf(it) }.getOrNull()
        } ?: SkillType.ATTACK
        setTrainingSkill(restoredTrainingSkill)
        resolveOfflineRewardsAndSync(characterId)
    }

    private fun resolveOfflineRewardsAndSync(characterId: String) {
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.SkillingQueue
        if (queue != null) {
            val result = offlineIdleService.resolveOfflineProgress(characterId)
            if (result is ServiceResult.Success && result.value.actionsCompleted > 0) {
                val skillType = SkillType.valueOf(queue.skillId)
                val action = ActionCatalog.find(skillType, queue.itemId)
                if (action != null) {
                    val xpEarned = action.xpPerAction * result.value.actionsCompleted
                    progressionService.grantXp(characterId, skillType, xpEarned, guildXpBonusEffects())
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

        val buryQueue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.BuryQueue
        if (buryQueue != null) {
            val buryResult = offlineIdleService.resolveOfflineProgress(characterId)
            if (buryResult is ServiceResult.Success && buryResult.value.actionsCompleted > 0) {
                val boneInfo = PrayerBoneRequirements[buryQueue.itemId]
                if (boneInfo != null) {
                    val inventory = inventoryService.inventoryFor(characterId)
                    val available = inventory.quantityOf(buryQueue.itemId)
                    val effectiveActions = minOf(buryResult.value.actionsCompleted, available)
                    if (effectiveActions > 0) {
                        inventory.removeItem(buryQueue.itemId, effectiveActions)
                        val xpGranted = boneInfo.xpAmount * effectiveActions
                        progressionService.grantXp(characterId, SkillType.PRAYER, xpGranted, guildXpBonusEffects())
                        _offlineSummary.value = OfflineSummary(
                            awaySeconds = buryResult.value.claimedElapsed.seconds,
                            skillActionName = "Bury " + formatItemName(buryQueue.itemId),
                            itemName = formatItemName(buryQueue.itemId),
                            quantity = effectiveActions,
                            xpEarned = xpGranted
                        )
                    }
                }
            }
        }

        val combatQueue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.OfflineCombatQueue
        if (combatQueue != null) {
            val combatResult = offlineIdleService.resolveOfflineProgress(characterId)
            if (combatResult is ServiceResult.Success) {
                val elapsedSeconds = combatResult.value.effectiveElapsed.seconds
                if (elapsedSeconds > 0) {
                    // Mirrors tickCombat()'s per-style accuracy/max-hit computation exactly,
                    // using the character's live gear/levels at resolution time.
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
                    val selectedPrayerId = inventoryService.inventoryFor(characterId).selectedPrayerId
                    val prayerAccuracy = if (selectedPrayerId == "clarity_of_thought") (accuracy * 1.1).toInt() else accuracy
                    val prayerMaxHit = if (selectedPrayerId == "burst_of_strength") (maxHit * 1.1).toInt() else maxHit
                    val prayerDropRateMultiplier = if (selectedPrayerId == "fortunes_favor") 1.15 else 1.0
                    val outcome = combatService.resolveOfflineCombat(characterId, combatQueue.zoneId, elapsedSeconds, prayerAccuracy, prayerMaxHit, prayerDropRateMultiplier)
                    if (outcome is ServiceResult.Success && outcome.value.estimatedKills > 0) {
                        if (outcome.value.xpEarned > 0) {
                            progressionService.grantXp(characterId, trainingSkill, outcome.value.xpEarned, guildXpBonusEffects())
                        }
                        val loot = combatService.collectLoot(characterId)
                        if (loot is ServiceResult.Success) {
                            loot.value.forEach { entry ->
                                inventoryService.inventoryFor(characterId).addItem(entry.itemId, entry.minQty)
                            }
                        }
                        val coinsEarned = combatService.collectCoins(characterId)
                        if (coinsEarned > 0) {
                            grantCombatCoins(characterId, coinsEarned)
                        }
                        _offlineSummary.value = OfflineSummary(
                            awaySeconds = combatResult.value.claimedElapsed.seconds,
                            skillActionName = "Combat",
                            itemName = "kills",
                            quantity = outcome.value.estimatedKills,
                            xpEarned = outcome.value.xpEarned
                        )
                    }
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
        val requiredSeedId = FarmingSeedRequirements[itemId]
        if (requiredSeedId != null) {
            val availableSeeds = inventoryService.inventoryFor(characterId).quantityOf(requiredSeedId)
            if (availableSeeds <= 0) return
        }
        // Starting a skill stops any active combat session - only one
        // activity can run at a time.
        leaveCombatZone()
        offlineIdleService.stopQueue(characterId)
        val effectiveSecondsPerAction = if (inventoryService.inventoryFor(characterId).selectedPrayerId == "efficient_hands") {
            (action.secondsPerAction * 0.85).toLong().coerceAtLeast(1L)
        } else {
            action.secondsPerAction
        }
        offlineIdleService.startSkillingQueue(characterId, skillType.name, itemId, effectiveSecondsPerAction)
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

    private fun tickSkilling(elapsedSeconds: Long) {
        val characterId = _currentCharacterId.value ?: return
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.SkillingQueue ?: return

        skillActionProgressSeconds += elapsedSeconds
        if (skillActionProgressSeconds < queue.secondsPerAction) return

        val actionsCompleted = skillActionProgressSeconds / queue.secondsPerAction
        skillActionProgressSeconds %= queue.secondsPerAction

        val skillType = SkillType.valueOf(queue.skillId)
        val action = ActionCatalog.find(skillType, queue.itemId)
        if (action != null) {
            val inventory = inventoryService.inventoryFor(characterId)
            val requiredSeedId = FarmingSeedRequirements[queue.itemId]
            val effectiveActions = if (requiredSeedId != null) {
                minOf(actionsCompleted, inventory.quantityOf(requiredSeedId).toLong())
            } else {
                actionsCompleted
            }
            if (effectiveActions > 0) {
                if (requiredSeedId != null) {
                    inventory.removeItem(requiredSeedId, effectiveActions.toInt())
                }
                progressionService.grantXp(characterId, skillType, action.xpPerAction * effectiveActions, guildXpBonusEffects() + capeBonusEffects(characterId))
                inventory.addItem(queue.itemId, effectiveActions.toInt())
                if (skillType == SkillType.MINING) {
                    MiningBonusGemTable.rollAndGrant(inventory, effectiveActions.toInt())
                }
                // Mastery Perk (gathering skills): chance of one bonus item per
                // completed action, rolled independently per action.
                val gatherBook = progressionService.skillBookFor(characterId)
                val gatherActiveEffects = UnlockTable.allActiveEffects(gatherBook) + capeBonusEffects(characterId)
                val dropRateBoostPercent = EffectStacker.totalDropRateBoostPercent(gatherActiveEffects, skillType)
                if (dropRateBoostPercent > 0.0) {
                    var bonusCount = 0
                    repeat(effectiveActions.toInt()) {
                        if (Random.nextDouble(0.0, 100.0) < dropRateBoostPercent) bonusCount++
                    }
                    if (bonusCount > 0) inventory.addItem(queue.itemId, bonusCount)
                }
            }
            if (requiredSeedId != null && effectiveActions < actionsCompleted) {
                // Ran out of seeds mid-batch - stop the queue instead of spinning uselessly.
                offlineIdleService.stopQueue(characterId)
                skillActionProgressSeconds = 0
                _actionStoppedNotifications.value = _actionStoppedNotifications.value + ActionStoppedNotice(
                    itemName = formatItemName(queue.itemId),
                    reason = "Out of " + formatItemName(requiredSeedId) + "."
                )
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

    data class ActionStoppedNotice(val itemName: String, val reason: String, val isCompletion: Boolean = false)

    private val _actionStoppedNotifications = MutableStateFlow<List<ActionStoppedNotice>>(emptyList())
    val actionStoppedNotifications: StateFlow<List<ActionStoppedNotice>> = _actionStoppedNotifications.asStateFlow()

    fun dismissActionStoppedNotification() {
        _actionStoppedNotifications.value = _actionStoppedNotifications.value.drop(1)
    }

    private data class CraftBatchResult(val successfulCrafts: Int, val itemsProduced: Int, val xpGranted: Long, val stoppedReason: String? = null)

    private fun craftItems(characterId: String, itemId: String, attempts: Int): CraftBatchResult {
        val recipe = RecipeCatalog.forOutput(itemId) ?: return CraftBatchResult(0, 0, 0)
        val skillType = SkillType.valueOf(recipe.skillRequired)
        val book = progressionService.skillBookFor(characterId)
        val skill = book.all().find { it.type == skillType }
        val playerLevel = if (skill != null) LevelCurve.levelForXp(skill.xp) else 1
        val inventory = inventoryService.inventoryFor(characterId)
        val xpPerAttempt = CraftingTierCurve.xpFor(recipe.levelRequired)

        val craftActiveEffects = UnlockTable.allActiveEffects(book) + capeBonusEffects(characterId)
        val materialSaveChancePercent = EffectStacker.totalMaterialSaveChancePercent(craftActiveEffects, skillType)
        val successBonusPercent = EffectStacker.totalCraftSuccessBoostPercent(craftActiveEffects, skillType)

        var successes = 0
        var totalProduced = 0
        var xpGranted = 0L
        var stoppedReason: String? = null
        for (i in 0 until attempts) {
            val result = craftingService.craftOnce(inventory, itemId, playerLevel, materialSaveChancePercent, successBonusPercent)
            if (result is ServiceResult.Success) {
                xpGranted += xpPerAttempt
                if (result.value.succeeded) {
                    successes += 1
                    totalProduced += result.value.quantityProduced
                }
            } else {
                stoppedReason = (result as? ServiceResult.Failure)?.reason ?: "Missing materials or requirements."
                break
            }
        }
        if (xpGranted > 0) {
            progressionService.grantXp(characterId, skillType, xpGranted, guildXpBonusEffects() + capeBonusEffects(characterId))
        }
        return CraftBatchResult(successes, totalProduced, xpGranted, stoppedReason)
    }

    fun startCraftingAction(itemId: String, targetQuantity: Int? = null) {
        val characterId = _currentCharacterId.value ?: return
        val recipe = RecipeCatalog.forOutput(itemId) ?: return
        // Starting crafting stops any active combat session - only one
        // activity can run at a time.
        leaveCombatZone()
        offlineIdleService.stopQueue(characterId)
        val baseCraftSeconds = CraftingTierCurve.secondsFor(recipe.levelRequired)
        val effectiveCraftSeconds = if (inventoryService.inventoryFor(characterId).selectedPrayerId == "efficient_hands") {
            (baseCraftSeconds * 0.85).toLong().coerceAtLeast(1L)
        } else {
            baseCraftSeconds
        }
        offlineIdleService.startCraftingQueue(
            characterId,
            itemId,
            effectiveCraftSeconds,
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

    private fun tickCrafting(elapsedSeconds: Long) {
        val characterId = _currentCharacterId.value ?: return
        val queue = offlineIdleService.activeQueueFor(characterId) as? ActiveQueue.CraftingQueue ?: return

        craftActionProgressSeconds += elapsedSeconds
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
        } else if (batch.stoppedReason != null) {
            offlineIdleService.stopQueue(characterId)
            craftActionProgressSeconds = 0
            refreshActiveQueue()
            _actionStoppedNotifications.value = _actionStoppedNotifications.value + ActionStoppedNotice(
                itemName = formatItemName(queue.itemId),
                reason = batch.stoppedReason
            )
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
        _inventoryCapacity.value = inv.maxSlots
        _equippedItems.value = inv.allEquipped()
        _loadoutSettings.value = LoadoutSettingsSnapshot(
            inv.selectedFoodId, inv.selectedPotionId, inv.potionTimerRemainingSeconds,
            inv.autoHealThresholdPercent, inv.autoFleeThresholdPercent, inv.selectedPrayerId
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
            is ActiveQueue.BuryQueue -> {
                val remaining = queue.targetQuantity - queue.quantityCompleted
                ActiveQueueInfo(
                    label = "Burying " + formatItemName(queue.itemId) + " (" + remaining + " left)",
                    secondsPerAction = queue.secondsPerAction,
                    startedAt = queue.startedAt
                )
            }
            else -> null
        }
    }

    fun refreshCurrency() {
        val accountId = _currentAccountId.value ?: return
        val account = accountService.accountById(accountId) ?: return
        _unlockedPresets.value = account.unlockedPresets.toSet()
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val gold = SupabaseMarketRepository.currencyBalance(characterId).getOrNull() ?: 0L
            val gems = SupabaseMarketRepository.gemsBalance(characterId).getOrNull() ?: 0L
            _currency.value = gold to gems
        }
    }

    fun creditPremiumCurrency(bundleId: String) {
        val bundle = CurrencyBundleCatalog.find(bundleId) ?: return
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseMarketRepository.creditGems(characterId, bundle.premiumCurrencyGranted)
            result.onFailure { _premiumActionError.value = it.message ?: it.toString() }
            result.onSuccess {
                _premiumActionError.value = null
                refreshCurrency()
                saveGame()
            }
        }
    }

    fun purchasePreset(presetId: String) {
        val accountId = _currentAccountId.value ?: return
        val characterId = _currentSupabaseCharacterId.value ?: return
        val account = accountService.accountById(accountId) ?: return
        if (presetId in account.unlockedPresets) {
            _premiumActionError.value = "Already unlocked."
            return
        }
        val preset = PremiumPresetCatalog.find(presetId) ?: return
        viewModelScope.launch {
            val spendResult = SupabaseMarketRepository.spendGems(characterId, preset.gemCost)
            spendResult.onFailure { _premiumActionError.value = it.message ?: it.toString() }
            spendResult.onSuccess {
                val result = accountService.unlockPreset(accountId, presetId)
                if (result is ServiceResult.Failure) {
                    _premiumActionError.value = result.reason
                    return@onSuccess
                }
                _premiumActionError.value = null
                refreshCurrency()
                saveGame()
            }
        }
    }

    // Moderator tool - grants Gems to ANY player by their Supabase character
    // id, via the server-authoritative admin_grant_gems RPC (SECURITY
    // DEFINER, independently re-checks caller_is_moderator() server-side,
    // same pattern as muteCharacterAsModerator/unmuteCharacterAsModerator
    // above). Replaces the old self-only grantTestGems, which only touched
    // the local logged-in account's in-memory Account.premiumCurrency and
    // never actually reached other players.
    fun grantGemsAsModerator(characterId: String, amount: Long, reason: String) {
        viewModelScope.launch {
            SupabaseModerationRepository.grantGems(characterId, amount, reason)
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

    private val MAX_OPEN_ORDERS_PER_SIDE = 2

    fun placeBuyOrder(itemId: String, quantity: Int, pricePerUnit: Long) {
        val characterId = _currentCharacterId.value ?: return
        val supabaseCharacterId = _currentSupabaseCharacterId.value ?: return
        if (_myBuyOrders.value.count { it.remainingQuantity > 0 } >= MAX_OPEN_ORDERS_PER_SIDE) {
            _marketActionError.value = "You can only have $MAX_OPEN_ORDERS_PER_SIDE open buy orders at a time."
            return
        }
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
        if (_mySellOrders.value.count { it.remainingQuantity > 0 } >= MAX_OPEN_ORDERS_PER_SIDE) {
            _marketActionError.value = "You can only have $MAX_OPEN_ORDERS_PER_SIDE open sell orders at a time."
            return
        }
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

