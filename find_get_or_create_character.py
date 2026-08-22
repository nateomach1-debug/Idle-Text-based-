"""
Discovery script - NOT a code-modifying patch.

Finds the full SupabaseCharacterRepository.kt (already known ~21 lines)
plus searches the entire repo for any .sql files or migration files that
might define the get_or_create_character RPC function itself (this
logic may live server-side in Supabase's SQL editor rather than in this
repo, in which case it won't be found here at all - important to know
either way).

Writes one new file: repo_get_or_create_character_search.txt
"""

import os

REPO_ROOT = "."
OUTPUT_PATH = "repo_get_or_create_character_search.txt"

lines_out = []
lines_out.append("=" * 70)
lines_out.append("SupabaseCharacterRepository.kt (full content)")
lines_out.append("=" * 70)

path = "app/src/main/kotlin/com/yourname/idlerpg/SupabaseCharacterRepository.kt"
if os.path.isfile(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    lines_out.append(content)
else:
    lines_out.append("NOT FOUND")

lines_out.append("")
lines_out.append("=" * 70)
lines_out.append("Searching entire repo for .sql files or 'get_or_create_character' mentions")
lines_out.append("=" * 70)

for root, dirs, files in os.walk(REPO_ROOT):
    # skip .git and build directories to keep this fast/relevant
    dirs[:] = [d for d in dirs if d not in (".git", "build", ".gradle", "node_modules")]
    for fname in files:
        fpath = os.path.join(root, fname)
        if fname.endswith(".sql"):
            lines_out.append(f"\n--- SQL FILE FOUND: {fpath} ---")
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    lines_out.append(f.read())
            except Exception as e:
                lines_out.append(f"(could not read: {e})")
        elif fname.endswith((".kt", ".md", ".txt", ".yml", ".yaml")):
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if "get_or_create_character" in content:
                    lines_out.append(f"\n--- mention found in: {fpath} ---")
                    for i, line in enumerate(content.splitlines()):
                        if "get_or_create_character" in line:
                            lines_out.append(f"  line {i+1}: {line.strip()}")
            except Exception:
                pass

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
