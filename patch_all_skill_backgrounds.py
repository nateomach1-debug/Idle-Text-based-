#!/usr/bin/env python3
"""
Guarded patch: Settings tab - global text color override + soft glow
outline, driven from one place (IdleRpgTypography) plus a handful of
individual call-site wraps for the few Text() calls that pass their own
explicit color= param.

Touches: NavigationDestinations.kt, SideRail.kt, Theme.kt, GameViewModel.kt,
MainActivity.kt, and creates SettingsScreen.kt.
"""
import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def guarded_replace(path, old, new, marker):
    content = read(path)
    if marker in content:
        print(f"SKIP (already applied): {path} :: {marker[:50]}")
        return
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly 1 match in {path}, found {count}.\n--- old_str ---\n{old}\n--- end ---")
    write(path, content.replace(old, new))
    print(f"PATCHED: {path} :: {marker[:50]}")


def replace_all(path, old, new, marker):
    """For sites where every occurrence wants the identical transform -
    no disambiguation needed since they're all treated the same way."""
    content = read(path)
    if marker in content:
        print(f"SKIP (already applied): {path} :: {marker[:50]}")
        return
    count = content.count(old)
    if count == 0:
        raise RuntimeError(f"No matches in {path} for: {old[:80]}")
    write(path, content.replace(old, new))
    print(f"PATCHED ({count}x): {path} :: {marker[:50]}")


# =======================================================================
# 1. NavigationDestinations.kt - new SETTINGS entry
# =======================================================================
nav_path = os.path.join(ROOT, "NavigationDestinations.kt")
guarded_replace(
    nav_path,
    old='    LEADERBOARDS("Leaderboards", "leaderboard"),\n    MODERATION("Moderation", "shield_person")',
    new='    LEADERBOARDS("Leaderboards", "leaderboard"),\n    SETTINGS("Settings", "settings"),\n    MODERATION("Moderation", "shield_person")',
    marker='SETTINGS("Settings", "settings")',
)

# =======================================================================
# 2. SideRail.kt - icon mapping
# =======================================================================
side_rail_path = os.path.join(ROOT, "SideRail.kt")
guarded_replace(
    side_rail_path,
    old="    AppDestination.LEADERBOARDS -> Icons.Filled.Leaderboard\n    AppDestination.MODERATION -> Icons.Filled.AdminPanelSettings",
    new="    AppDestination.LEADERBOARDS -> Icons.Filled.Leaderboard\n    AppDestination.SETTINGS -> Icons.Filled.Settings\n    AppDestination.MODERATION -> Icons.Filled.AdminPanelSettings",
    marker="AppDestination.SETTINGS -> Icons.Filled.Settings",
)

# =======================================================================
# 3. Theme.kt - imports + dynamic typography + overrideColor helper
# =======================================================================
theme_path = os.path.join(ROOT, "Theme.kt")

guarded_replace(
    theme_path,
    old=(
        "import androidx.compose.foundation.isSystemInDarkTheme\n"
        "import androidx.compose.material3.MaterialTheme\n"
        "import androidx.compose.material3.Typography\n"
        "import androidx.compose.material3.darkColorScheme\n"
        "import androidx.compose.runtime.Composable\n"
        "import androidx.compose.ui.graphics.Color\n"
        "import androidx.compose.ui.text.TextStyle\n"
        "import androidx.compose.ui.text.font.FontFamily\n"
        "import androidx.compose.ui.text.font.FontWeight\n"
        "import androidx.compose.ui.unit.sp\n"
    ),
    new=(
        "import androidx.compose.foundation.isSystemInDarkTheme\n"
        "import androidx.compose.material3.MaterialTheme\n"
        "import androidx.compose.material3.Typography\n"
        "import androidx.compose.material3.darkColorScheme\n"
        "import androidx.compose.runtime.Composable\n"
        "import androidx.compose.runtime.CompositionLocalProvider\n"
        "import androidx.compose.runtime.compositionLocalOf\n"
        "import androidx.compose.ui.geometry.Offset\n"
        "import androidx.compose.ui.graphics.Color\n"
        "import androidx.compose.ui.graphics.Shadow\n"
        "import androidx.compose.ui.text.TextStyle\n"
        "import androidx.compose.ui.text.font.FontFamily\n"
        "import androidx.compose.ui.text.font.FontWeight\n"
        "import androidx.compose.ui.unit.sp\n"
    ),
    marker="import androidx.compose.runtime.compositionLocalOf",
)

