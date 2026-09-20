#!/usr/bin/env python3
"""
patch_M1_more_monsters.py

ADDS 18 new monsters to the 6 existing zones in CombatSystem.kt (ZoneCatalog).
Purely additive: every existing monster block (goblin_grunt, wraith, wild_cow,
feral_chicken, marsh_snake, gem_hoarder, green_dragon, blue_dragon) is left
byte-for-byte untouched; new Monster(...) entries are appended after the last
existing monster in each zone's monsters = listOf(...).

No new zones. Loot tables only use item ids that existing monsters already drop.
Run from the repo root. Safe to re-run (idempotent). All-or-nothing: if any
anchor is missing/ambiguous nothing is written and the script exits 1.
"""
import os
import sys

SRC = "app/src/main/kotlin/com/yourname/idlerpg"
CS = os.path.join(SRC, "CombatSystem.kt")


def monster(mid, name, lvl, hp, dfn, weak, main, rare):
    def loot(entries):
        if not entries:
            return "listOf()"
        lines = ",\n".join(
            '                        LootEntry("%s", %d, %d, %s)' % (i, a, b, c)
            for (i, a, b, c) in entries
        )
        return "listOf(\n" + lines + "\n                    )"

    return (
        "                Monster(\n"
        '                    id = "%s",\n'
        '                    name = "%s",\n'
        "                    levelRequirement = %d,\n"
        "                    maxHealth = %d,\n"
        "                    defenseRating = %d,\n"
        "                    weakness = DamageType.%s,\n"
        "                    mainLootTable = %s,\n"
        "                    rareLootTable = %s\n"
        "                )"
    ) % (mid, name, lvl, hp, dfn, weak, loot(main), loot(rare))


# (zone_id_after, last-lines-of-last-existing-monster, [new monsters])
NEW = {
    "goblin_camp": [
        monster("goblin_scout", "Goblin Scout", 1, 20, 3, "WIND",
                [("goblin_ear", 1, 1, "35.0")], [("rusty_dagger", 1, 1, "1.5")]),
        monster("goblin_shaman", "Goblin Shaman", 4, 32, 7, "EARTH",
                [("goblin_ear", 1, 2, "45.0")], [("rusty_dagger", 1, 1, "2.5")]),
        monster("goblin_brute", "Goblin Brute", 7, 50, 12, "WATER",
                [("goblin_ear", 2, 3, "50.0")], [("rusty_dagger", 1, 1, "4.0")]),
    ],
    "farmland_outskirts": [
        monster("crop_crow", "Crop Crow", 2, 14, 2, "EARTH",
                [("feathers", 1, 3, "70.0"), ("raw_chicken", 1, 1, "35.0")], []),
        monster("angry_goat", "Angry Goat", 4, 30, 6, "WIND",
                [("cowhide", 1, 1, "55.0"), ("raw_beef", 1, 2, "55.0")], []),
        monster("haunted_scarecrow", "Haunted Scarecrow", 6, 42, 9, "FIRE",
                [("feathers", 2, 4, "60.0"), ("cowhide", 1, 1, "30.0")], []),
    ],
    "serpent_marsh": [
        monster("bog_toad", "Bog Toad", 10, 30, 8, "FIRE",
                [("snake_hide", 1, 1, "35.0")], []),
        monster("swamp_leech", "Swamp Leech", 12, 40, 12, "MELEE",
                [("snake_hide", 1, 1, "45.0")], []),
        monster("bog_lurker", "Bog Lurker", 14, 55, 16, "RANGED",
                [("snake_hide", 1, 2, "60.0")], [("uncut_gemstone", 1, 1, "2.0")]),
    ],
    "gem_cavern": [
        monster("cave_bat", "Cave Bat", 15, 32, 12, "WIND",
                [("uncut_gemstone", 1, 1, "25.0")], []),
        monster("gemstone_spider", "Gemstone Spider", 17, 52, 18, "FIRE",
                [("uncut_gemstone", 1, 1, "40.0")],
                [("uncut_opal", 1, 1, "5.0"), ("uncut_jade", 1, 1, "3.5"),
                 ("uncut_red_topaz", 1, 1, "2.5"), ("uncut_sapphire", 1, 1, "1.5")]),
        monster("crystal_golem", "Crystal Golem", 19, 70, 22, "MELEE",
                [("uncut_gemstone", 1, 3, "60.0")],
                [("uncut_sapphire", 1, 1, "3.0"), ("uncut_emerald", 1, 1, "2.0"),
                 ("uncut_ruby", 1, 1, "1.2"), ("uncut_diamond", 1, 1, "0.6")]),
    ],
    "shadow_ruins": [
        monster("restless_skeleton", "Restless Skeleton", 20, 70, 22, "MELEE",
                [("ectoplasm", 1, 1, "30.0")],
                [("rusty_dagger", 1, 1, "6.0"), ("wraith_essence", 1, 1, "0.2")]),
        monster("shadow_stalker", "Shadow Stalker", 26, 100, 31, "RANGED",
                [("ectoplasm", 1, 3, "60.0")], [("wraith_essence", 1, 1, "0.8")]),
        monster("ruin_banshee", "Ruin Banshee", 33, 130, 40, "EARTH",
                [("ectoplasm", 2, 4, "65.0")], [("wraith_essence", 1, 1, "1.2")]),
    ],
    "dragons_lair": [
        monster("dragon_whelp", "Dragon Whelp", 60, 160, 50, "RANGED",
                [("green_dragonhide", 1, 1, "30.0")], [("uncut_dragonstone", 1, 1, "0.4")]),
        monster("red_dragon", "Red Dragon", 70, 300, 85, "WATER",
                [("blue_dragonhide", 1, 1, "45.0")], [("uncut_dragonstone", 1, 1, "1.0")]),
        monster("black_dragon", "Black Dragon", 75, 340, 95, "EARTH",
                [("blue_dragonhide", 1, 1, "60.0")], [("uncut_dragonstone", 1, 1, "1.5")]),
    ],
}

