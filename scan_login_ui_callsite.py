"""
Discovery script - NOT a code-modifying patch.

Finds every call site of gameViewModel.login(...) or just login(...)
across LoginScreen.kt and MainActivity.kt, to see how the UI currently
handles the synchronous return value, before converting login() to
properly await the cloud recovery attempt.

Writes one new file: repo_login_ui_callsite.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_login_ui_callsite.txt"

lines_out = []

for filename in ["LoginScreen.kt", "MainActivity.kt"]:
    path = os.path.join(BASE, filename)
    if not os.path.isfile(path):
        continue
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    matches = [i for i, l in enumerate(lines) if ".login(" in l or "onLogin" in l]
    if matches:
        lines_out.append(f"\n--- {filename} ---")
        for i in matches:
            start = max(0, i - 5)
            end = min(len(lines), i + 15)
            lines_out.append(f"  [line {i+1}]")
            for j in range(start, end):
                lines_out.append(f"    {j+1}: {lines[j].rstrip()}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
