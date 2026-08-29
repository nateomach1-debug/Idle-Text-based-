import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
OUT = "discovery_output.txt"

with open(OUT, "w", encoding="utf-8") as f:
    f.write("REPO-WIDE SEARCH FOR match_market_orders\n")
    found_any = False
    for dirpath, _, files in os.walk(ROOT):
        for fn in files:
            if fn.endswith(".kt"):
                p = os.path.join(dirpath, fn)
                try:
                    with open(p, "r", encoding="utf-8") as src:
                        content = src.read()
                except Exception:
                    continue
                if "match_market_orders" in content:
                    found_any = True
                    idx = content.find("match_market_orders")
                    f.write(f"\nFOUND in {p} at offset {idx}:\n")
                    f.write(content[max(0, idx-200):idx+400])
                    f.write("\n")
    if not found_any:
        f.write("\n!!! match_market_orders is NOT referenced in ANY .kt file in the repo !!!\n")
    f.write("\nDONE\n")

print("wrote", OUT)
