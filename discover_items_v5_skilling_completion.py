import os

OUT = "discovery_output.txt"
REPO_ROOT = "."

TERMS = [
    "SkillingQueue",
    "skillingQueue",
    "ActionCatalog.find",
    "inventoryService.add",
    "InventoryService",
    "fun addItem",
    "fun grantItem",
    "fun resolveSkillingCompletion",
    "fun processSkillingQueue",
    "fun tickSkilling",
]

CODE_EXTENSIONS = (".kt",)
CONTEXT = 4

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

    out_lines.append("=== FILE LISTING (.kt) with sizes ===")
    for f in all_files:
        try:
            size = os.path.getsize(f)
        except OSError:
            size = -1
        out_lines.append(f"{f}  ({size} bytes)")

    out_lines.append("")
    out_lines.append("=== TERM SEARCH (whole repo, +/-4 lines context) ===")
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
