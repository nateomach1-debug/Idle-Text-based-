#!/usr/bin/env python3
"""
Quick-wins patch, part 2a: HomeScreen.kt

- HomeScreenState now takes `activeQueue: ActiveQueueInfo?` instead of
  `queueLabel`/`queueEndsAt`, and drops `pendingLootCount` entirely.
- QueueCard/LiveCountdown become QueueCard/CycleCountdown: the countdown is
  computed live from `startedAt + secondsPerAction` against wall-clock time
  (skilling/crafting loops repeat indefinitely -- there's no fixed end), and
  rolls back to the full duration each time a new cycle starts. Ticks every
  100ms so short cycles show a smooth "3.62s left" style countdown.
- CollectLootButton and its call site are removed -- items already collect
  automatically on reopen.
- `onCollectLoot` parameter removed from HomeScreen().

Run from repo root:
    python3 apply_quickwins_homescreen.py
Then run part 2b (MainActivity.kt) before rebuilding -- HomeScreen() call
sites won't compile until both are applied.
"""
import sys
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/HomeScreen.kt")

EXPECTED_OLD = '''package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import java.time.Duration
import java.time.Instant

// =========================================================
// HOME / CHECK-IN SCREEN
// Per the locked spec: queue status + time remaining, currency,
// HP (only if relevant), notification badge summary, collect-loot
// button if loot is pending. Timers tick live off a server-provided
// end-timestamp, not repeated polling.
// =========================================================

data class HomeScreenState(
    val queueLabel: String?,          // e.g. "Mining Iron Ore" -- null if no active queue
    val queueEndsAt: Instant?,        // server-provided end timestamp for the live countdown
    val softCurrency: Long,
    val premiumCurrency: Long,
    val currentHp: Int?,              // null if not in/near combat -- hides the HP bar entirely
    val maxHp: Int?,
    val isRecovering: Boolean,
    val pendingLootCount: Int,
    val unreadNotificationCount: Int
)

@Composable
fun HomeScreen(
    state: HomeScreenState,
    onCollectLoot: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(20.dp)
    ) {
        Text(
            text = "Home",
            style = MaterialTheme.typography.headlineMedium
        )

        Spacer(modifier = Modifier.height(20.dp))

        CurrencyRow(soft = state.softCurrency, premium = state.premiumCurrency)

        Spacer(modifier = Modifier.height(16.dp))

        if (state.currentHp != null && state.maxHp != null) {
            HpBar(current = state.currentHp, max = state.maxHp, isRecovering = state.isRecovering)
            Spacer(modifier = Modifier.height(16.dp))
        }

        QueueCard(label = state.queueLabel, endsAt = state.queueEndsAt)

        Spacer(modifier = Modifier.height(16.dp))

        if (state.pendingLootCount > 0) {
            CollectLootButton(count = state.pendingLootCount, onClick = onCollectLoot)
            Spacer(modifier = Modifier.height(16.dp))
        }

        if (state.unreadNotificationCount > 0) {
            NotificationSummary(count = state.unreadNotificationCount)
        }
    }
}

@Composable
private fun CurrencyRow(soft: Long, premium: Long) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        CurrencyPill(label = "Gold", amount = soft)
        CurrencyPill(label = "Gems", amount = premium)
    }
}

@Composable
private fun CurrencyPill(label: String, amount: Long) {
    Row(
        modifier = Modifier
            .clip(RoundedCornerShape(20.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(horizontal = 14.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(text = label, style = MaterialTheme.typography.labelSmall)
        Spacer(modifier = Modifier.width(6.dp))
        Text(text = amount.toString(), style = MaterialTheme.typography.titleMedium)
    }
}

@Composable
private fun HpBar(current: Int, max: Int, isRecovering: Boolean) {
    val fraction = (current.toFloat() / max.toFloat()).coerceIn(0f, 1f)
    val barColor = if (isRecovering) MaterialTheme.colorScheme.secondary else MaterialTheme.colorScheme.error

    Column {
        Text(
            text = if (isRecovering) "Recovering..." else "Health",
            style = MaterialTheme.typography.labelSmall
        )
        Spacer(modifier = Modifier.height(4.dp))
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(10.dp)
                .clip(RoundedCornerShape(5.dp))
                .background(MaterialTheme.colorScheme.surface)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(fraction)
                    .fillMaxHeight()
                    .clip(RoundedCornerShape(5.dp))
                    .background(barColor)
            )
        }
        Spacer(modifier = Modifier.height(2.dp))
        Text(text = "$current / $max", style = MaterialTheme.typography.labelSmall)
    }
}

@Composable
private fun QueueCard(label: String?, endsAt: Instant?) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(16.dp)
    ) {
        if (label == null || endsAt == null) {
            Text(text = "No active queue", style = MaterialTheme.typography.bodyMedium)
            return@Column
        }

        Text(text = label, style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        LiveCountdown(endsAt = endsAt)
    }
}

/**
 * Ticks locally off a fixed server-provided end-timestamp -- no repeated
 * polling required, just a local Compose recomposition loop.
 */
@Composable
private fun LiveCountdown(endsAt: Instant) {
    var remaining by remember(endsAt) { mutableStateOf(Duration.between(Instant.now(), endsAt)) }

    LaunchedEffect(endsAt) {
        while (true) {
            remaining = Duration.between(Instant.now(), endsAt)
            if (remaining.isNegative || remaining.isZero) break
            delay(1000)
        }
    }

    val displayText = if (remaining.isNegative || remaining.isZero) {
        "Finishing..."
    } else {
        val totalSeconds = remaining.seconds
        val hours = totalSeconds / 3600
        val minutes = (totalSeconds % 3600) / 60
        val seconds = totalSeconds % 60
        if (hours > 0) {
            String.format("%d:%02d:%02d remaining", hours, minutes, seconds)
        } else {
            String.format("%d:%02d remaining", minutes, seconds)
        }
    }

    Text(text = displayText, style = MaterialTheme.typography.bodyMedium)
}

@Composable
private fun CollectLootButton(count: Int, onClick: () -> Unit) {
    Button(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth()
    ) {
        Text(text = "Collect Loot ($count pending)")
    }
}

@Composable
private fun NotificationSummary(count: Int) {
    Text(
        text = "$count new notification" + if (count == 1) "" else "s",
        style = MaterialTheme.typography.labelSmall,
        textAlign = TextAlign.Start
    )
}
'''

