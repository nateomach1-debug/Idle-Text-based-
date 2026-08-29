import os, re

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
OUT = "discovery_output.txt"

def find_file(name):
    for dirpath, _, files in os.walk(ROOT):
        if name in files:
            return os.path.join(dirpath, name)
    return None

def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def dump_matches(f, path, label, pattern, before=150, after=1000):
    f.write(f"\n{'='*100}\n{label} in {path}\n{'='*100}\n")
    if path is None:
        f.write("!!! FILE NOT FOUND !!!\n")
        return
    content = read(path)
    count = 0
    for m in re.finditer(pattern, content):
        count += 1
        start = max(0, m.start() - before)
        end = min(len(content), m.end() + after)
        f.write(f"\n--- match #{count} at offset {m.start()} ---\n")
        f.write(content[start:end])
        f.write("\n")
    if count == 0:
        f.write("(no matches found)\n")
    f.write(f"\ntotal matches: {count}\n")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("MATCH-EXECUTION + CHECKPOINT-CALL-SITE DISCOVERY\n")

    market_repo = find_file("SupabaseMarketRepository.kt")
    dump_matches(f, market_repo, "any client-side call to match_market_orders RPC",
                 r"match_market_orders", before=100, after=400)

    game_vm = find_file("GameViewModel.kt")
    dump_matches(f, game_vm, "placeBuyOrder/placeSellOrder full functions (does either call match_market_orders?)",
                 r"fun place(Buy|Sell)Order", before=50, after=1200)

    # Find the two recordLastSeen occurrences with wider surrounding context - what
    # function are they each inside, and under what condition is that function called?
    dump_matches(f, game_vm, "recordLastSeen occurrences - full enclosing function context",
                 r"offlineIdleService\.recordLastSeen\(characterId\)\n        checkForRecentSales\(characterId\)",
                 before=1500, after=200)

    f.write("\n\nDONE\n")

print("wrote", OUT)
