"""
Discovery script - NOT a code-modifying patch.

Extracts the declarations/signatures of trainingSkill, allowedTrainingSkills,
and setTrainingSkill from GameViewModel.kt so we know exact types before
writing the item-8 patch (routing Skills-tab combat-skill taps into
training-location selection).

Writes one new file: repo_gameviewmodel_training_signatures.txt
"""

import os
import re

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(BASE, "GameViewModel.kt")
OUTPUT_PATH = "repo_gameviewmodel_training_signatures.txt"

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

keywords = ["trainingSkill", "allowedTrainingSkills", "setTrainingSkill", "SkillType"]

out_lines = []
out_lines.append("=" * 70)
out_lines.append("Lines in GameViewModel.kt matching training-skill keywords")
out_lines.append("(with 2 lines of context before/after each match)")
out_lines.append("=" * 70)
out_lines.append("")

matched_indices = set()
for i, line in enumerate(lines):
    if any(k in line for k in keywords):
        matched_indices.add(i)

for i in sorted(matched_indices):
    start = max(0, i - 2)
    end = min(len(lines), i + 3)
    out_lines.append(f"--- around line {i+1} ---")
    for j in range(start, end):
        marker = ">> " if j == i else "   "
        out_lines.append(f"{marker}{j+1}: {lines[j].rstrip()}")
    out_lines.append("")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))

print(f"Wrote {OUTPUT_PATH}")
