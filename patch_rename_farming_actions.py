path = "app/src/main/kotlin/com/yourname/idlerpg/ActionCatalog.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

pairs = [
    ("potato_seed", "Potato Seed", 10, 3, 1, "potato", "Potato", 10, 3, 1),
    ("onion_seed", "Onion Seed", 10, 3, 1, "onion", "Onion", 10, 3, 1),
    ("cabbage_seed", "Cabbage Seed", 19, 3, 5, "cabbage", "Cabbage", 19, 3, 5),
    ("tomato_seed", "Tomato Seed", 30, 3, 10, "tomato", "Tomato", 30, 3, 10),
    ("sweetcorn_seed", "Sweetcorn Seed", 34, 3, 12, "sweetcorn", "Sweetcorn", 34, 3, 12),
    ("guam_seed", "Guam Seed", 41, 3, 15, "guam_leaf", "Guam Leaf", 41, 3, 15),
    ("strawberry_seed", "Strawberry Seed", 52, 3, 20, "strawberry", "Strawberry", 52, 3, 20),
    ("marrentill_seed", "Marrentill Seed", 63, 4, 25, "marrentill", "Marrentill", 63, 4, 25),
    ("watermelon_seed", "Watermelon Seed", 67, 4, 27, "watermelon", "Watermelon", 67, 4, 27),
    ("apple_sapling", "Apple Tree Sapling", 74, 4, 30, "apple", "Apple", 74, 4, 30),
    ("tarromin_seed", "Tarromin Seed", 78, 4, 32, "tarromin", "Tarromin", 78, 4, 32),
    ("banana_sapling", "Banana Tree Sapling", 85, 4, 35, "banana", "Banana", 85, 4, 35),
    ("harralander_seed", "Harralander Seed", 92, 4, 38, "harralander", "Harralander", 92, 4, 38),
    ("orange_sapling", "Orange Tree Sapling", 96, 4, 40, "orange", "Orange", 96, 4, 40),
    ("ranarr_seed", "Ranarr Seed", 107, 4, 45, "ranarr_weed", "Ranarr Weed", 107, 4, 45),
    ("grape_seed", "Grape Vine Seed", 118, 5, 50, "grapes", "Grapes", 118, 5, 50),
    ("toadflax_seed", "Toadflax Seed", 125, 5, 53, "toadflax", "Toadflax", 125, 5, 53),
    ("papaya_sapling", "Papaya Tree Sapling", 129, 5, 55, "papaya", "Papaya", 129, 5, 55),
    ("irit_seed", "Irit Seed", 140, 5, 60, "irit_leaf", "Irit Leaf", 140, 5, 60),
    ("palm_sapling", "Palm Tree Sapling", 151, 5, 65, "coconut", "Coconut", 151, 5, 65),
    ("avantoe_seed", "Avantoe Seed", 158, 5, 68, "avantoe", "Avantoe", 158, 5, 68),
    ("kwuarm_seed", "Kwuarm Seed", 173, 6, 75, "kwuarm", "Kwuarm", 173, 6, 75),
    ("snapdragon_seed", "Snapdragon Seed", 184, 6, 80, "snapdragon", "Snapdragon", 184, 6, 80),
    ("torstol_seed", "Torstol Seed", 206, 6, 90, "torstol", "Torstol", 206, 6, 90),
    ("celestial_herb_seed", "Celestial Herb Seed", 217, 6, 95, "celestial_herb", "Celestial Herb", 217, 6, 95),
    ("lemon_sapling", "Lemon Tree Sapling", 105, 4, 44, "lemon", "Lemon", 105, 4, 44),
    ("pumpkin_seed", "Pumpkin Seed", 48, 3, 18, "pumpkin", "Pumpkin", 48, 3, 18),
]

for seed_id, seed_name, xp, sec, lvl, crop_id, crop_name, cxp, csec, clvl in pairs:
    old_seed_line = f'        SkillActionDefinition(SkillType.FARMING, "{seed_id}", "Plant/Harvest {seed_name}", xpPerAction = {xp}, secondsPerAction = {sec}, levelRequired = {lvl}),'
    new_seed_line = f'        SkillActionDefinition(SkillType.FARMING, "{seed_id}", "Gather {seed_name}", xpPerAction = {xp}, secondsPerAction = {sec}, levelRequired = {lvl}),'
    count = content.count(old_seed_line)
    assert count == 1, f"Expected 1 match for seed line, found {count}: {old_seed_line!r}"
    content = content.replace(old_seed_line, new_seed_line, 1)

    old_crop_line = f'        SkillActionDefinition(SkillType.FARMING, "{crop_id}", "Plant/Harvest {crop_name}", xpPerAction = {cxp}, secondsPerAction = {csec}, levelRequired = {clvl}),'
    new_crop_line = f'        SkillActionDefinition(SkillType.FARMING, "{crop_id}", "Plant ({seed_name})", xpPerAction = {cxp}, secondsPerAction = {csec}, levelRequired = {clvl}),'
    count = content.count(old_crop_line)
    assert count == 1, f"Expected 1 match for crop line, found {count}: {old_crop_line!r}"
    content = content.replace(old_crop_line, new_crop_line, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("patch_rename_farming_actions.py applied cleanly.")
