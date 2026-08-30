# patch_add_pies_and_fruits.py
action_path = "app/src/main/kotlin/com/yourname/idlerpg/ActionCatalog.kt"
with open(action_path, encoding="utf-8") as f:
    content = f.read()

edits = [
    (
        '''        SkillActionDefinition(SkillType.FARMING, "orange", "Plant/Harvest Orange", xpPerAction = 96, secondsPerAction = 4, levelRequired = 40),
        SkillActionDefinition(SkillType.FARMING, "ranarr_seed", "Plant/Harvest Ranarr Seed", xpPerAction = 107, secondsPerAction = 4, levelRequired = 45),''',
        '''        SkillActionDefinition(SkillType.FARMING, "orange", "Plant/Harvest Orange", xpPerAction = 96, secondsPerAction = 4, levelRequired = 40),
        SkillActionDefinition(SkillType.FARMING, "lemon_sapling", "Plant/Harvest Lemon Tree Sapling", xpPerAction = 105, secondsPerAction = 4, levelRequired = 44),
        SkillActionDefinition(SkillType.FARMING, "lemon", "Plant/Harvest Lemon", xpPerAction = 105, secondsPerAction = 4, levelRequired = 44),
        SkillActionDefinition(SkillType.FARMING, "ranarr_seed", "Plant/Harvest Ranarr Seed", xpPerAction = 107, secondsPerAction = 4, levelRequired = 45),'''
    ),
    (
        '''        SkillActionDefinition(SkillType.FARMING, "guam_leaf", "Plant/Harvest Guam Leaf", xpPerAction = 41, secondsPerAction = 3, levelRequired = 15),
        SkillActionDefinition(SkillType.FARMING, "strawberry_seed", "Plant/Harvest Strawberry Seed", xpPerAction = 52, secondsPerAction = 3, levelRequired = 20),''',
        '''        SkillActionDefinition(SkillType.FARMING, "guam_leaf", "Plant/Harvest Guam Leaf", xpPerAction = 41, secondsPerAction = 3, levelRequired = 15),
        SkillActionDefinition(SkillType.FARMING, "pumpkin_seed", "Plant/Harvest Pumpkin Seed", xpPerAction = 48, secondsPerAction = 3, levelRequired = 18),
        SkillActionDefinition(SkillType.FARMING, "pumpkin", "Plant/Harvest Pumpkin", xpPerAction = 48, secondsPerAction = 3, levelRequired = 18),
        SkillActionDefinition(SkillType.FARMING, "strawberry_seed", "Plant/Harvest Strawberry Seed", xpPerAction = 52, secondsPerAction = 3, levelRequired = 20),'''
    ),
    (
        '''        SkillActionDefinition(SkillType.COOKING, "meat_pie", "Bake Meat Pie", xpPerAction = 83, secondsPerAction = 4, levelRequired = 34),
        SkillActionDefinition(SkillType.COOKING, "mackerel", "Cook Mackerel", xpPerAction = 85, secondsPerAction = 4, levelRequired = 35),''',
        '''        SkillActionDefinition(SkillType.COOKING, "meat_pie", "Bake Meat Pie", xpPerAction = 83, secondsPerAction = 4, levelRequired = 34),
        SkillActionDefinition(SkillType.COOKING, "apple_pie", "Bake Apple Pie", xpPerAction = 87, secondsPerAction = 4, levelRequired = 36),
        SkillActionDefinition(SkillType.COOKING, "mackerel", "Cook Mackerel", xpPerAction = 85, secondsPerAction = 4, levelRequired = 35),'''
    ),
    (
        '''        SkillActionDefinition(SkillType.COOKING, "swordfish", "Cook Swordfish", xpPerAction = 96, secondsPerAction = 4, levelRequired = 40),
        SkillActionDefinition(SkillType.COOKING, "cake", "Bake Cake", xpPerAction = 100, secondsPerAction = 4, levelRequired = 42),''',
        '''        SkillActionDefinition(SkillType.COOKING, "swordfish", "Cook Swordfish", xpPerAction = 96, secondsPerAction = 4, levelRequired = 40),
        SkillActionDefinition(SkillType.COOKING, "lemon_pie", "Bake Lemon Pie", xpPerAction = 98, secondsPerAction = 4, levelRequired = 41),
        SkillActionDefinition(SkillType.COOKING, "cake", "Bake Cake", xpPerAction = 100, secondsPerAction = 4, levelRequired = 42),'''
    ),
    (
        '''        SkillActionDefinition(SkillType.COOKING, "lobster", "Cook Lobster", xpPerAction = 107, secondsPerAction = 4, levelRequired = 45),
        SkillActionDefinition(SkillType.COOKING, "crab", "Cook Crab", xpPerAction = 118, secondsPerAction = 5, levelRequired = 50),''',
        '''        SkillActionDefinition(SkillType.COOKING, "lobster", "Cook Lobster", xpPerAction = 107, secondsPerAction = 4, levelRequired = 45),
        SkillActionDefinition(SkillType.COOKING, "pumpkin_pie", "Bake Pumpkin Pie", xpPerAction = 114, secondsPerAction = 4, levelRequired = 48),
        SkillActionDefinition(SkillType.COOKING, "crab", "Cook Crab", xpPerAction = 118, secondsPerAction = 5, levelRequired = 50),'''
    ),
]
for anchor, replacement in edits:
    count = content.count(anchor)
    assert count == 1, f"Expected 1 match, found {count}: {anchor!r}"
    content = content.replace(anchor, replacement, 1)
