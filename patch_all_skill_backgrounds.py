#!/usr/bin/env python3
"""
Guarded patch: 13 new craftable magic weapons (Crafting skill) + 4 new
elemental essence materials gathered from combat.

Touches: GeneratedItemCatalog.kt (new ItemDefinitions), ItemsEquipmentSystem.kt
(new Recipes), CombatSystem.kt (essence drop chance in rollLoot()).
"""
import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def guarded_replace(path, old, new, marker):
    content = read(path)
    if marker in content:
        print(f"SKIP (already applied): {path} :: {marker[:50]}")
        return
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly 1 match in {path}, found {count}.\n--- old_str ---\n{old}\n--- end ---")
    write(path, content.replace(old, new))
    print(f"PATCHED: {path} :: {marker[:50]}")


ELEMENTS = ["fire", "earth", "water", "wind"]

# =======================================================================
# 1. GeneratedItemCatalog.kt - 4 essence materials + 13 weapon items
# =======================================================================
cat_path = os.path.join(ROOT, "GeneratedItemCatalog.kt")

essence_defs = "\n".join(
    f'    ItemDefinition(\n'
    f'        id = "{el}_essence",\n'
    f'        name = "{el.capitalize()} Essence",\n'
    f'        category = ItemCategory.MATERIAL,\n'
    f'        isTradeable = true,\n'
    f'        isStackable = true\n'
    f'    ),'
    for el in ELEMENTS
)

weapon_defs = []
# Tier 1: Staff (equip Magic 1)
weapon_defs.append(
    '    ItemDefinition(\n'
    '        id = "staff",\n'
    '        name = "Staff",\n'
    '        category = ItemCategory.WEAPON,\n'
    '        isTradeable = true,\n'
    '        isStackable = false,\n'
    '        equipSlot = EquipSlot.WEAPON,\n'
    '        combatStyle = CombatStyle.MAGIC,\n'
    '        levelRequired = 1,\n'
    '        skillRequired = "MAGIC",\n'
    '        stats = ItemStats(attackBonus = 5, strengthBonus = 0, accuracyBonus = 10, maxHitBonus = 5)\n'
    '    ),'
)
# Tier 2: Elemental Staffs (equip Magic 10)
for el in ELEMENTS:
    weapon_defs.append(
        f'    ItemDefinition(\n'
        f'        id = "{el}_staff",\n'
        f'        name = "{el.capitalize()} Staff",\n'
        f'        category = ItemCategory.WEAPON,\n'
        f'        isTradeable = true,\n'
        f'        isStackable = false,\n'
        f'        equipSlot = EquipSlot.WEAPON,\n'
        f'        combatStyle = CombatStyle.MAGIC,\n'
        f'        levelRequired = 10,\n'
        f'        skillRequired = "MAGIC",\n'
        f'        stats = ItemStats(attackBonus = 15, strengthBonus = 0, accuracyBonus = 25, maxHitBonus = 15)\n'
        f'    ),'
    )
# Tier 3: Elemental Battlestaffs (equip Magic 50)
for el in ELEMENTS:
    weapon_defs.append(
        f'    ItemDefinition(\n'
        f'        id = "{el}_battlestaff",\n'
        f'        name = "{el.capitalize()} Battlestaff",\n'
        f'        category = ItemCategory.WEAPON,\n'
        f'        isTradeable = true,\n'
        f'        isStackable = false,\n'
        f'        equipSlot = EquipSlot.WEAPON,\n'
        f'        combatStyle = CombatStyle.MAGIC,\n'
        f'        levelRequired = 50,\n'
        f'        skillRequired = "MAGIC",\n'
        f'        stats = ItemStats(attackBonus = 50, strengthBonus = 0, accuracyBonus = 85, maxHitBonus = 55)\n'
        f'    ),'
    )
# Tier 4: Mystic Staffs (equip Magic 75)
for el in ELEMENTS:
    weapon_defs.append(
        f'    ItemDefinition(\n'
        f'        id = "mystic_{el}_staff",\n'
        f'        name = "Mystic {el.capitalize()} Staff",\n'
        f'        category = ItemCategory.WEAPON,\n'
        f'        isTradeable = true,\n'
        f'        isStackable = false,\n'
        f'        equipSlot = EquipSlot.WEAPON,\n'
        f'        combatStyle = CombatStyle.MAGIC,\n'
        f'        levelRequired = 75,\n'
        f'        skillRequired = "MAGIC",\n'
        f'        stats = ItemStats(attackBonus = 70, strengthBonus = 0, accuracyBonus = 120, maxHitBonus = 75)\n'
        f'    ),'
    )

all_new_items = essence_defs + "\n" + "\n".join(weapon_defs) + "\n"

old_battlestaff_block = (
    "    ItemDefinition(\n"
    "        id = \"battlestaff\",\n"
    "        name = \"Battlestaff\",\n"
    "        category = ItemCategory.WEAPON,\n"
    "        isTradeable = true,\n"
    "        isStackable = false,\n"
    "        equipSlot = EquipSlot.WEAPON,\n"
    "        combatStyle = CombatStyle.MAGIC,\n"
    "        levelRequired = 30,\n"
    "        skillRequired = \"MAGIC\",\n"
    "            stats = ItemStats(attackBonus = 38, strengthBonus = 0, accuracyBonus = 60, maxHitBonus = 40)\n"
    "        ),\n"
)
new_battlestaff_block = old_battlestaff_block + all_new_items

