import os, re

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
OUT = "discovery_output.txt"

def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def dump_matches(f, path, label, pattern, before=150, after=500):
    f.write(f"\n{'='*100}\n{label} in {path}\n{'='*100}\n")
    content = read(path)
    count = 0
    for m in re.finditer(pattern, content):
        count += 1
        start = max(0, m.start() - before)
        end = min(len(content), m.end() + after)
        f.write(f"\n--- match #{count} at offset {m.start()} ---\n")
        f.write(content[start:end])
        f.write("\n")
    if count == 0:
        f.write("(no matches found)\n")
    f.write(f"\ntotal matches: {count}\n")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("BACK ARROW STYLING DISCOVERY (skill pages)\n")

    # Find every file that references ArrowBack (icon for back navigation)
    candidates = []
    for dirpath, _, files in os.walk(ROOT):
        for fn in files:
            p = os.path.join(dirpath, fn)
            try:
                if "ArrowBack" in read(p):
                    candidates.append(p)
            except Exception:
                pass
    f.write(f"Files referencing ArrowBack: {candidates}\n")

    for c in candidates:
        dump_matches(f, c, f"ArrowBack usage in {c}", r"ArrowBack", before=250, after=350)

    f.write("\n\nDONE\n")

print("wrote", OUT)
