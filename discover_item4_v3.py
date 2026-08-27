import os

OUT = "discovery_output.txt"
REPO_ROOT = "."

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
    search_term(out_lines, "activeQueueInfo")
    search_term(out_lines, "HomeScreen(")
    search_term(out_lines, "import com.yourname.idlerpg.data.ActiveQueueInfo")

    with open(OUT, "w", encoding="utf-8") as out:
        out.write("\n".join(out_lines))

    print(f"Wrote {OUT} ({len(out_lines)} lines)")

if __name__ == "__main__":
    main()
