path = "app/build.gradle"
with open(path, "r") as f:
    content = f.read()

old_agp = "    id 'com.android.application' version '8.5.0'\n"
new_agp = "    id 'com.android.application' version '8.9.1'\n"
assert content.count(old_agp) == 1, "AGP plugin line not found or not unique"
content = content.replace(old_agp, new_agp, 1)

old_compilesdk = "    compileSdk 34\n"
new_compilesdk = "    compileSdk 36\n"
assert content.count(old_compilesdk) == 1, "compileSdk line not found or not unique"
content = content.replace(old_compilesdk, new_compilesdk, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: app/build.gradle patched (AGP 8.5.0 -> 8.9.1, compileSdk 34 -> 36; targetSdk/minSdk left unchanged).")
