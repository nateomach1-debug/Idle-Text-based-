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
        for i, line in enumerate(lines[:40], start=1):
            out_lines.append(f"{i}: {line.rstrip()}")

    with open(OUT, "w", encoding="utf-8") as out:
        out.write("\n".join(out_lines))

    print(f"Wrote {OUT} ({len(out_lines)} lines)")

if __name__ == "__main__":
    main()
