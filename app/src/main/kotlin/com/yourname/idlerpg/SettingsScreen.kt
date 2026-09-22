package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Slider
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.yourname.idlerpg.CurrencyBundleCatalog
import com.yourname.idlerpg.PremiumPreset
import com.yourname.idlerpg.PremiumPresetCatalog

@Composable
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
    cosmeticsContent: @Composable () -> Unit = {},
    modifier: Modifier = Modifier
) {
    var showGemShop by remember { mutableStateOf(false) }

    Column(
        modifier = modifier
            .fillMaxWidth()
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        Text(text = "Settings", style = MaterialTheme.typography.headlineSmall)
        Spacer(modifier = Modifier.height(20.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(text = "Gems: " + premiumCurrency, style = MaterialTheme.typography.titleMedium)
            Button(onClick = { showGemShop = true }) {
                Text("Get More Gems")
            }
        }

        Spacer(modifier = Modifier.height(16.dp))
        cosmeticsContent()
        Spacer(modifier = Modifier.height(16.dp))
        Text(text = "Premium Text Presets", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))

        PremiumPresetCatalog.presets.filterNot { it.isColorUnlockOnly }.forEach { preset ->
            PresetCard(
                preset = preset,
                isUnlocked = preset.id in unlockedPresets,
                canAfford = premiumCurrency >= preset.gemCost,
                onPurchase = { onPurchasePreset(preset.id) },
                onApply = {
                    onTextColorChanged(Color(preset.textColorArgb.toInt()))
                    onOutlineEnabledChanged(true)
                    onOutlineColorChanged(Color(preset.outlineColorArgb.toInt()))
                    onEffectModeChanged(preset.effectMode)
                    onSecondaryColorChanged(preset.secondaryColorArgb?.let { Color(it.toInt()) })
                }
            )
            Spacer(modifier = Modifier.height(8.dp))
        }

        Spacer(modifier = Modifier.height(28.dp))

        Text(text = "Text Color", style = MaterialTheme.typography.titleMedium)
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
            Text(text = "Text Outline", style = MaterialTheme.typography.titleMedium, modifier = Modifier.weight(1f))
            Switch(checked = outlineEnabled, onCheckedChange = { onOutlineEnabledChanged(it) })
        }
        if (outlineEnabled) {
            Spacer(modifier = Modifier.height(8.dp))
            RgbHexColorPicker(
                color = outlineColor,
                onColorChange = { onOutlineColorChanged(it) }
            )
        }
    }

    if (showGemShop) {
        GemShopDialog(
            onPurchaseBundle = onPurchaseBundle,
            onDismiss = { showGemShop = false }
        )
    }
}

@Composable
private fun GemShopDialog(
    onPurchaseBundle: (String) -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Get More Gems") },
        text = {
            Column {
                CurrencyBundleCatalog.bundles.forEach { bundle ->
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            val bonusText = if (bundle.bonusPercent > 0.0) " (+" + bundle.bonusPercent.toInt() + "% bonus)" else ""
                            Text(text = bundle.premiumCurrencyGranted.toString() + " Gems" + bonusText, style = MaterialTheme.typography.bodyLarge)
                            Text(text = "$" + bundle.realMoneyPriceUsd, style = MaterialTheme.typography.bodyMedium)
                        }
                        Button(onClick = { onPurchaseBundle(bundle.id) }) {
                            Text("Buy")
                        }
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text("Close")
            }
        }
    )
}

@Composable
private fun PresetCard(
    preset: PremiumPreset,
    isUnlocked: Boolean,
    canAfford: Boolean,
    onPurchase: () -> Unit,
    onApply: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, Color.Gray, RoundedCornerShape(8.dp))
            .padding(12.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Row {
            Box(
                modifier = Modifier
                    .size(24.dp)
                    .background(Color(preset.textColorArgb.toInt()), RoundedCornerShape(4.dp))
                    .border(1.dp, Color.Gray, RoundedCornerShape(4.dp))
            )
            Spacer(modifier = Modifier.padding(horizontal = 4.dp))
            Box(
                modifier = Modifier
                    .size(24.dp)
                    .background(Color(preset.outlineColorArgb.toInt()), RoundedCornerShape(4.dp))
                    .border(1.dp, Color.Gray, RoundedCornerShape(4.dp))
            )
            Spacer(modifier = Modifier.padding(horizontal = 8.dp))
            Column {
                Text(text = preset.displayName, style = MaterialTheme.typography.bodyLarge)
                if (!isUnlocked) {
                    Text(text = preset.gemCost.toString() + " Gems", style = MaterialTheme.typography.bodySmall)
                }
            }
        }
        if (isUnlocked) {
            Button(onClick = onApply) {
                Text("Apply")
            }
        } else {
            Button(onClick = onPurchase, enabled = canAfford) {
                Text("Unlock")
            }
        }
    }
}

@Composable
private fun RgbHexColorPicker(
    color: Color,
    onColorChange: (Color) -> Unit,
    modifier: Modifier = Modifier
) {
    val r = color.red * 255f
    val g = color.green * 255f
    val b = color.blue * 255f
    var hexText by remember(color) {
        mutableStateOf(String.format("#%02X%02X%02X", r.toInt(), g.toInt(), b.toInt()))
    }

    Column(modifier = modifier.fillMaxWidth()) {
        Row(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .background(color, RoundedCornerShape(6.dp))
                    .border(1.dp, Color.Gray, RoundedCornerShape(6.dp))
            )
            Spacer(modifier = Modifier.padding(horizontal = 8.dp))
            OutlinedTextField(
                value = hexText,
                onValueChange = { input ->
                    hexText = input
                    val cleaned = input.removePrefix("#")
                    if (cleaned.length == 6 && cleaned.all { it.isDigit() || it.uppercaseChar() in 'A'..'F' }) {
                        try {
                            val parsed = cleaned.toLong(16).toInt() or (0xFF shl 24)
                            onColorChange(Color(parsed))
                        } catch (e: NumberFormatException) {
                            // ignore invalid partial input while typing
                        }
                    }
                },
                label = { Text("Hex") },
                singleLine = true,
                modifier = Modifier.weight(1f)
            )
        }

        LabeledSlider(label = "R", value = r, onValueChange = { onColorChange(Color(it / 255f, g / 255f, b / 255f)) })
        LabeledSlider(label = "G", value = g, onValueChange = { onColorChange(Color(r / 255f, it / 255f, b / 255f)) })
        LabeledSlider(label = "B", value = b, onValueChange = { onColorChange(Color(r / 255f, g / 255f, it / 255f)) })
    }
}

@Composable
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
}
