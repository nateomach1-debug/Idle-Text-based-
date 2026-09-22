package com.yourname.idlerpg

import io.github.jan.supabase.postgrest.postgrest
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put

// =========================================================
// SERVER ACCESS FOR CHAT COSMETICS (titles + badges) AND
// PER-MONSTER KILL COUNTS
// Ownership, equipped state and kill totals live in Supabase so
// other players see the same title/badge and so kills survive
// device changes. Gem purchases go through purchase_cosmetic,
// which spends via the server-authoritative spend_gems RPC in the
// same transaction. Every call is best-effort: failures surface as
// Result.failure / empty maps, never crashes, since local
// gameplay must never depend on any of this succeeding.
// =========================================================

@Serializable
private data class EquippedCosmeticRow(
    @SerialName("character_id") val characterId: String,
    @SerialName("equipped_title_id") val equippedTitleId: String? = null,
    @SerialName("equipped_badge_id") val equippedBadgeId: String? = null
)

data class EquippedCosmetics(val titleId: String?, val badgeId: String?)

object SupabaseCosmeticRepository {

    private val client get() = SupabaseClientProvider.client

    // Equipped title/badge for a set of characters (used to decorate chat lines).
    suspend fun fetchEquipped(characterIds: List<String>): Map<String, EquippedCosmetics> {
        if (characterIds.isEmpty()) return emptyMap()
        return try {
            client.postgrest.from("character_cosmetics")
                .select { filter { isIn("character_id", characterIds) } }
                .decodeList<EquippedCosmeticRow>()
                .associateBy({ it.characterId }, { EquippedCosmetics(it.equippedTitleId, it.equippedBadgeId) })
        } catch (e: Exception) {
            emptyMap()
        }
    }

    suspend fun myCosmetics(characterId: String): Result<List<String>> = runCatching {
        client.postgrest.rpc("my_cosmetics", buildJsonObject {
            put("p_character_id", characterId)
        }).decodeAs<List<String>>()
    }

    suspend fun monsterKills(characterId: String): Result<Map<String, Long>> = runCatching {
        client.postgrest.rpc("get_monster_kills", buildJsonObject {
            put("p_character_id", characterId)
        }).decodeAs<Map<String, Long>>()
    }

    suspend fun recordKills(characterId: String, kills: Map<String, Int>): Result<Unit> = runCatching {
        client.postgrest.rpc("record_monster_kills", buildJsonObject {
            put("p_character_id", characterId)
            put("p_kills", buildJsonObject {
                kills.forEach { (monsterId, count) -> put(monsterId, count) }
            })
        })
        Unit
    }

    suspend fun purchaseCosmetic(characterId: String, cosmeticId: String): Result<Long> = runCatching {
        client.postgrest.rpc("purchase_cosmetic", buildJsonObject {
            put("p_character_id", characterId)
            put("p_cosmetic_id", cosmeticId)
        }).decodeAs<Long>()
    }

    suspend fun claimEarnedTitle(characterId: String, cosmeticId: String): Result<Unit> = runCatching {
        client.postgrest.rpc("claim_earned_title", buildJsonObject {
            put("p_character_id", characterId)
            put("p_cosmetic_id", cosmeticId)
        })
        Unit
    }

    suspend fun setEquipped(characterId: String, titleId: String?, badgeId: String?): Result<Unit> = runCatching {
        client.postgrest.rpc("set_equipped_cosmetics", buildJsonObject {
            put("p_character_id", characterId)
            put("p_title_id", titleId)
            put("p_badge_id", badgeId)
        })
        Unit
    }
}
