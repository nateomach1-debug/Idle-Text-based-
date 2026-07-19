package com.yourname.idlerpg.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.lerp
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import java.time.Duration
import java.time.Instant

// =========================================================
// PERSISTENT RECOVERY BAR
// Shown across EVERY screen (lives in the app's shared top-level
// layout, not inside any individual screen) whenever the character
// is recovering. Heart icon fills red -> green as the 600-second
// timer counts down; countdown text sits next to it.
// =========================================================

@Composable
fun RecoveryBar(
    recoveringUntil: Instant?,
    recoveryDurationSeconds: Long = 600L,
    modifier: Modifier = Modifier
) {
    val isRecovering = recoveringUntil != null && recoveringUntil.isAfter(Instant.now())

    AnimatedVisibility(
        visible = isRecovering,
        enter = fadeIn(),
        exit = fadeOut()
    ) {
        if (recoveringUntil != null) {
            RecoveryBarContent(
                recoveringUntil = recoveringUntil,
                recoveryDurationSeconds = recoveryDurationSeconds,
                modifier = modifier
            )
        }
    }
}

@Composable
private fun RecoveryBarContent(
    recoveringUntil: Instant,
    recoveryDurationSeconds: Long,
    modifier: Modifier = Modifier
) {
    var remainingSeconds by remember(recoveringUntil) {
        mutableStateOf(Duration.between(Instant.now(), recoveringUntil).seconds.coerceAtLeast(0))
    }

    LaunchedEffect(recoveringUntil) {
        while (true) {
            val remaining = Duration.between(Instant.now(), recoveringUntil).seconds
            remainingSeconds = remaining.coerceAtLeast(0)
            if (remaining <= 0) break
            delay(1000)
        }
    }

    val elapsedFraction = (1f - (remainingSeconds.toFloat() / recoveryDurationSeconds.toFloat())).coerceIn(0f, 1f)
    val heartColor = lerp(Color(0xFFB2453B), Color(0xFF5FAE68), elapsedFraction) // red -> green as recovery progresses

    Row(
        modifier = modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surface)
            .padding(horizontal = 16.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = Icons.Filled.Favorite,
            contentDescription = "Recovering",
            tint = heartColor,
            modifier = Modifier.size(18.dp)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = "Recovering — " + formatSeconds(remainingSeconds) + " remaining",
            style = MaterialTheme.typography.labelSmall
        )
    }
}

private fun formatSeconds(totalSeconds: Long): String {
    val minutes = totalSeconds / 60
    val seconds = totalSeconds % 60
    return String.format("%d:%02d", minutes, seconds)
}
