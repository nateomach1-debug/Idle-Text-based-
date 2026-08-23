"""
Discovery script - NOT a code-modifying patch.

Finds AccountService's function(s) for looking up a live Account by id
(needed after restoreAccount(export) to get the real Account domain
object, since AccountExport != Account).

Writes one new file: repo_accountservice_lookup.txt
"""

import os
import re

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_accountservice_lookup.txt"

lines_out = []
lines_out.append("=" * 70)
lines_out.append("Search for account-lookup functions across all files")
lines_out.append("=" * 70)

pattern = re.compile(r"fun \w*[Aa]ccount\w*\([^)]*\)\s*:\s*Account")

for fname in sorted(os.listdir(BASE)):
    if not fname.endswith(".kt"):
        continue
    fpath = os.path.join(BASE, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    matches = pattern.findall(content)
    if matches:
        lines_out.append(f"\n--- {fname} ---")
        for m in matches:
            lines_out.append(f"  {m}")

lines_out.append("")
lines_out.append("=" * 70)
lines_out.append("Full restoreAccount function (to see what it does with the id)")
lines_out.append("=" * 70)

path = os.path.join(BASE, "AccountCharacterSystem.kt")
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "fun restoreAccount" in line or "fun login(" in line:
        start = max(0, i - 1)
        end = min(len(lines), i + 20)
        lines_out.append(f"\n--- around line {i+1} ---")
        for j in range(start, end):
            lines_out.append(f"{j+1}: {lines[j].rstrip()}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
