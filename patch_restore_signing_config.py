path = "app/build.gradle"
with open(path, "r") as f:
    content = f.read()

old = (
    "android {\n"
    "    namespace 'com.yourname.idlerpg'\n"
    "    compileSdk 36\n"
    "\n"
    "    defaultConfig {\n"
)
new = (
    "android {\n"
    "    namespace 'com.yourname.idlerpg'\n"
    "    compileSdk 36\n"
    "\n"
    "    signingConfigs {\n"
    "        debug {\n"
    "            storeFile file('debug.keystore')\n"
    "            storePassword 'android'\n"
    "            keyAlias 'androiddebugkey'\n"
    "            keyPassword 'android'\n"
    "        }\n"
    "    }\n"
    "\n"
    "    defaultConfig {\n"
)
assert old in content, "android { defaultConfig pattern not found - build.gradle may have changed"
assert content.count(old) == 1, "pattern not unique"
content = content.replace(old, new)

# Ensure buildTypes.debug applies the signingConfig - add the block if missing.
if "buildTypes {" in content and "signingConfig signingConfigs.debug" not in content:
    old_compile_opts = "    compileOptions {"
    new_build_type = (
        "    buildTypes {\n"
        "        debug {\n"
        "            signingConfig signingConfigs.debug\n"
        "        }\n"
        "    }\n\n"
        "    compileOptions {"
    )
    assert old_compile_opts in content
    content = content.replace(old_compile_opts, new_build_type, 1)

with open(path, "w") as f:
    f.write(content)

print("Re-added signingConfigs block pointing at app/debug.keystore, and ensured")
print("buildTypes.debug applies it. Every future build should now sign identically")
print("and update in place instead of requiring an uninstall.")
