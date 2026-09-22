package com.yourname.idlerpg

import com.yourname.idlerpg.ui.components.ChatChannelUi
import com.yourname.idlerpg.ui.components.ChatMessageUi
import com.yourname.idlerpg.ui.components.DmConversationSummary
import io.github.jan.supabase.postgrest.postgrest
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put
import java.time.Instant

// =========================================================
// RAW ROW SHAPES (mirror the Supabase schema, not the UI)
// =========================================================

@Serializable
private data class ChatMessageRow(
    val id: String,
    @SerialName("channel_id") val channelId: String,
    @SerialName("sender_character_id") val senderCharacterId: String,
    val content: String,
    @SerialName("sent_at") val sentAt: String,
    val type: String
)

@Serializable
private data class ChatChannelRow(
    val id: String,
    val type: String,
    @SerialName("guild_id") val guildId: String? = null
)

@Serializable
private data class ChatChannelParticipantRow(
    @SerialName("channel_id") val channelId: String,
    @SerialName("character_id") val characterId: String
)

@Serializable
private data class ChatCharacterNameRow(
    val id: String,
    @SerialName("display_name") val displayName: String
)

@Serializable
private data class ChatPreferenceRow(
    @SerialName("character_id") val characterId: String,
    @SerialName("global_chat_opt_out") val globalChatOptOut: Boolean
)

// =========================================================
// REPOSITORY
// Every function is suspend - callers run these inside
// viewModelScope.launch, same pattern as SupabaseGuildRepository.
// Every read is best-effort: network failures surface as
// null/empty results rather than crashing, since local gameplay
// must never depend on any of this succeeding.
// =========================================================

object SupabaseChatRepository {

    private val client get() = SupabaseClientProvider.client

    private fun ChatChannelUi.toDbType(): String = when (this) {
        ChatChannelUi.GLOBAL -> "GLOBAL"
        ChatChannelUi.GUILD -> "GUILD"
        ChatChannelUi.TRADE -> "TRADE"
        ChatChannelUi.HELP -> "HELP"
        ChatChannelUi.DMS -> "DM"
    }

    // ---------------------------------------------------------
    // CHANNEL LOOKUP
    // GLOBAL/TRADE/HELP are singleton channels seeded by the
    // Phase A migration (guild_id is null). Filtering guild_id
    // client-side rather than via an isNull() filter call, since
    // that filter method's exact name varies by supabase-kt version.
    // ---------------------------------------------------------

    suspend fun fetchSingletonChannelId(channel: ChatChannelUi): String? {
        return try {
            client.postgrest.from("chat_channels")
                .select { filter { eq("type", channel.toDbType()) } }
                .decodeList<ChatChannelRow>()
                .firstOrNull { it.guildId == null }
                ?.id
        } catch (e: Exception) {
            null
        }
    }

    suspend fun getOrCreateGuildChannel(guildId: String): Result<String> = runCatching {
        client.postgrest.rpc("get_or_create_guild_channel", buildJsonObject {
            put("p_guild_id", guildId)
        }).decodeAs<String>()
    }

    suspend fun getOrCreateDmChannel(characterId: String, otherCharacterId: String): Result<String> = runCatching {
        client.postgrest.rpc("get_or_create_dm_channel", buildJsonObject {
            put("p_character_id", characterId)
            put("p_other_character_id", otherCharacterId)
        }).decodeAs<String>()
    }

    // ---------------------------------------------------------
    // MESSAGES
    // ---------------------------------------------------------

    suspend fun fetchChannelMessages(
        viewerCharacterId: String,
        channelId: String,
        channel: ChatChannelUi,
        limit: Int = 50
    ): List<ChatMessageUi> {
        return try {
            val rows = client.postgrest.rpc("get_channel_messages", buildJsonObject {
                put("p_viewer_character_id", viewerCharacterId)
                put("p_channel_id", channelId)
                put("p_limit", limit)
            }).decodeList<ChatMessageRow>()

            if (rows.isEmpty()) return emptyList()

            val senderIds = rows.map { it.senderCharacterId }.distinct()
            val names = client.postgrest.from("characters")
                .select { filter { isIn("id", senderIds) } }
                .decodeList<ChatCharacterNameRow>()
            val nameById = names.associateBy({ it.id }, { it.displayName })

            val cosmeticsBySender = SupabaseCosmeticRepository.fetchEquipped(senderIds)

            rows.sortedBy { it.sentAt }.map {
                ChatMessageUi(
                    id = it.id,
                    senderCharacterId = it.senderCharacterId,
                    senderName = nameById[it.senderCharacterId] ?: "Unknown",
                    content = it.content,
                    channel = channel,
                    senderTitleId = cosmeticsBySender[it.senderCharacterId]?.titleId,
                    senderBadgeId = cosmeticsBySender[it.senderCharacterId]?.badgeId
                )
            }
        } catch (e: Exception) {
            emptyList()
        }
    }

