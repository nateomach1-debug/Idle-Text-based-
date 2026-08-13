path = "app/src/main/kotlin/com/yourname/idlerpg/Theme.kt"
with open(path, "r") as f:
    content = f.read()

# --- 1. Add per-skill theme colors right after the existing color palette block. ---
old_colors = '''val TextPrimary = Color(0xFFEDE8DD)
val TextSecondary = Color(0xFFA39E93)
'''
new_colors = '''val TextPrimary = Color(0xFFEDE8DD)
val TextSecondary = Color(0xFFA39E93)

// =========================================================
// PER-SKILL THEME COLORS
// Each is a single named constant, same pattern as the base
// palette above - easy to retune individually after testing
// on-device, no need to touch anything else.
// =========================================================

val MiningStone = Color(0xFF7D8188)
val WoodcuttingGreen = Color(0xFF4C6B3F)
val FishingBlue = Color(0xFF3E6E9E)
val FarmingTan = Color(0xFF8A7B4E)
val ThievingPurple = Color(0xFF5B3E75)
val SmithingOrange = Color(0xFFB5621F)
val CookingEmber = Color(0xFF8C3B2E)
val CraftingViolet = Color(0xFF6E4B8A)
val FletchingOlive = Color(0xFF6B6B3A)
val AlchemyToxic = Color(0xFF4E8C4A)
val MagicArcane = Color(0xFF5A4FCF)

// How strongly the skill color blends into the screen background.
// Placeholder value, same spirit as other tunable placeholders in
// this project - adjust after seeing it live.
private const val SKILL_THEME_BLEND_ALPHA = 0.35f

// Combat skills (Attack/Strength/Defense/Prayer/Archery) intentionally
// return null - they share the Combat screen rather than having their
// own detail page, and keep the existing deep-red danger theme.
fun skillThemeColor(skillId: String): Color? = when (skillId) {
    "MINING" -> MiningStone
    "WOODCUTTING" -> WoodcuttingGreen
    "FISHING" -> FishingBlue
    "FARMING" -> FarmingTan
    "THIEVING" -> ThievingPurple
    "SMITHING" -> SmithingOrange
    "COOKING" -> CookingEmber
    "CRAFTING" -> CraftingViolet
    "FLETCHING" -> FletchingOlive
    "ALCHEMY" -> AlchemyToxic
    "MAGIC" -> MagicArcane
    else -> null
}

fun skillThemeBackground(skillId: String): Color? =
    skillThemeColor(skillId)?.copy(alpha = SKILL_THEME_BLEND_ALPHA)
'''
assert content.count(old_colors) == 1, "color palette anchor not found or not unique"
content = content.replace(old_colors, new_colors, 1)

# --- 2. Fill the remaining 11 Typography slots, keeping the 4 existing ones untouched. ---
old_typography = '''val IdleRpgTypography = Typography(
    headlineMedium = TextStyle(
        fontFamily = HeaderFont,
        fontWeight = FontWeight.Bold,
        fontSize = 22.sp,
        color = TextPrimary
    ),
    titleMedium = TextStyle(
        fontFamily = HeaderFont,
        fontWeight = FontWeight.SemiBold,
        fontSize = 17.sp,
        color = TextPrimary
    ),
    bodyMedium = TextStyle(
        fontFamily = BodyFont,
        fontWeight = FontWeight.Normal,
        fontSize = 15.sp,
        color = TextPrimary
    ),
    labelSmall = TextStyle(
        fontFamily = BodyFont,
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        color = TextSecondary
    )
)'''
new_typography = '''val IdleRpgTypography = Typography(
    displayLarge = TextStyle(
        fontFamily = HeaderFont,
        fontWeight = FontWeight.Bold,
        fontSize = 40.sp,
        color = TextPrimary
    ),
    displayMedium = TextStyle(
        fontFamily = HeaderFont,
        fontWeight = FontWeight.Bold,
        fontSize = 34.sp,
        color = TextPrimary
    ),
    displaySmall = TextStyle(
        fontFamily = HeaderFont,
        fontWeight = FontWeight.Bold,
        fontSize = 28.sp,
        color = TextPrimary
    ),
    headlineLarge = TextStyle(
        fontFamily = HeaderFont,
        fontWeight = FontWeight.Bold,
        fontSize = 24.sp,
        color = TextPrimary
    ),
    headlineMedium = TextStyle(
        fontFamily = HeaderFont,
        fontWeight = FontWeight.Bold,
        fontSize = 22.sp,
        color = TextPrimary
    ),
    headlineSmall = TextStyle(
        fontFamily = HeaderFont,
        fontWeight = FontWeight.SemiBold,
        fontSize = 19.sp,
        color = TextPrimary
    ),
    titleLarge = TextStyle(
        fontFamily = HeaderFont,
        fontWeight = FontWeight.SemiBold,
        fontSize = 19.sp,
        color = TextPrimary
    ),
    titleMedium = TextStyle(
        fontFamily = HeaderFont,
        fontWeight = FontWeight.SemiBold,
        fontSize = 17.sp,
        color = TextPrimary
    ),
    titleSmall = TextStyle(
        fontFamily = HeaderFont,
        fontWeight = FontWeight.SemiBold,
        fontSize = 15.sp,
        color = TextPrimary
    ),
    bodyLarge = TextStyle(
        fontFamily = BodyFont,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        color = TextPrimary
    ),
    bodyMedium = TextStyle(
        fontFamily = BodyFont,
        fontWeight = FontWeight.Normal,
        fontSize = 15.sp,
        color = TextPrimary
    ),
    bodySmall = TextStyle(
        fontFamily = BodyFont,
        fontWeight = FontWeight.Normal,
        fontSize = 13.sp,
        color = TextPrimary
    ),
    labelLarge = TextStyle(
        fontFamily = BodyFont,
        fontWeight = FontWeight.Medium,
        fontSize = 13.sp,
        color = TextSecondary
    ),
    labelMedium = TextStyle(
        fontFamily = BodyFont,
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        color = TextSecondary
    ),
    labelSmall = TextStyle(
        fontFamily = BodyFont,
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        color = TextSecondary
    )
)'''
assert content.count(old_typography) == 1, "Typography block not found or not unique"
content = content.replace(old_typography, new_typography, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: Theme.kt patched (full 15-slot Typography scale, 11 skill colors, skillThemeColor()/skillThemeBackground() added).")
