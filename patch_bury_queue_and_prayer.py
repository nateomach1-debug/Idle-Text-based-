#!/usr/bin/env python3
"""
Guarded patch: themed Mining background (test case for the per-skill
background rollout). Pure procedural Canvas drawing, same approach as
the existing proceduralThemeBackground - no image assets.

Adds: drawPickaxeSilhouette, drawMineSupportTrusses, drawOreGlints,
Modifier.miningThemedBackground(). Wires MINING into skillPatternBackground
via a when-branch (falls through to the existing generic tinted pattern
for every other skill, unchanged).
"""
import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(ROOT, "PatternBackground.kt")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. New imports
old_imports = (
    "import androidx.compose.ui.Modifier\n"
    "import androidx.compose.ui.draw.drawBehind\n"
    "import androidx.compose.ui.geometry.Offset\n"
    "import androidx.compose.ui.graphics.Brush\n"
    "import androidx.compose.ui.graphics.Color\n"
    "import androidx.compose.ui.graphics.drawscope.DrawScope\n"
)
new_imports = (
    "import androidx.compose.ui.Modifier\n"
    "import androidx.compose.ui.draw.drawBehind\n"
    "import androidx.compose.ui.geometry.Offset\n"
    "import androidx.compose.ui.graphics.Brush\n"
    "import androidx.compose.ui.graphics.Color\n"
    "import androidx.compose.ui.graphics.Path\n"
    "import androidx.compose.ui.graphics.StrokeCap\n"
    "import androidx.compose.ui.graphics.drawscope.DrawScope\n"
    "import androidx.compose.ui.graphics.drawscope.Stroke\n"
    "import androidx.compose.ui.graphics.drawscope.rotate\n"
)

if "import androidx.compose.ui.graphics.Path\n" in content:
    print("SKIP (imports already present)")
else:
    if content.count(old_imports) != 1:
        raise RuntimeError("Import anchor not found or not unique")
    content = content.replace(old_imports, new_imports)
    print("PATCHED: imports")

