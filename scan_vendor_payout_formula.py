"""
Discovery script - NOT a code-modifying patch.

Finds the exact sellToVendor() function body in EconomyMarketSystem.kt
to get the precise base-value accessor/multiplier used for vendor
payout, since the client now needs to compute this value itself before
sending it to the new server-side RPC.

Writes one new file: repo_vendor_payout_formula.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_vendor_payout_formula.txt"

path = os.path.join(BASE, "EconomyMarketSystem.kt")
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

lines_out = []
for i, line in enumerate(lines):
    if "fun sellToVendor" in line or "baseValue" in line or "vendorPrice" in line or "vendorPayout" in line:
        start = max(0, i - 2)
        end = min(len(lines), i + 15)
        lines_out.append(f"--- around line {i+1} ---")
        for j in range(start, end):
            lines_out.append(f"{j+1}: {lines[j].rstrip()}")
        lines_out.append("")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
