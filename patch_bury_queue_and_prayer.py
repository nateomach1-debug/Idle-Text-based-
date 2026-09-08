#!/usr/bin/env python3
"""
Corrective patch #3: LeaderboardsScreen.kt build failure.

`weight` is not a top-level function - it's a member extension on
RowScope/ColumnScope, resolved implicitly since OutlinedButton's content
lambda is a RowScope. The explicit `import androidx.compose.foundation.
layout.weight` line was wrong and caused the compiler to bind to an
internal symbol instead ("Cannot access 'val RowColumnParentData?.weight:
Float': it is internal in file"). Fix: delete that import line - no other
code change needed, Modifier.weight(1f) resolves fine without it inside
the button's RowScope.
"""
import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(ROOT, "LeaderboardsScreen.kt")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

bad_import = "import androidx.compose.foundation.layout.weight\n"

if bad_import not in content:
    print("SKIP (import already removed / not present)")
else:
    count = content.count(bad_import)
    if count != 1:
        raise RuntimeError(f"Expected exactly 1 match, found {count}")
    content = content.replace(bad_import, "")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"PATCHED (removed bad import): {path}")

print("Done.")
