import os

OUT = "discovery_output.txt"
FILE = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"

def main():
    out_lines = []
    if not os.path.exists(FILE):
        out_lines.append(f"!!! NOT FOUND: {FILE}")
    else:
        with open(FILE, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
        start = None
        for i, line in enumerate(lines):
            if "CRAFTING -- mirrors the SkillingQueue flow above" in line:
                start = i
                break
        if start is None:
            out_lines.append("!!! MARKER NOT FOUND")
        else:
            # Generous margin: dump well past the crafting section (150 lines)
            end = min(len(lines), start + 180)
            for k in range(start, end):
                out_lines.append(f"{k+1}: {lines[k].rstrip()}")

    with open(OUT, "w", encoding="utf-8") as out:
        out.write("\n".join(out_lines))

    print(f"Wrote {OUT} ({len(out_lines)} lines)")

if __name__ == "__main__":
    main()
