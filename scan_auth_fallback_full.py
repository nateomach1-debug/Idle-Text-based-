"""
Discovery script - NOT a code-modifying patch.

Gets full raw context (lines 70-160) of GameViewModel.kt to see the
existing signUp/signIn fallback logic in full, since the keyword scan
showed a confusing order (signUp -> signIn -> catch -> signUp again).

Writes one new file: repo_auth_fallback_full.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_auth_fallback_full.txt"

path = os.path.join(BASE, "GameViewModel.kt")
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

lines_out = []
lines_out.append("=" * 70)
lines_out.append("GameViewModel.kt lines 60-170 (full auth flow context)")
lines_out.append("=" * 70)
for i in range(59, min(170, len(lines))):
    lines_out.append(f"{i+1}: {lines[i].rstrip()}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
