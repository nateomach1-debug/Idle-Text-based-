#!/usr/bin/env python3
"""
Corrective patch: LeaderboardsScreen.kt build failure.

ExposedDropdownMenu is an extension function on ExposedDropdownMenuBoxScope,
not a plain top-level composable - fully-qualifying the call broke implicit
receiver resolution (and cascaded into a bogus "@Composable invocations..."
error on the next line). Fix: import it, call unqualified.
"""
import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(ROOT, "LeaderboardsScreen.kt")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

if "import androidx.compose.material3.ExposedDropdownMenu\n" in content:
    print("SKIP (import already present)")
else:
    old_import = "import androidx.compose.material3.ExposedDropdownMenuBox\n"
    count = content.count(old_import)
    if count != 1:
        raise RuntimeError(f"Expected exactly 1 match for import anchor, found {count}")
    content = content.replace(
        old_import,
        old_import + "import androidx.compose.material3.ExposedDropdownMenu\n",
    )

old_call = "            androidx.compose.material3.ExposedDropdownMenu(\n"
new_call = "            ExposedDropdownMenu(\n"
count = content.count(old_call)
if count == 1:
    content = content.replace(old_call, new_call)
    print("PATCHED: fully-qualified call site")
elif "ExposedDropdownMenu(\n" in content and old_call not in content:
    print("SKIP (call site already fixed)")
else:
    raise RuntimeError(f"Expected exactly 1 match for call-site anchor, found {count}")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Done.")
