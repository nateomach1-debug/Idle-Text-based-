import pathlib

settings_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/SettingsScreen.kt")
main_activity_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")

settings_text = settings_path.read_text()
main_activity_text = main_activity_path.read_text()

errors = []


def apply_edit(text, old, new, marker, label, errors):
    if text.count(marker) >= 1:
        return text, False  # already applied
    count_old = text.count(old)
    if count_old == 1:
        return text.replace(old, new), True
    errors.append(f"{label}: expected exactly 1 match of old block (and marker absent), found old={count_old}")
    return text, False


# ============================================================
# 1. SettingsScreen.kt - full targeted rewrite
# ============================================================

settings_old = '''package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Slider
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

@Composable
fun SettingsScreen(
    textColorOverride: Color?,
    outlineEnabled: Boolean,
    outlineColor: Color,
    onTextColorChanged: (Color?) -> Unit,
    onOutlineEnabledChanged: (Boolean) -> Unit,
    onOutlineColorChanged: (Color) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier.fillMaxWidth().padding(16.dp)) {
        Text(text = "Settings", style = MaterialTheme.typography.headlineSmall)
        Spacer(modifier = Modifier.height(20.dp))

        Text(text = "Text Color", style = MaterialTheme.typography.titleMedium)
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
}'''

settings_new = '''package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
    modifier: Modifier = Modifier
) {
    var showGemShop by remember { mutableStateOf(false) }

    Column(modifier = modifier.fillMaxWidth().padding(16.dp)) {
        Text(text = "Settings", style = MaterialTheme.typography.headlineSmall)
        Spacer(modifier = Modifier.height(20.dp))

        Text(text = "Text Color", style = MaterialTheme.typography.titleMedium)
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

        Spacer(modifier = Modifier.height(28.dp))

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
        Text(text = "Premium Text Presets", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))

        PremiumPresetCatalog.presets.forEach { preset ->
            PresetCard(
                preset = preset,
                isUnlocked = preset.id in unlockedPresets,
                canAfford = premiumCurrency >= preset.gemCost,
                onPurchase = { onPurchasePreset(preset.id) },
                onApply = {
                    onTextColorChanged(Color(preset.textColorArgb.toInt()))
                    onOutlineEnabledChanged(true)
                    onOutlineColorChanged(Color(preset.outlineColorArgb.toInt()))
                }
            )
            Spacer(modifier = Modifier.height(8.dp))
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
}'''

settings_text, c1 = apply_edit(settings_text, settings_old, settings_new, "GemShopDialog", "SettingsScreen.kt full rewrite", errors)

# ============================================================
# 2. MainActivity.kt - thread premiumCurrency/unlockedPresets/onPurchaseBundle/onPurchasePreset into the call site
# ============================================================

ma_old = """                                SettingsScreen(
                                    textColorOverride = settingsTextColorOverride,
                                    outlineEnabled = settingsOutlineEnabled,
                                    outlineColor = settingsOutlineColor,
                                    onTextColorChanged = { gameViewModel.setTextColorOverride(it) },
                                    onOutlineEnabledChanged = { gameViewModel.setTextOutlineEnabled(it) },
                                    onOutlineColorChanged = { gameViewModel.setTextOutlineColor(it) }
                                )"""

ma_new = """                                val premiumCurrencyBalance by gameViewModel.currency.collectAsState()
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
                                )"""

main_activity_text, c2 = apply_edit(main_activity_text, ma_old, ma_new, "val premiumCurrencyBalance by gameViewModel.currency.collectAsState()", "MainActivity.kt SettingsScreen call site", errors)

if errors:
    raise SystemExit(
        "PATCH C FAILED: one or more expected blocks did not match. No changes made to either file.\n"
        + "\n".join(f"  - {e}" for e in errors)
    )

settings_path.write_text(settings_text)
main_activity_path.write_text(main_activity_text)

any_changed = any([c1, c2])
if any_changed:
    print("Patch C applied:")
    print("  - SettingsScreen.kt: gem balance display, Get More Gems shop dialog (3 bundles), 3 premium preset cards (unlock/apply)")
    print("  - MainActivity.kt: threaded premiumCurrency/unlockedPresets/onPurchaseBundle/onPurchasePreset into the SettingsScreen call site")
else:
    print("Patch C: already fully applied, no changes made.")