guarded_replace(
    cat_path, old_battlestaff_block, new_battlestaff_block,
    marker='id = "staff",\n        name = "Staff",',
)

# =======================================================================
# 2. ItemsEquipmentSystem.kt - 13 new Crafting recipes
# =======================================================================
ies_path = os.path.join(ROOT, "ItemsEquipmentSystem.kt")

recipe_defs = []
recipe_defs.append(
    '        Recipe(\n'
    '            outputItemId = "staff",\n'
    '            outputQuantity = 1,\n'
    '            ingredients = listOf(RecipeIngredient("copper_ore", 2), RecipeIngredient("tin_ore", 1)),\n'
    '            skillRequired = "CRAFTING",\n'
    '            levelRequired = 1\n'
    '        ),'
)
for el in ELEMENTS:
    recipe_defs.append(
        f'        Recipe(\n'
        f'            outputItemId = "{el}_staff",\n'
        f'            outputQuantity = 1,\n'
        f'            ingredients = listOf(RecipeIngredient("staff", 1), RecipeIngredient("{el}_essence", 3)),\n'
        f'            skillRequired = "CRAFTING",\n'
        f'            levelRequired = 8\n'
        f'        ),'
    )
for el in ELEMENTS:
    recipe_defs.append(
        f'        Recipe(\n'
        f'            outputItemId = "{el}_battlestaff",\n'
        f'            outputQuantity = 1,\n'
        f'            ingredients = listOf(RecipeIngredient("{el}_staff", 1), RecipeIngredient("{el}_essence", 5), RecipeIngredient("volcanic_rock", 1)),\n'
        f'            skillRequired = "CRAFTING",\n'
        f'            levelRequired = 45\n'
        f'        ),'
    )
for el in ELEMENTS:
    recipe_defs.append(
        f'        Recipe(\n'
        f'            outputItemId = "mystic_{el}_staff",\n'
        f'            outputQuantity = 1,\n'
        f'            ingredients = listOf(RecipeIngredient("{el}_battlestaff", 1), RecipeIngredient("{el}_essence", 8), RecipeIngredient("celestial_silver", 1)),\n'
        f'            skillRequired = "CRAFTING",\n'
        f'            levelRequired = 65\n'
        f'        ),'
    )

all_new_recipes = "\n".join(recipe_defs) + "\n"

old_battlestaff_recipe = (
    "        Recipe(\n"
    "            outputItemId = \"battlestaff\",\n"
    "            outputQuantity = 1,\n"
    "            ingredients = listOf(RecipeIngredient(\"volcanic_rock\", 1), RecipeIngredient(\"celestial_silver\", 1)),\n"
    "            skillRequired = \"CRAFTING\",\n"
    "            levelRequired = 50\n"
    "        ),\n"
)
new_battlestaff_recipe = old_battlestaff_recipe + all_new_recipes

guarded_replace(
    ies_path, old_battlestaff_recipe, new_battlestaff_recipe,
    marker='outputItemId = "staff",\n            outputQuantity = 1,\n            ingredients = listOf(RecipeIngredient("copper_ore", 2)',
)

# =======================================================================
# 3. CombatSystem.kt - essence drop chance in rollLoot()
# =======================================================================
combat_path = os.path.join(ROOT, "CombatSystem.kt")

old_roll_loot_tail = (
    "        state.lootPool.add(LootEntry(boneType, 1, 1, 100.0))\n"
    "        state.pendingCoins += CoinDropTable.rollCoins(monster.levelRequirement)\n"
    "    }\n"
)
new_roll_loot_tail = (
    "        state.lootPool.add(LootEntry(boneType, 1, 1, 100.0))\n"
    "        state.pendingCoins += CoinDropTable.rollCoins(monster.levelRequirement)\n"
    "\n"
    "        // Elemental essences (Fire/Earth/Water/Wind) used for magic weapon\n"
    "        // crafting - a flat chance per kill to gather one, uniformly random\n"
    "        // type, independent of the monster's own loot table (same guaranteed-\n"
    "        // roll pattern as bones, works across all zones without needing\n"
    "        // per-monster loot table entries).\n"
    "        if (Random.nextDouble(0.0, 100.0) < 15.0) {\n"
    "            val essenceType = listOf(\"fire_essence\", \"earth_essence\", \"water_essence\", \"wind_essence\").random()\n"
    "            state.lootPool.add(LootEntry(essenceType, 1, 1, 100.0))\n"
    "        }\n"
    "    }\n"
)

guarded_replace(
    combat_path, old_roll_loot_tail, new_roll_loot_tail,
    marker="Elemental essences (Fire/Earth/Water/Wind) used for magic weapon",
)

print("\nAll magic weapon patches applied successfully.")
