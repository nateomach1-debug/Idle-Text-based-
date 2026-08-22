"""
Discovery script - NOT a code-modifying patch.

Finds GameStateRepository.kt (local game_state.json save/load) and any
top-level "GameState"-shaped data class, to see exactly what fields need
to be persisted server-side for real cloud save. Also finds
AccountCharacterSystem.kt's local login/account-creation flow in full,
since that's what needs to reconcile with server data.

Writes one new file: repo_gamestate_and_account_flow.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_gamestate_and_account_flow.txt"

lines_out = []

for filename in ["GameStateRepository.kt", "AccountCharacterSystem.kt"]:
    path = os.path.join(BASE, filename)
    lines_out.append("=" * 70)
    lines_out.append(filename)
    lines_out.append("=" * 70)
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        lines_out.append(f"(total lines: {len(content.splitlines())})")
        lines_out.append(content)
    else:
        lines_out.append("NOT FOUND")
    lines_out.append("")

# Also find whatever data class represents the full local save shape
lines_out.append("=" * 70)
lines_out.append("Search for 'data class GameState' or similar across all files")
lines_out.append("=" * 70)
for fname in sorted(os.listdir(BASE)):
    if not fname.endswith(".kt"):
        continue
    fpath = os.path.join(BASE, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    if "data class GameState" in content or "class GameState" in content:
        lines_out.append(f"\nFound in {fname}:")
        idx = content.find("GameState")
        lines_out.append(content[max(0,idx-50):idx+500])

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
