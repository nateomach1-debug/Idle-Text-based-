package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp

// =========================================================
// GUILD SCREEN
// Single scrollable screen: name -> active event/vote card ->
// tier+members row -> quests/structures -> leaderboard.
// =========================================================

enum class GuildMemberRole { LEADER, OFFICER, MEMBER }

data class GuildMemberSummary(
    val characterId: String,
    val displayName: String,
    val role: GuildMemberRole
)

data class GuildEventSummary(
    val id: String,
    val name: String,
    val itemId: String,
    val skillName: String,
    val progressCurrent: Int,
    val progressTarget: Int,
    val milestonesPaid: Int
)

data class GuildVoteSummary(
    val targetLeaderName: String,
    val hoursRemaining: Int,
    val removeVotes: Int,
    val keepVotes: Int
)

data class GuildQuestSummary(val name: String, val description: String)

data class GuildLeaderboardEntry(val displayName: String, val value: Long)

data class GuildHomeState(
    val guildName: String,
    val activeEvent: GuildEventSummary?,
    val activeVote: GuildVoteSummary?,
    val tier: Int,
    val guildLevel: Int,
    val guildXp: Long,
    val activeBonusPercent: Double,
    val members: List<GuildMemberSummary>,
    val quests: List<GuildQuestSummary>,
    val viewerRole: GuildMemberRole
)

@Composable
fun GuildHomeScreen(
    state: GuildHomeState,
    leaderboardEntries: List<GuildLeaderboardEntry>,
    leaderboardShowingDaily: Boolean,
    onToggleLeaderboardPeriod: () -> Unit,
    onMemberTapped: (GuildMemberSummary) -> Unit,
    onContributeToEvent: () -> Unit,
    onCastVote: (Boolean) -> Unit, // true = remove, false = keep
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
            text = state.guildName,
            style = MaterialTheme.typography.headlineMedium,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(12.dp))

        state.activeVote?.let { vote ->
            VoteCard(vote, onCastVote)
            Spacer(modifier = Modifier.height(12.dp))
        } ?: state.activeEvent?.let { event ->
            EventCard(event, onContributeToEvent)
            Spacer(modifier = Modifier.height(12.dp))
        }

        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            TierBonusCard(state.tier, state.activeBonusPercent, modifier = Modifier.weight(1f))
            MemberListCard(state.members, onMemberTapped, modifier = Modifier.weight(1f))
        }

        Spacer(modifier = Modifier.height(16.dp))

        QuestsSection(state.quests)

        Spacer(modifier = Modifier.height(16.dp))

        LeaderboardSection(leaderboardEntries, leaderboardShowingDaily, onToggleLeaderboardPeriod)
    }
}

@Composable
private fun EventCard(event: GuildEventSummary, onContribute: () -> Unit) {
    val fraction = (event.progressCurrent.toFloat() / event.progressTarget.toFloat()).coerceIn(0f, 1f)

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(14.dp)
    ) {
        Text(text = event.name, style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(6.dp))
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(8.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(MaterialTheme.colorScheme.background)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(fraction)
                    .fillMaxHeight()
                    .clip(RoundedCornerShape(4.dp))
                    .background(MaterialTheme.colorScheme.primary)
            )
        }
        Spacer(modifier = Modifier.height(4.dp))
        Text(text = event.progressCurrent.toString() + " / " + event.progressTarget, style = MaterialTheme.typography.labelSmall)
        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = onContribute, modifier = Modifier.fillMaxWidth()) {
            Text(text = "Contribute")
        }
    }
}

@Composable
private fun VoteCard(vote: GuildVoteSummary, onCastVote: (Boolean) -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.error.copy(alpha = 0.15f))
            .padding(14.dp)
    ) {
        Text(text = "Vote to remove " + vote.targetLeaderName + " as Leader", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(4.dp))
        Text(text = vote.hoursRemaining.toString() + "h remaining — " + vote.removeVotes + " remove / " + vote.keepVotes + " keep", style = MaterialTheme.typography.labelSmall)
        Spacer(modifier = Modifier.height(8.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = { onCastVote(true) }, modifier = Modifier.weight(1f)) { Text(text = "Remove") }
            OutlinedButton(onClick = { onCastVote(false) }, modifier = Modifier.weight(1f)) { Text(text = "Keep") }
        }
    }
}

@Composable
private fun TierBonusCard(tier: Int, bonusPercent: Double, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(14.dp)
    ) {
        Text(text = "Tier " + tier, style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = if (bonusPercent > 0) "+" + bonusPercent + "% active bonus" else "No active bonus",
            style = MaterialTheme.typography.labelSmall
        )
    }
}

@Composable
private fun MemberListCard(
    members: List<GuildMemberSummary>,
    onMemberTapped: (GuildMemberSummary) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(14.dp)
    ) {
        Text(text = "Members (" + members.size + "/20)", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(6.dp))
        members.forEach { member ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { onMemberTapped(member) }
                    .padding(vertical = 6.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(text = member.displayName, style = MaterialTheme.typography.bodyMedium)
                Text(text = member.role.name, style = MaterialTheme.typography.labelSmall)
            }
        }
    }
}

@Composable
private fun QuestsSection(quests: List<GuildQuestSummary>) {
    Column {
        Text(text = "Guild Quests", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        if (quests.isEmpty()) {
            Text(text = "No active guild quests.", style = MaterialTheme.typography.bodyMedium)
        }
        quests.forEach { quest ->
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(MaterialTheme.colorScheme.surface)
                    .padding(12.dp)
            ) {
                Text(text = quest.name, style = MaterialTheme.typography.bodyMedium)
                Text(text = quest.description, style = MaterialTheme.typography.labelSmall)
            }
        }
    }
}

@Composable
private fun LeaderboardSection(
    entries: List<GuildLeaderboardEntry>,
    showingDaily: Boolean,
    onTogglePeriod: () -> Unit
) {
    Column {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(text = "Leaderboard", style = MaterialTheme.typography.titleMedium)
            TextButton(onClick = onTogglePeriod) {
                Text(text = if (showingDaily) "Daily" else "All-Time")
            }
        }
        Spacer(modifier = Modifier.height(8.dp))
        entries.forEachIndexed { index, entry ->
            Row(
                modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(text = (index + 1).toString() + ". " + entry.displayName, style = MaterialTheme.typography.bodyMedium)
                Text(text = entry.value.toString(), style = MaterialTheme.typography.labelSmall)
            }
        }
    }
}
