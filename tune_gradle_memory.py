import pathlib

p = pathlib.Path("gradle.properties")
text = p.read_text() if p.exists() else ""

settings = {
    "org.gradle.jvmargs": "-Xmx1536m -XX:MaxMetaspaceSize=512m",
    "org.gradle.parallel": "false",
    "org.gradle.workers.max": "1",
}

lines = text.splitlines()
keys_found = set()
for i, line in enumerate(lines):
    for key, value in settings.items():
        if line.strip().startswith(key + "="):
            lines[i] = f"{key}={value}"
            keys_found.add(key)

for key, value in settings.items():
    if key not in keys_found:
        lines.append(f"{key}={value}")

p.write_text("\n".join(lines) + "\n")
print("gradle.properties updated:")
print(p.read_text())
