import sys

BASE = "app/src/main/kotlin/com/yourname/idlerpg/"
THEME = BASE + "Theme.kt"
MONETIZATION = BASE + "MonetizationSystem.kt"
SETTINGS = BASE + "SettingsScreen.kt"


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
# 1. Theme.kt - boost Pulse/Shimmer/ColorCycle/Wave intensity.
# Root cause: sweep offsets were raw pixel values (150-300px, only
# ~50-100dp on a high-density screen) - far too narrow to visibly
# cross normal text widths. Pulse's alpha swing was only 45%.
# Color Cycle didn't force high saturation/brightness, so a mellow
# base color barely showed hue rotation. Widened sweep amplitude
# ~5x, maxed shimmer highlight to pure white, widened pulse alpha
# swing to 88%, and forced full saturation/brightness on cycle.
# ===========================================================
old = '''    TextEffectMode.PULSE -> {
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
    }'''
new = '''    TextEffectMode.PULSE -> {
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
    }'''
results.append(guarded_replace(THEME, old, new, "Theme.kt boost Pulse/Shimmer/ColorCycle/Wave intensity"))

# ===========================================================
# 2. MonetizationSystem.kt - free first 3 presets, add Custom Color unlock
# ===========================================================
old = '''data class PremiumPreset(
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
new = '''data class PremiumPreset(
    val id: String,
    val displayName: String,
    val gemCost: Long,
    val textColorArgb: Long,
    val outlineColorArgb: Long,
    val effectMode: com.yourname.idlerpg.ui.theme.TextEffectMode = com.yourname.idlerpg.ui.theme.TextEffectMode.SOLID,
    val secondaryColorArgb: Long? = null,
    val isColorUnlockOnly: Boolean = false
)

object PremiumPresetCatalog {
    val presets = listOf(
        PremiumPreset(id = "preset_ember_glow", displayName = "Ember Glow", gemCost = 0, textColorArgb = 0xFFFFB86CL, outlineColorArgb = 0xFF8B0000L),
        PremiumPreset(id = "preset_arctic_shimmer", displayName = "Arctic Shimmer", gemCost = 0, textColorArgb = 0xFF9AEAFFL, outlineColorArgb = 0xFF00E5FFL),
        PremiumPreset(id = "preset_royal_amethyst", displayName = "Royal Amethyst", gemCost = 0, textColorArgb = 0xFFC77DFFL, outlineColorArgb = 0xFF7209B7L),
        // Placeholder gem prices, same spirit as other tunable placeholders
        // in this project - adjust after seeing them live.
        PremiumPreset(id = "preset_sunset_gradient", displayName = "Sunset Gradient", gemCost = 200, textColorArgb = 0xFFFF6B35L, outlineColorArgb = 0xFF8B0000L, effectMode = com.yourname.idlerpg.ui.theme.TextEffectMode.GRADIENT, secondaryColorArgb = 0xFFFFD23FL),
        PremiumPreset(id = "preset_pulse_glow", displayName = "Pulse Glow", gemCost = 250, textColorArgb = 0xFF9AEAFFL, outlineColorArgb = 0xFF00E5FFL, effectMode = com.yourname.idlerpg.ui.theme.TextEffectMode.PULSE),
        PremiumPreset(id = "preset_shimmer_silver", displayName = "Shimmer Silver", gemCost = 250, textColorArgb = 0xFFC0C0C0L, outlineColorArgb = 0xFF4A4A4AL, effectMode = com.yourname.idlerpg.ui.theme.TextEffectMode.SHIMMER),
        PremiumPreset(id = "preset_rainbow_cycle", displayName = "Rainbow Cycle", gemCost = 300, textColorArgb = 0xFFFF0000L, outlineColorArgb = 0xFF000000L, effectMode = com.yourname.idlerpg.ui.theme.TextEffectMode.COLOR_CYCLE),
        PremiumPreset(id = "preset_ocean_wave", displayName = "Ocean Wave", gemCost = 250, textColorArgb = 0xFF00B4D8L, outlineColorArgb = 0xFF03045EL, effectMode = com.yourname.idlerpg.ui.theme.TextEffectMode.WAVE, secondaryColorArgb = 0xFF90E0EFL),
        // Expensive on purpose: unlocking free-form color entry lets a
        // player recreate the look of any other premium preset for the
        // cost of one purchase, so it's priced above the individual presets.
        PremiumPreset(id = "unlock_custom_color", displayName = "Custom Color License", gemCost = 750, textColorArgb = 0xFFFFFFFFL, outlineColorArgb = 0xFF000000L, isColorUnlockOnly = true)
    )

    fun find(presetId: String): PremiumPreset? = presets.find { it.id == presetId }
}'''
results.append(guarded_replace(MONETIZATION, old, new, "MonetizationSystem.kt free presets + Custom Color unlock"))

# ===========================================================
# 3. SettingsScreen.kt - skip the color-unlock entry in the normal preset loop
# ===========================================================
old = '''        PremiumPresetCatalog.presets.forEach { preset ->
            PresetCard('''
new = '''        PremiumPresetCatalog.presets.filterNot { it.isColorUnlockOnly }.forEach { preset ->
            PresetCard('''
results.append(guarded_replace(SETTINGS, old, new, "SettingsScreen.kt skip color-unlock preset in main loop"))

# ===========================================================
# 4. SettingsScreen.kt - gate Text Color + Second Color pickers behind
# the Custom Color License; Reset to Default stays free.
# ===========================================================
old = '''        Text(text = "Text Color", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        RgbHexColorPicker(
            color = textColorOverride ?: Color(0xFFEDE8DD),
            onColorChange = { onTextColorChanged(it) }
        )
        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = { onTextColorChanged(null) }) {
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
new = '''        Text(text = "Text Color", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        val customColorUnlocked = unlockedPresets.contains("unlock_custom_color")
        if (customColorUnlocked) {
            RgbHexColorPicker(
                color = textColorOverride ?: Color(0xFFEDE8DD),
                onColorChange = { onTextColorChanged(it) }
            )
        } else {
            val customColorPreset = PremiumPresetCatalog.presets.first { it.isColorUnlockOnly }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text(text = "Fully custom color - pick any color, recreates any preset look", style = MaterialTheme.typography.bodyMedium)
                    Text(text = customColorPreset.gemCost.toString() + " Gems", style = MaterialTheme.typography.bodySmall)
                }
                Button(onClick = { onPurchasePreset(customColorPreset.id) }, enabled = premiumCurrency >= customColorPreset.gemCost) {
                    Text("Unlock")
                }
            }
        }
        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = { onTextColorChanged(null) }) {
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
        if (customColorUnlocked && (effectMode == com.yourname.idlerpg.ui.theme.TextEffectMode.GRADIENT || effectMode == com.yourname.idlerpg.ui.theme.TextEffectMode.WAVE)) {
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
results.append(guarded_replace(SETTINGS, old, new, "SettingsScreen.kt gate custom color pickers behind paywall"))

print()
print("=== Brace balance check ===")
for p in [THEME, MONETIZATION, SETTINGS]:
    check_braces(p)

if not all(results):
    print()
    print("One or more edits FAILED - review output above before committing.")
    sys.exit(1)

print()
print("All edits applied successfully.")
