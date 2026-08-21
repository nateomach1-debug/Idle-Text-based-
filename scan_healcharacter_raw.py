"""
Discovery script - NOT a code-modifying patch.

Fixes the previous script's bug (backward "fun " search missed modifiers
like "private fun"). This just prints a plain, generous raw context
window around every combatService.healCharacter occurrence in
GameViewModel.kt, no clever function-boundary detection.

Writes one new file: repo_healcharacter_raw_context.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_healcharacter_raw_context.txt"

path = os.path.join(BASE, "GameViewModel.kt")
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

lines_out = []
lines_out.append("=" * 70)
lines_out.append("GameViewModel.kt - raw context around every healCharacter occurrence")
lines_out.append("=" * 70)

found_any = False
for i, line in enumerate(lines):
    if "healCharacter" in line:
        found_any = True
        start = max(0, i - 25)
        end = min(len(lines), i + 15)
        lines_out.append(f"\n--- occurrence at line {i+1} ---")
        for j in range(start, end):
            marker = ">> " if j == i else "   "
            lines_out.append(f"{marker}{j+1}: {lines[j].rstrip()}")

if not found_any:
    lines_out.append("No occurrences found")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
