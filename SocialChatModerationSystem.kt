import java.time.Duration
import java.time.Instant
import java.util.UUID

// =========================================================
// CHANNELS
// =========================================================

enum class ChatChannel { GLOBAL, GUILD, TRADE, HELP, DIRECT_MESSAGE }

enum class MessageType { NORMAL, SYSTEM_ANNOUNCEMENT, MODERATOR_ACTION }

// =========================================================
// MESSAGES
// =========================================================

data class ChatMessage(
    val id: String = UUID.randomUUID().toString(),
    val senderCharacterId: String,
    val channel: ChatChannel,
    val content: String,
    val type: MessageType = MessageType.NORMAL,
    val sentAt: Instant = Instant.now(),
    val guildId: String? = null,
    val recipientCharacterId: String? = null
)

// =========================================================
// PROFANITY FILTER
// =========================================================

object ProfanityFilter {
    private val bannedWords = setOf("badword1", "badword2")

    fun containsBannedContent(text: String): Boolean {
        val normalized = text.lowercase()
        return bannedWords.any { normalized.contains(it) }
    }
}

// =========================================================
// REPORTS
// =========================================================

enum class ReportCategory { HARASSMENT, SPAM, HATE_SPEECH, SCAM_ATTEMPT, OTHER }
enum class ReportStatus { PENDING, REVIEWED_ACTION_TAKEN, REVIEWED_NO_ACTION }

data class MessageReport(
    val id: String = UUID.randomUUID().toString(),
    val messageId: String,
    val reporterCharacterId: String,
    val reportedCharacterId: String,
    val category: ReportCategory,
    val reasoning: String,
    val createdAt: Instant = Instant.now(),
    var status: ReportStatus = ReportStatus.PENDING
)

// =========================================================
// MUTING
// =========================================================

class SelfMuteList {
    private val mutedByViewer: MutableMap<String, MutableSet<String>> = mutableMapOf()

    fun mute(viewerCharacterId: String, targetCharacterId: String) {
        mutedByViewer.getOrPut(viewerCharacterId) { mutableSetOf() }.add(targetCharacterId)
    }

    fun unmute(viewerCharacterId: String, targetCharacterId: String) {
        mutedByViewer[viewerCharacterId]?.remove(targetCharacterId)
    }

    fun isMuted(viewerCharacterId: String, targetCharacterId: String): Boolean =
        mutedByViewer[viewerCharacterId]?.contains(targetCharacterId) == true
}

data class AdminMuteRecord(
    val characterId: String,
    val mutedUntil: Instant,
    val reason: String,
    val issuedBy: String
) {
    fun isActive(now: Instant = Instant.now()): Boolean = now.isBefore(mutedUntil)
}

// =========================================================
// APPEALS
// =========================================================

enum class AppealStatus { PENDING, GRANTED, DENIED }

data class Appeal(
    val id: String = UUID.randomUUID().toString(),
    val characterId: String,
    val relatedMuteReason: String,
    val appealText: String,
    val submittedAt: Instant = Instant.now(),
    var status: AppealStatus = AppealStatus.PENDING,
    var reviewedBy: String? = null,
    var reviewNotes: String? = null
)

// =========================================================
// FRIENDS & BLOCKING
// =========================================================

enum class FriendRequestStatus { PENDING, ACCEPTED, DECLINED }

data class FriendRequest(
    val id: String = UUID.randomUUID().toString(),
    val fromCharacterId: String,
    val toCharacterId: String,
    var status: FriendRequestStatus = FriendRequestStatus.PENDING
)

class SocialGraph {
    private val friendRequests: MutableList<FriendRequest> = mutableListOf()
    private val friendships: MutableMap<String, MutableSet<String>> = mutableMapOf()
    private val blocks: MutableMap<String, MutableSet<String>> = mutableMapOf()

