package com.yourname.idlerpg

import io.github.jan.supabase.postgrest.postgrest
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonElement
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

    // Lets the caller detect a local_character_id mismatch after
    // getOrCreateCharacter - a mismatch means an EXISTING character (from a
    // different device/install) was returned, not a fresh one.
    suspend fun getCharacterLocalId(characterId: String): Result<String?> = runCatching {
        client.postgrest.rpc("get_character_local_id", buildJsonObject {
            put("p_character_id", characterId)
        }).decodeAs<String?>()
    }

    // Uploads the local save JSON as-is (round-tripped through kotlinx's
    // JSON parser since org.json and kotlinx.serialization are different
    // libraries in this codebase) as this character's cloud backup.
    suspend fun uploadCharacterSave(characterId: String, saveJson: String): Result<Unit> = runCatching {
        val parsed: JsonElement = Json.parseToJsonElement(saveJson)
        client.postgrest.rpc("upload_character_save", buildJsonObject {
            put("p_character_id", characterId)
            put("p_save_data", parsed)
        })
        Unit
    }

    // Downloads this character's cloud backup, returned as the same raw
    // JSON string shape GameStateRepository already reads/writes locally.
    suspend fun downloadCharacterSave(characterId: String): Result<String?> = runCatching {
        val result = client.postgrest.rpc("download_character_save", buildJsonObject {
            put("p_character_id", characterId)
        }).decodeAs<JsonElement?>()
        result?.toString()
    }
}
