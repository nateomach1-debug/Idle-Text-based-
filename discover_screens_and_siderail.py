"""
Discovery script - NOT a code-modifying patch.

Purpose: list every file under ui/screens/ and ui/navigation/, and dump the
full content of SideRail.kt, into a single output txt file so it can be
uploaded/read for planning the scrollable-pages + scrollable-sidebar +
landscape-formatting patch.

This does not modify any Kotlin source files. It only writes one new file:
    repo_discovery_screens_siderail.txt
at the repo root.
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
SCREENS_DIR = os.path.join(BASE, "ui", "screens")
NAV_DIR = os.path.join(BASE, "ui", "navigation")
OUTPUT_PATH = "repo_discovery_screens_siderail.txt"

lines = []

def list_dir(label, path):
    lines.append("=" * 70)
    lines.append(f"{label}  (path: {path})")
    lines.append("=" * 70)
    if not os.path.isdir(path):
        lines.append(f"!!! DIRECTORY NOT FOUND: {path}")
        lines.append("")
        return
    entries = sorted(os.listdir(path))
    if not entries:
        lines.append("(empty directory)")
    for entry in entries:
        full = os.path.join(path, entry)
        kind = "DIR" if os.path.isdir(full) else "FILE"
        size = os.path.getsize(full) if os.path.isfile(full) else ""
        lines.append(f"  [{kind}] {entry}  {size}")
    lines.append("")

list_dir("ui/screens contents", SCREENS_DIR)
list_dir("ui/navigation contents", NAV_DIR)

# Dump SideRail.kt content specifically, wherever it is found
siderail_path = None
for root, dirs, files in os.walk(BASE):
    if "SideRail.kt" in files:
        siderail_path = os.path.join(root, "SideRail.kt")
        break

lines.append("=" * 70)
lines.append("SideRail.kt full content")
lines.append("=" * 70)
if siderail_path is None:
    lines.append("!!! SideRail.kt NOT FOUND anywhere under " + BASE)
else:
    lines.append(f"(found at: {siderail_path})")
    lines.append("")
    with open(siderail_path, "r", encoding="utf-8") as f:
        lines.append(f.read())

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Wrote {OUTPUT_PATH}")