old_typography_block = (
    "// =========================================================\n"
    "// TYPOGRAPHY\n"
    "// Bold serif for headers, clean sans-serif for body/data.\n"
    "// =========================================================\n"
    "\n"
    "private val HeaderFont = FontFamily.Serif\n"
    "private val BodyFont = FontFamily.SansSerif\n"
    "\n"
    "val IdleRpgTypography = Typography(\n"
    "    displayLarge = TextStyle(\n"
    "        fontFamily = HeaderFont,\n"
    "        fontWeight = FontWeight.Bold,\n"
    "        fontSize = 40.sp,\n"
    "        color = TextPrimary\n"
    "    ),\n"
    "    displayMedium = TextStyle(\n"
    "        fontFamily = HeaderFont,\n"
    "        fontWeight = FontWeight.Bold,\n"
    "        fontSize = 34.sp,\n"
    "        color = TextPrimary\n"
    "    ),\n"
    "    displaySmall = TextStyle(\n"
    "        fontFamily = HeaderFont,\n"
    "        fontWeight = FontWeight.Bold,\n"
    "        fontSize = 28.sp,\n"
    "        color = TextPrimary\n"
    "    ),\n"
    "    headlineLarge = TextStyle(\n"
    "        fontFamily = HeaderFont,\n"
    "        fontWeight = FontWeight.Bold,\n"
    "        fontSize = 24.sp,\n"
    "        color = TextPrimary\n"
    "    ),\n"
    "    headlineMedium = TextStyle(\n"
    "        fontFamily = HeaderFont,\n"
    "        fontWeight = FontWeight.Bold,\n"
    "        fontSize = 22.sp,\n"
    "        color = TextPrimary\n"
    "    ),\n"
    "    headlineSmall = TextStyle(\n"
    "        fontFamily = HeaderFont,\n"
    "        fontWeight = FontWeight.SemiBold,\n"
    "        fontSize = 19.sp,\n"
    "        color = TextPrimary\n"
    "    ),\n"
    "    titleLarge = TextStyle(\n"
    "        fontFamily = HeaderFont,\n"
    "        fontWeight = FontWeight.SemiBold,\n"
    "        fontSize = 19.sp,\n"
    "        color = TextPrimary\n"
    "    ),\n"
    "    titleMedium = TextStyle(\n"
    "        fontFamily = HeaderFont,\n"
    "        fontWeight = FontWeight.SemiBold,\n"
    "        fontSize = 17.sp,\n"
    "        color = TextPrimary\n"
    "    ),\n"
    "    titleSmall = TextStyle(\n"
    "        fontFamily = HeaderFont,\n"
    "        fontWeight = FontWeight.SemiBold,\n"
    "        fontSize = 15.sp,\n"
    "        color = TextPrimary\n"
    "    ),\n"
    "    bodyLarge = TextStyle(\n"
    "        fontFamily = BodyFont,\n"
    "        fontWeight = FontWeight.Normal,\n"
    "        fontSize = 16.sp,\n"
    "        color = TextPrimary\n"
    "    ),\n"
    "    bodyMedium = TextStyle(\n"
    "        fontFamily = BodyFont,\n"
    "        fontWeight = FontWeight.Normal,\n"
    "        fontSize = 15.sp,\n"
    "        color = TextPrimary\n"
    "    ),\n"
    "    bodySmall = TextStyle(\n"
    "        fontFamily = BodyFont,\n"
    "        fontWeight = FontWeight.Normal,\n"
    "        fontSize = 13.sp,\n"
    "        color = TextPrimary\n"
    "    ),\n"
    "    labelLarge = TextStyle(\n"
    "        fontFamily = BodyFont,\n"
    "        fontWeight = FontWeight.Medium,\n"
    "        fontSize = 13.sp,\n"
    "        color = TextSecondary\n"
    "    ),\n"
    "    labelMedium = TextStyle(\n"
    "        fontFamily = BodyFont,\n"
    "        fontWeight = FontWeight.Medium,\n"
    "        fontSize = 12.sp,\n"
    "        color = TextSecondary\n"
    "    ),\n"
    "    labelSmall = TextStyle(\n"
    "        fontFamily = BodyFont,\n"
    "        fontWeight = FontWeight.Medium,\n"
    "        fontSize = 12.sp,\n"
    "        color = TextSecondary\n"
    "    )\n"
    ")\n"
    "\n"
    "@Composable\n"
    "fun IdleRpgTheme(content: @Composable () -> Unit) {\n"
    "    MaterialTheme(\n"
    "        colorScheme = IdleRpgDarkColors,\n"
    "        typography = IdleRpgTypography,\n"
    "        content = content\n"
    "    )\n"
    "}\n"
)

