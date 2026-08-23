"""
Discovery script - NOT a code-modifying patch.

Checks whether MainActivity.kt already imports rememberCoroutineScope
and kotlinx.coroutines.launch, needed to wrap onLogin's callback in a
coroutine so it can await the suspend login() function.

Writes one new file: repo_mainactivity_coroutine_imports.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_mainactivity_coroutine_imports.txt"

path = os.path.join(BASE, "MainActivity.kt")
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

lines_out = []
lines_out.append("=" * 70)
lines_out.append("MainActivity.kt - all import lines")
lines_out.append("=" * 70)
for i, line in enumerate(lines):
    if line.strip().startswith("import "):
        lines_out.append(f"{i+1}: {line.rstrip()}")

lines_out.append("")
lines_out.append("has rememberCoroutineScope import: " + str(any("rememberCoroutineScope" in l for l in lines)))
lines_out.append("has kotlinx.coroutines.launch import: " + str(any("import kotlinx.coroutines.launch" in l for l in lines)))
lines_out.append("has any 'rememberCoroutineScope()' usage: " + str(any("rememberCoroutineScope()" in l for l in lines)))

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
