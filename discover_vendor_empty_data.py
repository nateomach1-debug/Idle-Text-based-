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

def dump_matches(f, path, label, pattern, before=100, after=1200):
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
    f.write("VENDOR TAB EMPTY-DATA DISCOVERY (Buy works, Vendor/Sell doesn't)\n")

    game_vm = find_file("GameViewModel.kt")

    # The inventoryItems StateFlow property itself (backing field + public exposure)
    dump_matches(f, game_vm, "inventoryItems StateFlow declaration (_inventoryItems / inventoryItems)",
                 r"(_inventoryItems|val inventoryItems)\s*[:=]", before=50, after=500)

    # refreshInventory() full definition
    dump_matches(f, game_vm, "refreshInventory() full definition",
                 r"fun refreshInventory\(", before=50, after=1500)

    # Where is refreshInventory() called from? All call sites
    dump_matches(f, game_vm, "all call sites of refreshInventory()",
                 r"(?<!fun )refreshInventory\(\)", before=150, after=50)

    # InventoryService - look for the class/data backing inventoryFor(), and any
    # method that lists items (to see if it filters equipped items, tradeable-only, etc.)
    inv_service_file = None
    for dirpath, _, files in os.walk(ROOT):
        for fn in files:
            p = os.path.join(dirpath, fn)
            try:
                if "class InventoryService" in read(p):
                    inv_service_file = p
                    break
            except Exception:
                pass
    dump_matches(f, inv_service_file, "InventoryService class full definition",
                 r"class InventoryService", before=0, after=4000)

    # InventorySlotEntry data class + wherever the list-of-entries getter is defined
    dump_matches(f, inv_service_file, "InventorySlotEntry / entries listing method",
                 r"(data class InventorySlotEntry|fun entries|fun allItems|fun itemEntries)",
                 before=50, after=800)

    f.write("\n\nDONE\n")

print("wrote", OUT)
