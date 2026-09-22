package com.yourname.idlerpg.ui.components

import androidx.compose.animation.animateContentSize
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp

// =========================================================
// PERSISTENT CHAT BANNER
// Lives in the app's shared top-level layout (like RecoveryBar).
// Collapsed: always shows last 3 messages from selected channel.
// Expanded: full panel with channel tabs, ~10-15% -> larger height.
// =========================================================

enum class ChatChannelUi { GLOBAL, GUILD, TRADE, HELP, DMS }

data class ChatMessageUi(
    val id: String,
    val senderCharacterId: String,
    val senderName: String,
    val content: String,
    val channel: ChatChannelUi,
    val senderTitleId: String? = null,
    val senderBadgeId: String? = null
)

data class DmConversationSummary(
    val characterId: String,
    val displayName: String,
    val lastMessagePreview: String
)

@Composable
fun ChatBanner(
    selectedChannel: ChatChannelUi,
    onChannelSelected: (ChatChannelUi) -> Unit,
    messages: List<ChatMessageUi>, // pre-filtered to selectedChannel by caller
    dmConversations: List<DmConversationSummary>,
    selectedDmCharacterId: String?,
    onDmSelected: (String) -> Unit,
    hasUnread: Boolean,
    messageInput: String,
    onMessageInputChanged: (String) -> Unit,
    onSendMessage: () -> Unit,
    onMessageAction: (ChatMessageUi, ChatMessageAction) -> Unit,
    modifier: Modifier = Modifier
) {
    var expanded by remember { mutableStateOf(false) }
    var showChannelPicker by remember { mutableStateOf(false) }

    Column(
        modifier = modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surface)
            .animateContentSize()
    ) {
        // Header -- always visible, tap to expand/collapse, tap title for channel picker
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clickable { expanded = !expanded }
                .padding(horizontal = 12.dp, vertical = 6.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                if (hasUnread) {
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .clip(RoundedCornerShape(4.dp))
                            .background(MaterialTheme.colorScheme.error)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                }
                Text(
                    text = selectedChannel.name,
                    style = MaterialTheme.typography.labelSmall,
                    modifier = Modifier.clickable { showChannelPicker = true }
                )
            }
            Text(text = if (expanded) "▼" else "▲", style = MaterialTheme.typography.labelSmall)
        }

        if (expanded) {
            ExpandedChatPanel(
                selectedChannel = selectedChannel,
                messages = messages,
                dmConversations = dmConversations,
                selectedDmCharacterId = selectedDmCharacterId,
                onDmSelected = onDmSelected,
                messageInput = messageInput,
                onMessageInputChanged = onMessageInputChanged,
                onSendMessage = onSendMessage,
                onMessageAction = onMessageAction
            )
        } else {
            CollapsedMessagePreview(messages.takeLast(3).reversed())
        }
    }

    if (showChannelPicker) {
        ChannelPickerDialog(
            currentChannel = selectedChannel,
            onChannelChosen = {
                onChannelSelected(it)
                showChannelPicker = false
            },
            onDismiss = { showChannelPicker = false }
        )
    }
}

@Composable
private fun CollapsedMessagePreview(lastThree: List<ChatMessageUi>) {
    Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 4.dp)) {
        if (lastThree.isEmpty()) {
            Text(text = "No messages yet.", style = MaterialTheme.typography.labelSmall)
        }
        lastThree.forEach { msg ->
            Text(
                text = chatLineText(msg),
                style = MaterialTheme.typography.labelSmall,
                maxLines = 1
            )
        }
    }
}

