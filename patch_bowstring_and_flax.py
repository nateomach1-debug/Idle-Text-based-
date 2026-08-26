import re

ACTION_CATALOG = "app/src/main/kotlin/com/yourname/idlerpg/ActionCatalog.kt"
ITEMS_EQUIPMENT = "app/src/main/kotlin/com/yourname/idlerpg/ItemsEquipmentSystem.kt"


def patch_action_catalog():
    with open(ACTION_CATALOG, "r", encoding="utf-8") as fh:
        content = fh.read()

    before = content.count("{") - content.count("}")

    # 1. The "Spin Flax into Bowstring" action currently produces an item
    #    literally named "flax_into_bowstring" instead of "bowstring" - fix
    #    it to match the established "leather"/"cake"/gem-cutting convention
    #    where a CRAFTING action can produce a finished item directly.
    old_action = 'SkillActionDefinition(SkillType.CRAFTING, "flax_into_bowstring", "Spin Flax into Bowstring", xpPerAction = 74, secondsPerAction = 4, levelRequired = 30),'
    new_action = 'SkillActionDefinition(SkillType.CRAFTING, "bowstring", "Spin Flax into Bowstring", xpPerAction = 74, secondsPerAction = 4, levelRequired = 30),'
    assert content.count(old_action) == 1, f"expected 1 occurrence, found {content.count(old_action)}"
    content = content.replace(old_action, new_action)

    # 2. flax itself has no source anywhere - add it as a new Farming crop,
    #    right after the last existing Farming entry (world_tree_sapling).
    old_tail = (
        '        SkillActionDefinition(SkillType.FARMING, "world_tree_sapling", "Plant/Harvest World Tree Sapling", xpPerAction = 226, secondsPerAction = 6, levelRequired = 99),\n'
        '        SkillActionDefinition(SkillType.THIEVING, "peasants_purse",'
    )
    new_tail = (
        '        SkillActionDefinition(SkillType.FARMING, "world_tree_sapling", "Plant/Harvest World Tree Sapling", xpPerAction = 226, secondsPerAction = 6, levelRequired = 99),\n'
        '        SkillActionDefinition(SkillType.FARMING, "flax", "Plant/Harvest Flax", xpPerAction = 34, secondsPerAction = 3, levelRequired = 12),\n'
        '        SkillActionDefinition(SkillType.THIEVING, "peasants_purse",'
    )
    assert content.count(old_tail) == 1, f"expected 1 occurrence, found {content.count(old_tail)}"
    content = content.replace(old_tail, new_tail)

    after = content.count("{") - content.count("}")
    assert before == after, f"brace balance changed: {before} -> {after}"

    with open(ACTION_CATALOG, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Patched {ACTION_CATALOG} (brace balance unchanged: {before})")


def patch_items_equipment():
    with open(ITEMS_EQUIPMENT, "r", encoding="utf-8") as fh:
        content = fh.read()

    before = content.count("{") - content.count("}")

    old_line = 'outputItemId = "flax_into_bowstring",'
    new_line = 'outputItemId = "bowstring",'
    assert content.count(old_line) == 1, f"expected 1 occurrence, found {content.count(old_line)}"
    content = content.replace(old_line, new_line)

    after = content.count("{") - content.count("}")
    assert before == after, f"brace balance changed: {before} -> {after}"

    with open(ITEMS_EQUIPMENT, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Patched {ITEMS_EQUIPMENT} (brace balance unchanged: {before})")


if __name__ == "__main__":
    patch_action_catalog()
    patch_items_equipment()
    print("Done.")
