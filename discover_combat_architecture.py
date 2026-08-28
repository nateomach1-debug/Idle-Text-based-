import os, re

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
OUT = "discovery_output.txt"

def find_files(name_pattern):
    matches = []
    for dirpath, _, files in os.walk(ROOT):
        for fn in files:
            if re.search(name_pattern, fn):
                matches.append(os.path.join(dirpath, fn))
    return matches

def dump_full(f, path, label):
    f.write(f"\n{'='*100}\nFULL FILE: {label} ({path})\n{'='*100}\n")
    if path is None:
        f.write("!!! FILE NOT FOUND !!!\n")
        return
    with open(path, "r", encoding="utf-8") as src:
        content = src.read()
    f.write(content)
    f.write(f"\n--- end of {label} ({len(content)} chars, {content.count(chr(10))+1} lines) ---\n")

def dump_matches(f, path, label, pattern, context=80):
    f.write(f"\n{'='*100}\nGREP: {label} in {path} (pattern: {pattern})\n{'='*100}\n")
    if path is None:
        f.write("!!! FILE NOT FOUND !!!\n")
        return
    with open(path, "r", encoding="utf-8") as src:
        content = src.read()
    for m in re.finditer(pattern, content):
        start = max(0, m.start() - 150)
        end = min(len(content), m.end() + context * 20)
        f.write(f"\n--- match at offset {m.start()} ---\n")
        f.write(content[start:end])
        f.write("\n")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("COMBAT ARCHITECTURE DISCOVERY\n")

    # Identify candidate files
    candidates = find_files(r"Combat|OfflineIdle|Progression|ActionCatalog|Monster|Zone")
    f.write("\nCANDIDATE FILES FOUND:\n")
    for c in candidates:
        f.write(f"  {c}\n")

    combat_files = [c for c in candidates if "Combat" in os.path.basename(c)]
    for cf in combat_files:
        dump_full(f, cf, os.path.basename(cf))

    offline_files = [c for c in candidates if "OfflineIdle" in os.path.basename(c)]
    for of in offline_files:
        dump_full(f, of, os.path.basename(of))

    game_vm = None
    for dirpath, _, files in os.walk(ROOT):
        if "GameViewModel.kt" in files:
            game_vm = os.path.join(dirpath, "GameViewModel.kt")
    dump_matches(f, game_vm, "tickCombat / tickSkilling / combat queue / fight loop state",
                 r"(fun tickCombat|fun tickSkilling|fun resolveOfflineRewards|combatQueue|CombatState|fun startFight|fun attack)",
                 context=100)

    action_catalog = None
    for dirpath, _, files in os.walk(ROOT):
        if "ActionCatalog.kt" in files:
            action_catalog = os.path.join(dirpath, "ActionCatalog.kt")
    dump_matches(f, action_catalog, "Monster / loot table definitions (for coin-drop scaling)",
                 r"(class Monster|data class Monster|lootTable|LootTable|object.*Zone)",
                 context=60)

    f.write("\n\nDONE\n")

print("wrote", OUT)
