import re

out = open("discovery_output2.txt", "w", encoding="utf-8")

def dump_all_matches(path, pattern, context=2, label=""):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    print(f"\n{'='*80}\n{label or path}\n{'='*80}", file=out)
    found = False
    for i, line in enumerate(lines):
        if re.search(pattern, line):
            found = True
            start = max(0, i - context)
            end = min(len(lines), i + context + 1)
            for j in range(start, end):
                print(f"{j+1:5d}: {lines[j]}", end="", file=out)
            print("-"*40, file=out)
    if not found:
        print(f"NO MATCH for pattern: {pattern}", file=out)

def dump_context(path, pattern, before=3, after=30, label=""):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    print(f"\n{'='*80}\n{label or path}\n{'='*80}", file=out)
    found = False
    for i, line in enumerate(lines):
        if re.search(pattern, line):
            found = True
            start = max(0, i - before)
            end = min(len(lines), i + after)
            for j in range(start, end):
                print(f"{j+1:5d}: {lines[j]}", end="", file=out)
            print("-"*40, file=out)
    if not found:
        print(f"NO MATCH for pattern: {pattern}", file=out)

GVM = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
MA = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"

# All occurrences of characterSyncError and chatActionError (declaration + usage sites)
dump_all_matches(GVM, r"characterSyncError", context=2, label="GameViewModel.kt - characterSyncError occurrences")
dump_all_matches(GVM, r"chatActionError", context=2, label="GameViewModel.kt - chatActionError occurrences")

# Full placeBuyOrder function
dump_context(GVM, r"fun placeBuyOrder", before=3, after=30, label="GameViewModel.kt - placeBuyOrder")

# Full debug AlertDialog body in MainActivity.kt
dump_context(MA, r"Debug: Supabase Sync", before=2, after=90, label="MainActivity.kt - full debug dialog body")

out.close()
