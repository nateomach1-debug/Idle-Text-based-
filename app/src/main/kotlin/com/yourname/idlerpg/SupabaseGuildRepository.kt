package com.yourname.idlerpg

import com.yourname.idlerpg.ui.screens.GuildHomeState
import com.yourname.idlerpg.ui.screens.GuildMemberRole
import com.yourname.idlerpg.ui.screens.GuildMemberSummary
import com.yourname.idlerpg.ui.screens.GuildEventSummary
import com.yourname.idlerpg.ui.screens.GuildVoteSummary
import com.yourname.idlerpg.ui.screens.GuildLeaderboardEntry
import io.github.jan.supabase.postgrest.postgrest
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put
import java.time.Duration
import java.time.Instant

// =========================================================
// RAW ROW SHAPES (mirror the Supabase schema, not the UI)
// =========================================================

@Serializable
private data class GuildMemberRow(
    @SerialName("guild_id") val guildId: String,
    @SerialName("character_id") val characterId: String,
    val role: String
)

@Serializable
private data class GuildRow(
    val id: String,
    val name: String,
    val tier: Int,
    @SerialName("last_failed_vote_at") val lastFailedVoteAt: String? = null,
    @SerialName("guild_level") val guildLevel: Int = 1
)

@Serializable
private data class CharacterNameRow(
    val id: String,
    @SerialName("display_name") val displayName: String
)

@Serializable
private data class GuildEventRow(
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
)

@Serializable
private data class GuildVoteRow(
    val id: String,
    @SerialName("target_character_id") val targetCharacterId: String,
    val status: String,
    @SerialName("created_at") val createdAt: String
)

@Serializable
private data class VoteBallotRow(
    @SerialName("vote_id") val voteId: String,
    val supports: Boolean
)

// =========================================================
// REPOSITORY
// Every function is suspend - callers run these inside
// viewModelScope.launch, same pattern as syncSupabaseAuth().
// Every function is best-effort: network failures surface as
// null/empty results rather than crashing, since local gameplay
// must never depend on any of this succeeding.
// =========================================================

data class GuildBrowseEntry(
    val id: String,
    val name: String,
    val tier: Int,
    val memberCount: Int
)

object SupabaseGuildRepository {

    private val client get() = SupabaseClientProvider.client

    // Finds which guild (if any) a character belongs to, and their role in it.
    suspend fun findMembership(characterId: String): Pair<String, GuildMemberRole>? {
        return try {
            val row = client.postgrest.from("guild_members")
                .select { filter { eq("character_id", characterId) } }
                .decodeSingleOrNull<GuildMemberRow>() ?: return null
            row.guildId to GuildMemberRole.valueOf(row.role)
        } catch (e: Exception) {
            null
        }
    }

    suspend fun fetchGuildHome(characterId: String): GuildHomeState? {
        try {
            val (guildId, viewerRole) = findMembership(characterId) ?: return null

            val guild = client.postgrest.from("guilds")
                .select { filter { eq("id", guildId) } }
                .decodeSingleOrNull<GuildRow>() ?: return null

            val memberRows = client.postgrest.from("guild_members")
                .select { filter { eq("guild_id", guildId) } }
                .decodeList<GuildMemberRow>()

            val characterIds = memberRows.map { it.characterId }
            val names = if (characterIds.isEmpty()) emptyList() else client.postgrest.from("characters")
                .select { filter { isIn("id", characterIds) } }
                .decodeList<CharacterNameRow>()
            val nameById = names.associateBy({ it.id }, { it.displayName })

            val members = memberRows.map {
                GuildMemberSummary(
                    characterId = it.characterId,
                    displayName = nameById[it.characterId] ?: "Unknown",
                    role = GuildMemberRole.valueOf(it.role)
                )
            }

            val activeEvent = client.postgrest.from("guild_events")
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
                }

            val openVoteRow = client.postgrest.from("guild_leader_votes")
                .select { filter { eq("guild_id", guildId); eq("status", "OPEN") } }
                .decodeList<GuildVoteRow>()
                .firstOrNull()

            val activeVote = openVoteRow?.let { vote ->
                val ballots = client.postgrest.from("guild_leader_vote_ballots")
                    .select { filter { eq("vote_id", vote.id) } }
                    .decodeList<VoteBallotRow>()
                val removeVotes = ballots.count { !it.supports }
                val keepVotes = ballots.count { it.supports }
                val targetName = nameById[vote.targetCharacterId] ?: "Unknown"
                val closesAt = Instant.parse(vote.createdAt).plus(Duration.ofHours(24))
                val hoursRemaining = Duration.between(Instant.now(), closesAt).toHours().coerceAtLeast(0)
                GuildVoteSummary(
                    targetLeaderName = targetName,
                    hoursRemaining = hoursRemaining.toInt(),
                    removeVotes = removeVotes,
                    keepVotes = keepVotes
                )
            }

            return GuildHomeState(
                guildName = guild.name,
                activeEvent = activeEvent,
                activeVote = activeVote,
                tier = guild.tier,
                guildLevel = guild.guildLevel,
                activeBonusPercent = 0.0,  // Phase 2 adds active bonus tracking
                members = members,
                quests = emptyList(),  // no backend concept for this yet - not fabricating fake data
                viewerRole = viewerRole
            )
        } catch (e: Exception) {
            return null
        }
    }
    
