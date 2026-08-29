import re, os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
OUT = "discovery_output2.txt"

def find_file(name):
    for dirpath, _, files in os.walk(ROOT):
        if name in files:
            return os.path.join(dirpath, name)
    return None

def grab(path, pattern, context=60, label=""):
    if not path or not os.path.exists(path):
        return f"\n=== {label}: FILE NOT FOUND ===\n"
    text = open(path, encoding="utf-8").read()
    out = [f"\n=== {label} (in {path}) ==="]
    for m in re.finditer(pattern, text):
        start = max(0, m.start() - 200)
        end = min(len(text), m.end() + context * 20)
        out.append(text[start:end])
        out.append("\n--- match end ---\n")
    if len(out) == 1:
        out.append("NO MATCHES FOUND\n")
    return "\n".join(out)

def grep_repo(pattern, label, context=15):
    out = [f"\n=== REPO-WIDE: {label} ==="]
    found = False
    for dirpath, _, files in os.walk(ROOT):
        for fname in files:
            if not fname.endswith(".kt"):
                continue
            path = os.path.join(dirpath, fname)
            text = open(path, encoding="utf-8").read()
            for m in re.finditer(pattern, text):
                found = True
                start = max(0, m.start() - 150)
                end = min(len(text), m.end() + context * 20)
                out.append(f"-- {path} --")
                out.append(text[start:end])
                out.append("--- match end ---\n")
    if not found:
        out.append("NO MATCHES FOUND ANYWHERE IN REPO\n")
    return "\n".join(out)

sections = []

combat_kt = find_file("CombatSystem.kt")
repo_kt = find_file("GameStateRepository.kt")

sections.append(grab(combat_kt, r"class CombatService", 400, "CombatService full class"))
sections.append(grab(combat_kt, r"fun leaveZone", 60, "leaveZone()"))
sections.append(grab(combat_kt, r"fun collectLoot", 60, "collectLoot()"))

sections.append(grep_repo(r"combat_grant_coins", "combat_grant_coins literal string"))
sections.append(grep_repo(r"grantCoins|GrantCoins", "grantCoins function"))
sections.append(grep_repo(r"class SupabaseCombatRepository|object SupabaseCombatRepository", "SupabaseCombatRepository"))
sections.append(grep_repo(r"pendingCoins", "pendingCoins all usages"))
sections.append(grep_repo(r"class CombatSessionExport|CombatSessionExport", "CombatSessionExport (should not exist yet)"))
sections.append(grep_repo(r"CharacterExport\(", "CharacterExport data class definition"))
sections.append(grep_repo(r"data class.*\(\s*\n?\s*val accounts", "top-level save/load data class shape"))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(sections))

print(f"Wrote {OUT}")