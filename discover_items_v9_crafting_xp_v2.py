import os

OUT = "discovery_output.txt"
FILE = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"

TERMS = [
    "CraftingQueue",
    "craftingQueue",
    "fun startCrafting",
    "fun tickCrafting",
    "Recipe.levelRequired",
    "recipe.levelRequired",
    "RecipeCatalog",
    "outputItemId",
    "xpAward",
    "craftingXp",
    "fun craftingXpFor",
]

def main():
    out_lines = []
    if not os.path.exists(FILE):
        out_lines.append(f"!!! NOT FOUND: {FILE}")
        with open(OUT, "w", encoding="utf-8") as out:
            out.write("\n".join(out_lines))
        print("wrote not-found")
        return

    with open(FILE, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()

    out_lines.append(f"Total lines in {FILE}: {len(lines)}")
    out_lines.append("")
    out_lines.append("=== TERM SEARCH (+/- 3 lines context) ===")
    for term in TERMS:
        out_lines.append("")
        out_lines.append(f"--- TERM: {term} ---")
        found_any = False
        for i, line in enumerate(lines):
            if term in line:
                found_any = True
                out_lines.append(f"  [line {i+1}]")
                lo = max(0, i - 3)
                hi = min(len(lines), i + 4)
                for k in range(lo, hi):
                    marker = ">>" if k == i else "  "
                    out_lines.append(f"    {marker} {k+1}: {lines[k].rstrip()}")
        if not found_any:
            out_lines.append("  (no matches)")

    with open(OUT, "w", encoding="utf-8") as out:
        out.write("\n".join(out_lines))

    print(f"Wrote {OUT} ({len(out_lines)} lines)")

if __name__ == "__main__":
    main()
