import os

# --- 1. New file: PatternBackground.kt (flat, per this repo's convention - package name doesn't match folder nesting). ---
pattern_path = "app/src/main/kotlin/com/yourname/idlerpg/PatternBackground.kt"
pattern_content = '''package com.yourname.idlerpg.ui.theme

import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.DrawScope

// =========================================================
// PROCEDURAL PATTERN BACKGROUNDS
// A soft top-to-bottom gradient (charcoal -> tinted color) plus
// a subtle diagonal hatch texture drawn directly, no image assets.
// Same tinting color feeds both layers so it reads as one
// coherent "themed" background rather than a flat color wash.
// Tune via PATTERN_LINE_ALPHA / PATTERN_LINE_SPACING_DP /
// GRADIENT_BOTTOM_ALPHA below if the effect feels too strong/weak
// once seen on-device.
// =========================================================

private const val PATTERN_LINE_SPACING_DP = 22f
private const val PATTERN_LINE_ALPHA = 0.06f
private const val GRADIENT_BOTTOM_ALPHA = 0.30f

private fun DrawScope.drawDiagonalHatch(lineColor: Color, spacingPx: Float) {
    val w = size.width
    val h = size.height
    var x = -h
    while (x < w) {
        drawLine(
            color = lineColor,
            start = Offset(x, h),
            end = Offset(x + h, 0f),
            strokeWidth = 1.5f
        )
        x += spacingPx
    }
}

fun Modifier.proceduralThemeBackground(baseColor: Color, accentColor: Color = baseColor): Modifier = this.drawBehind {
    val gradient = Brush.verticalGradient(
        colors = listOf(CharcoalBackground, baseColor.copy(alpha = GRADIENT_BOTTOM_ALPHA))
    )
    drawRect(brush = gradient)
    drawDiagonalHatch(accentColor.copy(alpha = PATTERN_LINE_ALPHA), spacingPx = PATTERN_LINE_SPACING_DP * density)
}

// Per-skill themed background. Falls back to MutedTeal for any skillId
// without a mapped color (shouldn't normally happen from the Skills tab).
fun Modifier.skillPatternBackground(skillId: String): Modifier =
    this.proceduralThemeBackground(baseColor = skillThemeColor(skillId) ?: MutedTeal)

// General app background for screens not tied to one skill (Home, Combat,
// Inventory, Market, Guild, Chat) - uses the base gold accent, not a skill color.
fun Modifier.appPatternBackground(): Modifier =
    this.proceduralThemeBackground(baseColor = ParchmentGold)

// Subtler variant for the narrow side rail - flat charcoal surface plus a
// faint hatch, no gradient (the strip is too narrow for one to read well).
fun Modifier.railPatternBackground(): Modifier = this.drawBehind {
    drawRect(color = CharcoalSurface)
    drawDiagonalHatch(ParchmentGold.copy(alpha = 0.05f), spacingPx = 18f * density)
}
'''
with open(pattern_path, "w") as f:
    f.write(pattern_content)
print("OK: created " + pattern_path)

# --- 2. MainActivity.kt: swap the flat-alpha skill background for the new patterned one,
#         apply appPatternBackground() to the general content area. ---
ma_path = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(ma_path, "r") as f:
    content = f.read()

old_import = "import com.yourname.idlerpg.ui.theme.skillThemeBackground\nimport androidx.compose.foundation.background\n"
new_import = (
    "import com.yourname.idlerpg.ui.theme.skillPatternBackground\n"
    "import com.yourname.idlerpg.ui.theme.appPatternBackground\n"
    "import androidx.compose.foundation.background\n"
)
assert content.count(old_import) == 1, "skillThemeBackground import anchor not found or not unique"
content = content.replace(old_import, new_import, 1)

old_skill_box = '''                                is SkillsScreenState.Detail -> allSkills[screen.skillId]?.let {
                                    val skillBackground = skillThemeBackground(screen.skillId)
                                    val skillBoxModifier = if (skillBackground != null) {
                                        Modifier.fillMaxSize().background(skillBackground)
                                    } else {
                                        Modifier.fillMaxSize()
                                    }
                                    Box(modifier = skillBoxModifier) {'''
new_skill_box = '''                                is SkillsScreenState.Detail -> allSkills[screen.skillId]?.let {
                                    Box(modifier = Modifier.fillMaxSize().skillPatternBackground(screen.skillId)) {'''
assert content.count(old_skill_box) == 1, "skill detail Box block not found or not unique"
content = content.replace(old_skill_box, new_skill_box, 1)

old_content_box = "                        Box(modifier = Modifier.weight(1f)) {\n"
new_content_box = "                        Box(modifier = Modifier.weight(1f).appPatternBackground()) {\n"
assert content.count(old_content_box) == 1, "general content Box not found or not unique"
content = content.replace(old_content_box, new_content_box, 1)

with open(ma_path, "w") as f:
    f.write(content)
print("OK: patched " + ma_path)

# --- 3. SideRail.kt: swap flat surface color for the patterned rail background. ---
sr_path = "app/src/main/kotlin/com/yourname/idlerpg/ui/navigation/SideRail.kt"
if not os.path.exists(sr_path):
    # Same flat-file convention as everything else in this repo.
    sr_path = "app/src/main/kotlin/com/yourname/idlerpg/SideRail.kt"
with open(sr_path, "r") as f:
    content = f.read()

old_sr_import = "import androidx.compose.ui.unit.dp\n"
new_sr_import = "import androidx.compose.ui.unit.dp\nimport com.yourname.idlerpg.ui.theme.railPatternBackground\n"
assert content.count(old_sr_import) == 1, "dp import anchor not found or not unique in SideRail.kt"
content = content.replace(old_sr_import, new_sr_import, 1)

old_sr_bg = "            .fillMaxHeight()\n            .background(MaterialTheme.colorScheme.surface)\n            .animateContentSize()"
new_sr_bg = "            .fillMaxHeight()\n            .railPatternBackground()\n            .animateContentSize()"
assert content.count(old_sr_bg) == 1, "SideRail background line not found or not unique"
content = content.replace(old_sr_bg, new_sr_bg, 1)

with open(sr_path, "w") as f:
    f.write(content)
print("OK: patched " + sr_path)
