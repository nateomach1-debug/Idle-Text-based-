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

// NOTE: adjust the ui.components import paths above if ChatChannelUi /
// ChatMessageUi / DmConversationSummary actually live somewhere else -
// chat_dump_4.txt showed them in a file found via grep, not a confirmed
// package declaration.

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
private data class CharacterNameRow(
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
    // Phase A migration (guild_id is null). GUILD and DM channels
    // are looked up/created via the RPC functions below.
    // ---------------------------------------------------------

    suspend fun fetchSingletonChannelId(channel: ChatChannelUi): String? {
        return try {
            client.postgrest.from("chat_channels")
                .select {
                    filter {
                        eq("type", channel.toDbType())
                        isNull("guild_id")
                    }
                }
                .decodeSingleOrNull<ChatChannelRow>()?.id
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
                .decodeList<CharacterNameRow>()
            val nameById = names.associateBy({ it.id }, { it.displayName })

            rows.sortedBy { it.sentAt }.map {
                ChatMessageUi(
                    id = it.id,
                    senderName = nameById[it.senderCharacterId] ?: "Unknown",
                    content = it.content,
                    channel = channel
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
    // p_category must be one of: HARASSMENT, SPAM, HATE_SPEECH,
    // SCAM_ATTEMPT, OTHER (report_category enum).
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
    // SELF-MUTES
    // Direct table access - RLS on self_mutes already enforces
    // that viewer_character_id belongs to the caller.
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
    // Direct table access - RLS on chat_preferences already
    // enforces that character_id belongs to the caller.
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
    // Finds every DM channel this character participates in,
    // the other participant in each, and a preview of the most
    // recent message.
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
                .decodeList<CharacterNameRow>()
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