    suspend fun sendMessage(characterId: String, channelId: String, content: String): Result<Unit> = runCatching {
        client.postgrest.rpc("send_chat_message", buildJsonObject {
            put("p_character_id", characterId)
            put("p_channel_id", channelId)
            put("p_content", content)
        })
    }

    // ---------------------------------------------------------
    // REPORTING
    // ---------------------------------------------------------

    suspend fun reportMessage(
        reporterCharacterId: String,
        messageId: String,
        category: String,
        reason: String
    ): Result<Unit> = runCatching {
        client.postgrest.rpc("report_chat_message", buildJsonObject {
            put("p_reporter_character_id", reporterCharacterId)
            put("p_message_id", messageId)
            put("p_category", category)
            put("p_reason", reason)
        })
    }

    // ---------------------------------------------------------
    // BLOCKING
    // ---------------------------------------------------------

    suspend fun blockCharacter(blockerCharacterId: String, blockedCharacterId: String): Result<Unit> = runCatching {
        client.postgrest.from("blocks").insert(
            buildJsonObject {
                put("blocker_character_id", blockerCharacterId)
                put("blocked_character_id", blockedCharacterId)
            }
        )
    }

    // ---------------------------------------------------------
    // SELF-MUTES
    // ---------------------------------------------------------

    suspend fun selfMute(viewerCharacterId: String, targetCharacterId: String): Result<Unit> = runCatching {
        client.postgrest.from("self_mutes").insert(
            buildJsonObject {
                put("viewer_character_id", viewerCharacterId)
                put("target_character_id", targetCharacterId)
            }
        )
    }

    suspend fun selfUnmute(viewerCharacterId: String, targetCharacterId: String): Result<Unit> = runCatching {
        client.postgrest.from("self_mutes").delete {
            filter {
                eq("viewer_character_id", viewerCharacterId)
                eq("target_character_id", targetCharacterId)
            }
        }
    }

    // ---------------------------------------------------------
    // CHAT PREFERENCES (global chat opt-out)
    // ---------------------------------------------------------

    suspend fun getGlobalChatOptOut(characterId: String): Boolean {
        return try {
            client.postgrest.from("chat_preferences")
                .select { filter { eq("character_id", characterId) } }
                .decodeSingleOrNull<ChatPreferenceRow>()?.globalChatOptOut ?: false
        } catch (e: Exception) {
            false
        }
    }

    suspend fun setGlobalChatOptOut(characterId: String, optOut: Boolean): Result<Unit> = runCatching {
        client.postgrest.from("chat_preferences").upsert(
            buildJsonObject {
                put("character_id", characterId)
                put("global_chat_opt_out", optOut)
                put("updated_at", Instant.now().toString())
            }
        )
    }

    // ---------------------------------------------------------
    // DM CONVERSATION LIST
    // ---------------------------------------------------------

    suspend fun fetchDmConversations(characterId: String): List<DmConversationSummary> {
        return try {
            val myParticipation = client.postgrest.from("chat_channel_participants")
                .select { filter { eq("character_id", characterId) } }
                .decodeList<ChatChannelParticipantRow>()
            val myChannelIds = myParticipation.map { it.channelId }
            if (myChannelIds.isEmpty()) return emptyList()

            val dmChannels = client.postgrest.from("chat_channels")
                .select { filter { isIn("id", myChannelIds); eq("type", "DM") } }
                .decodeList<ChatChannelRow>()
            val dmChannelIds = dmChannels.map { it.id }
            if (dmChannelIds.isEmpty()) return emptyList()

            val otherParticipants = client.postgrest.from("chat_channel_participants")
                .select { filter { isIn("channel_id", dmChannelIds) } }
                .decodeList<ChatChannelParticipantRow>()
                .filter { it.characterId != characterId }
            val otherIdByChannel = otherParticipants.associateBy({ it.channelId }, { it.characterId })

            val otherIds = otherIdByChannel.values.distinct()
            val names = if (otherIds.isEmpty()) emptyList() else client.postgrest.from("characters")
                .select { filter { isIn("id", otherIds) } }
                .decodeList<ChatCharacterNameRow>()
            val nameById = names.associateBy({ it.id }, { it.displayName })

            val allMessages = client.postgrest.from("chat_messages")
                .select { filter { isIn("channel_id", dmChannelIds) } }
                .decodeList<ChatMessageRow>()
            val lastMessageByChannel = allMessages.groupBy { it.channelId }
                .mapValues { (_, msgs) -> msgs.maxByOrNull { it.sentAt } }

            dmChannelIds.mapNotNull { channelId ->
                val otherId = otherIdByChannel[channelId] ?: return@mapNotNull null
                DmConversationSummary(
                    characterId = otherId,
                    displayName = nameById[otherId] ?: "Unknown",
                    lastMessagePreview = lastMessageByChannel[channelId]?.content ?: ""
                )
            }
        } catch (e: Exception) {
            emptyList()
        }
    }
}
