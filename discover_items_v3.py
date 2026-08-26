import os

OUT = "discovery_output.txt"
REPO_ROOT = "."

TERMS = [
    "bowstring",
    "vial_of_water",
    "cowhide",
    "snake_hide",
    "dragonhide",
    "gemstone",
    "outputItemId",
    "output_item_id",
    "fun craftItem",
    "fun startCrafting",
    "fun completeCrafting",
    "CraftingQueue",
    "SkillType.SMITHING",
    "fun grantGatheredItem",
    "fun completeSkillingAction",
    "startingInventory",
    "seedVault",
    "onCharacterCreated",
    "fun createCharacter",
]

CODE_EXTENSIONS = (".kt", ".sql")
CONTEXT = 3

def walk_files():
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        if ".git" in dirpath.split(os.sep):
            continue
        for fn in filenames:
            if fn.endswith(CODE_EXTENSIONS):
                yield os.path.join(dirpath, fn)

def main():
    all_files = sorted(walk_files())
    out_lines = []

    out_lines.append("=== FULL Recipe class definition block (ItemsEquipmentSystem.kt lines 1-40) ===")
    target = "app/src/main/kotlin/com/yourname/idlerpg/ItemsEquipmentSystem.kt"
    if os.path.exists(target):
        with open(target, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
        for i, line in enumerate(lines[:40], start=1):
            out_lines.append(f"{i}: {line.rstrip()}")
    else:
        out_lines.append(f"!!! NOT FOUND: {target}")

    out_lines.append("")
    out_lines.append("=== First 3 full Recipe( ... ) blocks (to see all fields per recipe) ===")
    if os.path.exists(target):
        with open(target, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
        count = 0
        i = 0
        while i < len(lines) and count < 3:
            if lines[i].strip().startswith("Recipe("):
                start = i
                depth = 0
                j = i
                started = False
                while j < len(lines):
                    depth += lines[j].count("(") - lines[j].count(")")
                    if "(" in lines[j]:
                        started = True
                    if started and depth <= 0:
                        break
                    j += 1
                for k in range(start, min(j + 1, len(lines))):
                    out_lines.append(f"{k+1}: {lines[k].rstrip()}")
                out_lines.append("---")
                count += 1
                i = j + 1
            else:
                i += 1

    out_lines.append("")
    out_lines.append("=== TERM SEARCH (whole repo, +/-3 lines context) ===")
    for term in TERMS:
        out_lines.append("")
        out_lines.append(f"--- TERM: {term} ---")
        for f in all_files:
            try:
                with open(f, "r", encoding="utf-8", errors="replace") as fh:
                    lines = fh.readlines()
            except OSError:
                continue
            for i, line in enumerate(lines):
                if term in line:
                    out_lines.append(f"  [{f}:{i+1}]")
                    lo = max(0, i - CONTEXT)
                    hi = min(len(lines), i + CONTEXT + 1)
                    for k in range(lo, hi):
                        marker = ">>" if k == i else "  "
                        out_lines.append(f"    {marker} {k+1}: {lines[k].rstrip()}")

    with open(OUT, "w", encoding="utf-8") as out:
        out.write("\n".join(out_lines))

    print(f"Wrote {OUT} ({len(out_lines)} lines)")

if __name__ == "__main__":
    main()
