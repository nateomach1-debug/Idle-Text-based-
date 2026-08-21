"""
Discovery script - NOT a code-modifying patch.

Gets full context around GameViewModel.kt's existing
combatService.healCharacter(...) call (line ~691) to see the enclosing
function's name/signature and whether it's combat-gated, plus checks
how onUseItem is currently wired to InventoryScreen in MainActivity.kt.

Writes one new file: repo_use_item_context.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_use_item_context.txt"

lines_out = []
lines_out.append("=" * 70)
lines_out.append("GameViewModel.kt - context around combatService.healCharacter call")
lines_out.append("=" * 70)

path = os.path.join(BASE, "GameViewModel.kt")
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

target_idx = None
for i, line in enumerate(lines):
    if "combatService.healCharacter" in line:
        target_idx = i
        break

if target_idx is not None:
    # walk backward to find the enclosing "fun " line
    fun_start = target_idx
    depth_check = 0
    for j in range(target_idx, -1, -1):
        if lines[j].strip().startswith("fun "):
            fun_start = j
            break
    # print from fun_start to ~40 lines after target, or until a line that
    # looks like a new top-level fun/closing brace at same indent as fun_start
    fun_indent = len(lines[fun_start]) - len(lines[fun_start].lstrip())
    end_idx = target_idx + 40
    for k in range(fun_start + 1, min(len(lines), target_idx + 60)):
        stripped = lines[k]
        indent = len(stripped) - len(stripped.lstrip())
        if stripped.strip() == "}" and indent == fun_indent:
            end_idx = k
            break
    for i in range(fun_start, min(len(lines), end_idx + 1)):
        lines_out.append(f"{i+1}: {lines[i].rstrip()}")
else:
    lines_out.append("healCharacter call not found")

lines_out.append("")
lines_out.append("=" * 70)
lines_out.append("MainActivity.kt - onUseItem wiring to InventoryScreen")
lines_out.append("=" * 70)

path = os.path.join(BASE, "MainActivity.kt")
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "onUseItem" in line or "InventoryScreen(" in line:
        start = max(0, i - 2)
        end = min(len(lines), i + 8)
        lines_out.append(f"--- around line {i+1} ---")
        for j in range(start, end):
            lines_out.append(f"{j+1}: {lines[j].rstrip()}")
        lines_out.append("")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
