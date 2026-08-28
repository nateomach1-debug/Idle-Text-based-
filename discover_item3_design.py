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

def dump_matches(f, path, label, pattern, before=150, after=1500):
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
    f.write("ITEM 3 DESIGN DISCOVERY: combat XP grant + save/load JSON aggregation shape\n")

    game_vm = find_file("GameViewModel.kt")

    # How is XP granted during live combat? Look at resolveAttack call site + surrounding
    dump_matches(f, game_vm, "combat XP granting (grantXp calls near combat attack handling)",
                 r"grantXp\([^)]*\)", before=300, after=200)

    # Full saveGame() function
    dump_matches(f, game_vm, "saveGame() full definition", r"fun saveGame\(", before=50, after=3000)

    # Full loadGame() function
    dump_matches(f, game_vm, "loadGame() full definition", r"fun loadGame\(", before=50, after=3000)

    # GameStateRepository's currentSaveJson/overwriteRawJson + whatever DTO shape it uses
    game_state_repo = find_file("GameStateRepository.kt")
    dump_matches(f, game_state_repo, "GameStateRepository save/load DTO shape",
                 r"(class .*Save.*Data|fun currentSaveJson|fun overwriteRawJson|@Serializable)",
                 before=50, after=600)

    f.write("\n\nDONE\n")

print("wrote", OUT)
