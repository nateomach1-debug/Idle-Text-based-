import os

OUT = "discovery_output.txt"
REPO_ROOT = "."

TERMS = [
    "enum class MarketTab",
    "VendorItemRow",
    "InventoryItemSummary",
    "data class InventoryItemSummary",
    "val inventoryItems",
]

FULL_FUNCTION_DUMPS = [
    # (file, start_marker) -> we'll dump from start_marker line to +40 lines
    ("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt", "fun sellItemToVendor"),
    ("app/src/main/kotlin/com/yourname/idlerpg/MarketScreen.kt", "private fun SellToVendorTab"),
]

CODE_EXTENSIONS = (".kt",)
CONTEXT = 6

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

    out_lines.append("=== FULL FUNCTION/BLOCK DUMPS (generous margin: +50 lines from marker) ===")
    for path, marker in FULL_FUNCTION_DUMPS:
        out_lines.append("")
        out_lines.append(f"--- {path} :: from '{marker}' ---")
        if not os.path.exists(path):
            out_lines.append(f"!!! NOT FOUND: {path}")
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
        start = None
        for i, line in enumerate(lines):
            if marker in line:
                start = i
                break
        if start is None:
            out_lines.append(f"!!! MARKER NOT FOUND: {marker}")
            continue
        end = min(len(lines), start + 50)
        for k in range(start, end):
            out_lines.append(f"{k+1}: {lines[k].rstrip()}")

    out_lines.append("")
    out_lines.append("=== TERM SEARCH (whole repo, +/-6 lines context) ===")
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
                        marker2 = ">>" if k == i else "  "
                        out_lines.append(f"    {marker2} {k+1}: {lines[k].rstrip()}")

    with open(OUT, "w", encoding="utf-8") as out:
        out.write("\n".join(out_lines))

    print(f"Wrote {OUT} ({len(out_lines)} lines)")

if __name__ == "__main__":
    main()
