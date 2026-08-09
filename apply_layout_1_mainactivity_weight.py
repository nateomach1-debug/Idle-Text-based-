"""
Fix: SideRail and the routed screen content are siblings in the same Row,
but only the outer Row has weight(1f) (relative to its own parent) --
none of the individual screen composables inside the
when (currentDestination) { ... } block were given a weight(1f) to
properly share remaining space with SideRail. This is the confirmed root
cause behind the width-squeeze layout bugs reported across multiple
screens (Equipment title wrapping mid-word, Guild member list wrapping
letter-by-letter). It's very plausibly a contributor to the
empty/oversized button symptom too, though that hasn't been fully
explained yet -- worth re-testing after this fix before digging further.

Wraps the when (currentDestination) { ... } block in
Box(modifier = Modifier.weight(1f)) so it correctly claims only the
space left over after SideRail, instead of contending for the full Row
width.

Run from repo root: python3 apply_layout_1_mainactivity_weight.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")

OLD_OPEN = "                        when (currentDestination) {"
NEW_OPEN = "                        Box(modifier = Modifier.weight(1f)) {\n                        when (currentDestination) {"

OLD_CLOSE = '''                            else -> androidx.compose.material3.Text(
                                text = currentDestination.label + " screen coming soon",
                                modifier = Modifier.fillMaxSize()
                            )
                        }
                    }

                    ChatBanner('''
NEW_CLOSE = '''                            else -> androidx.compose.material3.Text(
                                text = currentDestination.label + " screen coming soon",
                                modifier = Modifier.fillMaxSize()
                            )
                        }
                        }
                    }

                    ChatBanner('''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 0:
        raise SystemExit(f"ABORT: could not find expected block for '{label}'. No changes written.")
    if count > 1:
        raise SystemExit(f"ABORT: found {count} matches for '{label}', expected exactly 1. No changes written.")
    return text.replace(old, new, 1)


def main() -> None:
    if not TARGET.exists():
        raise SystemExit(f"ABORT: could not find {TARGET} from the current directory. Run this from the repo root.")

    content = TARGET.read_text()

    if "Box(modifier = Modifier.weight(1f)) {\n                        when (currentDestination)" in content:
        raise SystemExit("ABORT: this patch looks already applied. No changes written.")

    content = replace_once(content, OLD_OPEN, NEW_OPEN, "when (currentDestination) opening")
    content = replace_once(content, OLD_CLOSE, NEW_CLOSE, "when block / ChatBanner closing context")

    if content.count("{") != content.count("}"):
        raise SystemExit("ABORT: brace mismatch after patch -- refusing to write. No changes written.")

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
