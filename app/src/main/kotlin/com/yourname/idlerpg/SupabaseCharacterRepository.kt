package com.yourname.idlerpg

import io.github.jan.supabase.postgrest.postgrest
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put

// Bridges a local Room-database character (local_character_id) to its
// matching Supabase characters row (a separate, real uuid). Every
// chat/guild RPC call needs the Supabase uuid, not the local id -
// they are different ID schemes entirely.
object SupabaseCharacterRepository {

    private val client get() = SupabaseClientProvider.client

    suspend fun getOrCreateCharacter(localCharacterId: String, displayName: String): Result<String> = runCatching {
        client.postgrest.rpc("get_or_create_character", buildJsonObject {
            put("p_local_character_id", localCharacterId)
            put("p_display_name", displayName)
        }).decodeAs<String>()
    }
}
