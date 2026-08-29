import re, os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
OUT = "discovery_output3.txt"

def grep_repo(pattern, label, context=20):
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

sections.append(grep_repo(r"grantCombatCoins\(", "grantCombatCoins call sites (not just definition)"))
sections.append(grep_repo(r"class CharacterCombatState|data class CharacterCombatState", "CharacterCombatState full definition", context=25))
sections.append(grep_repo(r"class CombatSession|data class CombatSession", "CombatSession full definition", context=25))
sections.append(grep_repo(r"class RecoveryStatus|data class RecoveryStatus", "RecoveryStatus full definition", context=15))
sections.append(grep_repo(r"enum class SessionState", "SessionState enum", context=10))
sections.append(grep_repo(r"data class Monster\(", "Monster data class", context=20))
sections.append(grep_repo(r"data class Zone\(|class Zone\(", "Zone data class", context=15))
sections.append(grep_repo(r"object ZoneCatalog", "ZoneCatalog object", context=15))
sections.append(grep_repo(r"data class OfflineResolution", "OfflineResolution data class", context=15))
sections.append(grep_repo(r"private fun resolveOfflineRewardsAndSync|fun resolveOfflineRewardsAndSync", "resolveOfflineRewardsAndSync full body", context=120))
sections.append(grep_repo(r"fun save\(\s*\n(?:.*\n){0,5}?\).*\{", "GameStateRepository.save() full body incl JSON writing for lastSeen array", context=250))
sections.append(grep_repo(r"fun load\(\)", "GameStateRepository.load() full body", context=250))
sections.append(grep_repo(r"fun maxHpFor|fun equippedWeapon|fun skillLevel\(", "helper functions used by tickCombat (maxHpFor/equippedWeapon/skillLevel)", context=15))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(sections))

print(f"Wrote {OUT}")