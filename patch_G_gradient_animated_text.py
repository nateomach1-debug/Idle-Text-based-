import sys

BASE = "app/src/main/kotlin/com/yourname/idlerpg/"
THEME = BASE + "Theme.kt"


def guarded_replace(path, old, new, label):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    if new in text:
        print(f"SKIP (already applied): {label} ({path})")
        return True

    count = text.count(old)
    if count == 1:
        text = text.replace(old, new)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"OK: {label} ({path})")
        return True
    elif count == 0:
        print(f"FAIL (old_str not found, new_str not found either): {label} ({path})")
        return False
    else:
        print(f"FAIL (old_str matched {count} times, expected 1): {label} ({path})")
        return False


def check_braces(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    opens = text.count("{")
    closes = text.count("}")
    ok = opens == closes
    print(f"{'Brace check OK' if ok else 'WARNING: brace mismatch'}: {path} ({{ = {opens}, }} = {closes})")
    return ok


results = []

# ===========================================================
# 1. Theme.kt - imports + TextEffectMode enum
# ===========================================================
old = '''package com.yourname.idlerpg.ui.theme

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
import androidx.compose.ui.unit.sp'''
new = '''package com.yourname.idlerpg.ui.theme

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

enum class TextEffectMode { SOLID, GRADIENT, PULSE, SHIMMER, COLOR_CYCLE, WAVE }'''
results.append(guarded_replace(THEME, old, new, "Theme.kt imports + TextEffectMode enum"))

# ===========================================================
# 2. Theme.kt - resolvedTextColorAndBrush + lerpTowardWhite helpers
# ===========================================================
old = '''private fun outlineShadow(enabled: Boolean, color: Color): Shadow? =
    if (enabled) Shadow(color = color, offset = Offset.Zero, blurRadius = 8f) else null'''
new = '''private fun outlineShadow(enabled: Boolean, color: Color): Shadow? =
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
        val alpha = 0.55f + 0.45f * ((kotlin.math.sin(animationPhase * 2 * Math.PI).toFloat() + 1f) / 2f)
        base.copy(alpha = alpha) to null
    }
    TextEffectMode.SHIMMER -> {
        val highlight = lerpTowardWhite(base, 0.85f)
        val sweep = (animationPhase % 1f) * 600f - 300f
        base to Brush.linearGradient(
            colors = listOf(base, highlight, base),
            start = Offset(sweep - 150f, 0f),
            end = Offset(sweep + 150f, 0f)
        )
    }
    TextEffectMode.COLOR_CYCLE -> {
        val hsv = FloatArray(3)
        android.graphics.Color.colorToHSV(base.toArgb(), hsv)
        val cycledHue = (hsv[0] + animationPhase * 360f) % 360f
        Color(android.graphics.Color.HSVToColor(floatArrayOf(cycledHue, hsv[1].coerceAtLeast(0.5f), hsv[2].coerceAtLeast(0.7f)))) to null
    }
    TextEffectMode.WAVE -> {
        val sweep = (animationPhase % 1f) * 400f
        base to Brush.linearGradient(
            colors = listOf(base, secondary ?: base, base),
            start = Offset(sweep - 200f, 0f),
            end = Offset(sweep + 200f, 0f),
            tileMode = TileMode.Repeated
        )
    }
}'''
results.append(guarded_replace(THEME, old, new, "Theme.kt resolvedTextColorAndBrush helper"))

# ===========================================================
# 3. Theme.kt - buildIdleRpgTypography extended with brush support
# ===========================================================
old = '''private fun buildIdleRpgTypography(
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
}'''
new = '''private fun buildIdleRpgTypography(
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
        displayLarge = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.Bold, fontSize = 40.sp, color = primary, brush = primaryBrush, shadow = shadow),
        displayMedium = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.Bold, fontSize = 34.sp, color = primary, brush = primaryBrush, shadow = shadow),
        displaySmall = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.Bold, fontSize = 28.sp, color = primary, brush = primaryBrush, shadow = shadow),
        headlineLarge = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.Bold, fontSize = 24.sp, color = primary, brush = primaryBrush, shadow = shadow),
        headlineMedium = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.Bold, fontSize = 22.sp, color = primary, brush = primaryBrush, shadow = shadow),
        headlineSmall = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.SemiBold, fontSize = 19.sp, color = primary, brush = primaryBrush, shadow = shadow),
        titleLarge = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.SemiBold, fontSize = 19.sp, color = primary, brush = primaryBrush, shadow = shadow),
        titleMedium = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.SemiBold, fontSize = 17.sp, color = primary, brush = primaryBrush, shadow = shadow),
        titleSmall = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.SemiBold, fontSize = 15.sp, color = primary, brush = primaryBrush, shadow = shadow),
        bodyLarge = TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Normal, fontSize = 16.sp, color = primary, brush = primaryBrush, shadow = shadow),
        bodyMedium = TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Normal, fontSize = 15.sp, color = primary, brush = primaryBrush, shadow = shadow),
        bodySmall = TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Normal, fontSize = 13.sp, color = primary, brush = primaryBrush, shadow = shadow),
        labelLarge = TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Medium, fontSize = 13.sp, color = secondary, brush = secondaryBrush, shadow = shadow),
        labelMedium = TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Medium, fontSize = 12.sp, color = secondary, brush = secondaryBrush, shadow = shadow),
        labelSmall = TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Medium, fontSize = 12.sp, color = secondary, brush = secondaryBrush, shadow = shadow)
    )
}'''
results.append(guarded_replace(THEME, old, new, "Theme.kt buildIdleRpgTypography with brush support"))

# ===========================================================
# 4. Theme.kt - IdleRpgTheme drives the animation clock
# ===========================================================
old = '''@Composable
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
}'''
new = '''@Composable
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
}'''
results.append(guarded_replace(THEME, old, new, "Theme.kt IdleRpgTheme animation clock"))

# ===========================================================
# 5. MonetizationSystem.kt - PremiumPreset + catalog extended
# ===========================================================
path = BASE + "MonetizationSystem.kt"
old = '''data class PremiumPreset(
    val id: String,
    val displayName: String,
    val gemCost: Long,
    val textColorArgb: Long,
    val outlineColorArgb: Long
)

object PremiumPresetCatalog {
    val presets = listOf(
        PremiumPreset(id = "preset_ember_glow", displayName = "Ember Glow", gemCost = 150, textColorArgb = 0xFFFFB86CL, outlineColorArgb = 0xFF8B0000L),
        PremiumPreset(id = "preset_arctic_shimmer", displayName = "Arctic Shimmer", gemCost = 150, textColorArgb = 0xFF9AEAFFL, outlineColorArgb = 0xFF00E5FFL),
        PremiumPreset(id = "preset_royal_amethyst", displayName = "Royal Amethyst", gemCost = 150, textColorArgb = 0xFFC77DFFL, outlineColorArgb = 0xFF7209B7L)
    )

    fun find(presetId: String): PremiumPreset? = presets.find { it.id == presetId }
}'''
new = '''data class PremiumPreset(
    val id: String,
    val displayName: String,
    val gemCost: Long,
    val textColorArgb: Long,
    val outlineColorArgb: Long,
    val effectMode: com.yourname.idlerpg.ui.theme.TextEffectMode = com.yourname.idlerpg.ui.theme.TextEffectMode.SOLID,
    val secondaryColorArgb: Long? = null
)

object PremiumPresetCatalog {
    val presets = listOf(
        PremiumPreset(id = "preset_ember_glow", displayName = "Ember Glow", gemCost = 150, textColorArgb = 0xFFFFB86CL, outlineColorArgb = 0xFF8B0000L),
        PremiumPreset(id = "preset_arctic_shimmer", displayName = "Arctic Shimmer", gemCost = 150, textColorArgb = 0xFF9AEAFFL, outlineColorArgb = 0xFF00E5FFL),
        PremiumPreset(id = "preset_royal_amethyst", displayName = "Royal Amethyst", gemCost = 150, textColorArgb = 0xFFC77DFFL, outlineColorArgb = 0xFF7209B7L),
        // Placeholder gem prices, same spirit as other tunable placeholders
        // in this project - adjust after seeing them live.
        PremiumPreset(id = "preset_sunset_gradient", displayName = "Sunset Gradient", gemCost = 200, textColorArgb = 0xFFFF6B35L, outlineColorArgb = 0xFF8B0000L, effectMode = com.yourname.idlerpg.ui.theme.TextEffectMode.GRADIENT, secondaryColorArgb = 0xFFFFD23FL),
        PremiumPreset(id = "preset_pulse_glow", displayName = "Pulse Glow", gemCost = 250, textColorArgb = 0xFF9AEAFFL, outlineColorArgb = 0xFF00E5FFL, effectMode = com.yourname.idlerpg.ui.theme.TextEffectMode.PULSE),
        PremiumPreset(id = "preset_shimmer_silver", displayName = "Shimmer Silver", gemCost = 250, textColorArgb = 0xFFC0C0C0L, outlineColorArgb = 0xFF4A4A4AL, effectMode = com.yourname.idlerpg.ui.theme.TextEffectMode.SHIMMER),
        PremiumPreset(id = "preset_rainbow_cycle", displayName = "Rainbow Cycle", gemCost = 300, textColorArgb = 0xFFFF0000L, outlineColorArgb = 0xFF000000L, effectMode = com.yourname.idlerpg.ui.theme.TextEffectMode.COLOR_CYCLE),
        PremiumPreset(id = "preset_ocean_wave", displayName = "Ocean Wave", gemCost = 250, textColorArgb = 0xFF00B4D8L, outlineColorArgb = 0xFF03045EL, effectMode = com.yourname.idlerpg.ui.theme.TextEffectMode.WAVE, secondaryColorArgb = 0xFF90E0EFL)
    )

    fun find(presetId: String): PremiumPreset? = presets.find { it.id == presetId }
}'''
results.append(guarded_replace(path, old, new, "MonetizationSystem.kt PremiumPreset + 5 new presets"))

# ===========================================================
# 6. GameViewModel.kt - textEffectMode / textSecondaryColor state
# ===========================================================
path = BASE + "GameViewModel.kt"
old = '''    fun setTextOutlineColor(color: Color) {
        _textOutlineColor.value = color
        settingsPrefs.edit().putInt("text_outline_color", color.toArgb()).apply()
    }

    fun fetchLeaderboard(category: LeaderboardCategory) {'''
new = '''    fun setTextOutlineColor(color: Color) {
        _textOutlineColor.value = color
        settingsPrefs.edit().putInt("text_outline_color", color.toArgb()).apply()
    }

    private val _textEffectMode = MutableStateFlow(
        com.yourname.idlerpg.ui.theme.TextEffectMode.valueOf(
            settingsPrefs.getString("text_effect_mode", com.yourname.idlerpg.ui.theme.TextEffectMode.SOLID.name)
                ?: com.yourname.idlerpg.ui.theme.TextEffectMode.SOLID.name
        )
    )
    val textEffectMode: StateFlow<com.yourname.idlerpg.ui.theme.TextEffectMode> = _textEffectMode.asStateFlow()

    private val _textSecondaryColor = MutableStateFlow<Color?>(
        if (settingsPrefs.contains("text_secondary_color")) Color(settingsPrefs.getInt("text_secondary_color", 0)) else null
    )
    val textSecondaryColor: StateFlow<Color?> = _textSecondaryColor.asStateFlow()

    fun setTextEffectMode(mode: com.yourname.idlerpg.ui.theme.TextEffectMode) {
        _textEffectMode.value = mode
        settingsPrefs.edit().putString("text_effect_mode", mode.name).apply()
    }

    fun setTextSecondaryColor(color: Color?) {
        _textSecondaryColor.value = color
        if (color == null) {
            settingsPrefs.edit().remove("text_secondary_color").apply()
        } else {
            settingsPrefs.edit().putInt("text_secondary_color", color.toArgb()).apply()
        }
    }

    fun fetchLeaderboard(category: LeaderboardCategory) {'''
results.append(guarded_replace(path, old, new, "GameViewModel.kt textEffectMode/textSecondaryColor state"))

# ===========================================================
# 7. SettingsScreen.kt - signature extended
# ===========================================================
path = BASE + "SettingsScreen.kt"
old = '''@Composable
fun SettingsScreen(
    textColorOverride: Color?,
    outlineEnabled: Boolean,
    outlineColor: Color,
    onTextColorChanged: (Color?) -> Unit,
    onOutlineEnabledChanged: (Boolean) -> Unit,
    onOutlineColorChanged: (Color) -> Unit,
    premiumCurrency: Long = 0,
    unlockedPresets: Set<String> = emptySet(),
    onPurchaseBundle: (String) -> Unit = {},
    onPurchasePreset: (String) -> Unit = {},
    modifier: Modifier = Modifier
) {'''
new = '''@Composable
fun SettingsScreen(
    textColorOverride: Color?,
    outlineEnabled: Boolean,
    outlineColor: Color,
    onTextColorChanged: (Color?) -> Unit,
    onOutlineEnabledChanged: (Boolean) -> Unit,
    onOutlineColorChanged: (Color) -> Unit,
    premiumCurrency: Long = 0,
    unlockedPresets: Set<String> = emptySet(),
    onPurchaseBundle: (String) -> Unit = {},
    onPurchasePreset: (String) -> Unit = {},
    effectMode: com.yourname.idlerpg.ui.theme.TextEffectMode = com.yourname.idlerpg.ui.theme.TextEffectMode.SOLID,
    secondaryColor: Color? = null,
    onEffectModeChanged: (com.yourname.idlerpg.ui.theme.TextEffectMode) -> Unit = {},
    onSecondaryColorChanged: (Color?) -> Unit = {},
    modifier: Modifier = Modifier
) {'''
results.append(guarded_replace(path, old, new, "SettingsScreen.kt signature extended"))

# ===========================================================
# 8. SettingsScreen.kt - PresetCard onApply also sets effect + secondary color
# ===========================================================
old = '''                onApply = {
                    onTextColorChanged(Color(preset.textColorArgb.toInt()))
                    onOutlineEnabledChanged(true)
                    onOutlineColorChanged(Color(preset.outlineColorArgb.toInt()))
                }'''
new = '''                onApply = {
                    onTextColorChanged(Color(preset.textColorArgb.toInt()))
                    onOutlineEnabledChanged(true)
                    onOutlineColorChanged(Color(preset.outlineColorArgb.toInt()))
                    onEffectModeChanged(preset.effectMode)
                    onSecondaryColorChanged(preset.secondaryColorArgb?.let { Color(it.toInt()) })
                }'''
results.append(guarded_replace(path, old, new, "SettingsScreen.kt PresetCard onApply sets effect mode"))

# ===========================================================
# 9. SettingsScreen.kt - new Text Effect section
# ===========================================================
old = '''        Button(onClick = { onTextColorChanged(null) }) {
            Text("Reset to Default")
        }

        Spacer(modifier = Modifier.height(28.dp))

        Row(modifier = Modifier.fillMaxWidth()) {
            Text(text = "Text Outline", style = MaterialTheme.typography.titleMedium, modifier = Modifier.weight(1f))'''
new = '''        Button(onClick = { onTextColorChanged(null) }) {
            Text("Reset to Default")
        }

        Spacer(modifier = Modifier.height(28.dp))

        Text(text = "Text Effect", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(4.dp))
        Text(text = "Applies once you've set a custom Text Color above.", style = MaterialTheme.typography.labelSmall)
        Spacer(modifier = Modifier.height(8.dp))
        com.yourname.idlerpg.ui.theme.TextEffectMode.entries.forEach { mode ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 2.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(text = textEffectModeLabel(mode), style = MaterialTheme.typography.bodyMedium)
                if (mode == effectMode) {
                    Text(text = "Selected", style = MaterialTheme.typography.labelSmall)
                } else {
                    Button(onClick = { onEffectModeChanged(mode) }) {
                        Text("Select")
                    }
                }
            }
        }
        if (effectMode == com.yourname.idlerpg.ui.theme.TextEffectMode.GRADIENT || effectMode == com.yourname.idlerpg.ui.theme.TextEffectMode.WAVE) {
            Spacer(modifier = Modifier.height(8.dp))
            Text(text = "Second Color", style = MaterialTheme.typography.bodyMedium)
            Spacer(modifier = Modifier.height(4.dp))
            RgbHexColorPicker(
                color = secondaryColor ?: Color(0xFFFFFFFF),
                onColorChange = { onSecondaryColorChanged(it) }
            )
        }

        Spacer(modifier = Modifier.height(28.dp))

        Row(modifier = Modifier.fillMaxWidth()) {
            Text(text = "Text Outline", style = MaterialTheme.typography.titleMedium, modifier = Modifier.weight(1f))'''
results.append(guarded_replace(path, old, new, "SettingsScreen.kt new Text Effect section"))

# ===========================================================
# 10. SettingsScreen.kt - textEffectModeLabel helper (appended after LabeledSlider)
# ===========================================================
old = '''@Composable
private fun LabeledSlider(label: String, value: Float, onValueChange: (Float) -> Unit) {
    Row(modifier = Modifier.fillMaxWidth()) {
        Text(text = label, modifier = Modifier.padding(end = 8.dp))
        Slider(
            value = value,
            onValueChange = onValueChange,
            valueRange = 0f..255f,
            modifier = Modifier.weight(1f)
        )
        Text(text = value.toInt().toString(), modifier = Modifier.padding(start = 8.dp))
    }
}'''
new = '''@Composable
private fun LabeledSlider(label: String, value: Float, onValueChange: (Float) -> Unit) {
    Row(modifier = Modifier.fillMaxWidth()) {
        Text(text = label, modifier = Modifier.padding(end = 8.dp))
        Slider(
            value = value,
            onValueChange = onValueChange,
            valueRange = 0f..255f,
            modifier = Modifier.weight(1f)
        )
        Text(text = value.toInt().toString(), modifier = Modifier.padding(start = 8.dp))
    }
}

private fun textEffectModeLabel(mode: com.yourname.idlerpg.ui.theme.TextEffectMode): String = when (mode) {
    com.yourname.idlerpg.ui.theme.TextEffectMode.SOLID -> "Solid"
    com.yourname.idlerpg.ui.theme.TextEffectMode.GRADIENT -> "Gradient"
    com.yourname.idlerpg.ui.theme.TextEffectMode.PULSE -> "Pulse"
    com.yourname.idlerpg.ui.theme.TextEffectMode.SHIMMER -> "Shimmer"
    com.yourname.idlerpg.ui.theme.TextEffectMode.COLOR_CYCLE -> "Color Cycle"
    com.yourname.idlerpg.ui.theme.TextEffectMode.WAVE -> "Wave"
}'''
results.append(guarded_replace(path, old, new, "SettingsScreen.kt textEffectModeLabel helper"))

# ===========================================================
# 11. MainActivity.kt - top setContent IdleRpgTheme call site
# ===========================================================
path = BASE + "MainActivity.kt"
old = '''            val textColorOverride by gameViewModel.textColorOverride.collectAsState()
            val textOutlineEnabled by gameViewModel.textOutlineEnabled.collectAsState()
            val textOutlineColor by gameViewModel.textOutlineColor.collectAsState()
            IdleRpgTheme(
                textColorOverride = textColorOverride,
                outlineEnabled = textOutlineEnabled,
                outlineColor = textOutlineColor
            ) {'''
new = '''            val textColorOverride by gameViewModel.textColorOverride.collectAsState()
            val textOutlineEnabled by gameViewModel.textOutlineEnabled.collectAsState()
            val textOutlineColor by gameViewModel.textOutlineColor.collectAsState()
            val textEffectMode by gameViewModel.textEffectMode.collectAsState()
            val textSecondaryColor by gameViewModel.textSecondaryColor.collectAsState()
            IdleRpgTheme(
                textColorOverride = textColorOverride,
                outlineEnabled = textOutlineEnabled,
                outlineColor = textOutlineColor,
                effectMode = textEffectMode,
                secondaryColor = textSecondaryColor
            ) {'''
results.append(guarded_replace(path, old, new, "MainActivity.kt top IdleRpgTheme call site"))

# ===========================================================
# 12. MainActivity.kt - SETTINGS destination SettingsScreen( call site
# ===========================================================
old = '''                                val settingsTextColorOverride by gameViewModel.textColorOverride.collectAsState()
                                val settingsOutlineEnabled by gameViewModel.textOutlineEnabled.collectAsState()
                                val settingsOutlineColor by gameViewModel.textOutlineColor.collectAsState()
                                val premiumCurrencyBalance by gameViewModel.currency.collectAsState()
                                val ownedPresets by gameViewModel.unlockedPresets.collectAsState()
                                SettingsScreen(
                                    textColorOverride = settingsTextColorOverride,
                                    outlineEnabled = settingsOutlineEnabled,
                                    outlineColor = settingsOutlineColor,
                                    onTextColorChanged = { gameViewModel.setTextColorOverride(it) },
                                    onOutlineEnabledChanged = { gameViewModel.setTextOutlineEnabled(it) },
                                    onOutlineColorChanged = { gameViewModel.setTextOutlineColor(it) },
                                    premiumCurrency = premiumCurrencyBalance.second,
                                    unlockedPresets = ownedPresets,
                                    onPurchaseBundle = onLaunchPurchase,
                                    onPurchasePreset = { presetId -> gameViewModel.purchasePreset(presetId) }
                                )'''
new = '''                                val settingsTextColorOverride by gameViewModel.textColorOverride.collectAsState()
                                val settingsOutlineEnabled by gameViewModel.textOutlineEnabled.collectAsState()
                                val settingsOutlineColor by gameViewModel.textOutlineColor.collectAsState()
                                val settingsEffectMode by gameViewModel.textEffectMode.collectAsState()
                                val settingsSecondaryColor by gameViewModel.textSecondaryColor.collectAsState()
                                val premiumCurrencyBalance by gameViewModel.currency.collectAsState()
                                val ownedPresets by gameViewModel.unlockedPresets.collectAsState()
                                SettingsScreen(
                                    textColorOverride = settingsTextColorOverride,
                                    outlineEnabled = settingsOutlineEnabled,
                                    outlineColor = settingsOutlineColor,
                                    onTextColorChanged = { gameViewModel.setTextColorOverride(it) },
                                    onOutlineEnabledChanged = { gameViewModel.setTextOutlineEnabled(it) },
                                    onOutlineColorChanged = { gameViewModel.setTextOutlineColor(it) },
                                    premiumCurrency = premiumCurrencyBalance.second,
                                    unlockedPresets = ownedPresets,
                                    onPurchaseBundle = onLaunchPurchase,
                                    onPurchasePreset = { presetId -> gameViewModel.purchasePreset(presetId) },
                                    effectMode = settingsEffectMode,
                                    secondaryColor = settingsSecondaryColor,
                                    onEffectModeChanged = { gameViewModel.setTextEffectMode(it) },
                                    onSecondaryColorChanged = { gameViewModel.setTextSecondaryColor(it) }
                                )'''
results.append(guarded_replace(path, old, new, "MainActivity.kt SettingsScreen( call site"))

print()
print("=== Brace balance check ===")
for rel in [
    "Theme.kt",
    "MonetizationSystem.kt",
    "GameViewModel.kt",
    "SettingsScreen.kt",
    "MainActivity.kt",
]:
    check_braces(BASE + rel)

if not all(results):
    print()
    print("One or more edits FAILED - review output above before committing.")
    sys.exit(1)

print()
print("All edits applied successfully.")
