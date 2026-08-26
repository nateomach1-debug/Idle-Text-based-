ACTION_CATALOG = "app/src/main/kotlin/com/yourname/idlerpg/ActionCatalog.kt"
GAME_VIEW_MODEL = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"


def patch_action_catalog():
    with open(ACTION_CATALOG, "r", encoding="utf-8") as fh:
        content = fh.read()

    before = content.count("{") - content.count("}")

    # Add the Random import (not currently imported in this file)
    old_header = "package com.yourname.idlerpg\n\ndata class SkillActionDefinition("
    new_header = "package com.yourname.idlerpg\n\nimport kotlin.random.Random\n\ndata class SkillActionDefinition("
    assert content.count(old_header) == 1, f"expected 1 occurrence, found {content.count(old_header)}"
    content = content.replace(old_header, new_header)

    # Append the bonus-gem table object after the ActionCatalog object closes.
    # Rates are deliberately lower than Gem Cavern's rareLootTable rates for
    # the same gem (mining is a bonus/secondary source, combat is primary).
    old_tail = (
        '    fun allFor(skillType: SkillType): List<SkillActionDefinition> =\n'
        '        actions.filter { it.skillType == skillType }\n'
        '}'
    )
    assert content.count(old_tail) == 1, f"expected 1 occurrence, found {content.count(old_tail)}"
    new_tail = old_tail + '''

// Bonus gem drops from Mining, independent of which ore/rock node was mined.
// Rates are set lower than Gem Cavern's rareLootTable for the same gem -
// mining is a secondary source, combat is the primary one.
object MiningBonusGemTable {
    private val entries = listOf(
        "uncut_opal" to 2.0,
        "uncut_jade" to 1.5,
        "uncut_red_topaz" to 1.2,
        "uncut_sapphire" to 1.0,
        "uncut_emerald" to 0.8,
        "uncut_ruby" to 0.5,
        "uncut_diamond" to 0.3,
        "uncut_dragonstone" to 0.15,
        "uncut_onyx" to 0.08,
        "uncut_zenyte" to 0.04,
        "uncut_celestial_crystal" to 0.015
    )

    fun rollAndGrant(inventory: Inventory, actionsCompleted: Int) {
        if (actionsCompleted <= 0) return
        entries.forEach { (itemId, chancePercent) ->
            var count = 0
            repeat(actionsCompleted) {
                if (Random.nextDouble(0.0, 100.0) < chancePercent) count++
            }
            if (count > 0) inventory.addItem(itemId, count)
        }
    }
}'''
    content = content.replace(old_tail, new_tail)

    after = content.count("{") - content.count("}")
    assert before == after, f"brace balance changed: {before} -> {after}"

    with open(ACTION_CATALOG, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Patched {ACTION_CATALOG} (brace balance unchanged: {before})")


def patch_game_view_model():
    with open(GAME_VIEW_MODEL, "r", encoding="utf-8") as fh:
        content = fh.read()

    before = content.count("{") - content.count("}")

    # Site A: offline-progress resolution path
    old_a = '                    inventoryService.inventoryFor(characterId).addItem(queue.itemId, result.value.actionsCompleted)'
    assert content.count(old_a) == 1, f"expected 1 occurrence, found {content.count(old_a)}"
    new_a = old_a + '''
                    if (skillType == SkillType.MINING) {
                        MiningBonusGemTable.rollAndGrant(inventoryService.inventoryFor(characterId), result.value.actionsCompleted)
                    }'''
    content = content.replace(old_a, new_a)

    # Site B: live tickSkilling path
    old_b = '            inventoryService.inventoryFor(characterId).addItem(queue.itemId, actionsCompleted.toInt())'
    assert content.count(old_b) == 1, f"expected 1 occurrence, found {content.count(old_b)}"
    new_b = old_b + '''
            if (skillType == SkillType.MINING) {
                MiningBonusGemTable.rollAndGrant(inventoryService.inventoryFor(characterId), actionsCompleted.toInt())
            }'''
    content = content.replace(old_b, new_b)

    after = content.count("{") - content.count("}")
    assert before == after, f"brace balance changed: {before} -> {after}"

    with open(GAME_VIEW_MODEL, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Patched {GAME_VIEW_MODEL} (brace balance unchanged: {before})")


if __name__ == "__main__":
    patch_action_catalog()
    patch_game_view_model()
    print("Done.")
