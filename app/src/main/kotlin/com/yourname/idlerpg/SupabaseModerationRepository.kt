package com.yourname.idlerpg

import io.github.jan.supabase.postgrest.postgrest
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put

// =========================================================
// RAW ROW SHAPES (mirror the Supabase schema, not the UI)
// =========================================================

@Serializable
private data class MessageReportRow(
    val id: String,
    @SerialName("message_id") val messageId: String,
    @SerialName("reporter_character_id") val reporterCharacterId: String,
    @SerialName("reported_character_id") val reportedCharacterId: String,
    val category: String,
    val reason: String,
    val status: String,
    @SerialName("created_at") val createdAt: String
)

@Serializable
private data class ReportAppealRow(
    val id: String,
    @SerialName("report_id") val reportId: String,
    @SerialName("character_id") val characterId: String,
    @SerialName("appeal_text") val appealText: String,
    val status: String,
    @SerialName("created_at") val createdAt: String,
    @SerialName("reviewed_by") val reviewedBy: String? = null,
    @SerialName("review_notes") val reviewNotes: String? = null
)

@Serializable
private data class ModCharacterNameRow(
    val id: String,
    @SerialName("display_name") val displayName: String
)

@Serializable
private data class ModeratorFlagRow(
    val id: String,
    @SerialName("is_moderator") val isModerator: Boolean
)

// =========================================================
// UI-FACING SHAPES
// =========================================================

data class PendingReportUi(
    val id: String,
    val messageId: String,
    val reporterName: String,
    val reportedName: String,
    val category: String,
    val reason: String,
    val createdAt: String
)

data class PendingAppealUi(
    val id: String,
    val reportId: String,
    val characterName: String,
    val appealText: String,
    val createdAt: String
)

// =========================================================
// REPOSITORY
// Every function is suspend - callers run these inside
// viewModelScope.launch, same pattern as SupabaseChatRepository.
// Every read is best-effort: network failures surface as
// null/empty results rather than crashing.
//
// NOTE: every RPC here is SECURITY DEFINER and independently
// checks caller_is_moderator() server-side. The client-side
// is_moderator gate (wherever this screen is entered from) is
// a UX convenience only - it is not the source of truth.
// =========================================================

object SupabaseModerationRepository {

    private val client get() = SupabaseClientProvider.client

    // ---------------------------------------------------------
    // MODERATOR STATUS CHECK
    // UI-side gate only - every RPC below independently re-checks
    // caller_is_moderator() server-side regardless of this.
    // ---------------------------------------------------------

    suspend fun isCallerModerator(profileId: String): Boolean {
        return try {
            client.postgrest.from("profiles")
                .select { filter { eq("id", profileId) } }
                .decodeSingleOrNull<ModeratorFlagRow>()?.isModerator ?: false
        } catch (e: Exception) {
            false
        }
    }

    // ---------------------------------------------------------
    // REPORTS
    // ---------------------------------------------------------

    suspend fun fetchPendingReports(): List<PendingReportUi> {
        return try {
            val rows = client.postgrest.rpc("list_pending_reports")
                .decodeList<MessageReportRow>()

            if (rows.isEmpty()) return emptyList()

            val characterIds = (rows.map { it.reporterCharacterId } + rows.map { it.reportedCharacterId }).distinct()
            val names = client.postgrest.from("characters")
                .select { filter { isIn("id", characterIds) } }
                .decodeList<ModCharacterNameRow>()
            val nameById = names.associateBy({ it.id }, { it.displayName })

            rows.sortedBy { it.createdAt }.map {
                PendingReportUi(
                    id = it.id,
                    messageId = it.messageId,
                    reporterName = nameById[it.reporterCharacterId] ?: "Unknown",
                    reportedName = nameById[it.reportedCharacterId] ?: "Unknown",
                    category = it.category,
                    reason = it.reason,
                    createdAt = it.createdAt
                )
            }
        } catch (e: Exception) {
            emptyList()
        }
    }

    suspend fun resolveReport(reportId: String, actionTaken: Boolean): Result<Unit> = runCatching {
        client.postgrest.rpc("resolve_report", buildJsonObject {
            put("p_report_id", reportId)
            put("p_action_taken", actionTaken)
        })
    }

    // ---------------------------------------------------------
    // APPEALS
    // ---------------------------------------------------------

    suspend fun fetchPendingAppeals(): List<PendingAppealUi> {
        return try {
            val rows = client.postgrest.rpc("list_pending_appeals")
                .decodeList<ReportAppealRow>()

            if (rows.isEmpty()) return emptyList()

            val characterIds = rows.map { it.characterId }.distinct()
            val names = client.postgrest.from("characters")
                .select { filter { isIn("id", characterIds) } }
                .decodeList<ModCharacterNameRow>()
            val nameById = names.associateBy({ it.id }, { it.displayName })

            rows.sortedBy { it.createdAt }.map {
                PendingAppealUi(
                    id = it.id,
                    reportId = it.reportId,
                    characterName = nameById[it.characterId] ?: "Unknown",
                    appealText = it.appealText,
                    createdAt = it.createdAt
                )
            }
        } catch (e: Exception) {
            emptyList()
        }
    }

    suspend fun resolveAppeal(appealId: String, grant: Boolean, reviewNotes: String): Result<Unit> = runCatching {
        client.postgrest.rpc("resolve_appeal", buildJsonObject {
            put("p_appeal_id", appealId)
            put("p_grant", grant)
            put("p_review_notes", reviewNotes)
        })
    }

    // ---------------------------------------------------------
    // MUTING
    // ---------------------------------------------------------

    suspend fun muteCharacter(characterId: String, durationSeconds: Int, reason: String): Result<Unit> = runCatching {
        client.postgrest.rpc("admin_mute_character", buildJsonObject {
            put("p_character_id", characterId)
            put("p_duration_seconds", durationSeconds)
            put("p_reason", reason)
        })
    }

    suspend fun unmuteCharacter(characterId: String): Result<Unit> = runCatching {
        client.postgrest.rpc("admin_unmute_character", buildJsonObject {
            put("p_character_id", characterId)
        })
    }
}
