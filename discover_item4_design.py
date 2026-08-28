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
    f.write("ITEM 4 DISCOVERY: offline-summary popup pattern + lastSeenAt persistence\n")

    game_vm = find_file("GameViewModel.kt")

    # The offline summary popup StateFlow (whatever it's called) - declaration + how it's populated
    dump_matches(f, game_vm, "offline summary / popup StateFlow declaration + population",
                 r"(_offlineSummary|OfflineSummary|offlineSummary)", before=100, after=900)

    # lastSeenAt - how it's read/written/persisted
    dump_matches(f, game_vm, "lastSeenAt read/write/persist references",
                 r"lastSeenAt", before=80, after=300)

    # recordLastSeen definition
    dump_matches(f, game_vm, "recordLastSeen() definition",
                 r"fun recordLastSeen", before=50, after=600)

    # MainActivity.kt - how the offline summary popup is actually shown (Dialog/AlertDialog composable)
    main_activity = find_file("MainActivity.kt")
    dump_matches(f, main_activity, "offline summary popup UI (Dialog/AlertDialog) in MainActivity.kt",
                 r"(offlineSummary|OfflineSummaryDialog|OfflineSummary)", before=100, after=1200)

    # GameStateRepository.kt save/load signature (already partially seen, re-confirm exact param list)
    game_state_repo = find_file("GameStateRepository.kt")
    dump_matches(f, game_state_repo, "GameStateRepository.save() full signature",
                 r"fun save\(", before=50, after=1500)

    f.write("\n\nDONE\n")

print("wrote", OUT)
