PATH = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

def apply(old, new, label):
    global content
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"FAILED [{label}]: expected 1 match, found {count}")
    content = content.replace(old, new, 1)

apply(
"""        val session = state.session ?: return

        if (session.state == SessionState.SEARCHING) {
            val result = combatService.resolveSearchIfReady(characterId)
            if (result is ServiceResult.Success) {
                combatLogFor.getOrPut(characterId) { mutableListOf() }
                    .add(CombatLogEntry(result.value.name + " appears!"))
            }
            refreshCombatView()
            return
        }

        if (session.state != SessionState.IN_COMBAT) return""",
"""        var session = state.session ?: return

        if (session.state == SessionState.SEARCHING) {
            val result = combatService.resolveSearchIfReady(characterId)
            if (result is ServiceResult.Success) {
                combatLogFor.getOrPut(characterId) { mutableListOf() }
                    .add(CombatLogEntry(result.value.name + " appears!"))
                // Fall through into the attack logic below using this same tick's
                // elapsedSeconds budget, instead of returning - otherwise every single
                // fight pays an extra full tick-interval of pure dead time before the
                // first attack lands, which gets far more expensive once tick intervals
                // are inflated by background scheduling throttling.
                session = combatService.stateFor(characterId, maxHpFor(characterId)).session ?: return
            } else {
                refreshCombatView()
                return
            }
        }

        if (session.state != SessionState.IN_COMBAT) return""",
    "tickCombat search-to-attack fallthrough"
)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied successfully.")
