"""
Fix: SideRail's expanded width (180dp) eats roughly half of a typical
phone-width screen, leaving too little room for content even after the
weight(1f) fix in the companion patch. Trimming to 140dp -- still plenty
of room for icon + label, but leaves more space for the content pane.

Run from repo root: python3 apply_layout_2_siderail_width.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/SideRail.kt")

OLD = ".width(if (expanded) 180.dp else 64.dp)"
NEW = ".width(if (expanded) 140.dp else 64.dp)"


def main() -> None:
    if not TARGET.exists():
        raise SystemExit(f"ABORT: could not find {TARGET} from the current directory. Run this from the repo root.")

    content = TARGET.read_text()

    if NEW in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    count = content.count(OLD)
    if count == 0:
        raise SystemExit("ABORT: could not find the expected width line. No changes written.")
    if count > 1:
        raise SystemExit(f"ABORT: found {count} matches, expected exactly 1. No changes written.")

    content = content.replace(OLD, NEW, 1)

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