new_typography_block = (
    "// =========================================================\n"
    "// TYPOGRAPHY\n"
    "// Bold serif for headers, clean sans-serif for body/data.\n"
    "// Parameterized by the Settings tab's text-color-override and\n"
    "// outline settings so every style updates together from one\n"
    "// place, rather than touching each Text() call site.\n"
    "// =========================================================\n"
    "\n"
    "private val HeaderFont = FontFamily.Serif\n"
    "private val BodyFont = FontFamily.SansSerif\n"
    "\n"
    "// Settings-driven text color override, available to any composable\n"
    "// via overrideColor() below - covers the handful of Text() calls\n"
    "// elsewhere in the app that pass their own explicit color= param\n"
    "// (which bypasses Typography's embedded color entirely).\n"
    "val LocalTextColorOverride = compositionLocalOf<Color?> { null }\n"
    "\n"
    "@Composable\n"
    "fun overrideColor(fallback: Color): Color = LocalTextColorOverride.current ?: fallback\n"
    "\n"
    "private fun outlineShadow(enabled: Boolean, color: Color): Shadow? =\n"
    "    if (enabled) Shadow(color = color, offset = Offset.Zero, blurRadius = 8f) else null\n"
    "\n"
    "private fun buildIdleRpgTypography(\n"
    "    textColorOverride: Color?,\n"
    "    outlineEnabled: Boolean,\n"
    "    outlineColor: Color\n"
    "): Typography {\n"
    "    val primary = textColorOverride ?: TextPrimary\n"
    "    val secondary = textColorOverride ?: TextSecondary\n"
    "    val shadow = outlineShadow(outlineEnabled, outlineColor)\n"
    "    return Typography(\n"
    "        displayLarge = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.Bold, fontSize = 40.sp, color = primary, shadow = shadow),\n"
    "        displayMedium = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.Bold, fontSize = 34.sp, color = primary, shadow = shadow),\n"
    "        displaySmall = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.Bold, fontSize = 28.sp, color = primary, shadow = shadow),\n"
    "        headlineLarge = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.Bold, fontSize = 24.sp, color = primary, shadow = shadow),\n"
    "        headlineMedium = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.Bold, fontSize = 22.sp, color = primary, shadow = shadow),\n"
    "        headlineSmall = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.SemiBold, fontSize = 19.sp, color = primary, shadow = shadow),\n"
    "        titleLarge = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.SemiBold, fontSize = 19.sp, color = primary, shadow = shadow),\n"
    "        titleMedium = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.SemiBold, fontSize = 17.sp, color = primary, shadow = shadow),\n"
    "        titleSmall = TextStyle(fontFamily = HeaderFont, fontWeight = FontWeight.SemiBold, fontSize = 15.sp, color = primary, shadow = shadow),\n"
    "        bodyLarge = TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Normal, fontSize = 16.sp, color = primary, shadow = shadow),\n"
    "        bodyMedium = TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Normal, fontSize = 15.sp, color = primary, shadow = shadow),\n"
    "        bodySmall = TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Normal, fontSize = 13.sp, color = primary, shadow = shadow),\n"
    "        labelLarge = TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Medium, fontSize = 13.sp, color = secondary, shadow = shadow),\n"
    "        labelMedium = TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Medium, fontSize = 12.sp, color = secondary, shadow = shadow),\n"
    "        labelSmall = TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Medium, fontSize = 12.sp, color = secondary, shadow = shadow)\n"
    "    )\n"
    "}\n"
    "\n"
    "@Composable\n"
    "fun IdleRpgTheme(\n"
    "    textColorOverride: Color? = null,\n"
    "    outlineEnabled: Boolean = false,\n"
    "    outlineColor: Color = Color.Black,\n"
    "    content: @Composable () -> Unit\n"
    ") {\n"
    "    CompositionLocalProvider(LocalTextColorOverride provides textColorOverride) {\n"
    "        MaterialTheme(\n"
    "            colorScheme = IdleRpgDarkColors,\n"
    "            typography = buildIdleRpgTypography(textColorOverride, outlineEnabled, outlineColor),\n"
    "            content = content\n"
    "        )\n"
    "    }\n"
    "}\n"
)

