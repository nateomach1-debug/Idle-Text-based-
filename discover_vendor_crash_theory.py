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
    f.write("VENDOR CRASH THEORY CHECK\n")

    # Where is buildInventoryItemSummaries defined?
    candidates = []
    for dirpath, _, files in os.walk(ROOT):
        for fn in files:
            candidates.append(os.path.join(dirpath, fn))

    build_summaries_file = None
    for c in candidates:
        try:
            if "fun buildInventoryItemSummaries" in read(c):
                build_summaries_file = c
                break
        except Exception:
            pass
    dump_matches(f, build_summaries_file, "buildInventoryItemSummaries() full definition",
                 r"fun buildInventoryItemSummaries", before=50, after=2000)

    # vendorPayoutPerUnit implementation - likely in the legacy local EconomyMarketSystem.kt / MarketService
    payout_file = None
    for c in candidates:
        try:
            if "fun vendorPayoutPerUnit" in read(c):
                payout_file = c
                break
        except Exception:
            pass
    dump_matches(f, payout_file, "vendorPayoutPerUnit() full definition",
                 r"fun vendorPayoutPerUnit", before=50, after=1500)

    # ItemCatalog.baseValueFor implementation
    item_catalog_file = None
    for c in candidates:
        try:
            if "fun baseValueFor" in read(c):
                item_catalog_file = c
                break
        except Exception:
            pass
    dump_matches(f, item_catalog_file, "ItemCatalog.baseValueFor() full definition",
                 r"fun baseValueFor", before=50, after=1000)

    # Also dump ItemCatalog.find() since it's used with ?: fallback everywhere - confirm it's null-safe
    itemcatalog_find_file = None
    for c in candidates:
        try:
            content = read(c)
            if "object ItemCatalog" in content:
                itemcatalog_find_file = c
                break
        except Exception:
            pass
    dump_matches(f, itemcatalog_find_file, "ItemCatalog object - find() and baseValueFor() together",
                 r"object ItemCatalog", before=0, after=2500)

    # Check whether the new item-3 combat-drop item ids have ANY ItemCatalog entry at all
    f.write(f"\n{'='*100}\nCHECK: do new combat-drop item ids appear in ItemCatalog / GeneratedItemCatalog?\n{'='*100}\n")
    new_drop_ids = ["cowhide", "raw_beef", "raw_chicken", "feathers", "snake_hide",
                     "uncut_gemstone", "bone", "goblin_ear", "ectoplasm", "wraith_essence",
                     "rusty_dagger", "green_dragonhide", "blue_dragonhide"]
    catalog_files = [c for c in candidates if "ItemCatalog" in os.path.basename(c)]
    f.write(f"Catalog-related files found: {catalog_files}\n")
    for cf in catalog_files:
        content = read(cf)
        f.write(f"\n--- presence check in {cf} ---\n")
        for did in new_drop_ids:
            present = f'"{did}"' in content
            f.write(f"  {did}: {'FOUND' if present else 'MISSING'}\n")

    f.write("\n\nDONE\n")

print("wrote", OUT)