NEW_CONTENT = '''package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.yourname.idlerpg.data.ActiveQueueInfo
import kotlinx.coroutines.delay
import java.time.Duration
import java.time.Instant

// =========================================================
// HOME / CHECK-IN SCREEN
// Per the locked spec: queue status + time remaining, currency,
// HP (only if relevant), notification badge summary. Loot collects
// automatically on reopen, so there's no manual collect step here.
// The countdown reflects time remaining in the *current* action cycle --
// skilling/crafting loops repeat indefinitely, they don't have a fixed
// overall end -- computed live from the queue's startedAt + secondsPerAction
// rather than a single server end-timestamp.
// =========================================================

data class HomeScreenState(
    val activeQueue: ActiveQueueInfo?, // null if no active queue
    val softCurrency: Long,
    val premiumCurrency: Long,
    val currentHp: Int?,              // null if not in/near combat -- hides the HP bar entirely
    val maxHp: Int?,
    val isRecovering: Boolean,
    val unreadNotificationCount: Int
)

@Composable
fun HomeScreen(
    state: HomeScreenState,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(20.dp)
    ) {
        Text(
            text = "Home",
            style = MaterialTheme.typography.headlineMedium
        )

        Spacer(modifier = Modifier.height(20.dp))

        CurrencyRow(soft = state.softCurrency, premium = state.premiumCurrency)

        Spacer(modifier = Modifier.height(16.dp))

        if (state.currentHp != null && state.maxHp != null) {
            HpBar(current = state.currentHp, max = state.maxHp, isRecovering = state.isRecovering)
            Spacer(modifier = Modifier.height(16.dp))
        }

        QueueCard(queue = state.activeQueue)

        Spacer(modifier = Modifier.height(16.dp))

        if (state.unreadNotificationCount > 0) {
            NotificationSummary(count = state.unreadNotificationCount)
        }
    }
}

@Composable
private fun CurrencyRow(soft: Long, premium: Long) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        CurrencyPill(label = "Gold", amount = soft)
        CurrencyPill(label = "Gems", amount = premium)
    }
}

@Composable
private fun CurrencyPill(label: String, amount: Long) {
    Row(
        modifier = Modifier
            .clip(RoundedCornerShape(20.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(horizontal = 14.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(text = label, style = MaterialTheme.typography.labelSmall)
        Spacer(modifier = Modifier.width(6.dp))
        Text(text = amount.toString(), style = MaterialTheme.typography.titleMedium)
    }
}

@Composable
private fun HpBar(current: Int, max: Int, isRecovering: Boolean) {
    val fraction = (current.toFloat() / max.toFloat()).coerceIn(0f, 1f)
    val barColor = if (isRecovering) MaterialTheme.colorScheme.secondary else MaterialTheme.colorScheme.error

    Column {
        Text(
            text = if (isRecovering) "Recovering..." else "Health",
            style = MaterialTheme.typography.labelSmall
        )
        Spacer(modifier = Modifier.height(4.dp))
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(10.dp)
                .clip(RoundedCornerShape(5.dp))
                .background(MaterialTheme.colorScheme.surface)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(fraction)
                    .fillMaxHeight()
                    .clip(RoundedCornerShape(5.dp))
                    .background(barColor)
            )
        }
        Spacer(modifier = Modifier.height(2.dp))
        Text(text = "$current / $max", style = MaterialTheme.typography.labelSmall)
    }
}

@Composable
private fun QueueCard(queue: ActiveQueueInfo?) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(16.dp)
    ) {
        if (queue == null) {
            Text(text = "No active queue", style = MaterialTheme.typography.bodyMedium)
            return@Column
        }

        Text(text = queue.label, style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        CycleCountdown(queue = queue)
    }
}

/**
 * Skilling/crafting loops repeat every `secondsPerAction` and don't have a
 * fixed overall end -- so this ticks down the time remaining in the
 * *current* cycle, computed live from startedAt + secondsPerAction against
 * wall-clock time, and rolls back to the full duration once the next cycle
 * begins. Ticks every 100ms so short cycles still show a smooth countdown.
 */
@Composable
private fun CycleCountdown(queue: ActiveQueueInfo) {
    fun remainingSecondsNow(): Double {
        val elapsedMs = Duration.between(queue.startedAt, Instant.now()).toMillis().coerceAtLeast(0)
        val cycleMs = queue.secondsPerAction * 1000
        if (cycleMs <= 0) return 0.0
        val remainingMs = cycleMs - (elapsedMs % cycleMs)
        return remainingMs / 1000.0
    }

    var remainingSeconds by remember(queue.startedAt, queue.secondsPerAction) {
        mutableStateOf(remainingSecondsNow())
    }

    LaunchedEffect(queue.startedAt, queue.secondsPerAction) {
        while (true) {
            remainingSeconds = remainingSecondsNow()
            delay(100)
        }
    }

    val displayText = if (remainingSeconds >= 60.0) {
        val totalSeconds = remainingSeconds.toLong()
        val minutes = totalSeconds / 60
        val seconds = totalSeconds % 60
        String.format("%d:%02d remaining", minutes, seconds)
    } else {
        String.format("%.2fs left", remainingSeconds)
    }

    Text(text = displayText, style = MaterialTheme.typography.bodyMedium)
}

@Composable
private fun NotificationSummary(count: Int) {
    Text(
        text = "$count new notification" + if (count == 1) "" else "s",
        style = MaterialTheme.typography.labelSmall,
        textAlign = TextAlign.Start
    )
}
'''


def fail(msg):
    print(f"FAILED: {msg}")
    sys.exit(1)


def main():
    if not TARGET.exists():
        fail(f"{TARGET} not found -- run this from the repo root")

    text = TARGET.read_text()

    if text == NEW_CONTENT:
        fail("HomeScreen.kt already matches the new content -- patch may already be applied")

    if text != EXPECTED_OLD:
        fail(
            "current HomeScreen.kt does not exactly match the expected pre-patch content "
            "(it may have drifted since the last dump) -- aborting rather than risk overwriting "
            "unrelated changes. Paste the current file back to me and I'll adjust the script."
        )

    TARGET.write_text(NEW_CONTENT)
    print(f"OK: patched {TARGET}")
    print("Run part 2b (MainActivity.kt) next before rebuilding.")


if __name__ == "__main__":
    main()
