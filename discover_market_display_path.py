import re

out = open("discovery_output9.txt", "w", encoding="utf-8")

GVM = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
MA = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"

def dump(path, pattern, before=3, after=15, label=""):
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

# where is refreshMarketListings called from (all call sites)
dump(MA, r"refreshMarketListings", before=3, after=3, label="MainActivity.kt - refreshMarketListings call sites")
dump(GVM, r"refreshMarketListings", before=3, after=3, label="GameViewModel.kt - refreshMarketListings call sites")

# marketListingsUi derivation
dump(MA, r"marketListingsUi", before=3, after=8, label="MainActivity.kt - marketListingsUi")

# _marketListings declaration
dump(GVM, r"_marketListings", before=2, after=4, label="GameViewModel.kt - _marketListings")

# where MarketScreen / AppDestination.MARKET section is, to see LaunchedEffect triggers
dump(MA, r"AppDestination\.MARKET", before=3, after=25, label="MainActivity.kt - AppDestination.MARKET block")

out.close()
