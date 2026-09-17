package com.yourname.idlerpg

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp

// =========================================================
// STATE
// =========================================================

data class ModerationState(
    val pendingReports: List<PendingReportUi> = emptyList(),
    val pendingAppeals: List<PendingAppealUi> = emptyList(),
    val isLoading: Boolean = false
)

// =========================================================
// SCREEN
// This screen assumes the caller has already gated entry on
// the viewer's profile is_moderator flag. Every action below
// still calls a SECURITY DEFINER RPC that independently
// re-checks caller_is_moderator() - this screen is a UI
// convenience, not the enforcement boundary.
// =========================================================

@Composable
fun ModerationScreen(
    state: ModerationState,
    onResolveReport: (reportId: String, actionTaken: Boolean) -> Unit,
    onResolveAppeal: (appealId: String, grant: Boolean, notes: String) -> Unit,
    onMuteCharacter: (characterId: String, durationSeconds: Int, reason: String) -> Unit,
    onUnmuteCharacter: (characterId: String) -> Unit,
    onGrantGems: (String, Long, String) -> Unit = { _, _, _ -> },
    lookupError: String? = null,
    modifier: Modifier = Modifier
) {
    val scrollState = rememberScrollState()

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(20.dp)
            .verticalScroll(scrollState)
    ) {
        Text(
            text = "Moderation",
            style = MaterialTheme.typography.headlineMedium,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth()
        )

        if (lookupError != null) {
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = lookupError,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodyMedium
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        if (state.isLoading) {
            Text(text = "Loading...", style = MaterialTheme.typography.bodyMedium)
            Spacer(modifier = Modifier.height(16.dp))
        }

        ReportsSection(state.pendingReports, onResolveReport)

        Spacer(modifier = Modifier.height(20.dp))

        AppealsSection(state.pendingAppeals, onResolveAppeal)

        Spacer(modifier = Modifier.height(20.dp))

        ManualMuteSection(onMuteCharacter, onUnmuteCharacter)

        Spacer(modifier = Modifier.height(20.dp))

        ManualGrantGemsSection(onGrantGems)
    }
}

// ---------------------------------------------------------
// PENDING REPORTS
// ---------------------------------------------------------

@Composable
private fun ReportsSection(
    reports: List<PendingReportUi>,
    onResolveReport: (String, Boolean) -> Unit
) {
    Column {
        Text(text = "Pending Reports (${reports.size})", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))

        if (reports.isEmpty()) {
            Text(text = "No pending reports.", style = MaterialTheme.typography.bodyMedium)
        }

        reports.forEach { report ->
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(MaterialTheme.colorScheme.surface)
                    .padding(12.dp)
            ) {
                Text(text = "${report.category} - reported by ${report.reporterName}", style = MaterialTheme.typography.bodyMedium)
                Text(text = "Against: ${report.reportedName}", style = MaterialTheme.typography.labelSmall)
                Text(text = report.reason, style = MaterialTheme.typography.labelSmall)
                Spacer(modifier = Modifier.height(8.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(onClick = { onResolveReport(report.id, true) }, modifier = Modifier.weight(1f)) {
                        Text(text = "Action Taken")
                    }
                    OutlinedButton(onClick = { onResolveReport(report.id, false) }, modifier = Modifier.weight(1f)) {
                        Text(text = "No Action")
                    }
                }
            }
        }
    }
}

// ---------------------------------------------------------
// PENDING APPEALS
// ---------------------------------------------------------

@Composable
private fun AppealsSection(
    appeals: List<PendingAppealUi>,
    onResolveAppeal: (String, Boolean, String) -> Unit
) {
    Column {
        Text(text = "Pending Appeals (${appeals.size})", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))

        if (appeals.isEmpty()) {
            Text(text = "No pending appeals.", style = MaterialTheme.typography.bodyMedium)
        }

        appeals.forEach { appeal ->
            var notes by remember(appeal.id) { mutableStateOf("") }

            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(MaterialTheme.colorScheme.surface)
                    .padding(12.dp)
            ) {
                Text(text = appeal.characterName, style = MaterialTheme.typography.bodyMedium)
                Text(text = appeal.appealText, style = MaterialTheme.typography.labelSmall)
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(
                    value = notes,
                    onValueChange = { notes = it },
                    label = { Text(text = "Review notes") },
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(modifier = Modifier.height(8.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(onClick = { onResolveAppeal(appeal.id, true, notes) }, modifier = Modifier.weight(1f)) {
                        Text(text = "Grant")
                    }
                    OutlinedButton(onClick = { onResolveAppeal(appeal.id, false, notes) }, modifier = Modifier.weight(1f)) {
                        Text(text = "Deny")
                    }
                }
            }
        }
    }
}

// ---------------------------------------------------------
// MANUAL MUTE / UNMUTE
// For muting a character directly, outside the report flow -
// e.g. acting on something reported through another channel.
// ---------------------------------------------------------

@Composable
private fun ManualGrantGemsSection(
    onGrantGems: (String, Long, String) -> Unit
) {
    var characterId by remember { mutableStateOf("") }
    var amountText by remember { mutableStateOf("500") }
    var reason by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(12.dp)
    ) {
        Text(text = "Grant Gems", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = characterId,
            onValueChange = { characterId = it },
            label = { Text(text = "Character Name") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = amountText,
            onValueChange = { input -> if (input.all { it.isDigit() }) amountText = input },
            label = { Text(text = "Amount") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = reason,
            onValueChange = { reason = it },
            label = { Text(text = "Reason") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = {
                val amount = amountText.toLongOrNull()
                if (amount != null && amount > 0 && characterId.isNotBlank() && reason.isNotBlank()) {
                    onGrantGems(characterId, amount, reason)
                }
            }
        ) {
            Text(text = "Grant Gems")
        }
    }
}

@Composable
private fun ManualMuteSection(
    onMuteCharacter: (String, Int, String) -> Unit,
    onUnmuteCharacter: (String) -> Unit
) {
    var characterId by remember { mutableStateOf("") }
    var durationMinutes by remember { mutableStateOf("60") }
    var reason by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(12.dp)
    ) {
        Text(text = "Manual Mute", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = characterId,
            onValueChange = { characterId = it },
            label = { Text(text = "Character Name") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = durationMinutes,
            onValueChange = { durationMinutes = it },
            label = { Text(text = "Duration (minutes)") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = reason,
            onValueChange = { reason = it },
            label = { Text(text = "Reason") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(
                onClick = {
                    val minutes = durationMinutes.toIntOrNull() ?: 60
                    onMuteCharacter(characterId, minutes * 60, reason)
                },
                modifier = Modifier.weight(1f)
            ) {
                Text(text = "Mute")
            }
            OutlinedButton(
                onClick = { onUnmuteCharacter(characterId) },
                modifier = Modifier.weight(1f)
            ) {
                Text(text = "Unmute")
            }
        }
    }
}
