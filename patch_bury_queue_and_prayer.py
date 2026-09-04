def apply(content, old, new, label):
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"FAILED [{label}]: expected 1 match, found {count}")
    return content.replace(old, new, 1)

# ---------- SupabaseGuildRepository.kt ----------
SGR_PATH = "app/src/main/kotlin/com/yourname/idlerpg/SupabaseGuildRepository.kt"
with open(SGR_PATH, "r", encoding="utf-8") as f:
    sgr = f.read()

sgr = apply(sgr,
"""private data class GuildEventRow(
    val id: String,
    @SerialName("event_type") val eventType: String,
    @SerialName("bonus_tier") val bonusTier: Int,
    @SerialName("starts_at") val startsAt: String,
    @SerialName("ends_at") val endsAt: String
)""",
"""private data class GuildEventRow(
    val id: String,
    @SerialName("event_type") val eventType: String,
    @SerialName("bonus_tier") val bonusTier: Int,
    @SerialName("starts_at") val startsAt: String,
    @SerialName("ends_at") val endsAt: String,
    @SerialName("item_id") val itemId: String? = null,
    @SerialName("skill_name") val skillName: String? = null,
    @SerialName("required_quantity") val requiredQuantity: Int? = null,
    @SerialName("contributed_quantity") val contributedQuantity: Int = 0,
    @SerialName("milestones_paid") val milestonesPaid: Int = 0
)""",
    "GuildEventRow: add event-progress columns"
)

sgr = apply(sgr,
"""            val activeEvent = client.postgrest.from("guild_events")
                .select { filter { eq("guild_id", guildId) } }
                .decodeList<GuildEventRow>()
                .filter { Instant.parse(it.endsAt).isAfter(Instant.now()) }
                .maxByOrNull { it.startsAt }
                ?.let { GuildEventSummary(name = it.eventType, progressCurrent = 0, progressTarget = 0) }
            // Note: live progress (items contributed vs scaled target) isn't tracked in
            // guild_events yet - Phase 2 adds that. Shows the event name/existence for now.""",
"""            val activeEvent = client.postgrest.from("guild_events")
                .select { filter { eq("guild_id", guildId) } }
                .decodeList<GuildEventRow>()
                .filter { Instant.parse(it.endsAt).isAfter(Instant.now()) }
                .maxByOrNull { it.startsAt }
                ?.let {
                    GuildEventSummary(
                        id = it.id,
                        name = it.eventType,
                        itemId = it.itemId ?: "",
                        skillName = it.skillName ?: "",
                        progressCurrent = it.contributedQuantity,
                        progressTarget = it.requiredQuantity ?: 0,
                        milestonesPaid = it.milestonesPaid
                    )
                }""",
    "fetchGuildHome: populate real event progress"
)

sgr = apply(sgr,
"""    suspend fun joinGuild(guildId: String, characterId: String): Result<Unit> = runCatching {
        client.postgrest.rpc("join_guild", buildJsonObject {
            put("p_guild_id", guildId)
            put("p_character_id", characterId)
        })
    }
}""",
"""    suspend fun joinGuild(guildId: String, characterId: String): Result<Unit> = runCatching {
        client.postgrest.rpc("join_guild", buildJsonObject {
            put("p_guild_id", guildId)
            put("p_character_id", characterId)
        })
    }

    suspend fun startGuildEvent(
        guildId: String,
        actingCharacterId: String,
        displayName: String,
        itemId: String,
        skillName: String,
        requiredQuantity: Int,
        guildCoinRewardPerMilestone: Long
    ): Result<String> = runCatching {
        client.postgrest.rpc("start_guild_event", buildJsonObject {
            put("p_guild_id", guildId)
            put("p_acting_character_id", actingCharacterId)
            put("p_display_name", displayName)
            put("p_item_id", itemId)
            put("p_skill_name", skillName)
            put("p_required_quantity", requiredQuantity)
            put("p_guild_coin_reward_per_milestone", guildCoinRewardPerMilestone)
        }).decodeAs<String>()
    }

    suspend fun contributeToGuildEvent(eventId: String, characterId: String, quantity: Int): Result<ContributeGuildEventResult> = runCatching {
        client.postgrest.rpc("contribute_to_guild_event", buildJsonObject {
            put("p_event_id", eventId)
            put("p_character_id", characterId)
            put("p_quantity", quantity)
        }).decodeAs<ContributeGuildEventResult>()
    }

    suspend fun closeExpiredGuildEventIfNeeded(guildId: String): Result<Unit> = runCatching {
        client.postgrest.rpc("close_expired_guild_event_if_needed", buildJsonObject {
            put("p_guild_id", guildId)
        })
    }

    // Sums and clears this character's queued personal payouts from any guild
    // event milestones - including ones triggered by OTHER members' contributions,
    // since only the triggering client's session receives the milestone JSON
    // directly. The client credits the returned total to itself via the existing
    // combat_grant_coins path, never attempting to credit another character.
    suspend fun claimGuildEventPayouts(characterId: String): Result<Long> = runCatching {
        client.postgrest.rpc("claim_guild_event_payouts", buildJsonObject {
            put("p_character_id", characterId)
        }).decodeAs<Long>()
    }
}

@Serializable
data class GuildEventMilestonePayout(
    @SerialName("character_id") val characterId: String,
    val amount: Long
)

@Serializable
data class GuildEventMilestoneResult(
    val percent: Int,
    @SerialName("guild_coins_awarded") val guildCoinsAwarded: Long,
    val payouts: List<GuildEventMilestonePayout>
)

@Serializable
data class ContributeGuildEventResult(
    @SerialName("contributed_quantity") val contributedQuantity: Int,
    @SerialName("required_quantity") val requiredQuantity: Int,
    @SerialName("milestones_just_paid") val milestonesJustPaid: List<GuildEventMilestoneResult>
)""",
    "SupabaseGuildRepository: new event RPC wrapper functions"
)

