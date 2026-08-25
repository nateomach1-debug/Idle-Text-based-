import re

out = open("discovery_output7.txt", "w", encoding="utf-8")
GVM = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(GVM, "r", encoding="utf-8") as f:
    lines = f.readlines()

def dump(pattern, before=2, after=20, label=""):
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

dump(r"fun sellItemToVendor", before=2, after=6, label="sellItemToVendor header")
dump(r"fun refreshCurrency", before=2, after=15, label="refreshCurrency")
dump(r"fun refreshMarketListings", before=2, after=15, label="refreshMarketListings")
dump(r"fun refreshMyOrders", before=2, after=15, label="refreshMyOrders")

out.close()
