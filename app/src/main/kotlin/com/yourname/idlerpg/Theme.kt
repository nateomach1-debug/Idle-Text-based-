package com.yourname.idlerpg.ui.theme

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.compositionLocalOf
import androidx.compose.runtime.getValue
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shadow
import androidx.compose.ui.graphics.TileMode
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

// =========================================================
// TEXT EFFECT MODE
// Drives how the player's chosen text color(s) render, on top
// of the existing solid-color-override system below. SOLID is
// the default/free behavior (unchanged). The other 5 modes are
// only applied once a custom text color has been set - see
// resolvedTextColorAndBrush() and buildIdleRpgTypography().
// =========================================================

enum class TextEffectMode { SOLID, GRADIENT, PULSE, SHIMMER, COLOR_CYCLE, WAVE }

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

private fun lerpTowardWhite(color: Color, fraction: Float): Color = Color(
    red = color.red + (1f - color.red) * fraction,
    green = color.green + (1f - color.green) * fraction,
    blue = color.blue + (1f - color.blue) * fraction,
    alpha = color.alpha
)

// Resolves a base color (+ optional second color) and the current
// TextEffectMode into a (Color, Brush?) pair for use on a TextStyle.
// When brush is non-null, Compose renders the brush and ignores the
// plain color entirely - only GRADIENT/SHIMMER/WAVE return a brush.
// PULSE/COLOR_CYCLE instead animate the plain Color itself, since
// they don't need a spatial gradient. animationPhase cycles 0f..1f
// continuously and is only meaningful for the 4 animated modes.
private fun resolvedTextColorAndBrush(
    base: Color,
    secondary: Color?,
    mode: TextEffectMode,
    animationPhase: Float
): Pair<Color, Brush?> = when (mode) {
    TextEffectMode.SOLID -> base to null
    TextEffectMode.GRADIENT -> base to Brush.linearGradient(listOf(base, secondary ?: base))
    TextEffectMode.PULSE -> {
        val alpha = 0.12f + 0.88f * ((kotlin.math.sin(animationPhase * 2 * Math.PI).toFloat() + 1f) / 2f)
        base.copy(alpha = alpha) to null
    }
    TextEffectMode.SHIMMER -> {
        val highlight = lerpTowardWhite(base, 1f)
        val sweep = (animationPhase % 1f) * 3000f - 1000f
        base to Brush.linearGradient(
            colors = listOf(base, highlight, base),
            start = Offset(sweep - 500f, 0f),
            end = Offset(sweep + 500f, 0f)
        )
    }
    TextEffectMode.COLOR_CYCLE -> {
        val hsv = FloatArray(3)
        android.graphics.Color.colorToHSV(base.toArgb(), hsv)
        val cycledHue = (hsv[0] + animationPhase * 360f) % 360f
        Color(android.graphics.Color.HSVToColor(floatArrayOf(cycledHue, 1f, 1f))) to null
    }
    TextEffectMode.WAVE -> {
        val sweep = (animationPhase % 1f) * 2000f
        base to Brush.linearGradient(
            colors = listOf(base, secondary ?: base, base),
            start = Offset(sweep - 600f, 0f),
            end = Offset(sweep + 600f, 0f),
            tileMode = TileMode.Repeated
        )
    }
}

private fun styledText(
    fontFamily: FontFamily,
    fontWeight: FontWeight,
    fontSize: androidx.compose.ui.unit.TextUnit,
    color: Color,
    brush: Brush?,
    shadow: Shadow?
): TextStyle = if (brush != null) {
    TextStyle(fontFamily = fontFamily, fontWeight = fontWeight, fontSize = fontSize, brush = brush, shadow = shadow)
} else {
    TextStyle(fontFamily = fontFamily, fontWeight = fontWeight, fontSize = fontSize, color = color, shadow = shadow)
}

