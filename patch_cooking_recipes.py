ITEMS_EQUIPMENT = "app/src/main/kotlin/com/yourname/idlerpg/ItemsEquipmentSystem.kt"


def main():
    with open(ITEMS_EQUIPMENT, "r", encoding="utf-8") as fh:
        content = fh.read()

    before = content.count("{") - content.count("}")

    old_tail = '''        Recipe(
            outputItemId = "celestial_diadem",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("amulet_u", 1), RecipeIngredient("celestial_crystal", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 90
        )
    )

    fun forOutput(itemId: String): Recipe? = recipes.find { it.outputItemId == itemId }'''
    assert content.count(old_tail) == 1, f"expected 1 occurrence, found {content.count(old_tail)}"

    new_tail = '''        Recipe(
            outputItemId = "celestial_diadem",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("amulet_u", 1), RecipeIngredient("celestial_crystal", 1), RecipeIngredient("bowstring", 1)),
            skillRequired = "CRAFTING",
            levelRequired = 90
        ),
        Recipe(
            outputItemId = "cake_mix",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("flour", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "COOKING",
            levelRequired = 1
        ),
        Recipe(
            outputItemId = "pie_shell",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("flour", 1), RecipeIngredient("vial_of_water", 1)),
            skillRequired = "COOKING",
            levelRequired = 1
        )
    )

    fun forOutput(itemId: String): Recipe? = recipes.find { it.outputItemId == itemId }'''

    content = content.replace(old_tail, new_tail)

    after = content.count("{") - content.count("}")
    assert before == after, f"brace balance changed: {before} -> {after}"

    with open(ITEMS_EQUIPMENT, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Patched {ITEMS_EQUIPMENT} (brace balance unchanged: {before})")


if __name__ == "__main__":
    main()
