package com.yourname.idlerpg.ui.theme

import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.runtime.Composable
import androidx.compose.ui.draw.paint
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.graphics.ImageShader
import androidx.compose.ui.graphics.ShaderBrush
import androidx.compose.ui.graphics.TileMode
import androidx.compose.ui.res.imageResource
import com.yourname.idlerpg.R

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
private const val PATTERN_LINE_ALPHA = 0.045f
private const val GRADIENT_BOTTOM_ALPHA = 0.20f

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

// =========================================================
// MINING - themed background (test case for the per-skill rollout).
// A large rotated pickaxe silhouette watermark, tiled A-frame mine-
// support trusses (like timber props down a shaft), and scattered
// ore-glint diamonds, layered on the existing gradient base.
// =========================================================
private fun DrawScope.drawPickaxeSilhouette(color: Color, center: Offset, scale: Float, rotationDegrees: Float) {
    rotate(rotationDegrees, pivot = center) {
        val handleLength = 220f * scale
        val handleWidth = 10f * scale
        drawLine(
            color = color,
            start = Offset(center.x, center.y - handleLength / 2f),
            end = Offset(center.x, center.y + handleLength / 2f),
            strokeWidth = handleWidth,
            cap = StrokeCap.Round
        )
        val headY = center.y - handleLength / 2f
        val bladeSpan = 95f * scale
        val headPath = Path().apply {
            moveTo(center.x - bladeSpan, headY - bladeSpan * 0.5f)
            quadraticBezierTo(center.x, headY - bladeSpan * 0.05f, center.x + bladeSpan, headY - bladeSpan * 0.5f)
        }
        drawPath(path = headPath, color = color, style = Stroke(width = handleWidth * 0.85f, cap = StrokeCap.Round))
    }
}

private fun DrawScope.drawMineSupportTrusses(color: Color) {
    val spacing = 170f * density
    var y = spacing * 0.4f
    while (y < size.height) {
        val topY = y - 55f * density
        val bottomY = y + 55f * density
        val leftX = size.width * 0.10f
        val rightX = size.width * 0.90f
        val midX = size.width / 2f
        drawLine(color = color, start = Offset(leftX, bottomY), end = Offset(midX, topY), strokeWidth = 2.5f)
        drawLine(color = color, start = Offset(rightX, bottomY), end = Offset(midX, topY), strokeWidth = 2.5f)
        drawLine(color = color, start = Offset(leftX, bottomY), end = Offset(rightX, bottomY), strokeWidth = 2.5f)
        y += spacing
    }
}

private fun DrawScope.drawOreGlints(color: Color) {
    val relativePositions = listOf(
        Offset(0.15f, 0.20f), Offset(0.68f, 0.10f), Offset(0.33f, 0.52f),
        Offset(0.82f, 0.45f), Offset(0.52f, 0.76f), Offset(0.10f, 0.83f),
        Offset(0.92f, 0.80f)
    )
    relativePositions.forEach { rel ->
        val cx = rel.x * size.width
        val cy = rel.y * size.height
        val r = 5f * density
        val diamond = Path().apply {
            moveTo(cx, cy - r)
            lineTo(cx + r, cy)
            lineTo(cx, cy + r)
            lineTo(cx - r, cy)
            close()
        }
        drawPath(path = diamond, color = color)
    }
}

// Real generated image asset (res/drawable/bg_mining_pickaxes.webp) - a
// tessellated angled-pickaxe wallpaper pattern, TRUE-TILED via
// ImageShader/TileMode.Repeated so icon size stays fixed regardless of
// screen size (Crop-to-fill previously stretched one copy to cover the
// whole screen, which is what made icons look oversized).
@Composable
fun Modifier.miningThemedBackground(): Modifier {
    val imageBitmap = ImageBitmap.imageResource(id = R.drawable.bg_mining_pickaxes)
    return this.drawBehind {
        drawRect(brush = ShaderBrush(ImageShader(imageBitmap, TileMode.Repeated, TileMode.Repeated)))
    }
}

// Per-skill themed background. MINING gets its own thematic scene;
// every other skill falls through to the generic tinted pattern until
// its own themed background is added the same way.
@Composable
fun Modifier.skillPatternBackground(skillId: String): Modifier = when (skillId) {
    "MINING" -> this.miningThemedBackground()
    else -> this.proceduralThemeBackground(baseColor = skillThemeColor(skillId) ?: MutedTeal)
}

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
