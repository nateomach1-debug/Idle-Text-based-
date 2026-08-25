import os

OUT = "discovery_output.txt"

BASE = "app/src/main/kotlin/com/yourname/idlerpg"

FILES_TO_DUMP_FULLY = [
    f"{BASE}/ActionCatalog.kt",
    f"{BASE}/CombatSystem.kt",
    f"{BASE}/GameStateRepository.kt",
    f"{BASE}/SkillProgressionSystem.kt",
    f"{BASE}/OfflineIdleMechanicsSystem.kt",
]

def main():
    out_lines = []
    for f in FILES_TO_DUMP_FULLY:
        out_lines.append("=" * 100)
        out_lines.append(f"FILE: {f}")
        out_lines.append("=" * 100)
        if not os.path.exists(f):
            out_lines.append(f"!!! FILE NOT FOUND: {f}")
            continue
        try:
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
        except OSError as e:
            out_lines.append(f"!!! ERROR READING: {e}")
            continue
        for i, line in enumerate(lines, start=1):
            out_lines.append(f"{i}: {line.rstrip()}")
        out_lines.append("")

    with open(OUT, "w", encoding="utf-8") as out:
        out.write("\n".join(out_lines))

    print(f"Wrote {OUT} ({len(out_lines)} lines)")

if __name__ == "__main__":
    main()