    fun sendFriendRequest(fromCharacterId: String, toCharacterId: String): ServiceResult<FriendRequest> {
        if (fromCharacterId == toCharacterId) return ServiceResult.Failure("Cannot friend yourself.")
        if (areFriends(fromCharacterId, toCharacterId)) return ServiceResult.Failure("Already friends.")
        if (isBlocked(toCharacterId, fromCharacterId)) return ServiceResult.Failure("Cannot send a request to this player.")

        val existing = friendRequests.find {
            it.fromCharacterId == fromCharacterId && it.toCharacterId == toCharacterId && it.status == FriendRequestStatus.PENDING
        }
        if (existing != null) return ServiceResult.Failure("Request already pending.")

        val request = FriendRequest(fromCharacterId = fromCharacterId, toCharacterId = toCharacterId)
        friendRequests.add(request)
        return ServiceResult.Success(request)
    }

    fun respondToFriendRequest(requestId: String, accept: Boolean): ServiceResult<FriendRequest> {
        val request = friendRequests.find { it.id == requestId } ?: return ServiceResult.Failure("Request not found.")
        if (request.status != FriendRequestStatus.PENDING) return ServiceResult.Failure("Request already resolved.")

        request.status = if (accept) FriendRequestStatus.ACCEPTED else FriendRequestStatus.DECLINED
        if (accept) {
            friendships.getOrPut(request.fromCharacterId) { mutableSetOf() }.add(request.toCharacterId)
            friendships.getOrPut(request.toCharacterId) { mutableSetOf() }.add(request.fromCharacterId)
        }
        return ServiceResult.Success(request)
    }

    fun areFriends(characterIdA: String, characterIdB: String): Boolean =
        friendships[characterIdA]?.contains(characterIdB) == true

    fun blockPlayer(blockerCharacterId: String, targetCharacterId: String) {
        blocks.getOrPut(blockerCharacterId) { mutableSetOf() }.add(targetCharacterId)
    }

    fun unblockPlayer(blockerCharacterId: String, targetCharacterId: String) {
        blocks[blockerCharacterId]?.remove(targetCharacterId)
    }

    fun isBlocked(blockerCharacterId: String, targetCharacterId: String): Boolean =
        blocks[blockerCharacterId]?.contains(targetCharacterId) == true
}

// =========================================================
// PLAYER PROFILE
// =========================================================

data class PlayerProfile(
    val characterId: String,
    val level: Int,
    val guildName: String?,
    val joinDate: Instant
)

// =========================================================
// CHAT & MODERATION SERVICE
// (ServiceResult now comes from SharedTypes.kt.)
// =========================================================

class ChatModerationService {
    private val messages: MutableList<ChatMessage> = mutableListOf()
    private val globalChatOptOut: MutableSet<String> = mutableSetOf()
    private val selfMutes = SelfMuteList()
    private val adminMutes: MutableMap<String, AdminMuteRecord> = mutableMapOf()
    private val reports: MutableList<MessageReport> = mutableListOf()
    private val reporterHiddenMessages: MutableMap<String, MutableSet<String>> = mutableMapOf()
    private val appeals: MutableList<Appeal> = mutableListOf()
    val socialGraph = SocialGraph()

    fun sendMessage(
        senderCharacterId: String,
        channel: ChatChannel,
        content: String,
        guildId: String? = null,
        recipientCharacterId: String? = null
    ): ServiceResult<ChatMessage> {
        adminMutes[senderCharacterId]?.let {
            if (it.isActive()) {
                return ServiceResult.Failure("You are muted until " + it.mutedUntil + ". Reason: " + it.reason)
            }
        }

        if (content.isBlank()) return ServiceResult.Failure("Message cannot be empty.")
        if (ProfanityFilter.containsBannedContent(content)) {
            return ServiceResult.Failure("Message blocked: contains disallowed content.")
        }
        if (channel == ChatChannel.GUILD && guildId == null) {
            return ServiceResult.Failure("Guild channel messages require a guildId.")
        }
        if (channel == ChatChannel.DIRECT_MESSAGE) {
            if (recipientCharacterId == null) return ServiceResult.Failure("Direct messages require a recipient.")
            if (socialGraph.isBlocked(recipientCharacterId, senderCharacterId)) {
                return ServiceResult.Failure("Cannot message this player.")
            }
        }

        val message = ChatMessage(
            senderCharacterId = senderCharacterId,
            channel = channel,
            content = content,
            guildId = guildId,
            recipientCharacterId = recipientCharacterId
        )
        messages.add(message)
        return ServiceResult.Success(message)
    }

