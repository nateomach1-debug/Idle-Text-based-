import re

out = open("discovery_output13.txt", "w", encoding="utf-8")

GVM = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
MA = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"

def dump(path, pattern, before=3, after=6, label=""):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    print(f"\n{'='*80}\n{label}\n{'='*80}", file=out)
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

dump(MA, r"refreshCurrency", before=3, after=3, label="MainActivity.kt - refreshCurrency call sites")
dump(MA, r"gameViewModel\.currency\.collectAsState|currency\.collectAsState", before=3, after=6, label="MainActivity.kt - where currency StateFlow is collected")
dump(MA, r"AppDestination\.MARKET -> \{", before=1, after=6, label="MainActivity.kt - Market tab entry (recheck after listings patch)")
dump(GVM, r"data class MarketPriceSummary|data class MarketListingSummary", before=1, after=6, label="MarketPriceSummary / MarketListingSummary definitions")
dump(MA, r"MarketListingSummary", before=2, after=8, label="MainActivity.kt - MarketListingSummary usage / display")

out.close()
