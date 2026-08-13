path = "app/src/main/AndroidManifest.xml"
with open(path, "r") as f:
    content = f.read()

old_manifest = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application'''
new_manifest = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />

    <application'''
assert content.count(old_manifest) == 1, "manifest header not found or not unique"
content = content.replace(old_manifest, new_manifest, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: AndroidManifest.xml patched (INTERNET permission added).")