guarded_replace(
    theme_path, old_typography_block, new_typography_block,
    marker="private fun buildIdleRpgTypography(",
)

# =======================================================================
# 4. GameViewModel.kt - settings state + persistence
# =======================================================================
gvm_path = os.path.join(ROOT, "GameViewModel.kt")

guarded_replace(
    gvm_path,
    old="import com.yourname.idlerpg.VendorBuyCatalog\n" if False else "import com.yourname.idlerpg.ui.screens.VendorBuyCatalog\n",
    new=(
        "import com.yourname.idlerpg.ui.screens.VendorBuyCatalog\n"
        "import androidx.compose.ui.graphics.Color\n"
        "import androidx.compose.ui.graphics.toArgb\n"
    ),
    marker="import androidx.compose.ui.graphics.toArgb\n",
)

guarded_replace(
    gvm_path,
    old=(
        "    private val _selectedLeaderboardCategory = MutableStateFlow(LeaderboardCategory.TOTAL_LEVEL)\n"
        "    val selectedLeaderboardCategory: StateFlow<LeaderboardCategory> = _selectedLeaderboardCategory.asStateFlow()\n"
    ),
    new=(
        "    private val _selectedLeaderboardCategory = MutableStateFlow(LeaderboardCategory.TOTAL_LEVEL)\n"
        "    val selectedLeaderboardCategory: StateFlow<LeaderboardCategory> = _selectedLeaderboardCategory.asStateFlow()\n"
        "\n"
        "    // =========================================================\n"
        "    // SETTINGS: text color override + outline (Settings tab)\n"
        "    // Persisted via SharedPreferences (idlerpg_prefs, same file/\n"
        "    // convention as inventory/skills view-mode prefs).\n"
        "    // =========================================================\n"
        "    private val settingsPrefs = application.getSharedPreferences(\"idlerpg_prefs\", android.content.Context.MODE_PRIVATE)\n"
        "\n"
        "    private val _textColorOverride = MutableStateFlow<Color?>(\n"
        "        if (settingsPrefs.contains(\"text_color_override\")) Color(settingsPrefs.getInt(\"text_color_override\", 0)) else null\n"
        "    )\n"
        "    val textColorOverride: StateFlow<Color?> = _textColorOverride.asStateFlow()\n"
        "\n"
        "    private val _textOutlineEnabled = MutableStateFlow(settingsPrefs.getBoolean(\"text_outline_enabled\", false))\n"
        "    val textOutlineEnabled: StateFlow<Boolean> = _textOutlineEnabled.asStateFlow()\n"
        "\n"
        "    private val _textOutlineColor = MutableStateFlow(Color(settingsPrefs.getInt(\"text_outline_color\", android.graphics.Color.BLACK)))\n"
        "    val textOutlineColor: StateFlow<Color> = _textOutlineColor.asStateFlow()\n"
        "\n"
        "    fun setTextColorOverride(color: Color?) {\n"
        "        _textColorOverride.value = color\n"
        "        if (color == null) {\n"
        "            settingsPrefs.edit().remove(\"text_color_override\").apply()\n"
        "        } else {\n"
        "            settingsPrefs.edit().putInt(\"text_color_override\", color.toArgb()).apply()\n"
        "        }\n"
        "    }\n"
        "\n"
        "    fun setTextOutlineEnabled(enabled: Boolean) {\n"
        "        _textOutlineEnabled.value = enabled\n"
        "        settingsPrefs.edit().putBoolean(\"text_outline_enabled\", enabled).apply()\n"
        "    }\n"
        "\n"
        "    fun setTextOutlineColor(color: Color) {\n"
        "        _textOutlineColor.value = color\n"
        "        settingsPrefs.edit().putInt(\"text_outline_color\", color.toArgb()).apply()\n"
        "    }\n"
    ),
    marker="SETTINGS: text color override + outline (Settings tab)",
)

