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
# Theme.kt - buildIdleRpgTypography: stop passing color+brush together.
# Compose's TextStyle constructor doesn't resolve when both are supplied
# as named args at once in this pinned version - it falls back to a
# completely unrelated TextStyle(spanStyle, paragraphStyle) overload,
# producing the "No parameter with name 'fontFamily'" style errors.
# Fix: build each TextStyle with color OR brush via a small helper,
# never both in the same constructor call.
# ===========================================================
old = '''private fun buildIdleRpgTypography(
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
new = '''private fun styledText(
    fontFamily: FontFamily,
    fontWeight: FontWeight,
    fontSize: androidx.compose.ui.unit.TextUnit,
    color: Color,
    brush: Brush?,
    shadow: Shadow?
): TextStyle = if (brush != null) {
    TextStyle(fontFamily = fontFamily, fontWeight = fontWeight, fontSize = fontSize, brush = brush, shadow = shadow)
} else {
    TextStyle(fontFamily = fontFamily, fontWeight = fontWeight, fontSize = fontSize, color = color, shadow = shadow)
}

private fun buildIdleRpgTypography(
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
        displayLarge = styledText(HeaderFont, FontWeight.Bold, 40.sp, primary, primaryBrush, shadow),
        displayMedium = styledText(HeaderFont, FontWeight.Bold, 34.sp, primary, primaryBrush, shadow),
        displaySmall = styledText(HeaderFont, FontWeight.Bold, 28.sp, primary, primaryBrush, shadow),
        headlineLarge = styledText(HeaderFont, FontWeight.Bold, 24.sp, primary, primaryBrush, shadow),
        headlineMedium = styledText(HeaderFont, FontWeight.Bold, 22.sp, primary, primaryBrush, shadow),
        headlineSmall = styledText(HeaderFont, FontWeight.SemiBold, 19.sp, primary, primaryBrush, shadow),
        titleLarge = styledText(HeaderFont, FontWeight.SemiBold, 19.sp, primary, primaryBrush, shadow),
        titleMedium = styledText(HeaderFont, FontWeight.SemiBold, 17.sp, primary, primaryBrush, shadow),
        titleSmall = styledText(HeaderFont, FontWeight.SemiBold, 15.sp, primary, primaryBrush, shadow),
        bodyLarge = styledText(BodyFont, FontWeight.Normal, 16.sp, primary, primaryBrush, shadow),
        bodyMedium = styledText(BodyFont, FontWeight.Normal, 15.sp, primary, primaryBrush, shadow),
        bodySmall = styledText(BodyFont, FontWeight.Normal, 13.sp, primary, primaryBrush, shadow),
        labelLarge = styledText(BodyFont, FontWeight.Medium, 13.sp, secondary, secondaryBrush, shadow),
        labelMedium = styledText(BodyFont, FontWeight.Medium, 12.sp, secondary, secondaryBrush, shadow),
        labelSmall = styledText(BodyFont, FontWeight.Medium, 12.sp, secondary, secondaryBrush, shadow)
    )
}'''
results.append(guarded_replace(THEME, old, new, "Theme.kt: styledText helper avoids color+brush overload conflict"))

print()
print("=== Brace balance check ===")
check_braces(THEME)

if not all(results):
    print()
    print("One or more edits FAILED - review output above before committing.")
    sys.exit(1)

print()
print("All edits applied successfully.")
