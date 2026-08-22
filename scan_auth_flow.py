"""
Discovery script - NOT a code-modifying patch.

Finds the auth signup flow (where "user_already_exists" is being
handled/mishandled) so we can add a fallback to sign-in on that error.

Writes one new file: repo_auth_signup_flow.txt
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
OUTPUT_PATH = "repo_auth_signup_flow.txt"

keywords = ["signUp", "signIn", "user_already_exists", "Auth:", "class SupabaseAuth",
            "get_or_create_character", "profile_id", "fun signUp", "fun signIn", "fun login", "fun register"]

lines_out = []
lines_out.append("=" * 70)
lines_out.append("Search for auth signup/signin flow across all .kt files")
lines_out.append("=" * 70)

for fname in sorted(os.listdir(BASE)):
    if not fname.endswith(".kt"):
        continue
    fpath = os.path.join(BASE, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    matches = [i for i, line in enumerate(lines) if any(k in line for k in keywords)]
    if matches:
        lines_out.append(f"\n--- {fname} (total lines: {len(lines)}) ---")
        for i in matches:
            lines_out.append(f"  {i+1}: {lines[i].rstrip()}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out))

print(f"Wrote {OUTPUT_PATH}")
