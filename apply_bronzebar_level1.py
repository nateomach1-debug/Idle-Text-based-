#!/usr/bin/env python3
"""
Lowers the bronze_bar recipe's levelRequired from 5 to 1, so level-1
players have a Smithing option beyond copper_bar/tin_bar (which are
already level 1) right from the start.

Run from repo root:
    python3 apply_bronzebar_level1.py
Then rebuild:
    ./gradlew assembleDebug --console=plain --no-daemon --no-configuration-cache
"""
import sys
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/ItemsEquipmentSystem.kt")


def fail(msg):
    print(f"FAILED: {msg}")
    sys.exit(1)


def main():
    if not TARGET.exists():
        fail(f"{TARGET} not found -- run this from the repo root")

    text = TARGET.read_text()

    old = (
        'Recipe(\n'
        '            outputItemId = "bronze_bar",\n'
        '            outputQuantity = 1,\n'
        '            ingredients = listOf(RecipeIngredient("copper_ore", 1), RecipeIngredient("tin_ore", 1)),\n'
        '            skillRequired = "SMITHING",\n'
        '            levelRequired = 5\n'
        '        ),\n'
    )
    new = (
        'Recipe(\n'
        '            outputItemId = "bronze_bar",\n'
        '            outputQuantity = 1,\n'
        '            ingredients = listOf(RecipeIngredient("copper_ore", 1), RecipeIngredient("tin_ore", 1)),\n'
        '            skillRequired = "SMITHING",\n'
        '            levelRequired = 1\n'
        '        ),\n'
    )

    count = text.count(old)
    if count != 1:
        fail(f"expected exactly 1 occurrence of the bronze_bar recipe block, found {count}")

    if new in text and old not in text:
        fail("bronze_bar recipe already at levelRequired = 1 -- patch may already be applied")

    text = text.replace(old, new, 1)
    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")
    print("Run: git diff", TARGET, "to verify before rebuilding.")


if __name__ == "__main__":
    main()
