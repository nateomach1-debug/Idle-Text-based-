"""
Food/Potion feature, patch 2/3: populate catalog data.

Adds consumableType + healAmount (food) or consumableType +
buffDurationSeconds (stat-buff potions) or consumableType + healAmount
(instant-restore potions: Restore Potion, Super Restore Potion) to all
49 existing food/potion entries in GeneratedItemCatalog.kt. Values are
placeholder balance numbers, easy to retune later -- see the chat for
the full scheme.

Run from repo root: python3 apply_consumables_2_catalog_values.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/GeneratedItemCatalog.kt")

# (id, name, extra_indent, kind, value)
# kind: "FOOD" -> healAmount, "POTION_BUFF" -> buffDurationSeconds, "POTION_HEAL" -> healAmount
ENTRIES = [
    ("cooked_shrimp", "Cooked Shrimp", False, "FOOD", 3),
    ("cooked_anchovies", "Cooked Anchovies", False, "FOOD", 4),
    ("cooked_sardine", "Cooked Sardine", False, "FOOD", 5),
    ("cooked_chicken", "Cooked Chicken", True, "FOOD", 6),
    ("cooked_herring", "Cooked Herring", False, "FOOD", 7),
    ("cooked_beef", "Cooked Beef", False, "FOOD", 8),
    ("cooked_crayfish", "Cooked Crayfish", False, "FOOD", 9),
    ("cooked_trout", "Cooked Trout", False, "FOOD", 10),
    ("cooked_salmon", "Cooked Salmon", False, "FOOD", 11),
    ("bread", "Bread", False, "FOOD", 12),
    ("cooked_tuna", "Cooked Tuna", False, "FOOD", 13),
    ("meat_pie", "Meat Pie", False, "FOOD", 14),
    ("cooked_mackerel", "Cooked Mackerel", False, "FOOD", 15),
    ("cooked_swordfish", "Cooked Swordfish", False, "FOOD", 16),
    ("cake", "Cake", False, "FOOD", 17),
    ("cooked_lobster", "Cooked Lobster", False, "FOOD", 18),
    ("cooked_crab", "Cooked Crab", False, "FOOD", 19),
    ("cooked_shark", "Cooked Shark", False, "FOOD", 20),
    ("stew", "Stew", False, "FOOD", 21),
    ("cooked_monkfish", "Cooked Monkfish", False, "FOOD", 22),
    ("cooked_manta_ray", "Cooked Manta Ray", False, "FOOD", 23),
    ("cooked_eel", "Cooked Eel", False, "FOOD", 24),
    ("cooked_deep_sea_cod", "Cooked Deep Sea Cod", False, "FOOD", 25),
    ("cooked_anglerfish", "Cooked Anglerfish", False, "FOOD", 26),
    ("gourmet_feast", "Gourmet Feast", False, "FOOD", 40),
    ("leviathan_steak", "Leviathan Steak", False, "FOOD", 55),
    ("ambrosia_banquet", "Ambrosia Banquet", False, "FOOD", 75),
    ("attack_potion", "Attack Potion", False, "POTION_BUFF", 180),
    ("antipoison", "Antipoison", False, "POTION_BUFF", 180),
    ("strength_potion", "Strength Potion", False, "POTION_BUFF", 180),
    ("defense_potion", "Defense Potion", False, "POTION_BUFF", 180),
    ("restore_potion", "Restore Potion", False, "POTION_HEAL", 30),
    ("energy_potion", "Energy Potion", False, "POTION_BUFF", 180),
    ("combat_potion", "Combat Potion", False, "POTION_BUFF", 180),
    ("prayer_potion", "Prayer Potion", False, "POTION_BUFF", 180),
    ("super_attack_potion", "Super Attack Potion", False, "POTION_BUFF", 240),
    ("super_strength_potion", "Super Strength Potion", False, "POTION_BUFF", 240),
    ("super_defense_potion", "Super Defense Potion", False, "POTION_BUFF", 240),
    ("ranging_potion", "Ranging Potion", False, "POTION_BUFF", 180),
    ("magic_potion", "Magic Potion", False, "POTION_BUFF", 180),
    ("super_restore_potion", "Super Restore Potion", False, "POTION_HEAL", 50),
    ("antidote_plus", "Antidote+", False, "POTION_BUFF", 180),
    ("brew_of_vigor", "Brew of Vigor", False, "POTION_BUFF", 240),
    ("antifire_potion", "Antifire Potion", False, "POTION_BUFF", 180),
    ("extreme_attack_potion", "Extreme Attack Potion", False, "POTION_BUFF", 300),
    ("extreme_strength_potion", "Extreme Strength Potion", False, "POTION_BUFF", 300),
    ("overload_potion", "Overload Potion", False, "POTION_BUFF", 420),
    ("divine_potion", "Divine Potion", False, "POTION_BUFF", 480),
    ("elixir_of_the_ancients", "Elixir of the Ancients", False, "POTION_BUFF", 600),
]


def build_old(item_id: str, name: str, extra_indent: bool) -> str:
    open_indent = "        " if extra_indent else "    "
    return (
        f'{open_indent}ItemDefinition(\n'
        f'        id = "{item_id}",\n'
        f'        name = "{name}",\n'
        f'        category = ItemCategory.CONSUMABLE,\n'
        f'        isTradeable = true,\n'
        f'        isStackable = true\n'
        f'    ),'
    )


def build_new(item_id: str, name: str, extra_indent: bool, kind: str, value: int) -> str:
    open_indent = "        " if extra_indent else "    "
    if kind == "FOOD":
        extra = f'        consumableType = ConsumableType.FOOD,\n        healAmount = {value}\n'
    elif kind == "POTION_BUFF":
        extra = f'        consumableType = ConsumableType.POTION,\n        buffDurationSeconds = {value}\n'
    else:  # POTION_HEAL
        extra = f'        consumableType = ConsumableType.POTION,\n        healAmount = {value}\n'
    return (
        f'{open_indent}ItemDefinition(\n'
        f'        id = "{item_id}",\n'
        f'        name = "{name}",\n'
        f'        category = ItemCategory.CONSUMABLE,\n'
        f'        isTradeable = true,\n'
        f'        isStackable = true,\n'
        f'{extra}'
        f'    ),'
    )


def main() -> None:
    if not TARGET.exists():
        raise SystemExit(f"ABORT: could not find {TARGET} from the current directory. Run this from the repo root.")

    content = TARGET.read_text()

    if "consumableType = ConsumableType.FOOD" in content or "consumableType = ConsumableType.POTION" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    for item_id, name, extra_indent, kind, value in ENTRIES:
        old = build_old(item_id, name, extra_indent)
        new = build_new(item_id, name, extra_indent, kind, value)
        count = content.count(old)
        if count == 0:
            raise SystemExit(f"ABORT: could not find expected block for '{item_id}'. No changes written.")
        if count > 1:
            raise SystemExit(f"ABORT: found {count} matches for '{item_id}', expected exactly 1. No changes written.")
        content = content.replace(old, new, 1)

    TARGET.write_text(content)
    print(f"OK: patched {TARGET} ({len(ENTRIES)} entries updated)")


if __name__ == "__main__":
    main()
