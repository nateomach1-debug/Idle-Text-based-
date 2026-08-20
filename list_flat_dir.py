"""
Discovery script v2 - NOT a code-modifying patch.

Repo uses a flat file layout despite package names (confirmed via
SideRail.kt living directly in the base package dir, not in ui/navigation/).
This lists every .kt file directly under the base package directory so we
can identify all screen files by name.

Writes one new file: repo_discovery_flat_listing.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_discovery_flat_listing.txt"

lines = []
lines.append("=" * 70)
lines.append(f"Flat listing of: {BASE}")
lines.append("=" * 70)

if not os.path.isdir(BASE):
    lines.append(f"!!! DIRECTORY NOT FOUND: {BASE}")
else:
    entries = sorted(os.listdir(BASE))
    for entry in entries:
        full = os.path.join(BASE, entry)
        kind = "DIR" if os.path.isdir(full) else "FILE"
        size = os.path.getsize(full) if os.path.isfile(full) else ""
        lines.append(f"  [{kind}] {entry}  {size}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Wrote {OUTPUT_PATH}")
