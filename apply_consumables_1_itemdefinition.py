"""
Food/Potion feature, patch 1/3: data model foundation.

Adds a ConsumableType enum (FOOD/POTION) and three new optional fields to
ItemDefinition: consumableType, healAmount, buffDurationSeconds. All
default to null, so every existing catalog entry (which uses named
arguments exclusively) keeps compiling unchanged. Also populates the
previously-bare minor_healing_potion entry as an instant-heal potion.

Run from repo root: python3 apply_consumables_1_itemdefinition.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/SharedTypes.kt")

OLD_CLASS = '''data class ItemDefinition(
    val id: String,
    val name: String,
    val category: ItemCategory,
    val rarity: Rarity = Rarity.COMMON,
    val isTradeable: Boolean,
    val isStackable: Boolean,
    val isRealMoneyPurchasable: Boolean = false,
    val equipSlot: EquipSlot? = null,
    val combatStyle: CombatStyle? = null,
    val levelRequired: Int = 1,
    val skillRequired: String? = null,
    val stats: ItemStats = ItemStats()
)'''

NEW_CLASS = '''enum class ConsumableType { FOOD, POTION }

data class ItemDefinition(
    val id: String,
    val name: String,
    val category: ItemCategory,
    val rarity: Rarity = Rarity.COMMON,
    val isTradeable: Boolean,
    val isStackable: Boolean,
    val isRealMoneyPurchasable: Boolean = false,
    val equipSlot: EquipSlot? = null,
    val combatStyle: CombatStyle? = null,
    val levelRequired: Int = 1,
    val skillRequired: String? = null,
    val stats: ItemStats = ItemStats(),
    val consumableType: ConsumableType? = null,
    val healAmount: Int? = null,
    val buffDurationSeconds: Int? = null
)'''

OLD_POTION = 'ItemDefinition(id = "minor_healing_potion", name = "Minor Healing Potion", category = ItemCategory.CONSUMABLE, isTradeable = true, isStackable = true),'
NEW_POTION = (
    'ItemDefinition(\n'
    '            id = "minor_healing_potion", name = "Minor Healing Potion", category = ItemCategory.CONSUMABLE,\n'
    '            isTradeable = true, isStackable = true,\n'
    '            consumableType = ConsumableType.POTION, healAmount = 20\n'
    '        ),'
)


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

    if "enum class ConsumableType" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    content = replace_once(content, OLD_CLASS, NEW_CLASS, "ItemDefinition class fields")
    content = replace_once(content, OLD_POTION, NEW_POTION, "minor_healing_potion entry")

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")
    if content.count("(") != content.count(")"):
        raise SystemExit("ABORT: paren mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