# 2. New drawing helpers + miningThemedBackground, inserted right before
#    skillPatternBackground's existing definition.
old_skill_fn = (
    "// Per-skill themed background. Falls back to MutedTeal for any skillId\n"
    "// without a mapped color (shouldn't normally happen from the Skills tab).\n"
    "fun Modifier.skillPatternBackground(skillId: String): Modifier =\n"
    "    this.proceduralThemeBackground(baseColor = skillThemeColor(skillId) ?: MutedTeal)\n"
)
new_skill_fn = (
    "// =========================================================\n"
    "// MINING - themed background (test case for the per-skill rollout).\n"
    "// A large rotated pickaxe silhouette watermark, tiled A-frame mine-\n"
    "// support trusses (like timber props down a shaft), and scattered\n"
    "// ore-glint diamonds, layered on the existing gradient base.\n"
    "// =========================================================\n"
    "private fun DrawScope.drawPickaxeSilhouette(color: Color, center: Offset, scale: Float, rotationDegrees: Float) {\n"
    "    rotate(rotationDegrees, pivot = center) {\n"
    "        val handleLength = 220f * scale\n"
    "        val handleWidth = 10f * scale\n"
    "        drawLine(\n"
    "            color = color,\n"
    "            start = Offset(center.x, center.y - handleLength / 2f),\n"
    "            end = Offset(center.x, center.y + handleLength / 2f),\n"
    "            strokeWidth = handleWidth,\n"
    "            cap = StrokeCap.Round\n"
    "        )\n"
    "        val headY = center.y - handleLength / 2f\n"
    "        val bladeSpan = 95f * scale\n"
    "        val headPath = Path().apply {\n"
    "            moveTo(center.x - bladeSpan, headY - bladeSpan * 0.5f)\n"
    "            quadraticBezierTo(center.x, headY - bladeSpan * 0.05f, center.x + bladeSpan, headY - bladeSpan * 0.5f)\n"
    "        }\n"
    "        drawPath(path = headPath, color = color, style = Stroke(width = handleWidth * 0.85f, cap = StrokeCap.Round))\n"
    "    }\n"
    "}\n"
    "\n"
    "private fun DrawScope.drawMineSupportTrusses(color: Color) {\n"
    "    val spacing = 170f * density\n"
    "    var y = spacing * 0.4f\n"
    "    while (y < size.height) {\n"
    "        val topY = y - 55f * density\n"
    "        val bottomY = y + 55f * density\n"
    "        val leftX = size.width * 0.10f\n"
    "        val rightX = size.width * 0.90f\n"
    "        val midX = size.width / 2f\n"
    "        drawLine(color = color, start = Offset(leftX, bottomY), end = Offset(midX, topY), strokeWidth = 2.5f)\n"
    "        drawLine(color = color, start = Offset(rightX, bottomY), end = Offset(midX, topY), strokeWidth = 2.5f)\n"
    "        drawLine(color = color, start = Offset(leftX, bottomY), end = Offset(rightX, bottomY), strokeWidth = 2.5f)\n"
    "        y += spacing\n"
    "    }\n"
    "}\n"
    "\n"
    "private fun DrawScope.drawOreGlints(color: Color) {\n"
    "    val relativePositions = listOf(\n"
    "        Offset(0.15f, 0.20f), Offset(0.68f, 0.10f), Offset(0.33f, 0.52f),\n"
    "        Offset(0.82f, 0.45f), Offset(0.52f, 0.76f), Offset(0.10f, 0.83f),\n"
    "        Offset(0.92f, 0.80f)\n"
    "    )\n"
    "    relativePositions.forEach { rel ->\n"
    "        val cx = rel.x * size.width\n"
    "        val cy = rel.y * size.height\n"
    "        val r = 5f * density\n"
    "        val diamond = Path().apply {\n"
    "            moveTo(cx, cy - r)\n"
    "            lineTo(cx + r, cy)\n"
    "            lineTo(cx, cy + r)\n"
    "            lineTo(cx - r, cy)\n"
    "            close()\n"
    "        }\n"
    "        drawPath(path = diamond, color = color)\n"
    "    }\n"
    "}\n"
    "\n"
    "fun Modifier.miningThemedBackground(): Modifier = this.drawBehind {\n"
    "    val baseColor = skillThemeColor(\"MINING\") ?: MutedTeal\n"
    "    val gradient = Brush.verticalGradient(\n"
    "        colors = listOf(CharcoalBackground, baseColor.copy(alpha = GRADIENT_BOTTOM_ALPHA))\n"
    "    )\n"
    "    drawRect(brush = gradient)\n"
    "    drawMineSupportTrusses(baseColor.copy(alpha = 0.10f))\n"
    "    drawOreGlints(ParchmentGold.copy(alpha = 0.30f))\n"
    "    drawPickaxeSilhouette(\n"
    "        color = baseColor.copy(alpha = 0.16f),\n"
    "        center = Offset(size.width * 0.78f, size.height * 0.32f),\n"
    "        scale = 1.3f,\n"
    "        rotationDegrees = -35f\n"
    "    )\n"
    "}\n"
    "\n"
    "// Per-skill themed background. MINING gets its own thematic scene;\n"
    "// every other skill falls through to the generic tinted pattern until\n"
    "// its own themed background is added the same way.\n"
    "fun Modifier.skillPatternBackground(skillId: String): Modifier = when (skillId) {\n"
    "    \"MINING\" -> this.miningThemedBackground()\n"
    "    else -> this.proceduralThemeBackground(baseColor = skillThemeColor(skillId) ?: MutedTeal)\n"
    "}\n"
)

if "fun Modifier.miningThemedBackground(): Modifier" in content:
    print("SKIP (mining background already added)")
else:
    if content.count(old_skill_fn) != 1:
        raise RuntimeError("skillPatternBackground anchor not found or not unique")
    content = content.replace(old_skill_fn, new_skill_fn)
    print("PATCHED: mining themed background + skillPatternBackground dispatch")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Done.")
