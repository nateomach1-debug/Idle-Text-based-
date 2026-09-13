import pathlib

settings_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/SettingsScreen.kt")
settings_text = settings_path.read_text()

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
# 1. Add scroll-related imports
# ============================================================
imp_old = """import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement"""
imp_new = """import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.layout.Arrangement"""
settings_text, c1 = apply_edit(settings_text, imp_old, imp_new, "import androidx.compose.foundation.verticalScroll", "SettingsScreen.kt scroll imports", errors)

# ============================================================
# 2. Reorder: Gems/shop/presets section moves to the top, page becomes scrollable
# ============================================================
body_old = '''    var showGemShop by remember { mutableStateOf(false) }

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
    }'''

body_new = '''    var showGemShop by remember { mutableStateOf(false) }

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

        Spacer(modifier = Modifier.height(28.dp))

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
    }'''

settings_text, c2 = apply_edit(settings_text, body_old, body_new, ".verticalScroll(rememberScrollState())", "SettingsScreen.kt reorder + scroll", errors)

if errors:
    raise SystemExit(
        "PATCH D FAILED: one or more expected blocks did not match. No changes made.\n"
        + "\n".join(f"  - {e}" for e in errors)
    )

settings_path.write_text(settings_text)

any_changed = any([c1, c2])
if any_changed:
    print("Patch D applied: Settings screen is now scrollable, and the Gems balance/shop/presets section moved to the top of the page (above Text Color/Text Outline).")
else:
    print("Patch D: already fully applied, no changes made.")