    fun sendSystemAnnouncement(content: String, channel: ChatChannel = ChatChannel.GLOBAL): ChatMessage {
        val message = ChatMessage(
            senderCharacterId = "SYSTEM",
            channel = channel,
            content = content,
            type = MessageType.SYSTEM_ANNOUNCEMENT
        )
        messages.add(message)
        return message
    }

    fun visibleMessagesFor(viewerCharacterId: String, channel: ChatChannel, guildId: String? = null): List<ChatMessage> {
        if (channel == ChatChannel.GLOBAL && globalChatOptOut.contains(viewerCharacterId)) {
            return emptyList()
        }

        val hiddenForViewer = reporterHiddenMessages[viewerCharacterId] ?: emptySet()

        return messages.filter { msg ->
            msg.channel == channel &&
            (channel != ChatChannel.GUILD || msg.guildId == guildId) &&
            msg.id !in hiddenForViewer &&
            !selfMutes.isMuted(viewerCharacterId, msg.senderCharacterId) &&
            !socialGraph.isBlocked(viewerCharacterId, msg.senderCharacterId)
        }
    }

    fun setGlobalChatOptOut(characterId: String, optedOut: Boolean) {
        if (optedOut) globalChatOptOut.add(characterId) else globalChatOptOut.remove(characterId)
    }

    fun selfMute(viewerCharacterId: String, targetCharacterId: String) = selfMutes.mute(viewerCharacterId, targetCharacterId)
    fun selfUnmute(viewerCharacterId: String, targetCharacterId: String) = selfMutes.unmute(viewerCharacterId, targetCharacterId)

    fun adminMute(characterId: String, duration: Duration, reason: String, issuedBy: String, now: Instant = Instant.now()): AdminMuteRecord {
        val record = AdminMuteRecord(characterId, now.plus(duration), reason, issuedBy)
        adminMutes[characterId] = record
        return record
    }

    fun reportMessage(
        reporterCharacterId: String,
        messageId: String,
        category: ReportCategory,
        reasoning: String
    ): ServiceResult<MessageReport> {
        val message = messages.find { it.id == messageId } ?: return ServiceResult.Failure("Message not found.")
        if (reasoning.isBlank()) return ServiceResult.Failure("A reason must be provided.")

        val report = MessageReport(
            messageId = messageId,
            reporterCharacterId = reporterCharacterId,
            reportedCharacterId = message.senderCharacterId,
            category = category,
            reasoning = reasoning
        )
        reports.add(report)

        reporterHiddenMessages.getOrPut(reporterCharacterId) { mutableSetOf() }.add(messageId)

        return ServiceResult.Success(report)
    }

    fun pendingReports(): List<MessageReport> = reports.filter { it.status == ReportStatus.PENDING }

    fun resolveReport(reportId: String, actionTaken: Boolean): ServiceResult<MessageReport> {
        val report = reports.find { it.id == reportId } ?: return ServiceResult.Failure("Report not found.")
        report.status = if (actionTaken) ReportStatus.REVIEWED_ACTION_TAKEN else ReportStatus.REVIEWED_NO_ACTION
        return ServiceResult.Success(report)
    }

    fun submitAppeal(characterId: String, relatedMuteReason: String, appealText: String): ServiceResult<Appeal> {
        if (appealText.isBlank()) return ServiceResult.Failure("Appeal text cannot be empty.")
        val appeal = Appeal(characterId = characterId, relatedMuteReason = relatedMuteReason, appealText = appealText)
        appeals.add(appeal)
        return ServiceResult.Success(appeal)
    }

    fun pendingAppeals(): List<Appeal> = appeals.filter { it.status == AppealStatus.PENDING }

    fun resolveAppeal(appealId: String, grant: Boolean, reviewerId: String, notes: String): ServiceResult<Appeal> {
        val appeal = appeals.find { it.id == appealId } ?: return ServiceResult.Failure("Appeal not found.")
        appeal.status = if (grant) AppealStatus.GRANTED else AppealStatus.DENIED
        appeal.reviewedBy = reviewerId
        appeal.reviewNotes = notes
        if (grant) {
            adminMutes.remove(appeal.characterId)
        }
        return ServiceResult.Success(appeal)
    }
}
