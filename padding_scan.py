"""
Discovery script v4 - NOT a code-modifying patch.

Scans every screen file for hardcoded .padding(...dp) and
Spacer(modifier = Modifier.height/width(...dp)) calls so we can see
current spacing values before designing the landscape-density reduction.

Writes one new file: repo_padding_values_report.txt
"""

import os
import re

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_padding_values_report.txt"

SCREEN_FILES = [
    "CharacterSelectScreen.kt",
    "CombatViewScreen.kt",
    "EquipmentScreen.kt",
    "GuildCreateJoinScreen.kt",
    "GuildHomeScreen.kt",
    "HomeScreen.kt",
    "InventoryScreen.kt",
    "LoadoutScreen.kt",
    "LoginScreen.kt",
    "MarketScreen.kt",
    "ModerationScreen.kt",
    "OrderBookScreen.kt",
    "SkillDetailScreen.kt",
    "SkillsScreen.kt",
    "SmithingScreen.kt",
    "ZoneSelectScreen.kt",
    "SideRail.kt",
    "MainActivity.kt",
]

PADDING_RE = re.compile(r"\.padding\([^)]*\)")
SPACER_RE = re.compile(r"Spacer\(modifier = Modifier\.(height|width)\(([\d.]+)\.dp\)\)")
FONT_RE = re.compile(r"MaterialTheme\.typography\.\w+")

lines = []
lines.append("=" * 70)
lines.append("Padding / Spacer / typography usage report")
lines.append("=" * 70)
lines.append("")

for filename in SCREEN_FILES:
    path = os.path.join(BASE, filename)
    if not os.path.isfile(path):
        lines.append(f"{filename}: !!! FILE NOT FOUND")
        continue

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    paddings = PADDING_RE.findall(content)
    spacers = SPACER_RE.findall(content)
    top_level_column_padding = re.findall(r"fillMaxSize\(\)\s*\n?\s*\.padding\(([\d.]+)\.dp\)", content)

    lines.append(f"{filename}:")
    lines.append(f"  .padding(...) calls ({len(paddings)}): {paddings[:15]}{'...' if len(paddings) > 15 else ''}")
    lines.append(f"  Spacer height/width dp values ({len(spacers)}): {[s[1] for s in spacers][:15]}")
    lines.append(f"  top-level fillMaxSize().padding(Xdp) value(s): {top_level_column_padding}")
    lines.append("")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Wrote {OUTPUT_PATH}")
