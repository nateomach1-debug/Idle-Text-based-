import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
OUT = "discovery_output.txt"

def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

with open(OUT, "w", encoding="utf-8") as f:
    f.write("THEME / COLOR SCHEME DISCOVERY\n")
    found = []
    for dirpath, _, files in os.walk(ROOT):
        for fn in files:
            if "theme" in fn.lower() or "color" in fn.lower():
                found.append(os.path.join(dirpath, fn))
    f.write(f"Theme/color-related files found: {found}\n")
    for p in found:
        f.write(f"\n{'='*100}\nFULL FILE: {p}\n{'='*100}\n")
        try:
            content = read(p)
            f.write(content)
            f.write(f"\n--- end ({len(content)} chars) ---\n")
        except Exception as e:
            f.write(f"!!! error reading: {e} !!!\n")
    f.write("\n\nDONE\n")

print("wrote", OUT)
