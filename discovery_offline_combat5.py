import re, os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
OUT = "discovery_output5.txt"

def grep_repo(pattern, label, context=60):
    out = [f"\n=== REPO-WIDE: {label} ==="]
    found = False
    for dirpath, _, files in os.walk(ROOT):
        for fname in files:
            if not fname.endswith(".kt"):
                continue
            path = os.path.join(dirpath, fname)
            text = open(path, encoding="utf-8").read()
            for m in re.finditer(pattern, text):
                found = True
                start = max(0, m.start() - 100)
                end = min(len(text), m.end() + context * 20)
                out.append(f"-- {path} --")
                out.append(text[start:end])
                out.append("--- match end ---\n")
    if not found:
        out.append("NO MATCHES FOUND ANYWHERE IN REPO\n")
    return "\n".join(out)

sections = []
sections.append(grep_repo(r"data class SavedGameState", "full SavedGameState data class", context=40))
sections.append(grep_repo(r"return SavedGameState\(", "return SavedGameState(...) call in load()", context=40))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(sections))

print(f"Wrote {OUT}")