private fun buildIdleRpgTypography(
    textColorOverride: Color?,
    outlineEnabled: Boolean,
    outlineColor: Color,
    effectMode: TextEffectMode = TextEffectMode.SOLID,
    secondaryColor: Color? = null,
    animationPhase: Float = 0f
): Typography {
    val basePrimary = textColorOverride ?: TextPrimary
    val baseSecondary = textColorOverride ?: TextSecondary
    val shadow = outlineShadow(outlineEnabled, outlineColor)

    // Gradient/animated effects only kick in once the player has actually
    // chosen a custom text color - the default (un-customized) theme stays
    // plain SOLID, same gating as textColorOverride itself above.
    val effectiveMode = if (textColorOverride == null) TextEffectMode.SOLID else effectMode
    val (primary, primaryBrush) = resolvedTextColorAndBrush(basePrimary, secondaryColor, effectiveMode, animationPhase)
    val (secondary, secondaryBrush) = resolvedTextColorAndBrush(baseSecondary, secondaryColor, effectiveMode, animationPhase)

    return Typography(
        displayLarge = styledText(HeaderFont, FontWeight.Bold, 40.sp, primary, primaryBrush, shadow),
        displayMedium = styledText(HeaderFont, FontWeight.Bold, 34.sp, primary, primaryBrush, shadow),
        displaySmall = styledText(HeaderFont, FontWeight.Bold, 28.sp, primary, primaryBrush, shadow),
        headlineLarge = styledText(HeaderFont, FontWeight.Bold, 24.sp, primary, primaryBrush, shadow),
        headlineMedium = styledText(HeaderFont, FontWeight.Bold, 22.sp, primary, primaryBrush, shadow),
        headlineSmall = styledText(HeaderFont, FontWeight.SemiBold, 19.sp, primary, primaryBrush, shadow),
        titleLarge = styledText(HeaderFont, FontWeight.SemiBold, 19.sp, primary, primaryBrush, shadow),
        titleMedium = styledText(HeaderFont, FontWeight.SemiBold, 17.sp, primary, primaryBrush, shadow),
        titleSmall = styledText(HeaderFont, FontWeight.SemiBold, 15.sp, primary, primaryBrush, shadow),
        bodyLarge = styledText(BodyFont, FontWeight.Normal, 16.sp, primary, primaryBrush, shadow),
        bodyMedium = styledText(BodyFont, FontWeight.Normal, 15.sp, primary, primaryBrush, shadow),
        bodySmall = styledText(BodyFont, FontWeight.Normal, 13.sp, primary, primaryBrush, shadow),
        labelLarge = styledText(BodyFont, FontWeight.Medium, 13.sp, secondary, secondaryBrush, shadow),
        labelMedium = styledText(BodyFont, FontWeight.Medium, 12.sp, secondary, secondaryBrush, shadow),
        labelSmall = styledText(BodyFont, FontWeight.Medium, 12.sp, secondary, secondaryBrush, shadow)
    )
}

@Composable
fun IdleRpgTheme(
    textColorOverride: Color? = null,
    outlineEnabled: Boolean = false,
    outlineColor: Color = Color.Black,
    effectMode: TextEffectMode = TextEffectMode.SOLID,
    secondaryColor: Color? = null,
    content: @Composable () -> Unit
) {
    val isAnimatedEffect = effectMode == TextEffectMode.PULSE ||
        effectMode == TextEffectMode.SHIMMER ||
        effectMode == TextEffectMode.COLOR_CYCLE ||
        effectMode == TextEffectMode.WAVE

    val animationPhase: Float = if (isAnimatedEffect) {
        val transition = rememberInfiniteTransition(label = "textEffectTransition")
        val phase by transition.animateFloat(
            initialValue = 0f,
            targetValue = 1f,
            animationSpec = infiniteRepeatable(
                animation = tween(durationMillis = 2600, easing = LinearEasing),
                repeatMode = RepeatMode.Restart
            ),
            label = "textEffectPhase"
        )
        phase
    } else {
        0f
    }

    CompositionLocalProvider(LocalTextColorOverride provides textColorOverride) {
        MaterialTheme(
            colorScheme = IdleRpgDarkColors,
            typography = buildIdleRpgTypography(textColorOverride, outlineEnabled, outlineColor, effectMode, secondaryColor, animationPhase),
            content = content
        )
    }
}
