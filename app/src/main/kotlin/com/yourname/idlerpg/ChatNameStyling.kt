package com.yourname.idlerpg.ui.components

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shadow
import androidx.compose.ui.graphics.TileMode
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.withStyle
import com.yourname.idlerpg.BadgeEffect
import com.yourname.idlerpg.ChatCosmeticCatalog
import kotlin.math.sin

// =========================================================
// CHAT NAME STYLING - titles + badge effects
// A chat line renders as:  [Title] Name: message
//   - Title: bold, single flat color (no animation).
//   - Name: optionally painted with a badge effect. The effect is a
//     SpanStyle applied to the NAME ONLY, so it layers over whatever
//     global text effect the viewer has chosen without touching the
//     app-wide Typography. Every badge effect is separate from (and
//     never reuses) the Settings text-effect modes.
// Gradients use absolute pixel offsets with a repeating tile, so the
// pattern flows across the name regardless of where it sits in the line.
// =========================================================

private const val BADGE_LOOP_MS = 3200

@Composable
fun rememberBadgePhase(): Float {
    val transition = rememberInfiniteTransition(label = "chatBadgePhase")
    val phase by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = BADGE_LOOP_MS, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "chatBadgePhaseValue"
    )
    return phase
}

// A repeating horizontal gradient that scrolls as phase goes 0 -> 1. The first
// color is appended at the end so the tile loops seamlessly.
private fun flowingBrush(colors: List<Color>, phase: Float, period: Float): Brush {
    val shift = (phase % 1f) * period
    return Brush.linearGradient(
        colors = colors + colors.first(),
        start = Offset(shift, 0f),
        end = Offset(shift + period, 0f),
        tileMode = TileMode.Repeated
    )
}

fun badgeSpanStyle(effect: BadgeEffect, phase: Float): SpanStyle {
    val twoPi = (2.0 * Math.PI).toFloat()
    val pulse = (sin(phase * twoPi) + 1f) / 2f
    return when (effect) {
        BadgeEffect.RAINBOW -> SpanStyle(
            brush = flowingBrush(
                listOf(
                    Color(0xFFFF3B3B), Color(0xFFFF9F1C), Color(0xFFFFEC3D), Color(0xFF3DDC84),
                    Color(0xFF29B6F6), Color(0xFF7C4DFF), Color(0xFFE040FB)
                ),
                phase, 420f
            ),
            fontWeight = FontWeight.Bold
        )
        BadgeEffect.GILDED -> SpanStyle(
            brush = flowingBrush(
                listOf(Color(0xFFB8860B), Color(0xFFFFE27A), Color(0xFFFFF8DC), Color(0xFFFFE27A), Color(0xFFB8860B)),
                phase, 360f
            ),
            fontWeight = FontWeight.Bold
        )
        BadgeEffect.INFERNO -> {
            val flicker = (sin(phase * twoPi * 3f) + 1f) / 2f
            SpanStyle(
                brush = flowingBrush(
                    listOf(Color(0xFFFF3B00), Color(0xFFFF9A00), Color(0xFFFFE066), Color(0xFFFF9A00)),
                    (phase * 2f) % 1f, 300f
                ),
                fontWeight = FontWeight.Bold,
                shadow = Shadow(color = Color(0xFFFF3B00), blurRadius = 6f + 8f * flicker)
            )
        }
        BadgeEffect.FROSTBITE -> SpanStyle(
            brush = flowingBrush(
                listOf(Color(0xFF9BE7FF), Color(0xFFFFFFFF), Color(0xFF4FC3F7), Color(0xFFFFFFFF), Color(0xFF9BE7FF)),
                phase, 380f
            ),
            fontWeight = FontWeight.Bold,
            shadow = Shadow(color = Color(0xFF00B8D4), blurRadius = 6f)
        )
        BadgeEffect.NEON_PULSE -> SpanStyle(
            color = Color(0xFF00F5FF),
            fontWeight = FontWeight.Bold,
            shadow = Shadow(color = Color(0xFF00F5FF), blurRadius = 4f + 14f * pulse)
        )
        BadgeEffect.AURORA -> SpanStyle(
            brush = flowingBrush(
                listOf(Color(0xFF00FFA3), Color(0xFF03E1FF), Color(0xFFB388FF)),
                phase, 600f
            ),
            fontWeight = FontWeight.Bold
        )
        BadgeEffect.STORMCALL -> {
            val flash = ((phase * 2f) % 1f) < 0.08f
            if (flash) {
                SpanStyle(
                    color = Color.White,
                    fontWeight = FontWeight.Bold,
                    shadow = Shadow(color = Color(0xFFBFD7FF), blurRadius = 16f)
                )
            } else {
                SpanStyle(
                    color = Color(0xFF8EA8FF),
                    fontWeight = FontWeight.Bold,
                    shadow = Shadow(color = Color(0xFF3D5AFE), blurRadius = 4f)
                )
            }
        }
        BadgeEffect.BLOOD_MOON -> SpanStyle(
            brush = flowingBrush(
                listOf(Color(0xFF9E1B1B), Color(0xFFE01B1B), Color(0xFFFF5A5A), Color(0xFFE01B1B)),
                phase, 400f
            ),
            fontWeight = FontWeight.Bold,
            shadow = Shadow(color = Color(0xFF8B0000), blurRadius = 4f + 8f * pulse)
        )
        BadgeEffect.TOXIC -> SpanStyle(
            brush = flowingBrush(
                listOf(Color(0xFF39FF14), Color(0xFFB6FF00), Color(0xFF39FF14)),
                (phase * 2f) % 1f, 300f
            ),
            fontWeight = FontWeight.Bold,
            shadow = Shadow(color = Color(0xFF1B5E20), blurRadius = 6f)
        )
        BadgeEffect.VOID -> SpanStyle(
            brush = flowingBrush(
                listOf(Color(0xFF7B2CBF), Color(0xFFC77DFF), Color(0xFFE0AAFF), Color(0xFFC77DFF)),
                phase, 500f
            ),
            fontWeight = FontWeight.Bold,
            shadow = Shadow(color = Color(0xFF5A189A), blurRadius = 4f + 8f * pulse)
        )
    }
}

// The full rendered chat line: "[Title] Name: message". Used by both the
// collapsed banner preview and the expanded message rows.
@Composable
fun chatLineText(message: ChatMessageUi): AnnotatedString {
    val title = message.senderTitleId?.let { ChatCosmeticCatalog.find(it) }
    val effect = message.senderBadgeId?.let { ChatCosmeticCatalog.find(it) }?.badgeEffect
    val phase = if (effect != null) rememberBadgePhase() else 0f
    return buildAnnotatedString {
        if (title != null) {
            withStyle(SpanStyle(color = Color(title.colorArgb), fontWeight = FontWeight.Bold)) {
                append("[" + title.displayName + "] ")
            }
        }
        if (effect != null) {
            withStyle(badgeSpanStyle(effect, phase)) {
                append(message.senderName)
            }
        } else {
            append(message.senderName)
        }
        append(": " + message.content)
    }
}

// Just a styled name, for previews in the badge shop.
@Composable
fun badgePreviewText(name: String, effect: BadgeEffect): AnnotatedString {
    val phase = rememberBadgePhase()
    return buildAnnotatedString {
        withStyle(badgeSpanStyle(effect, phase)) {
            append(name)
        }
    }
}
