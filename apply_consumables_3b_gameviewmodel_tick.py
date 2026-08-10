"""
Food/Potion feature, patch 3b/4: the tick logic itself.

Adds:
- combatService field (CombatService wasn't referenced anywhere in
  GameViewModel before this)
- persisted autoHealThresholdPercent/autoFleeThresholdPercent StateFlows
  + setters, replacing the local-only Compose state that reset on every
  app restart
- selectFood()/selectPotion() wrapper functions for the LoadoutScreen UI
  (patch 3d) to call
- tickConsumables(), wired into the existing per-second tick loop
  alongside tickSkilling()/tickCrafting(): auto-eats when real HP drops
  to/below the threshold, and counts down + auto-redrinks the equipped
  potion when its timer runs out

Run from repo root: python3 apply_consumables_3b_gameviewmodel_tick.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")

OLD_FIELDS = '''    val economyMonitoring = EconomyMonitoringService()
    val marketService = MarketService(economyMonitoring)'''
NEW_FIELDS = '''    val economyMonitoring = EconomyMonitoringService()
    val marketService = MarketService(economyMonitoring)
    val combatService = CombatService()

    private val _autoHealThresholdPercent = MutableStateFlow(30)
    val autoHealThresholdPercent: StateFlow<Int> = _autoHealThresholdPercent.asStateFlow()

    private val _autoFleeThresholdPercent = MutableStateFlow(10)
    val autoFleeThresholdPercent: StateFlow<Int> = _autoFleeThresholdPercent.asStateFlow()

    fun setAutoHealThreshold(percent: Int) {
        _autoHealThresholdPercent.value = percent.coerceIn(0, 100)
    }

    fun setAutoFleeThreshold(percent: Int) {
        _autoFleeThresholdPercent.value = percent.coerceIn(0, 100)
    }

    fun selectFood(itemId: String?) {
        val characterId = _currentCharacterId.value ?: return
        inventoryService.inventoryFor(characterId).selectFood(itemId)
        refreshInventory()
    }

    fun selectPotion(itemId: String?) {
        val characterId = _currentCharacterId.value ?: return
        inventoryService.inventoryFor(characterId).selectPotion(itemId)
        refreshInventory()
    }

    private fun tickConsumables() {
        val characterId = _currentCharacterId.value ?: return
        val inventory = inventoryService.inventoryFor(characterId)
        val combatState = combatService.stateFor(characterId)

        if (combatState.maxHp > 0) {
            val hpPercent = (combatState.currentHp * 100) / combatState.maxHp
            if (hpPercent <= _autoHealThresholdPercent.value) {
                inventory.consumeSelectedFood()?.let { food ->
                    combatService.healCharacter(characterId, food.healAmount ?: 0)
                }
            }
        }

        if (inventory.selectedPotionId != null) {
            if (inventory.potionTimerRemainingSeconds > 0) {
                inventory.potionTimerRemainingSeconds -= 1
            }
            if (inventory.potionTimerRemainingSeconds <= 0) {
                inventory.consumeSelectedPotion()?.let { potion ->
                    inventory.potionTimerRemainingSeconds = potion.buffDurationSeconds ?: 0
                }
            }
        }

        refreshInventory()
    }'''

OLD_TICK_LOOP = '''            while (true) {
                delay(1000L)
                tickSkilling()
            tickCrafting()
            }'''
NEW_TICK_LOOP = '''            while (true) {
                delay(1000L)
                tickSkilling()
            tickCrafting()
            tickConsumables()
            }'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 0:
        raise SystemExit(f"ABORT: could not find expected block for '{label}'. No changes written.")
    if count > 1:
        raise SystemExit(f"ABORT: found {count} matches for '{label}', expected exactly 1. No changes written.")
    return text.replace(old, new, 1)


def main() -> None:
    if not TARGET.exists():
        raise SystemExit(f"ABORT: could not find {TARGET} from the current directory. Run this from the repo root.")

    content = TARGET.read_text()

    if "val combatService" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    content = replace_once(content, OLD_FIELDS, NEW_FIELDS, "combatService + thresholds + tickConsumables")
    content = replace_once(content, OLD_TICK_LOOP, NEW_TICK_LOOP, "tick loop wiring")

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
