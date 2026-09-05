def apply(content, old, new, label):
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"FAILED [{label}]: expected 1 match, found {count}")
    return content.replace(old, new, 1)

# ---------- GuildHomeScreen.kt ----------
GHS_PATH = "app/src/main/kotlin/com/yourname/idlerpg/GuildHomeScreen.kt"
with open(GHS_PATH, "r", encoding="utf-8") as f:
    ghs = f.read()

ghs = apply(ghs,
"""@Composable
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
}""",
"""@Composable
fun GuildHomeScreen(
    state: GuildHomeState,
    leaderboardEntries: List<GuildLeaderboardEntry>,
    leaderboardShowingDaily: Boolean,
    contributableQuantity: Int,
    xpRequiredForNextLevel: Long,
    actionError: String?,
    onToggleLeaderboardPeriod: () -> Unit,
    onMemberTapped: (GuildMemberSummary) -> Unit,
    onContributeToEvent: (Int) -> Unit,
    onStartEvent: () -> Unit,
    onCastVote: (Boolean) -> Unit, // true = remove, false = keep
    onDismissError: () -> Unit,
    modifier: Modifier = Modifier
) {
    val scrollState = rememberScrollState()
    var showContributeDialog by remember { mutableStateOf(false) }

    actionError?.let { error ->
        AlertDialog(
            onDismissRequest = onDismissError,
            title = { Text(text = "Guild Action Failed") },
            text = { Text(text = error) },
            confirmButton = {
                TextButton(onClick = onDismissError) { Text(text = "OK") }
            }
        )
    }

    if (showContributeDialog && state.activeEvent != null) {
        ContributeDialog(
            event = state.activeEvent,
            availableQuantity = contributableQuantity,
            onDismiss = { showContributeDialog = false },
            onConfirm = { qty ->
                onContributeToEvent(qty)
                showContributeDialog = false
            }
        )
    }

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

        GuildLevelCard(state.guildLevel, state.guildXp, xpRequiredForNextLevel)

        Spacer(modifier = Modifier.height(12.dp))

        state.activeVote?.let { vote ->
            VoteCard(vote, onCastVote)
            Spacer(modifier = Modifier.height(12.dp))
        } ?: state.activeEvent?.let { event ->
            EventCard(event, onContribute = { showContributeDialog = true })
            Spacer(modifier = Modifier.height(12.dp))
        } ?: run {
            if (state.viewerRole == GuildMemberRole.OFFICER || state.viewerRole == GuildMemberRole.LEADER) {
                StartEventCard(onStartEvent)
                Spacer(modifier = Modifier.height(12.dp))
            }
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
private fun GuildLevelCard(level: Int, xp: Long, xpRequiredForNextLevel: Long) {
    val fraction = if (xpRequiredForNextLevel > 0) (xp.toFloat() / xpRequiredForNextLevel.toFloat()).coerceIn(0f, 1f) else 0f
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(14.dp)
    ) {
        Text(text = "Guild Level " + level, style = MaterialTheme.typography.titleMedium)
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
        Text(text = "%,d / %,d XP".format(xp, xpRequiredForNextLevel), style = MaterialTheme.typography.labelSmall)
    }
}

@Composable
private fun StartEventCard(onStartEvent: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(14.dp)
    ) {
        Text(text = "No active guild event", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = onStartEvent, modifier = Modifier.fillMaxWidth()) {
            Text(text = "Start Guild Event")
        }
    }
}

@Composable
private fun ContributeDialog(
    event: GuildEventSummary,
    availableQuantity: Int,
    onDismiss: () -> Unit,
    onConfirm: (Int) -> Unit
) {
    val remaining = (event.progressTarget - event.progressCurrent).coerceAtLeast(0)
    val maxContributable = availableQuantity.coerceAtMost(remaining)
    var quantityText by remember { mutableStateOf(maxContributable.coerceAtLeast(1).toString()) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(text = "Contribute to " + event.name) },
        text = {
            Column {
                Text(text = "You have " + availableQuantity + " available. " + remaining + " still needed.", style = MaterialTheme.typography.labelSmall)
                Spacer(modifier = Modifier.height(8.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    OutlinedTextField(
                        value = quantityText,
                        onValueChange = { input -> if (input.all { it.isDigit() }) quantityText = input },
                        modifier = Modifier.weight(1f),
                        label = { Text(text = "Quantity") }
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    TextButton(onClick = { quantityText = maxContributable.coerceAtLeast(0).toString() }) {
                        Text(text = "Max")
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = {
                val qty = quantityText.toIntOrNull()?.coerceIn(0, maxContributable) ?: 0
                if (qty > 0) onConfirm(qty)
            }) {
                Text(text = "Contribute")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text(text = "Cancel") }
        }
    )
}""",
    "GuildHomeScreen: add level card, start-event card, contribute dialog, error dialog"
)

