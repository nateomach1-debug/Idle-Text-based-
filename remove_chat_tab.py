BASE = "app/src/main/kotlin/com/yourname/idlerpg"

# ---------------------------------------------------------
# 1. NavigationDestinations.kt - remove CHAT enum entry
# ---------------------------------------------------------
nav_path = f"{BASE}/NavigationDestinations.kt"
with open(nav_path, "r") as f:
    content = f.read()

old = '    CHAT("Chat", "chat_bubble"),\n    MODERATION("Moderation", "shield_person")\n}'
new = '    MODERATION("Moderation", "shield_person")\n}'
assert old in content, f"Pattern not found in {nav_path}"
content = content.replace(old, new)
with open(nav_path, "w") as f:
    f.write(content)
print(f"Patched {nav_path}")

# ---------------------------------------------------------
# 2. SideRail.kt - remove CHAT icon mapping
# ---------------------------------------------------------
rail_path = f"{BASE}/SideRail.kt"
with open(rail_path, "r") as f:
    content = f.read()

old_icon = '    AppDestination.CHAT -> Icons.Filled.ChatBubble\n    AppDestination.MODERATION -> Icons.Filled.AdminPanelSettings\n}'
new_icon = '    AppDestination.MODERATION -> Icons.Filled.AdminPanelSettings\n}'
assert old_icon in content, f"Icon pattern not found in {rail_path}"
content = content.replace(old_icon, new_icon)
with open(rail_path, "w") as f:
    f.write(content)
print(f"Patched {rail_path}")

print("\nBoth files patched. NOTE: any explicit 'AppDestination.CHAT ->' branch")
print("in MainActivity.kt's when-block (if one exists) was NOT auto-patched -")
print("see manual check step below.")
