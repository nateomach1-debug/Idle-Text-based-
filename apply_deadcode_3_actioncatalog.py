"""
Cleanup (3/3): removes 32 dead ActionCatalog Smithing entries (12 bars +
20 gear pieces) -- confirmed unreachable, since Smithing runs entirely
through RecipeCatalog/SmithingScreen now. Confirmed no other screen reads
ActionCatalog for Smithing (MainActivity's one SkillType.SMITHING
reference outside RecipeCatalog is for the unlock-table lookup in
buildSmithingState(), unrelated to these entries).

Run from repo root: python3 apply_deadcode_3_actioncatalog.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/ActionCatalog.kt")

DEAD_BLOCK = '''        SkillActionDefinition(SkillType.SMITHING, "copper_bar", "Smelt Copper Bar", xpPerAction = 10, secondsPerAction = 3, levelRequired = 1),
        SkillActionDefinition(SkillType.SMITHING, "tin_bar", "Smelt Tin Bar", xpPerAction = 10, secondsPerAction = 3, levelRequired = 1),
        SkillActionDefinition(SkillType.SMITHING, "bronze_bar", "Smelt Bronze Bar", xpPerAction = 19, secondsPerAction = 3, levelRequired = 5),
        SkillActionDefinition(SkillType.SMITHING, "iron_bar", "Smelt Iron Bar", xpPerAction = 41, secondsPerAction = 3, levelRequired = 15),
        SkillActionDefinition(SkillType.SMITHING, "silver_bar", "Smelt Silver Bar", xpPerAction = 74, secondsPerAction = 4, levelRequired = 30),
        SkillActionDefinition(SkillType.SMITHING, "steel_bar", "Smelt Steel Bar", xpPerAction = 85, secondsPerAction = 4, levelRequired = 35),
        SkillActionDefinition(SkillType.SMITHING, "gold_bar", "Smelt Gold Bar", xpPerAction = 96, secondsPerAction = 4, levelRequired = 40),
        SkillActionDefinition(SkillType.SMITHING, "mithril_bar", "Smelt Mithril Bar", xpPerAction = 118, secondsPerAction = 5, levelRequired = 50),
        SkillActionDefinition(SkillType.SMITHING, "adamantite_bar", "Smelt Adamantite Bar", xpPerAction = 140, secondsPerAction = 5, levelRequired = 60),
        SkillActionDefinition(SkillType.SMITHING, "runite_bar", "Smelt Runite Bar", xpPerAction = 162, secondsPerAction = 5, levelRequired = 70),
        SkillActionDefinition(SkillType.SMITHING, "orichalcum_bar", "Smelt Orichalcum Bar", xpPerAction = 184, secondsPerAction = 6, levelRequired = 80),
        SkillActionDefinition(SkillType.SMITHING, "celestial_alloy_bar", "Smelt Celestial Alloy Bar", xpPerAction = 206, secondsPerAction = 6, levelRequired = 90),
        SkillActionDefinition(SkillType.SMITHING, "dagger", "Forge Dagger", xpPerAction = 10, secondsPerAction = 3, levelRequired = 1),
        SkillActionDefinition(SkillType.SMITHING, "nails", "Forge Nails", xpPerAction = 10, secondsPerAction = 3, levelRequired = 1),
        SkillActionDefinition(SkillType.SMITHING, "sword", "Forge Sword", xpPerAction = 19, secondsPerAction = 3, levelRequired = 5),
        SkillActionDefinition(SkillType.SMITHING, "mace", "Forge Mace", xpPerAction = 30, secondsPerAction = 3, levelRequired = 10),
        SkillActionDefinition(SkillType.SMITHING, "warhammer", "Forge Warhammer", xpPerAction = 41, secondsPerAction = 3, levelRequired = 15),
        SkillActionDefinition(SkillType.SMITHING, "chainmail_body", "Forge Chainmail Body", xpPerAction = 52, secondsPerAction = 3, levelRequired = 20),
        SkillActionDefinition(SkillType.SMITHING, "full_helm", "Forge Full Helm", xpPerAction = 63, secondsPerAction = 4, levelRequired = 25),
        SkillActionDefinition(SkillType.SMITHING, "platelegs", "Forge Platelegs", xpPerAction = 74, secondsPerAction = 4, levelRequired = 30),
        SkillActionDefinition(SkillType.SMITHING, "platebody", "Forge Platebody", xpPerAction = 85, secondsPerAction = 4, levelRequired = 35),
        SkillActionDefinition(SkillType.SMITHING, "kiteshield", "Forge Kiteshield", xpPerAction = 96, secondsPerAction = 4, levelRequired = 40),
        SkillActionDefinition(SkillType.SMITHING, "battleaxe", "Forge Battleaxe", xpPerAction = 107, secondsPerAction = 4, levelRequired = 45),
        SkillActionDefinition(SkillType.SMITHING, "two_handed_sword", "Forge Two-Handed Sword", xpPerAction = 118, secondsPerAction = 5, levelRequired = 50),
        SkillActionDefinition(SkillType.SMITHING, "arrowheads", "Forge Arrowheads", xpPerAction = 129, secondsPerAction = 5, levelRequired = 55),
        SkillActionDefinition(SkillType.SMITHING, "throwing_knives", "Forge Throwing Knives", xpPerAction = 140, secondsPerAction = 5, levelRequired = 60),
        SkillActionDefinition(SkillType.SMITHING, "full_plate_armor_set", "Forge Full Plate Armor Set", xpPerAction = 151, secondsPerAction = 5, levelRequired = 65),
        SkillActionDefinition(SkillType.SMITHING, "claws", "Forge Claws", xpPerAction = 162, secondsPerAction = 5, levelRequired = 70),
        SkillActionDefinition(SkillType.SMITHING, "halberd", "Forge Halberd", xpPerAction = 173, secondsPerAction = 6, levelRequired = 75),
        SkillActionDefinition(SkillType.SMITHING, "ceremonial_armor", "Forge Ceremonial Armor", xpPerAction = 184, secondsPerAction = 6, levelRequired = 80),
        SkillActionDefinition(SkillType.SMITHING, "masterwork_weapon", "Forge Masterwork Weapon", xpPerAction = 195, secondsPerAction = 6, levelRequired = 85),
        SkillActionDefinition(SkillType.SMITHING, "legendary_blade", "Forge Legendary Blade", xpPerAction = 206, secondsPerAction = 6, levelRequired = 90),
'''


def main() -> None:
    if not TARGET.exists():
        raise SystemExit(f"ABORT: could not find {TARGET} from the current directory. Run this from the repo root.")

    content = TARGET.read_text()

    count = content.count(DEAD_BLOCK)
    if count == 0:
        raise SystemExit(
            "ABORT: could not find the dead Smithing block -- looks like this patch "
            "was already applied, or the file has changed. No changes written."
        )
    if count > 1:
        raise SystemExit(f"ABORT: found {count} matches, expected exactly 1. No changes written.")

    content = content.replace(DEAD_BLOCK, "", 1)

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