# =======================================================================
# 5. MainActivity.kt - setContent wiring + new SETTINGS branch
# =======================================================================
ma_path = os.path.join(ROOT, "MainActivity.kt")

guarded_replace(
    ma_path,
    old=(
        "        setContent {\n"
        "            IdleRpgTheme {\n"
        "                AppRoot(gameViewModel)\n"
        "            }\n"
        "        }\n"
    ),
    new=(
        "        setContent {\n"
        "            val textColorOverride by gameViewModel.textColorOverride.collectAsState()\n"
        "            val textOutlineEnabled by gameViewModel.textOutlineEnabled.collectAsState()\n"
        "            val textOutlineColor by gameViewModel.textOutlineColor.collectAsState()\n"
        "            IdleRpgTheme(\n"
        "                textColorOverride = textColorOverride,\n"
        "                outlineEnabled = textOutlineEnabled,\n"
        "                outlineColor = textOutlineColor\n"
        "            ) {\n"
        "                AppRoot(gameViewModel)\n"
        "            }\n"
        "        }\n"
    ),
    marker="val textColorOverride by gameViewModel.textColorOverride.collectAsState()",
)

guarded_replace(
    ma_path,
    old=(
        "                            AppDestination.LEADERBOARDS -> {\n"
        "                                val leaderboardRows by gameViewModel.leaderboardRows.collectAsState()\n"
        "                                val leaderboardLoading by gameViewModel.leaderboardLoading.collectAsState()\n"
        "                                val selectedLeaderboardCategory by gameViewModel.selectedLeaderboardCategory.collectAsState()\n"
        "                                LaunchedEffect(Unit) { gameViewModel.fetchLeaderboard(selectedLeaderboardCategory) }\n"
        "                                LeaderboardsScreen(\n"
        "                                    selectedCategory = selectedLeaderboardCategory,\n"
        "                                    rows = leaderboardRows,\n"
        "                                    isLoading = leaderboardLoading,\n"
        "                                    onCategorySelected = { gameViewModel.fetchLeaderboard(it) }\n"
        "                                )\n"
        "                            }\n"
        "\n"
    ),
    new=(
        "                            AppDestination.LEADERBOARDS -> {\n"
        "                                val leaderboardRows by gameViewModel.leaderboardRows.collectAsState()\n"
        "                                val leaderboardLoading by gameViewModel.leaderboardLoading.collectAsState()\n"
        "                                val selectedLeaderboardCategory by gameViewModel.selectedLeaderboardCategory.collectAsState()\n"
        "                                LaunchedEffect(Unit) { gameViewModel.fetchLeaderboard(selectedLeaderboardCategory) }\n"
        "                                LeaderboardsScreen(\n"
        "                                    selectedCategory = selectedLeaderboardCategory,\n"
        "                                    rows = leaderboardRows,\n"
        "                                    isLoading = leaderboardLoading,\n"
        "                                    onCategorySelected = { gameViewModel.fetchLeaderboard(it) }\n"
        "                                )\n"
        "                            }\n"
        "\n"
        "                            AppDestination.SETTINGS -> {\n"
        "                                val settingsTextColorOverride by gameViewModel.textColorOverride.collectAsState()\n"
        "                                val settingsOutlineEnabled by gameViewModel.textOutlineEnabled.collectAsState()\n"
        "                                val settingsOutlineColor by gameViewModel.textOutlineColor.collectAsState()\n"
        "                                SettingsScreen(\n"
        "                                    textColorOverride = settingsTextColorOverride,\n"
        "                                    outlineEnabled = settingsOutlineEnabled,\n"
        "                                    outlineColor = settingsOutlineColor,\n"
        "                                    onTextColorChanged = { gameViewModel.setTextColorOverride(it) },\n"
        "                                    onOutlineEnabledChanged = { gameViewModel.setTextOutlineEnabled(it) },\n"
        "                                    onOutlineColorChanged = { gameViewModel.setTextOutlineColor(it) }\n"
        "                                )\n"
        "                            }\n"
        "\n"
    ),
    marker="AppDestination.SETTINGS -> {\n                                val settingsTextColorOverride",
)