with open(GHS_PATH, "w", encoding="utf-8") as f:
    f.write(ghs)

# ---------- GameViewModel.kt ----------
GVM_PATH = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(GVM_PATH, "r", encoding="utf-8") as f:
    gvm = f.read()

gvm = apply(gvm,
"""    // Must match the SQL curve in contribute_to_guild_event() - level L needs
    // 1000*L XP to advance to L+1. Exposed here so the UI can show a progress
    // bar without a network round trip.
    fun guildXpRequiredForLevel(level: Int): Long = 1000L * level""",
"""    // Must match the SQL curve in contribute_to_guild_event() - level L needs
    // 1000*L XP to advance to L+1. Exposed here so the UI can show a progress
    // bar without a network round trip.
    fun guildXpRequiredForLevel(level: Int): Long = 1000L * level

    fun currentInventoryQuantityOf(itemId: String): Int {
        val characterId = _currentCharacterId.value ?: return 0
        return inventoryService.inventoryFor(characterId).quantityOf(itemId)
    }

    fun clearGuildActionError() {
        _guildActionError.value = null
    }""",
    "add currentInventoryQuantityOf + clearGuildActionError"
)

with open(GVM_PATH, "w", encoding="utf-8") as f:
    f.write(gvm)

# ---------- MainActivity.kt ----------
MA_PATH = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(MA_PATH, "r", encoding="utf-8") as f:
    ma = f.read()

ma = apply(ma,
"""                                    GuildHomeScreen(
                                        state = guildState,
                                        leaderboardEntries = currentGuildLeaderboard,
                                        leaderboardShowingDaily = leaderboardShowingDaily,
                                        onToggleLeaderboardPeriod = { leaderboardShowingDaily = !leaderboardShowingDaily },
                                        onMemberTapped = { selectedGuildMember = it },
                                        onContributeToEvent = { },
                                        onCastVote = { }
                                    )""",
"""                                    val guildActionErrorState by gameViewModel.guildActionError.collectAsState()
                                    val contributableQuantity = guildState.activeEvent?.let { gameViewModel.currentInventoryQuantityOf(it.itemId) } ?: 0
                                    GuildHomeScreen(
                                        state = guildState,
                                        leaderboardEntries = currentGuildLeaderboard,
                                        leaderboardShowingDaily = leaderboardShowingDaily,
                                        contributableQuantity = contributableQuantity,
                                        xpRequiredForNextLevel = gameViewModel.guildXpRequiredForLevel(guildState.guildLevel),
                                        actionError = guildActionErrorState,
                                        onToggleLeaderboardPeriod = { leaderboardShowingDaily = !leaderboardShowingDaily },
                                        onMemberTapped = { selectedGuildMember = it },
                                        onContributeToEvent = { qty -> gameViewModel.contributeToGuildEvent(qty) },
                                        onStartEvent = { gameViewModel.startGuildEvent() },
                                        onCastVote = { },
                                        onDismissError = { gameViewModel.clearGuildActionError() }
                                    )""",
    "MainActivity: wire new GuildHomeScreen params"
)

with open(MA_PATH, "w", encoding="utf-8") as f:
    f.write(ma)

print("All edits applied successfully across all three files.")
