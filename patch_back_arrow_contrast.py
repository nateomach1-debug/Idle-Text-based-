import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"

def find_file(name):
    for dirpath, _, files in os.walk(ROOT):
        if name in files:
            return os.path.join(dirpath, name)
    raise SystemExit(f"!!! FILE NOT FOUND: {name} !!!")

def guarded_replace(path, old, new, expected_count=1):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    count = content.count(old)
    if count != expected_count:
        raise SystemExit(
            f"!!! ABORTING: expected {expected_count} occurrence(s) of anchor in {path}, found {count} !!!\n"
            f"--- anchor was ---\n{old}\n--- end anchor ---"
        )
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"patched {path} (replaced {count} occurrence(s))")

# Files using contentDescription = "Back"
back_files = [
    "SkillDetailScreen.kt",
    "SmithingScreen.kt",
    "OrderBookScreen.kt",
    "EquipmentScreen.kt",
    "LoadoutScreen.kt",
]
old_back = 'Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "Back")'
new_back = 'Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "Back", tint = MaterialTheme.colorScheme.onSurface)'
for fn in back_files:
    guarded_replace(find_file(fn), old_back, new_back)

# CombatViewScreen.kt uses contentDescription = "Leave zone" instead
old_leave = 'Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "Leave zone")'
new_leave = 'Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "Leave zone", tint = MaterialTheme.colorScheme.onSurface)'
guarded_replace(find_file("CombatViewScreen.kt"), old_leave, new_leave)

print("ALL PATCHES APPLIED SUCCESSFULLY")
