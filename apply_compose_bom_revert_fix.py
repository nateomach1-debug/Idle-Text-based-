path = "app/build.gradle"
with open(path, "r") as f:
    content = f.read()

old_bom = "    implementation platform('androidx.compose:compose-bom:2026.06.01')\n"
new_bom = "    implementation platform('androidx.compose:compose-bom:2024.06.00')\n"
assert content.count(old_bom) == 1, "compose-bom line not found or not unique"
content = content.replace(old_bom, new_bom, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: app/build.gradle patched (Compose BOM reverted to the original 2024.06.00 - it doesn't need to change for Kotlin 2.1.10/supabase-kt, and the newer BOM was pulling in AGP/compileSdk requirements this project doesn't meet).")