suspend fun blockCharacter(blockerCharacterId: String, blockedCharacterId: String): Result<Unit> = runCatching {
    client.postgrest.from("blocks").insert(
        buildJsonObject {
            put("blocker_character_id", blockerCharacterId)
            put("blocked_character_id", blockedCharacterId)
        }
    )
}
    suspend fun fetchLeaderboard(characterId: String): List<GuildLeaderboardEntry> {
        // Placeholder until Phase 2 adds contribution tracking columns - returns
        // members with a value of 0 rather than fabricating numbers.
        val (guildId, _) = findMembership(characterId) ?: return emptyList()
        return try {
            val memberRows = client.postgrest.from("guild_members")
                .select { filter { eq("guild_id", guildId) } }
                .decodeList<GuildMemberRow>()
            val characterIds = memberRows.map { it.characterId }
            val names = if (characterIds.isEmpty()) emptyList() else client.postgrest.from("characters")
                .select { filter { isIn("id", characterIds) } }
                .decodeList<CharacterNameRow>()
            names.map { GuildLeaderboardEntry(displayName = it.displayName, value = 0L) }
        } catch (e: Exception) {
            emptyList()
        }
    }

    // ---------------------------------------------------------
    // RPC ACTIONS - each mirrors a SECURITY DEFINER function from
    // guild_core_phase1.sql. Server enforces every rule; these are
    // thin wrappers, not a second copy of the business logic.
    // ---------------------------------------------------------

    suspend fun createGuild(name: String, founderCharacterId: String): Result<Unit> = runCatching {
        client.postgrest.rpc("create_guild", buildJsonObject {
            put("p_name", name)
            put("p_founder_character_id", founderCharacterId)
        })
    }

    suspend fun inviteMember(guildId: String, invitingCharacterId: String, invitedCharacterId: String): Result<Unit> = runCatching {
        client.postgrest.rpc("invite_member", buildJsonObject {
            put("p_guild_id", guildId)
            put("p_inviting_character_id", invitingCharacterId)
            put("p_invited_character_id", invitedCharacterId)
        })
    }

    suspend fun kickMember(guildId: String, actingCharacterId: String, targetCharacterId: String): Result<Unit> = runCatching {
        client.postgrest.rpc("kick_member", buildJsonObject {
            put("p_guild_id", guildId)
            put("p_acting_character_id", actingCharacterId)
            put("p_target_character_id", targetCharacterId)
        })
    }

    suspend fun promoteToOfficer(guildId: String, actingCharacterId: String, targetCharacterId: String): Result<Unit> = runCatching {
        client.postgrest.rpc("promote_to_officer", buildJsonObject {
            put("p_guild_id", guildId)
            put("p_acting_character_id", actingCharacterId)
            put("p_target_character_id", targetCharacterId)
        })
    }

    suspend fun promoteToLeader(guildId: String, actingCharacterId: String, targetCharacterId: String): Result<Unit> = runCatching {
        client.postgrest.rpc("promote_to_leader", buildJsonObject {
            put("p_guild_id", guildId)
            put("p_acting_character_id", actingCharacterId)
            put("p_target_character_id", targetCharacterId)
        })
    }

    suspend fun disbandGuild(guildId: String, actingCharacterId: String): Result<Unit> = runCatching {
        client.postgrest.rpc("disband_guild", buildJsonObject {
            put("p_guild_id", guildId)
            put("p_acting_character_id", actingCharacterId)
        })
    }

    // Lists every guild so a character with no guild yet can browse and self-join.
    suspend fun listGuilds(): List<GuildBrowseEntry> {
        return try {
            val guildRows = client.postgrest.from("guilds").select().decodeList<GuildRow>()
            val memberRows = client.postgrest.from("guild_members").select().decodeList<GuildMemberRow>()
            val countByGuild = memberRows.groupingBy { it.guildId }.eachCount()
            guildRows.map { GuildBrowseEntry(it.id, it.name, it.tier, countByGuild[it.id] ?: 0) }
        } catch (e: Exception) {
            emptyList()
        }
    }

    suspend fun joinGuild(guildId: String, characterId: String): Result<Unit> = runCatching {
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
)