L16 = "                )"
L12 = "            )"
L8 = "        ),"

# For each zone: the tail of the LAST EXISTING monster + what follows it. The
# new monsters are inserted between the last monster's closing paren and the
# closing paren of the zone's monsters = listOf(...).
EDITS = []


def add(zone_id, prefix, follower, closing_zone):
    old = prefix + "\n" + L16 + "\n" + L12 + "\n" + closing_zone + follower
    new = (prefix + "\n" + L16 + ",\n" + ",\n".join(NEW[zone_id]) + "\n"
           + L12 + "\n" + closing_zone + follower)
    EDITS.append((zone_id, old, new))


add("goblin_camp",
    '                        LootEntry("rusty_dagger", 1, 1, 2.0)\n                    )',
    '\n        Zone(\n            id = "shadow_ruins",', L8)
add("shadow_ruins",
    '                        LootEntry("wraith_essence", 1, 1, 0.5)\n                    )',
    '\n        Zone(\n            id = "farmland_outskirts",', L8)
add("farmland_outskirts",
    '                        LootEntry("feathers", 1, 5, 70.0)\n                    ),\n'
    '                    rareLootTable = listOf()',
    '\n        Zone(\n            id = "serpent_marsh",', L8)
add("serpent_marsh",
    '                        LootEntry("snake_hide", 1, 1, 55.0)\n                    ),\n'
    '                    rareLootTable = listOf()',
    '\n        Zone(\n            id = "gem_cavern",', L8)
add("gem_cavern",
    '                        LootEntry("uncut_celestial_crystal", 1, 1, 0.05)\n                    )',
    '\n        Zone(\n            id = "dragons_lair",', L8)
add("dragons_lair",
    '                        LootEntry("blue_dragonhide", 1, 1, 55.0)\n                    ),\n'
    '                    rareLootTable = listOf()',
    "\n    )", "        )")


def main():
    if not os.path.exists(CS):
        print("FAIL: %s not found (run from repo root)" % CS)
        sys.exit(1)
    with open(CS, encoding="utf-8", newline="") as f:
        content = f.read()

    plan, failed = [], False
    for zone_id, old, new in EDITS:
        if new in content:
            print("SKIP  %-20s already applied" % zone_id)
            continue
        n = content.count(old)
        if n == 1:
            plan.append((zone_id, old, new))
        else:
            failed = True
            print("FAIL  %-20s anchor matched %d times (expected 1)" % (zone_id, n))
    if failed:
        print("Aborting - nothing written.")
        sys.exit(1)

    for zone_id, old, new in plan:
        content = content.replace(old, new, 1)
        print("OK    %-20s +%d monsters" % (zone_id, len(NEW[zone_id])))

    if plan:
        with open(CS, "w", encoding="utf-8", newline="") as f:
            f.write(content)
    print("Done. %d zone(s) patched, %d already applied." % (len(plan), len(EDITS) - len(plan)))


if __name__ == "__main__":
    main()
