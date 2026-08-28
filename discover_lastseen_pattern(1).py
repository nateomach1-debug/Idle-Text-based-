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

def dump_matches(f, path, label, pattern, before=100, after=900):
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
    f.write("LAST-SEEN EXPORT/RESTORE PATTERN + RESTORE CALL SITES DISCOVERY\n")

    offline_idle_file = find_file("OfflineIdleMechanicsSystem.kt")
    dump_matches(f, offline_idle_file, "LastSeenExport data class + recordLastSeen/exportLastSeen/restoreLastSeen",
                 r"(class LastSeenExport|fun recordLastSeen|fun exportLastSeen|fun restoreLastSeen|fun lastSeenFor)",
                 before=50, after=500)

    repo_file = find_file("GameStateRepository.kt")
    dump_matches(f, repo_file, "lastSeen JSON write in save()", r'"lastSeen"', before=300, after=600)

    # Find the load/parse side - could be named load(), loadFromJson(), parse(), etc.
    dump_matches(f, repo_file, "lastSeen JSON read/parse side", r'lastSeen', before=100, after=400)

    game_vm = find_file("GameViewModel.kt")
    dump_matches(f, game_vm, "ALL restoreLastSeen call sites (loadGame + cloud recovery paths)",
                 r"restoreLastSeen", before=250, after=100)

    f.write("\n\nDONE\n")

print("wrote", OUT)
