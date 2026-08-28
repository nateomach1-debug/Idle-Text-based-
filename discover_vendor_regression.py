import os, re

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
OUT = "discovery_output.txt"

def find_file(name):
    for dirpath, _, files in os.walk(ROOT):
        if name in files:
            return os.path.join(dirpath, name)
    return None

def dump_full(f, path, label):
    f.write(f"\n{'='*100}\nFULL FILE: {label} ({path})\n{'='*100}\n")
    if path is None:
        f.write("!!! FILE NOT FOUND !!!\n")
        return
    with open(path, "r", encoding="utf-8") as src:
        content = src.read()
    f.write(content)
    f.write(f"\n--- end of {label} ({len(content)} chars, {content.count(chr(10))+1} lines) ---\n")

def dump_matches(f, path, label, pattern, context=60):
    f.write(f"\n{'='*100}\nGREP: {label} in {path} (pattern: {pattern})\n{'='*100}\n")
    if path is None:
        f.write("!!! FILE NOT FOUND !!!\n")
        return
    with open(path, "r", encoding="utf-8") as src:
        content = src.read()
    for m in re.finditer(pattern, content):
        start = max(0, m.start() - 200)
        end = min(len(content), m.end() + context * 20)
        f.write(f"\n--- match at offset {m.start()} ---\n")
        f.write(content[start:end])
        f.write("\n")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("VENDOR REGRESSION DISCOVERY\n")

    market_screen = find_file("MarketScreen.kt")
    dump_full(f, market_screen, "MarketScreen.kt")

    game_vm = find_file("GameViewModel.kt")
    dump_matches(f, game_vm, "sellItemToVendor + buyItemFromVendor + related state",
                 r"(fun sellItemToVendor|fun buyItemFromVendor|MarketTab|VendorBuy)", context=80)

    main_activity = find_file("MainActivity.kt")
    dump_matches(f, main_activity, "onSellToVendor / onBuyFromVendor / Market tab wiring",
                 r"(onSellToVendor|onBuyFromVendor|MarketScreen\(|MarketTab)", context=60)

    supabase_market_repo = find_file("SupabaseMarketRepository.kt")
    dump_matches(f, supabase_market_repo, "buyFromVendor / sellToVendor RPC wrappers",
                 r"(fun buyFromVendor|fun sellToVendor)", context=60)

    # Also check server-side tax rate in match_market_orders (for the benched popup feature)
    f.write(f"\n{'='*100}\nSQL TAX RATE CHECK: match_market_orders()\n{'='*100}\n")
    sql_files = [fn for fn in os.listdir(".") if fn.endswith(".sql")]
    f.write(f"SQL files at repo root: {sql_files}\n")
    for sf in sql_files:
        with open(sf, "r", encoding="utf-8") as s:
            content = s.read()
        if "match_market_orders" in content:
            f.write(f"\n--- match_market_orders() found in {sf} ---\n")
            m = re.search(r"(CREATE OR REPLACE FUNCTION match_market_orders.*?)\$\$ LANGUAGE", content, re.DOTALL)
            if m:
                f.write(m.group(1))
            else:
                idx = content.find("match_market_orders")
                f.write(content[max(0,idx-100):idx+6000])

    f.write("\n\nDONE\n")

print("wrote", OUT)
