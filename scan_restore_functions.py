"""
Discovery script - NOT a code-modifying patch.

Finds every "fun restore*" function signature across all files (the
reuse pattern for applying saved state back into live services), plus
every call site of GameStateRepository(...).load() or "load()" near
"GameStateRepository", to find how/whether loaded state currently gets
applied.

Writes one new file: repo_restore_functions_and_load_callsite.txt
"""

import os
import re

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_restore_functions_and_load_callsite.txt"

lines_out = []
lines_out.append("=" * 70)
lines_out.append("All 'fun restore*' signatures across all files")
lines_out.append("=" * 70)

restore_re = re.compile(r"fun restore\w*\([^)]*\)")

for fname in sorted(os.listdir(BASE)):
    if not fname.endswith(".kt"):
        continue
    fpath = os.path.join(BASE, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    matches = restore_re.findall(content)
    if matches:
        lines_out.append(f"\n--- {fname} ---")
        for m in matches:
            lines_out.append(f"  {m}")

lines_out.append("")
lines_out.append("=" * 70)
lines_out.append("Search for '.load()' or 'GameStateRepository' call sites")
lines_out.append("=" * 70)

for fname in sorted(os.listdir(BASE)):
    if not fname.endswith(".kt"):
        continue
    fpath = os.path.join(BASE, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        flines = f.readlines()
    matches = [i for i, l in enumerate(flines) if "GameStateRepository" in l or ".load()" in l or "gameStateRepository" in l]
    if matches:
        lines_out.append(f"\n--- {fname} ---")
        for i in matches:
            start = max(0, i - 3)
            end = min(len(flines), i + 15)
            lines_out.append(f"  [line {i+1}]")
            for j in range(start, end):
                lines_out.append(f"    {j+1}: {flines[j].rstrip()}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
