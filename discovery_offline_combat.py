import re, os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
OUT = "discovery_output.txt"

def find_file(name):
    for dirpath, _, files in os.walk(ROOT):
        if name in files:
            return os.path.join(dirpath, name)
    return None

def grab(path, pattern, context=40, label=""):
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

sections = []

repo_kt = find_file("GameStateRepository.kt")
offline_kt = find_file("OfflineIdleMechanicsSystem.kt")
combat_service_kt = find_file("CombatService.kt")
combat_system_kt = find_file("CombatSystem.kt")
viewmodel_kt = find_file("GameViewModel.kt")

# 1. GameStateRepository save/load shape
sections.append(grab(repo_kt, r"fun save\s*\(", 100, "GameStateRepository.save() signature"))
sections.append(grab(repo_kt, r"fun loadGame\s*\(", 150, "loadGame()"))

# 2. OfflineIdleMechanicsSystem scaffolding
sections.append(grab(offline_kt, r"enum class QueueType", 60, "QueueType enum"))
sections.append(grab(offline_kt, r"OfflineCombatQueue", 80, "OfflineCombatQueue (all occurrences)"))
sections.append(grab(offline_kt, r"fun optIntoOfflineCombat", 60, "optIntoOfflineCombat()"))
sections.append(grab(offline_kt, r"fun resolveOfflineProgress", 200, "resolveOfflineProgress()"))
sections.append(grab(offline_kt, r"class LastSeenExport", 40, "LastSeenExport data class"))
sections.append(grab(offline_kt, r"fun recordLastSeen|fun exportLastSeen|fun restoreLastSeen", 60, "lastSeen export/restore functions"))
sections.append(grab(offline_kt, r"combatPenaltyMultiplier", 40, "combatPenaltyMultiplier usage"))

# 3. CombatService state
sections.append(grab(combat_service_kt, r"class CharacterCombatState", 60, "CharacterCombatState"))
sections.append(grab(combat_service_kt, r"fun rollLoot", 150, "rollLoot()"))
sections.append(grab(combat_service_kt, r"pendingCoins|collectCoins", 60, "pendingCoins/collectCoins"))

# 4. CombatSystem coin drops
sections.append(grab(combat_system_kt, r"object CoinDropTable|fun rollCoins", 60, "CoinDropTable.rollCoins"))

# 5. GameViewModel: tick loop, zone entry/exit, restore call sites
sections.append(grab(viewmodel_kt, r"fun tickCombat", 100, "tickCombat()"))
sections.append(grab(viewmodel_kt, r"fun enterZone|fun enterCombatZone|fun leaveZone|fun exitCombatZone", 100, "zone entry/exit functions"))
sections.append(grab(viewmodel_kt, r"fun selectCharacter", 250, "selectCharacter() (mismatch/recovery branch)"))
sections.append(grab(viewmodel_kt, r"fun attemptCloudRecoveryLogin", 250, "attemptCloudRecoveryLogin()"))
sections.append(grab(viewmodel_kt, r"saved\.\w+\.forEach|recovered\.\w+\.forEach", 40, "restore forEach call sites"))
sections.append(grab(viewmodel_kt, r"xp = damageDealt|damageDealt \* 4", 40, "combat XP-per-hit formula"))
sections.append(grab(viewmodel_kt, r"combat_grant_coins", 40, "combat_grant_coins RPC call site"))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(sections))

print(f"Wrote {OUT}")