# =======================================================================
# 6. New SettingsScreen.kt
# =======================================================================
settings_screen_path = os.path.join(ROOT, "SettingsScreen.kt")
settings_screen_content = '''package com.yourname.idlerpg.ui.screens

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
'''

if os.path.exists(settings_screen_path) and "fun SettingsScreen" in read(settings_screen_path):
    print(f"SKIP (already exists): {settings_screen_path}")
else:
    write(settings_screen_path, settings_screen_content)
    print(f"CREATED: {settings_screen_path}")

# =======================================================================
# 7. Wrap the ~13 remaining explicit-color Text() call sites (excluding
#    Theme.kt's own definitions, PatternBackground.kt's Canvas draws,
#    MainActivity's Surface, and ZoneSelectScreen which already inherits
#    via MaterialTheme.typography.X.color)
# =======================================================================

guarded_replace(
    os.path.join(ROOT, "CharacterSelectScreen.kt"),
    old="Text(text = it, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.error)",
    new="Text(text = it, style = MaterialTheme.typography.labelSmall, color = overrideColor(MaterialTheme.colorScheme.error))",
    marker="color = overrideColor(MaterialTheme.colorScheme.error))",
)

guarded_replace(
    os.path.join(ROOT, "LoginScreen.kt"),
    old="Text(text = it, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.error)",
    new="Text(text = it, style = MaterialTheme.typography.labelSmall, color = overrideColor(MaterialTheme.colorScheme.error))",
    marker="color = overrideColor(MaterialTheme.colorScheme.error))",
)

combat_view_path = os.path.join(ROOT, "CombatViewScreen.kt")
guarded_replace(combat_view_path, old="            color = MaterialTheme.colorScheme.error\n", new="            color = overrideColor(MaterialTheme.colorScheme.error)\n", marker="color = overrideColor(MaterialTheme.colorScheme.error)\n")
guarded_replace(combat_view_path, old="            color = MaterialTheme.colorScheme.primary\n", new="            color = overrideColor(MaterialTheme.colorScheme.primary)\n", marker="color = overrideColor(MaterialTheme.colorScheme.primary)\n")

