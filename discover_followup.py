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

def dump_span(f, path, label, start_marker, end_marker, max_len=20000):
    f.write(f"\n{'='*100}\nSPAN: {label} ({path})\n{'='*100}\n")
    if path is None:
        f.write("!!! FILE NOT FOUND !!!\n")
        return
    content = read(path)
    start_idx = content.find(start_marker)
    if start_idx == -1:
        f.write(f"!!! start_marker not found: {start_marker!r} !!!\n")
        return
    end_idx = content.find(end_marker, start_idx + len(start_marker))
    if end_idx == -1:
        end_idx = min(len(content), start_idx + max_len)
        f.write(f"(end_marker not found after start; dumping up to {max_len} chars)\n")
    else:
        end_idx = min(end_idx, start_idx + max_len)
    f.write(content[start_idx:end_idx])
    f.write(f"\n--- end of span ({end_idx - start_idx} chars) ---\n")

def dump_all_matches_with_full_context(f, path, label, pattern, before=100, after=1500):
    f.write(f"\n{'='*100}\nALL MATCHES: {label} in {path} (pattern: {pattern})\n{'='*100}\n")
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
    f.write("FOLLOW-UP DISCOVERY: vendor blank-screen root cause + combat scheduling/persistence\n")

    main_activity = find_file("MainActivity.kt")

    # Full contiguous MARKET destination branch, start to the next top-level destination case
    dump_span(f, main_activity, "Full AppDestination.MARKET branch",
              "AppDestination.MARKET ->", "AppDestination.GUILD ->", max_len=25000)

    # Wherever inventoryItems / marketListingsUi / myBuyOrdersUi / mySellOrdersUi are DECLARED
    # (val/var assignment, not just usage) - search whole file
    for varname in ["inventoryItems", "marketListingsUi", "myBuyOrdersUi", "mySellOrdersUi"]:
        dump_all_matches_with_full_context(f, main_activity, f"declarations/derivations of `{varname}`",
                                            rf"\b(val|var)\s+{varname}\b", before=50, after=800)

    # Combat tick-loop scheduling - find where tickCombat() is actually invoked in a loop
    game_vm = find_file("GameViewModel.kt")
    dump_all_matches_with_full_context(f, game_vm, "tickCombat() call sites + any combat ticker coroutine",
                                        r"(tickCombat\(\)|combatTicker|startCombatLoop|combatJob)", before=200, after=1200)

    # CombatService state save/restore wiring - search across GameViewModel and GameStateRepository
    dump_all_matches_with_full_context(f, game_vm, "combatService save/restore/export/import references",
                                        r"combatService\.\w+", before=100, after=400)

    game_state_repo = find_file("GameStateRepository.kt")
    dump_all_matches_with_full_context(f, game_state_repo, "combat-related save/restore in GameStateRepository.kt",
                                        r"(?i)combat", before=100, after=400)

    # Any other references anywhere to the offline-combat scaffolding
    for fname in ["GameViewModel.kt", "MainActivity.kt", "OfflineIdleMechanicsSystem.kt"]:
        p = find_file(fname)
        dump_all_matches_with_full_context(f, p, f"OfflineCombatQueue/optIntoOfflineCombat references in {fname}",
                                            r"(OfflineCombatQueue|optIntoOfflineCombat|OFFLINE_COMBAT)", before=100, after=400)

    f.write("\n\nDONE\n")

print("wrote", OUT)
