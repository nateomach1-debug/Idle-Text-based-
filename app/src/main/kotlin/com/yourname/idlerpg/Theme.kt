package com.yourname.idlerpg.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

// =========================================================
// COLOR PALETTE
// Dark charcoal background, parchment-gold primary accent,
// muted teal secondary, deep red for danger/combat states.
// =========================================================

val CharcoalBackground = Color(0xFF16141B)
val CharcoalSurface = Color(0xFF201D26)
val ParchmentGold = Color(0xFFD4AF6A)
val MutedTeal = Color(0xFF4F8C86)
val DeepRed = Color(0xFFB2453B)
val TextPrimary = Color(0xFFEDE8DD)
val TextSecondary = Color(0xFFA39E93)

private val IdleRpgDarkColors = darkColorScheme(
    primary = ParchmentGold,
    secondary = MutedTeal,
    error = DeepRed,
    background = CharcoalBackground,
    surface = CharcoalSurface,
    onPrimary = CharcoalBackground,
    onBackground = TextPrimary,
    onSurface = TextPrimary
)

// =========================================================
// TYPOGRAPHY
// Bold serif for headers, clean sans-serif for body/data.
// =========================================================

private val HeaderFont = FontFamily.Serif
private val BodyFont = FontFamily.SansSerif

val IdleRpgTypography = Typography(
    headlineMedium = TextStyle(
        fontFamily = HeaderFont,
        fontWeight = FontWeight.Bold,
        fontSize = 22.sp,
        color = TextPrimary
    ),
    titleMedium = TextStyle(
        fontFamily = HeaderFont,
        fontWeight = FontWeight.SemiBold,
        fontSize = 17.sp,
        color = TextPrimary
    ),
    bodyMedium = TextStyle(
        fontFamily = BodyFont,
        fontWeight = FontWeight.Normal,
        fontSize = 15.sp,
        color = TextPrimary
    ),
    labelSmall = TextStyle(
        fontFamily = BodyFont,
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        color = TextSecondary
    )
)

@Composable
fun IdleRpgTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = IdleRpgDarkColors,
        typography = IdleRpgTypography,
        content = content
    )
}
