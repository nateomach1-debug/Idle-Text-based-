def apply(content, old, new, label):
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"FAILED [{label}]: expected 1 match, found {count}")
    return content.replace(old, new, 1)

# ---------- SupabaseCharacterRepository.kt ----------
SCR_PATH = "app/src/main/kotlin/com/yourname/idlerpg/SupabaseCharacterRepository.kt"
with open(SCR_PATH, "r", encoding="utf-8") as f:
    scr = f.read()

scr = apply(scr,
"""    // Downloads this character's cloud backup, returned as the same raw
    // JSON string shape GameStateRepository already reads/writes locally.
    suspend fun downloadCharacterSave(characterId: String): Result<String?> = runCatching {
        val result = client.postgrest.rpc("download_character_save", buildJsonObject {
            put("p_character_id", characterId)
        }).decodeAs<JsonElement?>()
        result?.toString()
    }
}""",
"""    // Downloads this character's cloud backup, returned as the same raw
    // JSON string shape GameStateRepository already reads/writes locally.
    suspend fun downloadCharacterSave(characterId: String): Result<String?> = runCatching {
        val result = client.postgrest.rpc("download_character_save", buildJsonObject {
            put("p_character_id", characterId)
        }).decodeAs<JsonElement?>()
        result?.toString()
    }

    // Reports a full skill snapshot for the leaderboards feature. Piggybacks
    // on the same call site as uploadCharacterSave - no separate sync cadence.
    suspend fun reportSkillLevels(characterId: String, skills: List<Skill>): Result<Unit> = runCatching {
        val payload = kotlinx.serialization.json.JsonArray(skills.map { skill ->
            buildJsonObject {
                put("skill_type", skill.type.name)
                put("level", LevelCurve.levelForXp(skill.xp))
                put("xp", skill.xp)
            }
        })
        client.postgrest.rpc("report_skill_levels", buildJsonObject {
            put("p_character_id", characterId)
            put("p_levels", payload)
        })
        Unit
    }
}""",
    "add reportSkillLevels"
)

with open(SCR_PATH, "w", encoding="utf-8") as f:
    f.write(scr)

# ---------- GameViewModel.kt ----------
GVM_PATH = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(GVM_PATH, "r", encoding="utf-8") as f:
    gvm = f.read()

gvm = apply(gvm,
"""        val supabaseCharacterId = _currentSupabaseCharacterId.value
        val json = repository.currentSaveJson()
        if (supabaseCharacterId != null && json != null) {
            viewModelScope.launch {
                SupabaseCharacterRepository.uploadCharacterSave(supabaseCharacterId, json)
            }
        }
    }

    fun selectCharacter(characterId: String) {""",
"""        val supabaseCharacterId = _currentSupabaseCharacterId.value
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

    fun selectCharacter(characterId: String) {""",
    "saveGame: report skill levels alongside cloud save upload"
)

with open(GVM_PATH, "w", encoding="utf-8") as f:
    f.write(gvm)

# ---------- SupabaseLeaderboardRepository.kt (new file) ----------
SLR_PATH = "app/src/main/kotlin/com/yourname/idlerpg/SupabaseLeaderboardRepository.kt"
slr_content = """package com.yourname.idlerpg

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
"""
with open(SLR_PATH, "w", encoding="utf-8") as f:
    f.write(slr_content)

print("All edits applied successfully, including new SupabaseLeaderboardRepository.kt.")
