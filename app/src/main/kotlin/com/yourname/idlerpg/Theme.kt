package com.yourname.idlerpg.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.compositionLocalOf
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shadow
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

// =========================================================
// PER-SKILL THEME COLORS
// Each is a single named constant, same pattern as the base
// palette above - easy to retune individually after testing
// on-device, no need to touch anything else.
// =========================================================

val MiningStone = Color(0xFF7D8188)
val WoodcuttingGreen = Color(0xFF4C6B3F)
val FishingBlue = Color(0xFF3E6E9E)
val FarmingTan = Color(0xFF8A7B4E)
val ThievingPurple = Color(0xFF5B3E75)
val SmithingOrange = Color(0xFFB5621F)
val CookingEmber = Color(0xFF8C3B2E)
val CraftingViolet = Color(0xFF6E4B8A)
val FletchingOlive = Color(0xFF6B6B3A)
val AlchemyToxic = Color(0xFF4E8C4A)
val MagicArcane = Color(0xFF5A4FCF)

// How strongly the skill color blends into the screen background.
// Placeholder value, same spirit as other tunable placeholders in
// this project - adjust after seeing it live.
private const val SKILL_THEME_BLEND_ALPHA = 0.35f

// Combat skills (Attack/Strength/Defense/Prayer/Archery) intentionally
// return null - they share the Combat screen rather than having their
// own detail page, and keep the existing deep-red danger theme.
fun skillThemeColor(skillId: String): Color? = when (skillId) {
    "MINING" -> MiningStone
    "WOODCUTTING" -> WoodcuttingGreen
    "FISHING" -> FishingBlue
    "FARMING" -> FarmingTan
    "THIEVING" -> ThievingPurple
    "SMITHING" -> SmithingOrange
    "COOKING" -> CookingEmber
    "CRAFTING" -> CraftingViolet
    "FLETCHING" -> FletchingOlive
    "ALCHEMY" -> AlchemyToxic
    "MAGIC" -> MagicArcane
    else -> null
}

fun skillThemeBackground(skillId: String): Color? =
    skillThemeColor(skillId)?.copy(alpha = SKILL_THEME_BLEND_ALPHA)

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
// Parameterized by the Settings tab's text-color-override and
// outline settings so every style updates together from one
// place, rather than touching each Text() call site.
// =========================================================

private val HeaderFont = FontFamily.Serif
private val BodyFont = FontFamily.SansSerif

// Settings-driven text color override, available to any composable
// via overrideColor() below - covers the handful of Text() calls
// elsewhere in the app that pass their own explicit color= param
// (which bypasses Typography's embedded color entirely).
val LocalTextColorOverride = compositionLocalOf<Color?> { null }

@Composable
fun overrideColor(fallback: Color): Color = LocalTextColorOverride.current ?: fallback

private fun outlineShadow(enabled: Boolean, color: Color): Shadow? =
    if (enabled) Shadow(color = color, offset = Offset.Zero, blurRadius = 8f) else null

private fun buildIdleRpgTypography(
    textColorOverride: Color?,
    outlineEnabled: Boolean,
    outlineColor: Color
): Typography {
    val primary = textColorOverride ?: TextPrimary
    val secondary = textColorOverride ?: TextSecondary
    val shadow = outlineShadow(outlineEnabled, outlineColor)
    return Typography(
        displayLarge = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.Bold, fontSize = 40.sp, color = primary, shadow = shadow),
        displayMedium = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.Bold, fontSize = 34.sp, color = primary, shadow = shadow),
        displaySmall = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.Bold, fontSize = 28.sp, color = primary, shadow = shadow),
        headlineLarge = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.Bold, fontSize = 24.sp, color = primary, shadow = shadow),
        headlineMedium = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.Bold, fontSize = 22.sp, color = primary, shadow = shadow),
        headlineSmall = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.SemiBold, fontSize = 19.sp, color = primary, shadow = shadow),
        titleLarge = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.SemiBold, fontSize = 19.sp, color = primary, shadow = shadow),
        titleMedium = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.SemiBold, fontSize = 17.sp, color = primary, shadow = shadow),
        titleSmall = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.SemiBold, fontSize = 15.sp, color = primary, shadow = shadow),
        bodyLarge = TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Normal, fontSize = 16.sp, color = primary, shadow = shadow),
        bodyMedium = TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Normal, fontSize = 15.sp, color = primary, shadow = shadow),
        bodySmall = TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Normal, fontSize = 13.sp, color = primary, shadow = shadow),
        labelLarge = TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Medium, fontSize = 13.sp, color = secondary, shadow = shadow),
        labelMedium = TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Medium, fontSize = 12.sp, color = secondary, shadow = shadow),
        labelSmall = TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Medium, fontSize = 12.sp, color = secondary, shadow = shadow)
    )
}

@Composable
fun IdleRpgTheme(
    textColorOverride: Color? = null,
    outlineEnabled: Boolean = false,
    outlineColor: Color = Color.Black,
    content: @Composable () -> Unit
) {
    CompositionLocalProvider(LocalTextColorOverride provides textColorOverride) {
        MaterialTheme(
            colorScheme = IdleRpgDarkColors,
            typography = buildIdleRpgTypography(textColorOverride, outlineEnabled, outlineColor),
            content = content
        )
    }
}
