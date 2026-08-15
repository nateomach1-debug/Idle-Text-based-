path = "app/src/main/kotlin/com/yourname/idlerpg/SupabaseGuildRepository.kt"
with open(path, "r") as f:
    content = f.read()

# --- 1. Add the public GuildBrowseEntry type right before the repository object. ---
old_anchor = "object SupabaseGuildRepository {"
new_anchor = '''data class GuildBrowseEntry(
    val id: String,
    val name: String,
    val tier: Int,
    val memberCount: Int
)

object SupabaseGuildRepository {'''
assert content.count(old_anchor) == 1, "repository object anchor not found or not unique"
content = content.replace(old_anchor, new_anchor, 1)

# --- 2. Add listGuilds()/joinGuild() right before the final closing brace of the object. ---
old_end = '''    suspend fun disbandGuild(guildId: String, actingCharacterId: String): Result<Unit> = runCatching {
        client.postgrest.rpc("disband_guild", buildJsonObject {
            put("p_guild_id", guildId)
            put("p_acting_character_id", actingCharacterId)
        })
    }
}'''
new_end = '''    suspend fun disbandGuild(guildId: String, actingCharacterId: String): Result<Unit> = runCatching {
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
}'''
assert content.count(old_end) == 1, "end-of-object anchor not found or not unique"
content = content.replace(old_end, new_end, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: SupabaseGuildRepository.kt patched (GuildBrowseEntry + listGuilds()/joinGuild() added).")
