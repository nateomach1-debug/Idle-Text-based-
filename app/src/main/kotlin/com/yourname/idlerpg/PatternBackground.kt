package com.yourname.idlerpg.ui.theme

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
