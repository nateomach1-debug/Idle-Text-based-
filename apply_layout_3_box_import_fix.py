"""
Fix: the previous layout patch (apply_layout_1_mainactivity_weight.py)
wrapped screen content in a Box(modifier = Modifier.weight(1f)), but
MainActivity.kt uses explicit individual imports rather than a wildcard
import, and androidx.compose.foundation.layout.Box was never imported --
causing "Unresolved reference: Box" and a cascade of
"@Composable invocations can only happen..." errors.

Run from repo root: python3 apply_layout_3_box_import_fix.py
"""
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")

OLD = "import androidx.compose.foundation.layout.Column\nimport androidx.compose.foundation.layout.Row"
NEW = "import androidx.compose.foundation.layout.Box\nimport androidx.compose.foundation.layout.Column\nimport androidx.compose.foundation.layout.Row"


def main() -> None:
    if not TARGET.exists():
        raise SystemExit(f"ABORT: could not find {TARGET} from the current directory. Run this from the repo root.")

    content = TARGET.read_text()

    if "import androidx.compose.foundation.layout.Box" in content:
        raise SystemExit("ABORT: Box import already present -- this patch looks already applied. No changes written.")

    count = content.count(OLD)
    if count == 0:
        raise SystemExit("ABORT: could not find the expected import block. No changes written.")
    if count > 1:
        raise SystemExit(f"ABORT: found {count} matches, expected exactly 1. No changes written.")

    content = content.replace(OLD, NEW, 1)

    TARGET.write_text(content)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
