import re

out = open("discovery_output6.txt", "w", encoding="utf-8")

GVM = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(GVM, "r", encoding="utf-8") as f:
    lines = f.readlines()

def dump_all(pattern, context=3, label=""):
    print(f"\n{'='*80}\n{label}\n{'='*80}", file=out)
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

dump_all(r"_currentCharacterId\s*=\s*MutableStateFlow|val currentCharacterId", context=3,
          label="_currentCharacterId declaration")
dump_all(r"_currentCharacterId\.value\s*=", context=3,
          label="All assignments to _currentCharacterId.value")
dump_all(r"_currentSupabaseCharacterId\.value\s*=", context=3,
          label="All assignments to _currentSupabaseCharacterId.value")

out.close()