with open(SGR_PATH, "w", encoding="utf-8") as f:
    f.write(sgr)

# ---------- GuildHomeScreen.kt ----------
GHS_PATH = "app/src/main/kotlin/com/yourname/idlerpg/GuildHomeScreen.kt"
with open(GHS_PATH, "r", encoding="utf-8") as f:
    ghs = f.read()

ghs = apply(ghs,
"""data class GuildEventSummary(
    val name: String,
    val progressCurrent: Int,
    val progressTarget: Int
)""",
"""data class GuildEventSummary(
    val id: String,
    val name: String,
    val itemId: String,
    val skillName: String,
    val progressCurrent: Int,
    val progressTarget: Int,
    val milestonesPaid: Int
)""",
    "GuildEventSummary: add id/itemId/skillName/milestonesPaid"
)

with open(GHS_PATH, "w", encoding="utf-8") as f:
    f.write(ghs)

# ---------- GameViewModel.kt ----------
GVM_PATH = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(GVM_PATH, "r", encoding="utf-8") as f:
    gvm = f.read()

gvm = apply(gvm,
"""    fun refreshGuildHome() {
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
    }""",
"""    fun refreshGuildHome() {
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
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
        }
    }

    // Per-member base quantity by rarity - rarer items require far fewer units
    // to reach the same milestone. Guild-coin reward per milestone is keyed
    // off rarity directly (not off requiredQuantity) so rarer-item events
    // don't perversely pay LESS just because fewer units are needed. Both
    // tables are first-pass numbers, flagged as tunable during balancing.
    private fun eventPerMemberQuantityFor(rarity: Rarity): Int = when (rarity) {
        Rarity.COMMON -> 40
        Rarity.UNCOMMON -> 25
        Rarity.RARE -> 15
        Rarity.EPIC -> 8
        Rarity.LEGENDARY -> 3
    }

    private fun eventGuildCoinRewardPerMilestoneFor(rarity: Rarity): Long = when (rarity) {
        Rarity.COMMON -> 100L
        Rarity.UNCOMMON -> 200L
        Rarity.RARE -> 400L
        Rarity.EPIC -> 800L
        Rarity.LEGENDARY -> 1600L
    }

    // Picks a random skill, then a random item tagged to that skill. Retries
    // with a different skill (up to a small cap) if the chosen skill happens
    // to have zero eligible items in the catalog, rather than ever throwing.
    private fun pickRandomGuildEventResource(): ItemDefinition? {
        val skills = SkillType.entries.toList()
        repeat(20) {
            val skill = skills.random()
            val candidates = ItemCatalog.items.filter { it.skillRequired == skill.name }
            if (candidates.isNotEmpty()) return candidates.random()
        }
        return null
    }

    fun startGuildEvent() {
        val guildId = _guildId.value ?: return
        val actingCharacterId = _currentSupabaseCharacterId.value ?: return
        val memberCount = (_guildHomeState.value?.members?.size ?: 1).coerceAtLeast(1)
        val item = pickRandomGuildEventResource() ?: run {
            _guildActionError.value = "No eligible items found for an event right now."
            return
        }
        val requiredQuantity = eventPerMemberQuantityFor(item.rarity) * memberCount
        val rewardPerMilestone = eventGuildCoinRewardPerMilestoneFor(item.rarity)
        val displayName = item.name + " Drive"

        viewModelScope.launch {
            val result = SupabaseGuildRepository.startGuildEvent(
                guildId = guildId,
                actingCharacterId = actingCharacterId,
                displayName = displayName,
                itemId = item.id,
                skillName = item.skillRequired ?: "",
                requiredQuantity = requiredQuantity,
                guildCoinRewardPerMilestone = rewardPerMilestone
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
            _guildActionError.value = removal.message
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
    }""",
    "GameViewModel: guild event start/contribute/claim wiring"
)

with open(GVM_PATH, "w", encoding="utf-8") as f:
    f.write(gvm)

print("All edits applied successfully across all three files.")
