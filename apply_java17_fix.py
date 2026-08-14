path = "app/build.gradle"
with open(path, "r") as f:
    content = f.read()

old_compile_options = """    compileOptions {
        sourceCompatibility JavaVersion.VERSION_21
        targetCompatibility JavaVersion.VERSION_21
    }

    kotlinOptions {
        jvmTarget = '21'
    }"""
new_compile_options = """    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = '17'
    }"""
assert content.count(old_compile_options) == 1, "compileOptions/kotlinOptions block not found or not unique"
content = content.replace(old_compile_options, new_compile_options, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: app/build.gradle patched (Java target 21 -> 17, matching the JDK actually installed in this Codespace).")
