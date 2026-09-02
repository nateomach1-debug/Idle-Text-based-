"""
Discovery script for the training-skill-reverts-to-Attack bug.
Run from repo root. Writes findings to discovery_output.txt.

Goal: determine whether trainingSkillId is present in the Supabase
cloud-save schema/upload payload, and inspect the restore-on-mismatch
logic that runs on cold start (login/signup/selectCharacter) to see
if it can overwrite a correct local trainingSkillId with a stale/
missing cloud value.
"""
import os
import re

REPO_ROOT = "."
OUT_PATH = "discovery_output.txt"

# File types worth scanning
KOTLIN_EXT = (".kt",)
SQL_EXT = (".sql",)

def find_files(root, exts):
    matches = []
    for dirpath, _dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "node_modules" in dirpath:
            continue
        for f in filenames:
            if f.endswith(exts):
                matches.append(os.path.join(dirpath, f))
    return matches

def grep_context(path, pattern, context=3, flags=re.IGNORECASE):
    """Return list of (line_no, context_block) for regex matches in a file."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except Exception as e:
        return [(0, f"<<could not read {path}: {e}>>")]

    results = []
    rx = re.compile(pattern, flags)
    for i, line in enumerate(lines):
        if rx.search(line):
            start = max(0, i - context)
            end = min(len(lines), i + context + 1)
            block = "".join(f"{n+1:5d}| {lines[n]}" for n in range(start, end))
            results.append((i + 1, block))
    return results

def section(title):
    return f"\n{'='*80}\n{title}\n{'='*80}\n"

def main():
    out = []

    kt_files = find_files(REPO_ROOT, KOTLIN_EXT)
    sql_files = find_files(REPO_ROOT, SQL_EXT)

    out.append(section("FILES SCANNED"))
    out.append(f"Kotlin files: {len(kt_files)}\nSQL files: {len(sql_files)}\n")
    out.append("SQL files found:\n" + "\n".join(sql_files) + "\n")

    # 1. trainingSkillId anywhere in SQL (schema/RPC) files
    out.append(section("1. 'trainingSkillId' or 'training_skill' in SQL files (cloud schema/RPCs)"))
    found_any_sql = False
    for f in sql_files:
        for line_no, block in grep_context(f, r"training[_]?skill"):
            found_any_sql = True
            out.append(f"--- {f}:{line_no} ---\n{block}\n")
    if not found_any_sql:
        out.append(">>> NO MATCHES for training_skill/trainingSkillId in any .sql file. "
                    "This strongly suggests the cloud schema never includes this field. <<<\n")

    # 2. character_saves table definition / upload payload structure
    out.append(section("2. 'character_saves' table + related upload/download RPC definitions"))
    for f in sql_files:
        for line_no, block in grep_context(f, r"character_saves", context=15):
            out.append(f"--- {f}:{line_no} ---\n{block}\n")

    # 3. Kotlin: whatever builds the JSON/payload sent to Supabase for character/inventory save
    out.append(section("3. Kotlin: upload/serialize functions for cloud character save (search terms: uploadCharacterSave, saveToCloud, character_saves, pushCharacterSave, syncToSupabase)"))
    upload_patterns = [
        r"uploadCharacterSave",
        r"saveToCloud",
        r"pushCharacterSave",
        r"syncToSupabase",
        r"character_saves",
        r"CharacterSaveDto",
        r"CharacterSavePayload",
    ]
    for f in kt_files:
        for pat in upload_patterns:
            for line_no, block in grep_context(f, pat, context=20):
                out.append(f"--- {f}:{line_no} (pattern: {pat}) ---\n{block}\n")

    # 4. restore-on-mismatch logic in selectCharacter/login/signup
    out.append(section("4. Kotlin: restore-on-mismatch logic (selectCharacter/login/signup, restoreFromCloud, mismatch)"))
    restore_patterns = [
        r"restoreFromCloud",
        r"restore.*mismatch",
        r"mismatch",
        r"downloadCharacterSave",
        r"fetchCloudSave",
    ]
    for f in kt_files:
        for pat in restore_patterns:
            for line_no, block in grep_context(f, pat, context=25):
                out.append(f"--- {f}:{line_no} (pattern: {pat}) ---\n{block}\n")

    # 5. Confirm whether local repository.save()/load() is separate from cloud push/pull
    out.append(section("5. Kotlin: repository.save()/load() definitions (local persistence layer)"))
    for f in kt_files:
        for line_no, block in grep_context(f, r"fun save\(|fun load\(|class .*Repository", context=15):
            out.append(f"--- {f}:{line_no} ---\n{block}\n")

    # 6. Double-check: trainingSkillId in Kotlin (should be present - sanity check the field still exists)
    out.append(section("6. Sanity check: 'trainingSkillId' occurrences in Kotlin files (should exist - confirms field wasn't accidentally removed)"))
    for f in kt_files:
        for line_no, block in grep_context(f, r"trainingSkillId", context=2):
            out.append(f"--- {f}:{line_no} ---\n{block}\n")

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))

    print(f"Wrote discovery output to {OUT_PATH} ({len(out)} sections/blocks)")

if __name__ == "__main__":
    main()