loadout_path = os.path.join(ROOT, "LoadoutScreen.kt")
guarded_replace(loadout_path, old="Text(text = prayer.displayName, style = MaterialTheme.typography.bodyMedium, color = textColor)", new="Text(text = prayer.displayName, style = MaterialTheme.typography.bodyMedium, color = overrideColor(textColor))", marker="prayer.displayName, style = MaterialTheme.typography.bodyMedium, color = overrideColor(textColor))")
guarded_replace(loadout_path, old="Text(text = prayer.description, style = MaterialTheme.typography.labelSmall, color = textColor)", new="Text(text = prayer.description, style = MaterialTheme.typography.labelSmall, color = overrideColor(textColor))", marker="prayer.description, style = MaterialTheme.typography.labelSmall, color = overrideColor(textColor))")
guarded_replace(loadout_path, old='Text(text = "Lv " + prayer.levelRequired, style = MaterialTheme.typography.labelSmall, color = textColor)', new='Text(text = "Lv " + prayer.levelRequired, style = MaterialTheme.typography.labelSmall, color = overrideColor(textColor))', marker='"Lv " + prayer.levelRequired, style = MaterialTheme.typography.labelSmall, color = overrideColor(textColor))')

side_rail_content_path = os.path.join(ROOT, "SideRail.kt")
guarded_replace(side_rail_content_path, old="                color = contentColor\n", new="                color = overrideColor(contentColor)\n", marker="color = overrideColor(contentColor)\n")

skill_detail_path = os.path.join(ROOT, "SkillDetailScreen.kt")
guarded_replace(skill_detail_path, old="Text(text = action.displayName, style = MaterialTheme.typography.bodyMedium, color = contentColor)", new="Text(text = action.displayName, style = MaterialTheme.typography.bodyMedium, color = overrideColor(contentColor))", marker="action.displayName, style = MaterialTheme.typography.bodyMedium, color = overrideColor(contentColor))")
guarded_replace(skill_detail_path, old='Text(text = "Lv. " + action.levelRequired, style = MaterialTheme.typography.labelSmall, color = contentColor)', new='Text(text = "Lv. " + action.levelRequired, style = MaterialTheme.typography.labelSmall, color = overrideColor(contentColor))', marker='"Lv. " + action.levelRequired, style = MaterialTheme.typography.labelSmall, color = overrideColor(contentColor))')

skills_screen_path = os.path.join(ROOT, "SkillsScreen.kt")
replace_all(
    skills_screen_path,
    old="color = MaterialTheme.colorScheme.onSurfaceVariant",
    new="color = overrideColor(MaterialTheme.colorScheme.onSurfaceVariant)",
    marker="color = overrideColor(MaterialTheme.colorScheme.onSurfaceVariant)",
)

smithing_path = os.path.join(ROOT, "SmithingScreen.kt")
guarded_replace(smithing_path, old="Text(text = recipe.displayName, style = MaterialTheme.typography.bodyMedium, color = contentColor)", new="Text(text = recipe.displayName, style = MaterialTheme.typography.bodyMedium, color = overrideColor(contentColor))", marker="recipe.displayName, style = MaterialTheme.typography.bodyMedium, color = overrideColor(contentColor))")
guarded_replace(smithing_path, old='Text(text = "Lv. " + recipe.levelRequired, style = MaterialTheme.typography.labelSmall, color = contentColor)', new='Text(text = "Lv. " + recipe.levelRequired, style = MaterialTheme.typography.labelSmall, color = overrideColor(contentColor))', marker='"Lv. " + recipe.levelRequired, style = MaterialTheme.typography.labelSmall, color = overrideColor(contentColor))')
guarded_replace(smithing_path, old="            color = contentColor\n", new="            color = overrideColor(contentColor)\n", marker="color = overrideColor(contentColor)\n")

print("\nAll Settings tab patches applied successfully.")
