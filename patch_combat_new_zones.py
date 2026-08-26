COMBAT_SYSTEM = "app/src/main/kotlin/com/yourname/idlerpg/CombatSystem.kt"


def main():
    with open(COMBAT_SYSTEM, "r", encoding="utf-8") as fh:
        content = fh.read()

    before = content.count("{") - content.count("}")

    old_tail = (
        '        )\n'
        '    )\n'
        '\n'
        '    fun zonesAvailableAt(level: Int): List<Zone> = zones.filter { it.levelRequirement <= level }'
    )
    assert content.count(old_tail) == 1, f"expected 1 occurrence, found {content.count(old_tail)}"

    new_zones = '''        ),
        Zone(
            id = "farmland_outskirts",
            name = "Farmland Outskirts",
            levelRequirement = 1,
            monsters = listOf(
                Monster(
                    id = "wild_cow",
                    name = "Wild Cow",
                    levelRequirement = 1,
                    maxHealth = 20,
                    defenseRating = 3,
                    mainLootTable = listOf(
                        LootEntry("cowhide", 1, 1, 65.0),
                        LootEntry("raw_beef", 1, 2, 65.0)
                    ),
                    rareLootTable = listOf()
                ),
                Monster(
                    id = "feral_chicken",
                    name = "Feral Chicken",
                    levelRequirement = 1,
                    maxHealth = 12,
                    defenseRating = 1,
                    mainLootTable = listOf(
                        LootEntry("raw_chicken", 1, 1, 65.0),
                        LootEntry("feathers", 1, 5, 70.0)
                    ),
                    rareLootTable = listOf()
                )
            )
        ),
        Zone(
            id = "serpent_marsh",
            name = "Serpent Marsh",
            levelRequirement = 10,
            monsters = listOf(
                Monster(
                    id = "marsh_snake",
                    name = "Marsh Snake",
                    levelRequirement = 10,
                    maxHealth = 35,
                    defenseRating = 10,
                    mainLootTable = listOf(
                        LootEntry("snake_hide", 1, 1, 55.0)
                    ),
                    rareLootTable = listOf()
                )
            )
        ),
        Zone(
            id = "gem_cavern",
            name = "Gem Cavern",
            levelRequirement = 15,
            monsters = listOf(
                Monster(
                    id = "gem_hoarder",
                    name = "Gem Hoarder",
                    levelRequirement = 15,
                    maxHealth = 45,
                    defenseRating = 15,
                    mainLootTable = listOf(
                        LootEntry("uncut_gemstone", 1, 2, 45.0)
                    ),
                    rareLootTable = listOf(
                        LootEntry("uncut_opal", 1, 1, 8.0),
                        LootEntry("uncut_jade", 1, 1, 6.0),
                        LootEntry("uncut_red_topaz", 1, 1, 5.0),
                        LootEntry("uncut_sapphire", 1, 1, 4.0),
                        LootEntry("uncut_emerald", 1, 1, 3.0),
                        LootEntry("uncut_ruby", 1, 1, 2.0),
                        LootEntry("uncut_diamond", 1, 1, 1.2),
                        LootEntry("uncut_dragonstone", 1, 1, 0.6),
                        LootEntry("uncut_onyx", 1, 1, 0.3),
                        LootEntry("uncut_zenyte", 1, 1, 0.15),
                        LootEntry("uncut_celestial_crystal", 1, 1, 0.05)
                    )
                )
            )
        ),
        Zone(
            id = "dragons_lair",
            name = "Dragon's Lair",
            levelRequirement = 60,
            monsters = listOf(
                Monster(
                    id = "green_dragon",
                    name = "Green Dragon",
                    levelRequirement = 60,
                    maxHealth = 220,
                    defenseRating = 65,
                    mainLootTable = listOf(
                        LootEntry("green_dragonhide", 1, 1, 60.0)
                    ),
                    rareLootTable = listOf()
                ),
                Monster(
                    id = "blue_dragon",
                    name = "Blue Dragon",
                    levelRequirement = 65,
                    maxHealth = 260,
                    defenseRating = 75,
                    mainLootTable = listOf(
                        LootEntry("blue_dragonhide", 1, 1, 55.0)
                    ),
                    rareLootTable = listOf()
                )
            )
        )
    )

    fun zonesAvailableAt(level: Int): List<Zone> = zones.filter { it.levelRequirement <= level }'''

    content = content.replace(old_tail, new_zones)

    after = content.count("{") - content.count("}")
    assert before == after, f"brace balance changed: {before} -> {after}"

    with open(COMBAT_SYSTEM, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Patched {COMBAT_SYSTEM} (brace balance unchanged: {before})")


if __name__ == "__main__":
    main()
