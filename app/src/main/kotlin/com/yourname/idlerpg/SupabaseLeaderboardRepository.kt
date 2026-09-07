package com.yourname.idlerpg

import io.github.jan.supabase.postgrest.postgrest
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put

@Serializable
data class SkillLeaderboardEntry(
    val characterId: String,
    val displayName: String,
    val level: Int,
    val xp: Long
)

@Serializable
data class TotalLevelLeaderboardEntry(
    val characterId: String,
    val displayName: String,
    val totalLevel: Long,
    val totalXp: Long
)

@Serializable
data class CombatLevelLeaderboardEntry(
    val characterId: String,
    val displayName: String,
    val combatLevel: Long
)

@Serializable
data class GuildLeaderboardStandingEntry(
    val guildId: String,
    val guildName: String,
    val guildLevel: Int,
    val guildCoins: Long
)

object SupabaseLeaderboardRepository {

    private val client get() = SupabaseClientProvider.client

    suspend fun fetchSkillLeaderboard(skillType: String, limit: Int = 50): Result<List<SkillLeaderboardEntry>> = runCatching {
        client.postgrest.rpc("fetch_skill_leaderboard", buildJsonObject {
            put("p_skill_type", skillType)
            put("p_limit", limit)
        }).decodeList<SkillLeaderboardEntry>()
    }

    suspend fun fetchTotalLevelLeaderboard(limit: Int = 50): Result<List<TotalLevelLeaderboardEntry>> = runCatching {
        client.postgrest.rpc("fetch_total_level_leaderboard", buildJsonObject {
            put("p_limit", limit)
        }).decodeList<TotalLevelLeaderboardEntry>()
    }

    suspend fun fetchCombatLevelLeaderboard(limit: Int = 50): Result<List<CombatLevelLeaderboardEntry>> = runCatching {
        client.postgrest.rpc("fetch_combat_level_leaderboard", buildJsonObject {
            put("p_limit", limit)
        }).decodeList<CombatLevelLeaderboardEntry>()
    }

    suspend fun fetchGuildLeaderboard(limit: Int = 50): Result<List<GuildLeaderboardStandingEntry>> = runCatching {
        client.postgrest.rpc("fetch_guild_leaderboard", buildJsonObject {
            put("p_limit", limit)
        }).decodeList<GuildLeaderboardStandingEntry>()
    }
}
