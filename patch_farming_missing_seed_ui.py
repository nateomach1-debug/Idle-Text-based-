# 1. Move farmingSeedRequirements out of GameViewModel.kt into a shared
#    top-level constant in ActionCatalog.kt.
gvm_path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(gvm_path, encoding="utf-8") as f:
    content = f.read()

anchor_map_block = '''    // Crop-harvest FARMING actions each require consuming one of the
    // corresponding seed/sapling item per action performed. Pure seed-gathering
    // actions (the values on the right, e.g. "guam_seed") are unaffected - they
    // remain free. Deliberately excludes willow_sapling/magic_sapling/
    // elder_sapling/world_tree_sapling (no separate crop step) and flax (no
    // seed at all).
    private val farmingSeedRequirements: Map<String, String> = mapOf(
        "potato" to "potato_seed",
        "onion" to "onion_seed",
        "cabbage" to "cabbage_seed",
        "tomato" to "tomato_seed",
        "sweetcorn" to "sweetcorn_seed",
        "guam_leaf" to "guam_seed",
        "strawberry" to "strawberry_seed",
        "marrentill" to "marrentill_seed",
        "watermelon" to "watermelon_seed",
        "apple" to "apple_sapling",
        "tarromin" to "tarromin_seed",
        "banana" to "banana_sapling",
        "harralander" to "harralander_seed",
        "orange" to "orange_sapling",
        "ranarr_weed" to "ranarr_seed",
        "grapes" to "grape_seed",
        "toadflax" to "toadflax_seed",
        "papaya" to "papaya_sapling",
        "irit_leaf" to "irit_seed",
        "coconut" to "palm_sapling",
        "avantoe" to "avantoe_seed",
        "kwuarm" to "kwuarm_seed",
        "snapdragon" to "snapdragon_seed",
        "torstol" to "torstol_seed",
        "celestial_herb" to "celestial_herb_seed",
        "lemon" to "lemon_sapling",
        "pumpkin" to "pumpkin_seed"
    )

    fun startSkillAction(skillType: SkillType, itemId: String) {
        val characterId = _currentCharacterId.value ?: return
        val action = ActionCatalog.find(skillType, itemId) ?: return
        val requiredSeedId = farmingSeedRequirements[itemId]'''
count = content.count(anchor_map_block)
assert count == 1, f"Expected 1 match, found {count}."
replacement_map_block = '''    fun startSkillAction(skillType: SkillType, itemId: String) {
        val characterId = _currentCharacterId.value ?: return
        val action = ActionCatalog.find(skillType, itemId) ?: return
        val requiredSeedId = FarmingSeedRequirements[itemId]'''
content = content.replace(anchor_map_block, replacement_map_block, 1)

anchor_tick_ref = '            val requiredSeedId = farmingSeedRequirements[queue.itemId]'
count = content.count(anchor_tick_ref)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(anchor_tick_ref, '            val requiredSeedId = FarmingSeedRequirements[queue.itemId]', 1)

with open(gvm_path, "w", encoding="utf-8") as f:
    f.write(content)

# 2. Add the shared constant to ActionCatalog.kt, right after the FARMING
#    section ends (anchored on the last FARMING line, "flax").
action_path = "app/src/main/kotlin/com/yourname/idlerpg/ActionCatalog.kt"
with open(action_path, encoding="utf-8") as f:
    content = f.read()

anchor_flax = '        SkillActionDefinition(SkillType.FARMING, "flax", "Plant/Harvest Flax", xpPerAction = 34, secondsPerAction = 3, levelRequired = 12),'
count = content.count(anchor_flax)
assert count == 1, f"Expected 1 match, found {count}."
# Note: this constant must live outside the enclosing object/list literal that
# holds the SkillActionDefinition entries, so it's appended at file end instead
# of inline - see the final append step below.
with open(action_path, "w", encoding="utf-8") as f:
    f.write(content)

with open(action_path, "a", encoding="utf-8") as f:
    f.write('''

// Crop-harvest FARMING actions each require consuming one of the corresponding
// seed/sapling item per action performed. Pure seed-gathering actions (the
// values on the right, e.g. "guam_seed") are unaffected - they remain free.
// Deliberately excludes willow_sapling/magic_sapling/elder_sapling/
// world_tree_sapling (no separate crop step) and flax (no seed at all).
val FarmingSeedRequirements: Map<String, String> = mapOf(
    "potato" to "potato_seed",
    "onion" to "onion_seed",
    "cabbage" to "cabbage_seed",
    "tomato" to "tomato_seed",
    "sweetcorn" to "sweetcorn_seed",
    "guam_leaf" to "guam_seed",
    "strawberry" to "strawberry_seed",
    "marrentill" to "marrentill_seed",
    "watermelon" to "watermelon_seed",
    "apple" to "apple_sapling",
    "tarromin" to "tarromin_seed",
    "banana" to "banana_sapling",
    "harralander" to "harralander_seed",
    "orange" to "orange_sapling",
    "ranarr_weed" to "ranarr_seed",
    "grapes" to "grape_seed",
    "toadflax" to "toadflax_seed",
    "papaya" to "papaya_sapling",
    "irit_leaf" to "irit_seed",
    "coconut" to "palm_sapling",
    "avantoe" to "avantoe_seed",
    "kwuarm" to "kwuarm_seed",
    "snapdragon" to "snapdragon_seed",
    "torstol" to "torstol_seed",
    "celestial_herb" to "celestial_herb_seed",
    "lemon" to "lemon_sapling",
    "pumpkin" to "pumpkin_seed"
)
''')

# 3. Wire it into buildSkillDetailState()'s else branch in MainActivity.kt.
main_path = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(main_path, encoding="utf-8") as f:
    content = f.read()

anchor_else = '''    } else {
        ActionCatalog.allFor(skillType)
            .filter { it.levelRequired <= summary.level }
            .map { SkillActionSummary(it.itemId, it.displayName, it.levelRequired) }
    }'''
count = content.count(anchor_else)
assert count == 1, f"Expected 1 match, found {count}."
replacement_else = '''    } else {
        ActionCatalog.allFor(skillType)
            .filter { it.levelRequired <= summary.level }
            .map { action ->
                val requiredSeedId = if (skillId == "FARMING") FarmingSeedRequirements[action.itemId] else null
                val missing = if (requiredSeedId != null) {
                    missingIngredientsFor(listOf(RecipeIngredient(requiredSeedId, 1)), inventoryQuantities)
                } else {
                    emptyList()
                }
                SkillActionSummary(action.itemId, action.displayName, action.levelRequired, missing)
            }
    }'''
content = content.replace(anchor_else, replacement_else, 1)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("patch_farming_missing_seed_ui.py applied cleanly.")
