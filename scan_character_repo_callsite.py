"""
Discovery script - NOT a code-modifying patch.

Gets full SupabaseCharacterRepository.kt content, plus a generous raw
context window around every place GameViewModel.kt calls
getOrCreateCharacter, so the reconciliation patch can be written against
exact current text.

Writes one new file: repo_character_repo_and_callsite.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_character_repo_and_callsite.txt"

lines_out = []
lines_out.append("=" * 70)
lines_out.append("SupabaseCharacterRepository.kt (full content)")
lines_out.append("=" * 70)

path = os.path.join(BASE, "SupabaseCharacterRepository.kt")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
lines_out.append(content)

lines_out.append("")
lines_out.append("=" * 70)
lines_out.append("GameViewModel.kt - context around getOrCreateCharacter call(s)")
lines_out.append("=" * 70)

path = os.path.join(BASE, "GameViewModel.kt")
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "getOrCreateCharacter" in line or "Char sync error" in line or "Char id:" in line:
        start = max(0, i - 15)
        end = min(len(lines), i + 20)
        lines_out.append(f"\n--- around line {i+1} ---")
        for j in range(start, end):
            marker = ">> " if j == i else "   "
            lines_out.append(f"{marker}{j+1}: {lines[j].rstrip()}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