with open(action_path, "w", encoding="utf-8") as f:
    f.write(content)

item_path = "app/src/main/kotlin/com/yourname/idlerpg/GeneratedItemCatalog.kt"
with open(item_path, encoding="utf-8") as f:
    content = f.read()

anchor_apple_block = '''    ItemDefinition(
        id = "apple_sapling",
        name = "Apple Tree Sapling",
        category = ItemCategory.MATERIAL,
        isTradeable = true,
        isStackable = true
    ),
    ItemDefinition(
        id = "apple",
        name = "Apple",
        category = ItemCategory.MATERIAL,
        isTradeable = true,
        isStackable = true
    ),'''
count = content.count(anchor_apple_block)
assert count == 1, f"Expected 1 match, found {count}."
replacement_apple_block = anchor_apple_block + '''
    ItemDefinition(
        id = "lemon_sapling",
        name = "Lemon Tree Sapling",
        category = ItemCategory.MATERIAL,
        isTradeable = true,
        isStackable = true
    ),
    ItemDefinition(
        id = "lemon",
        name = "Lemon",
        category = ItemCategory.MATERIAL,
        isTradeable = true,
        isStackable = true
    ),
    ItemDefinition(
        id = "pumpkin_seed",
        name = "Pumpkin Seed",
        category = ItemCategory.MATERIAL,
        isTradeable = true,
        isStackable = true
    ),
    ItemDefinition(
        id = "pumpkin",
        name = "Pumpkin",
        category = ItemCategory.MATERIAL,
        isTradeable = true,
        isStackable = true
    ),'''
content = content.replace(anchor_apple_block, replacement_apple_block, 1)

anchor_meat_pie_block = '''    ItemDefinition(
        id = "meat_pie",
        name = "Meat Pie",
        category = ItemCategory.CONSUMABLE,
        isTradeable = true,
        isStackable = true,
        consumableType = ConsumableType.FOOD,
        healAmount = 14
    ),'''
count = content.count(anchor_meat_pie_block)
assert count == 1, f"Expected 1 match, found {count}."
replacement_meat_pie_block = anchor_meat_pie_block + '''
    ItemDefinition(
        id = "apple_pie",
        name = "Apple Pie",
        category = ItemCategory.CONSUMABLE,
        isTradeable = true,
        isStackable = true,
        consumableType = ConsumableType.FOOD,
        healAmount = 14
    ),
    ItemDefinition(
        id = "lemon_pie",
        name = "Lemon Pie",
        category = ItemCategory.CONSUMABLE,
        isTradeable = true,
        isStackable = true,
        consumableType = ConsumableType.FOOD,
        healAmount = 14
    ),
    ItemDefinition(
        id = "pumpkin_pie",
        name = "Pumpkin Pie",
        category = ItemCategory.CONSUMABLE,
        isTradeable = true,
        isStackable = true,
        consumableType = ConsumableType.FOOD,
        healAmount = 14
    ),'''
content = content.replace(anchor_meat_pie_block, replacement_meat_pie_block, 1)

anchor_price1 = '''    "apple_sapling" to 12L,
    "apple" to 6L,'''
count = content.count(anchor_price1)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(anchor_price1, anchor_price1 + '''
    "lemon_sapling" to 24L,
    "lemon" to 9L,''', 1)

anchor_price2 = '''    "guam_seed" to 5L,
    "guam_leaf" to 8L,'''
count = content.count(anchor_price2)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(anchor_price2, anchor_price2 + '''
    "pumpkin_seed" to 6L,
    "pumpkin" to 9L,''', 1)

anchor_price3 = '"meat_pie" to 30L,'
count = content.count(anchor_price3)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(anchor_price3, anchor_price3 + '''
    "apple_pie" to 24L,
    "lemon_pie" to 27L,
    "pumpkin_pie" to 32L,''', 1)

with open(item_path, "w", encoding="utf-8") as f:
    f.write(content)

recipe_path = "app/src/main/kotlin/com/yourname/idlerpg/ItemsEquipmentSystem.kt"
with open(recipe_path, encoding="utf-8") as f:
    content = f.read()

anchor_recipe = '''        Recipe(
            outputItemId = "meat_pie",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("pie_shell", 1), RecipeIngredient("cooked_beef", 1)),
            skillRequired = "COOKING",
            levelRequired = 34
        ),'''
count = content.count(anchor_recipe)
assert count == 1, f"Expected 1 match, found {count}."
replacement_recipe = anchor_recipe + '''
        Recipe(
            outputItemId = "apple_pie",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("pie_shell", 1), RecipeIngredient("apple", 1)),
            skillRequired = "COOKING",
            levelRequired = 36
        ),
        Recipe(
            outputItemId = "lemon_pie",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("pie_shell", 1), RecipeIngredient("lemon", 1)),
            skillRequired = "COOKING",
            levelRequired = 41
        ),
        Recipe(
            outputItemId = "pumpkin_pie",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("pie_shell", 1), RecipeIngredient("pumpkin", 1)),
            skillRequired = "COOKING",
            levelRequired = 48
        ),'''
content = content.replace(anchor_recipe, replacement_recipe, 1)

with open(recipe_path, "w", encoding="utf-8") as f:
    f.write(content)

print("patch_add_pies_and_fruits.py applied cleanly.")
