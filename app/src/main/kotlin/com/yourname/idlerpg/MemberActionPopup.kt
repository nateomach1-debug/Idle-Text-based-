package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier

// =========================================================
// MEMBER ACTION POPUP
// Role-based actions shown depending on the VIEWER's role,
// not the tapped member's role. Leader sees the most options.
// =========================================================

@Composable
fun MemberActionPopup(
    member: GuildMemberSummary,
    viewerRole: GuildMemberRole,
    onDismiss: () -> Unit,
    onKick: () -> Unit,
    onPromote: () -> Unit,
    onDemote: () -> Unit,
    onInitiateVote: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(text = member.displayName, style = MaterialTheme.typography.headlineMedium) },
        text = {
            Column {
                Text(text = "Role: " + member.role.name, style = MaterialTheme.typography.bodyMedium)
                Spacer()

                if (viewerRole == GuildMemberRole.LEADER) {
                    if (member.role == GuildMemberRole.MEMBER) {
                        TextButton(onClick = onPromote) { Text(text = "Promote to Officer") }
                    }
                    if (member.role == GuildMemberRole.OFFICER) {
                        TextButton(onClick = onPromote) { Text(text = "Promote to Leader") }
                        TextButton(onClick = onDemote) { Text(text = "Demote to Member") }
                    }
                    if (member.role == GuildMemberRole.LEADER) {
                        TextButton(onClick = onInitiateVote) { Text(text = "Initiate Removal Vote") }
                    }
                    if (member.role != GuildMemberRole.LEADER) {
                        TextButton(onClick = onKick) { Text(text = "Kick from Guild") }
                    }
                }
                // Officers and Members currently have no actions available here --
                // consistent with the backend's Permissions object, where only
                // Leaders can kick/promote/demote/initiate votes.
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) { Text(text = "Close") }
        }
    )
}

@Composable
private fun Spacer() {
    androidx.compose.foundation.layout.Spacer(modifier = Modifier.fillMaxWidth())
}
