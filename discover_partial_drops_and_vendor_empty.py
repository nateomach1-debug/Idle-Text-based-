import os, re

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
OUT = "discovery_output.txt"

def find_file(name):
    for dirpath, _, files in os.walk(ROOT):
        if name in files:
            return os.path.join(dirpath, name)
    return None

def find_files_containing(text):
    matches = []
    for dirpath, _, files in os.walk(ROOT):
        for fn in files:
            p = os.path.join(dirpath, fn)
            try:
                with open(p, "r", encoding="utf-8") as f:
                    if text in f.read():
                        matches.append(p)
            except Exception:
                pass
    return matches

def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def dump_matches(f, path, label, pattern, before=100, after=1500):
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
    f.write("LOOT TABLE ID CHECK + VENDOR/LOADOUT DIVERGENCE DISCOVERY\n")

    # Find the Zone/Monster/ActionCatalog file(s) defining Goblin Camp and Shadow Ruins loot tables
    zone_files = find_files_containing("Goblin Camp")
    f.write(f"Files containing 'Goblin Camp': {zone_files}\n")
    for zf in zone_files:
        dump_matches(f, zf, "Goblin Camp zone/monster block (full loot tables)",
                     r"Goblin Camp", before=50, after=4000)

    shadow_files = find_files_containing("Shadow Ruins")
    f.write(f"\nFiles containing 'Shadow Ruins': {shadow_files}\n")
    for sf in shadow_files:
        dump_matches(f, sf, "Shadow Ruins zone/monster block (full loot tables)",
                     r"Shadow Ruins", before=50, after=4000)

    # InventoryService - allItems()/entries getter, full class already partly seen but
    # get the COMPLETE class this time including any category/tradeable filtering
    game_vm = find_file("GameViewModel.kt")
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
    dump_matches(f, inv_service_file, "InventoryService FULL class (looking for allItems/entries filtering)",
                 r"class InventoryService", before=0, after=6000)

    # How is gameViewModel.inventoryItems (the public StateFlow) actually produced/updated?
    dump_matches(f, game_vm, "public inventoryItems StateFlow exposure + backing production",
                 r"val inventoryItems[^\n]*StateFlow", before=200, after=800)

    # How does the Loadout/Inventory/Equip SCREEN actually read items - same StateFlow or different?
    main_activity = find_file("MainActivity.kt")
    dump_matches(f, main_activity, "AppDestination.INVENTORY or LOADOUT branch - what item source does it use",
                 r"AppDestination\.(INVENTORY|LOADOUT)", before=100, after=2500)

    # inventoryItemEntries - where declared/collected, to compare against what feeds Market
    dump_matches(f, main_activity, "inventoryItemEntries declaration/collection",
                 r"inventoryItemEntries", before=150, after=400)

    f.write("\n\nDONE\n")

print("wrote", OUT)