@Composable
private fun ExpandedChatPanel(
    selectedChannel: ChatChannelUi,
    messages: List<ChatMessageUi>,
    dmConversations: List<DmConversationSummary>,
    selectedDmCharacterId: String?,
    onDmSelected: (String) -> Unit,
    messageInput: String,
    onMessageInputChanged: (String) -> Unit,
    onSendMessage: () -> Unit,
    onMessageAction: (ChatMessageUi, ChatMessageAction) -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .heightIn(min = 220.dp, max = 320.dp)
            .padding(horizontal = 12.dp)
    ) {
        if (selectedChannel == ChatChannelUi.DMS && selectedDmCharacterId == null) {
            DmConversationList(dmConversations, onDmSelected)
        } else {
            LazyColumn(modifier = Modifier.weight(1f)) {
                items(messages.reversed()) { msg ->
                    ChatMessageRow(msg, onMessageAction)
                }
            }

            Spacer(modifier = Modifier.height(6.dp))

            Row(verticalAlignment = Alignment.CenterVertically) {
                OutlinedTextField(
                    value = messageInput,
                    onValueChange = onMessageInputChanged,
                    modifier = Modifier.weight(1f),
                    placeholder = { Text("Message...") },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                    keyboardActions = KeyboardActions(onSend = { onSendMessage() })
                )
                Spacer(modifier = Modifier.width(8.dp))
                Button(onClick = onSendMessage) { Text(text = "Send") }
            }
            Spacer(modifier = Modifier.height(8.dp))
        }
    }
}

@Composable
private fun DmConversationList(conversations: List<DmConversationSummary>, onSelected: (String) -> Unit) {
    LazyColumn {
        items(conversations) { convo ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { onSelected(convo.characterId) }
                    .padding(vertical = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(text = convo.displayName, style = MaterialTheme.typography.bodyMedium)
                Text(text = convo.lastMessagePreview, style = MaterialTheme.typography.labelSmall, maxLines = 1)
            }
        }
        if (conversations.isEmpty()) {
            item { Text(text = "No conversations yet.", style = MaterialTheme.typography.bodyMedium) }
        }
    }
}

enum class ChatMessageAction { REPORT, BLOCK, SELF_MUTE, MESSAGE_PLAYER }

@OptIn(androidx.compose.foundation.ExperimentalFoundationApi::class)
@Composable
private fun ChatMessageRow(message: ChatMessageUi, onAction: (ChatMessageUi, ChatMessageAction) -> Unit) {
    var showActionMenu by remember { mutableStateOf(false) }

    Box {
        Text(
            text = chatLineText(message),
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier
                .fillMaxWidth()
                .combinedClickable(
                    interactionSource = remember { MutableInteractionSource() },
                    indication = null,
                    onClick = { },
                    onLongClick = { showActionMenu = true }
                )
                .padding(vertical = 4.dp)
        )

        DropdownMenu(expanded = showActionMenu, onDismissRequest = { showActionMenu = false }) {
            DropdownMenuItem(
                text = { Text("Message " + message.senderName) },
                onClick = { onAction(message, ChatMessageAction.MESSAGE_PLAYER); showActionMenu = false }
            )
            DropdownMenuItem(
                text = { Text("Report") },
                onClick = { onAction(message, ChatMessageAction.REPORT); showActionMenu = false }
            )
            DropdownMenuItem(
                text = { Text("Block") },
                onClick = { onAction(message, ChatMessageAction.BLOCK); showActionMenu = false }
            )
            DropdownMenuItem(
                text = { Text("Self-Mute") },
                onClick = { onAction(message, ChatMessageAction.SELF_MUTE); showActionMenu = false }
            )
        }
    }
}

@Composable
private fun ChannelPickerDialog(
    currentChannel: ChatChannelUi,
    onChannelChosen: (ChatChannelUi) -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(text = "Select Channel") },
        text = {
            Column {
                ChatChannelUi.values().forEach { channel ->
                    Text(
                        text = channel.name,
                        style = if (channel == currentChannel) MaterialTheme.typography.titleMedium else MaterialTheme.typography.bodyMedium,
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { onChannelChosen(channel) }
                            .padding(vertical = 10.dp)
                    )
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) { Text("Cancel") }
        }
    )
}
