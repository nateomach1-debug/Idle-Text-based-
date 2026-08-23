"""
Discovery script - NOT a code-modifying patch.

Gets the full login(email, password) function in GameViewModel.kt (the
one calling accountService.login() then syncSupabaseAuth(isNewAccount
= false)), so the Login-button Supabase-recovery fallback can be
written against exact current text.

Writes one new file: repo_login_function_full.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_login_function_full.txt"

path = os.path.join(BASE, "GameViewModel.kt")
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

lines_out = []
lines_out.append("=" * 70)
lines_out.append("GameViewModel.kt - fun login(...) full context")
lines_out.append("=" * 70)

for i, line in enumerate(lines):
    if line.strip().startswith("fun login(") or "fun login(" in line:
        start = max(0, i - 2)
        end = min(len(lines), i + 40)
        lines_out.append(f"--- around line {i+1} ---")
        for j in range(start, end):
            lines_out.append(f"{j+1}: {lines[j].rstrip()}")
        lines_out.append("")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
