import os
import re

REPO_ROOT = "."
OUT = "discovery_output.txt"

# Keywords covering every place an item could plausibly be defined,
# obtained, or consumed. Broad on purpose for a first pass.
KEYWORD_GROUPS = {
    "RECIPE / CRAFTING / COOKING": [
        r"\bRecipe\b", r"\bRecipes\b", r"\bCrafting\b", r"\bCookingSystem\b",
        r"\bingredient", r"\bIngredient",
    ],
    "DROP TABLE / LOOT": [
        r"\bDropTable\b", r"\bLootTable\b", r"\bloot\b", r"\bDrop\b",
        r"\bLootEntry\b",
    ],
    "GATHERING": [
        r"\bGathering\b", r"\bGather\b", r"\bMining\b", r"\bWoodcutting\b",
        r"\bFishing\b", r"\bForaging\b", r"\bharvest",
    ],
    "VENDOR / SHOP": [
        r"\bVendor\b", r"\bShop\b", r"\bStore\b",
    ],
    "STARTING INVENTORY": [
        r"\bstartingInventory\b", r"\bStartingInventory\b", r"\binitialInventory\b",
        r"\bdefaultInventory\b",
    ],
    "ITEM CATALOG": [
        r"\bItemCatalog\b", r"\bGeneratedItemCatalog\b", r"\bItemDefinition\b",
        r"\bItemId\b", r"\bItem\(",
    ],
}

CODE_EXTENSIONS = (".kt", ".sql")

def walk_files():
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        if ".git" in dirpath.split(os.sep):
            continue
        for fn in filenames:
            if fn.endswith(CODE_EXTENSIONS):
                yield os.path.join(dirpath, fn)

def main():
    lines_out = []
    lines_out.append("=== FULL REPO FILE LISTING (.kt / .sql) ===")
    all_files = sorted(walk_files())
    for f in all_files:
        try:
            size = os.path.getsize(f)
        except OSError:
            size = -1
        lines_out.append(f"{f}  ({size} bytes)")

    lines_out.append("")
    lines_out.append("=== KEYWORD MATCHES (file : line_no : line) ===")

    compiled = {
        group: [re.compile(p) for p in pats]
        for group, pats in KEYWORD_GROUPS.items()
    }

    for group, patterns in compiled.items():
        lines_out.append("")
        lines_out.append(f"--- {group} ---")
        for f in all_files:
            try:
                with open(f, "r", encoding="utf-8", errors="replace") as fh:
                    file_lines = fh.readlines()
            except OSError:
                continue
            matched_any = False
            for i, line in enumerate(file_lines, start=1):
                if any(p.search(line) for p in patterns):
                    if not matched_any:
                        lines_out.append(f"  [{f}]")
                        matched_any = True
                    lines_out.append(f"    {i}: {line.rstrip()}")

    with open(OUT, "w", encoding="utf-8") as out:
        out.write("\n".join(lines_out))

    print(f"Wrote {OUT} ({len(lines_out)} lines)")

if __name__ == "__main__":
    main()
