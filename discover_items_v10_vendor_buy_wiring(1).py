import os

OUT = "discovery_output.txt"
BASE = "app/src/main/kotlin/com/yourname/idlerpg"

def dump_range(out_lines, path, start_line, end_line, label):
    out_lines.append("")
    out_lines.append(f"--- {label}: {path} lines {start_line}-{end_line} ---")
    if not os.path.exists(path):
        out_lines.append(f"!!! NOT FOUND: {path}")
        return
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()
    lo = max(0, start_line - 1)
    hi = min(len(lines), end_line)
    for k in range(lo, hi):
        out_lines.append(f"{k+1}: {lines[k].rstrip()}")

def dump_around_term(out_lines, path, term, before, after, label):
    out_lines.append("")
    out_lines.append(f"--- {label}: {path} around '{term}' ---")
    if not os.path.exists(path):
        out_lines.append(f"!!! NOT FOUND: {path}")
        return
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()
    hits = [i for i, line in enumerate(lines) if term in line]
    if not hits:
        out_lines.append(f"!!! TERM NOT FOUND: {term}")
        return
    for i in hits:
        lo = max(0, i - before)
        hi = min(len(lines), i + after)
        out_lines.append(f"  [match at line {i+1}]")
        for k in range(lo, hi):
            marker = ">>" if k == i else "  "
            out_lines.append(f"    {marker} {k+1}: {lines[k].rstrip()}")

def main():
    out_lines = []
    dump_range(out_lines, f"{BASE}/MarketScreen.kt", 1, 100, "MarketScreen.kt header + top composable + tab dispatch")
    dump_around_term(out_lines, f"{BASE}/MainActivity.kt", "MarketScreen(", 10, 45, "MainActivity.kt call site")
    dump_around_term(out_lines, f"{BASE}/GameViewModel.kt", "vendorSellableItems", 5, 15, "GameViewModel.kt vendorSellableItems source")
    dump_around_term(out_lines, f"{BASE}/ItemsEquipmentSystem.kt", "object RecipeCatalog", 2, 15, "RecipeCatalog object header")
    dump_around_term(out_lines, f"{BASE}/ItemsEquipmentSystem.kt", "fun forOutput", 20, 10, "RecipeCatalog.forOutput + tail of recipes list")

    with open(OUT, "w", encoding="utf-8") as out:
        out.write("\n".join(out_lines))

    print(f"Wrote {OUT} ({len(out_lines)} lines)")

if __name__ == "__main__":
    main()
