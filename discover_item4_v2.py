import os

OUT = "discovery_output.txt"
REPO_ROOT = "."

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

def walk_files():
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        if ".git" in dirpath.split(os.sep):
            continue
        for fn in filenames:
            if fn.endswith(".kt"):
                yield os.path.join(dirpath, fn)

def search_term(out_lines, term, context=5):
    out_lines.append("")
    out_lines.append(f"--- TERM: {term} ---")
    found = False
    for f in sorted(walk_files()):
        try:
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
        except OSError:
            continue
        for i, line in enumerate(lines):
            if term in line:
                found = True
                out_lines.append(f"  [{f}:{i+1}]")
                lo = max(0, i - context)
                hi = min(len(lines), i + context + 1)
                for k in range(lo, hi):
                    marker = ">>" if k == i else "  "
                    out_lines.append(f"    {marker} {k+1}: {lines[k].rstrip()}")
    if not found:
        out_lines.append("  (no matches)")

def main():
    out_lines = []

    dump_range(out_lines, "app/src/main/kotlin/com/yourname/idlerpg/HomeScreen.kt", 1, 45, "HomeScreen.kt header/package + HomeScreenState")
    dump_range(out_lines, "app/src/main/kotlin/com/yourname/idlerpg/HomeScreen.kt", 130, 200, "HomeScreen.kt QueueCard + CycleCountdown full bodies")

    search_term(out_lines, "SkillDetailState")
    search_term(out_lines, "SkillDetailScreen")
    search_term(out_lines, "fun placeSellOrder")
    search_term(out_lines, "onPlaceOrder")

    with open(OUT, "w", encoding="utf-8") as out:
        out.write("\n".join(out_lines))

    print(f"Wrote {OUT} ({len(out_lines)} lines)")

if __name__ == "__main__":
    main()
