import re

out = open("discovery_output.txt", "w", encoding="utf-8")

def dump_context(path, pattern, before=5, after=40, label=""):
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
            print("\n" + "-"*80, file=out)
    if not found:
        print(f"NO MATCH for pattern: {pattern}", file=out)

# 1. MainActivity.kt - find the sell-on-market confirm handler
dump_context(
    "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt",
    r"placeSellOrder|onPlaceOrder|Sell on [Mm]arket|SellOrderDialog|confirmSell",
    before=5, after=50,
    label="MainActivity.kt - sell order UI"
)

# 2. GameViewModel.kt - placeSellOrder implementation
dump_context(
    "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt",
    r"fun placeSellOrder",
    before=3, after=50,
    label="GameViewModel.kt - placeSellOrder"
)

# 3. SupabaseMarketRepository.kt - placeSellOrder RPC wrapper
dump_context(
    "app/src/main/kotlin/com/yourname/idlerpg/SupabaseMarketRepository.kt",
    r"fun placeSellOrder|placeSellOrder",
    before=3, after=50,
    label="SupabaseMarketRepository.kt - placeSellOrder"
)

# 4. Full SupabaseMarketRepository.kt for context (in case class-level setup matters)
try:
    with open("app/src/main/kotlin/com/yourname/idlerpg/SupabaseMarketRepository.kt", "r", encoding="utf-8") as f:
        content = f.read()
    print(f"\n{'='*80}\nFULL FILE: SupabaseMarketRepository.kt ({len(content)} chars)\n{'='*80}", file=out)
    print(content, file=out)
except Exception as e:
    print(f"Could not read full file: {e}", file=out)

out.close()
