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

def dump_matches(f, path, label, pattern, before=100, after=700):
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
    f.write("SERIALIZABLE ROW CLASS FORMAT DISCOVERY\n")

    market_repo = find_file("SupabaseMarketRepository.kt")
    dump_matches(f, market_repo, "MarketOrderRow / MarketListingRow / MarketCancelRpcResult data class definitions",
                 r"(data class MarketOrderRow|data class MarketListingRow|data class MarketCancelRpcResult)",
                 before=100, after=600)

    # Also grab the top of the file (imports) to confirm exact serialization library used
    with open(market_repo, "r", encoding="utf-8") as sf:
        head = sf.read(1500)
    f.write(f"\n{'='*100}\nFile header / imports of SupabaseMarketRepository.kt\n{'='*100}\n")
    f.write(head)

    f.write("\n\nDONE\n")

print("wrote", OUT)
