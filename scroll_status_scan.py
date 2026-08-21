"""
Discovery script v3 - NOT a code-modifying patch.

Scans every known screen file for signs it's already scrollable
(verticalScroll, LazyColumn, LazyVerticalGrid, LazyRow) vs. plain Column/Box
with no scroll handling. Writes a short report so we know exactly which
files need the scrollable-pages patch.

Writes one new file: repo_scroll_status_report.txt
"""

import os
import re

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_scroll_status_report.txt"

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
]

SCROLL_MARKERS = ["verticalScroll", "horizontalScroll"]
LAZY_MARKERS = ["LazyColumn", "LazyVerticalGrid", "LazyRow", "LazyVerticalStaggeredGrid"]

lines = []
lines.append("=" * 70)
lines.append("Scroll status report")
lines.append("=" * 70)
lines.append("")

for filename in SCREEN_FILES:
    path = os.path.join(BASE, filename)
    if not os.path.isfile(path):
        lines.append(f"{filename}: !!! FILE NOT FOUND")
        continue

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    has_scroll = any(m in content for m in SCROLL_MARKERS)
    has_lazy = any(m in content for m in LAZY_MARKERS)

    # count top-level Column( and Box( occurrences as a rough complexity signal
    column_count = len(re.findall(r"\bColumn\s*\(", content))
    box_count = len(re.findall(r"\bBox\s*\(", content))

    if has_scroll or has_lazy:
        status = "OK - already scrollable"
    else:
        status = "NEEDS FIX - no scroll/lazy found"

    lines.append(f"{filename}:")
    lines.append(f"  status: {status}")
    lines.append(f"  verticalScroll/horizontalScroll present: {has_scroll}")
    lines.append(f"  Lazy* present: {has_lazy}")
    lines.append(f"  Column( count: {column_count}, Box( count: {box_count}")
    lines.append("")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Wrote {OUTPUT_PATH}")
