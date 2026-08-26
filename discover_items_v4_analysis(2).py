import os
import re

OUT = "discovery_output.txt"
BASE = "app/src/main/kotlin/com/yourname/idlerpg"

ACTION_CATALOG = f"{BASE}/ActionCatalog.kt"
ITEMS_EQUIPMENT = f"{BASE}/ItemsEquipmentSystem.kt"
COMBAT_SYSTEM = f"{BASE}/CombatSystem.kt"
GENERATED_ITEM_CATALOG = f"{BASE}/GeneratedItemCatalog.kt"


def read(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def extract_action_outputs(text):
    # SkillActionDefinition(SkillType.X, "itemId", "Display", ...)
    pattern = re.compile(r'SkillActionDefinition\(\s*SkillType\.(\w+)\s*,\s*"([a-zA-Z0-9_]+)"')
    result = {}
    for m in pattern.finditer(text):
        skill, item_id = m.group(1), m.group(2)
        result.setdefault(item_id, []).append(f"ActionCatalog:{skill}")
    return result


def extract_recipes(text):
    # Recipe( outputItemId = "x", outputQuantity = N, ingredients = listOf(RecipeIngredient("a",1), ...), skillRequired = "S", levelRequired = N )
    recipes = []
    pattern = re.compile(
        r'Recipe\(\s*'
        r'outputItemId\s*=\s*"([a-zA-Z0-9_]+)"\s*,\s*'
        r'outputQuantity\s*=\s*(\d+)\s*,\s*'
        r'ingredients\s*=\s*(.*?)\s*,\s*'
        r'skillRequired\s*=\s*"([A-Z_]+)"\s*,\s*'
        r'levelRequired\s*=\s*(\d+)',
        re.DOTALL
    )
    ingredient_pattern = re.compile(r'RecipeIngredient\(\s*"([a-zA-Z0-9_]+)"\s*,\s*(\d+)\s*\)')
    for m in pattern.finditer(text):
        output_id, output_qty, ingredients_blob, skill, level = m.groups()
        ingredients = ingredient_pattern.findall(ingredients_blob)
        recipes.append({
            "output": output_id,
            "qty": output_qty,
            "ingredients": [(iid, qty) for iid, qty in ingredients],
            "skill": skill,
            "level": level,
        })
    return recipes


def extract_all_recipe_ingredients(recipes):
    all_ids = set()
    for r in recipes:
        for iid, qty in r["ingredients"]:
            all_ids.add(iid)
    return all_ids


def extract_loot_ids(text):
    pattern = re.compile(r'LootEntry\(\s*"([a-zA-Z0-9_]+)"')
    ids = {}
    for m in pattern.finditer(text):
        ids.setdefault(m.group(1), []).append("CombatSystem:LootEntry")
    return ids


def extract_item_catalog_ids(text):
    # ItemDefinition( id = "x", ...
    pattern = re.compile(r'ItemDefinition\(\s*id\s*=\s*"([a-zA-Z0-9_]+)"')
    return set(pattern.findall(text))


def main():
    out_lines = []

    action_text = read(ACTION_CATALOG) or ""
    items_text = read(ITEMS_EQUIPMENT) or ""
    combat_text = read(COMBAT_SYSTEM) or ""
    catalog_text = read(GENERATED_ITEM_CATALOG) or ""

    action_outputs = extract_action_outputs(action_text)
    recipes = extract_recipes(items_text)
    loot_ids = extract_loot_ids(combat_text)
    catalog_ids = extract_item_catalog_ids(catalog_text)

    recipe_by_output = {}
    for r in recipes:
        recipe_by_output.setdefault(r["output"], []).append(r)

    all_ingredient_ids = extract_all_recipe_ingredients(recipes)

    out_lines.append(f"Total Recipe( ... ) blocks parsed: {len(recipes)}")
    out_lines.append(f"Total unique recipe output ids: {len(recipe_by_output)}")
    out_lines.append(f"Total unique action-produced item ids: {len(action_outputs)}")
    out_lines.append(f"Total unique combat loot item ids: {len(loot_ids)}")
    out_lines.append(f"Total unique ids in GeneratedItemCatalog ItemDefinitions: {len(catalog_ids)}")
    out_lines.append(f"Total unique recipe ingredient ids to classify: {len(all_ingredient_ids)}")
    out_lines.append("")

    # Reachability closure: an item is obtainable if it's an action output,
    # a combat loot id, OR a recipe output whose ingredients are ALL obtainable
    # (recursively). No vendor-buy or starting-inventory sources exist (confirmed
    # by prior discovery passes returning zero matches).
    obtainable = {}  # item_id -> list of reasons/paths

    for iid, sources in action_outputs.items():
        obtainable[iid] = list(sources)
    for iid, sources in loot_ids.items():
        obtainable.setdefault(iid, []).extend(sources)

    changed = True
    iterations = 0
    while changed and iterations < 50:
        changed = False
        iterations += 1
        for output_id, recipe_list in recipe_by_output.items():
            if output_id in obtainable:
                continue
            for r in recipe_list:
                ing_ids = [iid for iid, qty in r["ingredients"]]
                if ing_ids and all(iid in obtainable for iid in ing_ids):
                    obtainable[output_id] = [f"Recipe(from {', '.join(ing_ids)})"]
                    changed = True
                    break

    out_lines.append("=== CLASSIFICATION OF EVERY RECIPE-INGREDIENT ITEM ===")
    out_lines.append("(OBTAINABLE = reachable via gathering action, combat loot, or a chain of recipes bottoming out in those)")
    out_lines.append("")

    unobtainable = []
    for iid in sorted(all_ingredient_ids):
        if iid in obtainable:
            out_lines.append(f"OK   {iid}  <-  {'; '.join(obtainable[iid])}")
        else:
            unobtainable.append(iid)
            in_catalog = "yes" if iid in catalog_ids else "NO ITEMDEFINITION FOUND"
            has_recipe = iid in recipe_by_output
            recipe_note = ""
            if has_recipe:
                unresolved = []
                for r in recipe_by_output[iid]:
                    missing = [i2 for i2, q2 in r["ingredients"] if i2 not in obtainable]
                    unresolved.append(f"needs {missing}")
                recipe_note = f" (has Recipe but blocked on: {'; '.join(unresolved)})"
            else:
                recipe_note = " (no Recipe produces this id at all, and no gathering action or combat drop produces it)"
            out_lines.append(f"GAP  {iid}  [catalog def: {in_catalog}]{recipe_note}")

    out_lines.append("")
    out_lines.append(f"=== SUMMARY: {len(unobtainable)} unobtainable ingredient item(s) ===")
    for iid in unobtainable:
        out_lines.append(f"  - {iid}")

    out_lines.append("")
    out_lines.append("=== POTENTIAL ID MISMATCHES (recipe outputs whose name doesn't match anything ever used as an ingredient elsewhere, or vice versa - possible typos) ===")
    ingredient_like_names = all_ingredient_ids
    for output_id in recipe_by_output:
        # Flag outputs that look like they were MEANT to satisfy an ingredient
        # elsewhere but don't match any ingredient id exactly, if a very similar
        # id does exist in the ingredient set.
        if output_id in ingredient_like_names:
            continue
        close_matches = [i for i in ingredient_like_names if i != output_id and (i in output_id or output_id in i)]
        if close_matches:
            out_lines.append(f"  Recipe output '{output_id}' is never used as an ingredient anywhere, but similar id(s) ARE used as ingredients: {close_matches}")

    out_lines.append("")
    out_lines.append("=== ALL RECIPE OUTPUT IDS THAT ARE THEMSELVES NEVER REQUIRED AS AN INGREDIENT BY ANY OTHER RECIPE (for reference; expected for most final equipment/consumables) ===")
    terminal_outputs = sorted(o for o in recipe_by_output if o not in ingredient_like_names)
    out_lines.append(f"  ({len(terminal_outputs)} such outputs, listing first 30) " + ", ".join(terminal_outputs[:30]))

    with open(OUT, "w", encoding="utf-8") as out:
        out.write("\n".join(out_lines))

    print(f"Wrote {OUT} ({len(out_lines)} lines). Unobtainable count: {len(unobtainable)}")


if __name__ == "__main__":
    main()
