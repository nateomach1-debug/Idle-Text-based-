import sys

BASE = "app/src/main/kotlin/com/yourname/idlerpg/"
ZONE_SELECT = BASE + "ZoneSelectScreen.kt"


def guarded_replace(path, old, new, label):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    if new in text:
        print(f"SKIP (already applied): {label} ({path})")
        return True

    count = text.count(old)
    if count == 1:
        text = text.replace(old, new)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"OK: {label} ({path})")
        return True
    elif count == 0:
        print(f"FAIL (old_str not found, new_str not found either): {label} ({path})")
        return False
    else:
        print(f"FAIL (old_str matched {count} times, expected 1): {label} ({path})")
        return False


def check_braces(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    opens = text.count("{")
    closes = text.count("}")
    ok = opens == closes
    print(f"{'Brace check OK' if ok else 'WARNING: brace mismatch'}: {path} ({{ = {opens}, }} = {closes})")
    return ok


results = []

# ===========================================================
# ZoneSelectScreen.kt - locked-zone dimming was mutating TextStyle.color
# directly, which clobbers any brush (gradient/pulse/shimmer/wave/color
# cycle) the style was carrying. Move the dimming to Modifier.alpha on
# the container instead, so whatever the style actually renders (solid
# color or brush) gets dimmed as a whole rather than color being
# reconstructed from scratch.
# ===========================================================
old = '''import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp'''
new = '''import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp'''
results.append(guarded_replace(ZONE_SELECT, old, new, "ZoneSelectScreen.kt import Modifier.alpha"))

old = '''        Column {
            Text(
                text = zone.name,
                style = MaterialTheme.typography.titleMedium.copy(
                    color = MaterialTheme.typography.titleMedium.color.copy(alpha = contentAlpha)
                )
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = zone.monsterNames.joinToString(", "),
                style = MaterialTheme.typography.labelSmall.copy(
                    color = MaterialTheme.typography.labelSmall.color.copy(alpha = contentAlpha)
                )
            )
        }'''
new = '''        Column(modifier = Modifier.alpha(contentAlpha)) {
            Text(
                text = zone.name,
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = zone.monsterNames.joinToString(", "),
                style = MaterialTheme.typography.labelSmall
            )
        }'''
results.append(guarded_replace(ZONE_SELECT, old, new, "ZoneSelectScreen.kt dim via Modifier.alpha instead of mutating color"))

print()
print("=== Brace balance check ===")
check_braces(ZONE_SELECT)

if not all(results):
    print()
    print("One or more edits FAILED - review output above before committing.")
    sys.exit(1)

print()
print("All edits applied successfully.")
