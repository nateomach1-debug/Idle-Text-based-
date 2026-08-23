"""
Discovery script - NOT a code-modifying patch.

Gets the full load() function and SavedGameState data class from
GameStateRepository.kt, plus finds wherever SavedGameState gets applied
back into live services (likely on app startup) - this is the exact
machinery to reuse for cloud-recovery.

Writes one new file: repo_load_and_apply_state.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_load_and_apply_state.txt"

lines_out = []
lines_out.append("=" * 70)
lines_out.append("GameStateRepository.kt - load() and SavedGameState (lines 188-388)")
lines_out.append("=" * 70)

path = os.path.join(BASE, "GameStateRepository.kt")
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()
for i in range(187, len(lines)):
    lines_out.append(f"{i+1}: {lines[i].rstrip()}")

lines_out.append("")
lines_out.append("=" * 70)
lines_out.append("Search all files for 'SavedGameState' usage (where it's applied)")
lines_out.append("=" * 70)

for fname in sorted(os.listdir(BASE)):
    if not fname.endswith(".kt"):
        continue
    fpath = os.path.join(BASE, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        flines = f.readlines()
    matches = [i for i, l in enumerate(flines) if "SavedGameState" in l]
    if matches:
        lines_out.append(f"\n--- {fname} ---")
        for i in matches:
            start = max(0, i - 2)
            end = min(len(flines), i + 3)
            lines_out.append(f"  [line {i+1}]")
            for j in range(start, end):
                lines_out.append(f"    {j+1}: {flines[j].rstrip()}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
