"""
Corrective fix for the food/potion feature's final patch: demoWeapons()
and the loadoutStyle local variable both reference CombatStyleOption/
WeaponOption, which no longer exist after LoadoutScreen.kt's full
rewrite (patch 3d-1) dropped them. Leaving them in as "unused dead code"
was wrong -- they still directly reference deleted types, which is a
compile error, not a warning. Removing both. loadoutWeaponId/autoHeal/
autoFlee are left alone -- genuinely unused but harmless, since they
don't reference anything deleted.

Run from repo root: python3 apply_consumables_3d3_fix_demoweapons.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")

OLD_DEMOWEAPONS = '''private fun demoWeapons(style: CombatStyleOption): List<WeaponOption> = when (style) {
    CombatStyleOption.MELEE -> listOf(
        WeaponOption("bronze_sword", "Bronze Sword", CombatStyleOption.MELEE),
        WeaponOption("iron_sword_common", "Iron Sword", CombatStyleOption.MELEE)
    )
    CombatStyleOption.RANGED -> listOf(WeaponOption("shortbow", "Shortbow", CombatStyleOption.RANGED))
    CombatStyleOption.MAGIC -> listOf(WeaponOption("spark_bolt", "Spark Bolt Staff", CombatStyleOption.MAGIC))
}

'''
NEW_DEMOWEAPONS = ""

OLD_LOADOUT_STYLE = "    var loadoutStyle by remember { mutableStateOf(CombatStyleOption.MELEE) }\n"
NEW_LOADOUT_STYLE = ""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 0:
        raise SystemExit(f"ABORT: could not find expected block for '{label}'. No changes written.")
    if count > 1:
        raise SystemExit(f"ABORT: found {count} matches for '{label}', expected exactly 1. No changes written.")
    return text.replace(old, new, 1)


def main() -> None:
    if not TARGET.exists():
        raise SystemExit(f"ABORT: could not find {TARGET} from the current directory. Run this from the repo root.")

    content = TARGET.read_text()

    if "fun demoWeapons" not in content:
        raise SystemExit("ABORT: demoWeapons already gone -- this patch looks already applied. No changes written.")

    content = replace_once(content, OLD_DEMOWEAPONS, NEW_DEMOWEAPONS, "demoWeapons() function")
    content = replace_once(content, OLD_LOADOUT_STYLE, NEW_LOADOUT_STYLE, "loadoutStyle variable")

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
