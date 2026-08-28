import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
OUT = "discovery_output.txt"

def find_file(name):
    for dirpath, _, files in os.walk(ROOT):
        if name in files:
            return os.path.join(dirpath, name)
    return None

path = find_file("GeneratedItemCatalog.kt")
with open(OUT, "w", encoding="utf-8") as f:
    f.write("GeneratedItemCatalog.kt FULL CONTENTS\n")
    f.write("="*100 + "\n")
    if path is None:
        f.write("!!! FILE NOT FOUND !!!\n")
    else:
        with open(path, "r", encoding="utf-8") as src:
            content = src.read()
        f.write(content)
        f.write(f"\n--- end ({len(content)} chars, {content.count(chr(10))+1} lines) ---\n")
    f.write("\nDONE\n")

print("wrote", OUT)
