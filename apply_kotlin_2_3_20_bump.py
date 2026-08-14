path = "app/build.gradle"
with open(path, "r") as f:
    content = f.read()

old_plugins = """    id 'org.jetbrains.kotlin.android' version '2.1.10'
    id 'org.jetbrains.kotlin.plugin.compose' version '2.1.10'
    id 'org.jetbrains.kotlin.plugin.serialization' version '2.1.10'"""
new_plugins = """    id 'org.jetbrains.kotlin.android' version '2.3.20'
    id 'org.jetbrains.kotlin.plugin.compose' version '2.3.20'
    id 'org.jetbrains.kotlin.plugin.serialization' version '2.3.20'"""
assert content.count(old_plugins) == 1, "Kotlin plugin versions block not found or not unique"
content = content.replace(old_plugins, new_plugins, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: app/build.gradle patched (Kotlin 2.1.10 -> 2.3.20 across all three Kotlin plugins, matching the version supabase-kt's actual dependency jars were compiled with).")
